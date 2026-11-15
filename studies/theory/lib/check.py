# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The mechanical steps of a theory round (.claude/skills/theory/SKILL.md). No model judges anything here.

  uv run studies/theory/lib/check.py dump <round dir> [--cutoff 2026-11-14T23:00:00] [--skip <word> ...]
      creates the round folder with before.jsonl and after.jsonl: every result and knowledge item of the board
      posted before, and at or after, the cutoff (id, kind, at, who, text). Without --cutoff, the cutoff is the
      posting time (UTC) of the item three quarters of the way through, so the newest quarter is held out.
      --skip drops items whose text holds the word.
  uv run studies/theory/lib/check.py check <round dir>
      targets.jsonl: every target's item is in after.jsonl, its quote is in the item's text, its value is in the quote.
      theories/*.json: at least 3 predictions; every quoted item is in before.jsonl and holds the quote.
      Then writes targets_blind.jsonl (id, what, unit), the only target file a predictor may see.
  uv run studies/theory/lib/check.py score <round dir>
      predictions/<name>.jsonl holds {id, value} for every target; null-1 and null-2 are the predictor without a theory.
      For each theory: on how many targets it is closer to the measured value than each null, and on how many farther.
      noise = |closer - farther| of null-1 against null-2. A theory beats the null when its closer - farther against
      each null is above noise. Writes metrics.json and prints the table.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def write(path, rows):
    Path(path).write_text("".join(json.dumps(row) + "\n" for row in rows))


def dump(folder, cutoff, skip):
    from boto3.dynamodb.conditions import Key

    from board import rows

    items = [i for kind in ("result", "knowledge") for i in rows(IndexName="new", KeyConditionExpression=Key("listed").eq(kind))]
    keep = lambda i: {"id": i["id"], "kind": i["kind"], "at": i["at"][:19].replace(" ", "T"), "who": i["who"], "text": i["text"]}
    items = sorted((keep(i) for i in items if not any(word in i["text"] for word in skip)), key=lambda i: i["at"])
    cutoff = cutoff or items[len(items) * 3 // 4]["at"]
    folder.mkdir(parents=True)  # a round folder is written once
    before = [i for i in items if i["at"] < cutoff]
    after = [i for i in items if i["at"] >= cutoff]
    write(folder / "before.jsonl", before)
    write(folder / "after.jsonl", after)
    print(f"{len(before)} items before {cutoff}, {len(after)} at or after")


def check(folder):
    before = {i["id"]: i["text"] for i in read(folder / "before.jsonl")}
    after = {i["id"]: i["text"] for i in read(folder / "after.jsonl")}
    wrong = []
    targets = read(folder / "targets.jsonl")
    for t in targets:
        if t["quote"] not in after.get(t["item"], ""):
            wrong.append(f"target {t['id']}: quote not in {t['item']} of after.jsonl")
        if f"{t['value']:g}" not in t["quote"].replace(",", ""):
            wrong.append(f"target {t['id']}: value {t['value']:g} not in its quote")
    for path in sorted((folder / "theories").glob("*.json")):
        theory = json.loads(path.read_text())
        if len(theory["predictions"]) < 3:
            wrong.append(f"{path.name}: fewer than 3 predictions")
        for cited in theory["explains"] + theory["conflicts"]:
            if cited["quote"] not in before.get(cited["item"], ""):
                wrong.append(f"{path.name}: quote not in {cited['item']} of before.jsonl: {cited['quote'][:60]!r}")
    if wrong:
        sys.exit("\n".join(wrong))
    write(folder / "targets_blind.jsonl", [{"id": t["id"], "what": t["what"], "unit": t["unit"]} for t in targets])
    print(f"{len(targets)} targets and {len(list((folder / 'theories').glob('*.json')))} theories pass; wrote targets_blind.jsonl")


def score(folder):
    value = {t["id"]: t["value"] for t in read(folder / "targets.jsonl")}
    error = {}
    for path in sorted((folder / "predictions").glob("*.jsonl")):
        predicted = {p["id"]: p["value"] for p in read(path)}
        assert predicted.keys() == value.keys(), f"{path.name}: its target ids differ from targets.jsonl"
        error[path.stem] = {t: abs(predicted[t] - value[t]) for t in value}

    def against(a, b):
        closer = sum(error[a][t] < error[b][t] for t in value)
        farther = sum(error[a][t] > error[b][t] for t in value)
        return {"closer": closer, "farther": farther, "net": closer - farther}

    noise = abs(against("null-1", "null-2")["net"])
    theories = {}
    for name in error:
        if name not in ("null-1", "null-2"):
            one, two = against(name, "null-1"), against(name, "null-2")
            theories[name] = {"vs_null_1": one, "vs_null_2": two, "beats_null": min(one["net"], two["net"]) > noise}
    metrics = {"targets": len(value), "noise": noise, "theories": theories}
    (folder / "metrics.json").write_text(json.dumps(metrics, indent=1) + "\n")
    print(f"{len(value)} targets; noise (null-1 against null-2, |closer - farther|) = {noise}")
    for name, m in sorted(theories.items(), key=lambda kv: -min(kv[1]["vs_null_1"]["net"], kv[1]["vs_null_2"]["net"])):
        print(f"{name:24} vs null-1 +{m['vs_null_1']['closer']} -{m['vs_null_1']['farther']}   "
              f"vs null-2 +{m['vs_null_2']['closer']} -{m['vs_null_2']['farther']}   {'beats the null' if m['beats_null'] else 'does not beat the null'}")


if __name__ == "__main__":
    command, folder, *rest = sys.argv[1:]
    folder = Path(folder)
    if command == "dump":
        cutoff = rest[rest.index("--cutoff") + 1] if "--cutoff" in rest else None
        dump(folder, cutoff, [rest[i + 1] for i, a in enumerate(rest) if a == "--skip"])
    else:
        {"check": check, "score": score}[command](folder)
