#!/usr/bin/env python3
"""Summarize a TRAPI message from `tct query find-neighborhood` / `find-path`.

The `tct query find-*` commands print a full TRAPI 1.5 message (often hundreds of
edges). Piping that raw into an LLM context is wasteful, so this helper collapses
it to a compact, ranked, provenance-bearing table.

Usage:
    tct query find-neighborhood "<curie>" '["biolink:OrganismTaxon"]' > out.json
    uv run python3 .claude/skills/translator-query/extract_trapi.py out.json [top_n]

For each ranked bridging/neighbor node it prints: score, label, CURIE, the
predicates on the supporting edges, the primary knowledge sources (infores IDs),
and up to five supporting publications.
"""
import json
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: extract_trapi.py <trapi.json> [top_n]", file=sys.stderr)
        return 2
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    raw = open(sys.argv[1]).read()
    # `tct query find-*` echoes the node id on its own line before the JSON body.
    msg = json.loads(raw[raw.index("{"):])

    kg = msg.get("knowledge_graph", {})
    nodes, edges = kg.get("nodes", {}), kg.get("edges", {})
    aux = msg.get("auxiliary_graphs", {})
    results = msg.get("results", [])
    if not results or not results[0].get("analyses"):
        print("No results returned by Translator for this query.")
        return 0

    rows = []
    for analysis in results[0]["analyses"]:
        score = analysis.get("score")
        for binding in analysis.get("path_bindings", {}).get("p0", []):
            aux_id = binding["id"]
            curie = aux_id.split("_", 2)[2]
            name = nodes.get(curie, {}).get("name", curie)
            rows.append((score, curie, name, aux_id))
    rows.sort(key=lambda r: -(r[0] or 0))

    for score, curie, name, aux_id in rows[:top_n]:
        preds, srcs, pubs = set(), set(), set()
        for edge_id in aux.get(aux_id, []):
            edge = edges.get(edge_id)
            if not isinstance(edge, dict) or curie not in (edge.get("subject"), edge.get("object")):
                continue
            preds.add(edge.get("predicate"))
            for s in edge.get("sources", []):
                if s.get("resource_role") == "primary_knowledge_source":
                    srcs.add(s["resource_id"])
            for attr in edge.get("attributes", []):
                if attr.get("attribute_type_id") == "biolink:publications":
                    val = attr.get("value")
                    pubs.update(val if isinstance(val, list) else [val])
        print(f"{score:>5}  {name} ({curie})")
        print(f"       predicates: {sorted(p for p in preds if p)}")
        print(f"       primary sources: {sorted(srcs)}")
        if pubs:
            print(f"       publications: {sorted(pubs)[:5]}")
    print(f"\n({len(rows)} total nodes; showing top {min(top_n, len(rows))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
