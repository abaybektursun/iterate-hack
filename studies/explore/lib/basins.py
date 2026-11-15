"""Online basin labels: an LLM judge assigns each submission to an approach basin, keeping one growing codebook.

A basin is the method of a program (e.g. "hand-placed hexagonal rows", "SLSQP on centers and radii"), not its
parameters. The judge sees, per submission, the IDEA line plus the program's imports and function names, and the
current codebook; it puts each new submission into an existing basin or names a new one. Used online by the
basin and randflush strategies (lib/strategies.py) and post hoc for every arm (analysis/label_basins.py).
"""
import json
import re

from studies.explore.lib.loop import chat, cost

JUDGE = "gpt-6.1-sol"

PROMPT = """You group versions of a program by METHOD: the algorithmic approach (how the solution is constructed or
searched), not its parameter values or small tweaks. Two versions that both hand-place circles in rows are the same
basin even with different radii; a version that runs a numerical optimizer is a different basin from one that does
not; a random search, a greedy constructor, a lattice template, a simulated annealing, a beam search are different.

TASK (one line): {task}

EXISTING BASINS (name: description):
{codebook}

NEW VERSIONS (id | idea | imports and functions):
{items}

Put every new version into an existing basin, or into a new basin when no existing one has the same method. Keep
basin names short (2-6 words). Reply with JSON only:
{{"assign": {{"<id>": "<basin name>", ...}}, "new": {{"<new basin name>": "<one-line description>", ...}}}}"""


def signature(code):
    if not code:
        return "(no program)"
    imports = sorted(set(re.findall(r"^\s*(?:from\s+(\S+)\s+import|import\s+(\S+))", code, re.M)))
    names = re.findall(r"^\s*def\s+(\w+)", code, re.M)
    return "imports " + ",".join(a or b for a, b in imports) + "; defs " + ",".join(names[:12])


class Labeler:
    def __init__(self, task_line, model=JUDGE):
        self.task_line, self.model = task_line, model
        self.codebook, self.label, self.usd = {}, {}, 0.0

    def add(self, rows):
        """Label rows (dicts with id, idea, code) not labeled yet. Fails loudly if the judge drops an id twice."""
        todo = [r for r in rows if r["id"] not in self.label]
        if not todo:
            return
        items = "\n".join(f"{r['id']} | {r['idea'][:240]} | {signature(r.get('code'))}" for r in todo)
        cb = "\n".join(f"{k}: {v}" for k, v in self.codebook.items()) or "(none yet)"
        msg = PROMPT.format(task=self.task_line, codebook=cb, items=items)
        for attempt in range(2):
            text, usage = chat([{"role": "user", "content": msg}], self.model)
            self.usd += cost(usage, self.model)
            m = re.search(r"\{.*\}", text, re.S)
            out = json.loads(m.group(0)) if m else {}
            assign, new = out.get("assign", {}), out.get("new", {})
            if all(r["id"] in assign for r in todo):
                break
        else:
            raise RuntimeError(f"judge left ids unlabeled: {[r['id'] for r in todo if r['id'] not in assign]}")
        for k, v in new.items():
            self.codebook.setdefault(k, v)
        for r in todo:
            b = assign[r["id"]]
            self.codebook.setdefault(b, "(named without description)")
            self.label[r["id"]] = b
