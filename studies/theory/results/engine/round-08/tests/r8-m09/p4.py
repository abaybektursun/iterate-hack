"""r8-m09 prediction 4: blank-v3 share of finished answers, hybrid sft1_rl20 minus think, hard328 transplant rows."""
import json
import re

from studies.theory.lib.noise import bootstrap, report, not_computable

PATH = "studies/rlneurons/results/transplant/hard328-01/rows.jsonl"


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


def is_blank_alt(ext):
    """Other order: substrings first, then whitespace and characters, then substrings again."""
    if ext is None:
        return True
    s = ext
    for sub in ("\\[", "\\]", "\\(", "\\)", "\\boxed{}", "{}"):
        s = s.replace(sub, "")
    s = re.sub(r"\s", "", s)
    for ch in "$*:.,":
        s = s.replace(ch, "")
    for sub in ("\\[", "\\]", "\\(", "\\)", "\\boxed{}", "{}"):
        s = s.replace(sub, "")
    return s == ""


def main():
    try:
        with open(PATH) as f:
            rows = [json.loads(line) for line in f if line.strip()]
    except Exception as e:  # noqa: BLE001
        not_computable(f"cannot read {PATH}: {e}")
        return
    per = {}
    example = None
    for r in rows:
        arm = r.get("arm")
        if arm not in ("sft1_rl20", "think"):
            continue
        if r.get("cap_hit") is True:
            continue
        g = "H" if arm == "sft1_rl20" else "T"
        d = per.setdefault(r.get("problem_index"), {"H": [], "T": []})
        b, ba = int(is_blank(r.get("extracted_v3"))), int(is_blank_alt(r.get("extracted_v3")))
        d[g].append((b, ba))
        if example is None and g == "H" and b:
            example = r
    entries = [(tuple(d["H"]), tuple(d["T"])) for _, d in sorted(per.items(), key=lambda x: (x[0] is None, x[0]))]
    nH = sum(len(e[0]) for e in entries)
    nT = sum(len(e[1]) for e in entries)
    print(json.dumps({"groups": {"H_sft1_rl20_finished": nH, "T_think_finished": nT}}))
    if nH == 0 or nT == 0:
        not_computable("an arm has no finished rows")
        return

    def stat_idx(sample, idx):
        h = [x[idx] for e in sample for x in e[0]]
        t = [x[idx] for e in sample for x in e[1]]
        return (sum(h) / len(h) if h else 0.0) - (sum(t) / len(t) if t else 0.0)

    def stat(sample):
        return stat_idx(sample, 0)

    m = stat(entries)
    if example is None:
        example = next(r for r in rows if r.get("arm") == "sft1_rl20" and r.get("cap_hit") is not True)
    report(m, min(nH, nT), bootstrap(stat, entries), "bootstrap", refuted_by_met=(m > 0.002),
           alt_measured=stat_idx(entries, 1), example_row=example)


main()
