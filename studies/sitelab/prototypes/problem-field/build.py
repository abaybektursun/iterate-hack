"""Build data.json for the problem-field prototype: one record per problem and one right/wrong vector per configuration,
on hard328 and MATH-500, from the committed per-problem rows of studies/rlneurons. Every total is checked against a stored
total (table.json, a readout or a manifest) and the build fails when one differs.

    python3 studies/sitelab/prototypes/problem-field/build.py
"""
import json, pathlib, re, subprocess, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
R = ROOT / "studies/rlneurons/results"
D = ROOT / "studies/rlneurons/data"
JOB = re.compile(r"[a-z]+-(11\d\d)-(\d{6})-[0-9a-f]{4}")


def load(p):
    return json.loads((R / p).read_text())


def rows(p):
    return [json.loads(line) for line in open(R / p)]


def when(text):
    """The launch time of the last job named in text, as 'MMDD-HHMMSS' (Pacific time, as written in the job id).
    The two RLN-4 cells of MATH-500 have no job id in the repository: their time is "" and they sort first."""
    ids = ["-".join(m) for m in JOB.findall(text)]
    assert ids, text[:200]
    return max(ids)


def when_of(folder):
    return when((R / folder / "run.json").read_text())


def bits(v):
    return "".join("1" if x else "0" for x in v)


def cfg(key, name, group, when_, src, stored, right, cap=None, tok=None, ans=None):
    right = [int(x) for x in right]
    assert sum(right) == stored, (key, sum(right), stored)
    c = {"k": key, "name": name, "group": group, "when": when_, "src": src, "total": stored, "r": bits(right)}
    if cap is not None:
        c["c"] = bits(cap)
    if tok is not None:
        c["t"] = tok
    if ans is not None:
        c["a"] = [(a or "")[:60] for a in ans]
    return c


def detail(rs, idx):
    """rs: one row per problem. Returns right, cap, tokens, answers in the order of idx."""
    by = {r["problem_index"]: r for r in rs}
    assert len(by) == len(rs) == len(idx), (len(by), len(rs), len(idx))
    o = [by[i] for i in idx]
    return ([r["score_v3"] for r in o], [r["cap_hit"] for r in o], [r["n_new"] + r.get("n_prefix", 0) for r in o],
            [r["extracted_v3"] for r in o])


def samples(folder, idx, label, group, key, stored4, per_sample=None):
    rs = [r for r in rows(folder + "/rows.jsonl") if r["attempt"] == 0]
    out, tot = [], 0
    for s in range(4):
        right, cap, tok, ans = detail([r for r in rs if r["sample"] == s], idx)
        tot += sum(right)
        if per_sample:
            assert sum(right) == per_sample[s], (folder, s)
        out.append(cfg(f"{key}|s{s}", f"{label}, sample {s + 1} of 4", group, when_of(folder), f"results/{folder}/rows.jsonl",
                       sum(right), right, cap, tok, ans))
    assert tot == stored4, (folder, tot, stored4)
    return out


# ---------------------------------------------------------------- hard328
def hard328():
    t = load("table/hard328-02/table.json")
    idx = t["problem_indices"]
    hard = {p["index"]: p for p in json.loads((D / "rln3/hard.json").read_text())}
    problems = [{"id": hard[i]["unique_id"], "tag": hard[i]["source"], "text": hard[i]["problem"][:320], "gold": hard[i]["answer"][:60]}
                for i in idx]
    man = load("axis/hard328-01/manifest.json")["arms"]
    edits = load("xreward/edits/readout.json")["cells"]
    tp = load("transplant/hard328-01/readout.json")["arms"]
    folders = {"base": "day1_3/hard328_base_cue_s4r2-01", "rl": "day1_3/hard328_rl_plain_s4r2-01",
               "think": "thinkvote/hard328_sft1_cue_s4-01", "dial4": "day1_3/hard328_top8x1.5_cue_s4-01"}
    wsp_when = time.strftime("%m%d-%H%M%S", time.gmtime(int(subprocess.run(
        ["git", "show", "-s", "--format=%ct", "bdba62b"], cwd=ROOT, capture_output=True, text=True, check=True).stdout) - 8 * 3600))
    group = {"base": "Base + cue", "rl": "RL-Zero-Math", "think": "Think-SFT", "mix": "Mixed votes", "relay": "Relay",
             "axis": "One sample, day 1", "other": "Think-SFT", "dial": "Weight edit: top-8 RL directions",
             "dial4": "Weight edit: top-8 RL directions", "transplant": "Weight edit: Think-SFT + a (RL - base)"}
    tr = rows("transplant/hard328-01/rows.jsonl")
    out = []
    for row in t["rows"]:
        key, v, src = row["key"], t["per_problem_right"][row["key"]], row["source"]
        if any(x not in (0, 1) for x in v):
            continue  # a mean over samples or orders: no single right or wrong per problem
        fam = key.split("|")[0]
        cap = tok = ans = None
        if fam in folders:
            w = when_of(folders[fam])
        elif fam == "mix":
            w = max(when_of(f) for f in folders.values())
        elif fam == "relay":
            w = when_of(src)
            writer, _, cut = key.split("|")[1].partition("->")[0], None, int(key.split("|")[2])
            right, cap, tok, ans = detail([r for r in rows(src + "/rows.jsonl") if r["writer"] == writer and r["cut"] == cut], idx)
            assert right == [int(x) for x in v], key
        elif fam == "axis":
            w = when(man[key.split("|")[1]]["job_id"])
        elif fam == "other":
            w = wsp_when
        elif fam == "dial":
            w = when(edits[re.search(r"\[(.+)\]", src).group(1)]["job_id"])
        elif fam == "transplant":
            arm = key.split("|")[1]
            w = when(" ".join(tp[arm]["jobs"]))
            right, cap, tok, ans = detail([r for r in tr if r["arm"] == arm], idx)
            assert right == [int(x) for x in v], key
        out.append(cfg(key, row["name"], group[fam], w, "results/table/hard328-02/table.json [" + key + "], from " + src,
                       round(row["right"]), v, cap, tok, ans))
    n4 = lambda k: round(4 * next(r["right"] for r in t["rows"] if r["key"] == k))
    for fam, label, key in (("base", "base + cue", "base|single"), ("rl", "RL plain", "rl|single"),
                            ("think", "Think-SFT + cue", "think|single"),
                            ("dial4", "base + 1.5 x top-8 RL directions + cue", "dial4|single")):
        out += samples(folders[fam], idx, label, group[fam], fam, n4(key), load(folders[fam] + "/readout.json")["each_sample"]["single_right"])
    cap = load("cap32/readout.json")["cells"]
    for name, label, g in (("sft_cue", "Think-SFT + cue", "Token cap 32,768"), ("rl_plain", "RL plain", "Token cap 32,768")):
        rs = rows(f"cap32/rows-01/{name}.jsonl")
        right, c, tok, ans = detail(rs, idx)
        w = when(cap[name]["job_id"])
        src = f"results/cap32/rows-01/{name}.jsonl"
        out.append(cfg(f"cap32|{name}|32768", f"{label}, one sample, cap 32,768", g, w, src, cap[name]["right_at_32768"], right, c, tok, ans))
        over = [x > 16384 or bool(h) for x, h in zip(tok, c)]
        out.append(cfg(f"cap32|{name}|16384", f"{label}, the same answers counted at cap 16,384", g, w, src,
                       cap[name]["right_at_16384_same_answers"], [r and not o for r, o in zip(right, over)], over,
                       [min(x, 16384) for x in tok], ["" if o else a for a, o in zip(ans, over)]))
    return {"label": "hard328", "title": "The 328 harder problems", "n": 328, "problems": problems, "configs": out,
            "a": "base|s0", "b": "rl|s0"}


# ---------------------------------------------------------------- MATH-500
def math500():
    v = load("axis/math500-01/vectors.json")
    man = load("axis/math500-01/manifest.json")["arms"]
    idx = v["problem_indices"]
    assert idx == list(range(500))
    meta = json.loads((D / "profile/math500_meta_v1.json").read_text())
    assert meta["unique_ids"] == v["unique_ids"]
    probs = json.loads((D / "rln4/math500.json").read_text())
    problems = [{"id": p["unique_id"], "tag": f"{meta['subject'][i]}, level {meta['level'][i]}", "text": p["problem"][:320],
                 "gold": p["answer"][:60]} for i, p in enumerate(probs)]
    rich = {}
    for arm, folder in (("base_cue", "day1_3/math500_base_cue-01"), ("rl_plain", "day1_3/math500_rl-01")):
        rs = [r for r in rows(folder + "/rows.jsonl") if r["attempt"] == 0]
        for s in range(4):
            rich[f"{arm}_s{s}"] = detail([r for r in rs if r["sample"] == s], idx)

    def grp(k):
        if k.startswith(("base_", "shots")): return "Base + cue"
        if k.startswith("rl_"): return "RL-Zero-Math"
        if k.startswith("sft1"): return "Think-SFT"
        if k.startswith(("theta", "random", "top8", "rand8")): return "Weight edits"
        return "Other RL-Zero checkpoints"
    out = []
    items = load("rln4/t1_t3_items-01/per_problem.json")
    assert [r["problem_index"] for r in items] == idx
    met = load("rln4/t1_t3_items-01/metrics.json")
    out.append(cfg("t3", "base plain, one sample", "Base plain", "", "results/rln4/t1_t3_items-01/per_problem.json [t3]",
                   met["t3"]["right"], [r["t3_right"] for r in items], [r["t3_cap_hit"] for r in items],
                   [r["t3_generated_tokens"] for r in items], [r["t3_extracted_v3"] for r in items]))
    out.append(cfg("t1", "base + cue, one sample, first run", "Base + cue", "", "results/rln4/t1_t3_items-01/per_problem.json [t1]",
                   met["t1"]["right"], [r["t1_right"] for r in items], [r["t1_cap_hit"] for r in items],
                   [r["t1_generated_tokens"] for r in items], [r["t1_extracted_v3"] for r in items]))
    for k, vec in v["arms"].items():
        if any(x is None for x in vec):
            continue  # the three shots arms have 3 problems used as examples
        m = man[k]
        w = when(m["job_id"]) if m["job_id"] else when((ROOT / m["run_folder"] / "run.json").read_text())
        cap = tok = ans = None
        if k in rich:
            right, cap, tok, ans = rich[k]
            assert right == vec, k
        out.append(cfg(k, m["what"], grp(k), w, f"results/axis/math500-01/vectors.json [{k}]", m["right"], vec, cap, tok, ans))
    folder = "thinkvote/math500_sft1_cue_s4-01"
    rs = [r for r in rows(folder + "/rows.jsonl") if r["attempt"] == 0]
    per = load(folder + "/readout.json")["each_sample"]["single_right"]
    for s in range(4):
        right, cap, tok, ans = detail([r for r in rs if r["sample"] == s], idx)
        out.append(cfg(f"think|s{s}", f"Think-SFT + cue, sample {s + 1} of 4", "Think-SFT", when_of(folder),
                       f"results/{folder}/rows.jsonl", per[s], right, cap, tok, ans))
    return {"label": "MATH-500", "title": "MATH-500", "n": 500, "problems": problems, "configs": out, "a": "t3", "b": "t1"}


sets = {"hard328": hard328(), "math500": math500()}
for s in sets.values():
    s["configs"].sort(key=lambda c: c["when"])  # stable: equal times keep the table's order
    assert len({c["k"] for c in s["configs"]}) == len(s["configs"])
    print(s["label"], len(s["configs"]), "configurations,", sum("t" in c for c in s["configs"]), "with tokens and cap hits")
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
(HERE / "data.json").write_text(json.dumps({"commit": commit, "sets": sets}, separators=(",", ":"), ensure_ascii=False))
print("data.json", (HERE / "data.json").stat().st_size, "bytes")
