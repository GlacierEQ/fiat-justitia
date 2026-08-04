"""Interface topology and visualization engine for the Tower registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .registry import TowerRegistry, load_registry


def build_topology_graph(registry: TowerRegistry) -> dict[str, Any]:
    nodes = []
    edges = []
    seen_edges: set[tuple[str, str, str]] = set()

    for tech in registry.technologies:
        nodes.append({
            "id": tech["id"],
            "name": tech["name"],
            "category": tech["category"],
            "artifact_type": tech["artifact_type"],
            "evidence_state": tech["evidence_state"],
            "proof_class": tech["proof_class"],
            "interfaces": tech.get("interfaces", []),
            "megamind": tech.get("megamind", {}),
        })

        tech_id = tech["id"]
        for interface in tech.get("interfaces", []):
            if not isinstance(interface, str):
                continue
            # Find target technologies that match interface or technology_id
            for other in registry.technologies:
                other_id = other["id"]
                if other_id == tech_id:
                    continue
                if interface.casefold() in {other_id.casefold(), other.get("name", "").casefold(), other.get("category", "").casefold()}:
                    edge_key = (tech_id, other_id, interface)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append({
                            "source": tech_id,
                            "target": other_id,
                            "interface": interface,
                        })

    return {
        "graph_version": "1.0.0",
        "tower_id": registry.payload.get("tower_id", "glaciereq.tower-of-babel.v1"),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def render_dot_graph(registry: TowerRegistry) -> str:
    topology = build_topology_graph(registry)
    lines = [
        'digraph TowerOfBabel {',
        '  rankdir=LR;',
        '  node [shape=box, style="filled,rounded", fontname="Arial", fontsize=10];',
        '  edge [fontname="Arial", fontsize=8];',
        '',
    ]

    # Group by category
    categories: dict[str, list[dict[str, Any]]] = {}
    for node in topology["nodes"]:
        categories.setdefault(node["category"], []).append(node)

    for category, nodes in categories.items():
        cluster_name = f'cluster_{category}'
        label = category.replace('_', ' ').title()
        lines.append(f'  subgraph {cluster_name} {{')
        lines.append(f'    label = "{label}";')
        lines.append('    style = "filled";')
        lines.append('    color = "lightgrey";')
        lines.append('    fillcolor = "#f8f9fa";')
        for node in nodes:
            name = node["name"]
            tech_id = node["id"]
            proof = node["proof_class"]
            lines.append(f'    "{tech_id}" [label="{name}\\n[{proof}]", fillcolor="#e3f2fd"];')
        lines.append('  }')
        lines.append('')

    for edge in topology["edges"]:
        src = edge["source"]
        tgt = edge["target"]
        iface = edge["interface"]
        lines.append(f'  "{src}" -> "{tgt}" [label="{iface}"];')

    lines.append('}')
    return "\n".join(lines)


def search_registry(registry: TowerRegistry, query: str) -> list[dict[str, Any]]:
    q = query.casefold().strip()
    if not q:
        return list(registry.technologies)
    
    matches = []
    for tech in registry.technologies:
        text_blob = " ".join([
            tech.get("id", ""),
            tech.get("name", ""),
            tech.get("category", ""),
            tech.get("artifact_type", ""),
            tech.get("evidence_state", ""),
            tech.get("proof_class", ""),
            tech.get("what", ""),
            tech.get("where", ""),
            tech.get("why", ""),
            tech.get("how", ""),
            *[str(iface) for iface in tech.get("interfaces", [])],
        ]).casefold()

        if q in text_blob:
            matches.append(tech)

    return matches
