package main

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestTelemetryRoundTrip(t *testing.T) {
	decoder := NewTelemetryDecoder()
	want := TelemetryFrame{
		Sequence:    41,
		TimestampNS: 1_234_567_890,
		Temperature: 22.5,
		PressurePA:  101325,
	}
	got, err := decoder.Decode(EncodeTelemetryFrame(want))
	if err != nil {
		t.Fatalf("Decode() error = %v", err)
	}
	if got != want {
		t.Fatalf("Decode() = %#v, want %#v", got, want)
	}
	metrics := decoder.Metrics()
	if metrics.Decoded != 1 || metrics.Rejected != 0 {
		t.Fatalf("unexpected metrics: %#v", metrics)
	}
}

func TestTelemetryRejectsShortAndCorruptFrames(t *testing.T) {
	decoder := NewTelemetryDecoder()
	if _, err := decoder.Decode([]byte("short")); err == nil {
		t.Fatal("expected short-frame error")
	}

	frame := EncodeTelemetryFrame(TelemetryFrame{Sequence: 1, Temperature: 1, PressurePA: 2})
	frame[20] ^= 0xff
	_, err := decoder.Decode(frame)
	var decodeErr *DecodeError
	if !errors.As(err, &decodeErr) || decodeErr.Code != CodeChecksumFailure {
		t.Fatalf("expected checksum failure, got %v", err)
	}
	if decoder.Metrics().Rejected != 2 {
		t.Fatalf("expected two rejected frames, got %#v", decoder.Metrics())
	}
}

func TestTelemetryDetectsSequenceGap(t *testing.T) {
	decoder := NewTelemetryDecoder()
	for _, sequence := range []uint32{10, 12} {
		_, err := decoder.Decode(EncodeTelemetryFrame(TelemetryFrame{
			Sequence: sequence, Temperature: 1, PressurePA: 2,
		}))
		if sequence == 10 && err != nil {
			t.Fatalf("first frame failed: %v", err)
		}
		if sequence == 12 {
			var decodeErr *DecodeError
			if !errors.As(err, &decodeErr) || decodeErr.Code != CodeSequenceGap {
				t.Fatalf("expected sequence gap, got %v", err)
			}
		}
	}
	if decoder.Metrics().SequenceGaps != 1 {
		t.Fatalf("expected one sequence gap, got %#v", decoder.Metrics())
	}
}

func TestDecodeStreamHonorsCancellation(t *testing.T) {
	decoder := NewTelemetryDecoder()
	ctx, cancel := context.WithCancel(context.Background())
	input := make(chan []byte)
	output := decoder.DecodeStream(ctx, input, 1)
	cancel()

	select {
	case _, ok := <-output:
		if ok {
			t.Fatal("expected closed output channel")
		}
	case <-time.After(time.Second):
		t.Fatal("decoder did not stop after cancellation")
	}
}
