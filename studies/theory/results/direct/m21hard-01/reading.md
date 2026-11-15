# m21hard-01: 11 Q rows read by eye (every 6th, plus 170), with the cued base's solve count k of 4

| problem | k/4 | tokens | first characters | by eye |
|---|---|---|---|---|
| 0 | 4/4 | 349 | "To convert from rectangular coordinates..." | deliberation, right value with an appended note |
| 41 | 4/4 | 1 | (empty) | easy problem, empty reply |
| 68 | 4/4 | 659 | "Help is available. Problem ..." | web text |
| 78 | 4/4 | 1 | (empty) | empty reply |
| 109 | 2/4 | 439 | " and it should be enclosed in quotation marks..." | prompt continuation |
| 128 | 2/4 | 336 | " Area of circles Video transcript" | web text |
| 157 | 4/4 | 5 | ' or "Solution."' | prompt continuation |
| 170 | 0/4 | 143 | " and don't forget about the appropriate units... Let's solve this step-by-step" | hard problem, short attempt |
| 182 | 4/4 | 165 | ".\nAnswer: To find the number of students..." | short deliberation, arithmetic slip |
| 207 | 4/4 | 162 | "To determine the number of different pizzas..." | short deliberation |

The per-problem k/4 of all 60 Q and 105 N problems is in readout.json (keys q and n). 4 of the 11 read rows (0,
170, 182, 207) are short deliberative attempts, and three of those are on problems the cued base solves 4 of 4; most are format failures (empty, prompt continuation, web text),
which fail on easy and hard problems alike. Q's problems are solved 0.833 of the time by the cued base, N's 0.838,
all 250 problems 0.814: Q is not harder. Instrument check: the same measure on m21's 33 long wrong answers
(> 1,000 tokens) gives 0.40, so it does detect harder problems when they are there; problems the cued base solves 4
of 4 give 1.0.
