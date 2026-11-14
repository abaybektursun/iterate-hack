"""cleanneurons Part I item 7: files for the description test and its score (laptop, standard library only).

    python3 -m studies.cleanneurons.analysis.describe_test prep  <describe_neurons output dir> <work dir> [--selected 30] [--reference 15] [--seed 0]
    python3 -m studies.cleanneurons.analysis.describe_test score <work dir> <out json>

prep picks --selected neurons of the selected set and --reference of the reference set (seeded), and for each its stronger pole
(larger p99.9 of |a|). It writes
  describe_input.json   per unit: key, layer, neuron, pole, share of positions beyond the layer p97, promoted and suppressed tokens,
                        and the first10 top contexts (text with the firing token in << >>, activation). The describing reader sees
                        only this file and writes descriptions.json: {key: one sentence}.
  test_items.json       per unit: 20 contexts, the heldout10 top contexts and random10 random positions of the same answers, shuffled,
                        text only. The testing reader sees this file and descriptions.json and writes predictions.json:
                        {key: [ids of the 10 contexts it expects to fire]}.
  test_key.json         per unit: the ids of the heldout10 contexts. Neither reader sees it. The set of each unit is here only, so
                        both readers are blind to selected against reference.
score reads descriptions.json, predictions.json and test_key.json: per unit the share of the 20 contexts classified right
(10 picked of 20, so chance is 50 %), then the mean per set with a 95 % bootstrap interval over units.
"""
import json
import pathlib
import random
import sys


def prep(run, work, n_sel=30, n_ref=15, seed=0):
    run, work = pathlib.Path(run), pathlib.Path(work)
    work.mkdir(parents=True, exist_ok=True)
    neurons = json.load(open(run / "neurons.json"))["neurons"]
    poles = {(p["layer"], p["neuron"], p["pole"]): p for p in json.load(open(run / "contexts.json"))["poles"]}
    rng = random.Random(seed)
    chosen = []
    for name, k in (("selected", n_sel), ("reference", n_ref)):
        pool = sorted((x for x in neurons if x["set"] == name), key=lambda x: (x["layer"], x["neuron"]))
        chosen += [(name, x) for x in rng.sample(pool, k)]
    rng.shuffle(chosen)
    inp, items, key = [], {}, {}
    for i, (name, x) in enumerate(chosen):
        pole = "+" if x["pos"]["p99.9"] >= x["neg"]["p99.9"] else "-"
        p = poles[(x["layer"], x["neuron"], pole)]
        assert len(p["first10"]) == 10 and len(p["heldout10"]) == 10 and len(p["random10"]) == 10, (x["layer"], x["neuron"], pole)
        k = f"u{i:02d}"
        side = "pos" if pole == "+" else "neg"
        inp.append({"key": k, "layer": x["layer"], "neuron": x["neuron"], "pole": pole, "share_of_positions_beyond_layer_p97": x[side]["share_beyond_p97"],
                    "promoted_tokens": [t for t, _ in x["promoted"]], "suppressed_tokens": [t for t, _ in x["suppressed"]],
                    "contexts": [{"text": c["text"], "activation": c["activation"]} for c in p["first10"]]})
        mixed = [(c["text"], True) for c in p["heldout10"]] + [(c["text"], False) for c in p["random10"]]
        rng.shuffle(mixed)
        items[k] = [{"id": j, "text": t} for j, (t, _) in enumerate(mixed)]
        key[k] = {"set": name, "layer": x["layer"], "neuron": x["neuron"], "pole": pole, "fires": [j for j, (_, f) in enumerate(mixed) if f]}
    json.dump({"source": str(run), "seed": seed, "units": inp}, open(work / "describe_input.json", "w"), indent=1)
    json.dump(items, open(work / "test_items.json", "w"), indent=1)
    json.dump(key, open(work / "test_key.json", "w"), indent=1)
    print(len(inp), "units ->", work)


def score(work, out):
    work = pathlib.Path(work)
    desc, pred, key = (json.load(open(work / f)) for f in ("descriptions.json", "predictions.json", "test_key.json"))
    assert set(desc) == set(pred) == set(key), "descriptions, predictions and key name different units"
    units, by = [], {"selected": [], "reference": []}
    for k, v in sorted(key.items()):
        assert len(set(pred[k])) == 10 and all(0 <= j < 20 for j in pred[k]), (k, pred[k])
        hit = len(set(pred[k]) & set(v["fires"]))
        acc = (hit + (10 - (10 - hit))) / 20               # right = picked firing + left-out non-firing = 2 * hit
        units.append({"key": k, **{f: v[f] for f in ("set", "layer", "neuron", "pole")}, "accuracy": acc, "description": desc[k]})
        by[v["set"]].append(acc)
    rng = random.Random(0)

    def ci(xs):
        means = sorted(sum(rng.choices(xs, k=len(xs))) / len(xs) for _ in range(5000))
        return [means[125], means[4874]]
    res = {"chance": 0.5, "sets": {s: {"units": len(xs), "mean_accuracy": sum(xs) / len(xs), "ci95": ci(xs)} for s, xs in by.items()}, "units": units}
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res["sets"], indent=1))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "prep":
        opt = {a[i]: int(a[i + 1]) for i in range(3, len(a), 2)}
        prep(a[1], a[2], opt.get("--selected", 30), opt.get("--reference", 15), opt.get("--seed", 0))
    else:
        score(a[1], a[2])
