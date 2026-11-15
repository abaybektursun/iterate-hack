# m21open-01: 10 Q rows and 10 N rows read by eye

Q = m21's 60 quick wrong rows (every 6th row by problem index). AF = the plan's answer-first rule.

| problem | rule | tokens | first characters | by eye |
|---|---|---|---|---|
| 0 | not AF | 349 | "To convert from rectangular coordinates to polar..." | deliberation; answer right but a note appended, so v3 scores it wrong |
| 41 | not AF | 1 | (empty) | empty reply, not deliberative, not answer-first |
| 68 | not AF | 659 | ".\n\nHelp is available.\n\nProblem ..." | web-page continuation |
| 78 | not AF | 1 | (empty) | empty reply |
| 109 | not AF | 439 | " and it should be enclosed in quotation marks..." | prompt continuation then junk algebra |
| 128 | not AF | 336 | " Area of circles Video transcript..." | web text |
| 157 | not AF | 5 | ' or "Solution."' | prompt continuation |
| 182 | AF | 165 | ".\nAnswer: To find the number of students..." | rule error: deliberation written after "Answer:" |
| 207 | not AF | 162 | ".\nTo determine the number of different pizzas..." | short deliberation, wrong value |
| 226 | AF | 55 | ' so the response ... will say "Answer:"...' | rule error: prompt continuation echoing "Answer:" |

N = the plain base's 105 quick wrong rows (every 10th): 9 web/difficulty text, 36 prompt continuation, 61 template
text, 83 "give JSON output only", 105 prompt continuation, 130 short step-by-step, 159 " $Answer$", 177 " without
quotes", 200 short "Let's start", 218 empty. The rule calls all 10 not AF, and by eye none is an answer-first reply.

What the rows show: m21's quick wrongs and the plain base's quick wrongs are the same kinds of failure (prompt
continuations, empty replies, web text, short attempts); few of either are "Answer:"-first replies. 2 of 20 rows are
misclassified, both by counting a non-answer-first row as AF, so by the spec the verdict uses the strict rule, which
gives the same shares (0.25 vs 0.21). Of the 15 Q rows the rule calls AF, only 3 to 5 (problems 37, 42, 131, maybe 28,
234) are answer-first by eye; most of the rest start with "(" or contain a quoted "Answer:" in a prompt continuation.
So s_Q = 0.25 is an upper bound, and the floor test (0.40) fails with or without that correction.
Instrument check: long right T3 answers (n 58) are 0.14 AF and 0.48 open with "Okay"; Q 0.03 and N 0.00 open with
"Okay". The spec's check "N must be mostly AF" failed (0.21): by eye the rule reads N correctly, so it is the
premise that plain-base quick wrongs are answer-first that fails, which makes the gap test uninformative; the floor
test does not use N.
