# Cold read of the site's first-screen text

Reader: a software engineer who uses LLMs at work, has never trained one, reads English as a second language, two minutes.
Read once, in order: home.txt, first_lines.txt (31 results), board_plain_rows.txt (first 25 entries).
Note: my read of the board file showed me about 45 entries before I stopped; I base everything below on the first 25 only. Counts in C come from a word count over home.txt, first_lines.txt and the first 25 board entries.

## A. What I think this is

1. A small team at a hackathon uses coding agents to run experiments on an open language model (Olmo 3), and this site shows what they found, live.
   Confidence: high. Words: "Invariant is a small team of people and their coding agents at the SF AI Research Hackathon. This site shows their findings, their papers and the board they work from, live."
2. Their main question is how close the untrained ("base") model can get on a math benchmark (MATH-500) to the same model after RL training, without any training at all.
   Confidence: medium-high. Words: "We measure how far the Olmo 3 base model gets on MATH-500 with no training, against the RL-trained model." I am guessing "RL" means reinforcement learning; the site never says.
3. Main result, as I read it: putting three fixed tokens at the start of the model's answer (they call this a "cue") lifts the base model from about 45 % to 82 % on MATH-500, and a majority vote over 6 answers reaches the RL model's score, but at about 5 times the tokens.
   Confidence: medium. Words: "Three opening tokens raise the base model from 44.8 % to 82.0 % on MATH-500"; "A vote over 6 samples of Base + cue ... within RL's one-sample range, at 5.2 times the tokens". I do not know what the three tokens are; I guess they include the word "Okay" ("openings starting with Okay"). I do not know the RL model's exact score from the first screen; the home sentence has it only as a template ("points below the RL-trained model's ... %").
4. They also look inside the weights: the difference between the RL model and the base seems to sit partly in a few "directions" that make answers finish instead of running too long, and one hand-written change to one weight matrix gives a big jump.
   Confidence: low. Words: "Eight RL directions per matrix", "The finish dial", "One hand-written edit to one matrix lifts the base model from 45% to 79%". I am guessing what a "direction" is.
5. Why it would matter: if most of what expensive RL training gives can be had with a short prompt prefix or with voting, then RL mostly teaches the model how to start and finish an answer, not new math, and a cheaper route may exist.
   Confidence: low-medium. This is my own inference from "81 % of the RL gain is on problems the base model already solves sometimes" and "Does solving math need RL training?". The site does not say why it matters in words I found.

## B. The 31 results

Format: (i) what I think it found | (ii) understood / partly / not understood | (iii) words that stopped me.

1. A quarter of RL: adding only 1/4 of the weight difference (RL minus base) to the base gives 66 % of RL's improvement. | partly | "RL weight change", "Scaled to a quarter" (scaled how? a quarter of what?)
2. The base opens itself: if the base model generates several starts and you keep one that begins with "Okay", it scores as well as with the cue (411 vs 410 of 500). | partly | "RL's opening", "nothing prefilled", "Base + cue", "openings"
3. The cue beyond math: the same three tokens also help on code and general questions (+37.2, +19.3, +30.0 points). | understood | "three-token cue" (which tokens?), "found on math"
4. Cut off is unfinished: answers cut at 16,384 tokens, when allowed 32,768, finish; for "Think-SFT" 23 of 93 become right, for the cued base only 4 of 64. | partly | "Think-SFT", "unfinished or stuck", "Base + cue's finish"
5. Eight directions: some small part of RL's weight change matches the cue and does a bit better on harder problems. | not understood | "Eight RL directions per matrix", "match the cue", "328 harder problems" (which set?)
6. More samples against RL: even with 4.2x the tokens, combining several base answers stays 1.2 points below one RL answer. | understood | "the best base rule" (rule for what?), "equal token frontier" (file name)
7. Forecasts before results: some "theories" predicted experiment numbers better than "no-theory readers" 65 times out of 162, vs 54 by chance. | not understood | "a theory", "no-theory readers", "39 of the 65 are on one code experiment the readers forecast too low"
8. Hand-written edit: one manual change to one weight matrix lifts the base from 45 % to 79 % on MATH-500. | understood (the claim, not the method) | "hand-written edit" (what was written?)
9. Gap closed without reward: "Think-SFT" gets more than all of the gain from cued base to RL (122 %). | partly | "Think-SFT", "without reward", "122 % of the gap" (more than 100 % of a gap confused me)
10. Imitation beats RL: fine-tuning on worked solutions beats RL on harder problems, also on 2026 problems. | understood | "2.7 points per sample", "6.1 when four samples vote"
11. Loop neurons: turning off 1,000 neurons cuts cases where the model repeats itself from 71 to 19. | understood | none
12. Neurons you can describe: from a one-sentence description, a reader can find where a neuron activates 90.7 % of the time. | partly | "blind reader", "finds a neuron's firings"
13. No early warning: nothing in the early text of an answer predicts that it will fail. | partly | "AUROC 0.568", "text sign", "failing sample"
14. One difficulty order: different improvement methods solve the same problems, as if problems have one ranking from easy to hard. | not understood | "one difficulty order predicts", "−0.05 problems over 618 pairs"
15. The opening cue: three tokens at the start of the answer lift the base from 44.8 % to 82.0 % on MATH-500. | understood | "opening tokens" (which ones?)
16. Restarting stuck answers: starting over an answer that hit the length limit adds 12 points at one setting and 1.6 at another. | partly | "T 0.6", "T 1.0" (I guess temperature), "cut-off answers"
17. RL avoids the slip: at the point where the cued base makes its first error, the RL model is half as likely to make the same error. | partly | "Given Base + cue's wrong answer", "first wrong step", "0.49 times as likely"
18. RL change on imitation: adding twice the RL weight difference to "Think-SFT" raises its score from 209 to 231.5 of 328, above RL's 200. | partly | "Twice RL's weight change", "Think-SFT", "231.5" (half a problem?), "of 328"
19. RL directions move activations: RL's weight directions change the model's internal values 95x more than random ones of the same size. | not understood | "equal weight norm", "RL's 8 directions", "shift the activations"
20. RL's edge comes early: if the base continues an answer that RL started, it gets most of the way to RL, so RL's advantage is in the first part. | partly | "Finishing RL's half-written answers", "closes 65 to 81 % of its gap"
21. RL's change is spread out: copying the 1 % most important neurons from RL to base gives only 16 % of RL's effect. | understood | "RL's effect" (measured how?)
22. The first 100 RL steps land near the cue: after a short RL training, the model already scores like base + cue; most of the gain comes later. | partly | "417.5 of 500", "RL steps", "land near the cue" (title)
23. Where RL's gain comes from: most of RL's gain is on problems the base can already solve sometimes. | understood | none
24. More Wait, same score: making the base write "Wait" as often as RL does not raise its score. | partly | "Pushed to RL's rate of Wait" (why "Wait"? how pushed?)
25. The finish dial: making some RL directions bigger makes answers finish, with good scores on math and code. | not understood | "Enlarging 8 RL directions", "at size 1.5", "dial"
26. Theories on trial: "our theories" were no better than "readers with no theory" at predicting numbers. | not understood | "Our theories", "readers with no theory", "predictions"; also seems to disagree with result 7 and I could not tell why
27. Two jobs in one edit: early layers of the RL weight change add right answers; late layers only stop answers from being cut off. | partly | "RL's weight edit", "early layers ... add 7.6 points right", "reduce cut-offs"
28. Vote over 6 samples: a majority vote over 6 answers of base + cue matches one RL answer, at 5.2x the tokens. | understood | "456.6 of 500" (fraction), "one-sample range"; file name says "four"
29. Where the gap goes: two thirds of the gap is on problems the base sometimes solves; with a random weight change, 71 %. | not understood | "with a random weight change, 71 % of its gap" (gap between what and what?)
30. Idea basins: the team's 515 board posts group into 12 topic clusters. | partly | "idea basins", "board items"
31. Review cuts waste: after the agents reviewed their own process three times, compute per batch fell from 16.3 to 4.4 minutes. | partly | "the review skill", "compute per batch"

Counts: understood 9, partly 15, not understood 7.

## C. Words and phrases I had to guess

Counts are approximate occurrences across the three files (first 25 board entries).

| Word or phrase | My guess | Times met |
|---|---|---|
| RL | reinforcement learning; the "RL-trained model" is the same model after RL training | ~117 |
| base / Base | the model before any training for math | ~64 |
| cue | a fixed short text (three tokens, maybe "Okay" with a newline) put at the start of the model's answer | ~46 |
| sample(s) | one generated answer per problem | ~37 |
| direction(s) | a pattern inside a weight matrix, maybe from a matrix decomposition | ~23 |
| finish / cut-off / cap / cap hits | the answer stops because it reached the maximum token length, not because it is done | ~20-23 each |
| 328 / hard328 / "328 harder problems" | a second, harder test set of 328 math problems | ~24 |
| Think-SFT | another model, fine-tuned on written-out reasoning ("SFT" = supervised fine-tuning?) | ~20 |
| vote / "vote over 4" | majority vote over several answers to the same problem | ~19 |
| interval, numbers in [ , ] | confidence interval | ~19 |
| edit | a change made directly to the weights | ~18 |
| T 0.6 / T 1.0 | sampling temperature | ~18 |
| points | percentage points | ~15 |
| neuron / firings | one unit inside the model and when it activates | ~12 |
| weight change | RL model's weights minus base model's weights | ~11 |
| dial | (a) the round menu on the home page; (b) a weight change you can make bigger or smaller ("finish dial") | ~11 |
| gap / "closes X % of the gap" | the score difference between base (+cue) and RL | ~9 |
| opening / openings | the first tokens of an answer | ~9 |
| theory / theories | some written explanation that predicts numbers; not clear who writes it | ~9 |
| seed | random seed for sampling | ~9 |
| Base + cue | the base model with the cue added | ~9 |
| filed / predictions / pre-registered | predictions written down before the run | ~8 |
| board | the team's shared to-do and results list | ~7 |
| AI Psychosis maxxing / Psychosis | an internal joke, slang | ~7 |
| loop(s) | the model repeating the same text | ~7 |
| reward / "without reward" | training without a correct/incorrect signal | ~6 |
| matrix | one weight matrix in the model | ~5 |
| layers / early / late layers | model layers near the input / output | ~5 |
| Wait | the word "Wait" the model writes when it reconsiders | ~5 |
| activations | internal values while the model runs | ~4 |
| no-theory readers / readers | people or agents predicting without a theory | ~4 |
| v2 / v3 | version of the grader | ~4 |
| prefilled | text placed into the answer before the model writes | ~3 |
| idea basins | clusters of similar ideas | ~3 |
| norm / "equal weight norm" | size of a weight change | ~3 |
| rank / "rank-8" | number of directions kept | ~3 |
| RL-Math, RL-Zero-Math, RL-Code, Code-RL | different RL-trained versions of the model; not sure they are different from "RL" | ~3 |
| M(2) | Think-SFT plus 2x the RL change? pure guess | ~2 |
| SPEC_transplant, amendment 3 | an internal plan document | ~2 |
| entropy, forks, nats | how unsure the model is at each token | ~2 |
| min-p / top-p | sampling settings | ~2 |
| AUROC | a score for how well something predicts yes/no; 0.5 is chance | ~1 |
| review skill | an agent instruction file for reviewing work | ~1 |
| 417.5, 456.6, 231.5 "of 500/328" | averages over several runs (only guessed) | several |

## D. Best and least understood

Best understood: 11 Loop neurons, 23 Where RL's gain comes from, 15 The opening cue, 8 Hand-written edit, 21 RL's change is spread out.

Least understood: 19 RL directions move activations, 25 The finish dial, 29 Where the gap goes, 14 One difficulty order, 26 Theories on trial (with 7 Forecasts before results close behind).

What the best ones do that the worst ones do not: the best ones state one plain action and one before/after number ("switching off 1,000 neurons ... from 71 to 19", "from 44.8 % to 82.0 %"), use words I already know (neurons, repetition, problems, solves), and the question and the line talk about the same thing. The worst ones use team words with no explanation ("directions", "dial", "size 1.5", "equal weight norm", "theories", "no-theory readers"), compare against something not named ("its gap", "one difficulty order predicts"), or give a number with no "from ... to ..." so I cannot tell if it is good.

## E. Would I come back or pass it on

I would pass on one or two results to a colleague (the three-token cue going from 45 % to 82 %, and "a vote over 6 answers matches RL at 5x tokens"), because those are concrete and I can repeat them. I would probably not come back to the site itself in two minutes of reading. What decided it on the first screen: the one clear sentence ("We measure how far the Olmo 3 base model gets on MATH-500 with no training, against the RL-trained model") made me interested, but the main number in the home sentence was not visible to me in the extracted text, the round "dial with beads" menu and "AI Psychosis maxxing" did not tell me where to start, and "cue" is used everywhere without being defined, so most result lines needed guessing.
