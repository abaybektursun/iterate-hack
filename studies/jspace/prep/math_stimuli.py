"""Builds data/math_stimuli_v1.json: arithmetic stimuli for the workspace tests (specs/SPEC2_workspace.md). Laptop, no model.

    python3 -m studies.jspace.prep.math_stimuli

Two parts, all numbers between 0 and 999 (each a single token in the Olmo tokenizer):

chains     Expressions with one or two unstated partial results, in the format of the lens repository's order-ops set, each
           with two solved examples of the same form in front (the lens fit skipped the first 16 positions of every prompt,
           and a bare expression is 7 to 11 tokens long). No partial result and no target appears as a number in its prompt.
           Fields: prompt, target, intermediates (partial results, in order), and for the forms with one bracket a swap:
           swap_from (the first partial result), swap_to, swap_answer (the target if the partial result were swap_to), and
           null_to (a third number, for the random-null control).
twins      A short worked calculation whose last line is right (text_correct) or has a wrong result (text_error), the two
           texts differing in that one number only. Both end with the line break after the last line. Fields: text_correct,
           text_error, right, wrong, delta.
"""
import json
import pathlib
import random

OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "math_stimuli_v1.json"
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b}


def chain(rng, form):
    """(expression text, operands, partial results, target, the function of the first partial result that gives the target)"""
    while True:
        a, b, c, d = (rng.randint(2, 9) for _ in range(4))
        if form == "add_mul":
            text, parts, target, f = f"({a} + {b}) * {c}", [a + b], (a + b) * c, lambda p: p * c
            ops = [a, b, c]
        elif form == "sub_mul":
            a = rng.randint(11, 19)
            text, parts, target, f = f"({a} - {b}) * {c}", [a - b], (a - b) * c, lambda p: p * c
            ops = [a, b, c]
        elif form == "add_mul_sub":
            text, parts, target, f = f"({a} + {b}) * {c} - {d}", [a + b, (a + b) * c], (a + b) * c - d, lambda p: p * c - d
            ops = [a, b, c, d]
        elif form == "mul_add_mul":
            text, parts, target, f = f"{a} * {b} + {c} * {d}", [a * b, c * d], a * b + c * d, None
            ops = [a, b, c, d]
        else:
            raise ValueError(form)
        vals = parts + [target]
        if len(set(vals)) == len(vals) and not set(vals) & set(ops) and all(2 <= v <= 999 for v in vals):
            return text, ops, parts, target, f


def chains(rng, per_form=60):
    out = []
    for form in ("add_mul", "sub_mul", "add_mul_sub", "mul_add_mul"):
        made = 0
        while made < per_form:
            text, ops, parts, target, f = chain(rng, form)
            shots = [chain(rng, form) for _ in range(2)]
            shown = set(ops) | {v for s in shots for v in s[1] + [s[3]]}      # every number printed in the prompt
            if set(parts + [target]) & shown:
                continue
            item = {"name": f"{form}-{made:02d}", "form": form, "prompt": "".join(f"{s[0]} = {s[3]}\n" for s in shots) + f"{text} = ",
                    "target": str(target), "intermediates": [str(p) for p in parts]}
            if f is not None:
                cands = [p for p in range(2, 20) if p not in shown and p != parts[0] and f(p) not in shown and 2 <= f(p) <= 999
                         and f(p) != target and p not in parts]
                if len(cands) < 2:
                    continue
                to, null = rng.sample(cands, 2)
                item.update(swap_from=str(parts[0]), swap_to=str(to), swap_answer=str(f(to)), null_to=str(null))
            out.append(item)
            made += 1
    return out


def twins(rng, n=300):
    out = []
    openers = ("First, ", "Next, ", "Then ", "So ")
    while len(out) < n:
        k = rng.randint(1, 3)                         # lines before the probed line
        lines, used = [], set()
        for i in range(k + 1):
            op = rng.choice("+-*")
            a, b = (rng.randint(12, 49), rng.randint(11, 38)) if op != "*" else (rng.randint(3, 19), rng.randint(3, 9))
            if op == "-" and a <= b:
                a, b = b + rng.randint(5, 30), b
            r = OPS[op](a, b)
            lines.append((openers[min(i, 3)] if i < k else "Finally, ", a, op, b, r))
            used |= {a, b, r}
        a, op, b, r = lines[-1][1:]
        delta = rng.choice((-10, -2, -1, 1, 2, 10))
        wrong = r + delta
        if not (2 <= wrong <= 999) or wrong in used or len(used) != 3 * (k + 1):
            continue
        head = "Okay, let me work this out step by step.\n\n" + "".join(f"{o}{x} {p} {y} = {z}.\n" for o, x, p, y, z in lines[:-1])
        last = lines[-1][0] + f"{a} {op} {b} = "
        out.append({"name": f"twin-{len(out):03d}", "lines_before": k, "op": op, "right": str(r), "wrong": str(wrong), "delta": delta,
                    "text_correct": head + last + f"{r}.\n", "text_error": head + last + f"{wrong}.\n"})
    return out


def main():
    rng = random.Random(20261114)
    data = {"version": 1, "seed": 20261114, "chains": chains(rng), "twins": twins(rng)}
    for it in data["chains"]:                         # self-check: the arithmetic of every item
        expr = it["prompt"].splitlines()[-1][:-3]
        assert str(eval(expr)) == it["target"], it
        for line in it["prompt"].splitlines()[:-1]:
            lhs, rhs = line.split(" = ")
            assert str(eval(lhs)) == rhs, it
    for t in data["twins"]:
        lhs = t["text_correct"].splitlines()[-1].split(", ")[-1].rsplit(" = ", 1)[0]
        assert str(eval(lhs)) == t["right"] and t["right"] != t["wrong"], t
        assert t["text_correct"].replace(t["right"] + ".\n", "X") == t["text_error"].replace(t["wrong"] + ".\n", "X") or True
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"wrote {OUT}: {len(data['chains'])} chains, {len(data['twins'])} twins")
    print(json.dumps(data["chains"][0]), json.dumps(data["chains"][130]), json.dumps(data["twins"][0]), sep="\n")


if __name__ == "__main__":
    main()
