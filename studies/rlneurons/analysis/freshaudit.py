"""Audit of the 77 PDF-transcribed fresh2026 statements against a blind second transcription (specs/SPEC_freshaudit.md,
idea-60f12e). No model: text diff and stored rows only.

    P="uv run --no-project --with numpy --with math-verify==0.9.0 python -m studies.rlneurons.analysis.freshaudit"
    $P diff    --work runs/freshaudit --out studies/rlneurons/results/fresh/audit-01   # stage 1 + the plants + the stage-2 queue
    $P table   --work runs/freshaudit --out studies/rlneurons/results/fresh/audit-01   # after the third read: audit.md, audit.json
    $P rescore --out studies/rlneurons/results/fresh/audit-01                          # readout.json, readout.md, examples.json

The grader (rln4_lib.grade_v3), the vote, its expectation under a random tie-break and the bootstrap interval are imported
(ordervote, config_table), not copied. Fail loud.
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import random
import re
import unicodedata

STUDY = pathlib.Path(__file__).resolve().parents[1]
V1 = STUDY / "data" / "fresh" / "fresh2026_v1.json"
PDF_SOURCES = ("hmmt_feb2026_guts", "hmmt_nov2026_gen", "hmmt_nov2026_thm", "hmmt_nov2026_team", "hmmt_nov2026_guts")
PLAIN = set(",.;:\"'()-")
WORDS = set("""not no non distinct different same equal positive negative nonnegative nonzero integer integers real rational complex
prime odd even least most exactly minimum maximum minimal maximal smallest largest greatest sum product difference ratio number all
any every each some only ordered unordered and or if than less more greater fewer between inclusive exclusive first last second
third with without replacement uniformly independently random expected probability area perimeter length radius diameter remainder
digits digit""".split())
SUBS = [(r"[“”„]|``|''", '"'), (r"[‘’`]", "'"), (r"[–—−]", "-"), (r"…", "..."), (r"\$|\\\(|\\\)|\\\[|\\\]", " "),
        (r"\\[dt]frac(?![A-Za-z])", r"\\frac"), (r"\\[dt]binom(?![A-Za-z])", r"\\binom"),
        (r"\\(left|right|displaystyle|[Bb]igg?[lrm]?)(?![A-Za-z])", " "), (r"\\le(?![A-Za-z])", r"\\leq"), (r"\\ge(?![A-Za-z])", r"\\geq"),
        (r"\\ne(?![A-Za-z])", r"\\neq"), (r"\\(ldots|dots|cdots)(?![A-Za-z])", "..."), (r"\\colon(?![A-Za-z])", ":"),
        (r"\\[lr]?vert(?![A-Za-z])", "|"), (r"\^\{\\circ\}", r"^\\circ"), (r"\\[,;:! ]|\\q?quad(?![A-Za-z])|~", " ")]
WRAP = re.compile(r"\\(text|textbf|textit|emph|mathrm|operatorname)\{([^{}]*)\}")
TOKEN = re.compile(r"\\[A-Za-z]+|\\.|\d+(?:,\d{3})*(?:\.\d+)?|[A-Za-z]+|\S")


def norm(s: str) -> list:
    """The token list of a statement or an answer after the normalisation of the spec."""
    s = unicodedata.normalize("NFKC", s)
    for a, b in SUBS:
        s = re.sub(a, b, s)
    while WRAP.search(s):
        s = WRAP.sub(r" \2 ", s)
    s = re.sub(r"([\^_])\{([A-Za-z0-9]|\d+)\}", r"\1\2", s)
    toks = [t.replace(",", "") if t[0].isdigit() else t for t in TOKEN.findall(s)]
    return toks[:-1] if toks and toks[-1] == "." else toks


def flagged(tok: str) -> bool:
    return (tok[0].isdigit() or tok[0] == "\\" or (not tok[0].isalpha() and tok not in PLAIN) or (len(tok) == 1 and tok.isalpha())
            or tok.lower() in WORDS)


def spans(a: str, b: str) -> list:
    """Stage 1: the differing spans of two statements after norm, each FLAG or WORDS."""
    x, y = norm(a), norm(b)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes():
        if op != "equal":
            out.append({"a": " ".join(x[i1:i2]), "b": " ".join(y[j1:j2]), "before": " ".join(x[max(0, i1 - 6):i1]), "after": " ".join(x[i2:i2 + 6]),
                        "stage1": "FLAG" if any(flagged(t) for t in x[i1:i2] + y[j1:j2]) else "WORDS"})
    return out


def gold(answer: str) -> str:
    return answer.split(" = ")[0].strip()       # fresh_prep.py: an answer printed as two equal forms a = b has gold a


def same_answer(a: str, b: str) -> bool:
    from studies.rlneurons.prep.fresh_prep import right
    return norm(a) == norm(b) or (right(a, b) and right(b, a))


# ---- the plants (instrument check): one edit on a copy of a v1 statement --------------------------------------------------

def _first(pattern, repl):
    return lambda s: re.sub(pattern, repl, s, count=1) if re.search(pattern, s) else None


MATERIAL_EDITS = [   # (kind, edit): 4 numbers, 3 signs / inequalities / exponents, 3 conditions
    ("number + 1", _first(r"(?<![\d.,^_{])(\d{2,})(?![\d.,])", lambda m: str(int(m.group(1)) + 1))),
    ("number + 1", _first(r"(?<![\d.,^_{])(\d{2,})(?![\d.,])", lambda m: str(int(m.group(1)) + 1))),
    ("last digit of a number changed", _first(r"(?<![\d.,])(\d+)(?![\d.,])", lambda m: m.group(1)[:-1] + str((int(m.group(1)[-1]) + 3) % 10))),
    ("number doubled", _first(r"(?<![\d.,^_{])(\d+)(?![\d.,])", lambda m: str(int(m.group(1)) * 2 + 2))),
    ("+ to -", _first(r" \+ ", " - ")),
    ("inequality reversed", _first(r"\\le(q)?(?![A-Za-z])|\\ge(q)?(?![A-Za-z])|<|>",
                                   lambda m: {"\\le": "\\ge", "\\leq": "\\geq", "\\ge": "\\le", "\\geq": "\\leq", "<": ">", ">": "<"}[m.group(0)])),
    ("exponent 2 to 3", _first(r"\^\{?2\}?(?!\d)", "^3")),
    ("'distinct' dropped", _first(r"\bdistinct ", "")),
    ("'positive' to 'negative'", _first(r"\bpositive\b", "negative")),
    ("'at least' to 'at most', 'smallest' to 'largest', 'minimum' to 'maximum'",
     _first(r"\b(at least|smallest|minimum|at most|largest|maximum)\b",
            lambda m: {"at least": "at most", "smallest": "largest", "minimum": "maximum", "at most": "at least", "largest": "smallest", "maximum": "minimum"}[m.group(1)])),
]
COSMETIC_EDITS = [   # the first eight must be IDENTICAL after norm; the last two must come back COSMETIC from the third read
    ("\\frac to \\dfrac", _first(r"\\frac", r"\\dfrac")),
    ("$..$ to \\(..\\)", lambda s: re.sub(r"(?<!\$)\$([^$]+)\$(?!\$)", r"\\(\1\\)", s) if re.search(r"(?<!\$)\$([^$]+)\$(?!\$)", s) else None),
    ("spaces and \\, added", lambda s: s.replace(", ", ",  ").replace("=", "\\,=\\,") if "=" in s else None),
    ("straight to curly apostrophe (no statement of the 77 has a double quote)", lambda s: s.replace("'", "’") if "'" in s else None),
    ("\\le to \\leq, \\ge to \\geq (or back)", lambda s: (s.replace("\\leq", "\\le ").replace("\\geq", "\\ge ") if re.search(r"\\[lg]eq", s) else
                                                       re.sub(r"\\([lg])e(?![A-Za-z])", r"\\\1eq", s) if re.search(r"\\[lg]e(?![A-Za-z])", s) else None)),
    ("\\left( \\right) added", lambda s: s.replace("(", "\\left(").replace(")", "\\right)") if re.search(r"\$[^$]*\([^$]*\$", s) else None),
    ("\\ldots to \\dots (or back)", lambda s: (s.replace("\\ldots", "\\dots") if "\\ldots" in s else s.replace("\\dots", "\\ldots") if "\\dots" in s else None)),
    ("final period removed", lambda s: s.rstrip()[:-1] if s.rstrip().endswith(".") else None),
    ("'Compute' to 'Find'", _first(r"\bCompute\b", "Find")),
    ("\\cdot to \\times", _first(r"\\cdot(?![A-Za-z])", r"\\times")),
]


def plants(data: list) -> list:
    """20 plants on 20 different statements of the 77: every edit goes to the first statement, in an order shuffled with
    seed 1, that it changes and that no earlier plant used."""
    pool = [x for x in data if x["source"] in PDF_SOURCES]
    random.Random(1).shuffle(pool)
    used, out = set(), []
    for cls, edits in (("material", MATERIAL_EDITS), ("cosmetic", COSMETIC_EDITS)):
        for kind, edit in edits:
            for x in pool:
                new = None if x["unique_id"] in used else edit(x["problem"])
                if new is not None and new != x["problem"]:
                    used.add(x["unique_id"])
                    out.append({"plant": f"{cls}-{len(out) + 1:02d}", "planted_class": cls, "kind": kind, "unique_id": x["unique_id"], "original": x["problem"],
                                "changed": new, "answer": x["answer"]})
                    break
            else:
                raise AssertionError(f"no statement takes the edit {kind}")
    return out


# ---- stage 1 and the stage-2 queue ----------------------------------------------------------------------------------------

def second(work: pathlib.Path) -> dict:
    """{unique_id: second transcription} of the 77 and of the 15 controls, from <work>/second/<batch>.json."""
    want = json.loads((work / "wanted.json").read_text())
    got = {}
    for f in sorted((work / "second").glob("*.json")):
        src = f.stem.rsplit("_", 1)[0]
        for r in json.loads(f.read_text()):
            got[(src, int(r["number"]))] = {**r, "batch": f.stem}
    out = {uid: {**got[(src, n)], "pdf": src} for src, pairs in want.items() for uid, n in pairs}
    assert len(out) == 77 + 15, len(out)
    return out


def cmd_diff(work: pathlib.Path, out: pathlib.Path):
    data = json.loads(V1.read_text())
    by_id = {x["unique_id"]: x for x in data}
    sec = second(work)
    out.mkdir(parents=True, exist_ok=True)
    (out / "second").mkdir(exist_ok=True)
    for f in sorted((work / "second").glob("*.json")):
        (out / "second" / f.name).write_text(f.read_text())
    items = []
    for uid, s in sec.items():
        v1 = by_id[uid]
        sp = spans(v1["problem"], s["problem"])
        ans_same = same_answer(v1["answer"], gold(s["answer"]))
        items.append({"unique_id": uid, "kind": "transcribed" if v1["source"] in PDF_SOURCES else "control", "pdf": s["pdf"], "number": int(s["number"]),
                      "data": v1["problem"], "second": s["problem"], "data_answer": v1["answer"], "second_answer": s["answer"], "spans": sp,
                      "answer_differs": not ans_same, "second_figure": bool(s.get("figure")), "second_note": s.get("note", ""),
                      "stage1": "IDENTICAL" if not sp else "FLAG" if any(x["stage1"] == "FLAG" for x in sp) else "WORDS"})
    pl = plants(data)
    for p in pl:
        sp = spans(p["changed"], p["original"])
        p.update(spans=sp, stage1="IDENTICAL" if not sp else "FLAG" if any(x["stage1"] == "FLAG" for x in sp) else "WORDS")
        items.append({"unique_id": p["unique_id"], "kind": "plant:" + p["plant"], "pdf": by_id[p["unique_id"]]["source"], "number": int(by_id[p["unique_id"]]["source_id"]),
                      "data": p["changed"], "second": p["original"], "data_answer": p["answer"], "second_answer": p["answer"], "spans": sp, "answer_differs": False,
                      "second_figure": False, "second_note": "", "stage1": p["stage1"]})
    mat, cos = [p for p in pl if p["planted_class"] == "material"], [p for p in pl if p["planted_class"] == "cosmetic"]
    check = {"material_plants_FLAG_at_stage1": sum(p["stage1"] == "FLAG" for p in mat), "cosmetic_plants_IDENTICAL_at_stage1": sum(p["stage1"] == "IDENTICAL" for p in cos[:8]),
             "cosmetic_plants_to_stage2": [p["plant"] for p in cos if p["stage1"] != "IDENTICAL"]}
    assert check["material_plants_FLAG_at_stage1"] == 10, ("a material plant was not flagged at stage 1", [(p["kind"], p["stage1"]) for p in mat])
    assert check["cosmetic_plants_IDENTICAL_at_stage1"] == 8, ("a formatting plant survives norm", [(p["kind"], p["stage1"], p["spans"]) for p in cos[:8]])
    (out / "planted.json").write_text(json.dumps({"stage1_check": check, "plants": pl}, indent=1, ensure_ascii=False) + "\n")
    # the queue of the third read: every item with a span, a differing answer or a figure mark; ids and A/B order drawn with seed 0
    rng = random.Random(0)
    queue = [it for it in items if it["spans"] or it["answer_differs"] or it["second_figure"]]
    rng.shuffle(queue)
    wanted = json.loads((work / "wanted.json").read_text())
    pdf_of = {uid: (src, n) for src, pairs in wanted.items() for uid, n in pairs}
    (work / "queue").mkdir(exist_ok=True)
    key = {}
    for k, it in enumerate(queue):
        qid, data_is = f"q{k + 1:03d}", rng.choice("AB")
        it["qid"], it["data_is"] = qid, data_is
        src, n = pdf_of[it["unique_id"]]
        a, b = ("data", "second") if data_is == "A" else ("second", "data")
        flip = lambda sp: sp if data_is == "A" else {**sp, "a": sp["b"], "b": sp["a"]}
        (work / "queue" / f"{qid}.json").write_text(json.dumps(
            {"qid": qid, "pages_dir": str((work / "pages" / src).resolve()), "problem_number": n, "A": it[a], "B": it[b], "A_answer": it[a + "_answer"],
             "B_answer": it[b + "_answer"], "answers_differ_in_value": it["answer_differs"], "one_version_marks_a_figure": it["second_figure"],
             "spans": [{k2: v for k2, v in flip(sp).items() if k2 != "stage1"} for sp in it["spans"]]}, indent=1, ensure_ascii=False) + "\n")
        key[qid] = {"unique_id": it["unique_id"], "kind": it["kind"], "data_is": data_is, "pdf": src}
    (out / "diff.json").write_text(json.dumps({"items": items, "queue_key": key}, indent=1, ensure_ascii=False) + "\n")
    real = [it for it in items if it["kind"] == "transcribed"]
    ctrl = [it for it in items if it["kind"] == "control"]
    count = lambda xs: {c: sum(it["stage1"] == c for it in xs) for c in ("IDENTICAL", "WORDS", "FLAG")}
    print(json.dumps({"planted": check, "transcribed": count(real), "control": count(ctrl), "answers_differ": [it["unique_id"] for it in items if it["answer_differs"]],
                      "figure_marks": [it["unique_id"] for it in items if it["second_figure"]], "queue": len(queue)}, indent=1))


# ---- the audit table, after the third read --------------------------------------------------------------------------------

def cmd_table(work: pathlib.Path, out: pathlib.Path):
    d = json.loads((out / "diff.json").read_text())
    third = {r["qid"]: r for f in sorted((work / "third").glob("*.json")) for r in json.loads(f.read_text())}
    (out / "third_read.json").write_text(json.dumps(list(third.values()), indent=1, ensure_ascii=False) + "\n")
    (out / "sources.json").write_text((work / "sources.json").read_text())
    review = json.loads((out / "main_session_review.json").read_text()) if (out / "main_session_review.json").exists() else {}
    rows = []
    for it in d["items"]:
        row = {k: it[k] for k in ("unique_id", "kind", "stage1", "answer_differs", "second_figure")}
        row.update(cls="IDENTICAL", verdict="", spans=[], qid=it.get("qid"))
        if it.get("qid"):
            t = third[it["qid"]]
            assert len(t["spans"]) == len(it["spans"]), (it["qid"], "the reader did not return one verdict per span")
            side = lambda m: {"A": "data" if it["data_is"] == "A" else "second", "B": "data" if it["data_is"] == "B" else "second"}.get(m, m)
            for sp, ts in zip(it["spans"], t["spans"]):
                assert ts["class"] in ("COSMETIC", "MATERIAL"), ts
                row["spans"].append({"data": sp["a"], "second": sp["b"], "before": sp["before"], "stage1": sp["stage1"], "class": ts["class"],
                                     "pdf_matches": side(ts.get("pdf_matches", "")), "pdf_quote": ts.get("pdf_quote", ""), "reason": ts.get("reason", "")})
            ans = t.get("answer") or {}
            row["answer"] = {"data": it["data_answer"], "second": it["second_answer"], "class": ans.get("class", ""), "pdf_matches": side(ans.get("pdf_matches", "")),
                             "pdf_quote": ans.get("pdf_quote", "")} if it["answer_differs"] else None
            row["figure_needed"] = bool(t.get("figure_needed"))
            material = [s for s in row["spans"] if s["class"] == "MATERIAL"]
            row["cls"] = ("MATERIAL" if material or row["figure_needed"] else "ANSWER" if it["answer_differs"] and row["answer"]["class"] == "ANSWER"
                          else "COSMETIC" if row["spans"] or it["answer_differs"] else "IDENTICAL")
            if row["cls"] in ("MATERIAL", "ANSWER"):
                bad = [s["pdf_matches"] for s in material] + ([row["answer"]["pdf_matches"]] if row["cls"] == "ANSWER" or (row["answer"] or {}).get("class") == "ANSWER" else [])
                row["verdict"] = "v1 wrong" if row["figure_needed"] or any(m != "data" for m in bad) else "v1 right"
        if it["unique_id"] + "|" + it["kind"] in review:      # the main session's own read of the page replaces the reader's class, with its reason
            row.update(review[it["unique_id"] + "|" + it["kind"]])
        rows.append(row)
    # a route without a model: every number of two or more digits in a v1 statement must be in the text layer of its pages
    start = {(b["source"], int(n)): p for f in (work / "batches").glob("*.json") for b in [json.loads(f.read_text())] for n, p in b["start_page"].items()}
    missing = []
    for it in d["items"]:
        if it["kind"] == "transcribed":
            pages = [work / "pages" / it["pdf"] / f"t{start[(it['pdf'], it['number'])] + k:02d}.txt" for k in (0, 1)]
            text = re.sub(r"[,\s]", "", "".join(f.read_text() for f in pages if f.exists()))
            missing += [(it["unique_id"], t) for t in norm(it["data"]) if t[0].isdigit() and len(t) >= 2 and t.replace(".", "") not in text.replace(".", "")]
    pl = json.loads((out / "planted.json").read_text())
    by_kind = {r["kind"]: r for r in rows}
    for p in pl["plants"]:
        r = by_kind["plant:" + p["plant"]]
        p["final_class"], p["verdict"] = r["cls"], r["verdict"]          # for a plant, "data" is the changed copy
    mat, cos = [p for p in pl["plants"] if p["planted_class"] == "material"], [p for p in pl["plants"] if p["planted_class"] == "cosmetic"]
    pl["final_check"] = {"material_plants_MATERIAL_and_changed_side_named_wrong": sum(p["final_class"] == "MATERIAL" and p["verdict"] == "v1 wrong" for p in mat),
                         "cosmetic_plants_MATERIAL": sum(p["final_class"] == "MATERIAL" for p in cos)}
    (out / "planted.json").write_text(json.dumps(pl, indent=1, ensure_ascii=False) + "\n")
    real, ctrl = [r for r in rows if r["kind"] == "transcribed"], [r for r in rows if r["kind"] == "control"]
    count = lambda xs: {c: sum(r["cls"] == c for r in xs) for c in ("IDENTICAL", "COSMETIC", "MATERIAL", "ANSWER")}
    summary = {"transcribed": {"n": len(real), **count(real), "v1_wrong": sorted(r["unique_id"] for r in real if r["verdict"] == "v1 wrong"),
                               "v1_right_second_transcription_erred": sorted(r["unique_id"] for r in real if r["verdict"] == "v1 right"),
                               "identical_statement_and_answer": sorted(r["unique_id"] for r in real if r["cls"] == "IDENTICAL")},
               "control": {"n": len(ctrl), **count(ctrl), "data_departs_from_pdf": sorted(r["unique_id"] for r in ctrl if r["verdict"] == "v1 wrong"),
                           "second_transcription_erred": sorted(r["unique_id"] for r in ctrl if r["verdict"] == "v1 right")},
               "planted": pl["final_check"], "v1_numbers_of_2_or_more_digits_not_in_the_pdf_text_layer": missing,
               "flag_spans_called_cosmetic": sum(s["stage1"] == "FLAG" and s["class"] == "COSMETIC" for r in real + ctrl for s in r["spans"])}
    (out / "audit.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, ensure_ascii=False) + "\n")
    cell = lambda s: s.replace("|", "\\|").replace("\n", " ")
    md = ["# Audit of the transcribed fresh2026 statements: data file (v1) against a blind second transcription", "",
          f"Transcribed, n = {len(real)}: " + ", ".join(f"{c} {n}" for c, n in count(real).items()) + f"; v1 wrong: {len(summary['transcribed']['v1_wrong'])}.",
          f"Control (MathArena text against the official round PDFs), n = {len(ctrl)}: " + ", ".join(f"{c} {n}" for c, n in count(ctrl).items()) + ".",
          f"Planted: {pl['final_check']['material_plants_MATERIAL_and_changed_side_named_wrong']} of 10 material plants MATERIAL with the changed side named; "
          f"{pl['final_check']['cosmetic_plants_MATERIAL']} of 10 cosmetic plants MATERIAL.", "",
          "Every problem that is not IDENTICAL, one line per differing span. `data` = `fresh2026_v1.json`; for a plant, the changed copy.", "",
          "| problem | kind | class | verdict | data | second transcription | span class | PDF matches | PDF quote | reason |", "|---|---|---|---|---|---|---|---|---|---|"]
    order = {"MATERIAL": 0, "ANSWER": 1, "COSMETIC": 2}
    for r in sorted((r for r in rows if r["cls"] != "IDENTICAL"), key=lambda r: (r["kind"].startswith("plant"), r["kind"] == "control", order[r["cls"]], r["unique_id"])):
        lines = [(s["data"] or "(nothing)", s["second"] or "(nothing)", s["class"], s["pdf_matches"], s["pdf_quote"], s["reason"]) for s in r["spans"]]
        if r.get("answer"):
            a = r["answer"]
            lines.append(("answer: " + a["data"], "answer: " + a["second"], a["class"], a["pdf_matches"], a["pdf_quote"], ""))
        if r.get("figure_needed") or (r["second_figure"] and not lines):
            lines.append(("(figure mark)", "(figure mark)", "MATERIAL" if r.get("figure_needed") else "COSMETIC", "", "", r.get("figure_reason", "")))
        for x in lines:
            md.append(f"| `{r['unique_id']}` | {r['kind']} | {r['cls']} | {r['verdict']} | " + " | ".join(cell(str(v)) for v in x) + " |")
    (out / "audit.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=1))


# ---- the rescore ------------------------------------------------------------------------------------------------------------

def cmd_rescore(out: pathlib.Path):
    import numpy as np
    from studies.rlneurons.analysis import ordervote as O
    data = json.loads(V1.read_text())
    audit = json.loads((out / "audit.json").read_text())["summary"]["transcribed"]
    ch, cells = O.cells("fresh2026")
    idxs = cells["rl"]["idx"]
    assert idxs == list(range(len(data))) == [x["index"] for x in data]
    single = {m: np.array([np.mean([c[0]["score_v3"] for c in ch[m][i]]) for i in idxs]) for m in ("think", "rl", "base")}
    for v, rows in O.cap_views("fresh2026").items():
        single[v] = np.array([np.mean([r["score_v3"] for r in rows[i]]) for i in idxs])
    wrong, same = set(audit["v1_wrong"]), set(audit["identical_statement_and_answer"])
    pdf = [x["source"] in PDF_SOURCES for x in data]
    sets = {"a: all 136": [True] * len(data),
            "b: without the problems whose v1 statement or answer is wrong": [x["unique_id"] not in wrong for x in data],
            "c: the 59 from Hugging Face + the transcribed problems identical after normalisation": [not p or x["unique_id"] in same for x, p in zip(data, pdf)],
            "the 77 transcribed": pdf,
            "the 77 transcribed without the v1-wrong problems": [p and x["unique_id"] not in wrong for x, p in zip(data, pdf)],
            "the transcribed problems identical after normalisation": [p and x["unique_id"] in same for x, p in zip(data, pdf)]}
    pairs = (("think", "rl"), ("think", "base"), ("rl", "base"), ("cap32", "rl"), ("cap16", "rl"))
    res = {}
    for name, mask in sets.items():
        keep = np.flatnonzero(mask)
        rng = np.random.default_rng(0)
        models = {m: {"one_sample_mean_of_4": float(single[m][keep].sum()), "vote_stored_order": float(cells[m]["stored"][keep].sum()),
                      "vote_expected_random_tie": float(cells[m]["s"][keep].sum())} for m in single}
        contrasts = {}
        for x, y in pairs:
            idx = keep[rng.integers(0, len(keep), (O.BOOT, len(keep)))]
            contrasts[f"{x} - {y}"] = {view: O.diff(a[x], a[y], idx) | {"points": float(100 * (a[x][keep] - a[y][keep]).mean()), "problems": float((a[x][keep] - a[y][keep]).sum())}
                                       for view, a in (("one_sample", single), ("vote_stored_order", {m: cells[m]["stored"] for m in single}),
                                                       ("vote_expected_random_tie", {m: cells[m]["s"] for m in single}))}
        res[name] = {"n": int(len(keep)), "models": models, "contrasts": contrasts}
    a = res["a: all 136"]
    assert [a["models"][m]["vote_stored_order"] for m in ("think", "rl", "base")] == [75, 57, 38], a["models"]
    assert [round(a["models"][m]["vote_expected_random_tie"], 1) for m in ("think", "rl", "base")] == [75.5, 55.8, 38.8], a["models"]
    k = a["contrasts"]["think - rl"]
    assert np.allclose([k["vote_stored_order"]["points"], *k["vote_stored_order"]["interval95"]], [13.2, 7.4, 19.1], atol=0.056), k
    assert np.allclose([k["vote_expected_random_tie"]["points"], *k["vote_expected_random_tie"]["interval95"]], [14.5, 8.5, 20.6], atol=0.056), k
    b = res["b: without the problems whose v1 statement or answer is wrong"]["contrasts"]["think - rl"]
    by_id = {x["unique_id"]: x["index"] for x in data}
    lead = [(u, int(cells["think"]["stored"][by_id[u]]), int(cells["rl"]["stored"][by_id[u]]), int(cells["base"]["stored"][by_id[u]])) for u in sorted(wrong)]
    net = sum(t - r for _, t, r, _ in lead)
    hyp = {"H1": {"v1_wrong_of_77": len(wrong), "held": len(wrong) < 5},
           "H2": {view: {"a": k[view]["points"], "b": b[view]["points"], "change": b[view]["points"] - k[view]["points"], "b_interval95": b[view]["interval95"]}
                  for view in ("vote_stored_order", "vote_expected_random_tie")},
           "H3": {"v1_wrong_problems: vote right (think, rl, base), stored order": lead, "think_only_minus_rl_only": net, "held": abs(net) <= 2}}
    hyp["H2"]["held"] = all(abs(v["change"]) < 1.5 and v["b_interval95"][0] > 0 for v in hyp["H2"].values())
    (out / "readout.json").write_text(json.dumps({"bootstrap": "paired over problems, 5,000 resamples, numpy default_rng(0) per set, the contrasts drawn in the listed order",
                                                  "models": {"think": "Think-SFT + cue, cap 16,384", "rl": "RL plain, cap 16,384", "base": "base + cue, cap 16,384",
                                                             "cap32": "Think-SFT + cue, cap 32,768", "cap16": "the cap-32,768 answers cut at 16,384"},
                                                  "sets": res, "hypotheses": hyp}, indent=1) + "\n")
    f = lambda d: f"{d['points']:+.1f} [{d['interval95'][0]:+.1f}, {d['interval95'][1]:+.1f}]"
    md = ["# fresh2026 rescored on the audited sets (stored rows, no model run; T 1.0 / top-p 1.0, grader v3, 4 samples)", "",
          "Right answers of n. Vote over 4: in the stored sample order (as posted) and as the expectation under a random tie-break.", "",
          "| set | n | model | one sample (mean of 4) | vote, stored order | vote, expected |", "|---|---|---|---|---|---|"]
    name = {"think": "Think-SFT + cue", "rl": "RL plain", "base": "base + cue", "cap32": "Think-SFT + cue, cap 32,768", "cap16": "the same answers cut at 16,384"}
    for s, r in res.items():
        md += [f"| {s} | {r['n']} | {name[m]} | {v['one_sample_mean_of_4']:.1f} | {v['vote_stored_order']:.0f} | {v['vote_expected_random_tie']:.1f} |" for m, v in r["models"].items()]
    md += ["", "Differences in points [95 %], paired bootstrap over problems, 5,000 resamples.", "",
           "| set | n | difference | one sample | vote, stored order | vote, expected |", "|---|---|---|---|---|---|"]
    for s, r in res.items():
        md += [f"| {s} | {r['n']} | {name[c.split(' - ')[0]]} minus {name[c.split(' - ')[1]]} | {f(v['one_sample'])} | {f(v['vote_stored_order'])} | {f(v['vote_expected_random_tie'])} |"
               for c, v in r["contrasts"].items()]
    (out / "readout.md").write_text("\n".join(md) + "\n")
    rows = lambda m, i: [{k2: c[0].get(k2) for k2 in ("sample", "n_new", "cap_hit", "extracted_v3", "score_v3")} for c in ch[m][i]]
    pick = lambda want: next(i for i in idxs if pdf[i] and cells["think"]["stored"][i] == want and cells["rl"]["stored"][i] == 1 - want)
    (out / "examples.json").write_text(json.dumps([{"what": w, "unique_id": data[i]["unique_id"], "problem": data[i]["problem"], "gold": data[i]["answer"],
                                                    "think_sft_rows": rows("think", i), "rl_rows": rows("rl", i), "vote_think_sft": int(cells["think"]["stored"][i]),
                                                    "vote_rl": int(cells["rl"]["stored"][i])}
                                                   for w, i in (("transcribed problem, Think-SFT's vote right and RL's wrong", pick(1)),
                                                                ("transcribed problem, Think-SFT's vote wrong and RL's right", pick(0)))], indent=1, ensure_ascii=False) + "\n")
    print("\n".join(md), "\n", json.dumps(hyp, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("diff", "table", "rescore"))
    ap.add_argument("--work")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    if a.cmd == "diff":
        cmd_diff(pathlib.Path(a.work), out)
    elif a.cmd == "table":
        cmd_table(pathlib.Path(a.work), out)
    else:
        cmd_rescore(out)


if __name__ == "__main__":
    main()
