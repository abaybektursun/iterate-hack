"""r8-m09 prediction 3: among Think-SFT layout rows (finished, v3-wrong, gold-agreeing candidate), the share whose
stored extracted_v3 is blank or markup only. Pooled over 4 hard328 and 4 MATH-500 files."""
import json
import os
import re
import subprocess

from studies.rlneurons.lib import rln4_lib
from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

JOBS = {
    "hard328": ["abaybektursun-1115-000503-1e5f", "abaybektursun-1115-000525-ea4e",
                "abaybektursun-1115-014823-ef56", "abaybektursun-1115-014833-1daa"],
    "math500": ["abaybektursun-1115-000512-ee03", "abaybektursun-1115-014843-85d9",
                "abaybektursun-1115-000607-0e92", "abaybektursun-1115-000621-1d7e"],
}


def fetch(job):
    path = os.path.join("runs", "theory-tests", job, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        subprocess.run(["modal", "volume", "get", "iterate-runs", f"{job}/answers.jsonl", path], check=True)
    return path


def load_first(path):
    out = {}
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("problem_index") not in out:
                out[r.get("problem_index")] = r
    return out


def finished(r):
    return r.get("cap_hit") is not True and r.get("finish_reason") != "length"


def wrong(r):
    return r.get("score_v3") != 1


def last_boxed_content(c):
    i = c.rfind("\\boxed{")
    j = i + len("\\boxed{")
    depth, k = 1, j
    while k < len(c) and depth:
        depth += {"{": 1, "}": -1}.get(c[k], 0)
        k += 1
    return c[j:k - 1] if depth == 0 else c[j:]


def candidate(text):
    text = text or ""
    if "Answer:" in text:
        s = text[text.rfind("Answer:") + len("Answer:"):]
        parts = [p for p in s.split("\n") if p.strip()]
        c = parts[0] if parts else ""
    else:
        parts = [p for p in text.split("\n") if p.strip()]
        c = parts[-1] if parts else ""
    c = c.strip()
    c = c.replace("$", "").replace("*", "")
    if c.startswith("\\[") or c.startswith("\\("):
        c = c[2:]
    if c.endswith("\\]") or c.endswith("\\)"):
        c = c[:-2]
    if c.endswith("."):
        c = c[:-1]
    if "\\boxed{" in c:
        c = last_boxed_content(c)
    return c


def is_blank(ext):
    """Recipe order: whitespace, then the characters $ * : . ,, then the substrings."""
    if ext is None:
        return True
    s = re.sub(r"\s", "", ext)
    for ch in "$*:.,":
        s = s.replace(ch, "")
    for sub in ("\\[", "\\]", "\\(", "\\)", "\\boxed{}", "{}"):
        s = s.replace(sub, "")
    return s == ""


def main():
    entries_main, entries_alt, example = [], [], None
    for name, jobs in JOBS.items():
        try:
            files = [load_first(fetch(j)) for j in jobs]
        except Exception as e:  # noqa: BLE001
            not_computable(f"cannot read a {name} file: {e}")
            return
        pis = set().union(*[set(f) for f in files])
        for pi in sorted(pis, key=lambda x: (x is None, x)):
            em, ea = [], []
            for rows in files:
                r = rows.get(pi)
                if r is None or not finished(r) or not wrong(r):
                    continue
                if "text" not in r or "gold" not in r:
                    not_computable("row lacks text or gold")
                    return
                c = candidate(r["text"])
                if not c:
                    continue
                b = int(is_blank(r.get("extracted_v3")))
                if rln4_lib.agree(c, r["gold"]):
                    em.append(b)
                    if example is None:
                        example = {k: v for k, v in r.items() if k not in ("text", "prompt", "logprobs", "onsets")}
                        example["candidate"] = c
                if rln4_lib.agree(r["gold"], c):
                    ea.append(b)
            if em:
                entries_main.append(tuple(em))
            if ea:
                entries_alt.append(tuple(ea))
    n_layout = sum(len(e) for e in entries_main)
    if n_layout < 10:
        refuted_without_number()
        return

    def stat(sample):
        d = sum(len(e) for e in sample)
        return sum(sum(e) for e in sample) / d

    m = stat(entries_main)
    alt = stat(entries_alt) if entries_alt else None
    report(m, n_layout, bootstrap(stat, entries_main), "bootstrap", refuted_by_met=(m < 0.40),
           alt_measured=alt, example_row=example)


main()
