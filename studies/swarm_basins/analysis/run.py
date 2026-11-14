# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35", "numpy", "scipy", "scikit-learn", "anthropic>=0.40"]
# ///
"""Swarm basins: which research basins the team's agents explore, from the board. Laptop; the judge is the
Anthropic API (ANTHROPIC_API_KEY). Reads the board and the events; writes nothing to them.

    PYTHONPATH=. uv run studies/swarm_basins/analysis/run.py --arm live          # next folder results/swarm/live-<nn>/
    PYTHONPATH=. uv run studies/swarm_basins/analysis/run.py --arm live --dry    # fetch and build prompts, no API calls

Steps:
1. Items: every board item (idea, work, result, knowledge, skill; open and closed) from a scan of the table, joined
   to its `board post` event for the agent and session.
2. Partition: the judge groups all items by research approach, R=3 times with shuffled orders and anonymous ids.
   Basins = the partition with the highest mean adjusted Rand to the others; stability = that mean.
3. Triplets: "is B or C closer in research approach to A?", each asked in both orders; answers that flip with
   the order are dropped. About 90 appearances per item.
4. Checks: the basins must predict the triplets better than the same basins permuted over items; the triplets
   must be predicted better by the map than by same-author or same-kind labels.
5. Coverage: basins over time, the share of the largest basin, and the switch rate of each person's sequence of
   posts against the same posts shuffled in time (below the null = agents stay in a basin: hill climbing).
Judgments are cached in runs/swarm_basins/judgments.jsonl (not committed), so a rerun pays only for new items.
"""
import argparse
import hashlib
import json
import os
import pathlib
import random
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from sklearn.metrics import adjusted_rand_score

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from studies.swarm_basins.lib import basin_map as bm  # noqa: E402

# Model ids from the Claude 5 family list (claude-haiku-5-5, claude-sonnet-5-5).
TRIPLET_MODEL = "claude-haiku-5-5"
PARTITION_MODEL = "claude-sonnet-5-5"
PROMPT_VERSION = "v1"
CACHE = ROOT / "runs" / "swarm_basins" / "judgments.jsonl"
CONTEXT = ("The items come from the shared board of a research team at a hackathon. The team measures how much of "
           "a published RL gain on math (Olmo 3 RL-Zero-Math vs its base model) an untrained base model reaches with "
           "no training. Items are ideas, claims of work, results, knowledge and skills.")

PARTITION = """{context}

Here are {n} board items, each with an anonymous id.

{items}

Group the items by RESEARCH APPROACH: the question being asked and the method used to answer it. Two items belong
to the same group when they pursue the same approach, even if one is an idea, one a claim of work and one a
result, and even if wording or author differ. Make between 3 and 12 groups. Every id must appear in exactly one group.
Reply with JSON only: {{"groups": [{{"name": "<3-8 word name of the approach>", "ids": ["<id>", ...]}}, ...]}}"""

TRIPLET = """{context}

Item A: {a}

Item B: {b}

Item C: {c}

Which item, B or C, pursues a research approach (question and method) closer to item A's? Ignore wording, author,
and whether an item is an idea, a claim of work or a result. Reply with one letter: B or C."""


def items_from_board():
    import team
    from boto3.dynamodb.conditions import Attr

    table, rows, query = team.table(), [], {"FilterExpression": Attr("sk").eq("item")}
    while True:
        page = table.scan(**query)
        rows += page["Items"]
        if "LastEvaluatedKey" not in page:
            break
        query["ExclusiveStartKey"] = page["LastEvaluatedKey"]
    posts = {}
    for _, ev in team.Store("events").items():
        argv = ev.get("argv", [])
        if ev.get("tool") == "board" and len(argv) == 3 and argv[0] == "post":
            posts[(ev["who"], argv[1], argv[2])] = ev
    items = []
    for r in sorted(rows, key=lambda r: int(r["at_ns"])):
        ev = posts.get((r["who"], r["kind"], r["text"]), {})
        items.append({"id": r["id"], "kind": r["kind"], "text": r["text"], "who": r["who"], "at": r["at"],
                      "at_ns": int(r["at_ns"]), "open": "listed" in r, "ups": int(r["ups"]), "downs": int(r["downs"]),
                      "agent": ev.get("agent", ""), "session": ev.get("session", "")})
    return items


def short(text, n=500):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[:n] + " ..."


class Judge:
    def __init__(self, dry):
        self.dry = dry
        self.cache = {}
        if CACHE.exists():
            for line in open(CACHE):
                row = json.loads(line)
                self.cache[row["key"]] = row["answer"]
        if not dry:
            import anthropic

            if not os.environ.get("ANTHROPIC_API_KEY"):
                sys.exit("ANTHROPIC_API_KEY is not set in this shell (the judge is the Anthropic API).")
            self.client = anthropic.Anthropic(max_retries=8)

    def ask(self, model, prompt, max_tokens):
        key = hashlib.sha256(f"{model}\n{PROMPT_VERSION}\n{prompt}".encode()).hexdigest()
        if key in self.cache:
            return self.cache[key]
        if self.dry:
            return None
        msg = self.client.messages.create(model=model, max_tokens=max_tokens, temperature=0,
                                          messages=[{"role": "user", "content": prompt}])
        answer = "".join(b.text for b in msg.content if b.type == "text").strip()
        self.cache[key] = answer
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE, "a") as f:
            f.write(json.dumps({"key": key, "model": model, "answer": answer}) + "\n")
        return answer

    def many(self, model, prompts, max_tokens, workers=16):
        with ThreadPoolExecutor(workers) as pool:
            return list(pool.map(lambda p: self.ask(model, p, max_tokens), prompts))


def partitions(judge, items, reps, seed):
    out = []
    for r in range(reps):
        rng = random.Random(seed + r)
        order = list(range(len(items)))
        rng.shuffle(order)
        anon = {f"i{j}": order[j] for j in range(len(order))}
        lines = "\n".join(f"[i{j}] ({items[order[j]]['kind']}) {short(items[order[j]]['text'], 300)}" for j in range(len(order)))
        answer = judge.ask(PARTITION_MODEL, PARTITION.format(context=CONTEXT, n=len(items), items=lines), 8000)
        if answer is None:
            out.append(None)
            continue
        groups = json.loads(answer[answer.index("{"):answer.rindex("}") + 1])["groups"]
        labels = [-1] * len(items)
        names = []
        for g, group in enumerate(groups):
            names.append(group["name"])
            for i in group["ids"]:
                assert i in anon, f"partition {r}: unknown id {i}"
                assert labels[anon[i]] == -1, f"partition {r}: id {i} in two groups"
                labels[anon[i]] = g
        missing = [items[k]["id"] for k, l in enumerate(labels) if l == -1]
        assert not missing, f"partition {r}: {len(missing)} items in no group: {missing[:5]}"
        out.append({"labels": labels, "names": names})
    return out


def triplets(judge, items, per_item, seed):
    rng = random.Random(seed)
    n = len(items)
    plan = []
    for a in range(n):
        for _ in range(per_item // 3):
            b, c = rng.sample([i for i in range(n) if i != a], 2)
            plan.append((a, b, c))
    text = [short(it["text"]) for it in items]
    prompts = [TRIPLET.format(context=CONTEXT, a=text[a], b=text[x], c=text[y])
               for a, b, c in plan for x, y in ((b, c), (c, b))]
    answers = judge.many(TRIPLET_MODEL, prompts, 5)
    if any(ans is None for ans in answers):
        return plan, None, None
    kept, dropped = [], 0
    for t, (a, b, c) in enumerate(plan):
        first, second = answers[2 * t][:1].upper(), answers[2 * t + 1][:1].upper()
        assert first in "BC" and second in "BC", (answers[2 * t], answers[2 * t + 1])
        pick1 = b if first == "B" else c      # first order: B=b, C=c
        pick2 = c if second == "B" else b     # second order: B=c, C=b
        if pick1 != pick2:
            dropped += 1
            continue
        kept.append((a, pick1, c if pick1 == b else b))
    return plan, np.array(kept), dropped


def next_run_dir(arm):
    base = ROOT / "studies" / "swarm_basins" / "results" / "swarm"
    nn = 1 + max([int(p.name.rsplit("-", 1)[1]) for p in base.glob(f"{arm}-*")] or [0])
    out = base / f"{arm}-{nn:02d}"
    out.mkdir(parents=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="live")
    ap.add_argument("--per-item", type=int, default=90, help="triplet appearances per item")
    ap.add_argument("--reps", type=int, default=3, help="partitions with shuffled orders")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    items = items_from_board()
    n = len(items)
    print(f"{n} board items: " + ", ".join(f"{k} {v}" for k, v in Counter(i["kind"] for i in items).items()))
    assert n >= 12, f"only {n} board items: too few for a basin map"
    judge = Judge(args.dry)
    parts = partitions(judge, items, args.reps, args.seed)
    plan, T, dropped = triplets(judge, items, args.per_item, args.seed)
    if args.dry:
        print(f"dry run: {args.reps} partition prompts, {2 * len(plan)} triplet prompts "
              f"({sum(p is not None for p in parts)} partitions and "
              f"{'all' if T is not None else 'not all'} triplets already cached)")
        return

    out = next_run_dir(args.arm)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    (out / "run.json").write_text(json.dumps({"commit": sha, "argv": sys.argv, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                              "triplet_model": TRIPLET_MODEL, "partition_model": PARTITION_MODEL,
                                              "prompt_version": PROMPT_VERSION}, indent=1))

    # basins: the medoid partition
    aris = np.array([[adjusted_rand_score(p["labels"], q["labels"]) for q in parts] for p in parts])
    mean_ari = (aris.sum(1) - 1) / max(len(parts) - 1, 1)
    best = parts[int(np.argmax(mean_ari))]
    raw = np.array(best["labels"])
    order = np.argsort(-np.bincount(raw))
    labels = bm.by_size(raw)
    names = [best["names"][g] for g in order]
    k = len(names)

    # checks
    who = [it["who"] for it in items]
    kind = [it["kind"] for it in items]
    acc2d, _ = bm.heldout(n, T)
    X = bm.tste(n, T)
    checks = {
        "n_items": n, "n_triplets_asked": len(plan), "n_triplets_kept": int(len(T)),
        "order_consistency": 1 - dropped / len(plan),
        "partition_stability_mean_ari": float(mean_ari.max()), "partition_pairwise_ari": aris.round(3).tolist(),
        "partition_k": [len(p["names"]) for p in parts],
        "basins_predict_triplets": bm.label_null(labels, T),
        "map2d_heldout_agreement": acc2d,
        "same_author_agreement": bm.label_agreement(who, T),
        "same_kind_agreement": bm.label_agreement(kind, T),
    }

    # coverage over time
    t_order = np.argsort([it["at_ns"] for it in items])
    seen, timeline = set(), []
    for j, idx in enumerate(t_order):
        seen.add(int(labels[idx]))
        timeline.append({"at": items[idx]["at"], "n_posts": j + 1, "n_basins": len(seen)})
    by_person = defaultdict(list)
    by_session = defaultdict(list)
    for idx in t_order:
        by_person[who[idx]].append(int(labels[idx]))
        if items[idx]["session"]:
            by_session[items[idx]["session"]].append(int(labels[idx]))
    basins = []
    for g in range(k):
        members = [i for i in range(n) if labels[i] == g]
        basins.append({"basin": g, "name": names[g], "n": len(members),
                       "kinds": dict(Counter(kind[i] for i in members)), "people": dict(Counter(who[i] for i in members)),
                       "first_at": min(items[i]["at"] for i in members), "last_at": max(items[i]["at"] for i in members),
                       "open_work": sum(kind[i] == "work" and items[i]["open"] for i in members)})
    coverage = {
        "k": k, "largest_basin_share": float(np.bincount(labels).max() / n), "entropy_share": bm.entropy_share(labels, k),
        "ideas_without_work_or_result": [b["name"] for b in basins if b["kinds"].get("idea", 0) and not
                                         (b["kinds"].get("work", 0) or b["kinds"].get("result", 0))],
        "switch_by_person": bm.switch_null(by_person.values()),
        "switch_by_session": bm.switch_null(by_session.values()),
    }
    metrics = {"checks": checks, "coverage": coverage, "basins": basins}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    (out / "map.json").write_text(json.dumps({
        "basins": basins, "timeline": timeline,
        "items": [{**{key: it[key] for key in ("id", "kind", "who", "at", "open", "agent")}, "text": short(it["text"], 400),
                   "x": float(X[i, 0]), "y": float(X[i, 1]), "basin": int(labels[i])} for i, it in enumerate(items)]}, indent=1))

    # one triplet the map predicts and one it gets wrong, with the texts
    d = lambda i, j: float(((X[i] - X[j]) ** 2).sum())
    right = next(t for t in T if d(t[0], t[1]) < d(t[0], t[2]))
    wrong = next(t for t in T if d(t[0], t[1]) >= d(t[0], t[2]))
    ex = lambda t: {"A": items[t[0]]["text"], "judge_closer": items[t[1]]["text"], "judge_farther": items[t[2]]["text"]}
    (out / "examples.json").write_text(json.dumps({"map_agrees": ex(right), "map_disagrees": ex(wrong)}, indent=1))

    print(f"wrote {out.relative_to(ROOT)}")
    print(json.dumps({"checks": {k2: v for k2, v in checks.items() if k2 != "partition_pairwise_ari"},
                      "coverage": coverage, "basins": [(b["name"], b["n"]) for b in basins]}, indent=1))


if __name__ == "__main__":
    main()
