"""Steering directions and arm names for specs/SPEC3_steer.md. Torch only; no model is loaded here.

A lens direction of a token family at layer l is the mean of the unit vectors (W_U[t] - mean_vocab W_U) @ J_l over the family's
tokens, scaled to unit length: the direction in the output of block l along which the J-lens readout of these tokens rises
fastest, with the shift common to every token removed. An arm adds alpha * (median norm of the block's output) * direction to
the output of block l at every position.
"""
import re

import torch

FAMILIES = {
    "hold": (" Wait", "Wait", " wait", " Hmm", "Hmm", " hmm"),                 # the hold-on family of SPEC 2 (twins)
    "wrap": ("<|endoftext|>", " Answer", " So", ".The"),                        # the wrap-up family of SPEC 1
    "neutral": (" the", " so", " Therefore", " and", " is", " of"),             # the neutral family of SPEC 2
}
RAND_SEED = 20261115
HOLD_WORDS = re.compile(r"\b(?:[Ww]ait|[Hh]mm+)\b")                             # written hold-on words, counted in the answer text
ARM = re.compile(r"none|steer:(hold|wrap|holdwrap|neutral|rand):L(\d+):([0-9.]+)|bias:(hold|holdwrap):([0-9.]+)")


def family_ids(tok, name):
    ids = []
    for s in FAMILIES[name]:
        e = tok.encode(s, add_special_tokens=False)
        assert len(e) == 1, (s, e)
        ids.append(int(e[0]))
    assert len(set(ids)) == len(ids), (name, ids)
    return ids


def unit(v):
    return v / v.norm()


def lens_direction(W, mean, J, ids):
    """W [vocab, d] and J [d, d] in fp32, mean = W.mean(0). Unit vector [d]."""
    return unit(torch.stack([unit((W[t] - mean) @ J) for t in ids]).mean(0))


def directions(W, J, fam):
    """{name: unit vector [d]} for hold, wrap, neutral, holdwrap (hold minus wrap) and rand (Gaussian, fixed seed)."""
    mean = W.mean(0)
    d = {n: lens_direction(W, mean, J, ids) for n, ids in fam.items()}
    d["holdwrap"] = unit(d["hold"] - d["wrap"])
    d["rand"] = unit(torch.randn(W.shape[1], generator=torch.Generator().manual_seed(RAND_SEED)))
    return d


def gains(W, J, fam, d):
    """Linear change of each family's mean lens logit (relative to the vocabulary mean) per unit step along each direction."""
    mean = W.mean(0)
    rows = {n: (W[ids] - mean).mean(0) @ J for n, ids in fam.items()}
    return {dn: {fn: float(r @ v) for fn, r in rows.items()} for dn, v in d.items()}


def parse_arm(name):
    """'none' | 'steer:<direction>:L<layer>:<alpha>' | 'bias:<hold|holdwrap>:<nats>' -> dict."""
    m = ARM.fullmatch(name)
    assert m, f"arm {name!r} is not none, steer:<hold|wrap|holdwrap|neutral|rand>:L<layer>:<alpha> or bias:<hold|holdwrap>:<nats>"
    if name == "none":
        return {"arm": name, "kind": "none"}
    if m.group(1):
        return {"arm": name, "kind": "steer", "dir": m.group(1), "layer": int(m.group(2)), "alpha": float(m.group(3))}
    return {"arm": name, "kind": "bias", "family": m.group(4), "nats": float(m.group(5))}


def bias_map(arm, fam):
    """vLLM logit_bias for a bias arm: +nats on the hold family, and -nats on the wrap family for 'holdwrap'."""
    b = {t: arm["nats"] for t in fam["hold"]}
    if arm["family"] == "holdwrap":
        b.update({t: -arm["nats"] for t in fam["wrap"]})
    return b


def hold_count(text):
    return len(HOLD_WORDS.findall(text))


def selfcheck():
    g = torch.Generator().manual_seed(0)
    W, J = torch.randn(50, 16, generator=g), torch.randn(16, 16, generator=g)
    fam = {"hold": [1, 2], "wrap": [3], "neutral": [4, 5]}
    d = directions(W, J, fam)
    assert all(abs(float(v.norm()) - 1) < 1e-5 for v in d.values()) and set(d) == {"hold", "wrap", "neutral", "holdwrap", "rand"}
    gn = gains(W, J, fam, d)
    assert gn["hold"]["hold"] > 0 and gn["holdwrap"]["hold"] > 0 > gn["holdwrap"]["wrap"]      # a step along hold raises hold
    assert gn["hold"]["hold"] > abs(gn["rand"]["hold"])
    assert parse_arm("steer:hold:L24:0.25") == {"arm": "steer:hold:L24:0.25", "kind": "steer", "dir": "hold", "layer": 24, "alpha": 0.25}
    assert parse_arm("bias:hold:1.5")["nats"] == 1.5 and parse_arm("none")["kind"] == "none"
    assert bias_map(parse_arm("bias:holdwrap:2"), fam) == {1: 2.0, 2: 2.0, 3: -2.0}
    assert hold_count("Wait, hmm. Hmmm, wait! awaiting waiter") == 4
    return True


if __name__ == "__main__":
    print(selfcheck())
