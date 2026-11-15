# capbox-01: 10 raw RL plain cap-hit rows read by hand

Rows: native 16,384-cap hard328, RL plain (job abaybektursun-1114-200505-5ff2, attempt 0). All 7 rows that grader v3
credits, then the first 3 uncredited rows that hold a box. Text around the winning answer and the last 300 characters
are in `rows10.json`. "pos" is where the winning candidate starts, as a share of the text length.

| problem / sample | v3 | extracted / gold | pos | what the text shows |
|---|---|---|---|---|
| 79 / 0 | right | 321 / 321 | 0.98 | Finishes reasoning, "**Final Answer** \boxed{321}", then starts a second write-up ("To solve the problem, we start by...") and is cut inside it. |
| 79 / 2 | right | 321 / 321 | 0.96 | Same pattern: box, then a restated solution cut at step 6. |
| 133 / 0 | right | 1 / 1 | 0.98 | "Thus, the answer should be \boxed{1}", "**Final Answer** \boxed{1}", then a second write-up cut mid-expansion. |
| 187 / 2 | right | \sqrt{6} / \sqrt{6} | 0.93 | "So I'll go with \boxed{\sqrt{6}}", Final Answer box, then a coordinate write-up cut. |
| 300 / 2 | right | 2302 / 2302 | 0.99 | "the final answer is \boxed{2302}.", then the write-up begins and is cut after two sentences. |
| 333 / 3 | right | 5 / 5 | 0.96 | Gives up ("time's up, perhaps the answer is \boxed{1}"), then "**Final Answer** \boxed{5}" (right), then a write-up cut. A late guess, credited. |
| 344 / 2 | right | 990 / 990 | 0.94 | Garbled ending ("Iboxed 990"), "\boxed{ 990}" earlier wins, then a write-up cut. |
| 61 / 0 | wrong | ":" / 113 | 1.00 | Cut right after "Thus, the final answer is:\n\[\n\"; its own value would have been 27 (wrong); v3 takes ":" from the marker. |
| 62 / 0 | wrong | 289 / 371 | 0.98 | Same box-then-write-up pattern as the credited rows, with a wrong box. |
| 62 / 2 | wrong | 129 / 371 | 0.97 | Same pattern, wrong box ("I will go with \boxed{129}"). |

What the rows show: every credited RL cap-hit row is a finished solution whose box was followed by a second,
restated write-up that ran into the cap; none is a box written in the middle of the reasoning and then abandoned. The
uncredited boxed rows have the same shape with a wrong answer. So the mechanism's premise (RL's capped rows hold a box:
68 % here, matching the 69 % of knowledge-16c62a) reproduces on hard328, but the boxes are mostly wrong: 7 of the 75
rows whose winning candidate is a box are right. Row 61/0 shows a v3 quirk (a lone ":" extracted from "final answer
is:"); it is scored wrong either way.
