"""The explore results page: reads runs/explore (laptop, runs the best programs once to draw them), writes one
self-contained HTML page. Published privately at https://claude.ai/artifact/XQwm42PhgcxWjtro4WXN1E.

    python3 studies/explore/analysis/page/build.py <out.html>
"""
import json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[4]
R = ROOT / "runs/explore"
PY = R / ".venv/bin/python"
T = ROOT / "studies/explore/tasks"

def rows(d):
    return [json.loads(l) for l in open(d / "log.jsonl")] if (d / "log.jsonl").exists() else []

def curve(rs):
    b, c = None, []
    for r in rs:
        if r["valid"] and r["score"] is not None:
            b = r["score"] if b is None else max(b, r["score"])
        c.append(b)
    return c

def exp(path):
    out = {}
    for d in sorted((R / path).iterdir()):
        if not d.is_dir(): continue
        arm, seed = d.name.rsplit("-s", 1)
        rs = rows(d)
        out.setdefault(arm, []).append({"seed": int(seed), "curve": curve(rs), "n": len(rs),
            "done": (d / "metrics.json").exists(),
            "pts": [[r["step"], r["score"] if r["valid"] else None] for r in rs]})
    return out

data = {"starter": {"circles26": 2.54138, "ahc014": 0.221686}}
data["c_mini"] = exp("circles26/main-01")
data["c_mini_abl"] = exp("circles26/main-02")
data["a_mini"] = exp("ahc014/main-01")
data["c_swe"] = exp("circles26/swe2-01")
data["a_swe"] = exp("ahc014/swe2-01")

# basin timeline: circles main-02 basin-s0 (gpt-5.4-mini), and ahc014 swe2 basin if labeled
def timeline(d):
    d = R / d
    if not (d / "basins.json").exists(): return None
    b = json.loads((d / "basins.json").read_text()); fl = json.loads((d / "flushes.json").read_text())
    rs = rows(d)
    return {"codebook": b["codebook"], "flushes": fl,
            "subs": [{"id": r["id"], "agent": r["agent"], "step": r["step"], "score": r["score"] if r["valid"] else None,
                      "basin": b["label"].get(r["id"]), "idea": r["idea"][:160]} for r in rs]}
data["tl_c_mini"] = timeline("circles26/main-02/basin-s0")
data["tl_a_mini"] = timeline("ahc014/main-01/basin-s0")

def best(d):
    rs = [r for r in rows(R / d) if r["valid"]]
    b = max(rs, key=lambda r: r["score"]); return R / d / "code" / f"{b['id']}.py", b

def run_prog(p, stdin=None):
    r = subprocess.run([str(PY), str(p)], input=stdin, capture_output=True, text=True, timeout=60)
    return r.stdout

# circles: starter, best gpt-5.4-mini (over main-01 and main-02), best SWE-2
circ = {}
circ["starter"] = {"score": 2.54138, "circles": json.loads([l for l in run_prog(T / "circles26/starter.py").splitlines() if l.startswith("{")][-1])["circles"]}
cands = [f"circles26/main-01/{a}-s{s}" for a in ["single","parallel","fnf","forget"] for s in range(5)]
bm = max((best(c) for c in cands), key=lambda x: x[1]["score"])
# prefer a non-starter-like hand layout too: best single run
bs = best("circles26/main-01/single-s0")
for key, (p, row) in {"mini_best_single": bs, "swe": max((best(f"circles26/swe2-01/{a}-s0") for a in ["single","fnf","basin","fnf_keep"]), key=lambda x: x[1]["score"])}.items():
    out = run_prog(p)
    circ[key] = {"score": row["score"], "idea": row["idea"][:200], "run": str(p.parent.parent.name), "id": row["id"],
                 "circles": json.loads([l for l in out.splitlines() if l.strip().startswith("{")][-1])["circles"]}
data["circles"] = circ

# ahc014 case 1: starter, best mini (forget-s0), best swe so far
inp = (T / "ahc014/data/1.in").read_text()
N, M = map(int, inp.split()[:2]); pts = list(map(int, inp.split()[2:2 + 2 * M]))
ah = {"N": N, "dots": [pts[i:i + 2] for i in range(0, 2 * M, 2)]}
def ops(p):
    t = run_prog(p, inp).split(); k = int(t[0]); v = list(map(int, t[1:1 + 8 * k]))
    return [v[i:i + 8] for i in range(0, 8 * k, 8)]
p, row = best("ahc014/main-01/forget-s0"); ah["mini"] = {"score": row["score"], "id": row["id"], "idea": row["idea"][:200], "ops": ops(p)}
sw = [best(f"ahc014/swe2-01/{a}-s0") for a in ["single","parallel","fnf","fnf_keep","forget","basin"] if any(r["valid"] for r in rows(R / f"ahc014/swe2-01/{a}-s0"))]
p, row = max(sw, key=lambda x: x[1]["score"]); ah["swe"] = {"score": row["score"], "id": row["id"], "run": p.parent.parent.name, "idea": row["idea"][:200], "ops": ops(p)}
data["ahc"] = ah

# optimizer share
import re
OPT = re.compile(r"scipy|minimize|SLSQP|gradient|anneal|penalty")
def optshare(path):
    n = k = 0
    for f in (R / path).glob("*/code/*.py"):
        n += 1; k += bool(OPT.search(f.read_text()))
    return [k, n]
data["opt"] = {"c_mini": optshare("circles26/main-01"), "c_swe": optshare("circles26/swe2-01")}
# assign-01: assigned methods per fresh branch, controls and the two literature arms
data["c_assign"] = exp("circles26/assign-01")
data["a_assign"] = exp("ahc014/assign-01")
data["assign_cmp"] = {t: json.loads((ROOT / f"studies/explore/results/{t}/assign-01/compare.json").read_text())["arms"]
                      for t in ("circles26", "ahc014")}
for k in ("c_assign", "a_assign"):  # the strong-list arm is left off the page (owner's request)
    data[k].pop("assign_sol", None)
for t in data["assign_cmp"]:
    data["assign_cmp"][t].pop("assign_sol", None)
p, row = best("circles26/assign-01/assign_mini-s0")
circ["assign"] = {"score": row["score"], "id": row["id"], "idea": row["idea"][:200],
                  "circles": json.loads([l for l in run_prog(p).splitlines() if l.strip().startswith("{")][-1])["circles"]}
data["seeds"] = json.loads((ROOT / "studies/explore/results/ahc014/swe2-seeds-01/summary.json").read_text())
import time
tpl = (pathlib.Path(__file__).parent / "template.html").read_text()
pathlib.Path(sys.argv[1]).write_text(tpl.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
                                     .replace("__SNAP__", time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())))
print({k: (len(v) if hasattr(v, "__len__") else v) for k, v in data.items()})
print(circ["mini_best_single"]["score"], circ["swe"]["score"], len(ah["mini"]["ops"]), len(ah["swe"]["ops"]), ah["swe"]["score"])
