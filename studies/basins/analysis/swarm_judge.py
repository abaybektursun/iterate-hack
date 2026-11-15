"""Swarm map, step 2 (laptop, calls the OpenAI API, or the Claude Code CLI with --backend claude; no local model): LLM judgments over the board snapshot.

    python3 -m studies.basins.analysis.swarm_judge runs/swarm/board-<t>.json runs/swarm/judge-<t> --model <id>

Nodes are the board items plus "possible directions": a list the judge writes from DIRECTION.md alone, before it
sees any board item, so it marks the regions the swarm could have visited. The judge never sees who posted an item.
1. directions.json  - 20 possible directions for the mission (judge sees only DIRECTION.md).
2. partitions.jsonl - all nodes grouped by approach, twice, in two random orders (stability check).
3. triplets.jsonl   - "is B or C closer in approach to A?", every anchor x --per-anchor pairs, both orders.
4. calls/           - every prompt and raw answer, for reading the judge's work.
Control: two exact copies of one board item (ids ctl-1, ctl-2) must share the original's group and sit next to it.
The key is read from $OPENAI_API_KEY or ~/.config/openai/key. Every call's token usage is saved in calls/*.out.
"""
import argparse
import json
import os
import pathlib
import random
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[3]
CLI = os.environ.get("CLAUDE_CLI", "claude")
KEY_FILE = pathlib.Path.home() / ".config" / "openai" / "key"  # written by the person, chmod 600; never committed

DIRECTIONS = """Below is a research direction for a team. Without proposing anything the text already rules out, list
the 20 most plausible distinct approach families a strong research team could try for its mission (literature
methods, experiments, analyses). Cover the space broadly: decoding, prompting, test-time compute, model editing,
training-free methods, data and evaluation checks, interpretability. One family per entry, specific enough to run.

{direction}

Reply with JSON only: {{"directions": [{{"name": "<3-6 words>", "what": "<one sentence>"}}, ...]}}"""

PARTITION = """Below are {n} items from a research team's work board, plus possible directions. Each describes a piece
of work, idea, finding or result. Group them by APPROACH: the lever or method the item is about (for example a
sampling setting, a prompt cue, a grader, a weight edit, a literature finding about one method, team tooling).
Items about the same lever go together even if one is an idea and another a result. Use between {gmin} and {gmax}
groups: merge close levers rather than making groups of one or two items.

{items}

Reply with JSON only: {{"groups": [{{"name": "<3-6 words>", "ids": ["<id>", ...]}}, ...]}} with every id exactly once."""

COVERAGE = """Below are possible research directions (ids dir-..) and the items of a research team's work board.
For each direction, list the board items that substantially pursue it: run it, plan it, claim it, or report a
finding or result about it. Mentioning a direction in passing does not count. Tooling items pursue no direction.

DIRECTIONS:
{dirs}

BOARD ITEMS:
{items}

Reply with JSON only: {{"coverage": [{{"direction": "<dir id>", "items": ["<board id>", ...]}}, ...]}} with every
direction exactly once (an empty list when no item pursues it)."""

TRIPLETS = """Each question shows three items from a research team's board: A, B and C. Answer which of B or C is
closer to A in APPROACH (the lever or method it is about), not in wording, author or item type.

{questions}

Reply with JSON only: {{"answers": ["B" or "C", ...]}} with exactly {n} answers, in question order."""


def call_openai(prompt, model):
    key = os.environ.get("OPENAI_API_KEY") or KEY_FILE.read_text().strip()
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(4):  # retry only rate limits and server errors; anything else fails loudly
        try:
            r = json.load(urllib.request.urlopen(req, timeout=600))
            return r["choices"][0]["message"]["content"], r.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503) or attempt == 3:
                raise RuntimeError(f"OpenAI HTTP {e.code}: {e.read()[:300]}")
            time.sleep(10 * (attempt + 1))


def call_claude(prompt, model):
    with tempfile.TemporaryDirectory() as cwd:  # empty folder, no tools, settings or MCP: no project hook fires
        r = subprocess.run([CLI, "-p", "--model", model, "--tools", "", "--setting-sources", "", "--strict-mcp-config",
                            "--no-session-persistence"], input=prompt, capture_output=True, text=True, cwd=cwd, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"claude -p failed ({r.returncode}): {r.stdout[-300:]} {r.stderr[-300:]}")
    return r.stdout, {}


def ask(prompt, path):
    """One judge call; the prompt, the raw answer and the token usage are saved next to path."""
    path.write_text(prompt)
    text, usage = (call_openai if BACKEND == "openai" else call_claude)(prompt, MODEL)
    path.with_suffix(".out").write_text(text + "\n[usage] " + json.dumps(usage))
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise RuntimeError(f"no JSON in answer for {path.name}: {text[-300:]}")
    return json.loads(m.group(0))


def node_text(n):
    return f"[possible direction] {n['text']}" if n["kind"] == "possible" else f"[{n['kind']}] {n['text']}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshot")
    ap.add_argument("out")
    ap.add_argument("--backend", choices=["openai", "claude"], default="openai",
                    help="claude spends the person's Claude subscription: use it only when they agreed")
    ap.add_argument("--model", required=True, help="exact model id, checked against the provider's model list")
    ap.add_argument("--groups", type=int, nargs=2, default=[6, 12], help="range of group counts asked for")
    ap.add_argument("--reuse", default=None, help="judge folder whose directions.json and nodes.json to reuse (same nodes)")
    ap.add_argument("--steps", default="partitions,triplets,coverage", help="comma list of steps to run")
    ap.add_argument("--no-partitions", action="store_true", help="triplets only (to compare judges on the same questions)")
    ap.add_argument("--per-anchor", type=int, default=12)
    ap.add_argument("--batch", type=int, default=60)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--clip", type=int, default=700, help="characters of each item's text shown to the judge")
    args = ap.parse_args()
    BACKEND, MODEL = args.backend, args.model
    out = pathlib.Path(args.out)
    (out / "calls").mkdir(parents=True, exist_ok=True)
    rng = random.Random(0)
    board = json.loads(pathlib.Path(args.snapshot).read_text())

    if args.reuse:
        for f in ("directions.json", "nodes.json"):
            (out / f).write_text((pathlib.Path(args.reuse) / f).read_text())
        nodes = json.loads((out / "nodes.json").read_text())
    else:
        # 1. possible directions, from DIRECTION.md only
        d = ask(DIRECTIONS.format(direction=(ROOT / "DIRECTION.md").read_text()), out / "calls" / "directions.txt")["directions"]
        assert len(d) >= 10, d
        (out / "directions.json").write_text(json.dumps(d, indent=1))

        nodes = [{"id": b["id"], "kind": b["kind"], "who": b.get("who"), "at": b.get("at"), "at_ns": b.get("at_ns"),
                  "text": b["text"][:args.clip]} for b in board]
        nodes += [{"id": f"dir-{k:02d}", "kind": "possible", "who": None, "at": None, "at_ns": None,
                   "text": f"{x['name']}: {x['what']}"} for k, x in enumerate(d)]
        src = rng.choice([n for n in nodes if n["kind"] != "possible"])  # planted control: two exact copies of one item
        nodes += [{**src, "id": f"ctl-{k}", "control_of": src["id"]} for k in (1, 2)]
        rng.shuffle(nodes)
        (out / "nodes.json").write_text(json.dumps(nodes, indent=1))
    ids = [n["id"] for n in nodes]
    by_id = {n["id"]: n for n in nodes}
    print(f"{len(nodes)} nodes ({sum(n['kind'] == 'possible' for n in nodes)} possible directions)", flush=True)

    # 2. two partitions in two orders
    steps = args.steps.split(",")
    if "coverage" in steps:  # 5. which board items pursue each possible direction (two orders of the board)
        dirs = [n for n in nodes if n["kind"] == "possible"]
        real = [n for n in nodes if n["kind"] != "possible" and not n.get("control_of")]
        with open(out / "coverage.jsonl", "w") as f:
            for r in range(2):
                order = real[:]
                random.Random(10 + r).shuffle(order)
                cov = ask(COVERAGE.format(dirs="\n".join(f"{n['id']}: {n['text']}" for n in dirs),
                                          items="\n".join(f"{n['id']}: [{n['kind']}] {n['text']}" for n in order)),
                          out / "calls" / f"coverage-{r}.txt")["coverage"]
                assert sorted(c["direction"] for c in cov) == sorted(n["id"] for n in dirs), f"coverage {r}: directions mismatch"
                bad = [i for c in cov for i in c["items"] if i not in {n["id"] for n in real}]
                assert not bad, f"coverage {r}: unknown ids {bad}"
                f.write(json.dumps({"order": r, "coverage": cov}) + "\n")
                print(f"coverage {r}: {sum(bool(c['items']) for c in cov)}/{len(cov)} directions pursued", flush=True)

    with open(out / "partitions.jsonl", "w" if "partitions" in steps else "a") as f:
        for r in range(0 if args.no_partitions or 'partitions' not in steps else 2):
            order = ids[:]
            random.Random(r).shuffle(order)
            items = "\n".join(f"{i}: {node_text(by_id[i])}" for i in order)
            groups = ask(PARTITION.format(n=len(order), items=items, gmin=args.groups[0], gmax=args.groups[1]), out / "calls" / f"partition-{r}.txt")["groups"]
            got = sorted(i for g in groups for i in g["ids"])
            assert got == sorted(ids), f"partition {r}: {len(got)} ids returned, {len(set(got))} distinct, {len(ids)} expected"
            f.write(json.dumps({"order": r, "groups": groups}) + "\n")
            print(f"partition {r}: {len(groups)} groups", flush=True)

    if "triplets" not in steps:
        raise SystemExit(0)
    # 3. triplets, both orders, in batches
    trng = random.Random(1)  # own generator: the same nodes give the same questions for every judge
    trips = []
    for a in ids:
        others = [i for i in ids if i != a]
        for _ in range(args.per_anchor):
            b, c = trng.sample(others, 2)
            trips += [(a, b, c, 0), (a, c, b, 1)]
    trng.shuffle(trips)
    batches = [trips[k:k + args.batch] for k in range(0, len(trips), args.batch)]

    def run(k):
        qs = "\n\n".join(f"Q{j + 1}.\nA: {node_text(by_id[a])}\nB: {node_text(by_id[b])}\nC: {node_text(by_id[c])}"
                         for j, (a, b, c, _) in enumerate(batches[k]))
        ans = ask(TRIPLETS.format(questions=qs, n=len(batches[k])), out / "calls" / f"triplets-{k:03d}.txt")["answers"]
        assert len(ans) == len(batches[k]), f"batch {k}: {len(ans)} answers for {len(batches[k])} questions"
        return [{"a": a, "b": b, "c": c, "flip": fl, "answer": x, "pick": {"B": b, "C": c}.get(str(x).strip().upper()[:1])}
                for (a, b, c, fl), x in zip(batches[k], ans)]

    with ThreadPoolExecutor(args.workers) as pool:
        results = [row for rows in pool.map(run, range(len(batches))) for row in rows]
    with open(out / "triplets.jsonl", "w") as f:
        for row in results:
            f.write(json.dumps(row) + "\n")
    print(f"triplets: {len(results)} judgments in {len(batches)} calls", flush=True)
