# Cold read v2: tile texts

Reader role: software engineer, uses LLMs at work, never trained one, English as second language, two minutes.
Read once, in order, after the intro paragraph. No other context.

Counts: understood 17, partly 13, not understood 1.

## A. Per result

1. finding_a_quarter_of_rl.py: a smaller version of RL's weight change keeps about two-thirds of RL's math gain. PARTLY. Stopped by: "Scaled to a quarter (0.42 of its size after rounding)" (a quarter is 0.25, so 0.42 looks like a contradiction; I could not tell which number is the real scale).
2. finding_base_opens_itself.py: the base model, without the cue, sometimes starts its answer with "Okay" by itself, and then scores as well as with the cue (411 vs 410 of 500). PARTLY. Stopped by: "continue the first of its own openings that has a line starting 'Okay'" (how many openings were drawn? who picks?); "openings".
3. finding_cue_on_code.py: the three cue tokens, found on math, also help on code and general questions. PARTLY. Stopped by: "there, an estimate that corrects for answers with no letter gives about 9.6" (where is "there"? what letter? is the real general-questions gain 30.0 or 9.6?).
4. finding_cut_off_is_unfinished.py: when Think-SFT hits the length limit, it is not looping; with double the length it finishes, and 23 of 93 such answers are right, vs 4 of 64 for base + cue. UNDERSTOOD. Small pause: "cut off" (I guessed: stopped at the token limit).
5. finding_eight_directions.py: adding only 8 directions of RL's weight change per matrix brings the base model to cue level (85.4 % vs 82.0 %), and it helps on top of the cue on hard problems. PARTLY. Stopped by: "with the cue added to both" (both of what?); "the 328 harder problems" (which set? first time I see it).
6. finding_equal_token_frontier.py: many samples of base + cue, with the best answer-picking rule, cost 4.2x the tokens of one RL sample and still score 1.2 points lower (not clearly different). UNDERSTOOD. Small pause: "best rule for drawing several samples".
7. finding_forecasts_before_results.py: theories written by AI did not predict the team's next numbers better than AI without a theory. PARTLY. Stopped by: "outside one code experiment"; "nearer in 26 of 82 forecasts (chance: 27)" (nearer than what? why is chance 27, not 41?); "log score"; "AI readers".
8. finding_hand_written_edit.py: one edit, written by hand into one weight matrix, raises the base model from 45 % to 79 % on MATH-500, near the cue's 82 %. UNDERSTOOD (the number). I do not know what a "hand-written edit" to weights is made of.
9. finding_how_much_of_the_gap.py: Think-SFT, trained with no reward, does better than RL on 328 hard problems (122 % of the base+cue-to-RL gap). PARTLY. Stopped by: "122 % of the gap from the base model with the opening cue to the RL model"; "At the token cost of one RL sample it closes 79 %" (one sample is one sample; why does its cost differ?).
10. finding_imitation_beats_rl.py: Think-SFT with the cue beats RL by 2.7 points (one sample) and 6.1 points (vote of 4) on 328 hard problems, also on 136 problems from 2026. UNDERSTOOD. Small pause: "published in 2026" (I guessed: problems newer than the training data).
11. finding_loop_neurons.py: turning off 1,000 neurons cuts answers stuck repeating from 71 to 19 of 500, with the same accuracy (381 vs 378). UNDERSTOOD.
12. finding_neurons_you_can_describe.py: a one-sentence description lets another model predict when a neuron is active, 90.7 % right for important neurons vs 71.3 % for random ones. PARTLY. Stopped by: "sorts 90.7 % of new text snippets right"; "the neurons that matter most to what reinforcement learning (RL) changed" (matter how? measured how?). Sentence too long to hold.
13. finding_no_early_warning.py: looking at partial Think-SFT answers (token 4,000 to 12,000), six signals cannot tell which answers will fail; best AUROC 0.568, near chance. UNDERSTOOD. Small pause: "six signs" (which signs?).
14. finding_one_difficulty_axis.py: different improvement methods mostly solve the same problems; problems have one difficulty order. PARTLY (direction only from the question). Stopped by: "Two methods together solve no more ... than predicted if both followed one shared order of difficulty"; "618 pairs of methods" (what methods? there are hundreds?); "measured count minus the predicted count is −0.05".
15. finding_opening_cue.py: three tokens at the start of the answer raise the base model from 44.8 % to 82.0 % on MATH-500, without training. UNDERSTOOD. Stopped briefly by: "without them, the base model scores 63.8 % at temperature 0.6" (why switch temperature for the comparison?).
16. finding_restart_on_cap.py: for base + cue, re-sampling answers that hit the length limit adds 12 points at temperature 0.6 and 1.6 at 1.0. UNDERSTOOD.
17. finding_rl_avoids_the_slip.py: RL may be about half as likely to write the base model's first wrong step, but the interval includes 1, so maybe chance. PARTLY. Stopped by: "0.49 times as likely ... to write the first wrong step" (how is the "first wrong step" found? likely = probability of those tokens?); title "under RL".
18. finding_rl_change_on_imitation.py: adding RL's weight change (times two) onto Think-SFT raises it from 209 to 231.5 of 328, above RL (200). PARTLY. Stopped by: "Twice RL's weight change" (scaled by 2, or applied twice?); "231.5" (half a problem?).
19. finding_rl_directions_move_activations.py: RL's top 8 directions change internal activations 95x more than random directions of the same size. UNDERSTOOD. Small pause: "At equal weight norm"; "activations".
20. finding_rl_edge_comes_early.py: if base + cue continues an RL answer from its middle, it gets most of RL's advantage (65 %), so RL's difference is in the first half. PARTLY. Stopped by: "81 % on a set of 183 chosen with the base model's own answers" (chosen how? why two sets?).
21. finding_rl_every_neuron.py: copying the top 1 % of RL's neurons into the base model recovers only 16.1 % of the difference in predictions; RL's change is spread over many neurons. UNDERSTOOD. Small pause: "ranked most important" (by what?).
22. finding_rl_learns_the_opening_first.py: after only 100 RL steps the model is already near the cue's score (417.5 vs 410.5 of 500); most of RL's extra gain comes later. UNDERSTOOD. Small pauses: "417.5" (half problems); the switch to temperature 0.6 with "27 ahead".
23. finding_rl_reliability.py: most (81 %) of RL's 198 extra right answers are on problems base + cue already solves sometimes; RL mainly makes it more reliable. UNDERSTOOD.
24. finding_rl_wait_habit.py: making the base model say "Wait" as often as RL does not help (413 vs 410.5); RL scores 457. UNDERSTOOD. Small pause: "Steered through its activations"; is the 410.5 base or base + cue?
25. finding_the_finish_dial.py: making 8 RL directions bigger makes answers finish and also adds right answers; at 1.5 it reaches 203 of 328, RL 206. PARTLY. Stopped by: "Enlarging 8 RL directions"; "where Base + cue already finished" (I could not follow what was compared with what); "at size 1.5".
26. finding_theories_on_trial.py: the team's theories were nearer to the real number in 202 of 412 predictions, which is about half: no better than no theory. UNDERSTOOD. (Confusion with result 7: two tiles on the same test with different counts, 26 of 82 and 202 of 412.)
27. finding_two_jobs_in_the_edit.py: RL's weight change in early layers adds right answers (+7.6 points); in late layers it only reduces answers cut off at the limit. UNDERSTOOD. Small pause: "add 7.6 points right".
28. finding_vote_over_four.py: base + cue needs a vote over 6 samples (5.2x the tokens) to equal one RL sample (456.6 vs 456-464 of 500). UNDERSTOOD. Small pause: "the RL model's one-sample range" (range over repeated runs?).
29. finding_where_the_gap_goes.py: something about why base misses problems RL solves, and a random weight change gives a similar split. NOT UNDERSTOOD. Stopped by: "66 % are finished wrong answers that other base samples get right"; "a random weight change gives 71 %" (71 % of what? applied to which model?); "the split".
30. proof_idea_basins.py: the team's ideas group into 12 clusters. PARTLY. Stopped by: "board items"; "idea basins". No sense of whether 12 is many or few.
31. proof_review_cuts_waste.py: following a written review procedure, an agent cut compute in a test study from 16.3 to 4.4 container minutes per batch. UNDERSTOOD. Small pause: "written review procedure"; "container minutes".

## B. Words and phrases I had to guess (count = times met in the 31 tiles, filenames excluded)

| Word or phrase | My guess | Times met |
|---|---|---|
| opening / openings (beyond "opening cue") | the first words of the answer | 18 incl. "opening cue" (guessed only in "its own openings", 1) |
| sample(s), one sample, vote over N samples | one generated answer; majority vote over N answers | 17 (vote: 5) |
| MATH-500 | a math test set of 500 problems | 14 |
| neuron(s) | one hidden unit inside the model's feed-forward layers | 10 |
| cut off / cut-off / token limit | the answer stopped because it reached the maximum length | 9 |
| finish / finished / finishes (an answer) | the answer ends by itself before the limit | 8 |
| theories / theory | explanations written by AI agents that predict numbers | 8 |
| 328 harder problems | a separate set of harder math problems | 5 |
| edit (RL's edit, weight edit) | the same as "weight change" | 5 |
| activations | internal values in the model while it reads text | 4 |
| half counts (231.5, 410.5, 417.5, 456.6) | averages over several runs | 4 |
| readers / AI readers / language-model readers | other LLMs asked to predict without a theory | 3 |
| 95 % interval | confidence interval | 3 |
| loop / repetition loop | the answer repeats the same text again and again | 3 |
| first wrong step | the first line in an answer where the reasoning goes wrong | 3 |
| token cost / times the tokens of one RL sample | total generated tokens, compared to one RL answer | 3 |
| problems published in 2026 / from 2026 | new problems the model could not have seen in training | 2 |
| steered / steering | changing activations to push the model to a behavior | 2 |
| idea basins | clusters of similar ideas | 2 |
| early / late layers | first and last layers of the network | 2 |
| enlarging, at size 1.5 | multiplying the directions by 1.5 | 2 |
| a quarter (0.42) | scale factor; unclear which | 1 |
| answers with no letter | multiple-choice answers missing the A/B/C/D letter | 1 |
| outside one code experiment | one experiment was excluded | 1 |
| chance: 27 | expected count if theory gave no help | 1 |
| log score | a scoring rule for probability forecasts | 1 |
| fires | the neuron is active | 1 |
| sorts ... right | classifies correctly | 1 |
| matter most to what RL changed | neurons ranked by some importance score | 1 |
| ranked most important | same; method unknown | 1 |
| six signs | features read from the text, unknown which | 1 |
| one shared order of difficulty | all methods find the same problems hard | 1 |
| weight norm | size of the weight change | 1 |
| hand-written edit | a weight change made by a person, not training | 1 |
| one-sample range | the spread of RL scores over repeated single-sample runs | 1 |
| the split | the 66 % / rest division of failures | 1 |
| board items | posts on the team's work board | 1 |
| planted inefficiencies / compute waste | waste added on purpose to test the procedure | 1 |
| written review procedure | a checklist the agent follows | 1 |
| container minutes | minutes of cloud compute | 1 |

## C. Headlines too long to take in at a glance

- finding_cue_on_code.py (three numbers, then "there, an estimate that corrects..." in the same sentence)
- finding_eight_directions.py (two claims joined by a semicolon, second one with "both")
- finding_forecasts_before_results.py
- finding_how_much_of_the_gap.py (three sentences with two percentages)
- finding_neurons_you_can_describe.py (three percentages plus a parenthesis)
- finding_no_early_warning.py (longest line; AUROC explanation at the end)
- finding_one_difficulty_axis.py (parenthesis plus two counts)
- finding_rl_edge_comes_early.py
- finding_rl_learns_the_opening_first.py (two temperatures, an interval and a third sentence)
- finding_where_the_gap_goes.py
- finding_equal_token_frontier.py (borderline)
- finding_imitation_beats_rl.py (borderline)
