"""Pack every review's files for the judge of rubric_v2.md, under neutral names.

  MH_HOME=<dir> python3 -m studies.metaharness.grader.judge_pack

Writes $MH_HOME/judge/r<nn>.md, one per review run in shuffled order (seed 0), and $MH_HOME/judge/map.json
(r<nn> -> experiment, run, round). A pack holds the session's final message, the entry it added to meta/dana.md (the
newest entry only), the list of changed files, and the diff without the files under meta/ (at most 14,000 characters).
The arm is not named anywhere in a pack; a pack with an entry is from the skill arm, which the judge can see.
"""
import json
import random
import re

from studies.metaharness.lib import arena as A

arenas = json.loads((A.STUDY / "data" / "planted_arenas_v1.json").read_text())
packs = []
for experiment in ("planted", "clean"):
    for run, arena_id in arenas[experiment].items():
        for folder in sorted(A.state_dir(arena_id).glob("review[0-9]")):
            packs.append((experiment, run, int(folder.name[6:]), folder))
random.Random(0).shuffle(packs)
out = A.HOME / "judge"
out.mkdir()
mapping = {}
for index, (experiment, run, round_index, folder) in enumerate(packs, 1):
    name = f"r{index:02d}"
    mapping[name] = {"experiment": experiment, "run": run, "round": round_index}
    entry = ""
    if (folder / "meta_entry.md").exists():
        found = re.search(r"^## .*?(?=^## |\Z)", (folder / "meta_entry.md").read_text(), flags=re.S | re.M)
        entry = found.group(0) if found else ""
    sections = re.split(r"(?=^diff --git )", (folder / "change.diff").read_text(), flags=re.M)
    code = "".join(part for part in sections if part.startswith("diff --git") and not re.match(r"diff --git a/meta/", part))
    text = (f"# Review {name}\n\n## Final message of the session\n\n{(folder / 'final_message.md').read_text()}\n\n"
            f"## Entry added to meta/dana.md (empty when the session wrote none)\n\n{entry}\n\n"
            f"## Files changed\n\n```\n{(folder / 'files.txt').read_text()}\n```\n\n"
            f"## Diff, without files under meta/ ({len(code)} characters, shown up to 14,000)\n\n```diff\n{code[:14000]}\n```\n")
    (out / f"{name}.md").write_text(text)
(out / "map.json").write_text(json.dumps(mapping, indent=1))
print(len(packs), "packs in", out)
