# r4-m12 prediction 3: exact-string match N(extracted_v3) == N(gold) among
# v3-right answers, RL (86ef) minus base (e72c), on non-integer-gold problems
# that both models got right under v3.
import json
import os
import re
import signal
import subprocess
import sys

import numpy as np

BUCKET = "s3://pg-lineage-769063704696/results/rlneurons/r5/day1_hard328-01"
JOBS = {
    "e72c": "abaybektursun-1114-151534-e72c",
    "86ef": "abaybektursun-1114-151540-86ef",
}
REQ = ["problem_index", "gold", "extracted", "extracted_v3", "score_v3", "cap_hit"]


def emit(obj):
    print(json.dumps(obj))
    sys.exit(0)


def not_computable(reason):
    emit({"measured": None, "refuted_by_met": False, "alt_measured": None,
          "not_computable": reason, "example_row": None})


def load(tag):
    path = os.path.join("runs", "theory-tests", tag, "answers.jsonl")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = subprocess.run(["aws", "s3", "cp", f"{BUCKET}/{JOBS[tag]}/answers.jsonl", path,
                            "--profile", "iterate-ecr"], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            not_computable(f"could not fetch {JOBS[tag]}/answers.jsonl: {r.stderr.strip()[:300]}")
    rows = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                for k in REQ:
                    if k not in row:
                        not_computable(f"field {k} missing in {JOBS[tag]} rows")
                pi = row["problem_index"]
                if pi not in rows:  # one row per problem; keep the first if ever duplicated
                    rows[pi] = row
    except (OSError, ValueError) as e:
        not_computable(f"{path} not readable: {e}")
    return rows


def slim(row):
    out = {}
    for k, v in row.items():
        if isinstance(v, str) and len(v) > 400:
            out[k] = v[:400] + "...[truncated]"
        elif isinstance(v, list) and len(v) > 20:
            out[k] = v[:20] + ["...[truncated]"]
        else:
            out[k] = v
    return out


# ---------------- N(s) ----------------
def _unbox_entire(s):
    """If s is entirely \\boxed{...}, return the inside, else None."""
    if not s.startswith("\\boxed{"):
        return None
    depth = 0
    start = len("\\boxed")
    for i in range(start, len(s)):
        c = s[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:i] if i == len(s) - 1 else None
    return None


REMOVE = ["$", "\\left", "\\right", "\\displaystyle", "\\,", "\\!", "\\;", "^\\circ", "^{\\circ}"]


def N(s, alt=False):
    if s is None:
        return ""
    s = str(s)
    if not alt:
        inner = _unbox_entire(s.strip())
        if inner is not None:
            s = inner
    s = s.replace("$", "")
    s = re.sub(r"\s+", "", s)
    if alt:
        # alternative reading: unwrap \boxed{...} after '$' and whitespace are gone
        inner = _unbox_entire(s)
        if inner is not None:
            s = inner
    for t in REMOVE:
        s = s.replace(t, "")
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    if s.endswith("."):
        s = s[:-1]
    if "=" in s and not any(t in s for t in ("<", ">", "\\le", "\\ge")):
        s = s.split("=")[-1]
    return s


def is_int_gold(gold, alt=False):
    return re.fullmatch(r"-?\d+", N(gold, alt)) is not None


# ---------------- E(a, g) ----------------
class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


signal.signal(signal.SIGALRM, _alarm)


def _num(v):
    c = complex(v)
    if not (np.isfinite(c.real) and np.isfinite(c.imag)):
        return None
    if abs(c.imag) > 1e-12 * max(1.0, abs(c.real)):
        return None
    return c.real


def _close(a, g):
    return abs(a - g) <= 1e-6 * max(1.0, abs(g))


def _E_inner(na, ng):
    from sympy.parsing.latex import parse_latex
    ea = parse_latex(na)
    eg = parse_latex(ng)
    fa = {str(x) for x in ea.free_symbols}
    fg = {str(x) for x in eg.free_symbols}
    if fa != fg:
        return False
    if not fa:
        va = _num(ea.evalf())
        vg = _num(eg.evalf())
        if va is None or vg is None:
            return False
        return _close(va, vg)
    names = sorted(fa)
    syms_a = {str(x): x for x in ea.free_symbols}
    syms_g = {str(x): x for x in eg.free_symbols}
    rng = np.random.default_rng(0)
    pts = rng.uniform(0.5, 2.5, size=(5, len(names)))
    for p in pts:
        va = _num(ea.subs({syms_a[n]: float(p[j]) for j, n in enumerate(names)}).evalf())
        vg = _num(eg.subs({syms_g[n]: float(p[j]) for j, n in enumerate(names)}).evalf())
        if va is None or vg is None or not _close(va, vg):
            return False
    return True


def E(a, g, alt=False):
    if a is None or g is None or str(a) == "" or str(g) == "":
        return False
    na, ng = N(a, alt), N(g, alt)
    if na == "" or ng == "":
        return False
    for t in (",", "\\cup"):
        if t in na or t in ng:
            return False
    signal.setitimer(signal.ITIMER_REAL, 5.0)
    try:
        return bool(_E_inner(na, ng))
    except _Timeout:
        return False
    except Exception:
        return False
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def nonempty(x):
    return x is not None and str(x) != ""


# ---------------- recipe ----------------
def stat(base, rl, alt):
    kept = []
    for pi in sorted(set(base) & set(rl)):  # a problem missing from either file is dropped
        b, r = base[pi], rl[pi]
        if is_int_gold(b["gold"]):  # integer test always with the main N
            continue
        if b["score_v3"] != 1 or r["score_v3"] != 1:
            continue
        kept.append(pi)
    if not kept:
        return None, 0, None

    def ind(row):
        x = row["extracted_v3"]
        if not nonempty(x):
            return 0  # an empty extracted_v3 counts as 0
        if alt:
            # alternative reading: raw exact string match (surrounding whitespace stripped)
            return int(str(x).strip() == str(row["gold"]).strip())
        return int(N(x) == N(row["gold"]))

    mb = sum(ind(base[pi]) for pi in kept) / len(kept)
    mr = sum(ind(rl[pi]) for pi in kept) / len(kept)
    pi0 = kept[0]
    ex = {"problem_index": pi0, "e72c": slim(base[pi0]), "86ef": slim(rl[pi0])}
    return mr - mb, len(kept), ex


def main():
    base = load("e72c")
    rl = load("86ef")
    measured, n, ex = stat(base, rl, alt=False)
    alt, _, _ = stat(base, rl, alt=True)
    if measured is None:
        not_computable("no non-integer-gold problem has score_v3 == 1 in both files")
    print(f"# kept problems {n}", file=sys.stderr)
    emit({"measured": measured, "refuted_by_met": measured < 0.01, "alt_measured": alt,
          "not_computable": None, "example_row": ex})


if __name__ == "__main__":
    main()
