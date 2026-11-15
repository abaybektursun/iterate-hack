"""The team's one account of what RL changed, and how its new claims held: 6 of 9 in round 15.

The page of one finding, served at /finding/one-account-of-the-facts (view.py serves every tools/finding_<slug>.py) and
reached from its tile on /findings, which ICON draws. It is the fourth page about the team's theory engine
(.claude/skills/theory/SKILL.md, studies/theory/README.md, section Round 15): tools/finding_mechanisms_tested_directly.py
shows the one-sentence causes written per surprising number and tested directly, tools/finding_theories_on_trial.py
scores the engine's theories on their predictions. In round 15 three agents, blind to each other, each wrote one account
of all 42 directly tested facts, and each named 3 new consequences checkable on stored data, with its range and the
null's range fixed before the check. A judge listed the points where the accounts disagree (one) and a test for each.

The picture is one lit plate. The account that scored best, account 2, stands in the middle as six plain sentences
(NODES, written for this page from the six sentences of account-2.json; the verbatim text opens on a click). Beside
each sentence hang the new claims that test it, each one row: the measured value and its 90 % interval on a small
axis, against the account's range (filled) and the null's range (dashed). A small column of three dots beside each
sentence says which accounts state it. The control (Account 1, Account 2, Account 3, and a quiet "Where they
disagree") keeps every shared sentence still: only the clause where an account differs changes, and the deciding
test of the one disagreement replays, its value travelling from the null into account 2's range, outside account 1's.
A click on a sentence or a claim opens it in the side column. Address: /finding/one-account-of-the-facts#<a1|a3|split,
or nothing for account 2>/<panel, s1 to s6, or a claim: a1c1 ... a3c3, d1>. The rules are in
.claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py (.claude/skills/site-ui/SKILL.md).

    uv run tools/finding_one_account_of_the_facts.py                            checks RECORD against the working tree
    uv run tools/finding_one_account_of_the_facts.py --ref origin/theory        checks RECORD against the files at a ref
    uv run tools/finding_one_account_of_the_facts.py --write [--ref origin/theory]   rewrites RECORD, REF and COMMIT

Without --ref the check compares with the working tree only when it holds round 15's files; otherwise it says the
comparison was skipped (round 15 is on branch theory while main is frozen). The deployed site ships only tools/*.py,
so the page reads nothing from studies/ at run time: RECORD is the copy.
"""
import json
import os
import pprint
import re
import subprocess
import sys

R = "studies/theory/results/"
W = R + "wide/round-15/"
FILES = [R + "direct_tested.json", R + "refuted.json"]

TITLE = "One account of the facts"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Does one story of what RL changed survive new checks on stored data?"

DATA = {
    "sources": {
        "accounts": W + "account-1.json, account-2.json, account-3.json (sentences, fact marks, consequences)",
        "plans": W + "synthesis_tests.json (claim, statistic, null, ranges fixed before each test); disagreements.json "
                     "(the judge's file)",
        "scores": W + "synthesis.md (the table this page's counts are checked against)",
        "record": R + "direct_tested.json and refuted.json (verdict, measured, board item of every test)",
        "tests": R + "direct/<test>/metrics.json (value, 90 % interval, n); specs studies/theory/specs/SPEC_direct_*.md",
        "plain words": "NODES, CLAUSES and TESTS below, written for this page",
    },
}

# The story: account 2's six sentences, one plain sentence each, in order. With each: the sentences of account 1 and of
# account 3 that state the same (numbers of their sentences in account-<k>.json), and how each account stands on it:
# "same" (states it too), "other" (states otherwise), "none" (takes no side).
NODES = [
    ["RL on the model's own answers concentrates its small weight change in 8 directions per matrix that the base "
     "already uses; at 1.5 times, those 8 alone match RL.", [1, 2], [1, 4], "same", "same"],
    ["The change does two things: it opens answers in a deliberate style, learned mostly in RL's first 100 steps, and "
     "then it makes wrong steps rarer and lets answers finish.", [2, 3], [2, 4], "same", "same"],
    ["The opening needs no RL weights: a three-token cue gives it to the base, and the cue alone reaches 78 % of RL's "
     "gain on MATH-500.", [3], [4], "same", "same"],
    ["Rarer wrong steps come only from sampling again: the base's mistakes are one-off, not shared, so a vote over "
     "about 6 base samples matches one RL sample.", [4], [3, 4], "same", "same"],
    ["On the 328 harder problems, most of RL's extra right answers fall where Base + cue has no right answer in 4 "
     "samples, and inference cannot reach them;", [5, 6], [5], "other", "none"],
    ["The directions act on the domain whose reward trained them: on code, Math's directions add +1.5 points of pass "
     "rate, Code's +7.0.", [6], [6], "same", "same"],
]
# Sentence 5 ends differently by account: the one point the judge found (disagreement d1). Account 3 takes no side.
CLAUSES = {
    "2": "and the 8 directions win them about as often as RL.",
    "1": "and the 8 directions win only a minority of them.",
    "3": "Account 3 takes no side on what the 8 directions do there.",
}
# Account 3's one claim the others do not make, beside sentence 6; it marks one fact (F26) as against it.
EXTRA3 = ["Account 3 adds: finishing sits in direction 1, right answers in directions 2 to 8.",
          "It marks fact F26 as against this."]

# One entry per test of round 15 (the 9 new consequences and the judge's disagreement d1), written for this page:
#   [short label, the sentence it tests (1 to 6), test folder under results/direct/, key of the value in its
#    metrics.json, key of its 90 % interval, key of n, what n counts, key of the null's measured value or "",
#    unit of the value ("" for a plain ratio or share, "points"), axis domain [low, high] or None, caveat]
TESTS = {
    "round-15/account-1/c1": [
        "Code-RL sits in Math's directions", 1, "hostcap-01", "value", "ci90", "n_matrices", "matrices", "", "",
        [0, 8],
        "Code's change also sits 2.13 times Think-SFT's in IF-RL's directions and 1.78 times in the base matrix's own "
        "top 8, so the ratio is not specific to Math's directions; the null (equal to Think-SFT) is weak."],
    "round-15/account-1/c2": [
        "IF and Math concentrate alike", 1, "sharerho-01", "D", "D_ci90", "n", "matrices", "", "", None,
        "The value lies below the null's range too: Math's pattern across matrices follows Think-SFT's (0.594), not "
        "IF-RL's (−0.010)."],
    "round-15/account-3/c2": [
        "8 directions' vote over 4 equals RL's", 1, "editvote-01", "order_averaged.statistic_points",
        "order_averaged.interval90", "n", "problems", "order_averaged.null_points", "points", None,
        "With ties broken in the stored order the difference is −2.13 points (90 % interval −4.57 to 0.3), also inside "
        "the range; the posted 214 against 221 of 328 is that version."],
    "round-15/account-2/c2": [
        "Step 100 gains from votes like the base", 2, "s100vote-01", "G_points", "ci90", "n", "problems",
        "context_final_rl.order_averaged.G_points", "points", None,
        "Base + cue gains as much (+7.55 points), as the account says; 1.85 of the 7.18 points come from problems where "
        "cut-off answers cast no vote and no wrong answer was written."],
    "round-15/account-3/c3": [
        "Step 100 answers as long as the base's", 2, "s100len-01", "step100_vs_cued_base.value",
        "step100_vs_cued_base.ci90", "step100_vs_cued_base.n_problems", "problems",
        "null_final_rl_vs_cued_base.value", "", None,
        "The value, 1.147, sits just below the null's range (1.15 to 1.60) and its interval reaches into it: step 100's "
        "right answers are already about 15 % longer than Base + cue's."],
    "round-15/account-3/c1": [
        "Own deliberate opening equals the cue", 3, "t3open-01", "value", "ci90", "n", "problems",
        "null_value_unflagged", "", None,
        "Which plain answers open deliberately is read from those answers' own first 240 characters."],
    "round-15/account-2/c1": [
        "Wrong answers scatter on hard problems too", 4, "merge328-01", "D", "ci90", "n", "problems", "", "", None,
        "88 problems (the plan said about 110); the difference comes only from problems with 1 or 2 right samples of 4."],
    "round-15/account-2/c3": [
        "8 directions equal RL where base gets 0 of 4", 5, "edit0of4-01", "D", "ci90", "n_problems", "problems",
        "null_value", "", None,
        "The measured null, −0.097, lies between the null's range and the account's range, 0.02 below the account's "
        "edge, so the test separates less than planned. Base + cue fails these problems mostly by being cut off. The "
        "engine-16 retest (result-61c569) counts it as the same measurement as d1, on the same rows, and gives it no "
        "row of its own."],
    "round-15/d1": [
        "8 directions' share of RL's gain there", 5, "editreach-02", "S", "S_ci90", "n_problems",
        "problems", "", "", None,
        "Base + cue fails these problems mostly by being cut off at 16,384 tokens (234 of its 480 samples; the edit 61, "
        "RL 89), so much of the edit's gain there is finishing. The first run read only 102 of the 121 problems (a "
        "loop over ids 0 to 327 while the ids run to 399); this is the rerun."],
    "round-15/account-1/c3": [
        "8 directions keep base answers where RL fails", 5, "rlfail-01", "value", "ci90", "n_edit_samples", "samples",
        "", "", None,
        "Only 6 right base samples and 12 right edit samples; about 990 edit samples would decide."],
}
TEST_ORDER = list(TESTS)  # the order of the rows in the picture

# Written by --write from the files at REF: the accounts, the plans, the measured values and the record's verdicts.
RECORD = {'facts': 42,
 'accounts': {'1': {'sentences': ["RL's weight change is 0.24 % of the weight norm, and about 12 % of its square "
                                  'sits in 8 input-to-output direction pairs per matrix (0.5-0.8 % for noise) whose '
                                  "inputs are directions the base's own text already drives strongly (8-11x a random "
                                  "subspace; code text drives Math's inputs 0.87 as much as math text); because RL "
                                  "trains on the model's own samples, every reward concentrates this way (top-8 "
                                  'share 0.12-0.21 for Math, Code, IF and LM-judge RL against 0.03 for Think-SFT, '
                                  'whose diffuse change still lies along the same base-driven inputs).',
                                  'Added to the base, the pairs act as one graded shift on every sample, not a '
                                  'per-sample lottery: they switch the base into its own deliberate-then-commit mode '
                                  "(open with 'Okay', more hold-on words, finish and state the answer in the task's "
                                  'format) and make its scattered slips rarer on problems it can already solve, so '
                                  'the 1.5x edit matches RL (MATH-500 456 vs 457, hard328 200.25 vs 200.0) and even '
                                  'its short answers are right.',
                                  "The base already contains the switch: a 3-token opening, its own 'Okay' openings "
                                  'drawn at T 1.0, or a one-tensor hand edit turn it on per prompt (MATH-500 224 to '
                                  '410, RL 463), which is about what the first 100 RL steps learn, still '
                                  "incompletely (step 100 plain 418 with the cued base's cap-hit rate, and the cue "
                                  "still adds 8.5), giving about 78 % of RL's gain on MATH-500 and 53-77 % on code "
                                  'and general questions.',
                                  'What remains is reliability: 81 % of the MATH-500 gap lies on problems the base '
                                  'solves in at least 1 of 4 samples, and its wrong answers there are split slips '
                                  '(same-problem wrong pairs agree 26 %, not one attractor value), so a plurality '
                                  "vote over about 6 cued samples recovers it (456.6 against one RL sample's "
                                  '456-463).',
                                  'Inference cannot add solves the base never samples: on hard328 the vote only '
                                  'narrows the gap (195 vs 224) because the base has no right sample within the '
                                  "16,384-token cap on 26 of RL's 36 vote wins, at T 0.6 the switched base loops "
                                  'instead (52-63 % of its answers past 4,096 tokens), and a 4,096 cap cuts its '
                                  'right routes, which are longer.',
                                  "The pairs carry the shared shift, not RL's problem-specific choices: Code-RL's "
                                  "pairs raise code correctness where Math's barely do (the output side is "
                                  "reward-specific although the inputs are driven by any text), the edit's code "
                                  'fixes are problems the base solves in other samples, and on problems RL fails but '
                                  "the base passes the edit passes at the base's own resample rate."],
                    'marks': {'explained': 27, 'not addressed': 15, 'contradicts': 0},
                    'facts': 42,
                    'contradicts': []},
              '2': {'sentences': ['RL-Zero-Math changes the base by 0.24 % of its weight norm, with 12 % of that '
                                  "change in 8 paired input-output directions per matrix that lie in the base's own "
                                  'most-driven activation directions; any on-policy RL reward concentrates this way '
                                  '(LM-judge General-RL top-8 share 0.127, Math 0.135, imitation-only Think-SFT '
                                  '0.030) because the update only re-weights text the base already writes, and those '
                                  '8 pairs at 1.5x alone match RL (456 vs 457 of 500 on MATH-500, 200.25 vs 200.0 on '
                                  'hard328) while random, unpaired or Think-SFT directions of equal norm do nothing.',
                                  "The re-weighting does two things to the base's token habits: it opens the answer "
                                  "in deliberation mode ('Okay', 'Wait'), which RL learns mostly in its first 100 "
                                  'steps (step 100 plain 418 vs cued base 410, same cap-hit rate), and it then '
                                  'lowers the per-step slip rate and lets a finished derivation wrap up (step 100 to '
                                  'final +45 of 500, cap hits -2.9 points, RL half as likely as the base to write '
                                  "the base's own wrong step).",
                                  'The opening is fully available at inference: a three-token cue (224 to 410 of '
                                  '500), a self-opened draw (411) or a one-tensor hand edit that writes the cue '
                                  '(397) gives it with no RL weights, which is why the cue alone reaches 78 % of '
                                  "RL's MATH-500 gain and the same Math cue works on code and on general questions.",
                                  'The slip part is available only by resampling, and resampling works because the '
                                  "base's slips are independent one-off events, not shared attractors (same-problem "
                                  'wrong-pair agreement 0.26 vs 0.005 by chance; merging the wrong answers costs a '
                                  '4-vote 0.07): where chains are short the base already writes the right answer in '
                                  "some samples (81 % of RL's MATH-500 gain on problems it solves at least 1 in 4; "
                                  '75 % of Code-edit fixes passed in another base sample, the edit keeping base '
                                  "passes only at a base resample's rate), so a vote over about 6 base samples "
                                  'matches one RL sample.',
                                  'Because a lower slip rate compounds over chain length, on long hard328 '
                                  "derivations RL's extra right answers fall where the base has no right sample in 4 "
                                  '(26 of 36 vote wins), and neither more tokens nor restarts buy them, since the '
                                  "base's long answers are loops at T 0.6 (52 %) or unsolved cap hits at T 1.0 (+1.2 "
                                  'points at a 32k cap), so inference stops 8.8 points [5.5, 12.5] short of RL '
                                  'there.',
                                  'The pairs act per domain on what the reward paid for, not by how strongly a text '
                                  "drives their inputs: Math's directions, driven 87 % as much by code text as by "
                                  "math, add only +1.5 points to code pass rate against Code's +7.0 and neither box "
                                  'code nor drop its block, and answer-format habits (no box, no fence) sit on '
                                  'problems of average difficulty, not on failures to solve.'],
                    'marks': {'explained': 35, 'not addressed': 7, 'contradicts': 0},
                    'facts': 42,
                    'contradicts': []},
              '3': {'sentences': ["RL's weight change is small (0.24 % of the weight norm), and the part that "
                                  'matters sits in 8 paired input-output singular directions per matrix (about 12 % '
                                  "of its squared norm). The base's own activations already drive these directions "
                                  '8-11x more than a random subspace, and code text drives them 87 % as strongly as '
                                  "math text. Because on-policy RL takes its gradient from the base's own samples, "
                                  'any reward piles the change into them (LM-judge top-8 share 0.127 against Math '
                                  '0.135), while imitating outside traces spreads its change (Think-SFT 0.030) but '
                                  'still overlaps them (4.8x chance).',
                                  'These directions add no new solution routes. Problem by problem, they re-weight '
                                  "the base's own sampling distribution toward the deliberate 'Okay ... Wait' mode "
                                  'the base already has, and toward finishing that mode instead of looping or '
                                  'running to the cap. A prompt, template or edit can only choose among modes the '
                                  'weights already hold, and answer layout (boxed endings, code fences) is a surface '
                                  'habit that does not depend on difficulty and is not what the directions carry.',
                                  "The shift raises each problem's chance of success; it does not switch a whole "
                                  'sample over. So its gains fall on problems the base already solves in other '
                                  'samples (81 % of the MATH-500 sample gap, 75 % of code fixes). Short answers stay '
                                  "the base's short right answers (83 % right; 41 % of right answers are "
                                  "plain-short, null 0.50), leftover errors keep the base's mix and difficulty, and "
                                  'on problems that RL itself fails the edit passes at the rate of a base resample '
                                  '(0.45 against 0.435).',
                                  'Inference-only changes move the same probability, so they reach the same share of '
                                  "RL's gain. The 3-token cue or a self-opened 'Okay' draw selects the mode (410 "
                                  "against 224 of 500, with RL at 463: 78 %; equal to RL step 100's 418 with the "
                                  "same cap-hit rate; 53-77 % of RL's gain on code and MMLU/BBH). Later RL steps, or "
                                  'the top-8 edit at 1.5x, add the finishing and match RL (456 against 457; 200.25 '
                                  'against 200.0 on hard328); the edit needs 1.5x because the other 88 % of the '
                                  'change carries an overlapping part of the gain. Votes recover reliability because '
                                  "the base's wrong answers are split (same-problem agreement 0.26, merging them "
                                  'costs 0.07 per problem), so a minority right answer can win, and 6 votes reach '
                                  'one RL sample.',
                                  'Inference cannot reach the part of the gap where the base has no right sample: on '
                                  "hard328 the base has none on 26 of the 36 problems that RL's vote wins, and its "
                                  "long unsolved answers guess, like RL's capped boxes (6 % right). Caps and low "
                                  'temperature also lose the long right routes the base does have (median right '
                                  "length 3,921 tokens on hard328): 71 % of the Karpathy method's losses have every "
                                  'right route past its 4,096 cap, and at T 0.6 half or more of the answers past '
                                  '4,096 tokens are loops (0.52 plain, 0.63 cued).',
                                  'Inside the edit, finishing sits in direction 1 and the late layers, while most of '
                                  'the gain in right answers needs directions 2-8 in the early and middle layers '
                                  "with RL's exact input-output pairing. So a domain's own directions raise its "
                                  'correct-answer rate (Code directions on code: +7.0 pass points over a random '
                                  "edit), while another domain's directions carry over mainly the shared "
                                  'deliberation and finishing (Math directions on code: +1.5).'],
                    'marks': {'explained': 38, 'not addressed': 3, 'contradicts': 1},
                    'facts': 42,
                    'contradicts': [['F26',
                                     'Against S6: direction 1 alone adds right answers where the base finished wrong '
                                     '(+7.2 [0.7, 13.6]), close to directions 2-8 (+9.3; difference +2.1 [-6.1, '
                                     '10.5]), so finishing and right answers are not cleanly split by rank here.']]}},
 'tests': {'round-15/account-1/c1': {'kind': 'consequence',
                                     'claim': 'If on-policy RL under any reward concentrates in the inputs the '
                                              "base's own text drives (S1), Code-RL 3.1's change must sit in RL-Math "
                                              "3.1's top-8 input subspace far more than off-policy Think-SFT's "
                                              "diffuse change does. If each reward wrote its own subspace, Code's "
                                              "capture would be no higher than Think-SFT's.",
                                     'statistic': 'median over matrices of cap_right(Code 3.1 change, Math 3.1 top-8 '
                                                  'input subspace) / cap_right(Think-SFT change, same subspace), a '
                                                  'ratio (unitless)',
                                     'null': "Another model's change in the same subspace: Think-SFT's own capture, "
                                             "so ratio about 1 if concentration is reward-specific and Code's change "
                                             "is as unrelated to Math's inputs as a diffuse fine-tune",
                                     'why_new': "F24 gives only Think-SFT's capture (4.80x chance) and says the >=2x "
                                                "property is 'shared' with Code 3.1; no fact or result gives Code "
                                                "3.1's capture relative to Think-SFT's in the same subspace.",
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'1': [2.0, 60.0], 'null': [0.5, 1.5]},
                                     'plan_n': 224,
                                     'value': 5.1575,
                                     'lo': 4.7984,
                                     'hi': 5.5591,
                                     'n': 224,
                                     'null_value': None,
                                     'verdicts': {'1': 'holds'},
                                     'result': 'result-105d5c',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'1': '5.16 [90 % 4.80, 5.56], n 224 matrices, null value 1.0 (null '
                                                       'range [0.5, 1.5]), account-1 range [2.0, 60.0]'},
                                     'record_claim': {'1': "Code-RL 3.1's weight change sits in RL-Math 3.1's top-8 "
                                                           "input subspace far more than Think-SFT's change does "
                                                           '(median per-matrix cap_right ratio Code / Think-SFT in '
                                                           '[2.0, 60.0]).'},
                                     'retest': {}},
           'round-15/account-1/c2': {'kind': 'consequence',
                                     'claim': "If concentration is set by which base inputs the model's own samples "
                                              'drive (S1), the matrices where Math-RL concentrates most should also '
                                              'be the ones where an unrelated on-policy reward (IF) concentrates '
                                              'most, beyond what they share with off-policy Think-SFT.',
                                     'statistic': 'Spearman rho(Math 3.1, IF) minus Spearman rho(Math 3.1, '
                                                  "Think-SFT) of per-matrix top-8 share after each module family's "
                                                  'median is subtracted (difference of correlations, unitless)',
                                     'null': "Another model's directions: Think-SFT's per-matrix pattern shares as "
                                             'much with Math-RL as IF-RL does, so the difference is about 0 '
                                             '(concentration pattern reward- or training-agnostic)',
                                     'why_new': 'F03 and result-82eb02 compare mean top-8 shares across models only. '
                                                'No fact or result relates the per-matrix concentration pattern of '
                                                "one reward to another's.",
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'1': [0.15, 1.0], 'null': [-0.1, 0.1]},
                                     'plan_n': 224,
                                     'value': -0.6038,
                                     'lo': -0.7326,
                                     'hi': -0.4747,
                                     'n': 224,
                                     'null_value': None,
                                     'verdicts': {'1': 'refuted'},
                                     'result': 'result-caa23d',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'1': 'D = rho(Math 3.1, IF) - rho(Math 3.1, Think-SFT) = -0.010 - '
                                                       '0.594 = -0.604 [90 % -0.733, -0.475], n 224 matrices, null '
                                                       'value 0 (null range [-0.1, 0.1]), account-1 range [0.15, '
                                                       '1.0]'},
                                     'record_claim': {'1': "After each module family's median is removed, Math-RL "
                                                           "3.1's per-matrix top-8 share correlates (Spearman) more "
                                                           "with IF-RL's than with Think-SFT's, by at least 0.15."},
                                     'retest': {}},
           'round-15/account-3/c2': {'kind': 'consequence',
                                     'claim': "The 1.5x top-8 edit is RL's re-weighting of the base distribution "
                                              "(S3, S4), so its wrong answers are split like RL's, and its vote over "
                                              "4 should match RL's vote over 4 on hard328, not stay at the base's "
                                              'vote. If the edit only added finishing, its votes would gain like a '
                                              "base resample's and fall about 9 points short of RL's.",
                                     'statistic': 'vote-over-4 right of 328 for base + 1.5x top-8 RL-Math directions '
                                                  "minus RL plain's vote over 4, in points (percent of 328)",
                                     'null': "The base's own resample: a vote over 4 cued-base samples "
                                             '(equivalently, a base-like random rank-8 edit at 1.5x, which '
                                             "result-39497c shows does nothing) against RL's vote, about -8.8 "
                                             'points.',
                                     'why_new': "result-95a4dc and data.md report only the edit's single samples "
                                                '(207, 198, 199, 197) and its mean; no listed result or fact gives '
                                                "the edit's vote over 4 on hard328.",
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'3': [-5.0, 5.0], 'null': [-14.0, -6.0]},
                                     'plan_n': 328,
                                     'value': 0.1,
                                     'lo': -1.8,
                                     'hi': 1.96,
                                     'n': 328,
                                     'null_value': -9.55,
                                     'verdicts': {'3': 'holds'},
                                     'result': 'result-d6fe92',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'3': '+0.1 points [90 % -1.8, 1.96], n 328 (order-averaged ties: '
                                                       'edit 216.25, RL 215.92); null (base vote minus RL) -9.55 '
                                                       '[-12.5, -6.78]; account-3 range [-5.0, 5.0], null range '
                                                       '[-14.0, -6.0]; stored-order ties -2.13 [-4.57, 0.3], also '
                                                       'holds'},
                                     'record_claim': {'3': 'On hard328 the vote over 4 of base + 1.5x top-8 RL-Math '
                                                           "directions matches RL plain's vote over 4 (within 5 "
                                                           "points), not the base's vote."},
                                     'retest': {}},
           'round-15/account-2/c2': {'kind': 'consequence',
                                     'claim': 'RL step 100 has learned only the opening (S2), not the lower slip '
                                              "rate, so its wrong answers scatter like the cued base's and a vote "
                                              "over its 4 samples gains as much over one sample as the cued base's "
                                              "vote does (+7.1 points), not as little as final RL's (+2.8).",
                                     'statistic': 'Vote-over-4 right minus mean single-sample right for RL step 100 '
                                                  'plain, in points of 500 (percentage points)',
                                     'null': "Final RL's own vote gain (results/day1_3/math500_rl-01: vote 474 vs "
                                             "mean single 460, +2.8 points), i.e. step 100 already carrying RL's "
                                             'lowered slip rate.',
                                     'why_new': "F07/F38 and result-6832a8 give step 100's single-sample score and "
                                                'cap hits only; no fact or result computes a vote over step-100 '
                                                'samples.',
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'2': [5.0, 10.0], 'null': [1.0, 4.5]},
                                     'plan_n': 500,
                                     'value': 7.1833,
                                     'lo': 6.0333,
                                     'hi': 8.3667,
                                     'n': 500,
                                     'null_value': 2.8667,
                                     'verdicts': {'2': 'holds'},
                                     'result': 'result-53addf',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'2': '+7.18 points [6.03, 8.37] (90 % bootstrap over problems), n '
                                                       '500, null value +2.8 (final RL; recomputed +2.87), account-2 '
                                                       'range [5.0, 10.0], null range [1.0, 4.5]'},
                                     'record_claim': {'2': 'RL step 100 plain on MATH-500 gains as much from a vote '
                                                           'over its 4 samples (vote right minus mean single-sample '
                                                           'right) as the cued base does, 5 to 10 points, not as '
                                                           'little as final RL.'},
                                     'retest': {'2': {'verdict': 'not separated',
                                                      'adversary': 6.237,
                                                      'result': 'result-61c569',
                                                      'measured': 'G = +7.18 points [6.03, 8.37] (90 % bootstrap '
                                                                  "over problems), n 500; adversary (final RL's vote "
                                                                  "gain per right count k, weighted by step 100's k "
                                                                  'distribution) +6.24, inside the interval; G minus '
                                                                  'adversary +0.95 [-0.09, 2.00]',
                                                      'added': '2026-11-15T23:44:43Z'}}},
           'round-15/account-3/c3': {'kind': 'consequence',
                                     'claim': 'RL step 100 is only the mode selection the cue makes, with the same '
                                              'cap-hit rate and none of the later finishing or lengthening (S4). So '
                                              "on problems both arms solve, step 100's right answers should be as "
                                              "long as the cued base's right answers, while final RL, which carries "
                                              'the finishing and lengthening, should not be.',
                                     'statistic': 'geometric mean over problems of (median generated tokens of '
                                                  'step-100 plain right samples / median generated tokens of '
                                                  'cued-base right samples), as a ratio',
                                     'null': 'Another model: final RL-Zero-Math against the cued base on the same '
                                             'problems, which carries the lengthening of short answers '
                                             '(result-1b6bf2) that step 100 should lack.',
                                     'why_new': 'Facts F07 and F38 and results fad48d and 6832a8 compare step 100 '
                                                'with the cue on score and cap hits only; no fact or result compares '
                                                'the lengths of right answers.',
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'3': [0.88, 1.1], 'null': [1.15, 1.6]},
                                     'plan_n': 430,
                                     'value': 1.1466,
                                     'lo': 1.1122,
                                     'hi': 1.1815,
                                     'n': 459,
                                     'null_value': 1.6129,
                                     'verdicts': {'3': 'refuted'},
                                     'result': 'result-534492',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'3': '1.147 [90 % 1.112, 1.181], n 459 problems; null value (final '
                                                       'RL / cued base) 1.613 [1.560, 1.667], n 465; account-3 range '
                                                       '[0.88, 1.10], null range [1.15, 1.60]'},
                                     'record_claim': {'3': 'On MATH-500 problems both arms solve, RL step-100 plain '
                                                           'right answers are as long as the cued base right answers '
                                                           '(geometric-mean ratio of per-problem medians in [0.88, '
                                                           '1.10]), while final RL right answers are longer.'},
                                     'retest': {}},
           'round-15/account-3/c1': {'kind': 'consequence',
                                     'claim': 'The plain-prompt base answers that happen to open deliberatively '
                                              "('Okay', 'Alright', 'Hmm', 'Let me', 'Let's', 'I need to' within the "
                                              "first 240 characters) are already in the cue's mode. On the same "
                                              "problems they should be right about as often as the cued base's "
                                              'answer (S2, S4: a prompt only selects a mode the weights hold). If '
                                              'the cue added something beyond choosing the mode, those answers would '
                                              'sit near the plain rate instead.',
                                     'statistic': 'mean over problems of (T3 plain right - T1 cued right) on '
                                                  'problems whose T3 answer opens deliberatively, in fraction of '
                                                  'problems',
                                     'null': 'Opening irrelevant (the cue adds more than mode selection): flagged '
                                             'answers do as well as plain answers do elsewhere, i.e. the same T3-T1 '
                                             'difference computed on the unflagged problems (the overall T3-T1 is '
                                             '-0.37).',
                                     'why_new': 'The self-opened draw (result-3a3af3) selects openings by resampling '
                                                "32 draws; no fact or result compares the base's natural, unselected "
                                                'deliberative plain openings with the cued answer on the same '
                                                'problems.',
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'3': [-0.15, 0.1], 'null': [-0.65, -0.22]},
                                     'plan_n': 120,
                                     'value': -0.0336,
                                     'lo': -0.1007,
                                     'hi': 0.0336,
                                     'n': 149,
                                     'null_value': -0.5157,
                                     'verdicts': {'3': 'holds'},
                                     'result': 'result-1f98b0',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'3': 'mean(T3 right - T1 right) -0.034 [90 % -0.101, 0.034], n 149 '
                                                       'of 500, null (unflagged problems) -0.516 [-0.564, -0.467]; '
                                                       'account-3 range [-0.15, 0.10], null range [-0.65, -0.22]'},
                                     'record_claim': {'3': 'On MATH-500 problems whose plain-prompt base answer '
                                                           'opens deliberatively, that answer is right about as '
                                                           "often as the cued base's answer on the same problems."},
                                     'retest': {}},
           'round-15/account-2/c1': {'kind': 'consequence',
                                     'claim': "On hard328 the cued base's finished wrong answers also scatter, so "
                                              'the vote over its 4 samples with the real wrong answers is right '
                                              'clearly more often than the same vote with every finished wrong '
                                              'answer of a problem merged into one value. S4 says vote gains come '
                                              'from independent one-off slips, so D lies in [0.06, 0.40]; if '
                                              'hard-problem wrongs shared one attractor, D would be about 0.',
                                     'statistic': 'D = mean over problems of P(vote of 4 right | real answers) - '
                                                  'P(vote of 4 right | finished wrong answers merged), in '
                                                  'probability units',
                                     'null': "Merged-wrong vote (the base's wrong answers on a problem share one "
                                             'attractor value), where D = 0 exactly; the strongest null for this '
                                             'statistic.',
                                     'why_new': 'F37 measured this on MATH-500 with 12 samples; F23/F42 measured '
                                                'MATH-500 agreement only. No fact or result gives the merged-wrong '
                                                'vote contrast on hard328, where wrong answers could plausibly '
                                                'concentrate on shared traps.',
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'2': [0.06, 0.4], 'null': [-0.03, 0.03]},
                                     'plan_n': 110,
                                     'value': 0.1089,
                                     'lo': 0.0777,
                                     'hi': 0.142,
                                     'n': 88,
                                     'null_value': None,
                                     'verdicts': {'2': 'holds'},
                                     'result': 'result-3394eb',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'2': 'D 0.109 [90 % 0.078, 0.142], n 88, null value 0 (null range '
                                                       '[-0.03, 0.03]), account-2 range [0.06, 0.40]'},
                                     'record_claim': {'2': 'On hard328 the cued base vote over 4 attempt-0 samples '
                                                           'is right more often with its real finished wrong answers '
                                                           'than with every finished wrong answer of a problem '
                                                           'merged into one, by D in [0.06, 0.40].'},
                                     'retest': {'2': {'verdict': 'not separated',
                                                      'adversary': 0.1024,
                                                      'result': 'result-61c569',
                                                      'measured': 'D = 0.109 [0.078, 0.142] (90 % bootstrap over '
                                                                  'problems), n 88; adversary (wrong answers are '
                                                                  'shared attractor values at the measured pair '
                                                                  'agreement 0.218 of 257 pairs, q 0.467, 2,000 '
                                                                  'simulations) 0.102; fully independent wrong '
                                                                  'answers would give 0.139',
                                                      'added': '2026-11-15T23:44:43Z'}}},
           'round-15/account-2/c3': {'kind': 'consequence',
                                     'claim': 'The 1.5x top-8 edit is a weight change that lowers the slip rate the '
                                              'way RL does (S1, S2, S5), so on hard328 problems where the cued base '
                                              'has no right answer in 4 samples it is right per sample as often as '
                                              'RL plain: the edit-minus-RL rate lies in [-0.08, 0.08]. If the edit '
                                              "were only a resample of the base, it would sit near the base's own "
                                              'rate there and about 0.2 below RL.',
                                     'statistic': 'Edit per-sample right rate minus RL plain per-sample right rate '
                                                  'on base-0-of-4 hard328 problems, in probability units',
                                     'null': 'The edit as a base resample: its rate on these problems equals the '
                                             "cued base's own fresh-sample rate (near 0.05), giving D about -0.2.",
                                     'why_new': 'result-95a4dc matches edit and RL on totals; F04/F26 split by one '
                                                "base sample's outcome. No fact or result compares edit and RL on "
                                                "the problems outside the base's 4-sample reach.",
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'2': [-0.08, 0.08], 'null': [-0.35, -0.12]},
                                     'plan_n': 110,
                                     'value': -0.0124,
                                     'lo': -0.0372,
                                     'hi': 0.0103,
                                     'n': 121,
                                     'null_value': -0.0967,
                                     'verdicts': {'2': 'holds'},
                                     'result': 'result-378eef',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'2': 'E - R = -0.012 [-0.037, 0.010] (90 % paired bootstrap), n '
                                                       '121 problems; null value -0.097 [-0.136, -0.060]; account-2 '
                                                       'range [-0.08, 0.08], null range [-0.35, -0.12]'},
                                     'record_claim': {'2': 'On hard328 problems where the cued base has 0 of 4 '
                                                           'right, the 1.5x top-8 edit is right per sample as often '
                                                           'as RL plain (edit minus RL in [-0.08, 0.08]).'},
                                     'retest': {}},
           'round-15/d1': {'kind': 'disagreement',
                           'claim': 'On hard328 problems where the cued base has 0 right among its 4 attempt-0 '
                                    "samples, the 1.5x top-8 edit's per-sample lift over a fresh cued-base sample, "
                                    "as a fraction of RL plain's lift over the same fresh base sample, is 0.6 or "
                                    'more if account-2 holds and 0.10-0.45 if account-1 holds.',
                           'statistic': "S = (E - B) / (R - B), the share of RL plain's per-sample advantage over a "
                                        'fresh cued-base sample that the edit captures on base-0-of-4 problems '
                                        '(unitless ratio of mean per-sample right rates)',
                           'null': "The edit as a base resample: on these problems the edit's rate equals a fresh "
                                   "cued-base sample's (E = B, as a random rank-8 1.5x edit does), so S is about 0.",
                           'why_new': '',
                           'about': "Whether the 1.5x top-8 RL-Math edit, a weight change that matches RL's total on "
                                    'hard328, also wins the problems the cued base cannot solve in 4 samples (where '
                                    "RL's extra wins sit), or only re-weights the base toward problems it already "
                                    'reaches.',
                           'positions': {'account-1': 'S2/S6 (and its c3): the pairs carry one shared graded shift '
                                                      "that makes the base's scattered slips rarer on problems it "
                                                      "can already solve, not RL's problem-specific solves. So on "
                                                      "problems outside the base's 4-sample reach the edit lifts the "
                                                      "base only a little and captures a minority of RL's advantage "
                                                      'there.',
                                         'account-2': 'S2/S5 (and its c3): the edit is a weight change that lowers '
                                                      'the per-step slip rate the way RL does. Because that lower '
                                                      'rate compounds over long chains, it wins the base-0-of-4 '
                                                      'hard328 problems about as often as RL plain does (edit minus '
                                                      "RL in [-0.08, 0.08]), so it captures most or all of RL's "
                                                      'advantage there.'},
                           'ranges': {'1': [0.1, 0.45], '2': [0.6, 1.4], 'null': [-0.15, 0.08]},
                           'plan_n': 108,
                           'value': 0.88,
                           'lo': 0.6857,
                           'hi': 1.1316,
                           'n': 120,
                           'null_value': None,
                           'verdicts': {'1': 'refuted', '2': 'holds'},
                           'result': 'result-b90743',
                           'added': '2026-11-15T23:23:44',
                           'measured': {'1': 'S = (E - B) / (R - B) = 0.88 [0.69, 1.13] (90 % bootstrap), n 120 '
                                             'problems (480 edit samples), null value 0 (null range [-0.15, 0.08]), '
                                             'range [0.10, 0.45]: the interval lies wholly above it. Supersedes '
                                             'editreach-01 (result-fe30d5), which read only 102 problems',
                                        '2': 'S = (E - B) / (R - B) = 0.88 [0.69, 1.13] (90 % bootstrap), n 120 '
                                             'problems (480 edit samples), null value 0 (null range [-0.15, 0.08]), '
                                             'range [0.60, 1.40]: the interval lies wholly inside it. R - B 0.104 '
                                             '[0.065, 0.146]; edit minus RL -0.013 [-0.037, 0.010]. Supersedes '
                                             'editreach-01 (result-fe30d5)'},
                           'record_claim': {'1': 'The 1.5x top-8 edit carries one shared graded shift that makes the '
                                                 "base's slips rarer on problems it already solves, so on hard328 "
                                                 "problems outside the cued base's 4-sample reach it captures only a "
                                                 "minority (0.10-0.45) of RL plain's per-sample advantage over a "
                                                 'fresh base sample.',
                                            '2': 'The 1.5x top-8 edit lowers the per-step slip rate the way RL does, '
                                                 "so on hard328 problems outside the cued base's 4-sample reach it "
                                                 'wins about as often as RL plain and captures most or all '
                                                 "(0.60-1.40) of RL's per-sample advantage over a fresh base "
                                                 'sample.'},
                           'retest': {'2': {'verdict': 'not separated',
                                            'adversary': 1.006,
                                            'result': 'result-61c569',
                                            'measured': 'S = (E - B) / (R - B) = 0.880 [0.686, 1.132] (90 % '
                                                        'bootstrap over problems), n 120; adversary (S from overall '
                                                        'hard328 accuracy alone: edit 0.611, RL 0.610, cued base '
                                                        '0.483) 1.006. edit0of4 (c3) is the same measurement on the '
                                                        'same rows: no separate row',
                                            'added': '2026-11-15T23:44:43Z'}}},
           'round-15/account-1/c3': {'kind': 'consequence',
                                     'claim': "If the 1.5x top-8 edit carries RL's shared shift but not its "
                                              'problem-specific choices (S6), then on hard328 problems where RL '
                                              "solves none of 4 samples the edit keeps at least most of the base's "
                                              "right answers, as F20 found on code. If the edit copied RL's "
                                              'outcomes, it would lose them.',
                                     'statistic': 'edit right samples / base right samples on hard328 problems with '
                                                  'RL 0 of 4 right (ratio, unitless)',
                                     'null': "The edit copies RL's outcomes per problem (fully or for two thirds of "
                                             'samples), so edit right samples on RL-0/4 problems fall to at most '
                                             "half the base's",
                                     'why_new': 'F19/F20 test this only on code. No fact or listed result splits the '
                                                "hard328 edit rows by RL's per-problem outcome.",
                                     'about': '',
                                     'positions': {},
                                     'ranges': {'1': [0.75, 4.0], 'null': [0.0, 0.5]},
                                     'plan_n': 280,
                                     'value': 2.0,
                                     'lo': 0.8,
                                     'hi': 5.0,
                                     'n': 352,
                                     'null_value': None,
                                     'verdicts': {'1': 'undecided'},
                                     'result': 'result-f638fb',
                                     'added': '2026-11-15T23:22:45',
                                     'measured': {'1': 'edit/base right samples 2.0 [90 % 0.8, 5.0] (12 vs 6 right), '
                                                       'n 352 edit samples on 88 problems, null value 0 (full copy '
                                                       'of RL; null range [0, 0.5], interval wholly above it), '
                                                       'account-1 range [0.75, 4.0]; about 990 edit samples would '
                                                       'decide'},
                                     'record_claim': {'1': 'On hard328 problems where RL plain gets 0 of 4 right, '
                                                           'the 1.5x top-8 edit keeps at least most of the cued '
                                                           "base's right answers (edit/base right samples in [0.75, "
                                                           "4.0]) rather than copying RL's outcomes (ratio <= 0.5)."},
                                     'retest': {}}},
 'round14': [1, 12]}
REF = 'origin/theory'  # the git ref --write read the files from ("" for the working tree)
COMMIT = '5c30305'  # the last commit of those files at that ref when RECORD was written


def _git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def _text(ref, path):
    return _git("show", f"{ref}:{path}") if ref else open(path).read()


def _load(ref, path):
    return json.loads(_text(ref, path))


def _get(obj, path):  # a value by a dotted key path
    for k in path.split("."):
        obj = obj[k]
    return obj


def _build(ref=""):
    plans = {t["name"]: t for t in _load(ref, W + "synthesis_tests.json")}
    assert list(plans) and set(plans) == set(TESTS), f"TESTS differ from synthesis_tests.json: {sorted(set(plans) ^ set(TESTS))}"
    rows = {}
    for p in FILES:
        for x in _load(ref, p):
            if x["mechanism"].startswith("round-15/") and not x["mechanism"].endswith("@16"):
                assert rows.setdefault(x["mechanism"], x) == x, f"{x['mechanism']} differs between the record files"
    judge = _load(ref, W + "disagreements.json")["disagreements"]
    assert [d["id"] for d in judge] == ["d1"], "the page draws one disagreement, d1"
    accounts, tests = {}, {}
    for k in ("1", "2", "3"):
        a = _load(ref, W + f"account-{k}.json")
        marks = {m: sum(x["mark"] == m for x in a["marks"]) for m in ("explained", "not addressed", "contradicts")}
        assert sum(marks.values()) == len(a["marks"])
        accounts[k] = {"sentences": a["account"], "marks": marks, "facts": len(a["marks"]),
                       "contradicts": [[x["fact"], x["why"]] for x in a["marks"] if x["mark"] == "contradicts"]}
    r16 = {x["mechanism"][:-3]: x for x in rows_all(ref) if x["mechanism"].startswith("round-15/") and x["mechanism"].endswith("@16")}
    for name, t in TESTS.items():
        plan, folder = plans[name], t[2]
        m = _load(ref, f"{R}direct/{folder}/metrics.json")
        lo, hi = _get(m, t[4])
        mech = plan["mechanisms"]  # {"account-k": mechanism id}
        verdicts = {a.split("-")[1]: rows[i]["verdict"] for a, i in mech.items()}
        if "verdict" in m:  # the test's own verdict agrees with the record's
            mv = m["verdict"] if isinstance(m["verdict"], dict) else {next(iter(mech)): m["verdict"]}
            assert {a.split("-")[1]: v for a, v in mv.items()} == verdicts, name
        first = rows[next(iter(mech.values()))]
        tests[name] = {
            "kind": plan["kind"], "claim": plan["claim"], "statistic": plan["statistic"], "null": plan["null"],
            "why_new": plan.get("why_new", ""), "about": plan.get("about", ""), "positions": plan.get("positions", {}),
            "ranges": {a.split("-")[-1] if a != "null" else "null": r for a, r in plan["ranges"].items()},
            "plan_n": plan["n"], "value": round(_get(m, t[3]), 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "n": _get(m, t[5]), "null_value": round(_get(m, t[7]), 4) if t[7] else None,
            "verdicts": verdicts, "result": first["result"], "added": first["added"].rstrip("Z")[:19],
            "measured": {a.split("-")[1]: rows[i]["measured"] for a, i in mech.items()},
            "record_claim": {a.split("-")[1]: rows[i]["claim"] for a, i in mech.items()},
            # the same claim retested under engine 16's adversary rule (mechanism id + "@16"), where it was
            "retest": {a.split("-")[1]: {k: r16[i][k] for k in ("verdict", "adversary", "result", "measured", "added")}
                       for a, i in mech.items() if i in r16},
        }
    facts = _load(ref, W + "synthesis_facts.json")
    assert all(a["facts"] == len(facts) for a in accounts.values()), "every account marks every fact once"
    r14 = [x for x in rows_all(ref) if re.match(r"round-14/s\d-[ab]$", x["mechanism"])]
    files = [W, *FILES, *[f"{R}direct/{t[2]}/" for t in TESTS.values()]]
    commit = _git("log", "-1", "--format=%h", *([ref] if ref else []), "--", *files).strip()
    return {"facts": len(facts), "accounts": accounts, "tests": tests,
            "round14": [sum(x["verdict"] == "holds" for x in r14), len(r14)]}, commit


def rows_all(ref):  # every row of the record, a mechanism once (direct_tested.json first)
    seen = {}
    for p in FILES:
        for x in _load(ref, p):
            seen.setdefault(x["mechanism"], x)
    return list(seen.values())


def _tally(rec):
    """The headline counts. held, refuted, undecided, tested: the 9 new consequences of the three accounts. accounts[k]:
    that account's own counts, its d1 verdict ("" when it took no side) and its score (holds minus facts it marks as
    against it, the engine's score in synthesis.md)."""
    if not rec:
        return {}
    cons = {n: t for n, t in rec["tests"].items() if t["kind"] == "consequence"}
    v = [next(iter(t["verdicts"].values())) for t in cons.values()]
    d1 = rec["tests"]["round-15/d1"]["verdicts"]
    acc = {}
    for k, a in rec["accounts"].items():
        own = [next(iter(t["verdicts"].values())) for t in cons.values() if k in t["verdicts"]]
        acc[k] = {"held": own.count("holds"), "refuted": own.count("refuted"), "undecided": own.count("undecided"),
                  "tested": len(own), "explained": a["marks"]["explained"], "unaddressed": a["marks"]["not addressed"],
                  "contradicts": a["marks"]["contradicts"], "d1": d1.get(k, ""),
                  "score": own.count("holds") - a["marks"]["contradicts"]}
    c = {"held": v.count("holds"), "refuted": v.count("refuted"), "undecided": v.count("undecided"), "tested": len(v),
         "accounts": acc, "facts": rec["facts"], "disagreements": 1, "round14": rec["round14"],
         "not_separated": sum(x["verdict"] == "not separated" for t in rec["tests"].values() for x in t["retest"].values()),
         "best": max(acc, key=lambda k: (acc[k]["score"], acc[k]["d1"] == "holds"))}
    assert c["held"] + c["refuted"] + c["undecided"] == c["tested"]
    return c


COUNTS = _tally(RECORD)
_c = COUNTS
_a = _c.get("accounts", {})
LINE = (f"{_c.get('held')} of {_c.get('tested')} new claims from three accounts of what RL changed held on stored data; a stricter retest "
        f"could not separate {_c.get('not_separated')} of them from predictions made without the account.")
EXAMPLES = [["d1", "Example: the one disagreement, and its test"], ["a3c3", "Example: a claim that was refuted"]]


def _acc_line(k):
    x = _a[k]
    return (f"account {k}: {x['held']} held, {x['refuted']} refuted, {x['undecided']} undecided; {x['explained']} of "
            f"{_c['facts']} facts marked explained, {x['contradicts']} marked against it; score {x['score']}")


PANELS = [] if not _c else [
    ["new", "What is new",
     f"Until round 14 the team's theory engine wrote one cause per surprising number, and those lost: in round 14, "
     f"{_c['round14'][0]} of {_c['round14'][1]} rival causes held their test. Round 15 asked each of three agents for one "
     f"account of all {_c['facts']} directly tested facts.",
     ["The agents worked blind to each other. Each account had to name 3 new consequences that stored data could check, "
      "with the account's range and the null's range fixed before the check.",
      "A judge then listed every point where the accounts disagree, with a test for each. It found one (d1).",
      "AutoCog (arXiv 2606.26448, abstract and its loop's stages 3 and 4) has language-model agents advocate competing "
      "theories, run experiments that tell them apart and revise the weaker one. Here the accounts are not revised: "
      "their consequences are checked once, on data already stored.",
      ["Mechanisms tested directly: the one-cause-per-number approach this round replaced ›", "/finding/mechanisms-tested-directly"],
      ["Theories on trial: the same engine's theories, scored on their predictions ›", "/finding/theories-on-trial"]]],
    ["why", "Why it matters",
     f"Account 2 is now the team's single explanation of what RL did to this model; under round 15's rule every new "
     f"test of it held, {_a['2']['held']} of {_a['2']['tested']}, and the one disagreement went its way.",
     ["The disagreement was the most informative test: the 8-direction edit wins the problems Base + cue cannot solve in "
      "4 samples about as often as RL does (edit minus RL −0.013, 90 % interval −0.037 to 0.010, 120 problems).",
      "So the 8 directions carry the part of RL's gain that inference cannot reach, not only the part the base already "
      "samples.",
      f"{_c['held']} of {_c['tested']} new consequences held, against {_c['round14'][0]} of {_c['round14'][1]} rival "
      "causes in round 14."]],
    ["how", "How we know",
     "Each of the 10 tests ran offline on stored answers or weights, one agent per test, with its plan, null and "
     "ranges committed before the data was read.",
     ["A claim holds when its 90 % interval lies wholly inside its range with n of 50 or more, is refuted when the "
      "interval lies wholly outside, and is undecided otherwise.",
      "Score: consequences that hold minus facts the account marks as against it. " + "; ".join(
          _acc_line(k) for k in ("2", "1", "3")) + ".",
      "Counts are read from the record files and agree with the board item (result-61a7ab) and synthesis.md.",
      "The first run of d1 read 102 of its 121 problems; the rerun (editreach-02, result-b90743) replaced it and "
      "moved account 2 from undecided to holds."]],
    ["limits", "What it does not show",
     f"A stricter retest found {_c['not_separated']} of account 2's holds not separated: a blind adversary, without "
     "the account, predicted a value inside each interval (engine 16, board item result-61c569).",
     ["The retested holds are c1 (wrong answers scatter), c2 (step 100's vote gain) and d1; c3 was counted as the same "
      "measurement as d1. Open one of them to read the adversary's value.",
      "A consequence that holds on stored data is not a forecast of a new GPU number: every check reads answers or "
      "weights that already existed.",
      "One model family wrote all three accounts, after reading the same 42 facts. Their agreement is not independent "
      "evidence: most tests confirm one shared story rather than choose between stories.",
      "Some nulls are weak or miscalibrated: the Code-RL null equals Think-SFT (weak), and the edit-equals-RL test's "
      "measured null sits next to the account's range. Open a claim to read its caveat.",
      "The two refutations are each account's most specific claim. Account 2 made no claim that failed, and its GPU "
      "forecast (the hand edit on the 328 harder problems, 62 of 164 predicted) has not been run."]],
    ["run", "How to reproduce it",
     "uv run tools/finding_one_account_of_the_facts.py --ref " + (REF or "<ref>") + ", from the repository root, "
     "rebuilds every value from the files and checks the copy on this page.",
     [f"Files: {W} (account-1.json to account-3.json, disagreements.json, synthesis_tests.json, synthesis.md)" +
      (f" on branch {REF.split('/')[-1]}" if REF else "") + f", commit {COMMIT}.",
      "Each test: studies/theory/results/direct/<test>/metrics.json, its spec studies/theory/specs/SPEC_direct_<name>.md "
      "and the README section Round 15; the round's plan is studies/theory/specs/SPEC_round15.md.",
      "Board items: result-61a7ab (the round), result-b90743 (d1), and one per claim, named when it is open."]],
]

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table
   with a cast shadow in place of the glow. Blue marks a claim that held and the range an account fixed in advance; a
   ring, a claim that was refuted; a dashed ring, one left undecided; a dashed outline, the null's range. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --tick: #8b97a1; --band: rgba(16, 24, 32, .075); --ring: #56636d; --grey: #a3adb5; --own: rgba(31, 67, 214, .22);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --tick: #66737e; --band: rgba(233, 239, 243, .07); --ring: #9aa7b2; --grey: #56626c; --own: rgba(143, 177, 255, .34);
  }
}
:root[data-theme="dark"] {
  --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
  --blue: #8fb1ff; --red: #ff6b7c;
  --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
  --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
  --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
  --tick: #66737e; --band: rgba(233, 239, 243, .07); --ring: #9aa7b2; --grey: #56626c; --own: rgba(143, 177, 255, .34);
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 27vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0; height: 100vh; min-height: 620px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: one plate with the six sentences, the claims that test them and the one control */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: calc(100vh - 170px); display: block; overflow: visible; cursor: default; user-select: none; -webkit-user-select: none; }
svg:focus:not(:focus-visible) { outline: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 104%; }
svg * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.hair { stroke: var(--rule); stroke-width: 1; }
.big { font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; }
.set { fill: var(--ink) !important; font-weight: 640; }
.lab { fill: var(--mute) !important; font-weight: 520; }
.lab0 { fill: var(--ink) !important; font-weight: 460; }
.lab2 { fill: var(--ink) !important; font-weight: 560; }
.hd { fill: var(--mute) !important; font-weight: 540; }
.sn { font-weight: 400; }
.cl { font-weight: 560; }
.cl.q { fill: var(--mute) !important; font-weight: 450; font-style: italic; }
.cl.t1 { fill: var(--mute) !important; }
.ex { fill: var(--mute) !important; font-weight: 450; }
.num { fill: var(--mute) !important; font-weight: 640; font-stretch: 100%; }
.spine { stroke: var(--rule); stroke-width: 1.2; }
.bead { fill: url(#bead) var(--sheet); stroke: var(--rim-c); stroke-width: 1; }
.ag { stroke-width: 1.1; transition: opacity .3s ease; }
.ag.same { fill: var(--ink); stroke: none; }
.ag.other { fill: var(--sheet); stroke: var(--ink); }
.ag.none { fill: none; stroke: var(--ring); stroke-dasharray: 1.8 1.6; }
.agc { fill: none; stroke: var(--blue); stroke-width: 1; }
.gl { fill: var(--mute) !important; font-weight: 520; }
.gl.own { fill: var(--ink) !important; font-weight: 600; }
.gv { font-weight: 640; font-stretch: 100%; }
.gv.r, .gv.u { fill: var(--mute) !important; }
.ax { stroke: var(--rule); stroke-width: 1; }
.rg { fill: var(--own); }
.rg2 { fill: var(--band); stroke: var(--faint); stroke-width: .6; }
.nl { fill: none; stroke: var(--faint); stroke-width: 1; stroke-dasharray: 2.2 2; }
.adv { stroke: var(--ink); stroke-width: 1.6; stroke-linecap: round; }
.ci { stroke-width: 2.4; stroke-linecap: round; }
.ci.h { stroke: var(--blue); } .ci.r, .ci.u, .ci.n { stroke: var(--ring); }
.pt { stroke-width: 1.5; }
.pt.h { fill: var(--blue); stroke: none; }
.pt.r { fill: var(--sheet); stroke: var(--ring); }
.pt.u { fill: var(--sheet); stroke: var(--ring); stroke-dasharray: 2 1.6; }
.pt.n { fill: var(--ink); stroke: none; }
.halo { fill: none; stroke: var(--blue); stroke-width: 1; }
.burst { fill: none; stroke: var(--blue); }
.selbox { fill: none; stroke: var(--ink); stroke-width: 1; stroke-dasharray: 3 3; }
.bl { fill: var(--mute) !important; font-weight: 560; }
.bl.own { fill: var(--blue) !important; font-weight: 660; }
.kt { fill: var(--mute) !important; font-weight: 520; }
.rp { fill: var(--mute) !important; font-weight: 500; }
.ctl { display: flex; align-items: center; gap: 12px; align-self: center; margin-top: 12px; flex-wrap: wrap; justify-content: center; }
.ctl .lbl { font-size: 13px; color: var(--mute); }
.switch { display: inline-flex; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { min-width: 40px; padding: 8px 16px; border-radius: 999px; font-weight: 600; font-size: 14.5px; text-align: center; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.quiet { font-size: 13.5px; color: var(--mute); padding: 6px 1px 4px; border-bottom: 1px solid transparent; transition: color .15s ease; white-space: nowrap; margin-left: 10px; }
.quiet:hover { color: var(--ink); }
.quiet[aria-pressed="true"] { color: var(--ink); font-weight: 640; border-bottom-color: var(--ink); }
.hint { align-self: center; margin: 8px 0 0; font-size: 13px; color: var(--mute); }

/* One drawn entrance, then only the slow sway and one replayed test at a time */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .read, .enter .key { animation: fade .7s .4s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); padding-bottom: 24px; }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.more.ex { margin-top: 18px; border-top: 0; }
.more.ex button { font-size: 15px; color: var(--mute); padding: 9px 0; }
.more.ex button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.quote { margin: 10px 0 0; font-size: clamp(15px, 1.05vw, 17px); line-height: 1.45; font-weight: 380; max-width: 38ch; overflow-wrap: anywhere; }
.quote.small { font-size: 14px; color: var(--mute); }
.tag { margin: 12px 0 0; font-size: 13.5px; color: var(--mute); }
.tag b { color: var(--ink); font-weight: 640; }
.why { margin: 8px 0 0; font-size: 14px; line-height: 1.45; color: var(--mute); max-width: 44ch; overflow-wrap: anywhere; }
.why b { color: var(--ink); font-weight: 640; }
.case { margin: 16px 0 0; padding: 8px 0 8px 12px; border-left: 2px solid var(--blue); font-size: 14px; line-height: 1.45; max-width: 44ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts a { color: var(--ink); text-decoration: none; }
.facts a:hover { color: var(--blue); }
h3 { margin: 22px 0 0; font-size: 14px; font-weight: 660; font-stretch: 110%; padding-bottom: 6px; border-bottom: 1px solid var(--rule); }
.gauge { width: 100%; max-width: 340px; height: auto; margin: 14px 0 0; max-height: none; }
.g-t { fill: var(--mute) !important; font-weight: 520; }
.g-v { font-weight: 640; }
.steps { display: flex; justify-content: space-between; margin-top: 16px; font-size: 13px; color: var(--mute); }
.steps button:hover { color: var(--ink); }
.lnk { color: var(--ink); border-bottom: 1px solid var(--faint); }
.lnk:hover { color: var(--blue); }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .ctl { flex-direction: column; gap: 8px; margin-top: 14px; }
  .switch { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); width: 100%; border-radius: 18px; }
  .switch button { min-width: 0; padding: 10px 0; font-size: 14px; border-radius: 14px; }
  .quiet { margin: 0; }
  .hint { text-align: center; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a, .quiet, .ag { transition: none; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage" id="stage">
    <svg id="svg" role="img" tabindex="0"></svg>
    <div class="ctl">
      <span class="lbl" id="ctllbl">Read as</span>
      <div class="switch" id="switch" role="group" aria-labelledby="ctllbl"></div>
      <button class="quiet" id="split" data-state="3" aria-pressed="false">Where they disagree</button>
    </div>
    <p class="hint">Click a sentence or a claim, or press Enter on the picture, to read it in full.</p>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const minus = s => String(s).replace(/(^|[\s(\[,])-(?=\d|\.\d)/g, "$1−");
/* A number at a precision that keeps it readable, with a real minus sign; points carry a sign. */
function fv(x, unit) {
  if (x == null) return "none";
  const a = Math.abs(x), s = (+a.toFixed(a >= 10 ? 1 : a >= 2 ? 2 : 3)).toString();
  return (x < 0 ? "−" : unit === "points" && x > 0 ? "+" : "") + s + (unit ? " " + unit : "");
}

/* The four states of the one control: read as account 1, 2 or 3, or where they disagree. Account 2 is the first view. */
const STATES = ["a1", "a2", "a3", "split"], SNAME = ["Account 1", "Account 2", "Account 3", "Where they disagree"];
const ACC = s => s === 3 ? "2" : String(s + 1);  // whose words the picture uses; the disagreement view shows account 2's
const VK = { holds: "h", refuted: "r", undecided: "u" }, VFULL = { h: "holds", r: "refuted", u: "undecided", n: "no side" };
const CAP = s => s[0].toUpperCase() + s.slice(1);

/* The tests, in the order of the picture. key: a1c1 ... a3c3, d1. */
const T = C.order.map((name, i) => {
  const r = C.record.tests[name], t = C.tests[name];
  const key = name === "round-15/d1" ? "d1" : name.replace("round-15/account-", "a").replace("/", "");
  const acc = Object.keys(r.verdicts);
  return { i, name, key, r, label: t[0], node: t[1] - 1, folder: t[2], nunit: t[6], unit: t[8], dom: t[9], caveat: t[10],
           acc, d1: name === "round-15/d1" };
});
const TK = Object.fromEntries(T.map(t => [t.key, t])), D1 = TK.d1;
const NODES = C.nodes.map((n, i) => ({ i, key: "s" + (i + 1), text: n[0], a1: n[1], a3: n[2], st: { "1": n[3], "2": "same", "3": n[4] },
                                       tests: T.filter(t => t.node === i) }));
const NK = Object.fromEntries(NODES.map(n => [n.key, n]));
/* The verdict a test's mark shows in a state: a consequence its own; d1 the verdict of the account read ("n" for none). */
function vOf(t, s) {
  if (!t.d1) return VK[t.r.verdicts[t.acc[0]]];
  const v = t.r.verdicts[ACC(s)];
  return v ? VK[v] : "n";
}
const S = { s: 1, open: null, g: null, el: {}, shown: {}, last: 0, t0: -1e9, dirty: true, rp: null, rpNext: 0, rpAt: 0,
            started: false, enterT: -1e9, entered: false, from: 1, d1t: -1e9, burst: null };

/* Geometry, in plate units (x right, y down; z toward the viewer). */
function geo() {
  return narrow.matches
    ? { w: 480, cx: 240, D: 2000, r: 22, deep: 30, blur: 12, phone: true, fs: 17.5, fb: 84, fn: 17.5, lh: 23, fg: 17, fk: 17,
        setX: 24, setY: 50, bigX: 20, bigY: 132, labX: 24, labY: [178, 204, 234], top: 352,
        sx0: 52, sx1: 456, bead: 26, agX: 26, agY: 22, gx0: 52, gx1: 456, gv: 140, pitch: 50, gap: 30 }
    : { w: 1000, cx: 500, D: 2200, r: 30, deep: 40, blur: 16, phone: false, fs: 14, fb: 84, fn: 15.5, lh: 20.5, fg: 13, fk: 13,
        setX: 58, setY: 58, bigX: 52, bigY: 136, labX: 320, labY: [98, 120, 146], top: 222,
        sx0: 98, sx1: 538, bead: 70, agX: 558, agY: 0, gx0: 606, gx1: 952, gv: 122, pitch: 40, gap: 18 };
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k];
}
function rounded(g, [x0, y0, x1, y1], r, z) {  // a rounded rectangle at depth z
  const p = [], corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}

/* Lines of a text that fit a width, measured with the page's own font. */
function wrap(text, width, fs, cls) {
  const m = S.meas;
  m.setAttribute("font-size", fs); m.setAttribute("class", cls);
  const out = [];
  let line = "";
  text.split(" ").forEach(w => {
    const next = line ? line + " " + w : w;
    m.textContent = next;
    if (line && m.getComputedTextLength() > width) { out.push(line); line = w; } else line = next;
  });
  if (line) out.push(line);
  return out;
}

/* The layout: each sentence a block, its claims beside it (on a phone, under it). Every row's box is kept for clicks. */
function layout(g) {
  const L = { nodes: [], rows: {} };
  let y = g.top;
  const sw = g.sx1 - g.sx0;
  NODES.forEach(n => {
    const lines = wrap(n.text, sw, g.fn, "sn");
    let ty = y, h = lines.length * g.lh;
    const nd = { y, lines, ly: lines.map((_, j) => y + j * g.lh) };
    if (n.i === 4) {  // the clause slots: the account's clause, and in the disagreement view a second one
      nd.cv = Object.fromEntries(Object.entries(CLAUSE_TEXT()).map(([k, s]) => [k, wrap(s, sw, g.fn, "cl")]));
      const n0 = Math.max(nd.cv["1"].length, nd.cv["2"].length, nd.cv["3"].length, nd.cv.s2.length), n1 = nd.cv.s1.length;
      nd.cy = [y + h, y + h + n0 * g.lh]; h += (n0 + n1) * g.lh;
    }
    if (n.i === 5) {
      const ex = EXTRA_LINES(g);
      if (g.phone) { nd.ey = ex.map((_, j) => y + h + 4 + j * g.lh * .9); h += ex.length * g.lh * .9 + 4; }
      else nd.ey = ex.map((_, j) => y + 2 + j * g.lh * .92);
      nd.ex = ex;
    }
    let gy = g.phone ? y + h + 14 : y - 6;
    n.tests.forEach(t => {
      const tall = t.d1 ? g.fg + 8 : 0;  // d1 names its two accounts' ranges under its axis
      L.rows[t.key] = { y: gy, tall, box: [g.gx0 - 6, gy - g.fg - 5, g.gx1 + 6, gy + 20 + tall] };
      gy += g.pitch + tall;
    });
    const gh = n.tests.length ? gy - (g.phone ? y + h + 14 : y - 6) : 0;
    const block = g.phone ? h + (gh ? gh + 14 : 0) : Math.max(h, gh - 8);
    nd.box = [g.phone ? 10 : g.bead - 16, y - g.fn - 2, g.sx1 + 8, y + h - g.fn + 4];
    nd.h = block;
    L.nodes.push(nd);
    y += block + g.gap;
  });
  L.bottom = y - g.gap;
  return L;
}
const CLAUSE_TEXT = () => ({ "1": C.clauses["1"], "2": C.clauses["2"], "3": C.clauses["3"],
  s2: "Account 2: " + C.clauses["2"].replace(/^and /, ""), s1: "Account 1: " + C.clauses["1"].replace(/^and /, "") });
const EXTRA_LINES = g => C.extra3.flatMap(s => wrap(s, g.phone ? g.sx1 - g.sx0 : g.gx1 - g.gx0, g.fg + .5, "ex"));

const KEYS = [["rg", "Account's range, fixed before"], ["nl", "Null's range"], ["h", "Holds"], ["r", "Refuted"], ["u", "Undecided"], ["adv", "Adversary's value, retest"]];
function build() {
  const g = S.g = geo(), svg = $("svg");
  svg.innerHTML = `<text id="meas" x="-999" y="-999" style="opacity:0"></text>`;
  S.meas = svg.firstChild;
  S.L = layout(g);
  g.keyY = S.L.bottom + (g.phone ? 34 : 26);
  g.rpY = g.keyY + (g.phone ? 118 : 0);
  g.h = g.rpY + (g.phone ? 40 : 26);
  g.cy = g.h / 2;
  g.a = g.phone ? [4, 8, g.w - 4, g.h - 8] : [24, 16, 976, g.h - 10];
  const [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const X = (cls, id, fs, extra = "") => `<text class="${cls}" id="${id}" font-size="${fs}"${extra}></text>`;
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  let fg = `<path class="spine" id="spine"/>`;
  NODES.forEach(n => {
    fg += `<circle class="bead" id="bd${n.i}" r="${g.phone ? 11 : 12}"/>`;
    ["1", "2", "3"].forEach(k => { fg += `<circle class="ag ${n.st[k]}" id="ag${n.i}${k}" r="3.3"/>`; });
  });
  fg += ["1", "2", "3"].map(k => `<circle class="agc" id="agc${k}" r="0"/>`).join("");
  T.forEach(t => {
    fg += `<path class="ax" id="ax${t.i}"/>`;
    if (t.d1) fg += `<rect class="rg2" id="rgA${t.i}" height="9"/><rect class="rg" id="rgB${t.i}" height="9"/>`;
    else fg += `<rect class="rg" id="rg${t.i}" height="9"/>`;
    fg += `<path class="adv" id="adv${t.i}"/><rect class="nl" id="nl${t.i}" height="9"/><path class="ci" id="ci${t.i}"/><circle class="halo" id="ha${t.i}" r="0"/><circle class="pt" id="pt${t.i}" r="0"/>`;
  });
  fg += `<circle class="burst" id="bu" r="0"/>`;
  fg += `<g class="key">` + KEYS.map(([k], j) => k === "rg" ? `<rect class="rg" id="kd${j}" width="18" height="9"/>` :
    k === "nl" ? `<rect class="nl" id="kd${j}" width="18" height="9"/>` : k === "adv" ? `<path class="adv" id="kd${j}"/>` : `<circle class="pt ${k}" id="kd${j}" r="4.2"/>`).join("") + `</g>`;
  let tx = X("set", "set", g.fs) + X("big", "big", g.fb) + X("lab0", "bl0", g.fs + 2.5) + X("lab", "bl1", g.fs + 1.5) + X("lab2", "bl2", g.fs + 1.5) +
    X("hd", "h1", g.fg) + X("hd", "h2", g.fg) + X("hd", "h3", g.fg, ` text-anchor="middle"`);
  ["1", "2", "3"].forEach(k => { tx += X("hd", "ah" + k, g.fg - 1, ` text-anchor="middle"`); });
  NODES.forEach((n, i) => {
    tx += X("num", "nn" + i, g.fg, ` text-anchor="middle"`);
    S.L.nodes[i].lines.forEach((_, j) => { tx += X("sn", `s${i}_${j}`, g.fn); });
  });
  tx += X("cl", "cl0", g.fn) + X("cl", "cl1", g.fn);
  S.L.nodes[5].ex.forEach((_, j) => { tx += X("ex", "ex" + j, g.fg + .5); });
  T.forEach(t => {
    tx += X("gl", "gl" + t.i, g.fg) + X("gv", "gv" + t.i, g.fg, ` text-anchor="end"`);
    if (t.d1) tx += X("bl", "bl1_" + t.i, g.fg - (g.phone ? 0 : .5), ` text-anchor="middle"`) + X("bl", "bl2_" + t.i, g.fg - (g.phone ? 0 : .5), ` text-anchor="middle"`);
  });
  tx += KEYS.map((_, j) => X("kt", "kt" + j, g.fk)).join("") + X("kt", "ktA", g.fk) + X("rp", "rp", g.fk, g.phone ? "" : ` text-anchor="end"`);
  svg.innerHTML += "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<radialGradient id="bead" cx=".32" cy=".28" r=".9">${stop(0, "var(--glass-hi)")}${stop(1, "var(--glass)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${g.cy}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .03)}" width="${aw}" height="${ah}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .3)}" cy="${f(ay0 + ah * .2)}" rx="${f(aw * .3)}" ry="${f(ah * .16)}" transform="rotate(-14 ${f(ax0 + aw * .3)} ${f(ay0 + ah * .2)})" fill="url(#spec)"/>` +
    `<g id="fg">${fg}</g><g id="tx" class="read"><path class="hair" id="hair"/><rect class="selbox" id="sel" width="0" height="0"/>${tx}</g>`;
  S.el = {}; S.shown = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  S.meas = S.el.meas;
  statics();
  S.dirty = true;
}

/* Texts and positions that do not move with the state: written once per build, in plate units. */
function statics() {
  const g = S.g, E = S.el, L = S.L;
  const at = (el, x, y) => { el.setAttribute("x", f(x)); el.setAttribute("y", f(y)); };
  at(E.set, g.setX, g.setY); at(E.big, g.bigX, g.bigY);
  g.labY.forEach((y, j) => at(E["bl" + j], g.labX, y));
  E.set.textContent = `Round 15 · three accounts of the same ${C.counts.facts} tested facts`;
  E.bl0.textContent = "new claims held their test on stored data.";
  E.bl1.textContent = `${C.counts.refuted} refuted, ${C.counts.undecided} undecided. Retest: ${C.counts.not_separated} not separated.`;
  const hy = g.top - (g.phone ? 46 : 34);
  E.hair.setAttribute("d", `M${g.phone ? 24 : 58} ${f(hy - (g.phone ? 26 : 22))}H${g.phone ? 456 : 942}`);
  at(E.h1, g.phone ? 24 : g.bead - 12, hy); E.h1.textContent = "The account, in plain words";
  at(E.h2, g.gx0, hy); E.h2.textContent = g.phone ? "" : "New claims, against ranges fixed in advance";
  at(E.h3, -99, -99); E.h3.textContent = "";
  ["1", "2", "3"].forEach((k, j) => {
    if (g.phone) { at(E["ah" + k], -99, -99); return; }
    at(E["ah" + k], g.agX + 14 * j, hy);
    E["ah" + k].textContent = k;
  });
  // the spine and beads
  const by = n => L.nodes[n.i].y - g.fn * .35;
  E.spine.setAttribute("d", `M${g.bead} ${f(by(NODES[0]))}V${f(by(NODES[5]))}`);
  if (g.phone) E.spine.setAttribute("d", `M${g.bead} ${f(by(NODES[0]))}V${f(by(NODES[5]))}`);
  NODES.forEach(n => {
    const nd = L.nodes[n.i], y = by(n);
    E["bd" + n.i].setAttribute("cx", g.bead); E["bd" + n.i].setAttribute("cy", f(y));
    at(E["nn" + n.i], g.bead, y + g.fg * .36); E["nn" + n.i].textContent = n.i + 1;
    nd.lines.forEach((s, j) => { const e = E[`s${n.i}_${j}`]; at(e, g.sx0, nd.ly[j]); e.textContent = s; });
    ["1", "2", "3"].forEach((k, j) => {
      const e = E[`ag${n.i}${k}`];
      if (g.phone) { e.setAttribute("cx", g.bead - 9 + 9 * j); e.setAttribute("cy", f(y + g.agY)); }
      else { e.setAttribute("cx", g.agX + 14 * j); e.setAttribute("cy", f(y)); }
    });
  });
  const n5 = L.nodes[4];
  S.cl = { x: g.sx0, y: n5.cy, lh: g.lh, cv: n5.cv };
  const n6 = L.nodes[5];
  n6.ex.forEach((s, j) => { const e = E["ex" + j]; at(e, g.phone ? g.sx0 : g.gx0, n6.ey[j]); e.textContent = s; });
  // the rows of the claims
  T.forEach(t => {
    const rw = L.rows[t.key], ay = rw.y + (g.phone ? 15 : 13);
    at(E["gl" + t.i], g.gx0, rw.y); at(E["gv" + t.i], g.gx1, ay + g.fg * .36);
    E["gl" + t.i].textContent = `${t.d1 ? "1 vs 2" : t.acc[0]} · ${t.label}`;
    E["ax" + t.i].setAttribute("d", `M${g.gx0} ${f(ay + .5)}H${g.gx1 - g.gv}`);
    t.X = xscale(t, g);
    t.ay = ay;
    const band = (el, r) => { const a = t.X(r[0]), b = t.X(r[1]); el.setAttribute("x", f(a)); el.setAttribute("y", f(ay - 4.5)); el.setAttribute("width", f(Math.max(1, b - a))); };
    band(E["nl" + t.i], t.r.ranges.null);
    const adv = Object.values(t.r.retest)[0];  // the engine-16 adversary's value, a short upright tick
    E["adv" + t.i].setAttribute("d", adv ? `M${f(t.X(adv.adversary))} ${f(ay - 8)}V${f(ay + 9)}` : "");
    if (t.d1) {
      band(E["rgA" + t.i], t.r.ranges["1"]); band(E["rgB" + t.i], t.r.ranges["2"]);
      const mid = r => (t.X(r[0]) + t.X(r[1])) / 2;
      at(E["bl1_" + t.i], mid(t.r.ranges["1"]), ay + 10 + g.fg); at(E["bl2_" + t.i], mid(t.r.ranges["2"]), ay + 10 + g.fg);
    } else band(E["rg" + t.i], t.r.ranges[t.acc[0]]);
  });
  // the key
  const ky = g.keyY, xs = g.phone ? [24, 274, 24, 150, 276, 24] : [58, 286, 398, 462, 536, 628], ys = g.phone ? [ky, ky, ky + 30, ky + 30, ky + 30, ky + 60] : [ky, ky, ky, ky, ky, ky];
  KEYS.forEach(([k, name], j) => {
    const d = E["kd" + j];
    if (k === "rg" || k === "nl") { d.setAttribute("x", xs[j]); d.setAttribute("y", f(ys[j] - 4.5)); }
    else if (k === "adv") d.setAttribute("d", `M${xs[j] + 6} ${f(ys[j] - 8)}V${f(ys[j] + 8)}`);
    else { d.setAttribute("cx", xs[j] + 6); d.setAttribute("cy", f(ys[j])); }
    at(E["kt" + j], xs[j] + (k === "rg" || k === "nl" ? 26 : k === "adv" ? 14 : 16), ys[j] + g.fk * .36);
    E["kt" + j].textContent = name;
  });
  at(E.ktA, g.phone ? 24 : 808, g.phone ? ky + 90 : ky + g.fk * .36);
  E.ktA.textContent = g.phone ? "1, 2, 3: the three accounts; a dot: it states the sentence" : "1, 2, 3: accounts";
  E.rp.setAttribute("x", g.phone ? 24 : 942); E.rp.setAttribute("y", f(g.phone ? g.rpY + 28 : g.setY));
}
/* Each claim's own axis: its ranges and interval with a margin; a range beyond the axis ends open. */
function xscale(t, g) {
  const r = t.r, xs = [r.value, r.lo, r.hi, ...Object.values(r.ranges).flat()];
  let a = Math.min(...xs), b = Math.max(...xs);
  if (t.dom) { a = t.dom[0]; b = t.dom[1]; }
  const pad = (b - a) * .04;
  a -= pad; b += pad;
  return x => g.gx0 + (g.gx1 - g.gv - g.gx0) * (clamp(x, a, b) - a) / (b - a);
}

/* The state's words: the clause of sentence 5, the line under the large number, which account column is lit. */
function stateText() {
  const s = S.s, k = ACC(s), A = C.counts.accounts, x = A[k], E = S.el;
  const txt = (id, v) => { if (S.shown[id] !== v) E[id].textContent = S.shown[id] = v; };
  const d = x.d1 === "holds" ? "it won the one disagreement" : x.d1 === "refuted" ? "it lost the one disagreement" : "it took no side in the one disagreement";
  const line = s === 3 ? `The judge found ${C.counts.disagreements} point where the accounts disagree; one test decided it.`
    : `Account ${k}: ${x.held} of ${x.tested} held${x.refuted ? `, ${x.refuted} refuted` : ""}${x.undecided ? `, ${x.undecided} undecided` : ""}; ${d}.`;
  if (S.shown.bl2 === line) return;
  S.shown.bl2 = line;
  const g = S.g, parts = g.phone ? line.replace("; ", ";\n").split("\n") : [line];  // two lines on a phone
  E.bl2.innerHTML = parts.map((p, i) => `<tspan x="${g.labX}" y="${f(g.labY[2] + i * (g.fs + 6))}">${esc(p)}</tspan>`).join("");
}

/* Where the moving parts are now. The d1 value travels from the null value 0 to its measured value on each change. */
function place(now) {
  const g = S.g, E = S.el;
  E.back.setAttribute("d", rounded(g, g.a, g.r, -g.deep));
  E.plate.setAttribute("d", rounded(g, g.a, g.r, 0));
  const z = 10, A = proj(g, 0, 0, z), B = proj(g, g.w, 0, z), Cc = proj(g, 0, g.h, z);
  const m6 = [(B[0] - A[0]) / g.w, (B[1] - A[1]) / g.w, (Cc[0] - A[0]) / g.h, (Cc[1] - A[1]) / g.h, A[0], A[1]];
  E.fg.setAttribute("transform", `matrix(${m6.map(v => v.toFixed(4)).join(" ")})`);
  // the words keep upright: the same move and scale, with no turn
  E.tx.setAttribute("transform", `matrix(${m6[0].toFixed(4)} 0 0 ${m6[3].toFixed(4)} ${m6[4].toFixed(2)} ${m6[5].toFixed(2)})`);
  const s = S.s, k = ACC(s), split = s === 3;
  // the large number counts with the claims as they land in the entrance
  const landed = T.filter(t => !t.d1 && landP(t, now) >= 1 && vOf(t, s) === "h").length;
  const txt = (id, v) => { if (S.shown[id] !== v) E[id].textContent = S.shown[id] = v; };
  txt("big", `${landed} of ${C.counts.tested}`);
  E.bl0.style.opacity = E.bl1.style.opacity = E.bl2.style.opacity = clamp((now - S.enterT) / 600, 0, 1).toFixed(2);
  if (!S.dirty && !moving(now)) { replay(now); return; }
  const sel = S.open && TK[S.open] ? TK[S.open] : null, seln = S.open && NK[S.open] ? NK[S.open] : null;
  // the clause of sentence 5: the account's own, or both in the disagreement view; it changes with the d1 value
  const dp = clamp((now - S.d1t) / 900, 0, 1), cf = still.matches ? 1 : clamp((now - S.d1t) / 350, 0, 1);
  const lines = [split ? S.cl.cv.s2 : S.cl.cv[k], split ? S.cl.cv.s1 : []];
  lines.forEach((ls, j) => {  // each clause in its wrapped lines; it slides in from a few units above
    const el = E["cl" + j], key = ls.join("\n") + "|" + f((1 - cf) * -6);
    if (S.shown["cl" + j] !== key) {
      S.shown["cl" + j] = key;
      el.innerHTML = ls.map((s, i) => `<tspan x="${S.cl.x}" y="${f(S.cl.y[j] + i * S.cl.lh + (1 - cf) * -6)}">${esc(s)}</tspan>`).join("");
    }
  });
  E.cl0.setAttribute("class", "cl" + (k === "3" && !split ? " q" : ""));
  E.cl1.setAttribute("class", "cl t1");
  E.cl0.style.opacity = cf.toFixed(2); E.cl1.style.opacity = cf.toFixed(2);
  // dimming: the disagreement view keeps sentence 5 and its claims; a selection keeps itself
  const dimN = n => (split && n.i !== 4) || (seln && seln !== n) || (sel && sel.node !== n.i) ? .26 : 1;
  const dimT = t => (split && !t.d1 && t.node !== 4) || (split && t.key !== "d1" && t.key !== "a2c3" && t.key !== "a1c3" && false) || (sel && sel !== t) || (seln && seln.i !== t.node) ? .26 : 1;
  NODES.forEach((n, i) => {
    const o = dimN(n).toString();
    S.L.nodes[i].lines.forEach((_, j) => { E[`s${i}_${j}`].style.opacity = o; });
    E["nn" + i].style.opacity = o; E["bd" + i].style.opacity = o;
    ["1", "2", "3"].forEach(a => { E[`ag${i}${a}`].style.opacity = (dimN(n) * (split && a === "3" ? .35 : 1)).toFixed(2); });
  });
  if (dimN(NODES[4]) < 1) { E.cl0.style.opacity = E.cl1.style.opacity = (.26 * cf).toFixed(2); }
  // account 3's extra claim beside sentence 6
  const ex = k === "3" && !split ? cf : 0;
  S.L.nodes[5].ex.forEach((_, j) => { E["ex" + j].style.opacity = (ex * dimN(NODES[5])).toFixed(2); });
  // the lit account column
  ["1", "2", "3"].forEach((a, j) => {
    const c = E["agc" + a], on = !split && a === k;
    if (g.phone) { c.setAttribute("r", 0); return; }
    c.setAttribute("cx", g.agX + 14 * j); c.setAttribute("cy", f((S.L.nodes[0].y + S.L.nodes[5].y) / 2 - g.fn * .35));
    c.setAttribute("r", 0);
    E["ah" + a].style.fontWeight = on ? 760 : 540;
    E["ah" + a].style.fill = on ? "var(--blue)" : "";
  });
  // the claims
  T.forEach(t => {
    const v = vOf(t, s), p = landP(t, now), e = ease(p), o = dimT(t);
    let val = t.r.value, lo = t.r.lo, hi = t.r.hi;
    if (t.d1) { const q = still.matches ? 1 : ease(dp) * e; val = mix(0, val, q); lo = mix(0, lo, q); hi = mix(0, hi, q); }
    else { val = mix(0, val, e); lo = mix(val, lo, e); hi = mix(val, hi, e); }
    const x0 = t.X(t.d1 ? 0 : nullMid(t)), X = x => mix(x0, t.X(x), t.d1 ? 1 : e), cx = t.d1 ? t.X(val) : X(t.r.value);
    const pt = E["pt" + t.i], ci = E["ci" + t.i], ha = E["ha" + t.i];
    const arrived = t.d1 ? dp >= 1 && p >= 1 : p >= 1;
    const vc = arrived ? v : t.d1 ? "n" : "n";
    pt.setAttribute("class", "pt " + vc); ci.setAttribute("class", "ci " + (arrived ? v : "n"));
    pt.setAttribute("cx", f(cx)); pt.setAttribute("cy", f(t.ay + .5)); pt.setAttribute("r", p > 0 ? 4.4 : 0);
    const l = t.d1 ? t.X(lo) : X(t.r.lo), h = t.d1 ? t.X(hi) : X(t.r.hi);
    ci.setAttribute("d", p > 0 ? `M${f(l)} ${f(t.ay + .5)}H${f(h)}` : "");
    ha.setAttribute("cx", f(cx)); ha.setAttribute("cy", f(t.ay + .5)); ha.setAttribute("r", 7.4);
    ha.style.opacity = arrived && v === "h" ? (.32 * o * getBloom()).toFixed(2) : 0;
    pt.style.opacity = ci.style.opacity = o.toString();
    const ownT = t.d1 ? !!t.r.verdicts[k] || split : t.acc[0] === k;
    E["gl" + t.i].setAttribute("class", "gl" + (ownT && !split ? " own" : split && t.d1 ? " own" : ""));
    ["gl", "gv", "ax", "nl", "adv"].forEach(id => { E[id + t.i].style.opacity = o.toString(); });
    txt("gv" + t.i, arrived ? `${fv(t.r.value, t.unit)} · ${VFULL[v]}` : "");
    E["gv" + t.i].setAttribute("class", "gv " + v);
    if (t.d1) {
      const ownBand = split ? "2" : k;  // the band of the account read is lit; with no side, neither
      const a = E["rgA" + t.i], b = E["rgB" + t.i];
      a.setAttribute("class", ownBand === "1" ? "rg" : "rg2"); b.setAttribute("class", ownBand === "2" ? "rg" : "rg2");
      a.style.opacity = b.style.opacity = o.toString();
      txt("bl1_" + t.i, split ? "account 1" : "1"); txt("bl2_" + t.i, split ? "account 2" : "2");
      E["bl1_" + t.i].setAttribute("class", "bl" + (ownBand === "1" ? " own" : ""));
      E["bl2_" + t.i].setAttribute("class", "bl" + (ownBand === "2" ? " own" : ""));
      E["bl1_" + t.i].style.opacity = E["bl2_" + t.i].style.opacity = o.toString();
    } else E["rg" + t.i].style.opacity = o.toString();
  });
  // a burst where the d1 value lands
  const bt = (now - S.d1t - 900) / 900;
  if (!still.matches && bt >= 0 && bt <= 1 && S.d1t > 0) {
    const q = ease(bt);
    E.bu.setAttribute("cx", f(D1.X(D1.r.value))); E.bu.setAttribute("cy", f(D1.ay + .5));
    E.bu.setAttribute("r", f(5 + 16 * q)); E.bu.style.opacity = (1 - bt).toFixed(2); E.bu.setAttribute("stroke-width", f(1.6 * (1 - bt) + .3));
  } else if (!S.rp) E.bu.setAttribute("r", 0);
  // the selection box
  const box = sel ? S.L.rows[sel.key].box : seln ? S.L.nodes[seln.i].box : null;
  if (box) { E.sel.setAttribute("x", f(box[0])); E.sel.setAttribute("y", f(box[1])); E.sel.setAttribute("width", f(box[2] - box[0])); E.sel.setAttribute("height", f(box[3] - box[1])); E.sel.setAttribute("rx", 6); }
  else { E.sel.setAttribute("width", 0); E.sel.setAttribute("height", 0); }
  S.dirty = moving(now);
  replay(now);
}
const nullMid = t => (t.r.ranges.null[0] + t.r.ranges.null[1]) / 2;
/* The entrance: each claim's value travels from the middle of the null's range to its measured value, 90 ms apart. */
const landP = (t, now) => S.entered ? 1 : clamp((now - S.enterT - 500 - 90 * t.i) / 800, 0, 1);
const moving = now => (!S.entered && now - S.enterT < 500 + 90 * T.length + 900) || now - S.d1t < 1900;
function getBloom() { return parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--bloom")) || 1; }

/* The replay: about every 2.6 s the next test, in the order its row was added to the record, lights its value, and the
   line at the top right names it. Stops while something is open. */
function replay(now) {
  const E = S.el, g = S.g;
  if (still.matches || S.open || moving(now) || now - S.enterT < 3000) { if (S.shown.rp !== "") { E.rp.textContent = S.shown.rp = ""; } return; }
  const list = T.slice().sort((a, b) => a.r.added.localeCompare(b.r.added) || a.i - b.i);
  if (!S.rp && now > S.rpNext) S.rp = { t: list[S.rpAt++ % list.length], t0: now };
  if (!S.rp) return;
  const t = S.rp.t, p = clamp((now - S.rp.t0) / 1300, 0, 1), x = t.X(t.r.value);
  E.bu.setAttribute("cx", f(x)); E.bu.setAttribute("cy", f(t.ay + .5));
  E.bu.setAttribute("r", f(5 + 13 * ease(p))); E.bu.style.opacity = (1 - p).toFixed(2); E.bu.setAttribute("stroke-width", f(1.5 * (1 - p) + .3));
  const v = vOf(t, S.s), line = `${t.r.added.slice(11, 16)} UTC · ${t.label} · ${VFULL[v]}`;
  if (S.shown.rp !== line) E.rp.textContent = S.shown.rp = line;
  E.rp.style.opacity = .9;
  if (p >= 1) { S.rp = null; S.rpNext = now + 1300; }
}
function stopReplay() { S.rp = null; S.rpNext = performance.now() + 2200; if (S.el.bu) S.el.bu.setAttribute("r", "0"); }

/* Always on: the plate sways by a few degrees and leans toward the mouse, about 30 frames a second. With reduced motion
   the page shows one still frame per state. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = now / 1000;
  V.px += (V.tx - V.px) * .1; V.py += (V.ty - V.py) * .1;
  aim(3 * Math.sin(t * .13) + 2.6 * V.px, 1.6 * Math.sin(t * .09) - 1.6 * V.py);
  place(now);
}
/* A change of state: the shared sentences stay; the clause of sentence 5 and the d1 value replay. */
function setState(s, opts = {}) {
  const now = performance.now();
  const changed = s !== S.s;
  S.s = s;
  if (changed && !opts.instant) S.d1t = now; else if (opts.instant) S.d1t = -1e9;
  S.dirty = true;
  stopReplay();
  stateText();
  $("switch").querySelectorAll("button").forEach((b, j) => b.setAttribute("aria-pressed", j === s));
  $("split").setAttribute("aria-pressed", s === 3);
  const k = ACC(s), x = C.counts.accounts[k];
  $("svg").setAttribute("aria-label", `${SNAME[s]}: the account in six plain sentences, each with the new claims that test it. ` +
    `${C.counts.held} of ${C.counts.tested} new claims held. Arrow keys change the account; Enter opens a claim.`);
  if (still.matches) { aim(0, 0); place(now); }
}

/* The side column: the five panels and two examples, one sentence, or one claim. */
function gaugeSvg(t) {
  const r = t.r, s = S.s, v = vOf(t, s), k = ACC(s), W = 340, x0 = 14, x1 = 326;
  const xs = [r.value, r.lo, r.hi, ...Object.values(r.ranges).flat(), ...(r.null_value != null ? [r.null_value] : [])];
  let a = Math.min(...xs), b = Math.max(...xs);
  if (t.dom) { a = t.dom[0]; b = t.dom[1]; }
  const pad = (b - a) * .05; a -= pad; b += pad;
  const X = x => x0 + (x1 - x0) * (clamp(x, a, b) - a) / (b - a);
  const lab = (x, y, s, anchor = "middle") => `<text class="g-t" x="${f(x)}" y="${y}" font-size="11.5" text-anchor="${anchor}">${s}</text>`;
  const band = (rg, cls, name, y) => {
    const p = X(rg[0]), q = X(rg[1]), open = t.dom && rg[1] > t.dom[1];
    return `<rect class="${cls}" x="${f(p)}" y="28" width="${f(Math.max(1, q - p))}" height="14"/>` +
      lab((p + q) / 2, y, name + " " + fv(rg[0]) + " to " + fv(rg[1]) + (open ? " ›" : ""));
  };
  let h = `<svg class="gauge" viewBox="0 0 ${W} 92" aria-hidden="true">`;
  h += band(r.ranges.null, "nl", "null", 18);
  if (t.d1) { h += band(r.ranges["1"], (s === 3 ? "2" : k) === "1" ? "rg" : "rg2", "account 1", 62); h += band(r.ranges["2"], (s === 3 ? "2" : k) === "2" ? "rg" : "rg2", "account 2", 18); }
  else h += band(r.ranges[t.acc[0]], "rg", "account " + t.acc[0], 62);
  h += `<path class="ax" d="M${x0} 42.5H${x1}"/>`;
  if (r.null_value != null) h += `<path d="M${f(X(r.null_value))} 24V46" stroke="var(--faint)" stroke-width="1.4"/>` + lab(X(r.null_value), 84, "null measured " + fv(r.null_value, t.unit));
  h += `<path class="ci ${v}" d="M${f(X(r.lo))} 35H${f(X(r.hi))}"/><circle class="pt ${v}" cx="${f(X(r.value))}" cy="35" r="5.5"/>`;
  return h + `</svg>`;
}
function testPane(t) {
  const r = t.r, s = S.s, v = vOf(t, s), node = NODES[t.node];
  const who = t.d1 ? "The judge's one disagreement, between accounts 1 and 2" : `Account ${t.acc[0]} · new claim ${t.key.slice(2)}`;
  const verdict = t.d1 ? `Account 2 ${r.verdicts["2"]}, account 1 ${r.verdicts["1"]}` : CAP(VFULL[v]);
  const rg = x => `${fv(x[0])} to ${fv(x[1])}`;
  let h = `<div class="dhead"><h2>${esc(t.label)}</h2><button class="close" data-open="">Close</button></div>`;
  h += `<p class="tag">${who} · <b>${esc(verdict)}</b></p>`;
  if (t.d1) {
    h += `<h3>What the accounts disagree on, in the judge's words</h3><p class="quote">${esc(minus(r.about))}</p>`;
    h += ["2", "1"].map(k => `<p class="why"><b>Account ${k}:</b> ${esc(minus(r.positions["account-" + k]))}</p>`).join("");
  }
  h += `<h3>The claim, in the plan's words</h3><p class="quote">${esc(minus(r.claim))}</p>`;
  h += gaugeSvg(t);
  const ranges = Object.entries(r.ranges).filter(([k]) => k !== "null").map(([k, x]) => `account ${k} ${rg(x)}`).join(", ");
  h += `<p class="why">Measured: <b>${fv(r.value, t.unit)}</b> (90 % interval ${fv(r.lo)} to ${fv(r.hi)}), n ${r.n} ${esc(t.nunit)}. ` +
    `Ranges fixed before the test: ${ranges}; the null ${rg(r.ranges.null)}` + (r.null_value != null ? `; the null measured on the same rows ${fv(r.null_value, t.unit)}` : "") + ".</p>";
  h += `<h3>The statistic</h3><p class="why">${esc(minus(r.statistic))}</p>`;
  h += `<h3>The null, in the plan's words</h3><p class="why">${esc(minus(r.null))}</p>`;
  if (t.caveat) h += `<p class="case">${esc(t.caveat)}</p>`;
  Object.entries(r.retest || {}).forEach(([k, x]) => {
    h += `<p class="case"><b>Retest under engine 16</b> (<a href="/#${esc(x.result)}">${esc(x.result)}</a>): ${esc(x.verdict)}; ` +
      `the adversary's value, ${fv(x.adversary, t.unit)}, lies inside the interval. ${esc(minus(x.measured))}</p>`;
  });
  h += `<h3>Measured, as the record holds it</h3>` + Object.entries(r.measured).filter((e, j, all) => j === 0 || e[1] !== all[0][1])
    .map(([k, m]) => `<p class="why">${Object.keys(r.measured).length > 1 ? `<b>Account ${k}:</b> ` : ""}${esc(minus(m))}</p>`).join("");
  h += `<ul class="facts"><li>Tests sentence <button class="lnk" data-open="${node.key}">${node.i + 1}</button> of the account</li>` +
    (r.why_new ? `<li>Why it is new: ${esc(minus(r.why_new))}</li>` : "") +
    `<li>Test ${esc(t.folder)}: studies/theory/results/direct/${esc(t.folder)}/metrics.json</li>` +
    `<li>Board item <a href="/#${esc(r.result)}">${esc(r.result)}</a>; row added ${esc(r.added.slice(11, 16))} UTC</li></ul>`;
  return h + steps();
}
function nodePane(n) {
  const A = C.record.accounts, s = S.s;
  let h = `<div class="dhead"><h2>Sentence ${n.i + 1} of 6</h2><button class="close" data-open="">Close</button></div>`;
  h += `<p class="lead">${esc(n.text)}${n.i === 4 ? " " + esc(C.clauses["2"]) : ""}</p>`;
  h += `<h3>Account 2, sentence ${n.i + 1}, verbatim</h3><p class="quote">${esc(minus(A["2"].sentences[n.i]))}</p>`;
  const stand = { same: "states the same", other: "states otherwise", none: "takes no side on the last part" };
  [["1", n.a1], ["3", n.a3]].forEach(([k, idx]) => {
    h += `<h3>Account ${k}, sentence${idx.length > 1 ? "s" : ""} ${idx.join(" and ")} (${stand[n.st[k]]})</h3>` +
      idx.map(j => `<p class="quote small">${esc(minus(A[k].sentences[j - 1]))}</p>`).join("");
  });
  if (n.i === 5) h += `<p class="case">Account 3 marks one of the ${C.counts.facts} facts as against it: ${esc(A["3"].contradicts.map(c => c[0] + ". " + c[1]).join(" "))}</p>`;
  h += `<ul class="facts">` + (n.tests.length ? n.tests.map(t => `<li><button class="lnk" data-open="${t.key}">${esc(t.label)}</button>: ${esc(t.d1 ? `account 2 ${t.r.verdicts["2"]}, account 1 ${t.r.verdicts["1"]}` : `account ${t.acc[0]}, ${VFULL[vOf(t, s)]}`)}</li>`).join("")
    : `<li>No new claim of round 15 tests this sentence.</li>`) + `</ul>`;
  return h + steps();
}
const steps = () => `<div class="steps"><button data-step="-1">‹ Previous</button><button data-step="1">Next ›</button></div>`;
const ORDER = () => NODES.flatMap(n => [n.key, ...n.tests.map(t => t.key)]);
function pane() {
  const p = C.panels.find(p => p[0] === S.open), t = S.open && TK[S.open], n = S.open && NK[S.open];
  const fact = x => Array.isArray(x) ? `<li><a href="${esc(x[1])}">${esc(x[0])}</a></li>` : `<li>${esc(minus(x))}</li>`;
  $("pane").innerHTML = t ? testPane(t) : n ? nodePane(n) : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(fact).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>` +
      `<ul class="more ex">${C.examples.map(x => `<li><button data-open="${x[0]}">${esc(x[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
  S.dirty = true;
}
/* The state and what is open are one value in the address: #<a1|a3|split>/<panel, sentence or claim>. */
function address(push) {
  const parts = [S.s !== 1 ? STATES[S.s] : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const k = STATES.indexOf(parts.find(x => STATES.includes(x))), s = k >= 0 ? k : 1;
  S.open = parts.find(x => C.panels.some(p => p[0] === x) || TK[x] || NK[x]) || null;
  if (first === true) {
    setState(s, { instant: true });
    const travel = !still.matches && !location.hash;
    if (travel) watchEntrance(); else { S.entered = true; S.enterT = -1e9; }
  } else if (s !== S.s) setState(s);
  pane();
  place(performance.now());
}
function watchEntrance() {
  S.enterT = 1e12;
  const go = () => { if (S.started) return; S.started = true; S.enterT = performance.now() + 400; S.dirty = true;
                     setTimeout(() => { S.entered = true; S.dirty = true; }, 500 + 90 * T.length + 1000); };
  if (!("IntersectionObserver" in window)) return go();
  const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); go(); } }, { threshold: .3 });
  io.observe($("svg"));
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" }); };
function open(key) {
  const was = S.open;
  S.open = key || null;
  if (key) stopReplay();
  address(true);
  pane();
  place(performance.now());
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  else if (!key) $("svg").focus({ preventScroll: true });
}
function choose(s) {
  if (s === S.s) return;
  setState(s);
  pane();
  address(false);
}

/* The picture's control: click a sentence or a claim's row to open it. The point is mapped into plate units. */
const svg = $("svg");
function hit(e) {
  const mi = S.el.tx.getScreenCTM().inverse(), u = mi.a * e.clientX + mi.c * e.clientY + mi.e, v = mi.b * e.clientX + mi.d * e.clientY + mi.f;
  const inside = b => u >= b[0] && u <= b[2] && v >= b[1] && v <= b[3];
  const t = T.find(t => inside(S.L.rows[t.key].box));
  if (t) return t.key;
  const n = NODES.find(n => inside(S.L.nodes[n.i].box));
  return n ? n.key : null;
}
svg.addEventListener("pointermove", e => { if (e.pointerType === "mouse") svg.style.cursor = hit(e) ? "pointer" : "default"; });
svg.addEventListener("click", e => { const k = hit(e); if (k) { open(k); show(); } });
document.addEventListener("click", e => {
  const b = e.target.closest("[data-state]"), o = e.target.closest("[data-open]"), st = e.target.closest("[data-step]");
  if (b) choose(Number(b.dataset.state) === S.s && b.id === "split" ? 1 : Number(b.dataset.state));
  if (o) { open(o.dataset.open); if (o.dataset.open) show(); }
  if (st) {
    const L = ORDER(), k = L.indexOf(S.open), next = L[(k + Number(st.dataset.step) + L.length) % L.length];
    open(next);
    $("pane").querySelector(`[data-step="${st.dataset.step}"]`).focus({ preventScroll: true });
  }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) open("");
  if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
    choose(clamp(S.s + (e.key === "ArrowRight" ? 1 : -1), 0, 3));
  }
  if (e.key === "Enter" && document.activeElement === svg) {  // the first example
    e.preventDefault();
    open(C.examples[0][0]);
    show();
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); stateText(); place(performance.now()); });
still.addEventListener("change", () => { if (still.matches) { stopReplay(); S.entered = true; S.d1t = -1e9; aim(0, 0); S.dirty = true; place(performance.now()); } });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1; V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("switch").innerHTML = SNAME.slice(0, 3).map((n, k) => `<button data-state="${k}">${n}</button>`).join("");
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(\d+ of \d+)/, "<b>$1</b>");
build();
aim(0, 0);
fromHash(true);
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
/* The sentences are wrapped with the page's font: once it has loaded, lay them out again. */
if (document.fonts) document.fonts.ready.then(() => { build(); stateText(); S.dirty = true; place(performance.now()); });
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with a spine of six beads, one per sentence, and beside them the new claims: lit dots that held,
# rings that were refuted, a dashed ring left undecided. They drift a little.
ICON = r"""(kit, t, tilt) => {
  const top = 2.5, k = Number(t) || 0, marks = __MARKS__;
  let out = kit.slab(44, 38, 5);
  const a = kit.at(-30, -24, top), b = kit.at(-30, 24, top);
  out += `<path d="M${a[0].toFixed(1)} ${a[1].toFixed(1)}L${b[0].toFixed(1)} ${b[1].toFixed(1)}" stroke="${kit.token.ink}" stroke-width=".8" opacity=".45"/>`;
  for (let j = 0; j < 6; j++) {
    const d = kit.at(-30, -24 + 9.6 * j, top);
    out += `<circle cx="${d[0].toFixed(1)}" cy="${d[1].toFixed(1)}" r="2.2" fill="${kit.token.ink}" opacity=".7"/>`;
  }
  marks.forEach(([row, col, v], j) => {
    const d = kit.at(-8 + 12 * col + .6 * Math.sin(k * .7 + j), -24 + 9.6 * row, top), x = d[0].toFixed(1), y = d[1].toFixed(1);
    out += v === "h" ? `<circle cx="${x}" cy="${y}" r="3" fill="${kit.token.blue}"/>`
      : `<circle cx="${x}" cy="${y}" r="2.5" fill="none" stroke="${kit.token.ink}" stroke-width="1.1"${v === "u" ? ' stroke-dasharray="1.6 1.4"' : ""}/>`;
  });
  return out;
}"""
if RECORD:
    _rows = {}
    _marks = []
    for _n in TEST_ORDER:
        _t = TESTS[_n]
        if RECORD["tests"][_n]["kind"] != "consequence":
            continue
        _col = _rows.setdefault(_t[1], 0)
        _rows[_t[1]] += 1
        _marks.append([_t[1] - 1, _col, {"holds": "h", "refuted": "r", "undecided": "u"}[next(iter(RECORD["tests"][_n]["verdicts"].values()))]])
    ICON = ICON.replace("__MARKS__", json.dumps(_marks))

PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "examples": EXAMPLES, "counts": COUNTS, "record": RECORD,
    "order": TEST_ORDER, "tests": TESTS, "nodes": NODES, "clauses": CLAUSES, "extra3": EXTRA3,
}, ensure_ascii=False).replace("</", "<\\/"))

if __name__ == "__main__":  # run from the repository root
    args = sys.argv[1:]
    ref = args[args.index("--ref") + 1] if "--ref" in args else ""
    if "--write" in args:
        rec, commit = _build(ref)
        src = open(__file__).read()
        start = src.index("\nRECORD = ") + 1
        end = src.index("\nREF = ", start) + 1
        src = src[:start] + "RECORD = " + pprint.pformat(rec, width=118, sort_dicts=False) + "\n" + src[end:]
        for name, val in (("REF", ref), ("COMMIT", commit)):
            start = src.index(f"\n{name} = ") + 1
            src = src[:start] + f"{name} = {val!r}" + src[src.index("  #", start):]
        open(__file__, "w").write(src)
        print(f"wrote {len(rec['tests'])} tests and {len(rec['accounts'])} accounts from {ref or 'the working tree'}, commit {commit}")
        sys.exit(0)
    if not ref:
        if not os.path.exists(W + "synthesis_tests.json"):
            print(f"comparison skipped: the working tree has no {W} (RECORD was written from {REF or 'the working tree'} "
                  f"at {COMMIT}); run with --ref {REF or '<ref>'}")
            sys.exit(0)
    rec, commit = _build(ref)
    assert rec == RECORD, "RECORD differs from the files: run with --write" + (f" --ref {ref}" if ref else "")
    if ref == REF:
        assert COMMIT == commit, f"the files changed since commit {COMMIT} (now {commit}): run with --write"
    # the counts agree with the engine's own table in synthesis.md
    table = {m.group(1): [int(x) for x in m.groups()[1:]] for m in re.finditer(
        r"^\| account-(\d) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (-?\d+) \|$", _text(ref, W + "synthesis.md"), re.M)}
    assert sorted(table) == ["1", "2", "3"], "synthesis.md has no table of the three accounts"
    for k, x in COUNTS["accounts"].items():
        d1 = [x["d1"] == "holds", x["d1"] == "refuted"]
        mine = [x["explained"], x["unaddressed"], x["contradicts"], x["held"], x["refuted"], x["undecided"], *d1, x["score"]]
        assert mine == table[k], f"account {k}: page {mine}, synthesis.md {table[k]}"
    assert COUNTS["best"] == "2" and NODES and len(NODES) == len(RECORD["accounts"]["2"]["sentences"]), "the page draws account 2"
    print(f"RECORD matches the files ({ref or 'working tree'}, commit {commit}). {COUNTS['held']} of {COUNTS['tested']} "
          f"new consequences hold, {COUNTS['refuted']} refuted, {COUNTS['undecided']} undecided; synthesis.md agrees.")
