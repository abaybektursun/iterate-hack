"""Swarm map, idea-tree step (laptop, one judge call): which earlier board items each item builds on, and how.

    python3 -m studies.basins.analysis.swarm_lineage runs/swarm/judge-<t> --model gpt-6.1-sol

Explicit links are ids an item names (in its text or comments). The judge adds links nobody wrote down and labels
every link: variation (same idea, changed setting or method), combination (merges two or more parents), refinement
(fixes or narrows a parent), result_of (reports the outcome of a parent's work), claims (a work item taking up an
idea), critique (questions or refutes a parent). A parent must be posted before its child; a link to an unknown or
later id stops the script. Check: share of explicit links that the judge also returns (it sees the texts, so this
is a floor on attention, not a proof). Writes <judge>/lineage.json.
"""
import argparse
import json
import pathlib
import re

from studies.basins.analysis import swarm_judge as J

RELS = ("variation", "combination", "refinement", "result_of", "claims", "critique")
PROMPT = """Below are the items of a research team's work board, oldest first. For each item, list the EARLIER items
it builds on, and how. Use only these relations: variation (same idea with a changed setting, model or method),
combination (merges two or more earlier ideas; give every merged parent), refinement (fixes, narrows or extends a
parent), result_of (reports the outcome of a parent's work), claims (a work item taking up an idea), critique
(questions or refutes a parent). Include links the text states (an id it names) and links that are clear from the
content. An item may have no parent. Do not link tooling to research unless it is built for that research.

{items}

Reply with JSON only: {{"links": [{{"child": "<id>", "parent": "<earlier id>", "relation": "<one of the six>",
"why": "<at most 12 words>"}}, ...]}}"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("judge")
    ap.add_argument("--model", required=True)
    ap.add_argument("--snapshot", default=None, help="board snapshot, for comments (default: the judge's own)")
    args = ap.parse_args()
    J.BACKEND, J.MODEL = "openai", args.model
    d = pathlib.Path(args.judge)
    nodes = sorted([n for n in json.loads((d / "nodes.json").read_text()) if n["kind"] != "possible" and not n.get("control_of")],
                   key=lambda n: int(n["at_ns"]))
    order = {n["id"]: k for k, n in enumerate(nodes)}
    snap = {b["id"]: b for b in json.loads(pathlib.Path(args.snapshot).read_text())} if args.snapshot else {}
    full = {n["id"]: snap.get(n["id"], {}).get("text", n["text"]) + " " + " ".join(c.get("text") or "" for c in snap.get(n["id"], {}).get("comments", []))
            for n in nodes}
    explicit = {(n["id"], m) for n in nodes for m in set(re.findall(r"\b(?:idea|work|result|knowledge|skill)-[0-9a-f]{6}\b", full[n["id"]]))
                if m in order and order[m] < order[n["id"]]}
    items = "\n\n".join(f"{n['id']} [{n['kind']}, {n['at']}]: {n['text']}" for n in nodes)
    links = J.ask(PROMPT.format(items=items), d / "calls" / "lineage.txt")["links"]
    for l in links:
        assert l["child"] in order and l["parent"] in order, f"unknown id in {l}"
        assert order[l["parent"]] < order[l["child"]], f"parent posted after child: {l}"
        assert l["relation"] in RELS, f"bad relation: {l}"
    got = {(l["child"], l["parent"]) for l in links}
    links += [{"child": c, "parent": p, "relation": "named", "why": "id named in the item"} for c, p in sorted(explicit - got)]
    for l in links:
        l["explicit"] = (l["child"], l["parent"]) in explicit
    out = {"links": links, "n_explicit": len(explicit), "explicit_also_found_by_judge": len(explicit & got)}
    (d / "lineage.json").write_text(json.dumps(out, indent=1))
    from collections import Counter
    print(f"{len(links)} links ({dict(Counter(l['relation'] for l in links))}); explicit {len(explicit)}, judge found {len(explicit & got)} of them")
