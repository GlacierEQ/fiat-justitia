from tower import build
from tower.registry import TowerRegistry


def test_unrecognized_primary_tool_becomes_review_work_without_execution():
    result = build.build_floor(
        {
            "id": "external-fetch",
            "toolchain": {
                "tool": "curl",
                "reference_pin": "1",
                "build": [["curl", "https://example.invalid"]],
                "test": [],
            },
            "execution": {"hardware_gate": "", "ci_tier": "portable"},
        }
    )

    assert result["status"] == "CONTINUATION_REQUIRED"
    assert result["continuation"] == "enabled"
    assert "review_execution_frontend:curl" in result["resolution_work"]
    assert result["commands"][0]["execution"] == "review_required"


def test_missing_toolchain_is_resolution_work(monkeypatch):
    fake = {
        "id": "missing",
        "toolchain": {"tool": "mojo", "reference_pin": "1.0", "build": [], "test": []},
        "execution": {"ci_tier": "portable", "hardware_gate": ""},
    }
    monkeypatch.setattr(build, "_available", lambda _tool: False)

    result = build.build_floor(fake)

    assert result["status"] == "CONTINUATION_REQUIRED"
    assert result["continuation"] == "enabled"
    assert "make_toolchain_available:mojo" in result["resolution_work"]


def test_hardware_gate_becomes_environment_activation_work(monkeypatch):
    fake = {
        "id": "gpu",
        "toolchain": {"tool": "python3", "reference_pin": "test", "build": [], "test": []},
        "execution": {"ci_tier": "hardware", "hardware_gate": "Example accelerator"},
    }
    monkeypatch.delenv("TOWER_ENABLE_GPU", raising=False)

    result = build.build_floor(fake)

    assert result["status"] == "CONTINUATION_REQUIRED"
    assert result["continuation"] == "enabled"
    assert "activate_declared_environment:Example accelerator" in result["resolution_work"]


def test_unknown_request_becomes_discovery_work():
    registry = TowerRegistry(payload={"tower_id": "test", "technologies": []}, source=None, source_files=())

    report = build.build_many(registry, ["new-language"])

    assert report["continuation"] == "enabled"
    assert report["results"][0]["status"] == "CONTINUATION_REQUIRED"
    assert "discover_requested_technology" in report["results"][0]["resolution_work"]
