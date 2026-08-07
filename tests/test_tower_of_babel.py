"""System tests for the governed Tower."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from integrations.megamind.adapter import TechnologyRequest, select_technologies
from tower import build as build_module
from tower.benchmark import benchmark_many
from tower.build import build_floor
from tower.generate import build_surfaces, generate
from tower.integrity import verify_integrity, write_manifest
from tower.proofs import build_proof_report
from tower.receipt import build_receipt
from tower.registry import REPO_ROOT, TowerRegistry, load_registry, validate_registry


def test_canonical_registry_governs_all_advertised_floors():
    registry = load_registry()
    assert len(registry.technologies) > 0

def test_receipt_is_deterministic():
    registry = load_registry()
    first = build_receipt({"counts": {"VERIFIED": 3}})
    second = build_receipt({"counts": {"VERIFIED": 3}})
    assert first == second
    assert len(first["receipt_sha256"]) == 64
    assert first["technology_count"] == len(registry.technologies)
    assert {row["id"] for row in registry.technologies} >= {
        "motion-dismiss", "complaint-1983", "evidence-documentary", "damages-compensatory",
    }


def test_every_floor_has_complete_w4h_examples_and_proof():
    registry = load_registry()
    for row in registry.technologies:
        for key in ("what", "where", "when", "why", "how"):
            if key in row:
                assert len(row[key].strip()) >= 12, (row["id"], key)
        if "easy_example" in row and not row["easy_example"].startswith("N/A"):
            assert (REPO_ROOT / row["easy_example"]).is_file()
        if "advanced_example" in row and not row["advanced_example"].startswith("N/A"):
            assert (REPO_ROOT / row["advanced_example"]).is_file()
        assert row["evidence_state"]
        assert row["proof_class"]


def test_generated_surfaces_do_not_drift():
    assert generate(check=True) == []


def test_generator_emits_one_canonical_build_contract_per_floor():
    registry = load_registry()
    surfaces = build_surfaces(registry)
    path = REPO_ROOT / "generated" / "build_commands.json"
    payload = json.loads(surfaces[path])
    assert set(payload) == {row["id"] for row in registry.technologies}
    for technology_id, contract in payload.items():
        assert contract["toolchain"]["tool"], technology_id
        assert contract["toolchain"]["reference_pin"], technology_id
        assert isinstance(contract["toolchain"]["build"], list), technology_id
        assert isinstance(contract["toolchain"]["test"], list), technology_id
        assert contract["execution"]["ci_tier"], technology_id


def test_runtime_registry_is_thin_canonical_facade():
    import babel_registry

    canonical = load_registry()
    assert len(babel_registry.BABEL_REGISTRY) == len(canonical.technologies)
    assert babel_registry.BabelRegistryEngine().get_spec("rust")["what"] == canonical.by_id("rust")["what"]


def test_sidecar_has_no_hardcoded_floor_count():
    source = (REPO_ROOT / "mastermind_sidecar.py").read_text(encoding="utf-8")
    assert "total_technologies" in source
    assert '"total_languages": 17' not in source
    assert "len(technologies)" in source


def test_weak_advanced_exhibits_are_substantive():
    minimum_bytes = {
        "languages/rust/advanced_safety_governor.rs": 2500,
        "languages/typescript/advanced_mcp_gateway.ts": 2500,
        "languages/cuda/advanced_reference_attention.cu": 2000,
        "languages/lean4/advanced_truth_gate_proof.lean": 700,
        "languages/protobuf/advanced_colossus_cooling.proto": 900,
    }
    for rel, minimum in minimum_bytes.items():
        assert (REPO_ROOT / rel).stat().st_size >= minimum, rel


def test_missing_toolchain_is_an_exact_blocker(monkeypatch):
    fake = {
        "id": "missing",
        "toolchain": {
            "tool": "mojo",
            "reference_pin": "1.0",
            "build": [],
            "test": [],
        },
        "execution": {"ci_tier": "portable", "hardware_gate": ""},
    }
    monkeypatch.setattr(build_module, "_available", lambda _tool: False)
    result = build_floor(fake)
    assert result["status"] == "BLOCKED_TOOLCHAIN"
    assert "mojo" in result["blocker"]


def test_hardware_gate_is_not_reported_as_success(monkeypatch):
    fake = {
        "id": "gpu",
        "toolchain": {"tool": "python3", "reference_pin": "test", "build": [], "test": []},
        "execution": {"ci_tier": "hardware", "hardware_gate": "Example accelerator"},
    }
    monkeypatch.delenv("TOWER_ENABLE_GPU", raising=False)
    result = build_floor(fake)
    assert result == {
        "technology_id": "gpu",
        "status": "BLOCKED_HARDWARE",
        "blocker": "Example accelerator",
        "tool": "python3",
        "reference_pin": "test",
        "commands": [],
    }


def test_megamind_adapter_selects_technology_and_owners():
    plan = select_technologies(
        TechnologyRequest(
            mission_id="m-1",
            capabilities=("coding", "evidence", "tool"),
            interfaces=("protobuf",),
            minimum_proof_class="compile",
        )
    )
    assert plan["mission_id"] == "m-1"
    assert plan["technology_ids"]
    assert len(plan["tower_registry_sha256"]) == 64
    assert plan["agent_ids"]
    assert plan["piston_ids"]


def test_registry_rejects_missing_w4h():
    registry = load_registry()
    payload = deepcopy(registry.payload)
    next(row for row in payload["technologies"] if row["id"] == "python")["why"] = ""
    broken = TowerRegistry(payload=payload, source=registry.source, source_files=registry.source_files)
    assert any("python.why" in error for error in validate_registry(broken, check_paths=False))


def test_integrity_manifest_detects_and_clears_drift(tmp_path):
    manifest_path = tmp_path / "file_hashes.json"
    manifest = write_manifest(manifest_path)
    assert manifest["file_count"] > 30
    assert verify_integrity(manifest_path)["ok"]


def test_receipt_is_deterministic():
    first = build_receipt({"counts": {"VERIFIED": 3}})
    second = build_receipt({"counts": {"VERIFIED": 3}})
    assert first == second
    assert len(first["receipt_sha256"]) == 64
    assert first["technology_count"] == 36


def test_tower_proto_contains_registry_and_megamind_contracts():
    tower_proto = (REPO_ROOT / "proto/tower.proto").read_text(encoding="utf-8")
    bridge_proto = (REPO_ROOT / "integrations/megamind/tower_adapter.proto").read_text(encoding="utf-8")
    assert "message TechnologySpec" in tower_proto
    assert "service TowerAuthority" in tower_proto
    assert "service TowerMegamindBridge" in bridge_proto


def test_benchmark_report_is_truthful_about_missing_tools():
    registry = load_registry()
    report = benchmark_many(registry, ["mlir"], iterations=1)
    assert report["results"][0]["status"] in {"BLOCKED_TOOLCHAIN", "MEASURED", "NO_RUNTIME_BENCHMARK"}
    assert "not universal language rankings" in report["truth_note"]


def test_proof_report_binds_declared_gate_to_build_status():
    registry = load_registry()
    report = build_proof_report(
        registry,
        {"results": [{"technology_id": "lean4", "status": "BLOCKED_TOOLCHAIN"}]},
    )
    lean = next(row for row in report["floors"] if row["technology_id"] == "lean4")
    assert lean["proof_class"] == "formal"
    assert lean["proof_status"] == "BLOCKED"


def test_packaged_registry_is_exact_canonical_mirror():
    canonical = load_registry(REPO_ROOT / "registry/tower.yml")
    packaged = load_registry(REPO_ROOT / "src/tower/data/tower.yml")
    assert packaged.payload == canonical.payload
    assert packaged.canonical_bytes() == canonical.canonical_bytes()
    assert len(packaged.source_files) == len(canonical.source_files)


def test_registry_fragments_are_contained_and_unique(tmp_path):
    index = tmp_path / "tower.yml"
    index.write_text(
        json.dumps({
            "tower_id": "glaciereq.tower-of-babel.v1",
            "governance": {"canonical_source": "registry/tower.yml"},
            "fragments": ["../outside.json"],
        }),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="fragment"):
        load_registry(index)


def test_babel_registry_engine_accepts_repo_root():
    from babel_registry import BabelRegistryEngine
    engine = BabelRegistryEngine(repo_root=REPO_ROOT)
    assert engine.get_spec("python")["ok"]


def test_megamind_adapter_short_capability_not_displaced_by_prefix():
    req = TechnologyRequest(mission_id="m1", capabilities=("go",))
    res = select_technologies(req)
    assert "go" in res["technology_ids"]


def test_receipt_v2_has_sha256_field():
    rec = build_receipt({"counts": {"VERIFIED": 1}})
    assert "receipt_sha256" in rec
    assert rec["body_sha256"] == rec["receipt_sha256"]


def test_topology_graph_and_dot_render():
    from tower.visualize import build_topology_graph, render_dot_graph
    registry = load_registry()
    graph = build_topology_graph(registry)
    assert graph["node_count"] == 36
    assert len(graph["nodes"]) == 36
    dot = render_dot_graph(registry)
    assert "digraph TowerOfBabel" in dot
    assert 'node [shape=box' in dot


def test_registry_search():
    from tower.visualize import search_registry
    registry = load_registry()
    python_matches = search_registry(registry, "python")
    assert any(tech["id"] == "python" for tech in python_matches)
    verilog_matches = search_registry(registry, "hardware")
    assert len(verilog_matches) > 0

