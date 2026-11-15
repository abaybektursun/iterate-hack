"""The change of this review, measured and not kept (it is not in tools/): print every number of a draft that the facts file does not hold.

    python3 meta/reviews/abaybektursun/20261115-1655-paper2/paper_check.py <draft 1 as text> studies/theory/paper/facts.json > after.txt
    (draft 1 is not in git: it was the session's scratchpad file paper_d1.txt, pdftotext of the first build)

A number is held when a number of the facts file (a value, or a number inside a string), or 100 times it, rounds to it
at the draft's own number of decimals. Signs are ignored.
"""
import json
import re
import sys

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers(text):
    for m in NUM.finditer(text):
        s = m.group().rstrip(",").replace(",", "")
        yield float(s), len(s.partition(".")[2]), m.start()


def held(node, out):
    if isinstance(node, dict):
        node = list(node.values())
    if isinstance(node, list):
        for v in node:
            held(v, out)
    elif isinstance(node, str):
        out.update(v for v, _, _ in numbers(node))
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        out.add(abs(float(node)))


facts = set()
held(json.load(open(sys.argv[2])), facts)
missing = 0
for n, line in enumerate(open(sys.argv[1]).read().splitlines(), 1):
    for value, dec, start in numbers(line):
        if not any(abs(f * k - value) <= 0.5 * 10 ** -dec + 1e-9 for f in facts for k in (1, 100)):
            missing += 1
            print(f"{n}: {value:.{dec}f} | {line[max(0, start - 45):start + 30].strip()}")
print(f"{missing} numbers of the draft are not in the facts file")
