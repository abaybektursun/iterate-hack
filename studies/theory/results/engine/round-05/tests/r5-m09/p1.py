"""r5-m09 prediction 1: share of base finished-wrong judged items flagged answer_from_problem (anatomy judge-01)."""
import json
import os

MODEL = "base"
PATH = "studies/rlneurons/results/anatomy/judge-01/labels.json"
CONTROL_KINDS = {"planted", "shuffled"}  # the two control kinds anatomy_judge.py builds


def out(measured, refuted, alt, nc, ex):
    print(json.dumps({"measured": measured, "refuted_by_met": refuted, "alt_measured": alt,
                      "not_computable": nc, "example_row": ex}))


def positive(v):
    """Literal: boolean true, or the string 'yes'/'true' (case-insensitive). Everything else negative."""
    if v is True:
        return True
    if isinstance(v, str) and v.strip().lower() in ("yes", "true"):
        return True
    return False


def positive_alt(v):
    """Other reading: any non-null, non-false value set in the field counts as a flag."""
    if positive(v):
        return True
    if v is None or v is False:
        return False
    if isinstance(v, str):
        return v.strip().lower() not in ("", "no", "false", "null", "none")
    return True


def main():
    if not os.path.exists(PATH):
        return out(None, False, None, f"{PATH} not found", None)
    items = json.load(open(PATH))
    if not all("model" in it for it in items):
        return out(None, False, None, "labels.json items lack the field 'model'", None)

    # main reading: model == MODEL, planted_at null/absent, kind not planted or another control kind
    kept = [it for it in items if it.get("model") == MODEL and it.get("planted_at") is None
            and str(it.get("kind")).lower() not in CONTROL_KINDS]
    # other reading: only 'planted' excluded as a kind (shuffled kept), any set value of the field counts as positive
    kept_alt = [it for it in items if it.get("model") == MODEL and it.get("planted_at") is None
                and str(it.get("kind")).lower() != "planted"]
    if not kept:
        return out(None, False, None, f"no items with model == {MODEL} outside controls", None)
    pos = sum(positive(it.get("answer_from_problem")) for it in kept)
    measured = pos / len(kept)
    alt = (sum(positive_alt(it.get("answer_from_problem")) for it in kept_alt) / len(kept_alt)) if kept_alt else None
    refuted = measured < 0.15
    ex = {k: v for k, v in kept[0].items() if k not in ("passA", "passB")}
    out(measured, refuted, alt, None, ex)


main()
