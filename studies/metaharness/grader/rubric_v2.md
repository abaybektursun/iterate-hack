# Rubric v2: scoring one review run of the planted-waste test

Fixed on 2026-11-15, before any review run. The plants are in `answer_key_v1.json`.

A review run is one fresh agent session. Its written output is: the entry it added to `meta/dana.md` (skill arm), the
session's final message, and any file it wrote. Its change is the diff of the work branch from before the session to
after it.

Per review run and per plant P1 to P6 that was present in the window before the review:

1. **named** (0 or 1). The written output states the plant: it points at the thing (the file, the step or the jobs) and
   says that it costs time or is not needed. A general remark ("jobs are slow", "some jobs failed") is 0. A plant that
   is only listed in a copied table of jobs, with no statement about it, is 0. The sentence that earns the 1 is quoted
   in the score file.
2. **changed** (0 or 1). The diff changes the cause named in the answer key, or changes another file in a way meant to
   remove the same waste. A proposal that is not in the diff is 0.
3. **removed** (0 or 1), mechanical: `present_when` of the answer key is true in the window before the review and false
   in the window after it (`grader/score_window.py`).
4. **recurs** (0 or 1), mechanical: removed after one round and present again in a later window.

Per review run, also:

- **answers kept**: of the 4 required cells of the next window, how many have a table equal to the reference
  (`data/gapmap_reference_v1.json`). A change that loses or alters an answer is reported next to the waste it removed.
- **other claims**: inefficiencies the output names that are not one of the six plants, one line each, with whether
  the window's records show them. They are listed, not scored.
- **cost**: session minutes, turns, USD, and the job minutes the session itself spent.

Clean windows: a **false alarm** is a clean-window review that names one of the six classes as present. The change a
clean-window review makes is reported with its effect on the next window (waste share, answers kept).

named and changed are judged from the text and the diff by a judge agent that gets this rubric, the answer key and the
review's files with the arm label removed from the folder name; every 1 carries its quote, and the study's author
checks each quote against the file. removed and recurs come from the job records only.
