"""The team's one account of what RL changed, and how its new claims held: 6 of 9 in round 15, 0 of 9 in round 16.

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
A click on a sentence or a claim opens it in the side column.

A quiet round switch (Round 15, Round 16; the newest is the first view) redraws the plate for round 16 (engine 16:
accounts written in turn, each denying claims of the earlier ones, and a blind adversary's value for every consequence,
drawn as a short tick; a claim holds only if its interval lies in the range and excludes that value). Round 16's story
is account 1's (NODES16, CLAUSES16, TESTS16, RECORD16); on the switch the values travel in again and the large number
counts from one round's to the other's. Address: /finding/one-account-of-the-facts#<15, or nothing for 16>/<a1|a2|a3|
split, or nothing for the round's best account>/<panel, s1 to s6, or a claim: a1c1 ... a3c3, d1>. The rules are in
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

# Round 16 (engine 16): three accounts written in turn, each with 3 consequences and denials of the others; a blind
# adversary predicts each consequence's value without the account, and a consequence holds only if its 90 % interval
# lies in the account's range and excludes the adversary's value. Files: W16; account 1 ranks first (on the tie-break).
W16 = R + "wide/round-16/"
# Account 1's six sentences, one plain sentence each, in the format of NODES above, the stands keyed by account.
NODES16 = [
    ["RL on the model's own answers concentrates its small weight change in 8 directions per matrix, on inputs the base "
     "already uses, so imitation's change lands there too.", {"2": [1], "3": [1]}, {"2": "same", "3": "same"}],
    ["The base's later layers amplify those directions, and in every sample they make a deliberate opening likelier "
     "and wrong steps rarer;", {"2": [2, 6], "3": [2]}, {"2": "other", "3": "other"}],
    ["At 1.5 times the 8 directions match RL per sample, under a vote and where the base never solves, without RL's "
     "losses;", {"2": [5], "3": [3]}, {"2": "other", "3": "same"}],
    ["A three-token cue gives the base that opening at the level of RL step 100, which still opens deliberately in most "
     "samples but not all.", {"2": [4], "3": [4]}, {"2": "same", "3": "same"}],
    ["The rest comes only from voting over samples, which works because the base's wrong answers split rather than "
     "agree.", {"2": [3, 4], "3": [5]}, {"2": "same", "3": "same"}],
    ["Voting cannot reach problems the base never solves, so on the 328 harder problems Base + cue stays 8.8 points "
     "below RL; the 1.5x edit does not.", {"2": [5], "3": [6]}, {"2": "same", "3": "same"}],
]
# The clause each account ends sentences 2 and 3 with (index of the sentence from 0), and the two shown side by side in
# the disagreement view: the denials of round 16 (account 2 denies account 1's c1 and c2, account 3 denies account 2's
# c2 and c3) are about these two clauses.
CLAUSES16 = {
    1: {"1": "an answer that misses the opening is an unswitched base answer.",
        "2": "the shift is graded, so an answer that skips the opening still carries it.",
        "3": "the shift is graded, so an answer that skips the opening still carries it.",
        "split": [["1", "Account 1: an answer that misses the opening is an unswitched base answer."],
                  ["2", "Accounts 2 and 3: the shift is graded, so an answer that skips the opening still carries it."]]},
    2: {"1": "there too they make wrong steps rarer.",
        "2": "they re-rank which route an answer takes.",
        "3": "they only make each step more reliable, with no route preference.",
        "split": [["2", "Account 2: they re-rank which route an answer takes."],
                  ["3", "Account 3: they only make each step more reliable, with no route preference."]]},
}
# One entry per consequence of round 16 (a denial is a second range on its consequence's test), written for this page:
#   [short label, the sentence of account 1 it tests (1 to 6), test folder under results/direct/, key of the value in
#    its metrics.json, unit ("" or "points"), what n counts, axis domain [low, high] or None, caveat]
TESTS16 = {
    "round-16/account-1/c3": ["Code-RL's pattern follows Think-SFT's", 1, "r16a1c3-01", "D3", "", "matrices", None,
        "Undecided: the interval's low end, 0.126, is below the range's 0.15. The adversary's value, 0.481, lies above "
        "the interval."],
    "round-16/account-2/c1": ["Think-SFT shares inputs, not outputs", 1, "r16a2c1-01", "value", "", "matrices", None,
        "Refuted: the value, 2.40, lies far above the range (0.05 to 0.70) and above the null's (0.85 to 1.25)."],
    "round-16/account-3/c3": ["RL shares outputs, Think-SFT only inputs", 1, "r16a3c3-01", "statistic.value", "",
        "matrices", [0, 3], "Refuted: the value lies below the range (1.4 to 8.0) and below the null's (0.8 to 1.2)."],
    "round-16/account-1/c2": ["Code edit without the opening is worse", 2, "r16a1c2-01", "value", "", "problems", None,
        "Undecided: the interval's top, 0.665, passes the range's 0.65, and the interval also contains the adversary's "
        "value. Account 2's denial is refuted."],
    "round-16/account-3/c2": ["Code edit without opening beats the base", 2, "r16a3c2-01", "value", "", "problems", None,
        "Undecided: the interval's low end, −0.013, is below the range's 0.10; 76 problems."],
    "round-16/account-2/c2": ["Edit's wrong answers match RL's", 3, "r16a2c2-01", "statistic.value", "", "problems", None,
        "Not separated: the interval contains the adversary's value, 0.151, which comes from accuracy alone (Think-SFT + "
        "cue in place of the edit). Account 3's denial is refuted."],
    "round-16/account-2/c3": ["Edit's wrong answers match RL's, 2026 set", 3, "r16a2c3-01", "value", "", "problems",
        None, "Undecided for both accounts: the interval, −0.033 to 0.334, crosses both ranges; 69 problems published "
        "in 2026, after all weights existed."],
    "round-16/account-1/c1": ["Step 100 without the opening is worse", 4, "r16a1c1-01", "value", "", "problems", None,
        "Undecided: the interval's low end, 0.120, is below the range's 0.15. Account 2's denial (up to 0.12) is refuted "
        "by a margin of 0.0002. The flag for a deliberate opening misreads answers that echo prompt text before 'Okay'."],
    "round-16/account-3/c1": ["Step 100 without opening beats the base", 4, "r16a3c1-01", "value", "", "problems", None,
        "Undecided: the interval's top, 0.444, passes the range's 0.38. The opening flag counts 86 of the 151 samples "
        "it calls non-deliberate as opening with a hold-on word later in their first 240 characters."],
}
TEST_ORDER16 = list(TESTS16)

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
COMMIT = 'ccd8f4d'  # the last commit of those files at that ref when RECORD was written
# Written by --write: round 16's accounts, plans, measured values and the record's verdicts.
RECORD16 = {'facts': 53,
 'accounts': {'1': {'sentences': ["RL-Zero's weight change is small (0.24 % of the base's weight norm) and, as in "
                                  "every on-policy RL run whatever the reward (top-8 share of each matrix's change: "
                                  'LM-judge General 0.127, Math 0.118-0.135, against 0.030 for imitation-trained '
                                  'Think-SFT), concentrated in 8 input-output pairs per matrix whose inputs are '
                                  "directions the base's own activations already drive strongly in any step-by-step "
                                  'text (8-11x a random subspace; code text 0.87 as much as math), which is why '
                                  "Think-SFT's diffuse change also sits there (4.8x chance) and why Math's "
                                  "per-matrix concentration pattern follows Think-SFT's (rho 0.59) and not IF-RL's "
                                  '(-0.01).',
                                  "The base's later layers amplify those pairs (95x a random edit's residual shift, "
                                  'and only while each input stays paired with its own reward-specific output), and '
                                  'in every sample they do two graded things: they raise the probability that the '
                                  "answer opens and stays in the base's own deliberative mode ('Okay', 'Wait'; near "
                                  "1 for Math's pairs at 1x, 427 against plain 224 of 500, only partly for Code's "
                                  'pairs, whose unswitched answers look like plain-base answers), and they lower the '
                                  'per-step slip and cap-hit rates, which adds right answers even where the base '
                                  'finishes wrong (+13.5 points).',
                                  'At 1.5x, which stands in for the diffuse 88 % of the change left out (not for a '
                                  'bf16 loss: the written change is 0.99996 of the intended one), the 8 pairs '
                                  "reproduce RL per sample, under the vote and past the base's reach (456 against "
                                  '457 on MATH-500; 200.25 against 200.0, vote 216.25 against 215.92, and 0.88 of '
                                  "RL's lift on hard328 problems the base never solves), but they carry RL's gains, "
                                  'not its losses: where RL fails problems the base solves, the edit passes at the '
                                  "base's resample rate (code 0.45 against 0.44, RL 0.22).",
                                  'Inference gets the first part almost free because the mode is already in the '
                                  "base: a three-token cue, a self-chosen 'Okay' opening or a one-tensor hand edit "
                                  'gives 397-411 of 500, the level of RL step 100 (417.5, same cap-hit rate, same '
                                  '+7-point vote gain, right answers only 15 % longer), which holds the mode in most '
                                  'samples but not all, so the cue still adds +8.5 problems there.',
                                  'The second part inference recovers only by selection, which works because the '
                                  "base's slips are chance events whose wrong answers split (same-problem agreement "
                                  '0.26, so a right answer held by under half the samples still wins the plurality), '
                                  "so votes over 4-12 samples recover RL's reliability on problems the base solves "
                                  'at least once (81 % of the MATH-500 gap; a vote over 6 equals one RL sample), '
                                  "provided sampling keeps the base's long right routes (T 1.0, not T 0.6 where "
                                  '52-63 % of long answers loop, and no 4,096-token cap).',
                                  'Selection cannot reach problems the base never solves (it has no right sample on '
                                  "26 of the 36 hard328 problems RL's vote wins), so the cued base's vote stays 8.8 "
                                  'points under RL on the 328 while the 1.5x edit, which lowers the slip rate there '
                                  'too, does not.'],
                    'marks': {'explained': 28, 'not addressed': 25, 'contradicts': 0},
                    'facts': 53,
                    'own_contradicts': 0,
                    'contradicts': []},
              '2': {'sentences': ["RL-Zero's weight change (0.24 % of the weight norm) is concentrated in 8 "
                                  'input-output pairs per matrix, as in every on-policy RL run whatever the reward '
                                  '(top-8 share 0.12-0.21, LM-judge General 0.127, against 0.03 for '
                                  "imitation-trained Think-SFT); the input side of each pair is set by the base's "
                                  'own activations on any step-by-step text (driven 8-11x a random subspace, code '
                                  "text 0.87 as much as math), which is why Think-SFT's and Code-RL's changes also "
                                  "land there and Math's per-matrix pattern follows Think-SFT's (rho 0.59), not "
                                  "IF-RL's (-0.01); the output side, the pairing, is what the reward chose (shifted "
                                  "pairs or random outputs do nothing, and the base's later layers enlarge only the "
                                  'real pairs, 95x a random edit).',
                                  "The pairs act in every sample as a graded shift of the base's own choices, not as "
                                  'an on/off switch of a mode: direction 1 and layers 22-31 mostly set when the '
                                  'answer stops, while directions 2-8 in layers 0-21 re-rank which route the answer '
                                  'takes in its first half toward routes the base already writes at a low rate (on '
                                  'hard328 problems the cued base never solves in 4, a fresh base sample is right 5 '
                                  '%, RL 15 %, the 1.5x edit 14 %).',
                                  'The base fails in two ways: chance slips, after which it is as likely to finish '
                                  'right as from the start and whose wrong answers split (same-problem agreement '
                                  '0.26), and early route errors (a misreading has already cost 32 points before its '
                                  "sentence), and RL's advantage is in the text by the halfway point.",
                                  'Inference reaches what is one early choice or a chance event: a three-token cue, '
                                  "a self-chosen 'Okay' opening or a one-tensor hand edit fixes the opening (397-411 "
                                  'of 500, the level of RL step 100 with its cap-hit rate and +7-point vote gain), '
                                  'and a plurality vote over 4-12 samples at T 1.0 (not T 0.6, where 52-63 % of long '
                                  'answers loop, and not under a 4,096 cap) removes slips wherever the right route '
                                  "is already the base's plurality (81 % of the MATH-500 gap lies where the base "
                                  'solves at least 1 of 4; a vote over 6 equals one RL sample).',
                                  'No prompt, sampling rule or vote re-ranks routes after the opening, so where the '
                                  'right route is rare and the wrong answers split the base stays short (no right '
                                  "sample on 26 of the 36 hard328 problems RL's vote wins; vote 8.8 points under "
                                  'RL), while the 1.5x edit, whose extra half stands in for the diffuse 88 % left '
                                  'out (not a bf16 loss: 0.99996 of the intended change is written), carries the '
                                  "re-ranking and matches RL per sample, under the vote and past the base's reach "
                                  "(456 vs 457; 200.25 vs 200.0; vote 216.25 vs 215.92; 0.88 of RL's lift).",
                                  'Because the shift is graded and present in every sample, an edited or partly '
                                  "trained model's answer that skips the deliberative opening still carries it "
                                  "(short 1x-edit answers are 82.9 % right, m21's quick wrong answers are not "
                                  'answer-first replies), so the cue adds little once the weights have moved (+8.5 '
                                  "of 500 at step 100), and an edit made of RL's top pairs alone carries RL's gains "
                                  'but not the losses that sit in the rest of the change (where RL-Code fails '
                                  "base-passed problems the Code edit passes at the base's resample rate, 0.45 vs "
                                  '0.44).'],
                    'marks': {'explained': 31, 'not addressed': 21, 'contradicts': 1},
                    'facts': 53,
                    'own_contradicts': 1,
                    'contradicts': [['F29',
                                     'S2 gives route re-ranking to directions 2-8 and stopping to direction 1, but '
                                     'the rank-1 edit alone raises rightness on finished-wrong problems by +7.2 '
                                     "[0.7, 13.6], close to d2-8's +9.3"]]},
              '3': {'sentences': ["RL-Zero's weight change is small (0.24 % of the weight norm), and under any "
                                  'on-policy reward about 12 % of it sits in 8 input-output pairs per matrix (top-8 '
                                  'share: LM-judge General 0.127, Math 0.118-0.135, imitation-trained Think-SFT '
                                  '0.030); the inputs are directions the base already drives in any step-by-step '
                                  "text (8-11x a random subspace; code text 0.87 as much as math), so Think-SFT's "
                                  "and Code-RL's changes also overlap them (4.8x chance; Code 5.2x Think-SFT) and "
                                  "Math's per-matrix pattern follows Think-SFT's (rho 0.59), not IF-RL's (-0.01); "
                                  "the output paired with each input is what the reward chose (on code, Code's pairs "
                                  "raise the pass rate 7.0 points over a random edit, Math's 1.5).",
                                  "The base's later layers enlarge these pairs only when they stay paired (95x a "
                                  "random edit's residual shift), and they act in every sample as a graded "
                                  'reweighting of each token the base already writes, not as a switch between modes: '
                                  'hold-on words go up (+1.1 to +1.7 points of readout positions), wrap-up words go '
                                  "down (-1.4), and the base's own wrong step becomes half as likely; so short "
                                  "answers of the 1x edit are 82.9 % right, m21's quick wrong answers are no more "
                                  "answer-first than the plain base's (0.25 vs 0.21), and the edit is written in "
                                  'full (0.99996 of the intended change).',
                                  'The effect on outcomes is one multiplier on the reliability of each step, not a '
                                  "preference for RL's own routes: the edit adds right answers where the base "
                                  'finishes wrong (+13.5 points over a second base sample) and where the base never '
                                  'solves the problem in 4 samples (14 % vs 5 %, RL 15 %); at 1.5x, which stands in '
                                  'for the diffuse 88 % of the change it leaves out, it equals RL per sample, under '
                                  "the vote and beyond the base's reach (456 vs 457; 200.25 vs 200.0; vote 216.25 vs "
                                  "215.92; 0.88 of RL's lift), and it does not carry RL's losses (on code problems "
                                  'RL fails: edit 0.45, base resample 0.44, RL 0.22).',
                                  'Inference reproduces the part of this reweighting that sits at a single token, '
                                  'the first word of the answer: a plain base answer that already opens '
                                  'deliberatively is as right as a cued one (-0.03), and a three-token cue, a '
                                  "self-chosen 'Okay' or a one-tensor hand edit gives 397-411 of 500, the level of "
                                  "RL step 100 (417.5); step 100 has the cued base's cap-hit rate and +7-point vote "
                                  'gain, writes right answers only 15 % longer (final RL 61 %), and still gains +8.5 '
                                  'of 500 from the cue, because 100 steps install only part of the per-token shift.',
                                  'Inference gets the per-step reliability only by selecting among whole answers, '
                                  "which works because the base's slips are chance events whose wrong answers split "
                                  '(pairwise agreement 0.26; splitting adds 0.07 to the vote over 4 on MATH-500 and '
                                  '0.11 on hard328; the problems the vote over 12 gains are split problems, not '
                                  'ties); a T 1.0 plurality over 4-12 samples therefore recovers RL wherever the '
                                  "right answer is already the base's plurality (81 % of the MATH-500 gap lies on "
                                  'problems the base solves at least 1 time in 4; a vote over 6 equals one RL '
                                  'sample), but only if sampling keeps the long right routes, so not at T 0.6, where '
                                  '52-63 % of answers past 4,096 tokens loop, and not under a 4,096-token cap (71 % '
                                  "of Karpathy's lost hard328 problems).",
                                  "Where the right answer is rarer than the base's wrong ones, selection has nothing "
                                  "to amplify (the base has no right sample on 26 of the 36 hard328 problems RL's "
                                  "vote wins), so the cued base's vote stays 8.8 points under RL on the 328, while "
                                  'the 1.5x edit, which makes every step more reliable, does not stay under it.'],
                    'marks': {'explained': 32, 'not addressed': 21, 'contradicts': 0},
                    'facts': 53,
                    'own_contradicts': 0,
                    'contradicts': []}},
 'tests': {'round-16/account-1/c3': {'owner': '1',
                                     'claim': 'S1: where the RL change concentrates is set by which matrices '
                                              'step-by-step text drives, not by the reward. Code-RL writes '
                                              'step-by-step text (its late directions also read Okay/Wait), so its '
                                              'per-matrix top-8 share pattern, with family medians removed, follows '
                                              "Think-SFT's, as Math 3.1's does (0.59), and not IF-RL's. A shared RL "
                                              'recipe would instead tie Code to IF.',
                                     'statistic': 'D3 = Spearman rho(Code-RL 3.1, Think-SFT) - rho(Code-RL 3.1, '
                                                  "IF-RL) of per-matrix top-8 share after the module family's median "
                                                  'is removed (unitless)',
                                     'null': "Another model's directions: IF-RL's pattern stands for 'RL runs share "
                                             "one concentration pattern whatever text they write', which gives D3 "
                                             "about 0 (F24's null range).",
                                     'why_new': "F24 correlated only Math 3.1's pattern with IF and Think-SFT; F03 "
                                                'and result-82eb02 compared median levels, not per-matrix patterns. '
                                                "No result correlates Code-RL's pattern with anything.",
                                     'ranges': {'1': [0.15, 1.0], 'null': [-0.1, 0.1]},
                                     'alternative': 'Code-RL 3.1 is a sibling of Math-RL 3.1: same base, same '
                                                    'RL-Zero 3.1 recipe (optimizer, learning rate, steps, rollout '
                                                    'setup). Matrices that soak up a concentrated low-rank change '
                                                    'under that recipe do so for both rewards, so the two share a '
                                                    'per-matrix top-8-share fingerprint. Code-RL 3.1 already tracks '
                                                    'Math 3.1 closely elsewhere: token-level log-prob agreement '
                                                    '0.405 (result-eb9211), and F27 notes the input-subspace overlap '
                                                    'with Think-SFT is shared by Code 3.1. result-caa23d already '
                                                    "measured Math 3.1's fingerprint on these exact 224 "
                                                    'family-median-removed matrices: it follows Think-SFT (rho '
                                                    '0.594) and not IF-RL (rho -0.010), so rho(T) - rho(I) = +0.604. '
                                                    "If Code 3.1's pattern is Math 3.1's pattern plus noise that is "
                                                    'unrelated to Think-SFT and IF, then D3 = rho(Code, Math 3.1) x '
                                                    '0.604. With the Code-Math rank correlation of about 0.5-0.7 '
                                                    'that sibling runs should have, that gives about 0.30-0.42, '
                                                    'inside [0.15, 1.0]. None of this needs a Code-specific '
                                                    'mechanism; it needs only the shared recipe and the Math 3.1 '
                                                    'result.',
                                     'denials': [],
                                     'plan_n': 224,
                                     'value': 0.2649,
                                     'lo': 0.1259,
                                     'hi': 0.4022,
                                     'n': 224,
                                     'adversary': 0.4807,
                                     'verdicts': {'1': 'undecided'},
                                     'measured': {'1': 'D3 0.265 [0.126, 0.402], n 224 matrices, adversary value '
                                                       '0.481'},
                                     'record_claim': {'1': 'Where the RL change concentrates is set by which '
                                                           "matrices step-by-step text drives, so Code-RL 3.1's "
                                                           'family-median-removed per-matrix top-8 share pattern '
                                                           "follows Think-SFT's (as Math 3.1's does) and not "
                                                           "IF-RL's."},
                                     'result': 'result-f861f7',
                                     'added': '2026-11-16T00:10:42'},
           'round-16/account-2/c1': {'owner': '2',
                                     'claim': "Sentence 1 says the input side of RL's pairs is fixed by the base's "
                                              'activations, so any training on step-by-step text lands there, while '
                                              'the output side is chosen by the reward. Think-SFT (imitation) should '
                                              "therefore sit in Math 3.1's top-8 subspace much less on the output "
                                              'side than on the input side, relative to Math 3.0, which has the same '
                                              'reward and shares both sides. Diffuseness alone gives a ratio of 1, '
                                              'because the chance levels cancel.',
                                     'statistic': 'Q = median over matrices of [cap_left(Think-SFT, Math 3.1 top-8) '
                                                  '/ cap_right(Think-SFT, Math 3.1 top-8)] / [cap_left(Math 3.0, '
                                                  'Math 3.1 top-8) / cap_right(Math 3.0, Math 3.1 top-8)], unitless',
                                     'null': "Another model's directions: whatever lands in Math 3.1's top-8 "
                                             'subspace lands there alike on both sides, whatever the objective. '
                                             "Think-SFT's output/input ratio then equals Math 3.0's (Q about 1), "
                                             'which is also the value pure diffuseness gives.',
                                     'why_new': 'F27 and F46 (results 3abd6f and 105d5c) used cap_right (input side) '
                                                'only. No fact or result reports the output-side capture (cap_left) '
                                                'of Think-SFT or Math 3.0, or the two sides set against each other.',
                                     'ranges': {'2': [0.05, 0.7], 'null': [0.85, 1.25]},
                                     'alternative': 'This alternative uses a known difference between the two models '
                                                    'and the generic shape of gradient updates. Every fine-tune of '
                                                    'this base gets updates of the form sum(delta x^T). Its right '
                                                    '(input) singular vectors therefore lean toward the input '
                                                    "directions that the base's own activations drive hard. RL-Math "
                                                    "3.1's top-8 input directions are such directions: the base's "
                                                    'text drives them 8-11x more than random (result-a7c052), and '
                                                    "they sit 1.33x inside the base matrix's own top input subspace "
                                                    "(result-3abd6f). So any change, Think-SFT's included, gets an "
                                                    'input-side capture above chance for free. That is the '
                                                    '4.80x-chance cap_right of Think-SFT (F27), which is also '
                                                    '2.0-2.2x the IF and General subspaces. The output (left) side '
                                                    'carries the loss-specific write. Math 3.0 has the same math '
                                                    'reward as Math 3.1 and a concentrated update (top-8 share '
                                                    "0.135), so it shares Math 3.1's input-output pairs and captures "
                                                    "on both sides. Think-SFT's update is diffuse (top-8 share "
                                                    '0.030, result-82eb02) and imitation-driven, so it writes along '
                                                    "RL-Math's output directions only at about chance. If "
                                                    'cap_left_TS is about 8/d_out and cap_right_TS is about 4.8 x '
                                                    '8/d_in, then r_TS is about d_in/(4.8 d_out). Math 3.0 has r_M30 '
                                                    '= (a_L/a_R)(d_in/d_out) with comparable excess multiples a_L '
                                                    'and a_R. So q is about (1/4.8)(a_R/a_L), roughly 0.2-0.3, well '
                                                    "inside [0.05, 0.7]. The prediction needs nothing beyond 'input "
                                                    "capture is generic and output capture is reward-specific', plus "
                                                    "Think-SFT's known diffuseness.",
                                     'denials': [],
                                     'plan_n': 224,
                                     'value': 2.4001,
                                     'lo': 2.164,
                                     'hi': 2.6121,
                                     'n': 224,
                                     'adversary': 1.6261,
                                     'verdicts': {'2': 'refuted'},
                                     'measured': {'2': '2.4001 [2.164, 2.6121], n 224, adversary value 1.6261'},
                                     'record_claim': {'2': 'The input side of RL top-8 pairs is fixed by base '
                                                           'activations and the output side by the reward, so '
                                                           'Think-SFT sits in Math 3.1 top-8 subspace much less on '
                                                           'the output side than the input side, relative to Math '
                                                           '3.0 (Q in [0.05, 0.7]).'},
                                     'result': 'result-54d454',
                                     'added': '2026-11-16T00:10:36'},
           'round-16/account-3/c3': {'owner': '3',
                                     'claim': 'S1 and S2: on-policy RL shares the output side of the deliberation '
                                              'pairs whatever the reward (the late directions that read Okay/Wait '
                                              'are in both RL-Math and RL-Code), while imitation-trained Think-SFT '
                                              'overlaps only the driven inputs. So relative to its own input-side '
                                              "capture, Code-RL 3.1's change sits on Math 3.1's top-8 output side "
                                              "far more than Think-SFT's does. The ratio of ratios removes overall "
                                              'concentration and the rank-8 chance levels.',
                                     'statistic': 'Q_C = median over matrices of [cap_left(Code 3.1)/cap_right(Code '
                                                  '3.1)] / [cap_left(Think-SFT)/cap_right(Think-SFT)], all against '
                                                  "Math 3.1's top-8 subspaces, unitless",
                                     'null': "Another model's directions: whatever lands in Math 3.1's top-8 "
                                             'subspace lands there equally on both sides, whatever the objective, so '
                                             "Code's output/input ratio equals Think-SFT's (Q_C about 1).",
                                     'why_new': 'F27 and F46 use cap_right (the input side) only. Account-2/c1 sets '
                                                'Think-SFT against Math 3.0, which has the same reward. No fact or '
                                                'result compares output-side to input-side capture for Code-RL '
                                                'against Think-SFT.',
                                     'ranges': {'3': [1.4, 8.0], 'null': [0.8, 1.2]},
                                     'alternative': 'A known difference between the two models compared: Code 3.1 is '
                                                    'a concentrated RL-Zero change (top-8 share 0.174) whose leading '
                                                    'singular pairs act on both the output and input sides of the '
                                                    "matrix. Think-SFT's change is diffuse (top-8 share 0.030, "
                                                    'result-82eb02). Its only above-chance alignment with another '
                                                    "model's subspace is on the input side, and that side follows "
                                                    "the base's high-variance input directions that any fine-tune "
                                                    "shares (F27: 1.33x even the base matrix's own subspace, about "
                                                    "2x IF and General). So Think-SFT's output-side capture sits "
                                                    'near chance while its input-side capture is raised, which makes '
                                                    "cap_left_TS/cap_right_TS small. Code's capture is raised on "
                                                    'both sides, so its own left/right ratio is near 1 or above. The '
                                                    'ratio of ratios is therefore well above 1 for any RL-Zero '
                                                    'reference subspace, math or not. The account (whatever ties '
                                                    'Code to Math 3.1 specifically) is not needed. The alternative '
                                                    "predicts the same Q computed against a non-math RL reward's "
                                                    'top-8 subspace (General-RL, an LM-judge reward) comes out about '
                                                    'the same, inside [1.4, 8.0].',
                                     'denials': [],
                                     'plan_n': 224,
                                     'value': 0.4919,
                                     'lo': 0.4418,
                                     'hi': 0.5532,
                                     'n': 224,
                                     'adversary': 0.5885,
                                     'verdicts': {'3': 'refuted'},
                                     'measured': {'3': '0.492 [0.442, 0.553], n 224, adversary value 0.589'},
                                     'record_claim': {'3': 'On-policy RL shares the output side of the deliberation '
                                                           'pairs whatever the reward while Think-SFT overlaps only '
                                                           'the driven inputs, so relative to its input-side capture '
                                                           'Code-RL 3.1 sits on Math 3.1 top-8 output side far more '
                                                           'than Think-SFT (Q_C in [1.4, 8.0]).'},
                                     'result': 'result-9f2b30',
                                     'added': '2026-11-16T00:10:55'},
           'round-16/account-1/c2': {'owner': '1',
                                     'claim': "Code-RL's 8 pairs at 1x on the base (m21, plain, MATH-500 first 250) "
                                              'switch the mode only partly, and the unswitched answers are '
                                              'plain-base answers (S2). On problems the cued base solves, m21 '
                                              'answers that open deliberatively should be right at about the cued '
                                              "base's rate (~0.85) and non-deliberative ones at about the plain "
                                              "base's rate (~0.35-0.5): a gap of 0.2-0.65. Openings that only marked "
                                              'easier problems would give a gap near 0 on this difficulty-restricted '
                                              'set.',
                                     'statistic': 'G = right rate (v3) of deliberative-opening m21 answers minus '
                                                  'right rate of non-deliberative m21 answers, on problems the cued '
                                                  'base T1 sample solves, as a fraction (0-1)',
                                     'null': 'Difficulty only: the opening marks easier problems, measured by the '
                                             "cued base's own 4-sample right rate on the same rows.",
                                     'why_new': 'F11, F12, F22 and F44 measured the opening share among quick wrong '
                                                "answers, their problems' difficulty, and right-answer length. No "
                                                "fact or result relates m21's correctness to its opening on fixed "
                                                'problems.',
                                     'ranges': {'1': [0.2, 0.65], '2': [-0.1, 0.17], 'null': [-0.06, 0.12]},
                                     'alternative': 'The opening type alone sorts answers into two modes of the '
                                                    'untrained base that already differ in accuracy, with no Code-RL '
                                                    'edit involved. A non-deliberative (answer-first) opening is the '
                                                    "plain-prompt base's way of replying, which is right about 30-40 "
                                                    "% of the time. A deliberative opening is the cued base's way of "
                                                    'replying, which is right about as often as T1 (F51 / '
                                                    'result-1f98b0: flagged plain-base answers are within -0.03 of '
                                                    'T1, unflagged ones are 0.52 below). So any model that mixes the '
                                                    'two modes shows a gap of about 0.4-0.55 between deliberative '
                                                    "and non-deliberative answers on T1-solved problems, and m21's G "
                                                    "should match the gap the same flag rule gives on the base's own "
                                                    'plain answers (T3) on the same rows. The account is not needed '
                                                    'for that.',
                                     'denials': [{'by': '2',
                                                  'why': "The premise that m21's non-deliberative answers are "
                                                         "plain-base answers (about 0.35-0.5 right) is wrong. Code's "
                                                         'pairs at 1x shift every sample by a graded amount: short '
                                                         "1x-edit answers are 82.9 % right, m21's quick wrong "
                                                         'answers are not answer-first replies, and S = 0.414 sits '
                                                         'above the lottery range. So on problems the cued base '
                                                         "solves, m21's non-deliberative answers are right nearly as "
                                                         'often as its deliberative ones.',
                                                  'instead': "Sentence 6: the gap between m21's deliberative and "
                                                             'non-deliberative answers on cued-solved problems is '
                                                             'small, G in [-0.10, 0.17].',
                                                  'range': [-0.1, 0.17]}],
                                     'plan_n': 205,
                                     'value': 0.5744,
                                     'lo': 0.4778,
                                     'hi': 0.6653,
                                     'n': 201,
                                     'adversary': 0.4977,
                                     'verdicts': {'1': 'undecided', '2': 'refuted'},
                                     'measured': {'1': '0.574 [0.478, 0.665], n 201, adversary value 0.498',
                                                  '2': '0.574 [0.478, 0.665], n 201, adversary value 0.498'},
                                     'record_claim': {'1': 'On cued-solved problems, m21 answers that open '
                                                           "deliberatively are right at about the cued base's rate "
                                                           "and the others at about the plain base's rate, a gap G "
                                                           'in [0.20, 0.65].',
                                                      '2': "Code's pairs at 1x shift every sample by a graded "
                                                           "amount, so on cued-solved problems m21's deliberative "
                                                           'and non-deliberative answers differ little, G in [-0.10, '
                                                           '0.17].'},
                                     'result': 'result-0f40ff',
                                     'added': '2026-11-16T00:11:25'},
           'round-16/account-3/c2': {'owner': '3',
                                     'claim': "S2: Code-RL's pairs at 1x reweight every token, including the hold-on "
                                              "words their late directions share with Math's. So an m21 answer that "
                                              'does not open deliberatively is still right more often than the plain '
                                              "base's non-deliberative answer to the same problem. The gain is part "
                                              "of the cue's ~0.5, not 0 (an unswitched plain-base answer) and not "
                                              "m21's whole gap over the plain base.",
                                     'statistic': 'D_m21 = mean over problems of (m21 right minus T3 right) where '
                                                  'both answers are non-deliberative, as a fraction (0-1)',
                                     'null': "The switch null: Code's pairs switch some samples fully and leave the "
                                             'rest as plain-base answers, so on problems where both are '
                                             'non-deliberative, m21 is right as often as T3 (D about 0).',
                                     'why_new': "F11/F12 looked only at m21's quick wrong answers, and F22/F44 at "
                                                "the length of right answers. Account-1/c2 compares m21's own "
                                                "openings with each other against the cued base's difficulty. No "
                                                "fact or result pairs m21's non-deliberative answers with the plain "
                                                "base's non-deliberative answers on the same problems.",
                                     'ranges': {'3': [0.1, 0.4], 'null': [-0.07, 0.07]},
                                     'alternative': 'A known difference between the models compared: m21 (base + '
                                                    'Code-RL top-8 at 1x, plain) is simply a more accurate model '
                                                    'than the plain base T3 on these problems (157/250 vs 107/250 '
                                                    "right, result-ac7104). T3's non-deliberative answers are its "
                                                    'low-accuracy mode (about 0.31 right on unflagged problems where '
                                                    'the cued base is about 0.83 right, result-1f98b0 null), so the '
                                                    "problems are not hard; T3 just answers badly there. m21's "
                                                    'per-problem advantage over T3 on those problems is a general '
                                                    "accuracy gap and does not depend on how m21's own answer opens. "
                                                    "If D is restricted by T3's flag only, ignoring m21's flag, it "
                                                    'already lands near 0.25, inside [0.1, 0.4]. Requiring m21 to be '
                                                    'non-deliberative as well, which is the part the account needs, '
                                                    'adds nothing.',
                                     'denials': [],
                                     'plan_n': 65,
                                     'value': 0.1053,
                                     'lo': -0.0132,
                                     'hi': 0.2237,
                                     'n': 76,
                                     'adversary': 0.352,
                                     'verdicts': {'3': 'undecided'},
                                     'measured': {'3': '0.105 [-0.013, 0.224], n 76, adversary value 0.352'},
                                     'record_claim': {'3': 'An m21 answer (base + Code-RL top-8 at 1x, plain) that '
                                                           'does not open deliberatively is still right more often '
                                                           "than the plain base's non-deliberative answer to the "
                                                           'same problem, by 0.1-0.4.'},
                                     'result': 'result-9cf361',
                                     'added': '2026-11-16T00:11:37'},
           'round-16/account-2/c2': {'owner': '2',
                                     'claim': "Sentences 2 and 5 say the 1.5x edit carries RL's re-ranking of "
                                              "routes, not just fewer slips. So where both fail, the edit's wrong "
                                              "answers should be closer to RL's than the base's are. The agreement "
                                              "is normalized by each model's own wrong-answer concentration, so a "
                                              'model that is merely sharper does not score higher. If the edit only '
                                              'lowered slips (account-1), its wrong answers would be drawn like the '
                                              "base's and the difference would be about 0.",
                                     'statistic': 'D = N(E,R) - N(B,R), with N(X,R) = A(X,R) / sqrt(A(X,X) * '
                                                  'A(R,R)). A(X,Y) is the pooled share of same-problem pairs of '
                                                  'finished wrong answers that agree (cross pairs between two '
                                                  'models, within pairs for one model); E = base + 1.5x top-8, R = '
                                                  'RL plain, B = cued base. Unitless.',
                                     'null': "The base's own resample: the edit's wrong answers are drawn like the "
                                             "base's (the edit only lowers the slip rate), computed as the base's "
                                             'samples 2-3 against its samples 0-1, each against RL. This gives D '
                                             'about 0.',
                                     'why_new': "F45, F48 and result-064aac measured agreement among the cued base's "
                                                'own wrong answers only, and F50, F52 and F53 compared right rates. '
                                                'No fact or result compares wrong answers across the edit, RL and '
                                                'the base.',
                                     'ranges': {'2': [0.08, 0.6], '3': [-0.1, 0.07], 'null': [-0.07, 0.06]},
                                     'alternative': "Accuracy, not RL's directions. On hard328 the 1.5x edit and RL "
                                                    'plain are about equally accurate (per sample 200.25 vs 200.0 of '
                                                    '328; 14.3 % vs 15.5 % on base-0/4 problems), and both are well '
                                                    'above the cued base (about 164). A more accurate model gets rid '
                                                    "of the base's careless, one-off wrong values: long arithmetic "
                                                    'slips and wrong values that finish after loops. Its remaining '
                                                    'finished wrong answers are the systematic near-misses that any '
                                                    'strong solver reaches (a missed case, a misread condition), and '
                                                    "these are the values RL's wrong answers also land on. On the "
                                                    'same problems, the per-problem weighting of cross pairs (w_X * '
                                                    "w_R) also lines up with the within-pair weighting when X's "
                                                    "wrong counts track RL's, and the normalization rewards that "
                                                    'alignment. So any model with RL-level accuracy and no RL '
                                                    'weights should give a positive N(X,R) - N(B,R) of the same '
                                                    'size. The test: Think-SFT + cue is accuracy-matched (209.0 of '
                                                    "328 per sample against the edit's 200.25 and RL's 200.0), "
                                                    'carries no RL weight change and no RL edit, and has 4 attempt-0 '
                                                    'samples stored on hard328. Its normalized wrong-answer '
                                                    "agreement with RL, minus the cued base's, should land at about "
                                                    '+0.1 to +0.2, inside [0.08, 0.6].',
                                     'denials': [{'by': '3',
                                                  'why': "Account-2 says the 1.5x edit carries RL's re-ranking of "
                                                         "routes, so the edit's wrong answers should be nearer RL's "
                                                         "than the base's are. Under S3 the edit and RL lower only "
                                                         'the rate of chance slips. Their remaining finished wrong '
                                                         "answers are the base's own systematic misreadings, plus "
                                                         "slips that split. With each model's agreement normalized "
                                                         'by its own concentration, the slip fraction cancels and '
                                                         'N(E,R) equals N(B,R).',
                                                  'instead': 'S3 (one reliability multiplier, no route preference): '
                                                             'D = N(E,R) - N(B,R) on hard328 lies near 0, in [-0.10, '
                                                             '0.07].',
                                                  'range': [-0.1, 0.07]}],
                                     'plan_n': 90,
                                     'value': 0.286,
                                     'lo': 0.1328,
                                     'hi': 0.4439,
                                     'n': 118,
                                     'adversary': 0.1509,
                                     'verdicts': {'2': 'not separated', '3': 'refuted'},
                                     'measured': {'2': '0.286 [0.133, 0.444], n 118, adversary 0.151',
                                                  '3': '0.286 [0.133, 0.444], n 118, adversary 0.151'},
                                     'record_claim': {'2': "The 1.5x edit carries RL's re-ranking of routes, so "
                                                           'where both fail its normalized wrong-answer agreement '
                                                           "with RL exceeds the cued base's by 0.08-0.6.",
                                                      '3': 'Under S3 the edit and RL only lower the chance-slip '
                                                           'rate, so N(E,R) equals N(B,R) and D lies in [-0.10, '
                                                           '0.07].'},
                                     'result': 'result-088836',
                                     'added': '2026-11-16T00:12:18'},
           'round-16/account-2/c3': {'owner': '2',
                                     'claim': 'The same consequence of sentences 2 and 5 on 136 contest problems '
                                              "published in 2026, after all weights existed. The edit shares RL's "
                                              'route re-ranking, so where all three fail its wrong answers are '
                                              "closer to RL's than the cued base's are, after normalizing for each "
                                              "model's own wrong-answer concentration.",
                                     'statistic': 'D_fresh = N(E,R) - N(B,R) on fresh2026, defined as in c2. '
                                                  'Unitless.',
                                     'null': "The base's own resample: the edit's wrong answers are drawn like the "
                                             "cued base's, so D is about 0 (base samples 2-3 against base samples "
                                             '0-1, each against RL).',
                                     'why_new': 'result-04e329 and the fresh readouts report right counts only. No '
                                                'fact or result compares wrong answers across models on fresh2026.',
                                     'ranges': {'2': [0.08, 0.6], '3': [-0.1, 0.07], 'null': [-0.07, 0.06]},
                                     'alternative': 'Strength covariate: any model more accurate than the cued base '
                                                    "on fresh2026 has wrong answers that agree more with RL's, "
                                                    'whatever its weights share with RL. Stronger models make fewer '
                                                    'one-off wrong answers (garbled or mis-extracted values, '
                                                    'near-cap guesses, scattered slips). More of their remaining '
                                                    'wrong answers land on the few common attractor values per '
                                                    'problem (a standard misreading, an off-by-one count, a partial '
                                                    "result), and RL's wrong answers land on those values too. The "
                                                    'cued base is weak on fresh2026 (29.5 of 136 per sample, against '
                                                    '48.25 for the edit and 50.5 for RL), so its wrong answers are '
                                                    "the most scattered and N(B,R) is the lowest. Any arm near RL's "
                                                    'accuracy then gives N(X,R) - N(B,R) clearly above 0, which '
                                                    'matches the predicted D_fresh of 0.08-0.6 without the edit '
                                                    "copying RL's mechanism. Think-SFT + cue tests this. It was "
                                                    'trained by imitation only and holds no RL-Math directions, it '
                                                    'is at least as strong on fresh2026 (60.0 per sample), and its '
                                                    '4-sample fresh2026 rows are stored. If D computed with '
                                                    'Think-SFT in place of the edit lands in [0.08, 0.6], accuracy '
                                                    'alone predicts the range.',
                                     'denials': [{'by': '3',
                                                  'why': 'The same claim on fresh2026: the edit has no route '
                                                         'preference of its own beyond fewer slips, so its wrong '
                                                         "answers are no nearer RL's than the cued base's are once "
                                                         "each model's own wrong-answer concentration is normalized "
                                                         'out.',
                                                  'instead': 'S3: D_fresh = N(E,R) - N(B,R) lies near 0, in [-0.10, '
                                                             '0.07].',
                                                  'range': [-0.1, 0.07]}],
                                     'plan_n': 85,
                                     'value': 0.1793,
                                     'lo': -0.033,
                                     'hi': 0.3339,
                                     'n': 69,
                                     'adversary': 0.0168,
                                     'verdicts': {'2': 'undecided', '3': 'undecided'},
                                     'measured': {'2': '0.179 [-0.033, 0.334], n 69, adversary value 0.0168',
                                                  '3': '0.179 [-0.033, 0.334], n 69, adversary value 0.0168'},
                                     'record_claim': {'2': "The 1.5x top-8 edit shares RL's route re-ranking, so on "
                                                           'fresh2026 problems where edit, RL and cued base all '
                                                           "fail, the edit's wrong answers are closer to RL's than "
                                                           "the base's are after normalizing each model's own "
                                                           'concentration (D_fresh in [0.08, 0.6]).',
                                                      '3': 'The edit has no route preference beyond fewer slips, so '
                                                           'its normalized wrong-answer agreement with RL on '
                                                           "fresh2026 is no higher than the cued base's (D_fresh in "
                                                           '[-0.10, 0.07]).'},
                                     'result': 'result-13c355',
                                     'added': '2026-11-16T00:12:24'},
           'round-16/account-1/c1': {'owner': '1',
                                     'claim': 'At RL step 100 (plain prompt, MATH-500, 4 samples) the samples that '
                                              'do not open deliberatively are unswitched plain-base answers (S4: '
                                              'step 100 holds the mode in most samples, not all; S2: an unswitched '
                                              'sample is a plain-base answer, about 0.5 below the cue on the same '
                                              "problem, F51's null -0.516). So on the same problem, the step-100 "
                                              'model with the cue is right far more often than its own '
                                              'non-deliberative plain samples, while its deliberative plain samples '
                                              'are right about as often as the cue. Pairing within each problem '
                                              'removes difficulty.',
                                     'statistic': 'D1 = mean over problems of (right rate of the 4 step-100 cue '
                                                  'samples minus right rate of the step-100 plain samples that do '
                                                  'not open deliberatively), as a fraction of samples (0-1)',
                                     'null': "The step-100 model's own deliberative plain samples on the same "
                                             'problems. This is the null that the opening is cosmetic because RL has '
                                             'already internalised the mode, so the cue minus any plain sample is '
                                             'about 0.',
                                     'why_new': 'F07 measured only the pooled cue-minus-plain difference at step 100 '
                                                '(+8.5/500), and F25/F41/F49 measured length, cap hits and the vote. '
                                                'F51 used the untrained base, one sample per problem. No fact or '
                                                'result splits step-100 samples by how they open.',
                                     'ranges': {'1': [0.15, 0.75], '2': [-0.1, 0.12], 'null': [-0.08, 0.08]},
                                     'alternative': 'The opening format is the covariate. A plain sample that does '
                                                    'not open deliberatively is an answer-first reply: short, with '
                                                    'no derivation. Replies like that are wrong at a high rate that '
                                                    'depends on the format, whatever the checkpoint. The untrained '
                                                    'base shows the size of this effect. On MATH-500 problems where '
                                                    'its plain T3 answer did not open deliberatively, the cued '
                                                    'answer (T1) beat it by 0.516 per problem (null of result-1f98b0 '
                                                    '/ F51: T3 - T1 = -0.516 [-0.564, -0.467]). Step 100 adds about '
                                                    "+0.03 to the cue's right rate (426.0 vs 410.5 of 500, "
                                                    'result-6832a8). So cue-minus-answer-first-plain at step 100 '
                                                    "should be about the base's format gap. That puts it near "
                                                    '0.45-0.55, inside [0.15, 0.75], and no account of what RL '
                                                    'changed is needed: only the fact that answer-first text skips '
                                                    'the derivation.',
                                     'denials': [{'by': '2',
                                                  'why': "Account-1's S2/S4 reading, that a step-100 plain sample "
                                                         'which does not open deliberatively is an unswitched '
                                                         'plain-base answer, is wrong: after 100 RL steps the '
                                                         'weights carry a graded shift in every sample, so how a '
                                                         'sample opens says little about whether it is right. The '
                                                         "cue's +8.5 of 500 is spread thinly over samples, not "
                                                         'concentrated in a few base-like ones.',
                                                  'instead': 'Sentence 6 (the shift is graded and present in every '
                                                             'sample): on the same problems the step-100 cue samples '
                                                             'beat the non-deliberative plain samples by little, D1 '
                                                             'in [-0.10, 0.12].',
                                                  'range': [-0.1, 0.12]}],
                                     'plan_n': 70,
                                     'value': 0.1753,
                                     'lo': 0.1202,
                                     'hi': 0.2304,
                                     'n': 174,
                                     'adversary': 0.5344,
                                     'verdicts': {'1': 'undecided', '2': 'refuted'},
                                     'measured': {'1': '0.175 [0.120, 0.230], n 174, adversary value 0.534',
                                                  '2': '0.175 [0.120, 0.230], n 174, adversary value 0.534'},
                                     'record_claim': {'1': 'At RL step 100 the plain samples that do not open '
                                                           'deliberatively are unswitched plain-base answers, so on '
                                                           'the same problem the cued step-100 model is right far '
                                                           'more often than they are.',
                                                      '2': 'After 100 RL steps the shift is graded and present in '
                                                           'every sample, so the step-100 cue samples beat the '
                                                           'non-deliberative plain samples by little (D1 in [-0.10, '
                                                           '0.12]).'},
                                     'result': 'result-f89757',
                                     'added': '2026-11-16T00:12:39'},
           'round-16/account-3/c1': {'owner': '3',
                                     'claim': 'S2 and S4: by step 100 the per-token hold-on shift is partly in the '
                                              'weights, in every sample. So a step-100 plain sample that does not '
                                              'open deliberatively still deliberates later and is right more often '
                                              "than the untrained plain base's non-deliberative answer to the same "
                                              'problem. But it lacks the first-token part, so it gains less than the '
                                              'full cue gain of about 0.5. A switch account (an unswitched sample is '
                                              'a plain-base answer) gives about 0. An accuracy-only account (every '
                                              'step-100 sample is as good as its average one) gives the full '
                                              'step-100-minus-plain gap of about 0.45-0.55.',
                                     'statistic': "D = mean over problems of (right rate of the problem's "
                                                  'non-deliberative step-100 plain samples minus right of the plain '
                                                  "base's T3 answer), as a fraction (0-1)",
                                     'null': 'The switch null (account-1 S2/S4): a step-100 sample that does not '
                                             'open deliberatively is an untrained plain-base answer, so D is about 0 '
                                             'apart from sampling noise.',
                                     'why_new': 'F07 is pooled over all samples, F51 uses the untrained base only, '
                                                'and F25/F41/F49 measure length, cap hits and the vote. No fact or '
                                                'result compares step-100 samples, split by their opening, with the '
                                                "plain base's answers on the same problems.",
                                     'ranges': {'3': [0.1, 0.38], 'null': [-0.08, 0.06]},
                                     'alternative': 'Accuracy plus problem difficulty, with no claim about what the '
                                                    'opening means. Being in the rows depends on two things: T3 '
                                                    'opens non-deliberatively, and step 100 still writes at least '
                                                    'one quick, non-deliberative opening. Step 100 opens that way '
                                                    "mainly on easy problems. On easy problems the plain base's "
                                                    'answer-first T3 reply is also right fairly often, so t on these '
                                                    '60 rows is well above the 0.29 that non-deliberative T3 answers '
                                                    'average over all 351 such problems (from result-1f98b0: T3 - T1 '
                                                    '= -0.516 against T1 of about 0.82). If the opening flag carries '
                                                    'no information about rightness within a problem, a '
                                                    'non-deliberative step-100 sample is right at the step-100 '
                                                    "model's own per-problem rate. Then D equals the accuracy-only "
                                                    'value: step-100 per-sample right rate on easy problems (about '
                                                    "0.9) minus the base's T3 right rate on the same problems (about "
                                                    '0.55-0.6). That gap is about 0.3, inside [0.10, 0.38]. The '
                                                    "step-100 model's general reliability gain over the plain base "
                                                    'and the easiness of the selected problems are enough to produce '
                                                    'the number.',
                                     'denials': [],
                                     'plan_n': 60,
                                     'value': 0.3588,
                                     'lo': 0.2723,
                                     'hi': 0.444,
                                     'n': 131,
                                     'adversary': 0.4733,
                                     'verdicts': {'3': 'undecided'},
                                     'measured': {'3': '0.359 [0.272, 0.444], n 131, adversary value 0.473'},
                                     'record_claim': {'3': 'By step 100 the hold-on shift is partly in the weights, '
                                                           'so a step-100 plain sample that does not open '
                                                           'deliberatively is right more often than the plain base '
                                                           'T3 answer on the same problem, by less than the full cue '
                                                           'gain (D in [0.10, 0.38]).'},
                                     'result': 'result-739c31',
                                     'added': '2026-11-16T00:12:34'}}}


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


def _build16(ref=""):
    plans = {t["name"]: t for t in _load(ref, W16 + "synthesis_tests.json")}
    assert set(plans) == set(TESTS16), f"TESTS16 differ from round 16's synthesis_tests.json: {sorted(set(plans) ^ set(TESTS16))}"
    rows = {x["mechanism"]: x for x in rows_all(ref) if x["mechanism"].startswith("round-16/")}
    accounts, tests = {}, {}
    for k in ("1", "2", "3"):
        a = _load(ref, W16 + f"account-{k}.json")
        blind = _load(ref, W16 + f"marks-account-{k}.json")["marks"]
        marks = {m: sum(x["mark"] == m for x in blind) for m in ("explained", "not addressed", "contradicts")}
        assert sum(marks.values()) == len(blind)
        accounts[k] = {"sentences": a["account"], "marks": marks, "facts": len(blind),
                       "own_contradicts": sum(x["mark"] == "contradicts" for x in a["marks"]),
                       "contradicts": [[x["fact"], x["why"]] for x in blind if x["mark"] == "contradicts"]}
    for name, t in TESTS16.items():
        plan = plans[name]
        mech = {a.split("-")[1]: i for a, i in plan["mechanisms"].items()}  # {account: mechanism id}
        row = rows[mech[plan["owner"].split("-")[1]]]
        for i in mech.values():  # one measurement: every row of the test has the same interval, adversary and n
            assert [rows[i][x] for x in ("interval", "adversary", "n", "result")] == [row[x] for x in ("interval", "adversary", "n", "result")], i
        v = _get(_load(ref, f"{R}direct/{t[2]}/metrics.json"), t[3])
        lo, hi = row["interval"]
        assert lo <= v <= hi, name
        tests[name] = {
            "owner": plan["owner"].split("-")[1], "claim": plan["claim"], "statistic": plan["statistic"],
            "null": plan["null"], "why_new": plan.get("why_new", ""),
            "ranges": {(a.split("-")[1] if a != "null" else "null"): r for a, r in plan["ranges"].items()},
            "alternative": plan["adversary"]["alternative"],
            "denials": [{"by": d["by"].split("-")[1], "why": d["why"], "instead": d["instead"], "range": d["range"]}
                        for d in plan["denials"]],
            "plan_n": plan["n"], "value": round(v, 4), "lo": round(lo, 4), "hi": round(hi, 4), "n": row["n"],
            "adversary": round(row["adversary"], 4),
            "verdicts": {k: rows[i]["verdict"] for k, i in mech.items()},
            "measured": {k: rows[i]["measured"] for k, i in mech.items()},
            "record_claim": {k: rows[i]["claim"] for k, i in mech.items()},
            "result": row["result"], "added": row["added"].rstrip("Z")[:19],
        }
    facts = _load(ref, W16 + "synthesis_facts.json")
    assert all(a["facts"] == len(facts) for a in accounts.values()), "every blind marker marks every fact once"
    return {"facts": len(facts), "accounts": accounts, "tests": tests}


def _tally16(rec):
    """Round 16's counts. held, not_separated, refuted, undecided, tested: the owners' verdicts on the 9 consequences.
    denials, denials_decided, denials_against_denier: the 4 denials. adversary_inside: tests whose interval contains the
    adversary's value. edge: undecided consequences whose interval crosses an edge of the owner's range. accounts[k]:
    that account's own counts and its score (holds and denials held minus facts the blind marker marks against it)."""
    if not rec:
        return {}
    ts = rec["tests"].values()
    own = [t["verdicts"][t["owner"]] for t in ts]
    den = [v for t in ts for k, v in t["verdicts"].items() if k != t["owner"]]
    acc = {}
    for k, a in rec["accounts"].items():
        o = [t["verdicts"][k] for t in ts if t["owner"] == k]
        d = [t["verdicts"][k] for t in ts if k in t["verdicts"] and t["owner"] != k]
        acc[k] = {"held": o.count("holds"), "not_separated": o.count("not separated"), "refuted": o.count("refuted"),
                  "undecided": o.count("undecided"), "tested": len(o), "denials": len(d),
                  "denials_held": d.count("holds"), "denials_refuted": d.count("refuted"),
                  "denials_undecided": d.count("undecided"), "explained": a["marks"]["explained"],
                  "unaddressed": a["marks"]["not addressed"], "contradicts": a["marks"]["contradicts"],
                  "own_contradicts": a["own_contradicts"],
                  "score": o.count("holds") + d.count("holds") - a["marks"]["contradicts"]}
    edge = sum(t["verdicts"][t["owner"]] == "undecided" and (t["lo"] < t["ranges"][t["owner"]][0] <= t["hi"] or
               t["lo"] <= t["ranges"][t["owner"]][1] < t["hi"]) for t in ts)
    c = {"held": own.count("holds"), "not_separated": own.count("not separated"), "refuted": own.count("refuted"),
         "undecided": own.count("undecided"), "tested": len(own), "denials": len(den),
         "denials_decided": sum(v != "undecided" for v in den), "denials_against_denier": den.count("refuted"),
         "adversary_inside": sum(t["lo"] <= t["adversary"] <= t["hi"] for t in ts), "edge": edge,
         "facts": rec["facts"], "accounts": acc}
    assert c["held"] + c["not_separated"] + c["refuted"] + c["undecided"] == c["tested"]
    return c


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


# COUNTS: the top-level keys are round 15's (held, refuted, undecided, tested: its 9 consequences under round 15's
# rule; not_separated: its holds that the engine-16 retest could not separate). COUNTS["r16"] holds round 16's (see
# _tally16), and COUNTS["rounds"] both rounds' headline numbers by round.
COUNTS = _tally(RECORD)
_c = COUNTS
_a = _c.get("accounts", {})
_d = _tally16(RECORD16)
if _c and _d:
    COUNTS["r16"] = _d
    COUNTS["rounds"] = {r: {k: x[k] for k in ("held", "not_separated", "refuted", "undecided", "tested")}
                        for r, x in (("15", _c), ("16", _d))}
    COUNTS["newest"] = "16"
_e = _d.get("accounts", {})
LINE = (f"Under round 15's rule, {_c.get('held')} of {_c.get('tested')} claims about what RL changed held; in round 16, with "
        f"a blind adversary's prediction as the bar, {_d.get('held')} of {_d.get('tested')} held.")
# An example opens an address: the round ("15/" or nothing for 16), then a claim.
EXAMPLES = [["a2c2", "Example: the one claim the adversary matched"], ["a1c1", "Example: a denial decided against the denier"],
            ["15/d1", "Example (round 15): the one disagreement, and its test"]]


def _acc_line(k):
    x = _a[k]
    return (f"account {k}: {x['held']} held, {x['refuted']} refuted, {x['undecided']} undecided; {x['explained']} of "
            f"{_c['facts']} facts marked explained, {x['contradicts']} marked against it; score {x['score']}")


PANELS = [] if not (_c and _d) else [
    ["new", "What is new",
     f"Until round 14 the team's theory engine wrote one cause per surprising number, and those lost: in round 14, "
     f"{_c['round14'][0]} of {_c['round14'][1]} rival causes held their test. Round 15 asked each of three agents for one "
     f"account of all {_c['facts']} directly tested facts.",
     ["The agents worked blind to each other. Each account had to name 3 new consequences that stored data could check, "
      "with the account's range and the null's range fixed before the check. A judge found one point where they "
      "disagree (d1).",
      f"Round 16 made the bar harder. The three accounts, of {_d['facts']} facts, were written in turn, each denying "
      "claims of the earlier ones, and a blind adversary predicted every consequence's value without the account. A "
      "consequence holds only if its interval lies in the account's range and excludes the adversary's value.",
      "AutoCog (arXiv 2606.26448, abstract and its loop's stages 3 and 4) has language-model agents advocate competing "
      "theories, run experiments that tell them apart and revise the weaker one. Here the accounts are not revised: "
      "their consequences are checked once, on data already stored.",
      ["Mechanisms tested directly: the one-cause-per-number approach this round replaced ›", "/finding/mechanisms-tested-directly"],
      ["Theories on trial: the same engine's theories, scored on their predictions ›", "/finding/theories-on-trial"]]],
    ["why", "Why it matters",
     f"Under the stricter rule no account has earned a hold yet: round 16 has {_d['held']} of {_d['tested']}, and round 15's "
     f"{_c['held']} holds become {_c['held'] - _c['not_separated']} once the retest's adversary is applied.",
     [f"The story itself barely changed between rounds: the round 16 accounts repeat round 15's, and the sentences on "
      "this page are nearly the same in both.",
      f"All {_d['denials_decided']} decided denials went against the account that denied: the later accounts denied "
      "claims the data supports in direction.",
      f"Round 15's account 2 won its round under the old rule: {_a['2']['held']} of {_a['2']['tested']} held and the one "
      "disagreement went its way.","The disagreement was the most informative test: the 8-direction edit wins the problems Base + cue cannot solve in "
      "4 samples about as often as RL does (edit minus RL −0.013, 90 % interval −0.037 to 0.010, 120 problems).",
      f"{_c['held']} of {_c['tested']} new consequences held in round 15, against {_c['round14'][0]} of "
      f"{_c['round14'][1]} rival causes in round 14."]],
    ["how", "How we know",
     "Each of the 10 tests ran offline on stored answers or weights, one agent per test, with its plan, null and "
     "ranges committed before the data was read.",
     ["A claim holds when its 90 % interval lies wholly inside its range with n of 50 or more, is refuted when the "
      "interval lies wholly outside, and is undecided otherwise.",
      "Score: consequences that hold minus facts the account marks as against it. " + "; ".join(
          _acc_line(k) for k in ("2", "1", "3")) + ".",
      "Counts are read from the record files and agree with the board item (result-61a7ab) and synthesis.md.",
      "The first run of d1 read 102 of its 121 problems; the rerun (editreach-02, result-b90743) replaced it and "
      "moved account 2 from undecided to holds.",
      "Round 16 (engine 16): the adversary's value was computed first in every test. Holds: interval inside the range "
      "and excluding the adversary's value; not separated: inside the range but containing it; refuted: wholly outside; "
      "otherwise undecided. 9 tests in 9 agents; board item result-368932."]],
    ["limits", "What it does not show",
     f"Round 16's {_d['held']} of {_d['tested']} does not show the accounts are wrong: {_d['undecided']} of the 9 are "
     f"undecided, all {_d['edge']} at an edge of the account's range, and the adversary's value missed the measured "
     f"interval in {_d['tested'] - _d['adversary_inside']} of 9 tests.",
     ["The adversaries could not read the stored rows, so they guessed; their values were rarely the bar that "
      "decided. The ranges the accounts fixed were narrower than the data's noise.",
      "The flag for a deliberate opening, used by three round 16 tests, misreads answers that echo prompt text before "
      "'Okay'; no planted failure had checked it.",
      f"Round 15: a stricter retest found {_c['not_separated']} of account 2's holds not separated: a blind adversary, "
      "without the account, predicted a value inside each interval (board item result-61c569).","The retested holds are c1 (wrong answers scatter), c2 (step 100's vote gain) and d1; c3 was counted as the same "
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
     [f"Round 16: {W16} (account-*.json, marks-account-*.json, adversary/, synthesis_tests.json, synthesis.md) and "
      "studies/theory/results/direct/r16<account><claim>-01/; board item result-368932.",
      f"Files: {W} (account-1.json to account-3.json, disagreements.json, synthesis_tests.json, synthesis.md)" +
      (f" on branch {REF.split('/')[-1]}" if REF else "") + f", commit {COMMIT}.",
      "Each test: studies/theory/results/direct/<test>/metrics.json, its spec studies/theory/specs/SPEC_direct_<name>.md "
      "and the README section Round 15; the round's plan is studies/theory/specs/SPEC_round15.md.",
      "Board items: result-61a7ab (the round), result-b90743 (d1), and one per claim, named when it is open."]],
]


def _key(name):  # round-15/account-2/c1 -> a2c1; round-15/d1 -> d1
    return "d1" if name.endswith("/d1") else re.sub(r"round-1\d/account-(\d)/(c\d)", r"a\1\2", name)


def _vk(v):
    return {"holds": "h", "refuted": "r", "undecided": "u", "not separated": "s"}[v]


def _round15():
    rec, c = RECORD, COUNTS
    nodes = [{"text": n[0], "sent": {"1": n[1], "3": n[2]}, "st": {"1": n[3], "2": "same", "3": n[4]},
              "clauses": None, "split": None} for n in NODES]
    nodes[4]["clauses"] = dict(CLAUSES)
    nodes[4]["split"] = [["2", "Account 2: " + CLAUSES["2"][4:]], ["1", "Account 1: " + CLAUSES["1"][4:]]]
    tests = []
    for name in TEST_ORDER:
        t, r = TESTS[name], rec["tests"][name]
        re16 = next(iter(r["retest"].values()), None)
        tests.append({**r, "key": _key(name), "name": name, "label": t[0], "node": t[1] - 1, "folder": t[2], "nunit": t[6],
                      "unit": t[8], "dom": t[9], "caveat": t[10], "owner": "" if name.endswith("/d1") else next(iter(r["verdicts"])),
                      "adversary": re16["adversary"] if re16 else None, "denials": []})
    lines = {}
    for k, x in c["accounts"].items():
        d = {"holds": "it won the one disagreement", "refuted": "it lost the one disagreement"}.get(x["d1"], "it took no side in the one disagreement")
        lines[k] = (f"Account {k}: {x['held']} of {x['tested']} held" + (f", {x['refuted']} refuted" if x["refuted"] else "") +
                    (f", {x['undecided']} undecided" if x["undecided"] else "") + f"; {d}.")
    return {"base": "2", "split_acc": "2", "facts": rec["facts"], "accounts": rec["accounts"], "nodes": nodes,
            "extra": {"node": 5, "acc": "3", "lines": EXTRA3}, "tests": tests, "target": c["held"], "tested": c["tested"],
            "set": f"Round 15 · three accounts of {rec['facts']} tested facts",
            "bl0": "new claims held their test on stored data.",
            "bl1": f"{c['refuted']} refuted, {c['undecided']} undecided. Retest: {c['not_separated']} not separated.",
            "acc_lines": lines, "split_line": f"The judge found {c['disagreements']} point where the accounts disagree; one test decided it.",
            "keys": [["rg", "Account's range, fixed before"], ["nl", "Null's range"], ["h", "Holds"], ["r", "Refuted"],
                     ["u", "Undecided"], ["adv", "Adversary's value, retest"]],
            "focus": "d1", "contested": [4]}


def _round16():
    rec, c = RECORD16, _d
    nodes = [{"text": n[0], "sent": n[1], "st": {"1": "same", **n[2]}, "clauses": None, "split": None} for n in NODES16]
    for i, x in CLAUSES16.items():
        nodes[i]["clauses"] = {k: x[k] for k in ("1", "2", "3")}
        nodes[i]["split"] = x["split"]
    tests = []
    for name in TEST_ORDER16:
        t, r = TESTS16[name], rec["tests"][name]
        tests.append({**r, "key": _key(name), "name": name, "label": t[0], "node": t[1] - 1, "folder": t[2], "nunit": t[5],
                      "unit": t[4], "dom": t[6], "caveat": t[7], "null_value": None, "retest": {}})
    lines = {}
    for k, x in c["accounts"].items():
        own = ", ".join(f"{x[a]} {b}" for a, b in (("held", "held"), ("not_separated", "not separated"),
                                                   ("refuted", "refuted"), ("undecided", "undecided")) if x[a])
        den = ("it denied no claim" if not x["denials"] else
               f"both its denials refuted" if x["denials_refuted"] == x["denials"] == 2 else
               f"its denials: {x['denials_refuted']} refuted, {x['denials_undecided']} undecided")
        lines[k] = f"Account {k}: {own}; {den}."
    return {"base": "1", "split_acc": "1", "facts": rec["facts"], "accounts": rec["accounts"], "nodes": nodes,
            "extra": None, "tests": tests, "target": c["held"], "tested": c["tested"],
            "set": f"Round 16 · three accounts in turn, {rec['facts']} facts",
            "bl0": "new claims held against the adversary's value.",
            "bl1": f"{c['not_separated']} not separated, {c['refuted']} refuted, {c['undecided']} undecided.",
            "acc_lines": lines,
            "split_line": f"{c['denials']} denials between accounts; the {c['denials_decided']} decided all went against the denier.",
            "keys": [["rg", "Account's range, fixed before"], ["nl", "Null's range"], ["s", "Not separated"], ["r", "Refuted"],
                     ["u", "Undecided"], ["adv", "Adversary's value"]],
            "focus": "a2c2", "contested": [1, 2]}


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
.pt.s { fill: var(--sheet); stroke: var(--blue); stroke-width: 1.8; }
.ci.s { stroke: var(--blue); opacity: .55; }
.gv.s { fill: var(--blue) !important; }
.rounds { display: inline-flex; gap: 16px; margin-right: 14px; }
.rounds button { font-size: 13.5px; color: var(--mute); padding: 6px 1px 4px; border-bottom: 1px solid transparent; transition: color .15s ease; white-space: nowrap; }
.rounds button:hover { color: var(--ink); }
.rounds button[aria-pressed="true"] { color: var(--ink); font-weight: 640; border-bottom-color: var(--ink); }
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
  .rounds { margin: 0 0 4px; justify-content: center; }
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
      <div class="rounds" id="rounds" role="group" aria-label="Round"></div>
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

/* Two controls. The round (15, or 16, the newest and the first view) picks whose accounts and tests stand on the plate.
   The account: read as account 1, 2 or 3, or where they disagree; the first view reads the round's best account. */
const ROUNDS = Object.keys(C.rounds).sort(), NEWEST = C.newest;
const STATES = ["a1", "a2", "a3", "split"], SNAME = ["Account 1", "Account 2", "Account 3", "Where they disagree"];
const VK = { holds: "h", refuted: "r", undecided: "u", "not separated": "s" };
const VFULL = { h: "holds", r: "refuted", u: "undecided", s: "not separated", n: "no side" };
const CAP = s => s[0].toUpperCase() + s.slice(1);
let RD, T, TK, NODES, NK, FOCUS;
const ACC = s => s === 3 ? RD.split_acc : String(s + 1);  // whose verdicts the picture shows
/* One round's tests and sentences, ready to draw. */
function useRound(r) {
  RD = C.rounds[r]; RD.r = r;
  T = RD.tests.map((x, i) => ({ ...x, i, r: x, acc: Object.keys(x.ranges).filter(k => k !== "null").sort(),
                               multi: Object.keys(x.ranges).filter(k => k !== "null").length > 1 }));
  TK = Object.fromEntries(T.map(t => [t.key, t]));
  FOCUS = TK[RD.focus];
  NODES = RD.nodes.map((n, i) => ({ ...n, i, key: "s" + (i + 1), tests: T.filter(t => t.node === i) }));
  NK = Object.fromEntries(NODES.map(n => [n.key, n]));
}
/* The verdict a test's mark shows in a state: the account read, where it took a side; else the claim's owner. */
function vOf(t, s) {
  const v = t.verdicts[ACC(s)] || (t.owner ? t.verdicts[t.owner] : null);
  return v ? VK[v] : "n";
}
const S = { round: NEWEST, s: 0, open: null, g: null, el: {}, shown: {}, last: 0, dirty: true, rp: null, rpNext: 0, rpAt: 0,
            started: false, enterT: -1e9, entered: false, d1t: -1e9, bigFrom: null, bigT: -1e9 };
const BEST = r => r === "15" ? 1 : 0;  // the account the first view reads in each round

/* Geometry, in plate units (x right, y down; z toward the viewer). */
function geo() {
  return narrow.matches
    ? { w: 480, cx: 240, D: 2000, r: 22, deep: 30, blur: 12, phone: true, fs: 17.5, fb: 84, fn: 17.5, lh: 23, fg: 17, fk: 17,
        setX: 24, setY: 50, bigX: 20, bigY: 132, labX: 24, labY: [178, 204, 234], top: 352,
        sx0: 52, sx1: 456, bead: 26, agX: 26, agY: 22, gx0: 52, gx1: 456, gv: 170, pitch: 50, gap: 30 }
    : { w: 1000, cx: 500, D: 2200, r: 30, deep: 40, blur: 16, phone: false, fs: 14, fb: 84, fn: 15.5, lh: 20.5, fg: 13, fk: 13,
        setX: 58, setY: 58, bigX: 52, bigY: 136, labX: 320, labY: [98, 120, 146], top: 222,
        sx0: 98, sx1: 538, bead: 70, agX: 558, agY: 0, gx0: 606, gx1: 952, gv: 134, pitch: 40, gap: 18 };
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

/* The layout: each sentence a block, its claims beside it (on a phone, under it). A sentence whose end differs by
   account keeps two clause slots: the account's own, and in the disagreement view a second one. */
function layout(g) {
  const L = { nodes: [], rows: {} };
  let y = g.top;
  const sw = g.sx1 - g.sx0;
  NODES.forEach(n => {
    const lines = wrap(n.text, sw, g.fn, "sn");
    let h = lines.length * g.lh;
    const nd = { y, lines, ly: lines.map((_, j) => y + j * g.lh) };
    if (n.clauses) {
      nd.cv = Object.fromEntries(Object.entries(n.clauses).map(([k, s]) => [k, wrap(s, sw, g.fn, "cl")]));
      nd.sv = n.split.map(([, s]) => wrap(s, sw, g.fn, "cl"));
      const n0 = Math.max(...Object.values(nd.cv).map(x => x.length), nd.sv[0].length), n1 = nd.sv[1].length;
      nd.cy = [y + h, y + h + n0 * g.lh]; h += (n0 + n1) * g.lh;
    }
    if (RD.extra && RD.extra.node === n.i) {
      const ex = RD.extra.lines.flatMap(s => wrap(s, g.phone ? sw : g.gx1 - g.gx0, g.fg + .5, "ex"));
      if (g.phone) { nd.ey = ex.map((_, j) => y + h + 4 + j * g.lh * .9); h += ex.length * g.lh * .9 + 4; }
      else nd.ey = ex.map((_, j) => y + 2 + j * g.lh * .92);
      nd.ex = ex;
    }
    let gy = g.phone ? y + h + 14 : y - 6;
    n.tests.forEach(t => {
      const tall = t.multi ? g.fg + 8 : 0;  // a test of two accounts names their ranges under its axis
      L.rows[t.key] = { y: gy, tall, box: [g.gx0 - 6, gy - g.fg - 5, g.gx1 + 6, gy + 20 + tall] };
      gy += g.pitch + tall;
    });
    const gh = n.tests.length ? gy - (g.phone ? y + h + 14 : y - 6) : 0;
    const block = g.phone ? h + (gh ? gh + 14 : 0) : Math.max(h, gh - 8);
    nd.box = [g.phone ? 10 : g.bead - 16, y - g.fn - 2, g.sx1 + 8, y + h - g.fn + 4];
    L.nodes.push(nd);
    y += block + g.gap;
  });
  L.bottom = y - g.gap;
  return L;
}

function build() {
  const g = S.g = geo(), svg = $("svg");
  svg.innerHTML = `<text id="meas" x="-999" y="-999" style="opacity:0"></text>`;
  S.meas = svg.firstChild;
  S.L = layout(g);
  g.keyY = S.L.bottom + (g.phone ? 34 : 26);
  g.rpY = g.keyY + (g.phone ? 118 : 0);
  g.h = g.rpY + (g.phone ? 64 : 26);
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
  T.forEach(t => {
    fg += `<path class="ax" id="ax${t.i}"/>`;
    fg += t.multi ? `<rect class="rg2" id="rgA${t.i}" height="9"/><rect class="rg" id="rgB${t.i}" height="9"/>` : `<rect class="rg" id="rg${t.i}" height="9"/>`;
    fg += `<path class="adv" id="adv${t.i}"/><rect class="nl" id="nl${t.i}" height="9"/><path class="ci" id="ci${t.i}"/><circle class="halo" id="ha${t.i}" r="0"/><circle class="pt" id="pt${t.i}" r="0"/>`;
  });
  fg += `<circle class="burst" id="bu" r="0"/>`;
  fg += `<g class="key">` + RD.keys.map(([k], j) => k === "rg" ? `<rect class="rg" id="kd${j}" width="18" height="9"/>` :
    k === "nl" ? `<rect class="nl" id="kd${j}" width="18" height="9"/>` : k === "adv" ? `<path class="adv" id="kd${j}"/>` : `<circle class="pt ${k}" id="kd${j}" r="4.2"/>`).join("") + `</g>`;
  let tx = X("set", "set", g.fs) + X("big", "big", g.fb) + X("lab0", "bl0", g.fs + (g.phone ? 0 : 2.5)) + X("lab", "bl1", g.fs + 1.5) + X("lab2", "bl2", g.fs + 1.5) +
    X("hd", "h1", g.fg) + X("hd", "h2", g.fg);
  ["1", "2", "3"].forEach(k => { tx += X("hd", "ah" + k, g.fg - 1, ` text-anchor="middle"`); });
  NODES.forEach((n, i) => {
    tx += X("num", "nn" + i, g.fg, ` text-anchor="middle"`);
    S.L.nodes[i].lines.forEach((_, j) => { tx += X("sn", `s${i}_${j}`, g.fn); });
    if (n.clauses) tx += X("cl", `cl${i}_0`, g.fn) + X("cl", `cl${i}_1`, g.fn);
    (S.L.nodes[i].ex || []).forEach((_, j) => { tx += X("ex", "ex" + j, g.fg + .5); });
  });
  T.forEach(t => {
    tx += X("gl", "gl" + t.i, g.fg) + X("gv", "gv" + t.i, g.fg, ` text-anchor="end"`);
    if (t.multi) tx += X("bl", "blA" + t.i, g.fg - (g.phone ? 0 : .5), ` text-anchor="middle"`) + X("bl", "blB" + t.i, g.fg - (g.phone ? 0 : .5), ` text-anchor="middle"`);
  });
  tx += RD.keys.map((_, j) => X("kt", "kt" + j, g.fk)).join("") + X("kt", "ktA", g.fk) + X("rp", "rp", g.fk, g.phone ? "" : ` text-anchor="end"`);
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

/* Texts and positions that do not move with the account: written once per build, in plate units. */
function statics() {
  const g = S.g, E = S.el, L = S.L;
  const at = (el, x, y) => { el.setAttribute("x", f(x)); el.setAttribute("y", f(y)); };
  at(E.set, g.setX, g.setY); at(E.big, g.bigX, g.bigY);
  g.labY.forEach((y, j) => at(E["bl" + j], g.labX, y));
  E.set.textContent = RD.set; E.bl0.textContent = RD.bl0; E.bl1.textContent = RD.bl1;
  const hy = g.top - (g.phone ? 46 : 34);
  E.hair.setAttribute("d", `M${g.phone ? 24 : 58} ${f(hy - (g.phone ? 26 : 22))}H${g.phone ? 456 : 942}`);
  at(E.h1, g.phone ? 24 : g.bead - 12, hy); E.h1.textContent = `Account ${RD.base}, in plain words`;
  at(E.h2, g.gx0, hy); E.h2.textContent = g.phone ? "" : "New claims, against ranges fixed in advance";
  ["1", "2", "3"].forEach((k, j) => {
    if (g.phone) { at(E["ah" + k], -99, -99); return; }
    at(E["ah" + k], g.agX + 14 * j, hy);
    E["ah" + k].textContent = k;
  });
  const by = n => L.nodes[n.i].y - g.fn * .35;
  E.spine.setAttribute("d", `M${g.bead} ${f(by(NODES[0]))}V${f(by(NODES[NODES.length - 1]))}`);
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
    (nd.ex || []).forEach((s, j) => { const e = E["ex" + j]; at(e, g.phone ? g.sx0 : g.gx0, nd.ey[j]); e.textContent = s; });
  });
  T.forEach(t => {
    const rw = L.rows[t.key], ay = rw.y + (g.phone ? 15 : 13);
    at(E["gl" + t.i], g.gx0, rw.y); at(E["gv" + t.i], g.gx1, ay + g.fg * .36);
    E["gl" + t.i].textContent = `${t.multi ? t.acc.join(" vs ") : t.owner} · ${t.label}`;
    E["ax" + t.i].setAttribute("d", `M${g.gx0} ${f(ay + .5)}H${g.gx1 - g.gv}`);
    t.X = xscale(t, g);
    t.ay = ay;
    const band = (el, r) => { const a = t.X(r[0]), b = t.X(r[1]); el.setAttribute("x", f(a)); el.setAttribute("y", f(ay - 4.5)); el.setAttribute("width", f(Math.max(1, b - a))); };
    band(E["nl" + t.i], t.ranges.null);
    E["adv" + t.i].setAttribute("d", t.adversary != null ? `M${f(t.X(t.adversary))} ${f(ay - 8)}V${f(ay + 9)}` : "");
    if (t.multi) {
      band(E["rgA" + t.i], t.ranges[t.acc[0]]); band(E["rgB" + t.i], t.ranges[t.acc[1]]);
      const mid = r => (t.X(r[0]) + t.X(r[1])) / 2;
      at(E["blA" + t.i], mid(t.ranges[t.acc[0]]), ay + 10 + g.fg); at(E["blB" + t.i], mid(t.ranges[t.acc[1]]), ay + 10 + g.fg);
    } else band(E["rg" + t.i], t.ranges[t.owner]);
  });
  const ky = g.keyY, xs = g.phone ? [24, 274, 24, 190, 330, 24] : [58, 280, 386, 510, 586, 674], ys = g.phone ? [ky, ky, ky + 30, ky + 30, ky + 30, ky + 60] : [ky, ky, ky, ky, ky, ky];
  RD.keys.forEach(([k, name], j) => {
    const d = E["kd" + j];
    if (k === "rg" || k === "nl") { d.setAttribute("x", xs[j]); d.setAttribute("y", f(ys[j] - 4.5)); }
    else if (k === "adv") d.setAttribute("d", `M${xs[j] + 6} ${f(ys[j] - 8)}V${f(ys[j] + 8)}`);
    else { d.setAttribute("cx", xs[j] + 6); d.setAttribute("cy", f(ys[j])); }
    at(E["kt" + j], xs[j] + (k === "rg" || k === "nl" ? 26 : k === "adv" ? 14 : 16), ys[j] + g.fk * .36);
    E["kt" + j].textContent = name;
  });
  at(E.ktA, g.phone ? 24 : 850, g.phone ? ky + 90 : ky + g.fk * .36);
  E.ktA.textContent = g.phone ? "1, 2, 3: the three accounts; a dot: it states the sentence" : "1, 2, 3: accounts";
  E.rp.setAttribute("x", g.phone ? 24 : 942); E.rp.setAttribute("y", f(g.phone ? g.rpY + 28 : g.setY));
}
/* Each claim's own axis: its ranges, interval and the adversary's value with a margin; a range beyond the axis ends. */
function xscale(t, g) {
  const xs = [t.value, t.lo, t.hi, ...Object.values(t.ranges).flat(), ...(t.adversary != null ? [t.adversary] : [])];
  let a = Math.min(...xs), b = Math.max(...xs);
  if (t.dom) { a = t.dom[0]; b = t.dom[1]; }
  const pad = (b - a) * .04;
  a -= pad; b += pad;
  return x => g.gx0 + (g.gx1 - g.gv - g.gx0) * (clamp(x, a, b) - a) / (b - a);
}

/* The line under the large number: the account read, or the disagreements. Two lines on a phone. */
function stateText() {
  const s = S.s, E = S.el, line = s === 3 ? RD.split_line : RD.acc_lines[ACC(s)];
  if (S.shown.bl2 === line) return;
  S.shown.bl2 = line;
  const g = S.g, parts = g.phone ? line.replace("; ", ";\n").split("\n") : [line];
  E.bl2.innerHTML = parts.map((p, i) => `<tspan x="${g.labX}" y="${f(g.labY[2] + i * (g.fs + 6))}">${esc(p)}</tspan>`).join("");
}

/* Where the moving parts are now. On an account change the values of the tests two accounts share travel from 0 to
   their measured value; on a round change every value travels in from the null's range and the count follows. */
function place(now) {
  const g = S.g, E = S.el;
  E.back.setAttribute("d", rounded(g, g.a, g.r, -g.deep));
  E.plate.setAttribute("d", rounded(g, g.a, g.r, 0));
  const z = 10, A = proj(g, 0, 0, z), B = proj(g, g.w, 0, z), Cc = proj(g, 0, g.h, z);
  const m6 = [(B[0] - A[0]) / g.w, (B[1] - A[1]) / g.w, (Cc[0] - A[0]) / g.h, (Cc[1] - A[1]) / g.h, A[0], A[1]];
  E.fg.setAttribute("transform", `matrix(${m6.map(v => v.toFixed(4)).join(" ")})`);
  E.tx.setAttribute("transform", `matrix(${m6[0].toFixed(4)} 0 0 ${m6[3].toFixed(4)} ${m6[4].toFixed(2)} ${m6[5].toFixed(2)})`);
  const s = S.s, k = ACC(s), split = s === 3;
  const txt = (id, v) => { if (S.shown[id] !== v) E[id].textContent = S.shown[id] = v; };
  // the large number: the owners' holds as their values land; on a round change it counts from the old round's number
  const landed = T.filter(t => t.owner && landP(t, now) >= 1 && t.verdicts[t.owner] === "holds").length;
  const bq = clamp((now - S.bigT) / (800 + 90 * T.length + 800), 0, 1), big = S.bigFrom != null && bq < 1 ? Math.round(mix(S.bigFrom, RD.target, ease(bq))) : landed;
  S.bigNow = big;
  txt("big", `${big} of ${RD.tested}`);
  E.bl0.style.opacity = E.bl1.style.opacity = E.bl2.style.opacity = clamp((now - S.enterT) / 600, 0, 1).toFixed(2);
  if (!S.dirty && !moving(now)) { replay(now); return; }
  const sel = S.open && TK[S.open] ? TK[S.open] : null, seln = S.open && NK[S.open] ? NK[S.open] : null;
  const dp = clamp((now - S.d1t) / 900, 0, 1), cf = still.matches ? 1 : clamp((now - S.d1t) / 350, 0, 1);
  const contested = n => RD.contested.includes(n.i);
  const dimN = n => (split && !contested(n)) || (seln && seln !== n) || (sel && sel.node !== n.i) ? .26 : 1;
  const dimT = t => (split && !t.multi && !contested(NODES[t.node])) || (sel && sel !== t) || (seln && seln.i !== t.node) ? .26 : 1;
  NODES.forEach((n, i) => {
    const o = dimN(n), nd = S.L.nodes[i];
    nd.lines.forEach((_, j) => { E[`s${i}_${j}`].style.opacity = o; });
    E["nn" + i].style.opacity = o; E["bd" + i].style.opacity = o;
    ["1", "2", "3"].forEach(a => { E[`ag${i}${a}`].style.opacity = o; });
    if (n.clauses) {  // the account's clause, or in the disagreement view both sides; it slides in from a few units above
      const lines = split ? nd.sv : [nd.cv[k], []];
      lines.forEach((ls, j) => {
        const el = E[`cl${i}_${j}`], key = ls.join("\n") + "|" + f((1 - cf) * -6);
        if (S.shown[el.id] !== key) {
          S.shown[el.id] = key;
          el.innerHTML = ls.map((x, q) => `<tspan x="${g.sx0}" y="${f(nd.cy[j] + q * g.lh + (1 - cf) * -6)}">${esc(x)}</tspan>`).join("");
        }
        el.setAttribute("class", "cl" + (j ? " t1" : !split && n.clauses[k].startsWith("Account") ? " q" : ""));
        el.style.opacity = (cf * o).toFixed(2);
      });
    }
    if (nd.ex) nd.ex.forEach((_, j) => { E["ex" + j].style.opacity = ((RD.extra.acc === k && !split ? cf : 0) * o).toFixed(2); });
  });
  ["1", "2", "3"].forEach(a => {
    if (g.phone) return;
    const on = !split && a === k;
    E["ah" + a].style.fontWeight = on ? 760 : 540;
    E["ah" + a].style.fill = on ? "var(--blue)" : "";
  });
  T.forEach(t => {
    const v = vOf(t, s), p = landP(t, now), e = ease(p), o = dimT(t);
    let cx, l, h;
    if (t.multi && p >= 1) {  // the contested value travels from 0 on each account change
      const q = still.matches ? 1 : ease(dp);
      cx = t.X(mix(0, t.value, q)); l = t.X(mix(0, t.lo, q)); h = t.X(mix(0, t.hi, q));
    } else {
      const x0 = t.X(nullMid(t)), X = x => mix(x0, t.X(x), e);
      cx = X(t.value); l = X(t.lo); h = X(t.hi);
    }
    const pt = E["pt" + t.i], ci = E["ci" + t.i], ha = E["ha" + t.i];
    const arrived = p >= 1 && (!t.multi || dp >= 1);
    pt.setAttribute("class", "pt " + (arrived ? v : "n")); ci.setAttribute("class", "ci " + (arrived ? v : "n"));
    pt.setAttribute("cx", f(cx)); pt.setAttribute("cy", f(t.ay + .5)); pt.setAttribute("r", p > 0 ? 4.4 : 0);
    ci.setAttribute("d", p > 0 ? `M${f(l)} ${f(t.ay + .5)}H${f(h)}` : "");
    ha.setAttribute("cx", f(cx)); ha.setAttribute("cy", f(t.ay + .5)); ha.setAttribute("r", 7.4);
    ha.style.opacity = arrived && v === "h" ? (.32 * o * getBloom()).toFixed(2) : 0;
    pt.style.opacity = ci.style.opacity = o;
    const own = split ? t.multi : t.owner === k || !!t.verdicts[k];
    E["gl" + t.i].setAttribute("class", "gl" + (own ? " own" : ""));
    ["gl", "gv", "ax", "nl", "adv"].forEach(id => { E[id + t.i].style.opacity = o; });
    txt("gv" + t.i, arrived ? `${fv(t.value, t.unit)} · ${VFULL[v]}` : "");
    E["gv" + t.i].setAttribute("class", "gv " + v);
    if (t.multi) {  // the band of the account read is lit; else the owner's; with neither, none
      const lit = split && t.ranges[RD.split_acc] ? RD.split_acc : !split && t.ranges[k] ? k : t.owner;
      [["A", t.acc[0]], ["B", t.acc[1]]].forEach(([c, a]) => {
        E["rg" + c + t.i].setAttribute("class", a === lit ? "rg" : "rg2"); E["rg" + c + t.i].style.opacity = o;
        txt("bl" + c + t.i, a);
        E["bl" + c + t.i].setAttribute("class", "bl" + (a === lit ? " own" : "")); E["bl" + c + t.i].style.opacity = o;
      });
    } else E["rg" + t.i].style.opacity = o;
  });
  const bt = (now - S.d1t - 900) / 900;  // a burst where the round's main contested value lands
  if (!still.matches && FOCUS && bt >= 0 && bt <= 1 && S.d1t > 0) {
    E.bu.setAttribute("cx", f(FOCUS.X(FOCUS.value))); E.bu.setAttribute("cy", f(FOCUS.ay + .5));
    E.bu.setAttribute("r", f(5 + 16 * ease(bt))); E.bu.style.opacity = (1 - bt).toFixed(2); E.bu.setAttribute("stroke-width", f(1.6 * (1 - bt) + .3));
  } else if (!S.rp) E.bu.setAttribute("r", 0);
  const box = sel ? S.L.rows[sel.key].box : seln ? S.L.nodes[seln.i].box : null;
  if (box) { E.sel.setAttribute("x", f(box[0])); E.sel.setAttribute("y", f(box[1])); E.sel.setAttribute("width", f(box[2] - box[0])); E.sel.setAttribute("height", f(box[3] - box[1])); E.sel.setAttribute("rx", 6); }
  else { E.sel.setAttribute("width", 0); E.sel.setAttribute("height", 0); }
  S.dirty = moving(now);
  replay(now);
}
const nullMid = t => (t.ranges.null[0] + t.ranges.null[1]) / 2;
/* The entrance: each claim's value travels from the middle of the null's range to its measured value, 90 ms apart. */
const landP = (t, now) => S.entered ? 1 : clamp((now - S.enterT - 500 - 90 * t.i) / 800, 0, 1);
const moving = now => (!S.entered && now - S.enterT < 500 + 90 * T.length + 900) || now - S.d1t < 1900 || now - S.bigT < 1700 + 90 * T.length;
function getBloom() { return parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--bloom")) || 1; }
function entrance(delay) {
  S.entered = false; S.enterT = performance.now() + delay; S.dirty = true;
  clearTimeout(S.enterTimer);
  S.enterTimer = setTimeout(() => { S.entered = true; S.dirty = true; }, delay + 500 + 90 * T.length + 1000);
}

/* The replay: about every 2.6 s the next test, in the order its row was added to the record, lights its value, and the
   line at the top right names it. Stops while something is open. */
function replay(now) {
  const E = S.el;
  if (still.matches || S.open || moving(now) || now - S.enterT < 3000) { if (S.shown.rp !== "") { E.rp.textContent = S.shown.rp = ""; } return; }
  const list = T.slice().sort((a, b) => a.added.localeCompare(b.added) || a.i - b.i);
  if (!S.rp && now > S.rpNext) S.rp = { t: list[S.rpAt++ % list.length], t0: now };
  if (!S.rp) return;
  const t = S.rp.t, p = clamp((now - S.rp.t0) / 1300, 0, 1), x = t.X(t.value);
  E.bu.setAttribute("cx", f(x)); E.bu.setAttribute("cy", f(t.ay + .5));
  E.bu.setAttribute("r", f(5 + 13 * ease(p))); E.bu.style.opacity = (1 - p).toFixed(2); E.bu.setAttribute("stroke-width", f(1.5 * (1 - p) + .3));
  const a = `${t.added.slice(11, 16)} UTC · `, line = a + `${t.label} · ${VFULL[vOf(t, S.s)]}`;
  if (S.shown.rp !== line) {  // on a phone in two lines
    S.shown.rp = line;
    if (S.g.phone) E.rp.innerHTML = `<tspan x="24">${esc(a + VFULL[vOf(t, S.s)])}</tspan><tspan x="24" dy="${S.g.fk + 6}">${esc(t.label)}</tspan>`;
    else E.rp.textContent = line;
  }
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
/* A change of account: the shared sentences stay; the differing clauses and the contested values replay. */
function setState(s, opts = {}) {
  const now = performance.now(), changed = s !== S.s;
  S.s = s;
  if (changed && !opts.instant) S.d1t = now; else if (opts.instant) S.d1t = -1e9;
  S.dirty = true;
  stopReplay();
  stateText();
  marks();
  if (still.matches) { aim(0, 0); place(now); }
}
/* A change of round: the plate is drawn again for the other round's accounts; the values travel in and the large number
   counts from the old round's number to the new one. */
function setRound(r, opts = {}) {
  const from = S.bigNow;
  S.round = r;
  useRound(r);
  build();
  S.shown = {};
  stateText();
  marks();
  if (opts.instant || still.matches) { S.entered = true; S.enterT = -1e9; S.bigFrom = null; }
  else { entrance(150); S.bigFrom = from == null ? null : from; S.bigT = performance.now(); }
  if (still.matches) { aim(0, 0); place(performance.now()); }
}
function marks() {  // the pressed buttons and the picture's label
  $("switch").querySelectorAll("button").forEach((b, j) => b.setAttribute("aria-pressed", j === S.s));
  $("split").setAttribute("aria-pressed", S.s === 3);
  $("rounds").querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.round === S.round));
  $("svg").setAttribute("aria-label", `Round ${S.round}, ${SNAME[S.s]}: account ${RD.base} in six plain sentences, each with the new claims ` +
    `that test it. ${RD.target} of ${RD.tested} new claims held. Arrow keys change the account; Enter opens a claim.`);
}

/* The side column: the five panels and the examples, one sentence, or one claim. */
function gaugeSvg(t) {
  const s = S.s, v = vOf(t, s), k = ACC(s), W = 340, x0 = 14, x1 = 326;
  const xs = [t.value, t.lo, t.hi, ...Object.values(t.ranges).flat(), ...(t.null_value != null ? [t.null_value] : []), ...(t.adversary != null ? [t.adversary] : [])];
  let a = Math.min(...xs), b = Math.max(...xs);
  if (t.dom) { a = t.dom[0]; b = t.dom[1]; }
  const pad = (b - a) * .05; a -= pad; b += pad;
  const X = x => x0 + (x1 - x0) * (clamp(x, a, b) - a) / (b - a);
  const lab = (x, y, s) => `<text class="g-t" x="${f(clamp(x, 40, 300))}" y="${y}" font-size="11.5" text-anchor="middle">${s}</text>`;
  const band = (rg, cls, name, y) => {
    const p = X(rg[0]), q = X(rg[1]), open = t.dom && rg[1] > t.dom[1];
    return `<rect class="${cls}" x="${f(p)}" y="28" width="${f(Math.max(1, q - p))}" height="14"/>` +
      lab((p + q) / 2, y, name + " " + fv(rg[0]) + " to " + fv(rg[1]) + (open ? " ›" : ""));
  };
  const lit = s === 3 && t.ranges[RD.split_acc] ? RD.split_acc : s !== 3 && t.ranges[k] ? k : t.owner;
  let h = `<svg class="gauge" viewBox="0 0 ${W} 108" aria-hidden="true">`;
  h += band(t.ranges.null, "nl", "null", 18);
  t.acc.forEach((a, j) => { h += band(t.ranges[a], t.multi && a !== lit ? "rg2" : "rg", "account " + a, j ? 18 : 62); });
  h += `<path class="ax" d="M${x0} 42.5H${x1}"/>`;
  if (t.null_value != null) h += `<path d="M${f(X(t.null_value))} 24V46" stroke="var(--faint)" stroke-width="1.4"/>` + lab(X(t.null_value), 78, "null measured " + fv(t.null_value, t.unit));
  if (t.adversary != null) h += `<path class="adv" d="M${f(X(t.adversary))} 22V48"/>` + lab(X(t.adversary), 98, "adversary " + fv(t.adversary, t.unit));
  h += `<path class="ci ${v}" d="M${f(X(t.lo))} 35H${f(X(t.hi))}"/><circle class="pt ${v}" cx="${f(X(t.value))}" cy="35" r="5.5"/>`;
  return h + `</svg>`;
}
function testPane(t) {
  const s = S.s, v = vOf(t, s), node = NODES[t.node];
  const who = !t.owner ? "The judge's one disagreement, between accounts 1 and 2" :
    `Account ${t.owner} · new claim ${t.key.slice(2)}` + (t.multi ? ` · denied by account ${t.acc.find(a => a !== t.owner)}` : "");
  const verdict = t.multi ? t.acc.map(a => `account ${a} ${t.verdicts[a]}`).join(", ") : VFULL[v];
  const rg = x => `${fv(x[0])} to ${fv(x[1])}`;
  let h = `<div class="dhead"><h2>${esc(t.label)}</h2><button class="close" data-open="">Close</button></div>`;
  h += `<p class="tag">Round ${RD.r} · ${who} · <b>${esc(CAP(verdict))}</b></p>`;
  if (t.about) {
    h += `<h3>What the accounts disagree on, in the judge's words</h3><p class="quote">${esc(minus(t.about))}</p>`;
    h += ["2", "1"].map(k => `<p class="why"><b>Account ${k}:</b> ${esc(minus(t.positions["account-" + k]))}</p>`).join("");
  }
  h += `<h3>The claim, in the plan's words</h3><p class="quote">${esc(minus(t.claim))}</p>`;
  t.denials.forEach(d => { h += `<h3>Account ${d.by} denies it</h3><p class="why">${esc(minus(d.why))}</p><p class="why"><b>Instead:</b> ${esc(minus(d.instead))}</p>`; });
  h += gaugeSvg(t);
  const ranges = t.acc.map(a => `account ${a} ${rg(t.ranges[a])}`).join(", ");
  h += `<p class="why">Measured: <b>${fv(t.value, t.unit)}</b> (90 % interval ${fv(t.lo)} to ${fv(t.hi)}), n ${t.n} ${esc(t.nunit)}. ` +
    `Ranges fixed before the test: ${ranges}; the null ${rg(t.ranges.null)}` + (t.null_value != null ? `; the null measured on the same rows ${fv(t.null_value, t.unit)}` : "") +
    (t.adversary != null ? `; the adversary's value ${fv(t.adversary, t.unit)}, ${t.adversary >= t.lo && t.adversary <= t.hi ? "inside" : "outside"} the interval` : "") + ".</p>";
  if (t.alternative) h += `<h3>The adversary's alternative, in its words</h3><p class="why">${esc(minus(t.alternative))}</p>`;
  h += `<h3>The statistic</h3><p class="why">${esc(minus(t.statistic))}</p>`;
  h += `<h3>The null, in the plan's words</h3><p class="why">${esc(minus(t.null))}</p>`;
  if (t.caveat) h += `<p class="case">${esc(t.caveat)}</p>`;
  Object.values(t.retest || {}).forEach(x => {
    h += `<p class="case"><b>Retest under engine 16</b> (<a href="/#${esc(x.result)}">${esc(x.result)}</a>): ${esc(x.verdict)}; ` +
      `the adversary's value, ${fv(x.adversary, t.unit)}, lies inside the interval. ${esc(minus(x.measured))}</p>`;
  });
  h += `<h3>Measured, as the record holds it</h3>` + Object.entries(t.measured).filter((e, j, all) => j === 0 || e[1] !== all[0][1])
    .map(([k, m]) => `<p class="why">${Object.keys(t.measured).length > 1 && t.measured[t.acc[0]] !== t.measured[t.acc[1]] ? `<b>Account ${k}:</b> ` : ""}${esc(minus(m))}</p>`).join("");
  h += `<ul class="facts"><li>Tests sentence <button class="lnk" data-open="${node.key}">${node.i + 1}</button> of account ${RD.base}</li>` +
    (t.why_new ? `<li>Why it is new: ${esc(minus(t.why_new))}</li>` : "") +
    `<li>Test ${esc(t.folder)}: studies/theory/results/direct/${esc(t.folder)}/metrics.json</li>` +
    `<li>Board item <a href="/#${esc(t.result)}">${esc(t.result)}</a>; row added ${esc(t.added.slice(11, 16))} UTC</li></ul>`;
  return h + steps();
}
function nodePane(n) {
  const A = RD.accounts, s = S.s, b = RD.base;
  let h = `<div class="dhead"><h2>Round ${RD.r} · sentence ${n.i + 1} of ${NODES.length}</h2><button class="close" data-open="">Close</button></div>`;
  h += `<p class="lead">${esc(n.text)}${n.clauses ? " " + esc(n.clauses[b]) : ""}</p>`;
  h += `<h3>Account ${b}, sentence ${n.i + 1}, verbatim</h3><p class="quote">${esc(minus(A[b].sentences[n.i]))}</p>`;
  const stand = { same: "states the same", other: "states otherwise", none: "takes no side on the last part" };
  Object.entries(n.sent).forEach(([k, idx]) => {
    h += `<h3>Account ${k}, sentence${idx.length > 1 ? "s" : ""} ${idx.join(" and ")} (${stand[n.st[k]]})</h3>` +
      idx.map(j => `<p class="quote small">${esc(minus(A[k].sentences[j - 1]))}</p>`).join("");
  });
  if (RD.extra && RD.extra.node === n.i) h += `<p class="case">Account ${RD.extra.acc} marks one of the ${RD.facts} facts as against it: ${esc(A[RD.extra.acc].contradicts.map(c => c[0] + ". " + c[1]).join(" "))}</p>`;
  h += `<ul class="facts">` + (n.tests.length ? n.tests.map(t => `<li><button class="lnk" data-open="${t.key}">${esc(t.label)}</button>: ${esc(t.multi ? t.acc.map(a => `account ${a} ${t.verdicts[a]}`).join(", ") : `account ${t.owner}, ${VFULL[vOf(t, s)]}`)}</li>`).join("")
    : `<li>No new claim of round ${RD.r} tests this sentence.</li>`) + `</ul>`;
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
      `<ul class="more ex">${C.examples.map(x => `<li><button data-go="${x[0]}">${esc(x[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
  S.dirty = true;
}
/* The round, the account and what is open are one value in the address: #<15>/<a1|a2|a3|split>/<panel, sentence or
   claim>, each part left out when it is the first view's. */
function address(push) {
  const parts = [S.round !== NEWEST ? S.round : "", S.s !== BEST(S.round) ? STATES[S.s] : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const r = parts.find(x => ROUNDS.includes(x)) || NEWEST;
  const k = STATES.indexOf(parts.find(x => STATES.includes(x))), s = k >= 0 ? k : BEST(r);
  if (first === true) {
    useRound(r); build(); S.round = r; S.s = s;
    setState(s, { instant: true });
    const travel = !still.matches && !location.hash;
    if (travel) watchEntrance(); else { S.entered = true; S.enterT = -1e9; }
  } else {
    if (r !== S.round) { S.s = s; setRound(r); }
    else if (s !== S.s) setState(s);
  }
  S.open = parts.find(x => C.panels.some(p => p[0] === x) || TK[x] || NK[x]) || null;
  pane();
  place(performance.now());
}
function watchEntrance() {
  S.enterT = 1e12;
  const go = () => { if (S.started) return; S.started = true; entrance(400); };
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
function chooseRound(r) {  // what is open closes with the round: its claims are not the other round's
  if (r === S.round) return;
  S.open = null;
  setRound(r);
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
  const rb = e.target.closest("[data-round]"), go = e.target.closest("[data-go]");
  if (b) choose(Number(b.dataset.state) === S.s && b.id === "split" ? BEST(S.round) : Number(b.dataset.state));
  if (rb) chooseRound(rb.dataset.round);
  if (go) { location.hash = go.dataset.go; show(); }
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
    location.hash = C.examples[0][0];
    show();
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); stateText(); place(performance.now()); });
still.addEventListener("change", () => { if (still.matches) { stopReplay(); S.entered = true; S.d1t = -1e9; S.bigFrom = null; aim(0, 0); S.dirty = true; place(performance.now()); } });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1; V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("switch").innerHTML = SNAME.slice(0, 3).map((n, k) => `<button data-state="${k}">${n}</button>`).join("");
$("rounds").innerHTML = ROUNDS.map(r => `<button data-round="${r}">Round ${r}</button>`).join("");
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(\d+ of \d+)/g, "<b>$1</b>");
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
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "examples": EXAMPLES,
    "rounds": {"15": _round15(), "16": _round16()} if RECORD and RECORD16 else {}, "newest": "16",
}, ensure_ascii=False).replace("</", "<\\/"))

if __name__ == "__main__":  # run from the repository root
    args = sys.argv[1:]
    ref = args[args.index("--ref") + 1] if "--ref" in args else ""
    if "--write" in args:
        rec, commit = _build(ref)
        rec16 = _build16(ref)
        commit = _git("log", "-1", "--format=%h", *([ref] if ref else []), "--", W, W16, *FILES, R + "direct/").strip()
        src = open(__file__).read()
        start = src.index("\nRECORD = ") + 1
        end = src.index("\nREF = ", start) + 1
        src = src[:start] + "RECORD = " + pprint.pformat(rec, width=118, sort_dicts=False) + "\n" + src[end:]
        start = src.index("\nRECORD16 = ") + 1
        end = src.index("\n\n", start) + 1
        src = src[:start] + "RECORD16 = " + pprint.pformat(rec16, width=118, sort_dicts=False) + "\n" + src[end:]
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
    commit = _git("log", "-1", "--format=%h", *([ref] if ref else []), "--", W, W16, *FILES, R + "direct/").strip()
    assert rec == RECORD, "RECORD differs from the files: run with --write" + (f" --ref {ref}" if ref else "")
    assert _build16(ref) == RECORD16, "RECORD16 differs from the files: run with --write" + (f" --ref {ref}" if ref else "")
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
    # round 16's counts agree with its table too (12 columns, the blind marker's marks)
    t16 = {m.group(1): [int(x) for x in m.groups()[1:]] for m in re.finditer(
        r"^\| account-(\d) \|" + r" (-?\d+) \|" * 12 + "$", _text(ref, W16 + "synthesis.md"), re.M)}
    assert sorted(t16) == ["1", "2", "3"], "round 16's synthesis.md has no table of the three accounts"
    for k, x in _d["accounts"].items():
        mine = [x["explained"], x["unaddressed"], x["contradicts"], x["own_contradicts"], x["held"], x["not_separated"],
                x["refuted"], x["undecided"], 0, x["denials_held"], x["denials_refuted"], x["score"]]
        assert mine == t16[k], f"round 16 account {k}: page {mine}, synthesis.md {t16[k]}"
    assert COUNTS["best"] == "2" and NODES and len(NODES) == len(RECORD["accounts"]["2"]["sentences"]), "the page draws account 2"
    print(f"RECORD matches the files ({ref or 'working tree'}, commit {commit}). {COUNTS['held']} of {COUNTS['tested']} "
          f"new consequences hold, {COUNTS['refuted']} refuted, {COUNTS['undecided']} undecided. Round 16: {_d['held']} of "
          f"{_d['tested']} hold, {_d['not_separated']} not separated, {_d['refuted']} refuted, {_d['undecided']} undecided; "
          f"denials {_d['denials_decided']} of {_d['denials']} decided, {_d['denials_against_denier']} against the denier; "
          f"adversary inside the interval in {_d['adversary_inside']} of 9; undecided at a range edge {_d['edge']}. "
          "Both synthesis.md tables agree.")
