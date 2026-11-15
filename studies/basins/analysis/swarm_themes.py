"""Swarm map, a second level (laptop, calls the OpenAI API): the judge groups the clusters of one map into themes.

    python3 -m studies.basins.analysis.swarm_themes studies/basins/results/swarm/<map run> studies/basins/results/swarm/themes-<nn> --model <id>

Reads the map run's summary.json and map.json. One call per order; a planted copy of the largest cluster is the control.
Writes metrics.json and run.json to the new run folder, and the prompts and raw answers (board text) to
runs/swarm/<themes run>-calls/. Spec: studies/basins/specs/SPEC_themes.md.
"""
import argparse
import itertools
import json
import pathlib
import random
import re
import subprocess
import sys

from studies.basins.analysis.swarm_judge import call_openai

PROMPT = """Below are {n} clusters of items from the board of a research team. Each cluster was formed because its items use the same method.

Put the clusters into 3 to 5 themes. Clusters in one theme do the same kind of work. Every cluster goes into exactly one theme.
Give each theme a name of one or two plain words. Give each cluster a short name of one or two plain words.

{clusters}

Reply with JSON only: {{"themes": [{{"name": "...", "clusters": ["<label>", ...]}}, ...], "short": {{"<label>": "...", ...}}}}"""

ap = argparse.ArgumentParser()
ap.add_argument("map_run", type=pathlib.Path)
ap.add_argument("out", type=pathlib.Path)
ap.add_argument("--model", required=True)
args = ap.parse_args()
if args.out.exists():
    sys.exit(f"{args.out} exists: a rerun gets the next number")
S = json.loads((args.map_run / "summary.json").read_text())
M = json.loads((args.map_run / "map.json").read_text())
calls = pathlib.Path("runs/swarm") / (args.out.name + "-calls")
calls.mkdir(parents=True, exist_ok=True)

basins = sorted(S["basins"], key=lambda b: -b["board_items"])
items = {b["basin"]: sorted((n for n in M["nodes"] if n["basin"] == b["basin"] and n["kind"] != "possible" and not n.get("control_of")),
                            key=lambda n: n["at_ns"])[:8] for b in basins}
CTL = "ctl"  # the planted copy of the largest cluster
shown = [(b["basin"], b["name"]) for b in basins] + [(CTL, "Unnamed")]


def one_order(k):
    order = shown[:]
    random.Random(k).shuffle(order)
    label = {key: f"K{i + 1}" for i, (key, _) in enumerate(order)}
    text = "\n\n".join(f"{label[key]}. {name}\n" + "\n".join("- " + n["text"][:180].replace("\n", " ") for n in items[basins[0]["basin"] if key == CTL else key])
                       for key, name in order)
    prompt = PROMPT.format(n=len(order), clusters=text)
    (calls / f"order-{k}.txt").write_text(prompt)
    answer, usage = call_openai(prompt, args.model)
    (calls / f"order-{k}.out").write_text(answer + "\n[usage] " + json.dumps(usage))
    r = json.loads(re.search(r"\{.*\}", answer, re.S).group(0))
    back = {v: key for key, v in label.items()}
    themes = [{"name": t["name"], "clusters": [back[c] for c in t["clusters"]]} for t in r["themes"]]
    seen = sorted((str(c) for t in themes for c in t["clusters"]))
    if seen != sorted(str(key) for key, _ in shown):
        raise RuntimeError(f"order {k}: the judge's themes do not hold every cluster exactly once: {seen}")
    return themes, {back[c]: v for c, v in r["short"].items()}, usage


runs = [one_order(k) for k in (0, 1)]
theme_of = [{c: i for i, t in enumerate(themes) for c in t["clusters"]} for themes, _, _ in runs]
control = [of[CTL] == of[basins[0]["basin"]] for of in theme_of]
keys = [b["basin"] for b in basins]
pairs = list(itertools.combinations(keys, 2))
agree = sum((theme_of[0][a] == theme_of[0][b]) == (theme_of[1][a] == theme_of[1][b]) for a, b in pairs)
strip = lambda themes: [{"name": t["name"], "clusters": [c for c in t["clusters"] if c != CTL]} for t in themes]
args.out.mkdir(parents=True)
(args.out / "metrics.json").write_text(json.dumps({
    "map_run": str(args.map_run), "judge": args.model, "n_clusters": len(keys),
    "themes": strip(runs[0][0]), "short": {str(k): v for k, v in runs[0][1].items() if k != CTL},
    "themes_order1": strip(runs[1][0]), "pairs_agree": [agree, len(pairs)],
    "control": {"copy_of": basins[0]["basin"], "same_theme": control},
    "usage": [u for _, _, u in runs]}, indent=1))
(args.out / "run.json").write_text(json.dumps({
    "commit_of_code_before_this_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
    "command": "python3 -m studies.basins.analysis.swarm_themes " + " ".join(sys.argv[1:]),
    "snapshot": json.loads((args.map_run / "run.json").read_text())["snapshot"],
    "calls": str(calls) + " (prompts and raw answers, board text, not committed)"}, indent=1))
print(json.dumps({"themes": [(t["name"], [next(b["name"] for b in basins if b["basin"] == c) for c in t["clusters"]]) for t in strip(runs[0][0])],
                  "pairs_agree": [agree, len(pairs)], "control": control}, indent=1))
