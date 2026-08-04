"""Behavioral proof for the Colossus cooling Protocol Buffers contract.

The generated classes remain schema-only; this host validator demonstrates how
an authority boundary can reject malformed telemetry, derive a bounded command,
round-trip deterministic binary messages, and emit a content-bound receipt.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import math
import re
import sys
from pathlib import Path

from google.protobuf.timestamp_pb2 import Timestamp

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_contract(generated_dir: Path):
    if not generated_dir.is_dir():
        raise ValueError(f"generated binding directory not found: {generated_dir}")
    sys.path.insert(0, str(generated_dir.resolve()))
    return importlib.import_module("advanced_colossus_cooling_pb2")


def validate_telemetry(telemetry) -> None:
    if telemetry.rack_id <= 0:
        raise ValueError("rack_id must be positive")
    if not telemetry.readings:
        raise ValueError("at least one sensor reading is required")

    sensor_ids: set[str] = set()
    for reading in telemetry.readings:
        if not reading.sensor_id or reading.sensor_id in sensor_ids:
            raise ValueError("sensor identifiers must be non-empty and unique")
        sensor_ids.add(reading.sensor_id)
        if not reading.HasField("observed_at") or reading.observed_at.seconds <= 0:
            raise ValueError("every reading requires a positive observation timestamp")
        values = (
            reading.temperature_c,
            reading.flow_liters_per_minute,
            reading.pressure_kpa,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("sensor values must be finite")
        if not -80.0 <= reading.temperature_c <= 150.0:
            raise ValueError("temperature is outside the governed sensor range")
        if reading.flow_liters_per_minute < 0.0 or reading.pressure_kpa < 0.0:
            raise ValueError("flow and pressure must be non-negative")


def derive_command(contract, telemetry, authority_receipt_sha256: str):
    validate_telemetry(telemetry)
    if not _SHA256.fullmatch(authority_receipt_sha256):
        raise ValueError("authority receipt must be a lowercase SHA-256 digest")

    maximum_temperature = max(
        reading.temperature_c for reading in telemetry.readings
    )
    command = contract.ControlCommand(
        command_id=f"rack-{telemetry.rack_id}-thermal-control",
        rack_id=telemetry.rack_id,
        authority_receipt_sha256=authority_receipt_sha256,
    )
    if maximum_temperature >= 95.0:
        command.emergency_shutdown = True
    elif maximum_temperature >= 75.0:
        command.set_pump_percent = min(100.0, 40.0 + maximum_temperature / 2.0)
    else:
        command.set_fan_percent = min(100.0, 20.0 + maximum_temperature / 3.0)
    return command


def deterministic_round_trip(message, message_type):
    first = message.SerializeToString(deterministic=True)
    second = message.SerializeToString(deterministic=True)
    require(first == second, "deterministic serialization changed between calls")
    restored = message_type()
    restored.ParseFromString(first)
    require(restored == message, "binary round-trip changed the message")
    return first


def build_valid_telemetry(contract):
    observed = Timestamp(seconds=1_786_000_000)
    telemetry = contract.RackTelemetry(rack_id=42, health=contract.DEGRADED)
    telemetry.labels.update({"zone": "west", "coolant": "water"})
    telemetry.readings.extend(
        [
            contract.SensorReading(
                sensor_id="rack-42-inlet",
                temperature_c=72.5,
                flow_liters_per_minute=118.0,
                pressure_kpa=230.0,
                observed_at=observed,
            ),
            contract.SensorReading(
                sensor_id="rack-42-outlet",
                temperature_c=82.0,
                flow_liters_per_minute=112.0,
                pressure_kpa=224.0,
                observed_at=observed,
            ),
        ]
    )
    return telemetry


def main() -> int:
    if len(sys.argv) != 2:
        raise ValueError(
            "usage: advanced_colossus_cooling_test.py <generated-python-directory>"
        )
    contract = load_contract(Path(sys.argv[1]))
    telemetry = build_valid_telemetry(contract)
    telemetry_binary = deterministic_round_trip(telemetry, contract.RackTelemetry)

    authority_hash = hashlib.sha256(b"tower-authority-receipt-v1").hexdigest()
    command = derive_command(contract, telemetry, authority_hash)
    command_binary = deterministic_round_trip(command, contract.ControlCommand)
    require(
        command.WhichOneof("action") == "set_pump_percent",
        "degraded thermal state selected the wrong action",
    )
    require(0.0 <= command.set_pump_percent <= 100.0, "pump command escaped bounds")

    output_hash = hashlib.sha256(command_binary).hexdigest()
    completed = Timestamp(seconds=1_786_000_001)
    receipt = contract.CommandReceipt(
        command_id=command.command_id,
        accepted=True,
        reason="validated telemetry and bounded thermal policy",
        output_sha256=output_hash,
        completed_at=completed,
    )
    receipt_binary = deterministic_round_trip(receipt, contract.CommandReceipt)

    duplicate_rejected = False
    invalid = build_valid_telemetry(contract)
    invalid.readings[1].sensor_id = invalid.readings[0].sensor_id
    try:
        validate_telemetry(invalid)
    except ValueError:
        duplicate_rejected = True
    require(duplicate_rejected, "duplicate sensor identifiers were accepted")

    authority_rejected = False
    try:
        derive_command(contract, telemetry, "not-a-sha256")
    except ValueError:
        authority_rejected = True
    require(authority_rejected, "invalid authority receipt was accepted")

    print(
        json.dumps(
            {
                "status": "SUCCEEDED",
                "rack_id": telemetry.rack_id,
                "sensor_count": len(telemetry.readings),
                "selected_action": command.WhichOneof("action"),
                "telemetry_bytes": len(telemetry_binary),
                "command_bytes": len(command_binary),
                "receipt_bytes": len(receipt_binary),
                "command_sha256": output_hash,
                "duplicate_sensor_rejected": duplicate_rejected,
                "invalid_authority_rejected": authority_rejected,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # explicit CLI boundary
        print(f"Protobuf cooling proof failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
