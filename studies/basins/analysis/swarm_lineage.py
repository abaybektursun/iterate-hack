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
    ap.add_argument("--drop-bad", action="store_true", help="drop links the board rules out, at most 2 %% of the answer (kept in lineage.json 'dropped')")
    ap.add_argument("--reuse-answer", action="store_true", help="read calls/lineage.out instead of asking the judge again")
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
    if args.reuse_answer:  # the answer of an earlier call of this script on the same judge folder
        links = json.loads(re.search(r"\{.*\}", (d / "calls" / "lineage.out").read_text().split("\n[usage]")[0], re.S).group(0))["links"]
    else:
        links = J.ask(PROMPT.format(items=items), d / "calls" / "lineage.txt")["links"]
    # A link the board rules out (an id not on it, or a parent posted after its child) is dropped and kept in "dropped".
    ok = lambda l: l["child"] in order and l["parent"] in order and order[l["parent"]] < order[l["child"]]
    dropped = [l for l in links if not ok(l)]
    assert not dropped or args.drop_bad, f"links the board rules out: {dropped}"
    assert len(dropped) <= 0.02 * len(links), f"{len(dropped)} of {len(links)} links ruled out: too many to drop"
    links = [l for l in links if ok(l)]
    for l in links:
        assert l["relation"] in RELS, f"bad relation: {l}"
    got = {(l["child"], l["parent"]) for l in links}
    links += [{"child": c, "parent": p, "relation": "named", "why": "id named in the item"} for c, p in sorted(explicit - got)]
    for l in links:
        l["explicit"] = (l["child"], l["parent"]) in explicit
    out = {"links": links, "n_explicit": len(explicit), "explicit_also_found_by_judge": len(explicit & got), "dropped": dropped}
    (d / "lineage.json").write_text(json.dumps(out, indent=1))
    from collections import Counter
    print(f"dropped {len(dropped)} links the board rules out")
    print(f"{len(links)} links ({dict(Counter(l['relation'] for l in links))}); explicit {len(explicit)}, judge found {len(explicit & got)} of them")
