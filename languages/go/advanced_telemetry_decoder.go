// Go — Advanced Example: Verified Binary Telemetry Decoder
//
// What: A bounded decoder for versioned telemetry frames with CRC validation,
// sequence-gap detection, cancellation, and atomic operational metrics.
// Where: Flight telemetry, industrial sensors, edge gateways, ingest daemons.
// When: Untrusted UDP or serial frames must be rejected without panics or stalls.
// Why: Go provides simple concurrency, binary primitives, and static deployment.
// How: Explicit frame layout, size checks before slicing, IEEE-754 decoding,
// CRC-32 integrity, context cancellation, and a bounded result channel.
package main

import (
	"context"
	"encoding/binary"
	"errors"
	"fmt"
	"hash/crc32"
	"math"
	"sync"
	"sync/atomic"
)

const (
	telemetryMagic       = "TLM1"
	telemetryVersion     = uint8(1)
	telemetryFrameSize   = 32
	telemetryPayloadSize = 16
)

type TelemetryFrame struct {
	Sequence    uint32
	TimestampNS uint64
	Temperature float32
	PressurePA  float32
}

type DecodeCode string

const (
	CodeShortFrame      DecodeCode = "SHORT_FRAME"
	CodeInvalidMagic    DecodeCode = "INVALID_MAGIC"
	CodeUnsupported     DecodeCode = "UNSUPPORTED_VERSION"
	CodeInvalidLength   DecodeCode = "INVALID_LENGTH"
	CodeChecksumFailure DecodeCode = "CHECKSUM_FAILURE"
	CodeSequenceGap     DecodeCode = "SEQUENCE_GAP"
)

type DecodeError struct {
	Code   DecodeCode
	Detail string
}

func (e *DecodeError) Error() string {
	return fmt.Sprintf("telemetry decode %s: %s", e.Code, e.Detail)
}

type DecodeResult struct {
	Frame *TelemetryFrame
	Err   error
}

type DecoderMetrics struct {
	Decoded      uint64
	Rejected     uint64
	SequenceGaps uint64
}

type TelemetryDecoder struct {
	decoded      atomic.Uint64
	rejected     atomic.Uint64
	sequenceGaps atomic.Uint64
	sequenceMu   sync.Mutex
	hasSequence  bool
	lastSequence uint32
}

func NewTelemetryDecoder() *TelemetryDecoder {
	return &TelemetryDecoder{}
}

func (d *TelemetryDecoder) Decode(buf []byte) (TelemetryFrame, error) {
	if len(buf) < telemetryFrameSize {
		d.rejected.Add(1)
		return TelemetryFrame{}, &DecodeError{
			Code:   CodeShortFrame,
			Detail: fmt.Sprintf("received %d bytes; need %d", len(buf), telemetryFrameSize),
		}
	}
	if string(buf[0:4]) != telemetryMagic {
		d.rejected.Add(1)
		return TelemetryFrame{}, &DecodeError{Code: CodeInvalidMagic, Detail: "magic must be TLM1"}
	}
	if buf[4] != telemetryVersion {
		d.rejected.Add(1)
		return TelemetryFrame{}, &DecodeError{
			Code:   CodeUnsupported,
			Detail: fmt.Sprintf("version %d is not supported", buf[4]),
		}
	}
	payloadLength := binary.BigEndian.Uint16(buf[6:8])
	if payloadLength != telemetryPayloadSize {
		d.rejected.Add(1)
		return TelemetryFrame{}, &DecodeError{
			Code:   CodeInvalidLength,
			Detail: fmt.Sprintf("payload length %d must equal %d", payloadLength, telemetryPayloadSize),
		}
	}

	expectedCRC := binary.BigEndian.Uint32(buf[28:32])
	actualCRC := crc32.ChecksumIEEE(buf[:28])
	if actualCRC != expectedCRC {
		d.rejected.Add(1)
		return TelemetryFrame{}, &DecodeError{
			Code:   CodeChecksumFailure,
			Detail: fmt.Sprintf("expected %08x, calculated %08x", expectedCRC, actualCRC),
		}
	}

	frame := TelemetryFrame{
		Sequence:    binary.BigEndian.Uint32(buf[8:12]),
		TimestampNS: binary.BigEndian.Uint64(buf[12:20]),
		Temperature: math.Float32frombits(binary.BigEndian.Uint32(buf[20:24])),
		PressurePA:  math.Float32frombits(binary.BigEndian.Uint32(buf[24:28])),
	}
	if math.IsNaN(float64(frame.Temperature)) || math.IsInf(float64(frame.Temperature), 0) ||
		math.IsNaN(float64(frame.PressurePA)) || math.IsInf(float64(frame.PressurePA), 0) {
		d.rejected.Add(1)
		return TelemetryFrame{}, errors.New("telemetry contains non-finite measurement")
	}

	if err := d.trackSequence(frame.Sequence); err != nil {
		d.sequenceGaps.Add(1)
		d.rejected.Add(1)
		return TelemetryFrame{}, err
	}
	d.decoded.Add(1)
	return frame, nil
}

func (d *TelemetryDecoder) trackSequence(sequence uint32) error {
	d.sequenceMu.Lock()
	defer d.sequenceMu.Unlock()

	if !d.hasSequence {
		d.hasSequence = true
		d.lastSequence = sequence
		return nil
	}
	expected := d.lastSequence + 1
	if sequence != expected {
		return &DecodeError{
			Code:   CodeSequenceGap,
			Detail: fmt.Sprintf("expected sequence %d, received %d", expected, sequence),
		}
	}
	d.lastSequence = sequence
	return nil
}

func (d *TelemetryDecoder) Metrics() DecoderMetrics {
	return DecoderMetrics{
		Decoded:      d.decoded.Load(),
		Rejected:     d.rejected.Load(),
		SequenceGaps: d.sequenceGaps.Load(),
	}
}

func (d *TelemetryDecoder) DecodeStream(ctx context.Context, input <-chan []byte, buffer int) <-chan DecodeResult {
	if buffer < 1 {
		buffer = 1
	}
	output := make(chan DecodeResult, buffer)
	go func() {
		defer close(output)
		for {
			select {
			case <-ctx.Done():
				return
			case raw, ok := <-input:
				if !ok {
					return
				}
				frame, err := d.Decode(raw)
				result := DecodeResult{Err: err}
				if err == nil {
					result.Frame = &frame
				}
				select {
				case output <- result:
				case <-ctx.Done():
					return
				}
			}
		}
	}()
	return output
}

func EncodeTelemetryFrame(frame TelemetryFrame) []byte {
	buf := make([]byte, telemetryFrameSize)
	copy(buf[0:4], telemetryMagic)
	buf[4] = telemetryVersion
	buf[5] = 0 // reserved flags
	binary.BigEndian.PutUint16(buf[6:8], telemetryPayloadSize)
	binary.BigEndian.PutUint32(buf[8:12], frame.Sequence)
	binary.BigEndian.PutUint64(buf[12:20], frame.TimestampNS)
	binary.BigEndian.PutUint32(buf[20:24], math.Float32bits(frame.Temperature))
	binary.BigEndian.PutUint32(buf[24:28], math.Float32bits(frame.PressurePA))
	binary.BigEndian.PutUint32(buf[28:32], crc32.ChecksumIEEE(buf[:28]))
	return buf
}

func main() {
	decoder := NewTelemetryDecoder()
	encoded := EncodeTelemetryFrame(TelemetryFrame{
		Sequence:    1,
		TimestampNS: 1_726_100_000_000_000_000,
		Temperature: 21.5,
		PressurePA:  101325,
	})
	decoded, err := decoder.Decode(encoded)
	if err != nil {
		panic(err)
	}
	metrics := decoder.Metrics()
	fmt.Printf(
		"status=VERIFIED sequence=%d timestamp_ns=%d temperature_c=%.1f pressure_pa=%.0f decoded=%d rejected=%d gaps=%d\n",
		decoded.Sequence,
		decoded.TimestampNS,
		decoded.Temperature,
		decoded.PressurePA,
		metrics.Decoded,
		metrics.Rejected,
		metrics.SequenceGaps,
	)
}
