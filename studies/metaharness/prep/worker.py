"""The scripted worker of the planted-waste test: runs one batch of the gapmap study inside an arena, the way the
arena's own files say to run it, and records the window.

  MH_HOME=<dir> python3 -m studies.metaharness.prep.worker <arena id> <window 0..3>

The worker is a fixed program. It does what the repository tells an agent to do, so a change a review makes to the
repository changes what the worker does:
  - the cells of the batch come from `queue.json` through `prep/make_cells.py`;
  - every launch uses the command lines of the code block under "## How to run" in the study's README that hold
    `<cell>`, in their order; a line that exits non-zero is a failed launch;
  - the launcher and the job are whatever `jobs/submit.sh` and `jobs/run_cell.sh` are at that commit.
What the worker brings itself (the same in every arena of a variant, SPEC2 "Plants"):
  - it gives the `subject` cell its own settings by hand; in a planted arena it types two of them wrongly, and after
    each failed launch it corrects the one the error names and launches again;
  - after a launch that fails on the data path, it drops `--data` for the rest of the window.
"""
import json
import re
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from studies.metaharness.lib import arena as A

BATCHES = ["accuracy", "cap_hit", "tokens", "tokens_both_right"]
REQUIRED = ["subject", "level5", "t2_length_quartile", "t1_length_quartile"]
DEFAULT_LAUNCH = ["bash studies/gapmap/jobs/submit.sh <batch> <cell>"]
# The subject cell's own settings per window: what the agent means (final) and what it types first (typed).
CUSTOM = [
    {"note": "90% interval, csv table", "final": {"ci": 0.9, "fmt": "csv"}, "typed": {"ci": 90, "fmt": "cvs"}},
    {"note": "99% interval, 3 digits", "final": {"ci": 0.99, "digits": 3}, "typed": {"ci": 99, "digits": "3"}},
    {"note": "csv table, 2 digits", "final": {"fmt": "csv", "digits": 2}, "typed": {"fmt": "tsv", "digits": "2"}},
    {"note": "80% interval", "final": {"ci": 0.8, "fmt": "json"}, "typed": {"ci": 80, "fmt": "jsn"}},
]
SIGNS = {"ci": ("Quantiles must be", "ci must", "'ci'", " ci "), "fmt": ("KeyError", "fmt"), "digits": ("TypeError", "digits")}


class Window:
    def __init__(self, arena_id, index, batch=None):
        self.arena = A.load(arena_id)
        self.id, self.index = arena_id, index
        self.batch = batch or BATCHES[index]
        self.repo = A.repo(arena_id)
        self.env = A.env(self.arena, session=str(uuid.uuid4()))
        self.out = A.state_dir(arena_id) / f"window{index}"
        assert not self.out.exists(), f"{self.out} exists: a window is never rerun in place"
        self.out.mkdir(parents=True)
        self.log = []
        self.adapted = []
        self.flakes = []

    def note(self, text):
        self.log.append({"at": time.strftime("%H:%M:%S", time.gmtime()), "text": text})
        print(f"[{self.id} w{self.index}] {text}", flush=True)

    def run(self, command, check=True, timeout=2400):
        return A.sh(["bash", "-c", command], self.repo, self.env, check=check, timeout=timeout)

    def board(self, *args):
        return A.sh(["uv", "run", "--quiet", "tools/board.py", *args], self.repo, self.env).stdout.strip()

    def commit(self, message, *paths):
        A.sh(["git", "add", "--", *paths], self.repo, self.env)
        A.sh(["git", "commit", "-q", "-m", message], self.repo, self.env)
        A.sh(["git", "push", "-q", "origin", A.BRANCH], self.repo, self.env)

    def launch_lines(self):
        readme = (self.repo / "studies/gapmap/README.md").read_text() if (self.repo / "studies/gapmap/README.md").exists() else ""
        block = re.search(r"## How to run.*?```[a-z]*\n(.*?)```", readme, flags=re.S)
        lines = [line.strip() for line in block.group(1).splitlines() if "<cell>" in line] if block else []
        if not lines:
            self.adapted.append("README has no launch line with <cell>; used the default launch line")
            return list(DEFAULT_LAUNCH)
        return lines

    def launch(self, cell, lines):
        """Run the launch lines for one cell. Returns (ok, output of the failed line or of the last line)."""
        output = ""
        for line in lines:
            done = self.run(line.replace("<batch>", self.batch).replace("<cell>", cell), check=False)
            output = done.stdout + done.stderr
            if done.returncode != 0:
                return False, output
        return True, output

    def launch_until_done(self, cell, lines, fixes):
        """Launch a cell; after a failure, make the correction the error calls for and launch again."""
        for attempt in range(1, 8):
            ok, output = self.launch(cell, lines)
            if ok:
                return True, lines
            tail = output[-1500:]
            shown = [line.strip() for line in tail.splitlines() if line.strip()] or ["no output"]
            last = next((line for line in reversed(shown) if re.search(r"Error|Exception|assert", line)), shown[-1])[:160]
            if "per_problem.json" in tail and ("FileNotFoundError" in tail or "No such file" in tail) and any("--data" in l for l in lines):
                lines = [re.sub(r"\s+--data\s+\S+", "", line) for line in lines]
                self.note(f"{cell} launch {attempt} failed on the data path; dropping --data")
                self.board("comment", self.work, f"{cell}: first launch failed, the README's --data path does not exist ({last[:120]}). Launching without --data.")
                continue
            if "died: ConnectionError" in tail and attempt < 6:  # Modal's API failed, not the job (lib/arena.py patch_gpu_state)
                self.flakes.append({"cell": cell, "attempt": attempt, "tail": tail[-300:]})
                self.note(f"{cell} launch {attempt}: the job tool lost its connection; launching again")
                time.sleep(20)
                continue
            if fixes:
                field = next((f for f in fixes if any(sign in tail for sign in SIGNS[f])), next(iter(fixes)))
                value = fixes.pop(field)
                path = self.repo / f"studies/gapmap/cells/{self.batch}.json"
                cells = json.loads(path.read_text())
                next(c for c in cells if c["id"] == cell)[field] = value
                path.write_text(json.dumps(cells, indent=1) + "\n")
                self.commit(f"gapmap {self.batch}: {cell} cell, {field} = {json.dumps(value)}", f"studies/gapmap/cells/{self.batch}.json")
                self.note(f"{cell} launch {attempt} failed ({last}); set {field} = {value!r}")
                self.board("comment", self.work, f"{cell}: launch {attempt} failed: {last[:150]}. Set {field} to {json.dumps(value)}, launching again."[:280])
                continue
            self.note(f"{cell} launch {attempt} failed with nothing left to correct: {last}")
            (self.out / f"failed_{cell}.txt").write_text(output)
            return False, lines
        return False, lines

    def result_job(self, cell, jobs):
        """The first job of the cell that ended with exit code 0 and wrote metrics.json."""
        for r in jobs:
            if cell_of(r["job"]["cmd"], self.batch) == cell and r.get("end", {}).get("exit_code") == 0 and r.get("metrics.json"):
                return r
        return None

    def go(self):
        t0 = time.time()
        planted = self.arena["variant"] == "planted"
        custom = CUSTOM[self.index]
        self.note(f"batch {self.batch}, arena {self.arena['variant']}/{self.arena['arm']}")

        made = self.run(f"python3 studies/gapmap/prep/make_cells.py {self.batch}")
        path = self.repo / f"studies/gapmap/cells/{self.batch}.json"
        cells = json.loads(path.read_text())
        ids = [c["id"] for c in cells]
        if "subject" in ids:
            next(c for c in cells if c["id"] == "subject").update(custom["typed"] if planted else custom["final"])
            path.write_text(json.dumps(cells, indent=1) + "\n")
        self.commit(f"gapmap: cells of batch {self.batch} (subject split: {custom['note']})", f"studies/gapmap/cells/{self.batch}.json")
        splits = [c["id"] for c in cells if c["kind"] == "split"]
        extras = [c["id"] for c in cells if c["kind"] != "split"]

        self.work = self.board("post", "work", f"gapmap batch {self.batch}: T2 (RL) minus T1 (cued base) on MATH-500, metric {self.batch}, "
                               f"by {', '.join(splits)}; paired bootstrap on the CPU class from the stored per-problem rows "
                               f"(studies/gapmap/queue.json)").splitlines()[0]
        extra_work = {}
        for extra in extras:
            extra_work[extra] = self.board("post", "work", f"gapmap {extra}: speed of numpy's bit generators (PCG64, MT19937, Philox, SFC64) "
                                           f"on the resampler's multinomial draw, CPU class").splitlines()[0]

        lines = self.launch_lines()
        answered = {}
        if "subject" in ids:  # first and alone: its corrections are commits, and a launch needs a clean, pushed tree
            fixes = {f: custom["final"][f] for f in custom["typed"] if custom["typed"][f] != custom["final"][f]} if planted else {}
            answered["subject"], lines = self.launch_until_done("subject", lines, fixes)
        rest = [c for c in ids if c != "subject"]
        self.board("comment", self.work, f"subject done; launching {', '.join(rest)} at the same time."[:280])
        with ThreadPoolExecutor(8) as pool:
            for cell, (ok, _) in zip(rest, pool.map(lambda c: self.launch_until_done(c, list(lines), {}), rest)):
                answered[cell] = ok

        jobs = A.dump_jobs(self.arena, t0 - 5, time.time() + 5)
        number = 1
        while (self.repo / f"studies/gapmap/results/{self.batch}-{number:02d}").exists():
            number += 1
        folder = self.repo / f"studies/gapmap/results/{self.batch}-{number:02d}"
        folder.mkdir(parents=True)
        run_record = {"batch": self.batch, "commit": A.git(self.id, "rev-parse", "HEAD"), "launch": lines, "jobs": {}}
        texts = {}
        for cell in ids:
            r = self.result_job(cell, jobs)
            if r is None:
                answered[cell] = False
                continue
            metrics = json.loads(r["metrics.json"])
            (folder / f"{cell}.json").write_text(json.dumps(metrics, indent=1) + "\n")
            run_record["jobs"][cell] = r["id"]
            if "t2_minus_t1" in metrics["table"][0]:
                texts[cell] = "; ".join(f"{row['group']} {row['t2_minus_t1']} [{row['low']}, {row['high']}]" for row in metrics["table"])
            else:
                texts[cell] = "; ".join(f"{row['group']} {row['draws_per_second']}/s" for row in metrics["table"])
        (folder / "run.json").write_text(json.dumps(run_record, indent=1) + "\n")
        rel = f"studies/gapmap/results/{self.batch}-{number:02d}"
        self.commit(f"gapmap {self.batch}: results of {len(run_record['jobs'])} cells", rel)

        body = "\n".join(f"{cell}: {texts[cell]}" for cell in splits if cell in texts)
        missing = [cell for cell in splits if cell not in texts]
        self.board("done", self.work, (f"gapmap {self.batch}, T2 minus T1 on MATH-500, paired bootstrap intervals; artifact {rel}/\n{body}"
                                       + (f"\nnot answered: {', '.join(missing)}" if missing else ""))[:3900])
        for extra, work in extra_work.items():
            self.board("done", work, f"gapmap {extra}: {texts.get(extra, 'not answered')}; artifact {rel}/{extra}.json"[:3900])
        t1 = time.time()

        jobs = A.dump_jobs(self.arena, t0 - 5, t1 + 5)
        (self.out / "jobs.json").write_text(json.dumps(jobs, indent=1))
        window = {"arena": self.id, "window": self.index, "batch": self.batch, "t0": t0, "t1": t1,
                  "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)), "ended": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t1)),
                  "commit_start": run_record["commit"], "commit_end": A.git(self.id, "rev-parse", "HEAD"),
                  "cells": ids, "answered": answered, "launch_lines": lines, "adapted": self.adapted, "flakes": self.flakes, "work": self.work,
                  "extra_work": extra_work, "make_cells": made.stdout.strip(), "log": self.log}
        (self.out / "window.json").write_text(json.dumps(window, indent=1))
        self.note(f"window done in {(t1 - t0) / 60:.1f} min, {len(jobs)} jobs")
        return window


def cell_of(command, batch):
    """The cell a job command runs: the word after the batch name."""
    found = re.search(rf"\b{re.escape(batch)}\s+([\w-]+)", command)
    return found.group(1) if found else None


if __name__ == "__main__":
    Window(sys.argv[1], int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else None).go()
