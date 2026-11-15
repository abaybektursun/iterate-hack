"""r7-m05 prediction 3: share of wrong-plan wrongstep items with g > 0 (noprob minus base, each lp_span - lp_control)."""
import json
import pathlib
import subprocess

from studies.theory.lib.noise import bootstrap, report, not_computable, refuted_without_number

REL = "studies/rlneurons/results/wrongstep/rules-01/items.json"
CACHE = pathlib.Path("runs/theory-tests/wrongstep/rules-01/items.json")


def load():
    p = pathlib.Path(REL)
    if p.exists():
        return json.loads(p.read_text())
    if not CACHE.exists():
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        out = subprocess.run(["git", "show", f"HEAD:{REL}"], capture_output=True, check=True).stdout
        CACHE.write_bytes(out)
    return json.loads(CACHE.read_text())


def get(row, m, keys):
    models = row.get("models")
    if not isinstance(models, dict):
        return None
    e = models.get(m)
    if not isinstance(e, dict):
        return None
    if any(e.get(k) is None for k in keys):
        return None
    return e


def kept_rows(rows, ks, kc):
    out = []
    for r in rows:
        lab = str(r.get("label") or "").lower()
        if not ("plan" in lab and "misread" not in lab and "slip" not in lab):
            continue
        if get(r, "base", (ks, kc)) is None or get(r, "noprob", (ks, kc)) is None:
            continue
        out.append(r)
    return out


def g(r, ks, kc):
    a, b = r["models"]["noprob"], r["models"]["base"]
    return (a[ks] - a[kc]) - (b[ks] - b[kc])


def make_stat(ks, kc):
    def stat(sample):
        return sum(1 for r in sample if g(r, ks, kc) > 0) / len(sample)
    return stat


def main():
    try:
        rows = load()
    except Exception as e:  # noqa: BLE001
        not_computable(f"cannot read {REL}: {e}")
        return
    if not isinstance(rows, list):
        not_computable(f"{REL} is not a list of rows")
        return
    kept = kept_rows(rows, "lp_span", "lp_control")
    if len(kept) < 6:
        refuted_without_number()
        return
    stat = make_stat("lp_span", "lp_control")
    measured = stat(kept)
    # Other reading: the first-5-token head of the span against head-length control text (lp_head, lp_head_control).
    kept_h = kept_rows(rows, "lp_head", "lp_head_control")
    alt = make_stat("lp_head", "lp_head_control")(kept_h) if kept_h else None
    report(measured, len(kept), bootstrap(stat, kept), "bootstrap",
           refuted_by_met=(measured > 0.68 or measured < 0.15), alt_measured=alt, example_row=kept[0])


main()
