# Audit of the English on the public site, 2026-11-15

The public text has 1,474 writing issues, and six causes produce most of them. 41 issues are serious: a newcomer
misreads the result or cannot tell what the page claims. 657 make a newcomer stop and re-read. 776 are minor.
Nothing was edited. This file is the summary; every issue, with its line, the exact words and a rewrite, is in
`issues.md` (by file) and `issues.jsonl` (the same rows for a script).

Board work item: work-98b9cd. Line numbers are from main at about fd99b40.

## What was read

| Text | Source | Issues |
|---|---|---|
| 29 finding pages and their tiles | `tools/finding_*.py` | 765 |
| Home, Board, Findings and Proof grids, Papers page, glossary, people | `tools/home.py`, `view.py`, `findings.py`, `papers.py`, `glossary.py`, `people.py` | 108 |
| Values, Exa, past.dev, Psychosis game, 2 proof pages, lab index and 12 lab pages | `tools/values.py`, `exa_page.py`, `pastdev.py`, `psychosis.py`, `proof_*.py`, `studies/sitelab/` | 197 |
| 5 papers | `studies/*/paper*/paper.tex` | 196 |
| 117 result rows of the Board (title, what, why, caveat) | live `/data`, read 21:10 UTC | 208 |

Not read: `/demo` (excluded by the owner), `README.md` (the repository is private), gpu.invariant.team (its source
was not located), 8 lab pages added during the audit (call-it, `ledger`, library, mobile, music-box, one-take, tide,
vote-machine), and the Design page, which was deleted during the audit. `tools/home.py` and `tools/papers.py` were
being rebuilt by other sessions while they were read, so their rows may be out of date.

## How it was done

Eight proofreaders, each a fresh Claude Opus session with its own pages, listed issues against one rule sheet
(`RULES.md`): 23 kinds of issue in five groups, each reported only with what the reader cannot do because of it.
They were told to report everything and not to filter. One more fresh session did a cold read with no rules and no
context (`cold_read.md`). The rule sheet comes from the sources in `sources.md`: Anthropic's guide "Prompting Claude
Fable 5.2", the US plain-language guidelines, the GOV.UK writing guidelines, ASD-STE100, and Nielsen Norman Group's
reading studies.

How far to trust the list: the proofreaders judged style, and a reviewer asked for problems always finds some, so
the severity 1 rows include matters of taste. A script found the first words of the quoted text in the cited file
for 973 of 1,266 page and paper rows; most of the other 293 quote a sentence that the page assembles from numbers at
run time. I read all 12 serious page issues and they hold up on their face. I did not check the rest row by row.

## The cold read

A reader told nothing about the project read the home page, the 31 tiles and 25 board results once. Of the 31
tiles it understood 9, partly understood 15 and did not understand 7. It could say what the team does, and it
guessed the main result with low confidence. It reported that the site never says why the result matters. The
words it had to guess most often: RL, base, cue, sample, direction, cap and cut-off, "328 harder problems",
Think-SFT, vote, and the numbers in square brackets.

## The six causes

| Issue | Count | Serious |
|---|---|---|
| Team label not explained | 256 | 22 |
| Compressed phrase | 217 | 7 |
| Inside talk | 108 | 0 |
| Metaphor or slang | 100 | 1 |
| Number without unit, total or comparison | 98 | 3 |
| Field term not explained | 97 | 1 |
| One thing with several names | 85 | 0 |
| Unclear reference | 83 | 0 |
| Grammar or format | 62 | 0 |
| Claim stronger than the evidence beside it | 58 | 3 |
| Overloaded sentence | 55 | 0 |
| Title names the topic, not the result | 50 | 0 |
| Caveat hidden | 44 | 4 |

1. The pages use the team's working names as if the visitor knew them. "Base + cue" appears on 25 of the 31
   finding and proof pages, about 80 times on seven of them alone, and is explained on a few pages inside a panel.
   "Think-SFT", "the 328 harder problems", "grader v3", "size 1.5", "restart", "the theory engine" and "the board"
   are used the same way. "RL" is never spelled out on any finding page. The glossary cannot help on the tiles:
   it does not mark a term inside a link, and a tile is a link. This one cause holds 22 of the 41 serious issues.

2. Sentences are compressed into notation. Examples: "a = 2 minus Think-SFT: +6.9 points … Minus RL: +9.6
   points."; "Cut off: 93 at 16,384, 2 at 32,768."; "(n 500, T 1.0 / top-p 1.0, v3, 1 sample, seed 182000000)".
   The reader has to rebuild the verb, the unit and the thing counted. "Points" is rarely said to mean percentage
   points, and a pair of numbers in square brackets is rarely said to be a 95 % interval.

3. Text written for the team is shown to the public: board ids ("result-855858"), commit ids, file paths, "the
   committed file", "the spec", "the job hung twice", "lost with its box; rerunning on AWS". 14 board results
   give "Not known yet." as the reason the result matters.

4. Titles are figures of speech or topics, not results: "The finish dial", "Theories on trial", "Two jobs in one
   edit", "RL avoids the slip", "A quarter of RL". A scanning visitor reads the title and the first sentence
   only, and on most finding pages neither states the result in words they know. The same holds for paper section
   titles and captions ("The dial."). Every "What is new" panel opens with earlier work and reaches the new
   result later.

5. One thing has several names. The weight change is "RL weight change", "weight edit", "edit" and "change". An
   answer that hits the token limit is "cut off", "cap hit", "stuck", "unfinished" and "never ends". "RL" names
   both the method and the trained model. "Recall" is a memory lookup on the past.dev page and a metric in the
   field. Percent is written "122 %" and "79%", sometimes on one page.

6. Headlines claim more than the page's own numbers support, or leave the caveat for the panel.
   - "RL avoids the slip": the page's own 95 % interval includes no effect.
   - Forecasts page: "Theories beat both no-theory readers in 65 of 162 forecasts", while outside one experiment
     the theories are at chance (26 of 82, chance 27).
   - Proof tile: "cut compute per batch from 16.3 to 4.4 minutes" does not say the waste was planted for the test.
   - "Gap closed without reward": at the token cost of one RL sample, 79 % of the gap is closed.
   - "A quarter of RL": the edit is 0.42 of the norm after bf16 rounding.
   - Exa page: "Every agent's work cycle passes Exa", which the page's limits section contradicts.

Also frequent: slang and metaphor on the Values and lab pages ("regime escape", "real estate in the context",
"good ol' hustle", "maxxing", "mid-yap"), and one use of a word the owner has banned, in the theory paper at line
287.

## The 12 serious issues on pages

| Page | Line | Words | Why a newcomer misreads |
|---|---|---|---|
| `finding_base_opens_itself.py` | 842 | "Prefilled cue" | The page never shows what the cue is, so the finding cannot be followed. |
| `finding_forecasts_before_results.py` | 506 | "Theories beat both no-theory readers in 65 of 162 forecasts…" | Reads as a win; outside one experiment the theories are at chance. |
| `finding_forecasts_before_results.py` | 564 | "Seven rounds of the theory engine…" | Theory engine, rounds and theories are never explained. |
| `finding_how_much_of_the_gap.py` | 265 | "With no reward, Think-SFT closes 122 % of the gap from Base + cue to RL." | Two team labels in the headline. |
| `finding_one_difficulty_axis.py` | 91 | "…no more than one difficulty order predicts: −0.05 problems over 618 pairs." | The measure and the number cannot be read (headline and tile). |
| `finding_rl_change_on_imitation.py` | 118 | "Twice RL's weight change lifts Think-SFT from 209 to 231.5 of 328; RL scores 200." | Think-SFT is explained nowhere on the page. |
| `finding_rl_reliability.py` | 48 | "…by fixed rules, 66 % for RL and 71 % for a random weight change…" | Follows "81 %" with no word on the different measure. |
| `finding_the_finish_dial.py` | 204 | "Enlarging 8 RL directions makes answers finish: at size 1.5, 203 of 328 are right…" | Three team terms and no baseline. |
| `finding_where_the_gap_goes.py` | 74 | "66 % of the RL gap is problems the base sometimes solves; with a random weight change, 71 % of its gap." | The point (the split also appears without RL) is hidden. |
| `finding_rl_avoids_the_slip.py` | 61 | "RL avoids the slip" | The title states an effect the interval does not support. |
| `proof_review_cuts_waste.py` | 31 | "…cut compute per batch from 16.3 to 4.4 minutes." | Does not say the waste was planted. |

(`finding_one_difficulty_axis.py` line 91 counts twice: as the headline and as the tile.) The 29 serious board
rows are in `issues.md` under "board"; 22 of them are unexplained labels in a title or a `what` field.

## Numbers that disagree between pages

These are for a check against the artifacts, not for a rewrite.

- Think-SFT's vote over 4 samples on the 328 problems is 236 on `finding_how_much_of_the_gap.py` and 241 on
  `finding_imitation_beats_rl.py`.
- `finding_where_the_gap_goes.py` says 66 % of the RL gap is on problems the base sometimes solves;
  `finding_rl_reliability.py` says 81 % of the RL gain. Neither names its measure.
- Board result fad48d says the cue equals the first 100 RL steps; result 6832a8 says that equality is not earned.
  Result d92d4a's 414 of 500 was later found to be mostly seed noise by result 460e0a. The older rows still stand.
- The address `/finding/vote-over-four` now carries a title about 6 samples.
- The home headline, on the board snapshot of 21:10 UTC, compares a base vote over 12 samples with an RL vote
  over 4 samples with restarts, and does not say so.

## Pages that read well

The Psychosis game, the glossary definitions, the Board's empty states, the Values page apart from its lead
sentences, and the paper "Two Token Limits". Among finding pages `finding_equal_token_frontier.py`,
`finding_cut_off_is_unfinished.py`, `finding_rl_edge_comes_early.py`, `finding_rl_every_neuron.py` and
`finding_vote_over_four.py` have mostly minor issues. Best board rows: result-59ed1a, result-5d032f,
result-c36598, result-96e819, result-dadeec.

## Issues per file

| File | Serious | Re-read | Minor | Total |
|---|---|---|---|---|
| Board result rows | 29 | 100 | 79 | 208 |
| `studies/theory/paper/paper.tex` | 0 | 20 | 28 | 48 |
| `studies/rlneurons/paper/paper.tex` | 0 | 19 | 28 | 47 |
| `studies/rlneurons/paper-first-steps/paper.tex` | 0 | 20 | 23 | 43 |
| `tools/finding_a_quarter_of_rl.py` | 0 | 17 | 23 | 40 |
| `tools/finding_rl_change_on_imitation.py` | 1 | 18 | 19 | 38 |
| `tools/finding_the_finish_dial.py` | 1 | 16 | 20 | 37 |
| `studies/rlneurons/paper-no-warning/paper.tex` | 0 | 13 | 22 | 35 |
| `tools/exa_page.py` | 0 | 11 | 24 | 35 |
| `tools/finding_how_much_of_the_gap.py` | 1 | 15 | 16 | 32 |
| `tools/finding_rl_directions_move_activations.py` | 0 | 16 | 16 | 32 |
| `tools/finding_opening_cue.py` | 0 | 18 | 13 | 31 |
| `tools/finding_rl_reliability.py` | 1 | 17 | 12 | 30 |
| `tools/view.py` | 0 | 12 | 18 | 30 |
| `tools/finding_forecasts_before_results.py` | 2 | 18 | 9 | 29 |
| `tools/finding_theories_on_trial.py` | 0 | 16 | 13 | 29 |
| `tools/finding_two_jobs_in_the_edit.py` | 0 | 15 | 14 | 29 |
| `tools/pastdev.py` | 0 | 13 | 16 | 29 |
| `tools/finding_imitation_beats_rl.py` | 0 | 11 | 17 | 28 |
| `tools/finding_rl_avoids_the_slip.py` | 1 | 16 | 11 | 28 |
| `tools/finding_restart_on_cap.py` | 0 | 14 | 13 | 27 |
| `tools/finding_rl_learns_the_opening_first.py` | 0 | 11 | 16 | 27 |
| `tools/finding_base_opens_itself.py` | 1 | 13 | 12 | 26 |
| `tools/finding_cue_on_code.py` | 0 | 13 | 13 | 26 |
| `tools/findings.py` | 0 | 11 | 14 | 25 |
| `tools/finding_hand_written_edit.py` | 0 | 10 | 14 | 24 |
| `tools/finding_one_difficulty_axis.py` | 2 | 10 | 12 | 24 |
| `tools/finding_cut_off_is_unfinished.py` | 0 | 13 | 10 | 23 |
| `tools/finding_eight_directions.py` | 0 | 10 | 13 | 23 |
| `tools/finding_rl_edge_comes_early.py` | 0 | 10 | 13 | 23 |
| `studies/rlneurons/paper-two-caps/paper.tex` | 0 | 6 | 17 | 23 |
| `tools/finding_no_early_warning.py` | 0 | 8 | 14 | 22 |
| `studies/sitelab/index.html` | 0 | 5 | 17 | 22 |
| `tools/finding_rl_every_neuron.py` | 0 | 7 | 14 | 21 |
| `tools/finding_rl_wait_habit.py` | 0 | 9 | 12 | 21 |
| `tools/finding_where_the_gap_goes.py` | 1 | 13 | 6 | 20 |
| `tools/papers.py` | 0 | 9 | 11 | 20 |
| `tools/finding_equal_token_frontier.py` | 0 | 9 | 10 | 19 |
| `tools/finding_loop_neurons.py` | 0 | 11 | 8 | 19 |
| `tools/finding_vote_over_four.py` | 0 | 7 | 12 | 19 |
| `tools/home.py` | 0 | 11 | 8 | 19 |
| `tools/finding_neurons_you_can_describe.py` | 0 | 7 | 11 | 18 |
| `tools/proof_idea_basins.py` | 0 | 9 | 9 | 18 |
| `tools/proof_review_cuts_waste.py` | 1 | 8 | 9 | 18 |
| `tools/values.py` | 0 | 4 | 9 | 13 |
| `tools/glossary.py` | 0 | 4 | 8 | 12 |
| `tools/psychosis.py` | 0 | 0 | 11 | 11 |
| 12 lab pages under `studies/sitelab/prototypes/` | 0 | 13 | 38 | 51 |
| `tools/people.py` | 0 | 1 | 1 | 2 |

## What the research says, in short

The full digest with links is in `sources.md`.

- For the writing: put the key point in the first sentence; write for an intelligent reader with no context; use
  no term made up during the work; when short and clear conflict, choose clear; use a literal phrase where one
  exists. A hard limit on sentence length makes Fable 5.2's prose choppy, so sentence length is a guide here and
  not a rule a proofreader enforces. (Anthropic, "Prompting Claude Fable 5.2" and the Fable 5 and 5.1 guides.)
- For the reader: 79 % of web users scan and they read about 20 % of the words. Text that was concise, scannable
  and objective together measured 124 % better usability than promotional text; objective wording alone, 27 %.
  (Nielsen Norman Group.) Sentences over 25 words get split; a specialist term is explained at first use. (GOV.UK.)
- For presenting our own results: the title states the result, the abstract tells the whole story, each claim
  sits beside its evidence. (Mensh and Kording 2017.) Short titles that state the result are cited more than
  titles that state the method.
- For briefing a proofreader: a fresh session with no view of the author's reasoning; a brief with the objective,
  the reader, the boundaries and the output format; the reason behind each rule; plain wording without capitals
  for emphasis; report everything and filter in a separate pass. (Anthropic's Claude Code best practices and
  multi-agent research post.)

## Files

- `meta/copy-audit/README.md`: this summary.
- `meta/copy-audit/issues.md`: all 1,474 issues by file, each with line, words, problem and rewrite (1,241 have a
  rewrite; 233 need facts the proofreader did not have).
- `meta/copy-audit/issues.jsonl`: the same rows, one JSON object per line.
- `meta/copy-audit/cold_read.md`: the cold read, tile by tile.
- `meta/copy-audit/RULES.md`: the rule sheet the proofreaders used.
- `meta/copy-audit/sources.md`: the research digest with links.

## After the fixes (same day, branch `copy`)

Editors fixed wording in 28 finding pages, the glossary (17 terms added), the Findings grid, the Board and home
pages, the Psychosis game, the review-cuts-waste proof page and the five papers. Reviewers with no view of the
editors' reasoning then read the whole diff and found 49 defects; the 34 that changed meaning were fixed or the edit
was taken out, and 15 about longer headlines were left for the owner. The second cold read of the 31 tiles
(`cold_read_after.md`): 17 understood, 13 partly, 1 not understood (before: 9, 15, 7).

Not changed: `/demo` and the three pages the deck embeds (`tools/exa_page.py`, `tools/pastdev.py`,
`tools/proof_idea_basins.py`); `tools/values.py` (the owner's own words); `tools/finding_the_finish_dial.py` and
`tools/finding_rl_change_on_imitation.py` (rewritten by other sessions the same hour); `tools/papers.py`,
`tools/finding_two_jobs_in_the_edit.py`, most of `tools/finding_theories_on_trial.py`; the lab pages; the board's
result rows (a draft exists and was not applied).
