"""Build data.json for the derby prototype: the MATH-500 score lines of the board, one lane per method family of the
untrained base model, from the live board (/data of the local sitelab server).

    python3 studies/sitelab/prototypes/derby/build.py        (the server of studies/sitelab/serve.py must run)

Definitions (the page states them and recomputes them from the same rules, stored in data.json, on live data):
- a score line counts when its benchmark is MATH-500 and its n is 500.
- RL posts: the lines with model rl. One sample: the earliest line whose configuration starts "plain, T 1.0".
  Best: the highest `right` (the earliest such line).
- left out: lines with model other whose configuration names another trained checkpoint (EXCLUDE): they are not
  a method applied to the base.
- family of a line with model base or other: the first rule of RULES whose pattern matches its configuration
  (after "no steering" is removed). A rule with model "other" only takes lines of model other.
- a lane's best at a time: the highest `right` among its lines posted up to then. An advance: a result that raises it.
- one sample: a configuration that names no vote and no restart.
The build fails when a line of model other matches neither EXCLUDE nor a weight rule, or when private text remains.
"""
import datetime, json, pathlib, re, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
SRC = "http://127.0.0.1:8777/data"
get = lambda u: json.loads(urllib.request.urlopen(u, timeout=30).read())

EXCLUDE = r"Code-RL|RL-Zero|RL step|^RL \("
RULES = [  # key, engraved name, what the plate says under it, pattern, model the rule is limited to
    ["edit", "Weight edit", "base + a weight difference", r"theta|top-?8|singular directions|RL-Math|matched-norm|m18", "other"],
    ["sft", "Think-SFT", "base fine-tuned, no reward", r"Think-SFT", "other"],
    ["vote", "Cue + vote", "vote over several samples", r"vote", ""],
    ["steer", "Cue + steering", "steering or neurons zeroed", r"neurons zeroed|steer|logit bias|random direction|edit of one matrix", ""],
    ["cue", "Opening cue", "one answer, base weights", r"\bcue\b", ""],
    ["plain", "Plain prompt", "no cue, base weights", r"", ""],
]
ORDER = ["plain", "cue", "steer", "vote", "edit", "sft"]  # lane 1 .. 6
ONE = r"vote|restart"  # a configuration that matches is not one sample

board = get(SRC)
lines = [s for s in board["scores"] if s["benchmark"] == "MATH-500" and s["n"] == 500]
assert len(lines) > 50, len(lines)


def family(s):
    if s["model"] == "rl":
        return "rl"
    if s["model"] == "other" and re.search(EXCLUDE, s["config"], re.I):
        return None
    cfg = re.sub(r"no steering", "", s["config"], flags=re.I)
    for key, _, _, pat, model in RULES:
        if (not model or model == s["model"]) and re.search(pat, cfg, re.I):
            assert s["model"] != "other" or model == "other", ("a changed model matched no weight rule", s)
            return key
    raise AssertionError(s)


ms = lambda sk: int(sk.split("#")[0]) // 1_000_000
clip = lambda t, n: t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"
rows = []
for s in sorted(lines, key=lambda s: s["sk"]):
    f = family(s)
    if f:
        rows.append({"t": ms(s["sk"]), "r": s["result"], "m": s["model"], "v": s["right"], "c": s["config"], "k": s["tokens"], "w": s["who"], "f": f})

items = {i["id"]: i for i in board["items"]}
titles = {}
for rid in sorted({r["r"] for r in rows}):
    title = (board["plain"].get(rid) or {}).get("title")
    if not title:
        if rid not in items:  # /data lists only the newest items of a kind; the site refuses more than 3 requests a second
            time.sleep(0.4)
            one = get(f"{SRC}/{rid}")
            items[rid] = one["item"]
            title = ((one.get("plain") or {}).get(rid) or {}).get("title")
        title = title or clip(re.sub(r"^title: ", "", items[rid]["text"].split("\n")[0]), 110)
    titles[rid] = title

handles = {i["who"] for i in board["items"]} | {s["who"] for s in board["scores"]}
assert {r["w"] for r in rows} <= handles
data = {"built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "t1": max(ms(s["sk"]) for s in board["scores"]), "exclude": EXCLUDE, "rules": RULES, "order": ORDER, "one": ONE,
        "left_out": sum(1 for s in lines if family(s) is None), "scores": rows, "titles": titles}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
assert len(blob.encode()) < 200_000, len(blob)
assert not re.search(r"/home/|/Users/|[\w.+-]+@[\w-]+\.[a-z]{2,}|sk-[A-Za-z0-9]{16}|AKIA[A-Z0-9]{12}|hf_[A-Za-z0-9]{20}", blob), "private text"
(HERE / "data.json").write_text(blob)

print(f"data.json {len(blob.encode()) // 1024} kB, {len(rows)} lines kept of {len(lines)} MATH-500 n 500 lines, {data['left_out']} left out")
t0 = rows[0]["t"]
for key in ORDER + ["rl"]:
    best, steps = 0, []
    for r in rows:
        if r["f"] == key and r["v"] > best:
            best = r["v"]
            steps.append(f"{best}@{(r['t'] - t0) / 3.6e6:.1f}h")
    one = max((r["v"] for r in rows if r["f"] == key and not re.search(ONE, r["c"], re.I)), default=None)
    print(f"  {key:6} lines {sum(r['f'] == key for r in rows):3}  best {best}  best one sample {one}  steps {' '.join(steps)}")
