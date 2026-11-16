# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3>=1.35"]
# ///
"""The Team page of the site: who the team is. view.py serves PAGE at /team; the home dial leads to it.

Three columns, one per person, in the order of their first board post: the name, a link to their GitHub profile (the
login is the board name and is public in the repository's history), one or two sentences on what they worked on here,
written from their own board items and commits, two or three of their results with links to the pages that show them,
and four counts. Below the columns, one picture: every board item of the three people as one mark on a shared time
axis in San Francisco time (solid: result, hollow: work item, small: idea or note), stacked by time bin, drawn once
on load. A click on a mark, or the arrow keys on a focused row, select an item: its title and a link to it on the
board show under the picture, and the address holds its id (/team#result-c36598). Esc clears the selection.

The optional fields role, before and contact are shown only when filled. Nobody has written them yet, so they are
empty: do not fill them from anything but the person's own words.

COUNTED, COUNTS and MARKS are literals so that the page needs no board read and no git at import (the Lambda has
neither). `uv run tools/people.py --write` reads every board item and the commits of the checked-out code and writes
them; `uv run tools/people.py` recomputes them at the stored time and commit and stops with an error if they differ.
Commits are matched to a person by the GitHub login in the author's address, the rule of team.who(); merges are left
out. Run both from the repository root.
"""
import html
import json

PEOPLE = [
    {"login": "abaybektursun", "name": "Abay Bektursun",
     "work": "Abay posted the team's first result, the opening cue, which takes the base model from 224 to 410 "
             "of 500 on MATH-500, and wrote the engine of the theory study, which tests explanations of the results on "
             "stored data. They also showed that enlarging the 8 largest directions of RL's weight change makes the base "
             "model finish its answers, forecast GPU rental prices for the hackathon's challenge, and ran the design "
             "rounds of this site.",
     "results": [("The opening cue", "/finding/opening-cue"), ("RL's gain in eight directions", "/finding/the-finish-dial"),
                 ("The Finish Dial, a paper", "/papers#the-finish-dial")],
     "role": None, "before": None, "contact": None},
    {"login": "sameraslan", "name": "Samer Aslan",
     "work": "Samer studied what RL changes inside Olmo 3: which neurons it changes, what a J-lens reads in the base and "
             "the RL model, and which weight edits recover RL's gain. They also wrote one weight edit by hand that makes "
             "the base model write the opening cue, measured how the team's review procedure cuts wasted compute, and "
             "wrote the site's design rules.",
     "results": [("Hand-written edit", "/finding/hand-written-edit"), ("Loop neurons", "/finding/loop-neurons"),
                 ("Review cuts waste", "/proof/review-cuts-waste")],
     "role": None, "before": None, "contact": None},
    {"login": "frustea", "name": "Ali Rad",
     "work": "Ali grouped every board item by the idea it pursues, with a language model as the judge, and compared the "
             "team's harness with Karpathy's autoresearch loop on problems neither had seen. They also tested the opening "
             "cue on 500 questions outside math and code, ran rounds 05 to 07 of the theory study, and made four slides "
             "of the talk.",
     "results": [("Idea basins", "/proof/idea-basins"), ("The cue beyond math", "/finding/cue-on-code"),
                 ("Against Karpathy's autoresearch", "/demo#efficiency")],
     "role": None, "before": None, "contact": None},
]
FIELDS = (("role", "Role"), ("before", "Before"), ("contact", "Contact"))
HUES = [325, 150, 65, 195, 105, 45, 175, 350]  # a person's color by their place in the sorted board names, as on every page
KIND = {"result": 0, "work": 1}  # every other kind (idea, knowledge, skill) is 2: an idea or a note

COUNTED = {"names": ["abaybektursun", "frustea", "sameraslan"], "start_ns": 1794687266529267000, "at_ns": 1794789331343701000, "span": 1701, "commit": "a3a88c1", "first": "12:14 on 14 November", "at": "16:35 on 15 November"}

COUNTS = {"abaybektursun": {"results": 252, "work": 223, "ideas": 112, "items": 587, "commits": 842}, "sameraslan": {"results": 61, "work": 36, "ideas": 24, "items": 121, "commits": 154}, "frustea": {"results": 26, "work": 21, "ideas": 10, "items": 57, "commits": 58}}

MARKS = {
    "abaybektursun": [
        [0, 2, "idea-b19ad2", "Day-1 #1: score the 328 harder problems (not in RL training prompts) at T 1.0 / top-p 1.0 on both models: base with ope…"],
        [0, 2, "idea-1bd34f", "Day-1 #2: base with opening cue at T 0.6 / top-p 1.0 on MATH-500 (n=500), to separate temperature from top-p. Cue base…"],
        [0, 2, "idea-8b9cc7", "Day-1 #3: restart and four-sample vote rows on both models (base with cue, RL), MATH-500 then 328, with generated token…"],
        [0, 2, "idea-2eb58d", "Day-1 #4: weight-difference scaling study: base + a*(RL - base) for several a, with the Code-RL difference and a random…"],
        [1, 0, "result-c36598", "Base Olmo-3-1025-7B + opening cue, T 1.0 / top-p 1.0: 410/500 MATH-500 (82.0 %), grader v3, 27 cap hits. Plain base at…"],
        [1, 0, "result-533123", "Olmo-3.1-7B-RL-Zero-Math, plain prompt: 463/500 MATH-500 at T 1.0 (92.6 %), 464/500 at T 0.6 (92.8 %), grader v3. Tempe…"],
        [1, 0, "result-bac4fd", "Gap at AI2 setting (T 1.0): RL minus cue base = 10.6 points [7.4, 13.8] (paired bootstrap, 5000, n=500 MATH-500, grader…"],
        [1, 0, "result-e870a1", "Base + cue at T 0.6 / top-p 0.95: 354/500 MATH-500 (70.8 %), 119 cap hits (loops to 16,384 tokens). Restarting cap hits…"],
        [1, 0, "result-7968b8", "Base plain prompt, T 0.6: 319/500 MATH-500 (63.8 %, base-01 run) and 305/500 (61.0 %, n13 run), grader v3; 65 and 69 ca…"],
        [1, 2, "knowledge-42a54f", "72 of the 400 harder problems are in the RL-Zero-Math training prompts (43 exact, 29 near; AIME 2022 24/30, AIME 2023 2…"],
        [1, 2, "knowledge-781efc", "Grader matters: v1->v3 moved 113 items wrong->right and 1 right->wrong across 9 cells; plain base at T 1.0 gains 28 (19…"],
        [1, 2, "knowledge-c3f1bf", "RLN-3 jobs (AWS pg, T 0.6): first release (fr-01) and step 2800 exited 137 before finishing; fr-01 has no harder-set cu…"],
        [1, 2, "idea-884e91", "Open: a second model reads the grader-v3 rescoring (rln4_grader_v3.py + flip_review, 113 flips). DIRECTION.md slide ite…"],
        [1, 2, "idea-1fcafe", "Open: harder set (328) is scored only for base at T 0.6; RL and cue rows at both settings are missing. Covered by idea-…"],
        [1, 2, "idea-bd0240", "Open: score RL steps 400 and first release at T 0.6 once the jobs end (fr-01 is partial: no harder-set cue cell). DIREC…"],
        [6, 2, "knowledge-bc9f95", "Board items now show person/branch and record the agent type and session (tools/board.py, 12:22)."],
        [11, 2, "knowledge-c59b0c", "rlneurons code is on main (b83bab4) in studies/rlneurons/: graders v1-v3 (lib/n13_score, lib/rln4_lib), opening cue + i…"],
        [29, 2, "knowledge-e1d4b9", "rlneurons Day-1 #1 and #2 runnable on any Modal workspace via tools/gpu.py: studies/rlneurons/jobs/run_cell.py, command…"],
        [35, 0, "result-3cc231", "Coordination tools cost fewer calls and tokens (main 2d5ee99): post work and done announce on all; done <id> \"<result>\"…"],
        [46, 1, "work-220ce2", "Make the meta-review measure and push experiment turnaround: tools/cycle.py (claim->job->answer minutes, queue/run/fail…"],
        [48, 0, "result-57107f", "Turnaround is measurable in one command: uv run tools/cycle.py --hours N (main 4016064). First read, last 3 h of abaybe…"],
        [55, 1, "work-d8aa69", "Day-1 #1 idea-b19ad2: 328 harder problems at T 1.0/top-p 1.0, base+cue and RL, via run_cell.py on Modal H100. First the…"],
        [60, 1, "work-0b7cb3", "Visual board: tools/view.py, a local read-only web page (columns per kind, work idle time, all-channel stream, item pag…"],
        [62, 1, "work-63fac2", "Day-1 #3 idea-8b9cc7: make restart and 4-sample vote rows runnable (run_cell.py restart option, vote/restart analysis s…"],
        [62, 1, "work-55d1fe", "Day-1 #2 idea-1bd34f: base+cue MATH-500 at T 0.6/top-p 1.0, seed 1000000, run_cell.py on H100; separates temperature fr…"],
        [65, 1, "work-e55493", "Redesign tools/view.py: the board page as a designed product (typography, layout, live updates without reload, keyboard…"],
        [70, 1, "work-a50d39", "328 at T 1.0/top-p 1.0: the two cells missing from work-d8aa69 (base plain, RL cue; new seed base 50000000), a 50-probl…"],
        [75, 1, "work-169263", "Deploy the board page (tools/view.py) to AWS, public, one-command redeploy, then a custom domain monitor.<invariant dom…"],
        [77, 1, "work-a028d2", "Literature: find the most relevant unread papers for DIRECTION.md (cue vs RL gap on Olmo 3.1, sampling/loops, no-reward…"],
        [96, 2, "knowledge-29fdeb", "7 more papers read in full, 48 findings in past.dev (texts in papers/, gitignored; recall.py finds them). (a) 2510.1490…"],
        [96, 0, "result-bede69", "7 papers read in full, 48 findings added to past.dev (2510.14901, 2506.15710, 2510.02611, 2505.17813, 2505.11711, 2610.…"],
        [111, 0, "result-83bce1", "Board page is public: https://monitor.invariant.team (HTTPS, cert to 2027-05-31), live data every 10 s. Lambda + Web Ad…"],
        [115, 0, "result-82b4dc", "Harder 328, T 1.0/top-p 1.0, v3, 1 sample: base+cue 164/328 (50.0 %, 77 cap hits), RL 206/328 (62.8 %, 20 cap hits); RL…"],
        [115, 0, "result-dadeec", "base+cue MATH-500 T 0.6/top-p 1.0, v3: 378/500 (75.6 %), 98 cap hits, 71 loops, 4,690 tokens/problem. vs 354 (top-p 0.9…"],
        [119, 1, "work-90fce4", "Hill-climbing chart of the base-vs-RL gap: board.py score attaches a structured score (model, benchmark, right/n, confi…"],
        [125, 0, "result-8f83b7", "Hill-climbing chart live on https://monitor.invariant.team (main 7b73e3e): per benchmark, best untrained base vs best R…"],
        [130, 1, "work-fc7bc7", "Agent cooperation protocol: survey published multi-agent research-system practice (Anthropic, OpenAI, academic), then a…"],
        [135, 2, "knowledge-d907b4", "Multi-agent cooperation, published evidence (2 surveys, work-fc7bc7). Helps: shared findings forum (Anthropic AAR repor…"],
        [139, 1, "work-656182", "Scores from the result text: a line 'score: base MATH-500 378/500 tokens 4690 | <config>' in done or post result writes…"],
        [150, 1, "work-28b3f7", "gpuprice sub-project (Hackathon Track 2, Pacific 'AI Scientist for GPU Value'): quantile forecasts q10/q50/q90 of GPU r…"],
        [156, 0, "result-099916", "Harder 328, T 1.0/top-p 1.0, v3, 1 sample: base plain 76, base cue 164 (77 cap), RL plain 206, RL cue 205. T 0.6 rescor…"],
        [157, 0, "result-ef32ec", "gpuprice study started, branch gpuprice, studies/gpuprice/README.md. Starter demo reproduced: drift +0.200 pooled skill…"],
        [158, 0, "result-e5c99c", "328 harder, T 1.0/top-p 1.0, grader v3, one sample: RL plain minus base+cue +12.8 points [8.5, 17.1] (T 0.6: +25.9). Ba…"],
        [160, 1, "work-f74f02", "gpuprice: literature + data-source research for frontier-model forecasters (TS foundation models, LLM fine-tune, prior-…"],
        [166, 0, "result-3408cd", "gpuprice SPEC1: forecasting the median by resampling its listings' h-day outcomes (price change, exit, entry) scores +0…"],
        [172, 2, "knowledge-dbab0c", "gpuprice track brief read in full (PDF linked from iterate.inc/ai-research): origin 2026-11-06, h 1/3/7, target daily_s…"],
        [172, 2, "idea-9f3cf7", "gpuprice FX pass-through: Scaleway's posted USD price = fixed EUR price x previous day's ECB EUR/USD rate (d-log correl…"],
        [179, 1, "work-d36669", "Day-1 #4 idea-2eb58d + idea-e0a5a7: MATH-500 at T 1.0, base + a*(RL - base) for a 0.25/0.5/0.75/1.5 with the cue (a 0.2…"],
        [180, 0, "result-ead656", "gpuprice SPEC1 on unseen origins narrows result-3408cd: simulator unchanged on 6 origins 2026-10-31..11-05 (357 cells,…"],
        [181, 0, "result-5de032", "328 harder, T 1.0, v3, base+cue (164) vs RL plain (206), per problem: both 157, base only 7, RL only 49, neither 115. O…"],
        [184, 1, "work-976c17", "Analysis of all agents' work and traces for an optimization round: events store, board, GPU jobs, git, local + uploaded…"],
        [185, 2, "idea-b3bbb8", "gpuprice simulator v2 (running, subagent): per-provider repricing behaviour instead of pooled, hazard by time since las…"],
        [185, 2, "idea-aaea4c", "gpuprice foundation model at the listing level (running, subagent): amazon/chronos-2 zero-shot per series, with all 37…"],
        [185, 2, "idea-cb493f", "gpuprice open-weights LLM as the density over the provider panel (running, subagent): prompt = 21 days of every listing…"],
        [185, 2, "idea-a9997e", "gpuprice prior-fitted network on synthetic rate-card markets (not started; literature subagent still reading): simulato…"],
        [185, 2, "idea-fd3b4f", "gpuprice agent program search with locked origins (not started): agents propose forecaster programs, eval.sh scores on…"],
        [187, 1, "work-d84808", "Code pair (DIRECTION deliverable, unclaimed so far): base Olmo-3-1025-7B plain and with an opening cue vs Olmo-3.1-7B-R…"],
        [193, 0, "result-823cd1", "gpuprice hill-climb, dev origins Oct 1-30, 3,109 cells, pooled skill vs last value (ledger studies/gpuprice/results/led…"],
        [193, 0, "result-3b8656", "gpuprice external data (prep/ext_history.py, branch gpuprice 75a6aaa): +30 days for fastgpu_daily (to 2026-08-09) and g…"],
        [194, 0, "result-17a66c", "Day-1 turnaround analysis: median work item 0 min to first job, 46 min in jobs, 2 min to answer. One 328 cell = 51 min…"],
        [201, 1, "work-02efb7", "Port all relevant research from ../interp_research (rlneurons RLN-1..4, jmech J-lens on Olmo-3, next/ literature + WDD,…"],
        [202, 0, "result-c9b27e", "Math-RL and Code-RL weight differences from the same Olmo-3-1025-7B base are nearly orthogonal: cos 0.014 over 7.3 B en…"],
        [203, 0, "result-f63ca7", "gpuprice dev ledger best +0.292 pooled skill (h1 +0.163, h3 +0.270, h7 +0.340, in-band 0.74; 3,109 cells, origins Oct 1…"],
        [204, 2, "knowledge-c788b4", "From interp_research instruments E2 (a check of the Weight-Space Programming loop edit, complements knowledge-c9fc18 an…"],
        [204, 2, "knowledge-980cbf", "From interp_research instruments (E1, E1b, E5, E6b; complements work-383069 and result-156f7b): on Olmo-3-1025-7B, writ…"],
        [205, 2, "knowledge-4fb5eb", "From interp_research mechanics (Olmo-3 internals; complements work-383069, relevant to the base's loops at T 0.6 in res…"],
        [205, 2, "knowledge-3bc2ab", "From interp_research neuronoff (single-neuron ablation effect sizes; complements work-383069): zeroing one MLP neuron a…"],
        [206, 2, "knowledge-8229be", "From interp_research next/n13 (verdict_n13.json, CLAIMS.md, READ_head.md): the RL math gain of allenai/Olmo-3.1-7B-RL-Z…"],
        [206, 2, "knowledge-b8d41a", "From interp_research bytegraft (scaling and sparse copies of a fine-tune weight difference; complements work-d36669, re…"],
        [206, 2, "knowledge-2ded8a", "From interp_research bytegraft (how small a fitted patch carries a skill, and whether an LLM editor finds it; complemen…"],
        [206, 2, "idea-6f902e", "From interp_research next (20_ABSTRACT.md, 'The highest-leverage next step'; not run): rank test of the RL delta. For e…"],
        [206, 2, "knowledge-61acfa", "From interp_research jmech (README.md, SPEC.md, results/run2/metrics.json): on the Olmo-3-1025-7B base, a J-lens swap o…"],
        [207, 2, "knowledge-a7e534", "From interp_research jmech (README.md; e2, e3, e4, e5, e6 results/run*/metrics.json): on the Olmo-3-1025-7B base, a few…"],
        [207, 2, "knowledge-9c5052", "From interp_research rlneurons (RLN-1): RL barely moves which tokens a neuron fires on most. For each MLP neuron pole (…"],
        [207, 2, "knowledge-87618d", "From interp_research rlneurons (RLN-2): the base and RL models compute almost the same MLP activations on general text…"],
        [207, 2, "knowledge-6f3040", "From interp_research rlneurons (RLN-2 labels): an LLM judge compared each pole's top-activating contexts in base vs RL…"],
        [207, 2, "knowledge-69adda", "From interp_research rlneurons (prior study n13, the RL weight-transplant test that RLN-1 to RLN-3 build on): the MATH-…"],
        [207, 2, "knowledge-1497e8", "From interp_research rlneurons (RLN-4 K): the base with cue loops at T 0.6 partly because it cannot continue its own lo…"],
        [207, 2, "knowledge-9e4147", "From interp_research rlneurons (RLN-4 T1/T2/T3): the cued-base gap to RL at T 1.0 is in every length quartile and large…"],
        [207, 2, "knowledge-787e53", "From interp_research rlneurons (RLN-4 loop detectors): use the zlib rule (rule A), not a period rule or a repeated-line…"],
        [208, 2, "knowledge-814454", "From interp_research rlneurons (RLN-3/RLN-4 checks): the same model, prompt and per-request seeds on a different GPU mo…"],
        [208, 2, "knowledge-0b450e", "From interp_research rlneurons (RLN-3 setup facts, before any accuracy): facts needed to score Olmo RL checkpoints. (1)…"],
        [208, 2, "knowledge-499152", "From interp_research rlneurons (RLN-4 grader v3 limits): two known ways grader v3 errs, and the format split behind mos…"],
        [208, 2, "knowledge-16c252", "From interp_research next (01_JLENS.md, 22_JLENS_MECHANISM_LITERATURE.md): J-lens follow-ups that add to result-da11d0.…"],
        [208, 2, "knowledge-b748bb", "From interp_research next (01_JLENS.md, 22_JLENS_MECHANISM_LITERATURE.md, 04_RECENT.md): J-lens assets for Olmo 3, and…"],
        [208, 2, "knowledge-9d49a7", "From interp_research next (04_RECENT.md, 04_LITERATURE.md, 04_PRACTICAL.md, 04_WDD.md): literature on what RL and fine-…"],
        [209, 2, "knowledge-c1fe13", "From interp_research next (04_PRACTICAL.md, 00_ASSETS.md, 09_PLAN.md): capability-engineering numbers and Olmo 3 checkp…"],
        [216, 2, "idea-7c89d6", "From interp_research next (04_PRACTICAL.md K2, not run): merge the Math-RL and Code-RL deltas, with RL-Zero-Mix as the…"],
        [237, 2, "knowledge-9f8067", "Code pair facts (subagent read Olmo 3 report 2512.13961, HF cards, open-instruct; work-d84808). (1) AI2 publishes no co…"],
        [243, 2, "knowledge-da11af", "gpuprice literature, 5 subagents, papers read in full (findings in team memory): (1) TS foundation models barely beat n…"],
        [282, 2, "knowledge-b15a21", "Literature from interp_research, 30 papers read in full, 147 findings in past.dev (recall.py). What bears on the direct…"],
        [282, 0, "result-5cd266", "interp_research ported: 25 knowledge items + 2 ideas of its own results (rlneurons 10, jmech/next 9, neurons/weight edi…"],
        [283, 0, "result-9979f1", "gpuprice: LoRA of amazon/chronos-2 on 8,000 SYNTHETIC sticky-price series only (no real price) scores +0.295 pooled ski…"],
        [303, 0, "result-9b6af3", "MATH-500, T 1.0, v3, n=500, recount from raw rows of work-d36669 (second model): cue cells vs cued base 410: theta0.25…"],
        [315, 0, "result-9800c2", "gpuprice: a 4.8M-parameter transformer trained ONLY on synthetic sticky-price listings (11 listing types, 15.4M series,…"],
        [327, 0, "result-4b0d5f", "Day-1 #4 (work-d36669): a quarter of the RL weight difference gives most of the gain, and the direction is RL-specific…"],
        [328, 0, "result-8f257f", "MATH-500, T 1.0, v3, n=500, recounted from raw rows by a second model: base + a*(RL - base) with the cue scores 410/441…"],
        [354, 1, "work-b1086f", "Theory engine as a skill (.claude/skills/theory + studies/theory/lib/check.py): each round, agents propose theories fro…"],
        [355, 1, "work-43d4a1", "328 harder at T 1.0/top-p 1.0, cue, one sample: Code-RL, theta(0.25) and theta(0.5) = base + a*(RL - base); scored once…"],
        [356, 0, "result-6eef5d", "theory skill ready: .claude/skills/theory/SKILL.md + studies/theory/lib/check.py on main. A round scores each proposed…"],
        [358, 2, "idea-607778", "RL gain as context: does a context window carry what the RL weight difference carries? Base + cue, MATH-500, T 1.0/top-…"],
        [359, 1, "work-be7af1", "RL gain as context idea-607778: base + cue on MATH-500, T 1.0/top-p 1.0, v3, with 3 solved MATH-500 problems in front o…"],
        [363, 1, "work-6d6308", "Theory round 01 (theory skill): theories proposed from board items before the cutoff, scored on the held-out newest qua…"],
        [363, 2, "idea-46b68c", "Reward content test: does the MATH-500 gain need a math reward, a reasoning reward, or only RL from the base? AI2 relea…"],
        [370, 2, "idea-0b2ad8", "Theory round 01: forward predictions, posted before the runs. Status of every theory below: candidate. None beat the no…"],
        [370, 0, "result-5f7f23", "theory round 01: 0 of 6 theories beat the null on 58 held-out targets (noise 3); planted theory +22 -14 and +23 -21, th…"],
        [371, 1, "work-069eca", "Reward content test idea-46b68c step 1: Olmo-3-7B-RL-Zero-IF, -General, -Mix (+3.0 Math, Code as same-version controls)…"],
        [380, 0, "result-b74234", "gpuprice SPEC2, candidate fixed before the run (average of Chronos-2 per listing with 3 listing rules and the own-histo…"],
        [382, 0, "result-a801dd", "gpuprice research + hill-climb done, branch gpuprice. Submission written: studies/gpuprice/results/submission/forecast_…"],
        [390, 0, "result-b9210d", "gpuprice LLM arm, negative: 80B open-weights LLM (Qwen3-Next-80B 4-bit, H100, 24 GPU-min) reading the provider listing…"],
        [403, 0, "result-5d032f", "Day-1 #3, MATH-500 n=500, T 1.0 / top-p 1.0, grader v3: a 4-sample vote adds 8.2 points to base+cue (405 -> 446, [5.8,…"],
        [403, 2, "knowledge-a41bb0", "Runner: a job dies with FileExistsError on /runs/<job-id> when its function starts a second time; infra/runner.py does…"],
        [403, 1, "work-b95a73", "Theory round 02 (theory skill v2, SPEC studies/theory/specs/SPEC_round02.md): score each theory on its own interval cla…"],
        [409, 1, "work-3095f1", "Label-free selector over the 4 stored samples idea-664670, offline, no GPU: tie-breaks, length-weighted votes, drop cap…"],
        [409, 1, "work-5c7b22", "Board page redesign from the three design reviews (tools/view.py, architecture.py :root/HUES only): honest hill charts…"],
        [410, 1, "work-aa5f97", "Record steps of the hill chart: new tools/climb.py (branch climb) lists, per benchmark, each result that raised the bes…"],
        [413, 0, "result-e5bed4", "uv run tools/climb.py [benchmark] [--json] is on main (0a24b4e): per benchmark, every result that raised the best base…"],
        [415, 0, "result-cbe0bc", "Label-free selector, MATH-500 n=500, 4 stored samples, v3: breaking vote ties by the shortest finished sample gives bas…"],
        [419, 1, "work-6b1fa5", "Literature sweep for the base-vs-RL gap: latest Goodfire interpretability research, Weight-Space Programming follow-up…"],
        [423, 0, "result-e45bf4", "328 harder, T 1.0, cue, v3 (work-43d4a1): weight differences raise the cued base 5.5-7.9 pts but all stay under RL plai…"],
        [424, 0, "result-6277ee", "328 harder, T 1.0, cue, v3, one sample, recounted from raw rows by a second model: theta(0.25) 182, theta(0.5) 190, Cod…"],
        [425, 2, "knowledge-f2629c", "Literature sweep 2026-11-15 (work-6b1fa5): 11 pieces read in full by subagents, 45 findings sent to past.dev (tools/pap…"],
        [431, 1, "work-3946b0", "Choose the next interpretability study: 4 proposer subagents (weight-space, activations/neurons, cross-checkpoint trans…"],
        [433, 0, "result-70e7a8", "theory round 02 (same held-out items as round 01, new score): 5 of 16 theories pass on 61 held-out targets, each on 2 t…"],
        [435, 1, "work-9763ed", "Vote distillation (no reward, no labels): LoRA-finetune the base on its own cue samples from MATH-500 that finish and a…"],
        [436, 1, "work-855406", "Audit of the climb-chart wins (result-c36598, e870a1, 4b0d5f, 5d032f, cbe0bc, 82b4dc): recompute each score from raw ro…"],
        [437, 0, "result-edceef", "Reward content test step 1 (work-069eca, idea-46b68c): in the Olmo 3 RL-Zero models the MATH-500 gain follows the math…"],
        [438, 2, "idea-ac4e14", "PICK for the next interpretability study (work-3946b0: 4 proposers, 12 proposals, inventory of our own studies, 2 skept…"],
        [438, 0, "result-e78dfe", "Audit of the MATH-500 climb chart: no answer-key leak in prompt, cue, restart, vote or tie-break (code read; grader v3…"],
        [447, 1, "work-0b9116", "Theory round 03 (SPEC studies/theory/specs/SPEC_round03.md): version 3 of the theory skill on held-out results posted s…"],
        [447, 1, "work-906b75", "Regrade our T 1.0 base+cue MATH-500 answers (job abaybektursun-1114-153825-208b) with the extraction rule of Wang 2610.…"],
        [449, 0, "result-60d899", "Our lead over Wang 2610.06851 on MATH-500 is a grader effect. Base+cue T 1.0, job abaybektursun-1114-153825-208b, right…"],
        [450, 2, "knowledge-80bbb1", "Subagents started inside the repository see result numbers that the prompt never gave them: Claude Code puts the 5 newe…"],
        [451, 2, "idea-0d55a4", "RL-Zero without the reward (plan, not started; riskier follow-up to idea-607778). Thesis: one RL sample is the base's o…"],
        [453, 2, "idea-eec971", "Policy improvement at decoding time, no weights and no reward (plan, not started; riskier follow-up to idea-46b68c). Th…"],
        [453, 0, "result-7ce335", "Board page redesign live on https://monitor.invariant.team (main 71ccafb, 056400f). 3 design reviews -> 14-item brief -…"],
        [454, 0, "result-eb9211", "Step 2 (token agreement), 500 stored base answers, 1,904,493 positions, Pearson r of each model's per-token log-prob ch…"],
        [458, 0, "result-6d422d", "Three answers written by Math-RL, placed in the base model's context, give +5.6 pts on MATH-500 with no weight change;…"],
        [458, 0, "result-40c0a5", "The record-steps list is live on https://monitor.invariant.team (main 3886f07): under each hill chart, one row per resu…"],
        [459, 1, "work-4fa42e", "Run idea-ac4e14 step 1: top-8 singular-subspace overlap between RL deltas of different rewards (Math 3.0/3.1, Code 3.0/…"],
        [462, 2, "idea-9e3dff", "Gap anatomy from stored samples (no GPU): with 4 samples per problem per model (Day-1 #3, MATH-500, T 1.0, v3), is the…"],
        [462, 1, "work-5b7270", "Gap anatomy idea-9e3dff: reliability shift vs new problems in the RL gain on MATH-500, from the stored 4 samples per pr…"],
        [463, 2, "idea-1c8b73", "One axis or several? (no GPU): do the partial routes toward the RL model (cue, weight blend theta, Code-RL and other-re…"],
        [463, 2, "idea-17d5b7", "Prefix hand-off at T 1.0: where inside an answer does RL's advantage enter? Stored attempt-0 answers of base+cue and RL…"],
        [463, 1, "work-b68a26", "Prefix hand-off at T 1.0 idea-17d5b7: writer {base, RL} x finisher {base, RL} x cut {25,50,75 %} on ~120 MATH-500 probl…"],
        [463, 1, "work-1aa34c", "One axis or several: item-level structure of all arms' per-problem 0/1 vectors (MATH-500, hard328), overlap vs resample…"],
        [470, 1, "work-1a972a", "hard328 with the configuration chosen on MATH-500 (vote over 4 after restart): run_cell --samples 4 --restarts 2 on bas…"],
        [471, 0, "result-0018d3", "Second read of grader v3 (idea-884e91, the DIRECTION open item): every v1/v3 disagreement in the 4,178 Day-1 #3 rows (M…"],
        [473, 0, "result-afc423", "RL's gain on MATH-500 is mostly a reliability shift: 81% of the 198-sample gap (4 samples per problem, n=500, T 1.0, v3…"],
        [475, 2, "knowledge-13cff3", "Temperature hybrid, simulated from stored rows (MATH-500, base+cue, v3, no GPU): sample at T 0.6/top-p 1.0 (job -151718…"],
        [475, 2, "idea-ae6eba", "Answer-statement repair: how many of the ~10 MATH-500 points between cued base (405-418/500) and RL (456-464) at T 1.0…"],
        [475, 1, "work-655434", "Answer-statement repair on MATH-500 T 1.0 (base cue vs RL, 2,000 stored samples each): gold-aware upper bound, label-fr…"],
        [477, 1, "work-25e631", "gpuprice hill-climb round 3 (branch gpuprice): (a) API LLM as adjuster of the ens-05 quantiles, no tools, context dated…"],
        [478, 0, "result-9d979a", "xreward Part 1 (weights only, 224 layer matrices, top-8 singular subspaces of model minus base; job abaybektursun-1114-…"],
        [486, 0, "result-8de03b", "theory round 03 (first run with blind agents headless and held-out items no round had used): no theory survives. 14 the…"],
        [487, 1, "work-3d6913", "Theory engine v4 and round 04: computed tests on stored rows become the main test (every theory's own offline predictio…"],
        [487, 0, "result-0c8739", "gpuprice fm2-19: +0.305 pooled skill vs last value on 30 dev origins (3,109 cells), up from +0.291 (fm2-17), by using t…"],
        [489, 0, "result-c57b51", "Stating the answer explains about 0.5 of the 9.9 points between cued base and RL on MATH-500 (T 1.0, mean of 4 samples,…"],
        [491, 1, "work-27bcd1", "Monitor page performance: data-oriented /data (ETag/304, shared snapshot cache, slim rows, no polling in hidden tabs),…"],
        [495, 0, "result-5da8a9", "One axis: on MATH-500 the 618 pairs of different arms have a mean excess union of -0.05 problems over the difficulty-ma…"],
        [501, 1, "work-eb10d7", "In-context improvement loop, no RL text and no reward (follows result-6d422d): generation 0 = cued base, 4 samples on t…"],
        [502, 0, "result-79f914", "gpuprice candidate 2: +0.283 pooled skill on the 6 locked origins (357 cells, declared second look, SPEC3) vs +0.252 ca…"],
        [505, 2, "idea-31636e", "Exchange-rate table: since all 36 MATH-500 arms lie on one Rasch axis (result-5da8a9), express every method (cue vote k…"],
        [505, 1, "work-c45b70", "Exchange-rate table idea-31636e (branch rate, laptop only): logit ability shift of every MATH-500 arm vs base+cue sampl…"],
        [505, 2, "idea-60d3e1", "Does RL check more, or err less per step? From the stored 4-sample texts of the cued base and RL on MATH-500 (T 1.0, v3…"],
        [505, 1, "work-768257", "Checks or per-step error idea-60d3e1: checking markers per 1k tokens in the stored MATH-500 4-sample texts, base+cue vs…"],
        [512, 1, "work-5d5dc3", "Critic at decoding time idea-eec971, stages 0-1: (0) offline on stored MATH-500 4-sample rows: accuracy and tokens of s…"],
        [513, 2, "idea-069f19", "Where does low temperature help and where does it loop? (for hard328; config chosen on MATH-500). Facts: cued base at T…"],
        [513, 1, "work-deec92", "Entropy-gated temperature idea-069f19: vLLM logits processor (logits/T_low only where next-token entropy is above the 8…"],
        [515, 0, "result-855858", "RL does not win by checking more: it writes more checking markers (13.1 vs 9.5 per 1k tokens, paired +3.6 [3.4, 3.9], n…"],
        [516, 0, "result-f45f9d", "gpuprice local-GPU arms: best single model +0.318 pooled skill on 30 dev origins (loc-09: half zero-shot Chronos-2, hal…"],
        [521, 0, "result-17e25e", "Exchange-rate table: a MATH-500 logit shift predicts the hard328 score no better than 'same point gain': leave-one-arm-…"],
        [522, 1, "work-72c687", "Finding page /finding/rl_reliability: RL gain is reliability (result-afc423, result-855858)"],
        [522, 2, "idea-7928c0", "Slip-hazard law for the RL gain: an answer is a chain of steps each with a small chance of an unrecovered slip, P(right…"],
        [523, 1, "work-26c268", "Slip-hazard law idea-7928c0: cloglog item model vs Rasch logit on the 36 x 500 MATH-500 matrix (held-out, logit-simulat…"],
        [524, 2, "idea-24bba3", "More H100 capacity for abaybektursun's jobs. Baseline 2026-11-15 04:55 UTC: 10 of 10 H100 running for 45-62 min each, 6…"],
        [525, 0, "result-bb7bba", "gpuprice OpenAI arms (dev only, not submitted): gpt-6-astra as adjuster reproduces Fable's gain (+0.313 vs +0.298, 3,10…"],
        [525, 0, "result-b624bb", "gpuprice round 3: candidate 2 submitted, +0.283 pooled skill on 6 locked origins (357 cells) vs +0.252 candidate 1 and…"],
        [530, 0, "result-429436", "tools/finding_rl_reliability.py at /finding/rl-reliability, commit 8f89f38 (main 58f2673): 5x5 k-of-4 table as columns,…"],
        [534, 0, "result-59ed1a", "Code pair (taken over after 10 min without answer; cells run by the codepair agent): on HumanEval+ and MBPP+ (538 probl…"],
        [537, 0, "result-5b322f", "Monitor page performance, live (main 40cc8e1), measured with infra/monitor/bench.py before/after: /data unchanged -> 30…"],
        [543, 0, "result-5227b9", "Examples in context do not move the cued base toward RL: the +5.6 pts of result-6d422d was one draw of 3 texts. MATH-50…"],
        [547, 1, "work-3d68e2", "Closing cue on hard328 (reward-free, fewer tokens): cut each stored cued-base answer (T 1.0) at N tokens and append a c…"],
        [556, 0, "result-b30f15", "Negative: the cued base's activations do not tell which of its own samples of a problem will fail. MATH-500, 2,000 stor…"],
        [556, 0, "result-e41d94", "Slip-hazard law refuted: the hazard (cloglog) item model fits held-out cells worse than Rasch logit, -0.2854 vs -0.2790…"],
        [557, 1, "work-40ec05", "Do the RL models make the base's own wrong steps less likely? For the 60 judged finished-wrong base samples (results/an…"],
        [559, 0, "result-51fd20", "Negative: forcing the cued base to commit when an answer runs long loses problems; its cap hits on the 328 are failures…"],
        [562, 1, "work-d9a824", "Signed self-training, no reward (idea-0d55a4 stages 1-2, the missing cell of the 2x2 {vote, key} x {SFT, signed}): LoRA…"],
        [563, 2, "idea-095c0d", "Do SFT and RL have opposite difficulty profiles? RL removes 89 % of the cued base's errors on easy MATH-500 problems an…"],
        [563, 1, "work-d13a7f", "Difficulty profile of SFT vs RL idea-095c0d: error reduction by difficulty bin (leave-out difficulty, MATH level) for R…"],
        [564, 2, "idea-c1d00f", "Is the RL gain practice on its training prompts? 72 of the 400 harder problems are in the Dolci RL-Zero-Math prompts (4…"],
        [564, 2, "idea-aa7280", "Token frontier: accuracy vs generated tokens per problem for base+cue and RL under reward-free test-time rules (single,…"],
        [564, 1, "work-fec451", "Seen vs unseen: score the 72 harder problems that are in the RL training prompts (4 samples, T 1.0, v3) on base+cue, RL…"],
        [564, 1, "work-86ad1e", "Token frontier idea-aa7280: offline frontier of right vs generated tokens per problem on MATH-500 (stored 4-sample rows…"],
        [569, 0, "result-faf15a", "Math-RL is about half as likely as the base to write the base's own located wrong step, and the base's wrong step is no…"],
        [570, 1, "work-d10ae6", "Screen decoding rules on the base's located wrong steps (no weights, no reward): for the 51 judged wrong steps of the c…"],
        [573, 0, "result-40ed3b", "No reward-free base rule reaches one RL sample on MATH-500 (n=500, T 1.0, v3, 24 rules fixed before scoring, stored 4-s…"],
        [579, 1, "work-95ff34", "Shared tool fixes from meta/FAILURES.md + bug reports: runner skips/kills cancelled jobs (ce39 killed 7 jobs), runner e…"],
        [579, 0, "result-bf6124", "Think-SFT and RL have different difficulty profiles, and the blind prediction from that held on hard328: Think-SFT cue…"],
        [581, 0, "result-296647", "Vote self-distillation does not transfer: base LoRA-tuned on its own vote-selected MATH-500 cue samples (455, no gold)…"],
        [583, 2, "idea-1d9f26", "Think-SFT (no reward) with cue under the vote rules chosen on MATH-500: 4 samples on hard328 and MATH-500, T 1.0, v3, s…"],
        [583, 1, "work-0a00c2", "Think-SFT cue, 4 samples (one H100 job per sample, no restarts) on hard328 (seed 3000000) and MATH-500 (seed 181000000)…"],
        [584, 0, "result-e07fb4", "Closed: vote self-distillation does not transfer to hard328 (V cue 167 vs base cue 164, +0.9 [-3.0, 5.2]; V-U cue -0.3)…"],
        [586, 1, "work-0cc8e5", "Second-model read of all 113+1 grader v1->v3 flips of the first table (9 cells, raw answers from S3), idea-884e91, DIRE…"],
        [588, 0, "result-284db5", "xreward Part 2, first four cells (hard328 n=328, cue, T 1.0/top-p 1.0, v3, one sample, seed 3000000; edits at 0.074 % o…"],
        [598, 0, "result-7b35e8", "Shared tool fixes on main (bdd6cd9, 6817e97), each tested on Modal cpu jobs: a job cancelled while queued never runs; k…"],
        [606, 0, "result-dba8ee", "All 114 grader v1->v3 flips of the first table read by a second model (Fable 5.2): 112 of 113 wrong-to-right are right;…"],
        [610, 0, "result-32b7a8", "Olmo-3.1 RL-Zero-Math cap hits at T 0.6 / top-p 0.95 rise early in RL, then fall, and the rise follows the opening, not…"],
        [610, 2, "knowledge-90431f", "Theory round 04 refuted 4 theories by their own computed tests (studies/theory/results/engine/round-04/metrics_v4.json)…"],
        [611, 2, "knowledge-aa06fe", "r4-m08 (theory round 04) lost to its rival: -2.65 nats over two rival turns, 5 tests, every one at or past the rival. T…"],
        [611, 2, "idea-1b0d2e", "r4-m01 (round 04, review: weak) is not separated from its rival: +1.11 nats over two turns (+4.43, then -3.32). The cue…"],
        [611, 0, "result-e9afe5", "theory round 04: 3 of 10 theories survive; 29 of 42 offline predictions computed, 18 inside, 11 outside; 4 refuted. stu…"],
        [611, 1, "work-502f19", "Theory engine v5.2 (lib/round.py, SKILL.md): a rival that beats its theory is carried as the theory and meets a fresh r…"],
        [611, 2, "idea-035a30", "From theory round 04: RL-Zero-Math's first 100 steps install the opening the cue forces in the base, and T 0.6 / top-p…"],
        [624, 0, "result-a6ab7a", "Prefix hand-off, T 1.0, MATH-500 pool of 183 (base right in <= 3 of 4): RL's advantage is in the first half of the answ…"],
        [650, 0, "result-a7c052", "xreward trace (forward pass, base model on its own 328 hard328 answers, 1,572,055 positions, job abaybektursun-1115-005…"],
        [671, 2, "idea-968e5b", "Think writes, RL finishes: a two-model text relay on hard328. Think-SFT (no reward, cue) has the better plans on hard p…"],
        [672, 1, "work-1c43cf", "Relay on hard328 (n 328, T 1.0, v3): Think-SFT cue writes, RL-Zero-Math finishes, and the 3 other writer x finisher pai…"],
        [672, 1, "work-09d814", "Tinker pair (second model pair, our own RL): Qwen3.5-9B-Base on Tinker, MATH-500 T 1.0/top-p 1.0 grader v3. (1) plain v…"],
        [679, 0, "result-f39ba8", "Budget of the cued-base-to-RL gap in four cells: loops replace reliability at T 0.6"],
        [710, 1, "work-3d1e3b", "Delta transplant on hard328: Think-SFT + a (RL-Math - base), a 0.5/1/2, cue, T 1.0, v3, 1 sample each + MATH-500 at a=1…"],
        [719, 2, "idea-019309", "Rows of joined four-sample cells into git. Baseline: 0 of 3 hard328 four-sample folders hold rows.jsonl (checked 03:15,…"],
        [719, 2, "idea-06a103", "Fewer GPUs per question in multi-model cells. Baseline (meta entry 03:53 UTC): 10 H100 cells of one question waited a m…"],
        [723, 0, "result-854ca8", "Signed self-training with no reward loses points"],
        [727, 1, "work-ceccc0", "Token cap 32,768 on hard328 for Think-SFT cue, RL plain and base cue (one sample, T 1.0, v3, seed 3000000): Think-SFT c…"],
        [727, 0, "result-34897a", "Entropy-gated temperature does not beat plain T 1.0"],
        [743, 1, "work-644fec", "Visuals lead for the findings pages (/findings, tools/finding_<slug>.py): audit which posted results worth telling have…"],
        [765, 2, "knowledge-861d66", "Literature for 'RL first installs the cue's opening' and for label-free RL, read 2026-11-15 (findings in tools/paper.py…"],
        [767, 2, "knowledge-4662c6", "Grader v3 scores an 'Answer:' line wrong when an algebraic answer ends with a period ('15x - 80.' against gold '15x - 8…"],
        [775, 0, "result-51a0e7", "RL's top directions make the model finish, not be right"],
        [777, 1, "work-e02ba4", "Finish dial: Math 3.1's 8 directions added to the base at sizes -1, 0.5, 1.5, 3 with a random edit at matched sizes, an…"],
        [777, 2, "idea-f1bae8", "No prefilled cue: pick the base's own draws that open with Okay"],
        [777, 1, "work-c82156", "Run idea-f1bae8: MATH-500, untrained base, plain prompt, no prefilled tokens; rejection-sample the base's own opening (…"],
        [780, 0, "result-5c961a", "Harder 328: the vote narrows the gap to RL, not closes it"],
        [781, 0, "result-066c9b", "The RL gain is not practice on its training prompts: D = (RL - Code-RL) seen minus unseen = +2.9 points, 95 % interval…"],
        [783, 0, "result-1b6bf2", "RL's directions lengthen short answers and cut the tail"],
        [788, 2, "knowledge-dab63f", "On the 328 the base-to-RL gap is not a selection problem. Vote over 4: RL right and base wrong on 36 problems; the base…"],
        [788, 1, "work-480b1f", "RL steps 100 and 400 at AI2's setting (T 1.0 / top-p 1.0, MATH-500, v3, 1 sample), plain and cue: the cue's gain at eac…"],
        [789, 1, "work-0d465a", "Offline, no GPU: mixed-model vote on hard328 from stored rows (2 RL + 2 Think-SFT samples against 4 RL, 4 Think-SFT, 4…"],
        [793, 0, "result-a497ff", "Lowering the base's wrong steps adds no right answers"],
        [793, 0, "result-0033d7", "Mixing RL and Think-SFT samples in one vote does not help"],
        [794, 0, "result-818c20", "Think-SFT + cue (no reward, trained on traces) beats RL under the vote on the 328: vote over 4 = 241/328 at 40,410 tok…"],
        [794, 1, "work-173c5c", "Laptop, no GPU: finish the Think-SFT training-overlap scan for hard328 and MATH-500 (result-f6a8bc left open: 33 of 156…"],
        [795, 0, "result-c495fe", "A slip is chance; a misreading starts before its sentence"],
        [804, 2, "idea-690b8e", "tools/cycle.py lists vast.ai jobs only when run from the main checkout: it globs '<own folder>-*', so from a worktree i…"],
        [806, 1, "work-2cd5d0", "Problem dependence as a label-free early sign of a wrong sample: log p(token | problem) - log p(token | no problem) of…"],
        [825, 1, "work-ab6833", "run_cell --shard k/N (problems k, k+N, ... of the set; seeds unchanged) and analysis/shard_join.py that joins the N run…"],
        [828, 0, "result-f3d708", "How much the early text depends on the problem tells nothing"],
        [828, 2, "knowledge-16c62a", "Closed routes for 'catch or avoid a wrong base sample while it is being written, no label, no second model' (cued base,…"],
        [835, 0, "result-bce075", "Handing a Think-SFT answer to RL to finish gains nothing"],
        [841, 2, "idea-67db73", "Fresh held-out set: does Think-SFT + cue's lead over RL-Zero-Math under the 4-sample vote (hard328: 241 vs 221) hold on…"],
        [841, 1, "work-7c069c", "Fresh held-out set (problems dated after the training data of Think-SFT, RL-Zero-Math, base): cutoffs from primary sour…"],
        [841, 2, "idea-ce2272", "Risk-coverage on stored rows (laptop): where does Think-SFT's lead over RL on hard328 sit? Order the 4 samples per prob…"],
        [841, 1, "work-4ecc65", "Risk-coverage of Think-SFT cue vs RL plain vs base cue on stored rows (hard328, MATH-500; laptop, no GPU): precision at…"],
        [855, 0, "result-b006f5", "Think-SFT's lead over RL on hard328 is in long answers only. Keeping each model's shortest answers, precision is equal…"],
        [857, 0, "result-77ca14", "One cell can now run as N jobs at once"],
        [858, 2, "idea-6f4b9e", "Derived or asserted: does RL's final answer follow from its own text? Blind hosted judge labels long (>8k tokens) finis…"],
        [858, 1, "work-dd4773", "Derived or asserted (idea-6f4b9e): blind hosted judge labels long (>8k tokens) finished answers of RL plain, Think-SFT…"],
        [860, 0, "result-d484cb", "Think-SFT's lead on the 328 survives a full data scan"],
        [867, 0, "result-3a3af3", "The base reaches the cue's score with no cue prefilled"],
        [867, 0, "result-49a816", "Untrained base, plain prompt, self-opened draw on MATH-500: 411/500 (cue 410, plain 224, control 216), result-3a3af3. R…"],
        [873, 0, "result-02da9f", "Unsolved long answers guess: the base as often as RL"],
        [876, 1, "work-55ae25", "Risk-coverage on hard328 stratified by difficulty: is Think-SFT's lead over RL in long answers or on hard problems? Tes…"],
        [880, 0, "result-527fbb", "Think-SFT's lead: long answers to hard problems"],
        [883, 2, "idea-44d6e1", "One table of every full-set configuration on hard328, rebuilt offline from committed per-problem rows: right/wrong/abst…"],
        [883, 1, "work-44d747", "One table of all hard328 configurations from committed per-problem rows (share of base-to-RL gap closed, intervals, tok…"],
        [893, 0, "result-389164", "One table of every configuration on the 328 harder problems"],
        [897, 1, "work-1d752c", "Per-sample rates for derived-or-asserted (review of result-02da9f, idea-6f4b9e): outcome of each of 1,312 samples per m…"],
        [898, 0, "result-fc7efc", "Per attempt, RL guesses more often than the base"],
        [932, 1, "work-8fd317", "Theory round 07 on engine 7.1 (no account; half the mechanisms must imply a change to the base alone; duel win needs 2…"],
        [941, 0, "result-6f1bb7", "A 0.11% weight edit takes the base to RL's score"],
        [942, 1, "work-ab0f72", "Replicate the 1.5x edit (base + 8 directions of RL-Math at 1.5x, result-6f1bb7): hard328 with 4 samples (single-sample…"],
        [962, 0, "result-3387ce", "Twice the RL weight change on Think-SFT: 231.5 of 328"],
        [963, 1, "work-8b4030", "Transplant a=2 off the set it was chosen on: Think-SFT + 2 x (RL-Math - base) on fresh2026 (136 problems, 4 samples, se…"],
        [1110, 0, "result-c8b994", "Twice the token cap gives Think-SFT 23 more problems"],
        [1110, 1, "work-60f040", "Vote over k = 1..12 samples of the untrained cued base on MATH-500 (8 new samples, T 1.0, v3, same cell as the stored 4…"],
        [1115, 0, "result-5251c9", "Think-SFT's lead over RL holds on 2026 problems"],
        [1117, 0, "result-564441", "Forecasts of 20 open GPU numbers, written before they land"],
        [1117, 2, "idea-01fe11", "Think-SFT + cue vote over 4 at token cap 32,768 on hard328 and fresh2026. At 16,384 it votes 241/328 and 75/136 but cap…"],
        [1117, 1, "work-dc9359", "Think-SFT + cue vote over 4 at token cap 32,768 on hard328 (samples 1-3 new, sample 0 = the cap32 run) and fresh2026 (4…"],
        [1119, 1, "work-abe449", "Tier list of the genuinely novel findings of the whole project (all 7 studies, board, theory rounds, meta): one workflo…"],
        [1126, 0, "result-95a4dc", "The 1.5x RL-direction edit matches RL on new samples"],
        [1128, 1, "work-16773f", "1.5x top-8 edit (base + 1.5 x top 8 directions of RL-Math - base, cue) on fresh2026, n 136, 4 samples, seeds of SPEC_fr…"],
        [1128, 1, "work-e1b23a", "Two controls for the finish dial (result-6f1bb7): random rank-8 edit at 1.5x, and Think-SFT's 8 directions scaled to Ma…"],
        [1133, 0, "result-05cf4d", "A theory's forecast of the 1.5x edit landed: 455 against 456"],
        [1142, 1, "work-5fd7c1", "gpuprice: public results page at gpu.invariant.team (static, S3 + CloudFront, stack gpuprice-site, profile fuelos); sou…"],
        [1149, 0, "result-8c92fc", "Tier list of novel findings: the finish dial is first"],
        [1149, 1, "work-bef559", "Site lab: 12 parallel 3D / interactive prototypes of new visualizations of the agents and the team's work, all on real…"],
        [1154, 0, "result-f688a7", "gpuprice results page is public at gpu.invariant.team"],
        [1155, 1, "work-0a1b10", "Short paper on the finish dial (result-6f1bb7, result-95a4dc; with the transplant and fresh2026 as supporting sections)…"],
        [1155, 1, "work-88e8d5", "Theory round 08 on engine 8: mechanisms are written with the open GPU targets, every theory forecasts them before its s…"],
        [1163, 2, "idea-e37da1", "Drift: what is a cut-off Think-SFT answer doing? Label-free signs in its text (switch to Chinese or another non-Latin s…"],
        [1164, 1, "work-76a232", "Drift: label-free signs in Think-SFT's cut-off answers (script switch to Chinese, repetition, restart phrases, length)…"],
        [1164, 0, "result-fad48d", "The cue equals the first 100 RL steps at AI2's setting"],
        [1174, 1, "work-3c3e3d", "Joke mini app on the site: /psychosis, a meditation and therapy session for AI psychosis (the team poking fun at itself…"],
        [1182, 0, "result-2fe32f", "Paper on the finish dial is on the site"],
        [1189, 0, "result-6fc6f3", "A joke therapy page for the team's own results is live"],
        [1189, 1, "work-746eaa", "Exa showcase page on the site at /exa (tools/exa_page.py, one route in view.py): the count of Exa calls from the transc…"],
        [1189, 1, "work-1a2d68", "Site page /pastdev: one page on how the team used past.dev as shared memory (real recalls from transcripts, usage numbe…"],
        [1192, 0, "result-4a38d4", "Exa showcase page is live at monitor.invariant.team/exa"],
        [1192, 0, "result-1adad9", "past.dev showcase page is live at /pastdev"],
        [1193, 0, "result-39497c", "Dial controls hold: random and Think-SFT edits do nothing"],
        [1194, 1, "work-df5e0a", "Second model pair for the finish dial: base + Code 3.1's 8 directions at 1x, 1.5x, 2x, random at 1.5x, and Math 3.1's a…"],
        [1196, 0, "result-0c1eef", "More tokens finish the base's answers, not fix them"],
        [1198, 1, "work-8b2ec9", "Think-SFT in its own chat format (ChatML template with <think>, never run here: every Think-SFT row uses the raw templa…"],
        [1200, 1, "work-184476", "Paper loop: tier list of the project's novel findings (parallel subagents, several views), then one short paper per loo…"],
        [1202, 1, "work-31a75c", "New home page at / (tools/home.py): one lit glass dial that turns to each destination and lists every page of the site…"],
        [1202, 0, "result-f587b2", "Twelve 3D pictures of the team's work are live at /lab/"],
        [1206, 0, "result-997be4", "No text sign predicts a failing Think-SFT sample early"],
        [1207, 1, "work-f8ecb6", "ckptcue3: 3 more samples of step-100 plain, step-100 cue, step-400 plain (MATH-500, T 1.0, v3) so the step-100 vs cued-…"],
        [1216, 0, "result-327ee5", "The site has a home page that leads to every page"],
        [1220, 2, "idea-7ca1fe", "Experiment that would make the top-8 switch theory (r5-m03-rival) new against 2510.10977 and 2504.07912: base + 1x top-…"],
        [1221, 1, "work-22359d", "top8x4: base + 1x top-8 RL-Math directions, plain, MATH-500, T 1.0, 3 new samples (4 with the stored one); readout of s…"],
        [1234, 0, "result-a1bf75", "The finish dial holds on a second model pair: code"],
        [1235, 0, "result-f5b7a3", "Theories forecast the code dial better than plain readers"],
        [1236, 0, "result-526568", "Paper 2 is on the site: Theories on Trial"],
        [1237, 2, "knowledge-df956c", "Not run: 'extrapolate the first 100 RL steps' (scale step-100's directions to reach final RL). Two reasons. (1) It is p…"],
        [1238, 1, "work-d80b27", "Smallest edit that reaches RL: one direction per matrix of RL-Math at 2x and 3x, and the 8 directions at 1.5x in layers…"],
        [1265, 2, "knowledge-a5a675", "Theory round 08 refuted 2 theories on stored rows. r8-m02 (cued base loses answers by switching lines of attack; RL swi…"],
        [1265, 0, "result-d69c51", "Theory round 08: new theories forecast what readers do"],
        [1265, 2, "idea-e9dfd5", "Three GPU cells designed by the theories to separate them (forecasts fixed in studies/theory/results/forecast/cells-01/…"],
        [1266, 1, "work-a68dfd", "Cell m20: untrained Olmo 3 base, plain prompt (no cue), fresh2026, 136 problems, 1 sample, T 1.0, v3, cap 16,384; forec…"],
        [1266, 1, "work-844e38", "Cell m06: RL-Zero-Math step 100, plain, first 164 of hard328, 1 sample, T 1.0 / top-p 1.0, cap 16,384, v3; forecasts 26…"],
        [1267, 1, "work-290625", "Cell m29: base + top-8 RL-Math directions at 2x, cue, MATH-500 n 500, T 1.0, v3 (the 1.5x dial run's command with scale…"],
        [1290, 1, "work-0a9281", "Theory round 09 on engine 9 (wide path): six families propose mechanisms, all forecast the open targets and design GPU…"],
        [1300, 0, "result-6832a8", "Four samples: 100 RL steps within 3.3 points of the cue"],
        [1301, 0, "result-d02d46", "Short top-8 answers are right on easy problems"],
        [1306, 0, "result-306787", "Finishing and right answers split by rank and by depth"],
        [1306, 1, "work-b5f51c", "Test the depth split on the Code pair (it was read after the run on math): Code 3.1's 8 directions at 1.5x in layers 0-…"],
        [1309, 0, "result-a74ac3", "Base without the cue: 10 of 136 fresh 2026 problems"],
        [1318, 0, "result-53ce14", "Paper 3 is on the site: The First Hundred Steps"],
        [1325, 2, "knowledge-b93bd6", "Published: 'probes read the problem, not the attempt'. Bulut, arXiv 2609.03436 (R1-Distill-Qwen-7B, MATH, 256 samples p…"],
        [1327, 1, "work-3baa2c", "Depth split on math, more samples (result-306787): base + Math 3.1 top-8 at 1.5x in L0-10 (+3 samples), L11-21, L22-31…"],
        [1332, 1, "work-739554", "Round-09 cells m11 and m13 (cells.md): m11 base - 1.0 x top-8 RL-Math directions, cue, MATH-500 n 500, readout cap hits…"],
        [1332, 1, "work-ef61c7", "Round-09 cells m21 and m18: (m21) base + 1.0x top-8 dirs of (RL-Code 3.1 - base), plain, MATH-500 first 250; (m18) base…"],
        [1335, 0, "result-04e329", "The 1.5x RL-direction edit holds on unseen 2026 problems"],
        [1338, 0, "result-c569d3", "Theory round 09: 10 carried, 7 to the graveyard, 39 cells"],
        [1339, 2, "knowledge-f51b8d", "Theory graveyard after round 09 (engine 9 standing: total forecast gain at or below -2 nats on 3 or more scored numbers…"],
        [1340, 0, "result-51ccc6", "The depth split of the dial does not hold on code"],
        [1342, 0, "result-9ce8ed", "RL step 100: 7 of 164 quick wrong answers on hard328"],
        [1344, 1, "work-8ea654", "Think-SFT (no reward) on the Code pair: HumanEval+ and MBPP+ (538), Code cue and Math cue, T 1.0, 1 sample, seed 510000…"],
        [1345, 0, "result-fbe153", "Home is invariant.team; the monitor's root is the board"],
        [1345, 1, "work-30f0ed", "Low-rank RL directions on other hosts: (1) Think-SFT + RL-Math's 8 directions at 1.5x, 3x, random 3x on hard328 (vs ful…"],
        [1346, 1, "work-ac9372", "xshift: activation-level readout of the edit cells. One job teacher-forces 48 stored base answers through the base and…"],
        [1363, 1, "work-744158", "Theory round 10 on engine 10: carry needs gain on 3 distinct results; separation needs 2 families per side; new track r…"],
        [1374, 1, "work-acad69", "UX/UI review of the whole site's structure (invariant.team, monitor.invariant.team and every page type): four reviewer…"],
        [1383, 1, "work-db4b01", "Level up the joke game at /psychosis (tools/psychosis.py): 5 levels with bosses, collision physics, letter particles, W…"],
        [1384, 0, "result-0c5fa5", "Paper 4 is on the site: No Early Warning"],
        [1385, 1, "work-f670f3", "Values page /values (tools/values.py): the team's six values with their quotes, one lit 3D SVG object in the site's des…"],
        [1393, 0, "result-98de28", "RL's directions move activations 95x more than random ones"],
        [1395, 0, "result-6f7ca3", "Math depth and rank split holds: 7 of 7 predictions"],
        [1396, 0, "result-d3a14c", "The paper loop has its own page, /papers"],
        [1397, 0, "result-ba6e70", "Site review: two tiers that do not connect"],
        [1399, 0, "result-c6b721", "Values page is live"],
        [1403, 0, "result-100d3d", "The joke meditation game has 5 levels and bosses"],
        [1405, 1, "work-ac51ca", "Site review fixes (work-acad69), all in tools/view.py send plus small edits: name links to invariant.team and a More li…"],
        [1408, 1, "work-ec17e2", "Second level-up of the joke game /psychosis (tools/psychosis.py): post-processing shader (bloom, ripples, chromatic spl…"],
        [1408, 0, "result-f2e433", "Site review fixes are live: one way home from every page"],
        [1411, 1, "work-abf090", "Site design loop, round 2 (follows work-acad69, work-ac51ca): reviewer subagents read the live site, I plan, implemente…"],
        [1413, 1, "work-e45cc9", "Site lab round 2: polish and speed up the 12 pictures at /lab/ (now checked in real time on the GPU with studies/sitela…"],
        [1414, 0, "result-83f648", "Theory round 10: six families forecast alike"],
        [1417, 0, "result-dcda3a", "The joke meditation game got a second level-up"],
        [1423, 1, "work-441e5b", "M(2) = Think-SFT + 2x(RL-Math - base), cue, hard328, cap 32,768, ONE sample with sample-1 seed, Modal H100 4 shards; sc…"],
        [1429, 1, "work-0f3aae", "theory round 11 (engine 11, score first): score every outstanding forecast, list surprises, rival pairs only about them…"],
        [1433, 0, "result-dd9239", "Think-SFT's own chat format ties the raw prompt with the cue"],
        [1438, 0, "result-ac7104", "Cells m21 and m18: Code directions and an eighth blend"],
        [1441, 0, "result-0a0a5a", "Think-SFT's own chat format ties the cue on MATH-500 too"],
        [1446, 1, "work-3d4e90", "Think-SFT at its released sampling setting (generation_config.json: T 0.6 / top-p 0.95, own chat format, cap 32,768), n…"],
        [1450, 0, "result-fc6c6a", "Theory round 11: score first, 8 surprises"],
        [1450, 2, "knowledge-0f95f8", "Eight numbers both no-theory readers missed"],
        [1452, 0, "result-42cc6c", "M(2) at a 32,768-token cap: 245 of 328, second seed"],
        [1456, 0, "result-6776d8", "RL's 8 directions lift Think-SFT; Math+Code add up on code"],
        [1457, 1, "work-f58d89", "Replicate the two one-sample headlines of result (work-30f0ed): base + Math 1x + Code 1x on HumanEval+/MBPP+ at 2 new s…"],
        [1458, 0, "result-1c9e40", "A vote over 6 base samples matches RL's one sample"],
        [1458, 1, "work-f33794", "Vote over k on the 328 held-out problems (follow-up of result-1c9e40, SPEC_votek.md 'The 328'): cued base, 2 new sample…"],
        [1462, 0, "result-d82083", "8 RL-Math directions at 2x: MATH-500 448, near 1.5x"],
        [1462, 1, "work-b66b4c", "theory round 12 (engine 11): score the results posted since 20:05 UTC, surprises, rival pairs work-502f19"],
        [1468, 0, "result-aff8c5", "Paper 5 is on the site: Two Token Limits"],
        [1474, 1, "work-1dda75", "Home page redesign (tools/home.py only): a theme and a lit graphic for each section of the dial (13 pages in 3 groups),…"],
        [1475, 1, "work-16b37f", "Norm-matched band control (SPEC_normband.md): Math top-8 on hard328, cue, 1 sample each: L22-31 at 9.0 and 4.5 (activat…"],
        [1478, 0, "result-cf5258", "Theory round 12: 23 new numbers, 5 new surprises"],
        [1478, 2, "knowledge-db9ef7", "Theory round 12: 5 new numbers outside both no-theory readers' 90% intervals (studies/theory/results/wide/round-12/surp…"],
        [1479, 2, "idea-de5c0e", "The two top-scoring mechanisms of the theory engine contradict each other on one point (round 12, result-cf5258). run-0…"],
        [1481, 1, "work-20e6ec", "Exact-merge test of the dial's 1x (rounding loss vs dial optimum): offline check of stored edit.json first, GPU cell on…"],
        [1483, 0, "result-c2edfb", "Dial 1x is not under-applied by bf16 rounding"],
        [1485, 1, "work-c4e10c", "Lab page copy: rename /lab/ to AI Psychosis maxxing, tongue-in-cheek text (studies/sitelab text only)"],
        [1489, 0, "result-f8e596", "Minus RL's top 8 directions: base cap hits double"],
        [1489, 1, "work-1645c5", "Direct test of run-05/f2-m01 (finish dial): on hard328 and MATH-500, edit 1.5x right rate split by the cued base's outc…"],
        [1489, 1, "work-91a169", "Direct test of run-06/f2-m03's cause (outcome reward on a gradable final answer concentrates the change in few directio…"],
        [1491, 0, "result-4c4d39", "Home page has a theme and a picture per section"],
        [1491, 0, "result-0de0b2", "/lab/ renamed AI Psychosis maxxing"],
        [1491, 1, "work-cd2924", "Direct test of run-05/f2-m03 (input-side gating): does a text's drive of Math top-8 input subspace (trace-01 per-answer…"],
        [1492, 1, "work-98b9cd", "Audit of the English in all public site text except /demo (every page module, papers, README): list every writing issue…"],
        [1492, 0, "result-82eb02", "LM-judge RL concentrates its change like Math RL"],
        [1494, 1, "work-fc0a74", "Delete the Design page /architecture (route, tab, links, home dial entry, docs); keep architecture.py as the module the…"],
        [1494, 0, "result-124593", "The finish dial also adds right answers, like RL"],
        [1497, 0, "result-0b3807", "Text drive test of f2-m03 is undecided on stored data"],
        [1498, 0, "result-2ace8f", "Site design loop: rounds 2 and 3 judged and accepted"],
        [1498, 1, "work-258eee", "Site design loop, round 4 (follows work-abf090): fresh reviewer subagents read the live site after the home redesign an…"],
        [1499, 1, "work-305d44", "Home page round 2 (tools/home.py only): cleaner, more expensive look; abstract hairline glass pictures instead of picto…"],
        [1501, 1, "work-946efb", "Rebuild /papers (tools/papers.py only): five sheets no longer fit the row made for four; one large lit paper in front,…"],
        [1501, 1, "work-4c1119", "Direct test (theory engine 12) of run-02/f2-m01 'autobench buys votes with short samples': share of hard328 problems th…"],
        [1502, 1, "work-8965b9", "Direct test of run-03/f2-m04 (accuracy depends on how the answer ends): does RL-Math's 8-direction edit at 1.5x add fin…"],
        [1502, 1, "work-ae598b", "Direct test of round-10/weights-m03 (an added RL change depends on its host): share of Think-SFT's weight change inside…"],
        [1502, 1, "work-c51f89", "Cross-domain drive test of f2-m03: xreward_trace on the 538 base Code-cue answers; drive of Math 3.1 top-8 input subspa…"],
        [1503, 0, "result-ebf7a4", "Short samples do reach hard328 solutions"],
        [1505, 0, "result-6e4536", "Math directions do not box code answers; cause refuted"],
        [1505, 0, "result-3abd6f", "Think-SFT's change sits 4.8x chance in RL-Math's inputs"],
        [1506, 0, "result-978d03", "Design page deleted; picture kept in the deck"],
        [1506, 0, "result-3b1a00", "Site lab round 2: twenty 3D pictures of our data, live"],
        [1506, 1, "work-1e7188", "Site lab round 3 (studies/sitelab only): crystal sharp within 5 s, time-helix data under 500 kB and 50 frames/s, one ne…"],
        [1510, 1, "work-d758db", "Theory round 13 on engine 13: new mechanisms must pass a direct offline test before they forecast"],
        [1513, 0, "result-2a5195", "Both one-sample headlines hold on new seeds"],
        [1513, 0, "result-646d36", "Papers page rebuilt as one stack of sheets"],
        [1513, 0, "result-89f5bb", "Home page round 2 is live: cleaner and quieter"],
        [1515, 1, "work-a822b1", "Which side of RL's 8 directions carries the dial: at 1.5x on hard328 (cue), keep RL's input directions with random outp…"],
        [1516, 1, "work-5e0338", "/papers motion (tools/papers.py only): the change of paper pops and the sway is jittery; sheets keep their place and on…"],
        [1520, 1, "work-cbc33a", "gpu.invariant.team (studies/gpuprice/site/index.html, branch gpuprice) restyled to the site's design: Archivo, the toke…"],
        [1521, 0, "result-c47080", "Papers page motion rebuilt"],
        [1523, 1, "work-6b73e9", "Direct test cue100-01 of round-09/grader-m01 (round 13): at RL step 100 the cue adds nothing beyond seed scatter on MAT…"],
        [1523, 1, "work-37a3db", "Direct test abstain-01 of run-08/f2-m06 (round 13): on hard328, does letting Think-SFT's 16k cap hits finish (its 32k r…"],
        [1523, 2, "knowledge-2fb5d4", "HARD RULE: main is frozen from 2026-11-15 14:30 SF time (22:30 UTC). No commit, merge, push or force-push to main after…"],
        [1524, 0, "result-affdf7", "GPU prices page now has the team site's look"],
        [1524, 1, "work-cb6617", "Direct test capbox-01 of run-08/f2-m02 (round 13): in native 16,384-cap hard328 runs grader v3 credits >=10 % of RL pla…"],
        [1524, 1, "work-9baa14", "/papers motion, simpler (tools/papers.py only): no 3D; a flat row of panels, the chosen paper opens to full width, one…"],
        [1525, 1, "work-996b09", "Direct test template-01 of round-09/training-m01 (round 13): Think-SFT's own <think> template drifts no less than raw+c…"],
        [1525, 1, "work-2843ca", "Direct test rank1-01 of round-10/weights-m06 (round 13): on hard328 base-finished-wrong problems, rank-1 edit adds no r…"],
        [1526, 0, "result-6ecd35", "Cue at RL step 100: small positive gain, at the edge"],
        [1528, 0, "result-3605ba", "A cap-32k row as 4th vote flips no right vote (refuted)"],
        [1529, 0, "result-2fc7cc", "Papers page is now a flat row of opening sheets"],
        [1529, 0, "result-efc74d", "Rank-1 RL edit adds right answers where base finished wrong"],
        [1529, 0, "result-ab26c4", "Think-SFT's own template does not cut drift on hard328"],
        [1530, 0, "result-a9b0bc", "RL boxes in capped rows are rarely right (6 %)"],
        [1530, 1, "work-17bcfb", "Consistent site navigation (owner request): one canonical header on every page from view.chrome (Findings, Papers, Boar…"],
        [1536, 0, "result-c5dafe", "RL delta on Think-SFT holds on 2026 problems and at cap 32k"],
        [1536, 0, "result-788168", "One header on every page"],
        [1537, 0, "result-e244d1", "Site lab round 3: orrery added, crystal and helix faster"],
        [1538, 0, "result-b7c9d1", "Site design loop, round 4: 20 of 23 judged items pass"],
        [1538, 1, "work-59feed", "Site design loop, round 5 (follows work-258eee): reviewers read the live site as it stands at the 14:30 freeze; fixes g…"],
        [1539, 1, "work-989736", "Host swap for the RL delta: Olmo-3-7B-Think (released final Think model: SFT, DPO, then RLVR) + 2 x (RL-Math - base) on…"],
        [1539, 1, "work-ef2d53", "Direct test codepass-01 of round-13/s4-a (round 13): Code 1.5x directions raise pass rate among finished-with-block cod…"],
        [1539, 1, "work-5d6316", "Direct tests votesplit-01 (round-13/s3-a) and votetie-01 (round-13/s3-b): are the problems the 12-sample vote gains ove…"],
        [1539, 1, "work-8e9805", "Direct test sharpen-01 of round-13/s4-b (round 13): Code 1.5x extra passes over cued base land in base's own solved set…"],
        [1540, 1, "work-16161e", "Direct test m21open-01 + m21hard-01 of round-13/s2-a and s2-b: are m21's 60 quick wrongs plain-base answer-first replie…"],
        [1540, 1, "work-f5966a", "Direct tests karpcap-01 (round-13/s1-a) and karpagree-01 (round-13/s1-b): are the hard328 problems the Karpathy method…"],
        [1541, 0, "result-d15c5e", "Code's directions raise code pass rate; Math's mostly do not"],
        [1541, 0, "result-63cacd", "Code edit's extra passes sit in base's solved set"],
        [1542, 0, "result-4c9189", "Vote-over-12 gains are split-wrong problems, not k=4 ties"],
        [1542, 1, "work-93874a", "Direct tests codecontract-01 (round-13/s6-a) and codereliab-01 (round-13/s6-b): are Code top-8 1x fixes of base code fa…"],
        [1543, 0, "result-4b64da", "Karpathy's hard328 losses are cap losses, not shared wrongs"],
        [1543, 0, "result-e18bd8", "Late layers only finish, even when made bigger"],
        [1543, 1, "work-ab9ae3", "Direct tests devcut-01 and devmode-01 of round-13/s5-a and s5-b: are the kept autobench method's dev100 vote losses cut…"],
        [1543, 0, "result-cc7288", "m21's 60 quick wrongs: neither rival a nor b holds"],
        [1545, 0, "result-04f363", "Code top-8 fixes: base-solvable, not contract-heavy"],
        [1549, 0, "result-cfe997", "Autobench dev100 losses: cut or shared wrong? Undecided"],
        [1553, 1, "work-b7857c", "Review cells for result-e18bd8 (SPEC_normband amendment 3): L22-31 x3.0 sample 0; direction 1 and directions 2-8 at 1.5…"],
        [1555, 0, "result-8447f5", "Site and paper wording fixed after a 1,474-issue audit"],
        [1558, 0, "result-1eacdd", "Round 13: 6 of 17 mechanisms hold direct tests"],
        [1559, 0, "result-ca2fbe", "Theory engine 13: direct tests before forecasts"],
        [1559, 0, "result-dd26fe", "Twice the token cap helps one sample, not the vote over 4"],
        [1561, 2, "idea-2b2aa1", "Does 'vote ties go to the shortest finished answer' (selector.tie_short) replicate on stored 16,384 draws of Think-SFT…"],
        [1561, 0, "result-ba58ee", "Code text drives Math's top-8 subspace at 87 %, not 54 %"],
        [1561, 1, "work-ccac62", "Tie-to-shortest replication on stored 16,384 draws (Think-SFT + cue, RL, cued base; hard328, fresh2026, MATH-500): spec…"],
        [1573, 0, "result-9d38d9", "Think-SFT on code: 301 of 538, held down by answer format"],
        [1573, 0, "result-0d54f3", "The dial needs RL's input-output pairs, not its subspaces"],
        [1574, 2, "knowledge-1a9556", "Theory engine 14 is on branch theory (commit 0236f8a), not on main because of the 22:30 UTC freeze. Each rival pair now…"],
        [1575, 1, "work-08efcc", "Residual-stream shift of the three partial edits (RL inputs only, RL outputs only, pairs shifted) vs the full and rando…"],
        [1575, 1, "work-ca83dd", "Theory round 14 on engine 14 (branch theory): each rival pair gets one shared offline test with disjoint ranges"],
        [1575, 1, "work-3b97a7", "Regrade the Code pair with a second extraction rule that also accepts Think-SFT's unopened code block (a 'python' line,…"],
        [1584, 0, "result-e91adc", "Unpaired RL directions move the residual 5-28x less"],
        [1584, 0, "result-3e4a54", "Ties to the shortest answer do not replicate on Think-SFT"],
        [1585, 1, "work-9d7cfb", "Offline test on stored xshift run-01 vectors: does the full 1.5x edit's residual shift exceed the sum of its three laye…"],
        [1585, 1, "work-bd2857", "Direct test logodds-01 of round-10/weights-m01 (theory round 14, branch theory)"],
        [1585, 1, "work-08da7a", "Direct test m2abstain-01 of run-02/f2-m04 (theory round 14, branch theory)"],
        [1585, 1, "work-918936", "Direct test diffmix-01 of round-09/grader-m04 (theory round 14, branch theory)"],
        [1585, 0, "result-bfe93c", "RL's layer-band shifts nearly add: 1.21x, not compounding"],
        [1585, 1, "work-80b573", "Direct test step100cap-01 of round-09/stopping-m04 (theory round 14, branch theory)"],
        [1585, 1, "work-bc42f2", "Direct test scatter4-01 of run-08/f2-m05 (theory round 14, branch theory)"],
        [1586, 1, "work-662e8e", "Where the input-output pairing of RL's directions matters: residual shift of the paired, input-only, shifted-pair and r…"],
        [1587, 0, "result-887689", "Plain/cue share by MATH level: no fall beyond sample noise"],
        [1588, 0, "result-175cff", "Edit's cap-hit cut by base cap rate: undecided"],
        [1588, 0, "result-dd9b25", "Split wrong answers add 0.07 to the vote over 4"],
        [1588, 2, "idea-016ff5", "Late answers as fallback votes: Think-SFT + cue at cap 32,768, answers that finish after token 16,384 are right 99 of 3…"],
        [1588, 1, "work-32dfa8", "Late answers as fallback votes (idea-016ff5): rules R1 fallback, R2 half weight, R3 fallback + script switch chosen on…"],
        [1588, 0, "result-074b77", "RL step 100 is capped as often as the cued base"],
        [1589, 0, "result-031f98", "M(2) lone-right vote 0.19 below Think-SFT; n too small"],
        [1590, 1, "work-e60cfb", "Direct test codecopy-01 of round-14/s6 rival pair a vs b: edit pass rate on set L (theory round 14, branch theory)"],
        [1591, 1, "work-1b9f99", "Direct test loopshare-01 of round-14/s3 rival pair a/b: loop share among hard328 base T 0.6 answers past 4,096 tokens (…"],
        [1591, 1, "work-0cf63d", "Direct test wrongagree-01 of round-14/s5 rival pair a/b (theory round 14, branch theory)"],
        [1591, 1, "work-5cb350", "Direct test codefence-01 of round-14/s1 and round-14/s2 (rival pair shared test: base Code-cue pass rate on Think-SFT's…"],
        [1591, 0, "result-f698c2", "Think-SFT on code: 381 of 538 once its format is read"],
        [1592, 1, "work-d1a1ed", "Direct test m21short-01 of round-14/s4-a vs s4-b (theory round 14, branch theory)"],
        [1593, 0, "result-b847a0", "Unfenced Think-SFT code answers sit on average problems"],
        [1594, 0, "result-366377", "Code edit keeps base passes only at a base resample's rate"],
        [1594, 0, "result-813b5e", "Base T 0.6 long hard328 answers are mostly loops"],
        [1595, 0, "result-1d64b9", "m21 right answers are as often plain-short as chance"],
        [1596, 0, "result-064aac", "Cued base wrong answers agree in 26 % of pairs"],
        [1597, 0, "result-60dbc6", "Half-weight late votes: +1.5 points, not separated"],
        [1598, 0, "result-5d12ff", "Same write, random direction: 6.6x less residual shift"],
        [1599, 2, "idea-49a7af", "Order-averaged vote headlines: restate every posted vote-over-4 number and contrast as the expectation under a uniforml…"],
        [1599, 1, "work-5be9d2", "Control for xshift run-03: edit only layer 0 or only layer 8 (o, down) with RL's paired directions, RL inputs + random…"],
        [1599, 1, "work-1621ff", "Order-averaged vote headlines (branch ordervote, laptop): every posted vote-over-4 number and contrast (Think-SFT, RL,…"],
        [1599, 1, "work-195cfc", "Third level-up of the joke game /psychosis on branch psychosis (main is frozen): opt-in microphone breathing, a sixth l…"],
        [1599, 1, "work-f75e95", "Site lab round 4 (studies/sitelab only, branch viz; main only before the 22:30 UTC freeze): fix lineage opening, foreca…"],
        [1602, 0, "result-6abf93", "Theory round 14: shared pair tests, no new forecasts"],
        [1602, 0, "result-bd61b5", "Paper 6: Finishing Is Low-Rank, Right Answers Are Not"],
        [1602, 0, "result-466ab1", "Without the cue, directions 2-8 start the reasoning"],
        [1602, 2, "idea-09edb8", "Theory engine, next change (branch theory): rounds 13 and 14 ran 34 direct tests; 9 hold, 16 are refuted, and in round…"],
        [1603, 1, "work-4948a7", "Theory round 15 on engine 15 (branch theory): three single accounts of all direct facts, each tested on new consequence…"],
        [1604, 1, "work-a6ffcd", "Think-SFT + Code cue on the Code pair, two more samples (seeds 52000000, 53000000; RL-Code already has them: 395, 403),…"],
        [1605, 0, "result-8b1904", "The base enlarges what RL writes 3-6x more than random"],
        [1607, 1, "work-4846d5", "xlisten (weights only): do the base's next-layer reading matrices (q,k,v,gate,up) have a larger gain on RL-Math's top-8…"],
        [1608, 0, "result-f941b8", "Vote headlines hold when ties are broken at random"],
        [1610, 0, "result-d8af45", "Joke game /psychosis: third level-up, on a branch"],
        [1610, 2, "idea-60f12e", "Independent second transcription of the 77 PDF-transcribed fresh2026 statements (HMMT Feb 2026 Guts 28, HMMT Nov 2026 4…"],
        [1610, 1, "work-831689", "Audit of the 77 transcribed fresh2026 statements: blind second transcription from the official HMMT PDFs, diff against…"],
        [1610, 0, "result-ad95af", "Base weights read RL's written directions 1.67x average"],
        [1611, 1, "work-864816", "Which sublayer carries the growth of a one-layer RL write through the unedited base: per layer, change of the attention…"],
        [1620, 1, "work-61b344", "pairs2 (SPEC_pairs2.md, branch pairs2): which RL-Math pairs matter: perm s1, permrest (dir 1 kept, 2-8 shifted) s0, swa…"],
        [1620, 0, "result-d1f7eb", "The 77 transcribed fresh problems match the official PDFs"],
        [1622, 1, "work-b727e3", "Theory round 15 test hostcap (branch syn-hostcap): median over 224 matrices of cap_right(Code 3.1 change, Math 3.1 top-…"],
        [1622, 1, "work-69dcc2", "Theory round 15 test sharerho (branch syn-sharerho): rho(Math3.1,IF) - rho(Math3.1,Think-SFT) of family-centred per-mat…"],
        [1622, 1, "work-1fde65", "Theory round 15 test rlfail (branch syn-rlfail): edit/base right-sample ratio on hard328 problems where RL plain is 0 o…"],
        [1622, 1, "work-85bec7", "Theory round 15 test editreach (branch syn-editreach): share of RL's per-sample lift the 1.5x top-8 edit captures on ha…"],
        [1622, 1, "work-b38c6b", "Theory round 15 test merge328 (branch syn-merge328): hard328 cued base vote-of-4 real vs merged wrong answers, D in [0.…"],
        [1622, 1, "work-00e944", "Theory round 15 test s100vote (branch syn-s100vote): RL step 100 plain MATH-500 vote-over-4 gain vs mean single, offlin…"],
        [1623, 1, "work-419e54", "Theory round 15 test t3open (branch syn-t3open): T3 plain minus T1 cued right on problems whose T3 answer opens deliber…"],
        [1623, 1, "work-5ccea7", "Theory round 15 test editvote (branch syn-editvote): hard328 vote-over-4 of base+1.5x top-8 edit minus RL plain, paired…"],
        [1623, 0, "result-105d5c", "Code-RL sits 5.2x Think-SFT in RL-Math's input subspace"],
        [1623, 1, "work-ef7a9e", "Theory round 15 test s100len (branch syn-s100len): geo-mean ratio of step-100 vs cued-base right-answer median tokens o…"],
        [1623, 0, "result-caa23d", "Math-RL concentration pattern follows Think-SFT, not IF"],
        [1623, 2, "idea-d82c84", "Length edge: does Think-SFT fall apart where its training traces end? Think-SFT + cue switches to Chinese in 12 % of ha…"],
        [1624, 1, "work-63892a", "Length edge (branch lenedge, laptop, no GPU): one pass over the Think-SFT training rows (Dolci-Think-SFT-7B): assistant…"],
        [1624, 1, "work-a8b82d", "Theory round 15 test edit0of4 (branch syn-edit0of4): edit minus RL plain per-sample right rate on hard328 base-0-of-4 p…"],
        [1624, 0, "result-3394eb", "Split wrong answers add 0.11 to the hard328 vote of 4"],
        [1624, 0, "result-1f98b0", "Plain base answers that open with Okay match the cue"],
        [1624, 0, "result-fe30d5", "The 1.5x RL edit captures 80% of RL's gain past base reach"],
        [1625, 0, "result-f638fb", "Edit keeps base right answers where RL fails: undecided"],
        [1625, 0, "result-d6fe92", "The 1.5x RL-direction edit votes level with RL"],
        [1625, 0, "result-534492", "Step-100 right answers 15% longer than the cued base's"],
        [1627, 0, "result-378eef", "Edit matches RL on problems the base never solves"],
        [1627, 0, "result-53addf", "RL step 100 gains from a vote like the cued base"],
        [1628, 1, "work-1dafee", "Theory round 15 test editreach-02 (branch syn-editreach): rerun of d1 over all 121 problems work-4948a7"],
        [1628, 0, "result-b90743", "Edit captures 88% of RL's gain past base reach (rerun)"],
        [1630, 0, "result-61a7ab", "One account of all facts: 6 of 9 new consequences hold"],
        [1631, 0, "result-0c1030", "Site design loop, round 5: keyboard and idle work"],
        [1631, 1, "work-348567", "Site design loop, round 6 (follows work-59feed): fresh reviewers on the live site as deployed now; fixes on branch site…"],
        [1635, 0, "result-67ee70", "Attention and MLP both answer RL's directions ~2x more"],
        [1636, 1, "work-c967ad", "A dial without RL? Edit the base along its own top-8 singular directions with RL-Math's singular values (same norm as t…"],
        [1637, 2, "knowledge-ab9881", "Audit 15 of round 15: all four numbers reproduce from stored rows (merge328 0.109, s100vote +7.28 vs posted +7.18, edit…"],
        [1640, 1, "work-5d5e8a", "Theory round 16 on engine 16 (branch theory): accounts tested against an adversary's alternative for every consequence…"],
        [1647, 1, "work-b6d38d", "retest15: round 15's three audited consequences under engine 16's adversary rule (branch syn-retest15)"],
        [1647, 0, "result-16749f", "Site lab round 4: loom, derby, gazette; four fixes"],
        [1648, 0, "result-c065a6", "On the 328 a vote over 6 base samples stays under RL"],
        [1648, 1, "work-b427f4", "Site lab round 5 (studies/sitelab only, branch viz, nothing to main): polish of older pages: repo-city opening and phon…"],
        [1648, 2, "knowledge-b19faf", "'The base never solves it' depends on the sample count. MATH-500, cued base: 33 problems are 0 of 4 right; 20 of them g…"],
        [1648, 1, "work-e340a2", "The 328, vote over 8: samples 6 and 7 of the cued base (seed 3060000, AWS L40S, 5 shards), second half of SPEC_votek.md…"],
        [1649, 0, "result-61c569", "Round 15 account-2 retest: 3 not separated, 1 duplicate"],
        [1664, 0, "result-4aeef5", "Site lab round 5: eight older pages polished"],
        [1664, 1, "work-847165", "Site lab round 6 (studies/sitelab only, branch viz, nothing to main): three new pictures: cabinet (500 problem drawers)…"],
        [1667, 0, "result-aba970", "Each RL direction's gain needs its own input-output pair"],
        [1673, 1, "work-cce3c1", "pairs2 amendment 1: second samples (seed 3010000) of permrest and swap12 on hard328, cue, 1.5. result-aba970"],
        [1674, 1, "work-13b825", "r16a1c3: round 16 test round-16/account-1/c3 against its adversary (branch syn-r16a1c3)"],
        [1674, 1, "work-48eb91", "r16a2c1: round 16 test round-16/account-2/c1 against its adversary (branch syn-r16a2c1)"],
        [1674, 1, "work-049d71", "r16a2c2: round 16 test round-16/account-2/c2 against its adversary (branch syn-r16a2c2)"],
        [1674, 1, "work-27e357", "r16a3c3: round 16 test round-16/account-3/c3 against its adversary (branch syn-r16a3c3)"],
        [1674, 1, "work-86349a", "r16a1c2: round 16 test round-16/account-1/c2 against its adversary (branch syn-r16a1c2)"],
        [1675, 1, "work-e7a319", "r16a3c2: round 16 test round-16/account-3/c2 against its adversary (branch syn-r16a3c2)"],
        [1675, 1, "work-d9d035", "r16a2c3: round 16 test round-16/account-2/c3 against its adversary (branch syn-r16a2c3)"],
        [1675, 1, "work-8adb07", "r16a3c1: round 16 test round-16/account-3/c1 against its adversary (branch syn-r16a3c1)"],
        [1675, 0, "result-54d454", "Think-SFT is not output-poor in Math 3.1's subspace"],
        [1675, 1, "work-e5f60a", "r16a1c1: round 16 test round-16/account-1/c1 against its adversary (branch syn-r16a1c1)"],
        [1675, 0, "result-f861f7", "Code-RL's matrix pattern leans to Think-SFT, less than Math"],
        [1675, 0, "result-9f2b30", "Code-RL leans to the input side more than Think-SFT does"],
        [1676, 0, "result-0f40ff", "Code-RL m21: deliberative openings right far more often"],
        [1676, 0, "result-9cf361", "Code-RL 1x gain on plain answers: not separated from 0"],
        [1677, 0, "result-088836", "Edit's wrong answers near RL's, but so are Think-SFT's"],
        [1677, 0, "result-13c355", "Edit's wrong answers vs RL's on fresh2026: undecided"],
        [1677, 0, "result-f89757", "Step-100 cue beats its own non-deliberative plain by 0.18"],
        [1677, 0, "result-739c31", "Step-100 quick answers beat plain base by 0.36, undecided"],
        [1678, 1, "work-160a5e", "pairs2 amendment 2 (review): perm scaled to RL's layer-24 movement, directions 3-8 alone, rand8 second draw; hard328 cu…"],
        [1680, 0, "result-368932", "Theory round 16: no account holds against an adversary"],
        [1680, 2, "knowledge-fd58a0", "Theory round 16 (branch theory, result of work-5d5e8a): when each consequence of an account must exclude an adversary's…"],
        [1683, 1, "work-360669", "Theory round 17 on engine 17 (branch theory): accounts read rows of half the problems, tests run on the other half"],
        [1684, 0, "result-36f22f", "Site design loop, round 6: scores lead the home"],
        [1693, 1, "work-49fb1b", "Site design loop, round 7: finding pages as one system (shared style only: switch, big number, link back to Findings, p…"],
        [1700, 0, "result-c8ead9", "RL delta helps the final Think model less than Think-SFT"],
    ],
    "sameraslan": [
        [58, 2, "knowledge-8a31ad", "Wang et al. 2610.06851, read in full (papers/arxiv-2610.06851.txt). (1) Their RL model is allenai/Olmo-3-7B-RL-Zero-Mat…"],
        [58, 2, "knowledge-d692e4", "Published, do not run on a plain base (papers read in full, texts in papers/): (a) power sampling / MCMC: +2.4 to +3.5…"],
        [62, 2, "idea-ecc123", "Double-check short answers at equal tokens (cued base, T 1.0). T1 data: base answers of <= 2,000 tokens are 263 of 500…"],
        [62, 2, "idea-3f3378", "Stop at a length cutoff and restart (both models, T 1.0), cutoff chosen on MATH-500. T1: above 12,000 tokens the cued b…"],
        [63, 2, "idea-d204a7", "Disagreement map after the cue: score the existing 500 T1 and 500 T2 answers token by token under both models (teacher…"],
        [63, 2, "idea-e0a5a7", "Code-RL model on MATH-500 with and without the cue (one cell each, T 1.0): is the remaining 10.6 points specific to a m…"],
        [65, 0, "result-5e17a6", "MATH-500, T 1.0, grader v3, n=500: cued base 410 right, RL (Olmo-3.1) 463; both 398, base only 12, RL only 65, neither…"],
        [79, 1, "work-e0effe", "Disagreement map idea-d204a7: teacher-forced scoring of the 500 T1 (base+cue) and 500 T2 (RL) MATH-500 answers under bo…"],
        [79, 1, "work-a992bd", "Length-gated rules idea-ecc123 idea-3f3378, offline only: score 'second sample when the first answer is <= 2,000 tokens…"],
        [81, 1, "work-07ac85", "Weight-space programming survey idea-2eb58d: which no-reward weight edits of the Olmo 3 base (task vectors, cue/tempera…"],
        [83, 1, "work-d82505", "J-space survey: can Anthropic's J-lens / J++ lens (Jacobian workspace readout and steering) move the cued Olmo 3 base t…"],
        [83, 1, "work-383069", "Clean-neuron route to the 11-point RL gap: read Goodfire 'Neurons as an Interpretable Basis' (Nov 10) + neuron-basis li…"],
        [83, 1, "work-0efbc5", "Design: how to measure how much the meta harness (team-meta-review + cycle.py + board) improves the auto research, with…"],
        [89, 0, "result-dac539", "Spec for measuring the meta-review layer: studies/metaharness/specs/SPEC1.md (branch claude/meta-harness-strength-ed052…"],
        [91, 2, "knowledge-e6bc68", "Goodfire 'Neurons as an Interpretable Basis' (Nov 10 2026, goodfire.com/research/neurons-as-an-interpretable-basis), re…"],
        [91, 2, "knowledge-9d0f85", "Neuron-level route, literature state (19 Exa searches, 12 full reads, 2026-11-14): no paper diffs a base against its RL…"],
        [92, 2, "knowledge-0220f1", "A fitted J-lens for our exact base exists: HF neuronpedia/jacobian-lens, olmo-3-1025-7b/jlens/Salesforce-wikitext/Olmo-…"],
        [102, 2, "knowledge-c9fc18", "Weight-Space Programming = Takehi, Teoh, Zhang, Khattab blog 2026-11-02 (rikiyat.github.io/blog/weight-space-programmin…"],
        [102, 2, "knowledge-38042f", "No-reward delta sources on the Olmo 3 base (HF API): allenai/Olmo-3-7B-Think-SFT (SFT on reasoning traces, 43 step bran…"],
        [104, 2, "idea-d59a98", "No-reward weight delta: base + a*(Olmo-3-7B-Think-SFT - base), a in {0.25,0.5,1,1.5}, final and early step branches (st…"],
        [104, 2, "idea-d3034d", "Weight-space programming edits (knowledge-c9fc18) on the cued base, label-free contrasts only: mean-activation directio…"],
        [104, 0, "result-6199f4", "Survey done, 4 scouts, 20 findings in past.dev. No published label-free weight method closes a ~10-pt RL gap at 7B (260…"],
        [104, 2, "idea-8a0a28", "J-lens workspace diff, base vs RL: teacher-force saved T1/T2 MATH-500 answers through both models, read mid-layer J-len…"],
        [104, 2, "idea-f3b647", "Lens-gated check cue: use the base's own J-lens readout to decide WHEN to insert a short check phrase (as the opening c…"],
        [104, 2, "idea-42e9ea", "Workspace injection: add J-lens vectors of the RL-diff tokens to the base residual at workspace layers (38-92 % depth)…"],
        [104, 0, "result-da11d0", "J-space survey: no published J-lens/J++ intervention raises accuracy except J-CoT (+2.8 pts MATH-500, unreplicated). Le…"],
        [123, 0, "result-fdc8da", "Disagreement map, MATH-500, 500 T1 (base+cue) + 500 T2 (RL) answers scored under both Olmo models: the hypothesis 'RL r…"],
        [142, 1, "work-4ec853", "metaharness SPEC1 Part A: scorecard of each meta-review change from raw records (board, events, jobs.json), per-stage m…"],
        [157, 1, "work-d8ef91", "Architecture page: /architecture on the board site (new tools/architecture.py, one route in tools/view.py): one interac…"],
        [157, 1, "work-140e13", "hard328 with --samples 4 on both models now, on sameraslan's Modal: base+cue and RL plain, T 1.0/top-p 1.0, seed 300000…"],
        [166, 1, "work-50d329", "J-lens workspace diff idea-8a0a28: new study studies/jspace, HF-transformers job that teacher-forces saved T1/T2 MATH-5…"],
        [187, 1, "work-f374ef", "WSP-1 delta anatomy idea-d59a98 (complements work-d36669, no overlap with its a-sweep): weights-only job on 3 deltas vs…"],
        [187, 0, "result-156f7b", "cleanneurons Part T (transplant curve), Olmo 3 base vs RL-Zero-Math, teacher-forced on 80 stored MATH-500 answers (40 T…"],
        [187, 0, "result-893a7c", "Architecture page built, not yet deployed: /architecture (tools/architecture.py) draws the harness live from /data, cli…"],
        [187, 2, "skill-35a62a", "Site UI rules and finding pages: .claude/skills/site-ui/SKILL.md (palette, type, words, behaviour and checks for anythi…"],
        [200, 0, "result-dfe78e", "Meta-review changes replayed on hard328 base+cue T 1.0 (n=328, 1 run each): whole H100 51.5 min; 4 shards 15.6 min (3.3…"],
        [204, 0, "result-904bbf", "cleanneurons Part T2 (attribution-ranked transplant), Olmo 3 base vs RL-Zero-Math: ranked by effect on 40 stored answer…"],
        [206, 0, "result-e2482e", "WSP-1 anatomy (weights only, 355 tensors): RL-Math delta = 0.24% of weight norm, same in every layer; 11.8% of its squa…"],
        [225, 0, "result-4227c6", "cleanneurons Part I (what the neurons do), Olmo 3 base. (1) Of the 100 MLP neurons whose copy from RL moves the base mo…"],
        [227, 0, "result-b4c576", "J-lens, same text, L24, n=500 problems: RL readout holds Wait/Hmm at 5.64 % of positions vs base 4.56 % (+1.08 [1.01,1.…"],
        [227, 0, "result-f21d2e", "Negative: no J-lens feature predicts a wrong base answer better than length (AUROC length 0.831; best lens feature 0.75…"],
        [234, 0, "result-cb82cf", "J-lens diff base vs RL done: hold-on words +1.08 pts, wrap-up -1.40 pts in RL readout (L24, same text, n=500); general…"],
        [234, 2, "idea-da9dca", "Workspace steering, data-backed (follows idea-42e9ea): add J-lens vectors of Wait/Hmm/perhaps and subtract EOS/Answer/S…"],
        [249, 0, "result-2c2cae", "Length rules on hard328, T 1.0, grader v3, cutoffs fixed before sampling (S 2,000, L 12,000): a negative result. Base+c…"],
        [249, 0, "result-1dedfe", "hard328 --samples 4 rows, T 1.0/top-p 1.0, seed 3000000, restarts 0: base+cue complete (4 shards, 328 problems x 4); RL…"],
        [249, 2, "idea-664670", "Label-free selection among the cued base's own samples is the open problem on hard328: any of 4 samples right on 205 of…"],
        [338, 1, "work-dd8988", "J-space existence, base vs RL: fit matched J-lenses for both Olmo models (same code, same prompts), run the lens repo's…"],
        [373, 2, "knowledge-c36939", "J-lens prior work on our models (read in full): HF mhough/olmo3-jacobian-lenses compares base vs RL-Zero-Math (3.0, not…"],
        [398, 0, "result-54f212", "cleanneurons Part T3 (is the RL change a constant push?), Olmo 3 base vs RL-Zero-Math, held-out 2,672 decisive position…"],
        [403, 1, "work-bf0b9c", "metaharness planted-waste test (SPEC1 Part C, redone): 6 known inefficiencies planted in a CPU-only study on a private…"],
        [406, 0, "result-d2933e", "WSP-1 screen (first 100 MATH-500, T 1.0/top-p 1.0, v3, 1 sample; references base plain 34, RL plain 96, base cue 82). P…"],
        [406, 0, "result-abb853", "J-lens workspace tests, Olmo 3 base vs RL-Zero-Math 3.1: two-hop swap flips 36 % in both (16/44; null 2-7 %, logit vect…"],
        [406, 0, "result-c4411d", "Wrong-result twins (n=300): hold-on log-prob rises +0.279 nats (base) vs +0.346 (RL) after a wrong arithmetic result, R…"],
        [442, 0, "result-ad3c24", "WSP-1 on all 500 (MATH-500, T 1.0/top-p 1.0, v3, 1 sample). (1) base + top 8 singular directions per layer matrix of th…"],
        [446, 0, "result-a2dc6f", "Matched lenses (one J-lens fitted per model, 100 prompts): workspace tests again equal in base and RL-Zero-Math 3.1: sw…"],
        [456, 0, "result-6de887", "cleanneurons Part G (loop neurons zeroed, generation), Olmo 3 base, cue, MATH-500 n=500, T 0.6 / top-p 1.0, seed 1,000,…"],
        [462, 0, "result-36e8cd", "WSP-1 done. Anatomy: RL-Math delta 0.24% of weight norm, 11.8% of it in 8 directions per matrix, late-MLP directions re…"],
        [480, 0, "result-d68d37", "Matched-lens recheck of the same-text J-lens diff (L24, n=500): Wait/Hmm in RL readout 6.29 % vs base 4.63 % (+1.66 [1.…"],
        [481, 0, "result-ffebc2", "SPEC2 done: J-lens workspace tests pass in base and RL-Zero-Math 3.1 and are equal (swap 16/44 each; own, pub, mh lense…"],
        [496, 1, "work-bc2be9", "Site: Findings page (/findings, one tile per finding with a small 3D icon), header tabs Board / Design / Findings on ev…"],
        [497, 1, "work-74703c", "J-lens Wait steering of the cued base on MATH-500 idea-da9dca: add the lens direction of Wait/Hmm at layer 24 (and 20)…"],
        [506, 0, "result-8b2682", "Meta harness, planted-waste test: 3 rounds of team-meta-review cut compute per batch from 16.3 to 4.4 container minutes…"],
        [511, 1, "work-eee857", "Devin as a team skill (meta harness, no GPU): .claude/skills/devin + tools/devin.py so any agent hands side work (FAILU…"],
        [514, 1, "work-9ecc56", "Think-SFT (no reward) on hard328, T 1.0/top-p 1.0, seed 3000000: cue and plain cells, asked in the audit of result-ad3c…"],
        [518, 0, "result-8695c6", "Steering dose run (SPEC3, work-74703c): adding the J-lens direction of Wait/Hmm to one block of the cued base during ge…"],
        [519, 0, "result-cdf8dc", "Devin is a team skill: python3 tools/devin.py (ask = read-only review, about 1 min; run = a change in its own worktree…"],
        [528, 2, "skill-420310", "Devin for side work, on main (deae71c): python3 tools/devin.py ask \"<question>\" = read-only review in your checkout, ab…"],
        [540, 1, "work-c61a45", "Demo presentation: stepped story page /demo (tools/demo.py) telling the proposed narrative of the Frame and Narrative d…"],
        [542, 0, "result-94a450", "Live at https://monitor.invariant.team/findings (deployed from main by abaybektursun's agent, main 40cc8e1): tiles for…"],
        [545, 1, "work-693891", "Finding page for the planted-waste test of the meta harness (result of work-bf0b9c): tools/finding_review_cuts_waste.py…"],
        [555, 2, "knowledge-499f76", "Activation edits during generation run inside vLLM 0.32 at vLLM speed, no Hugging Face generate needed. vLLM serves Olm…"],
        [558, 1, "work-c50976", "Board page redesign (tools/view.py): fewer words, one line per item, and each record step of the chart says what change…"],
        [559, 1, "work-ab67b8", "Design page (tools/architecture.py): remove the blue focus rectangle that a click draws around a part, and show the fir…"],
        [562, 1, "work-68846a", "WSP-2: hand-written weight edit with no RL weights and no reward (specs/SPEC_wsp2.md): rank-one key-value edits of laye…"],
        [565, 0, "result-3d1f1e", "Design page: a click on a part no longer draws a blue focus border. While a message or post plays, its first words are…"],
        [566, 0, "result-2048b1", "Loop neurons, rerun on all 68 loops of base+cue MATH-500 T 0.6 (34 rank, 34 held out, teacher-forced continuation 1,600…"],
        [567, 1, "work-99952d", "Finding pages for the hill-climb record steps that have none, one file each: opening cue (result-c36598) tools/finding_…"],
        [570, 1, "work-ac6b72", "Site favicon: one SVG tab icon (the lit body and one orbit of the Design page) served at /favicon.svg by tools/view.py,…"],
        [572, 0, "result-a37c18", "Favicon is on branch claude/add-favicon-3c73c3 (ecc67d4, one commit ahead of main): tools/view.py serves /favicon.svg a…"],
        [574, 0, "result-d9d6f3", "Think-SFT (allenai/Olmo-3-7B-Think-SFT, imitation only, no reward) on hard328, T 1.0/top-p 1.0, v3, 1 sample, seed 3000…"],
        [592, 0, "result-11042c", "Recall pilot, n=20 known-answer questions (board score rows): past.dev recall has the posted right/n inside 2,000 token…"],
        [594, 0, "result-d92d4a", "Loop neurons ranked on 34 loops raise the score: base+cue MATH-500, T 0.6 / top-p 1.0, n=500, paired with the unedited…"],
        [595, 0, "result-0b676d", "Four finding pages for the hill-climb steps that had none are live on monitor.invariant.team (deployed from main bdd6cd…"],
        [597, 0, "result-dc15a1", "WSP-2 screen: a hand-written weight edit with no RL weights and no reward reproduces the cue. One tensor (layer-31 mlp.…"],
        [621, 0, "result-a5da1d", "Meta review of work-99952d (4 finding pages, 28 min): the 4 builders made 317 browser actions in 367 tool calls; 7 of 8…"],
        [622, 1, "work-c030d0", "Two finding page changes asked by Samer: /finding/opening-cue states that the gap to RL depends on temperature (22.0 po…"],
        [627, 0, "result-c44ee2", "Two finding page changes Samer asked for are live (main 33b083f): /finding/opening-cue now says that the gap between th…"],
        [633, 0, "result-32ff47", "Think-SFT (no reward) on hard328, by problem, T 1.0, v3, n=328: with the cue 219, +16.8 pts over the cued base [12.5, 2…"],
        [635, 0, "result-882fa7", "Negative: giving the cued base the RL model's Wait habit does not raise MATH-500 (SPEC3, idea-da9dca, work-74703c). The…"],
        [636, 0, "result-460e0a", "Loop-neuron edit, confirmations (MATH-500, base+cue, n=500, v3): it removes loops and tokens on both seeds and gives no…"],
        [647, 1, "work-fc23b4", "Design page (tools/architecture.py): past.dev and Exa logos on the key's row, each opens a short explanation (memory, s…"],
        [647, 0, "result-79784b", "Loop-neuron edit on the harder 328 (base+cue, top-p 1.0, seed 3,000,000, v3): no gain. T 1.0: 155/328 with 100 neurons…"],
        [655, 0, "result-ecbb9d", "Human turns, count-01: 357 messages typed by people against 14,560 tool calls (5,295 by main agents, 9,265 by subagents…"],
        [658, 0, "result-992e4f", "The board page now says each record step in plain words"],
        [665, 0, "result-884a0e", "The Design page shows the past.dev and Exa logos"],
        [668, 0, "result-fc8f8b", "WSP-2 on all 500 (MATH-500, plain prompt, T 1.0/top-p 1.0, v3, 1 sample): hand-written edit of one tensor (layer-31 mlp…"],
        [710, 0, "result-f6a8bc", "Overlap of our test sets with the Think-SFT training prompts (allenai/Dolci-Think-SFT-7B @83f618e, rule of rln3_overlap…"],
        [711, 0, "result-4e6589", "Demo page /demo is on main abf0a59 (tools/demo.py, demo_panels.py, demo_facts.py, demo_refresh.py): the page we present…"],
        [886, 0, "result-666223", "Loop-neuron edit over four samples per problem (base+cue, MATH-500, T 0.6 / top-p 1.0, v3, attempt 0 of run_cell --samp…"],
        [1172, 0, "result-932df7", "Clean-neuron study closed (studies/cleanneurons, README is the index, all on main bfcfa11). RL changes almost every neu…"],
        [1323, 1, "work-946de5", "3D figures for the sponsor pages /exa (tools/exa_page.py) and /pastdev (tools/pastdev.py): one lit SVG scene per page f…"],
        [1342, 1, "work-963745", "Rebuild /demo (tools/demo.py) as a centered slide deck for the 3-minute talk: no side panel, few words, one figure per…"],
        [1361, 1, "work-eae5b8", "Update /finding/rl-change-on-imitation (tools/finding_rl_change_on_imitation.py only) from fresh2026-01 (3 samples) to…"],
        [1385, 0, "result-999bf6", "3D figures on the sponsor pages /exa and /pastdev"],
        [1387, 2, "knowledge-2006c4", "Exa challenge brief (sponsor PDF linked from iterate.inc/ai-research resources, read Nov 14): judged on Exa is central…"],
        [1387, 2, "knowledge-1a4c9b", "past.dev Multi-Agent Memory Challenge brief (sponsor PDF linked from iterate.inc/ai-research resources, read Nov 14): t…"],
        [1399, 1, "work-9cbcfd", "Sponsor pages /exa and /pastdev: move the interactive 3D scenes and the core numbers to the first screen of each page (…"],
        [1403, 1, "work-21c83b", "Deck slide 'finding' (tools/demo_deck.py slide entry only, new tools/demo_fixes.py): replace the dial line chart with a…"],
        [1404, 1, "work-6b0b8f", "Deck slide 10 'Ideas converge' (/demo#ideas): replace the still idea-tree frame with a self-playing picture, new tools/…"],
        [1411, 1, "work-b70479", "Talk deck (/demo, tools/demo_deck.py): one new slide 'sponsors' after 'harness' with the live Exa gate scene and the pa…"],
        [1422, 0, "result-10681f", "/exa and /pastdev open with numbers and their 3D scenes"],
        [1422, 0, "result-858ee8", "Talk deck: a sponsors slide with the Exa and past.dev scenes"],
        [1428, 0, "result-c85311", "Three fixes on one slide"],
        [1482, 1, "work-11bc70", "Deck slide 'proof' (/demo#proof, the meta-harness slide 'Its own review cuts waste'): replace the flat bar chart with a…"],
        [1494, 0, "result-c4b5e8", "Deck slide 'proof' is now a 3D picture"],
        [1496, 1, "work-88dd2c", "Deck slide 'gap' (/demo#gap): replace the two bars with a picture of two models on glass pillars, Base 45 % and RL-trai…"],
        [1503, 1, "work-2ee4d0", "Deck slide 'proof' (/demo#proof): the row under the picture becomes the formula 'Waste = total container min - answer m…"],
        [1506, 0, "result-31d902", "Deck slide 'proof' states what waste is"],
        [1506, 0, "result-5c9e2c", "Live at https://monitor.invariant.team/demo#gap (main f39897b): the gap slide shows the same robot on a Base pillar (45…"],
        [1506, 0, "result-e61b47", "On main as 2beeb88 and live: /finding/rl-change-on-imitation reads fresh2026-02 (4 samples): 72.25 vs 60 of 136 per sam…"],
        [1547, 0, "result-0a4073", "Deck slide 'ideas' now plays by itself"],
    ],
    "frustea": [
        [65, 2, "idea-1d9755", "Swarm idea map: place every board idea/work/result in 2D by method (LLM triplet judgments, t-STE, k-means basins; Bespo…"],
        [65, 2, "idea-65a86d", "Strategy basins base vs RL: blind LLM judge groups 32 samples per problem by method, 42 MATH-500 problems, base+cue vs…"],
        [65, 1, "work-4dfcf9", "Swarm idea map idea-1d9755: read-only over board + events, claude-CLI judge, map page. No GPU. Branch ali/strategy-basi…"],
        [95, 0, "result-47286f", "Swarm idea map (idea-1d9755), board at 21:36 UTC, 42 items, judge gpt-6.1-sol: 12 of 20 possible directions pursued (ju…"],
        [166, 0, "result-8c866c", "Swarm map main-02 (board 22:48 UTC, 72 items, gpt-6.1-sol): still 12 of 20 possible directions pursued, same 8 untouche…"],
        [188, 2, "idea-35c9d8", "Exploration-collapse testbed: reproduce Fork-and-Flush (2610.07447) vs single run vs best-of-4 at matched submissions o…"],
        [190, 1, "work-ff64d5", "Strategy basins idea-65a86d: base+cue vs RL, 32 samples x 42 MATH-500 problems, blind judge Qwen3-30B-A3B FP8, on Modal…"],
        [339, 1, "work-180a48", "Untouched direction 'alternative truncation rules': min-p on MATH-500, cue, T 1.0 (and T 1.5), base and RL with the sam…"],
        [357, 0, "result-15b095", "Paused before judging. Generations only: base+cue 272/336 (81.0%, 4,563 tok), RL 311/336 (92.6%, 5,026 tok), 21 MATH-50…"],
        [362, 1, "work-70152d", "Untouched direction 'draft-critique-revision': intrinsic self-review of the stored T 1.0 cue answers on MATH-500 (base…"],
        [396, 0, "result-44b4df", "No truncation rule beats untruncated sampling on MATH-500 at T 1.0 (cue, v3, n=500, paired vs same-seed min-p 0): base…"],
        [408, 0, "result-96e819", "Intrinsic self-review fixes no math on MATH-500 for base or RL (T 1.0 cue drafts, one review pass appended, v3, n=500,…"],
        [487, 1, "work-8cc441", "Basin Atlas, new landscape page (separate artifact, old pages untouched): the judge's idea map drawn as a 3D surface, b…"],
        [494, 0, "result-40e33a", "Basin Atlas Landscape page built (private artifact https://claude.ai/artifact/DuJgHJMvDg62WUo1arNQtt): main-02 map (72…"],
        [511, 1, "work-dfd055", "Basin Atlas Landscape, second design pass (same artifact): full-screen WebGL surface, far fewer marks and words. swarm_…"],
        [514, 0, "result-3f34dd", "Swarm map main-03 idea-1d9755 (board 04:08 UTC, 218 items, gpt-6.1-sol, same 20 possible directions): 16 of 20 directio…"],
        [518, 0, "result-467e1c", "Basin Atlas Landscape, second design (same private artifact https://claude.ai/artifact/DuJgHJMvDg62WUo1arNQtt): full-sc…"],
        [552, 1, "work-49fdd2", "Harness benchmark vs Karpathy autoresearch (commit 228791f): both arms on his task (5-min GPT training, val_bpb, Modal…"],
        [558, 0, "result-d3826a", "autobench built, not run: our harness vs Karpathy autoresearch (228791f) on his 5-min GPT task, equal experiment budget…"],
        [566, 1, "work-7e7d38", "autobench step 1 (SPEC1): deploy the Modal app autobench, prep data, one run of the unchanged Karpathy train.py under a…"],
        [578, 1, "work-947254", "autobench v2: Karpathy's loop (one agent, one file solve.py, keep or discard) on OUR task: base Olmo on MATH-500, grade…"],
        [587, 0, "result-a4845e", "autobench v2 built, not run: Karpathy's loop (1 agent, 1 file solve.py, keep/discard, 360 s generation per experiment)…"],
        [591, 1, "work-a0d758", "Basin atlas as a site page in the site-ui / finding-page look (glass slab, SVG, own projection): tools/proof_basin_atla…"],
        [605, 1, "work-9edc68", "autobench step 1 (SPEC2): deploy Modal app autobench, one run of the swarm cue config (solve_cue.py) on the 100 dev pro…"],
        [641, 1, "work-9abc35", "theory round 05 (engine v5.1 unchanged, cutoff 04:29:33 UTC, --from round-04; agreed with abaybektursun/theory on work-…"],
        [654, 0, "result-fa480f", "autobench pipeline check passes: swarm cue config through the Karpathy-arm runner scores 84 of 100 on the 100 dev MATH-…"],
        [654, 1, "work-ce7583", "autobench Karpathy arm running: one headless agent, 40 experiments on dev100 from the plain prompt (started 07:07 UTC,…"],
        [706, 2, "idea-44771d", "Theory round 05 rival (replaces r5-m03 'top-8 directions = the cue and nothing more'): the top-8 edit of the RL-Math we…"],
        [706, 2, "idea-2f32ff", "Theory round 05 rival (replaces r5-m10 'two whole answer modes chosen at the opening'): the cue's gain at T 1.0 is robu…"],
        [706, 2, "knowledge-1a0674", "Theory round 05, refuted theories (each by a number computed from stored rows; studies/theory/results/engine/round-05/m…"],
        [706, 0, "result-07f566", "Theory round 05 computed these numbers from stored rows"],
        [707, 0, "result-e0c365", "Theory round 05: one weak survivor, eleven theories refuted"],
        [775, 1, "work-a9a6dd", "theory round 06 (engine v6.3 unchanged, cutoff 06:51:23 UTC, --from round-05, --account-from account/run-03; go from ab…"],
        [906, 2, "idea-40d461", "Theory round 06 survivor, first one whose review says 'stands' (statement as in idea-44771d): the top-8 edit of the RL-…"],
        [906, 0, "result-c637b2", "Where the base loses to RL on MATH-500, split into six parts"],
        [906, 2, "knowledge-e387a8", "Theory round 06, refuted theories (numbers computed from stored rows and recomputed; studies/theory/results/engine/roun…"],
        [906, 0, "result-8b0706", "Theory round 06: the first theory that stands"],
        [1024, 0, "result-fec2c0", "closed by frustea after 86 idle minutes and no answer to the 13:02 UTC question (coordination rule 5); no round-07 file…"],
        [1024, 1, "work-466a39", "theory round 07, taken over from work-8fd317 (owner silent 86 min): plan studies/theory/specs/SPEC_round07.md by abaybe…"],
        [1078, 2, "idea-6fb0de", "Ideas from the Karpathy-loop agent (autobench, work-ce7583): one isolated agent, 40 experiments on 100 MATH-500 problem…"],
        [1080, 2, "knowledge-dbd18b", "Theory round 07 (engine 7.1), numbers computed from stored rows (studies/theory/results/engine/round-07/metrics_v4.json…"],
        [1081, 0, "result-5115c5", "Theory round 07: nothing new survives"],
        [1127, 1, "work-8cde9c", "Outside math and code: the Math cue on the base, RL-Zero-Math plain and Think-SFT + cue on 250 MMLU-Pro (non-STEM) + 25…"],
        [1144, 0, "result-6e7b64", "Karpathy's autoresearch loop does not beat the swarm's cue on unseen problems"],
        [1151, 0, "result-1a80e9", "The cue found on math also works outside math and code"],
        [1337, 0, "result-0f401d", "Three idea-map slides are live at /demo/ali/slide1"],
        [1376, 0, "result-58c66d", "Idea basins page is live"],
        [1390, 1, "work-21c6ee", "Add Ali's four slides to the /demo deck (tools/demo_deck.py, new tools/demo_results.py): accuracy climb as slide 2, Bey…"],
        [1403, 0, "result-726cfd", "Ali's four slides are in the /demo deck"],
        [1409, 1, "work-2ae4c8", "Refresh the idea basins and the best scores on the talk slides: judge (gpt-6.1-sol) on the board of 19:42 UTC (515 item…"],
        [1450, 0, "result-851e4e", "Idea basins and talk numbers refreshed on the 515-item board"],
        [1540, 1, "work-a4c315", "Deck slide sponsors (/demo#sponsors): add the recall-against-grep towers of /pastdev as a small third figure beside the…"],
        [1543, 1, "work-6afcf6", "Deck slide efficiency (/demo#efficiency): new title 'Benchmarking against Karpathy's autoresearch (100k stars on GitHub…"],
        [1545, 0, "result-105c31", "Deck slide efficiency has a new title"],
        [1549, 0, "result-a3d933", "Sponsors slide shows recall against grep"],
        [1554, 1, "work-448ac1", "Idea basins (/proof/idea-basins, deck /demo#ideas): rename five clusters from topic to the idea pursued (Team tools ->…"],
        [1573, 0, "result-4aefc5", "Idea basins: named by idea, GPU price basin left out"],
    ],
}


def page():
    esc = html.escape

    def person(p):
        c = COUNTS[p["login"]]
        extra = "".join(f"<div><dt>{label}</dt><dd>{esc(p[key])}</dd></div>" for key, label in FIELDS if p[key])
        links = "".join(f'<li><a href="{esc(href)}"><span>{esc(title)}</span><i aria-hidden="true">&rarr;</i></a></li>'
                        for title, href in p["results"])
        nums = "".join(f"<p><b>{c[key]:,}</b><span>{label}</span></p>" for key, label in
                       (("results", "results"), ("work", "work items"), ("ideas", "ideas and notes"), ("commits", "commits")))
        return (f'<section class="person hue" style="--h:{HUES[COUNTED["names"].index(p["login"]) % len(HUES)]}">'
                f'<h2>{esc(p["name"])}</h2>'
                f'<div class="id"><a class="gh" href="https://github.com/{esc(p["login"])}" rel="noopener">GitHub: {esc(p["login"])}</a>'
                f'{f"<dl>{extra}</dl>" if extra else ""}</div>'
                f'<p class="work">{esc(p["work"])}</p>'
                f'<div class="res"><p class="lab">Results</p><ul>{links}</ul></div>'
                f'<div class="nums" aria-label="Counts">{nums}</div></section>')

    fig = {"start": COUNTED["start_ns"] // 10**6, "span": COUNTED["span"],
           "people": [{"login": p["login"], "name": p["name"], "hue": HUES[COUNTED["names"].index(p["login"]) % len(HUES)],
                       "marks": MARKS[p["login"]]} for p in PEOPLE]}
    return (PAGE.replace("__PEOPLE__", "".join(person(p) for p in PEOPLE))
            .replace("__FIRST__", COUNTED["first"]).replace("__AT__", COUNTED["at"]).replace("__COMMIT__", COUNTED["commit"])
            .replace("__FIG__", json.dumps(fig, ensure_ascii=False).replace("</", "<\\/")))


def _title(text):
    lines = text.splitlines()
    title = " ".join(next((line[7:] for line in lines if line.startswith("title: ")), lines[0]).split())
    return title if len(title) <= 120 else title[:119].rstrip() + "…"


def _count(at_ns, commit):
    """COUNTED, COUNTS and MARKS from every board item posted up to at_ns and the commits reachable from commit."""
    import os
    import subprocess
    import sys
    from datetime import datetime
    from zoneinfo import ZoneInfo

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import board
    from boto3.dynamodb.conditions import Key

    items = [r for listed in board.KINDS + ("work-closed",)
             for r in board.rows(IndexName="new", KeyConditionExpression=Key("listed").eq(listed)) if int(r["at_ns"]) <= at_ns]
    authors = subprocess.run(["git", "log", "--no-merges", "--format=%ae", commit], capture_output=True, text=True, check=True).stdout.split()
    logins = [a.split("@")[0].split("+")[-1] for a in authors]  # the address is read here and never kept
    start = min(int(r["at_ns"]) for r in items)
    counts, marks = {}, {}
    for p in PEOPLE:
        mine = sorted((r for r in items if r["who"] == p["login"]), key=lambda r: int(r["at_ns"]))
        kinds = [KIND.get(r["kind"], 2) for r in mine]
        counts[p["login"]] = {"results": kinds.count(0), "work": kinds.count(1), "ideas": kinds.count(2),
                              "items": len(mine), "commits": logins.count(p["login"])}
        marks[p["login"]] = [[(int(r["at_ns"]) - start) // (60 * 10**9), k, r["id"], _title(r["text"])] for r, k in zip(mine, kinds)]
    sf = lambda ns: datetime.fromtimestamp(ns / 1e9, ZoneInfo("America/Los_Angeles"))
    when = lambda ns: f"{sf(ns):%H:%M} on {sf(ns).day} {sf(ns):%B}"
    counted = {"names": sorted({r["who"] for r in items}), "start_ns": start, "at_ns": at_ns, "span": (at_ns - start) // (60 * 10**9),
               "commit": commit, "first": when(start), "at": when(at_ns)}
    return counted, counts, marks


if __name__ == "__main__":  # run from the repository root: uv run tools/people.py [--write]
    import subprocess
    import sys
    import time

    if sys.argv[1:] == ["--write"]:
        head = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        counted, counts, marks = _count(time.time_ns(), head)
        src = open(__file__).read()
        rows = lambda m: "{\n" + "".join(f'    "{k}": [\n' + "".join("        " + json.dumps(r, ensure_ascii=False) + ",\n" for r in v) + "    ],\n"
                                         for k, v in m.items()) + "}"
        for name, text in (("COUNTED", json.dumps(counted)), ("COUNTS", json.dumps(counts)), ("MARKS", rows(marks))):
            start = src.index(f"\n{name} = ") + 1
            src = src[:start] + f"{name} = {text}" + src[src.index("\n\n", start):]
        open(__file__, "w").write(src)
        sys.exit(f"wrote the counts of {sum(c['items'] for c in counts.values())} board items at {counted['at']}, commit {head}")
    assert _count(COUNTED["at_ns"], COUNTED["commit"]) == (COUNTED, COUNTS, MARKS), "COUNTED, COUNTS or MARKS differ: run with --write"
    print(f"COUNTED, COUNTS and MARKS match the board up to {COUNTED['at']} and git at {COUNTED['commit']}")


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Team</title>
<meta name="description" content="Invariant is three people and their coding agents at the SF AI Research Hackathon: who they are, what each worked on, and every item they posted to the team board.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the type of home.py and architecture.py. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de; --blue: #1f43d6;
  --pl: .50; --pc: .15; --dim: .22;
}
@media (prefers-color-scheme: dark) {
  :root { --paper: #080c11; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630; --blue: #8fb1ff; --pl: .78; --pc: .13; --dim: .26; }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.hue { --c: oklch(var(--pl) var(--pc) var(--h)); }
.page { max-width: 1840px; margin: 0 auto; padding: 20px 40px 64px; }
.top { display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }

.cap { margin: clamp(30px, 7vh, 76px) 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 28ch; text-wrap: balance; }
.sub { margin: 14px 0 0; max-width: 62ch; font-size: 14.5px; line-height: 1.45; color: var(--mute); }

/* The three people: one column each, their rows aligned across the columns */
.people { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-template-rows: repeat(5, auto); column-gap: 48px; margin-top: clamp(32px, 6.5vh, 68px); }
.person { grid-row: span 5; display: grid; grid-template-rows: subgrid; }
h2 { margin: 0; padding-bottom: 14px; border-bottom: 1px solid var(--rule); font-size: clamp(30px, 2.7vw, 48px); line-height: 1.04; font-weight: 300; letter-spacing: -.02em; }
.id { padding: 11px 0 0; font-size: 13px; }
.gh { display: inline-flex; align-items: center; gap: 9px; color: var(--mute); text-decoration: none; transition: color .15s ease; }
.gh::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--c); }
.gh:hover { color: var(--ink); }
.id dl { margin: 8px 0 0; }
.id dl div { display: grid; grid-template-columns: 5.6em minmax(0, 1fr); column-gap: 12px; padding: 4px 0; }
.id dt { font-weight: 600; color: var(--mute); }
.id dd { margin: 0; }
.work { margin: 0; padding: 16px 0 24px; max-width: 50ch; font-size: 15px; line-height: 1.52; text-wrap: pretty; }
.lab { margin: 0 0 6px; font-size: 12.5px; font-weight: 600; color: var(--mute); }
.res ul { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.res a { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; padding: 9px 0; border-bottom: 1px solid var(--rule); text-decoration: none; font-size: 14.5px; }
.res i { font-style: normal; color: var(--faint); transition: transform .3s cubic-bezier(.3, 0, .2, 1), color .3s ease; }
.res a:hover i { transform: translateX(4px); color: var(--ink); }
.res a:focus-visible { outline-offset: -2px; }
.nums { display: grid; grid-template-columns: repeat(4, auto); justify-content: start; column-gap: clamp(18px, 2vw, 34px); padding-top: 22px; align-self: start; }
.nums p { margin: 0; display: flex; flex-direction: column; }
.nums b { font-size: clamp(24px, 1.9vw, 30px); line-height: 1.05; font-weight: 300; letter-spacing: -.02em; }
.nums span { margin-top: 3px; font-size: 12.5px; color: var(--mute); white-space: nowrap; }

/* The picture: every board item of the three on one time axis */
.fig { margin: clamp(48px, 9vh, 96px) 0 0; padding-top: 16px; border-top: 1px solid var(--rule); }
.fhead { display: flex; align-items: baseline; justify-content: space-between; gap: 8px 32px; flex-wrap: wrap; }
.ft { margin: 0; font-size: 15px; font-weight: 600; font-stretch: 104%; }
.fs { margin: 2px 0 0; font-size: 13.5px; color: var(--mute); max-width: 80ch; }
.key { display: flex; gap: 18px; margin: 0; font-size: 13px; color: var(--mute); }
.key span { display: inline-flex; align-items: center; gap: 7px; white-space: nowrap; }
.key svg { overflow: visible; }
.key circle { fill: var(--mute); }
.key .k1 { fill: none; stroke: var(--mute); stroke-width: 1.3; }
.key .k2 { opacity: .6; }
.plot { position: relative; margin-top: 18px; }
#strips { display: block; width: 100%; overflow: visible; cursor: pointer; -webkit-tap-highlight-color: transparent; }
#strips text { font-family: inherit; font-size: 12px; fill: var(--mute); }
#strips .who { font-size: 13px; font-weight: 620; font-stretch: 104%; fill: var(--c); }
#strips .hr { stroke: var(--rule); stroke-width: 1; }
#strips .day { stroke: var(--mute); stroke-width: 1; opacity: .45; }
#strips .base { stroke: var(--rule); stroke-width: 1; }
#strips .frame { fill: none; stroke: transparent; stroke-width: 2; rx: 4; }
#strips .row:focus { outline: none; }
#strips .row:focus-visible .frame { stroke: var(--blue); }
.mk { fill: var(--c); transition: opacity .3s ease; }
.mk.k1 { fill: none; stroke: var(--c); stroke-width: 1.3; }
.mk.k2 { opacity: .62; }
#strips.picked .mk { opacity: var(--dim); }
#strips.picked .mk.on { opacity: 1; }
#ring { fill: none; stroke: var(--ink); stroke-width: 1.4; pointer-events: none; }
.enter .mk { animation: rise .7s cubic-bezier(.2, .8, .2, 1) both; animation-delay: calc(var(--d) * 1ms); transform-box: fill-box; transform-origin: center; }
@keyframes rise { from { opacity: 0; transform: translateY(6px) scale(.3); } }
.detail { margin: 14px 0 0; padding-top: 10px; border-top: 1px solid var(--rule); min-height: 4.4em; font-size: 14px; line-height: 1.5; }
.detail .hint { color: var(--mute); }
.detail b { font-weight: 620; color: var(--c); margin-right: 10px; }
.detail .meta { color: var(--mute); margin-right: 10px; white-space: nowrap; }
.detail .t { margin-right: 10px; }
.detail a { color: var(--blue); text-underline-offset: 3px; white-space: nowrap; }
.note { margin: 36px 0 0; max-width: 92ch; font-size: 13px; line-height: 1.5; color: var(--mute); }

@media (max-width: 900px) {
  .page { padding: 6px 16px 40px; }
  .top { gap: 0 13px; padding-bottom: 2px; flex-wrap: wrap; }
  .top a { display: inline-flex; align-items: center; min-height: 40px; }
  .name { font-stretch: 112%; margin-right: 0; }
  .cap { margin-top: 26px; font-size: 25px; }
  .people { grid-template-columns: 1fr; grid-template-rows: none; row-gap: 44px; margin-top: 34px; }
  .person { grid-row: auto; grid-template-rows: none; }
  .work { max-width: none; padding-bottom: 20px; }
  .res a { padding: 11px 0; }
  .nums { grid-template-columns: repeat(2, auto); row-gap: 14px; column-gap: 40px; }
  .key { gap: 14px; flex-wrap: wrap; }
}
@media (prefers-reduced-motion: reduce) {
  .enter .mk { animation: none; }
  .mk, .res i, .gh { transition: none; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/proof">Proof</a>
    <a href="/findings">Findings</a>
  </header>
  <p class="cap">Invariant is three people and their coding agents at the SF AI Research Hackathon.</p>
  <p class="sub">The items and commits counted under each name were written by that person and their Claude Code agents.</p>
  <div class="people">__PEOPLE__</div>
  <figure class="fig" id="fig">
    <figcaption class="fhead">
      <div><p class="ft">Every item the three posted to the team board</p>
      <p class="fs">One mark per item, by the time it was posted, from __FIRST__ to __AT__ (San Francisco time).</p></div>
      <p class="key" aria-hidden="true">
        <span><svg width="8" height="8"><circle cx="4" cy="4" r="3.6"/></svg>Result</span>
        <span><svg width="8" height="8"><circle class="k1" cx="4" cy="4" r="3"/></svg>Work item</span>
        <span><svg width="8" height="8"><circle class="k2" cx="4" cy="4" r="2.2"/></svg>Idea or note</span>
      </p>
    </figcaption>
    <div class="plot"><svg id="strips" aria-label="Board items of each person over time. Focus a row and use the arrow keys to step through its items."></svg></div>
    <p class="detail" id="detail" aria-live="polite"></p>
  </figure>
  <p class="note">Counted at __AT__ (San Francisco time). Board items are every kind on the team board, open or closed; ideas and notes include knowledge and skill items. Commits are those in the history of the site's code at commit __COMMIT__, merges left out, matched to each person by the GitHub login in the commit's author address.</p>
</div>
<script>
const D = __FIG__;
const $ = id => document.getElementById(id), svg = $("strips"), detail = $("detail");
const NS = "http://www.w3.org/2000/svg", KINDS = ["Result", "Work item", "Idea or note"];
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
const sf = (o) => new Intl.DateTimeFormat("en-GB", { timeZone: "America/Los_Angeles", hourCycle: "h23", ...o });
const clock = sf({ hour: "2-digit", minute: "2-digit" }), stamp = sf({ day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" });
const dayName = sf({ day: "numeric", month: "long" }), hourOf = sf({ hour: "numeric" });
const byId = new Map();
let L = null, sel = null, first = true;

/* Layout: the axis spans the hours of the board; marks stack in time bins whose width fits the screen */
function layout() {
  const W = Math.round(svg.parentNode.clientWidth), narrow = W < 640;
  const binMin = [5, 10, 15, 20, 30, 60, 120].find(s => D.span / s <= W / (narrow ? 5 : 8.5)) || 120;
  const bw = W * binMin / D.span, r = Math.max(2, Math.min(3.4, bw * .36)), pitch = 2 * r + Math.max(1.2, r * .45);
  let y = 0;
  const rows = D.people.map((p, pi) => {
    const fill = new Map();
    const marks = p.marks.map(([m, k, id, t]) => ({ m, k, id, t, pi })).sort((a, b) => a.k - b.k || a.m - b.m);
    for (const d of marks) { d.b = Math.floor(d.m / binMin); d.s = fill.get(d.b) || 0; fill.set(d.b, d.s + 1); }
    const top = y + 30, h = Math.max(...fill.values()) * pitch;
    for (const d of marks) { d.x = Math.min(W - r, (d.b + .5) * bw); d.y = top + h - (d.s + .5) * pitch; d.r = d.k === 2 ? r * .62 : d.k === 1 ? r - .55 : r; }
    marks.sort((a, b) => a.m - b.m || a.k - b.k);
    marks.forEach((d, i) => { d.i = i; byId.set(d.id, d); });
    y = top + h + 26;
    return { p, top, h, marks };
  });
  return { W, H: y - 26 + 40, rows, r, narrow, x: m => m / D.span * W };
}

function draw() {
  L = layout();
  const { W, H, rows, narrow, x } = L, out = [];
  // hour lines through every row; midnight a little stronger and named; a clock label every 3 hours (6 on a phone)
  const t0 = D.start, every = narrow ? 6 : 3, wide = s => s.length * 6.6;  // a label's width at 12 px, so labels never touch
  let right = wide(dayName.format(t0));
  out.push(`<text x="0" y="${H - 12}">${dayName.format(t0)}</text>`);
  for (let ms = Math.ceil(t0 / 3600000) * 3600000; ms <= t0 + D.span * 60000; ms += 3600000) {
    const m = (ms - t0) / 60000, X = x(m), h = +hourOf.format(ms), mid = h === 0, s = mid ? dayName.format(ms) : clock.format(ms);
    out.push(`<line class="${mid ? "day" : "hr"}" x1="${X.toFixed(1)}" x2="${X.toFixed(1)}" y1="${rows[0].top - 4}" y2="${H - 30}"/>`);
    if (h % every === 0 && X - wide(s) / 2 > right + 12 && X + wide(s) / 2 < W) {
      out.push(`<text x="${X.toFixed(1)}" y="${H - 12}" text-anchor="middle">${s}</text>`);
      right = X + wide(s) / 2;
    }
  }
  for (const [pi, R] of rows.entries()) {
    out.push(`<g class="row hue" data-pi="${pi}" tabindex="0" role="group" aria-label="${esc(R.p.name)}, ${R.marks.length} board items" style="--h:${R.p.hue}">` +
      `<rect class="frame" x="-6" y="${R.top - 26}" width="${W + 12}" height="${R.h + 32}"/>` +
      `<text class="who" x="0" y="${R.top - 12}">${esc(R.p.name)}<tspan dx="10" style="fill:var(--mute);font-weight:400">${R.marks.length} items</tspan></text>` +
      `<line class="base" x1="0" x2="${W}" y1="${R.top + R.h + .5}" y2="${R.top + R.h + .5}"/>` +
      R.marks.map(d => `<circle class="mk k${d.k}" data-id="${d.id}" cx="${d.x.toFixed(1)}" cy="${d.y.toFixed(1)}" r="${d.r.toFixed(2)}" style="--d:${Math.round(d.x / W * 1500 + d.s * 6)}"/>`).join("") +
      `</g>`);
  }
  out.push(`<circle id="ring" r="0" cx="-20" cy="-20"/>`);
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("height", H);
  svg.classList.toggle("enter", first && !still); first = false;
  svg.innerHTML = out.join("");
  show();
}

/* The selection: one item, in the address */
function show() {
  const d = sel && byId.get(sel);
  svg.classList.toggle("picked", Boolean(d));
  svg.querySelectorAll(".mk.on").forEach(e => e.classList.remove("on"));
  const ring = $("ring");
  if (!d) {
    ring.setAttribute("r", 0);
    detail.innerHTML = `<span class="hint">Click a mark to read the item it stands for. On a focused row, the arrow keys step through the items.</span>`;
    return;
  }
  svg.querySelector(`.mk[data-id="${CSS.escape(d.id)}"]`)?.classList.add("on");
  ring.setAttribute("cx", d.x.toFixed(1)); ring.setAttribute("cy", d.y.toFixed(1)); ring.setAttribute("r", (L.r + 3.2).toFixed(1));
  const p = D.people[d.pi];
  detail.innerHTML = `<span class="hue" style="--h:${p.hue}"><b>${esc(p.name)}</b></span><span class="meta">${KINDS[d.k]}, ${stamp.format(D.start + d.m * 60000)}</span>` +
    `<span class="t">${esc(d.t)}</span><a href="/#${encodeURIComponent(d.id)}">Open on the board</a>`;
}
function pick(id, push) {
  sel = id;
  const url = location.pathname + location.search + (id ? "#" + id : "");
  if (push) history.pushState(null, "", url); else history.replaceState(null, "", url);
  show();
}
addEventListener("hashchange", () => { sel = byId.has(location.hash.slice(1)) ? location.hash.slice(1) : null; show(); });

// a click picks the nearest mark within 16 px: a generous hit area for marks a few pixels wide
svg.addEventListener("click", e => {
  const b = svg.getBoundingClientRect(), px = (e.clientX - b.left) * L.W / b.width, py = (e.clientY - b.top) * L.W / b.width;
  let best = null, bd = 16 * 16;
  for (const R of L.rows) for (const d of R.marks) { const q = (d.x - px) ** 2 + (d.y - py) ** 2; if (q < bd) { bd = q; best = d; } }
  if (best) { pick(best.id === sel ? null : best.id, true); svg.querySelector(`.row[data-pi="${best.pi}"]`)?.focus({ preventScroll: true }); }
  else if (sel) pick(null, true);
});
svg.addEventListener("keydown", e => {
  const g = e.target.closest?.(".row");
  if (!g) return;
  const pi = +g.dataset.pi, R = L.rows[pi], cur = sel && byId.get(sel);
  const at = cur ? cur.m : null, near = (marks, m) => marks.reduce((a, d) => Math.abs(d.m - m) < Math.abs(a.m - m) ? d : a);
  let to = null;
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
    const step = e.key === "ArrowRight" ? 1 : -1;
    to = cur && cur.pi === pi ? R.marks[Math.max(0, Math.min(R.marks.length - 1, cur.i + step))] : at !== null ? near(R.marks, at) : R.marks[step > 0 ? 0 : R.marks.length - 1];
  } else if (e.key === "Home") to = R.marks[0];
  else if (e.key === "End") to = R.marks[R.marks.length - 1];
  else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    const R2 = L.rows[pi + (e.key === "ArrowDown" ? 1 : -1)];
    if (!R2) return;
    e.preventDefault();
    svg.querySelector(`.row[data-pi="${L.rows.indexOf(R2)}"]`).focus();
    if (at !== null) pick(near(R2.marks, at).id, false);
    return;
  } else if (e.key === "Enter" && cur) { e.preventDefault(); location.href = "/#" + encodeURIComponent(cur.id); return; }
  else if (e.key === "Escape" && cur) { e.preventDefault(); pick(null, true); return; }
  else return;
  e.preventDefault();
  pick(to.id, false);
});
addEventListener("keydown", e => { if (e.key === "Escape" && sel && !e.target.closest?.(".row")) pick(null, true); });

let lastW = Math.round(svg.parentNode.clientWidth);  // the first draw is below; the observer redraws only when the width changes
new ResizeObserver(() => { const w = Math.round(svg.parentNode.clientWidth); if (w !== lastW) { lastW = w; draw(); } }).observe(svg.parentNode);
draw();
sel = byId.has(location.hash.slice(1)) ? location.hash.slice(1) : null;
show();
</script>
</body>
</html>
"""
