# rank1-01: 10 raw rows read

Ten problems drawn at random (numpy default_rng(1)) from the primary set (a base sample on seed 3020000 or 3030000
finished wrong). Each line: problem, gold, selector's wrong answer and length, second-base right mean (b), then the
TOP1 row and the D28 row (answer, v3 score, cap hit, tokens). Text read in `runs/<job>/answers.jsonl`.

1. P67, gold 025. Base b2: 125 (13,415 tok); b 1.00. TOP1: 25, right, 3,235 tok, clean `\boxed{25}`. D28: 25, right, 3,494 tok.
2. P97, gold 77. Base b2: -73/4 (12,493 tok); b 0.67. TOP1: 77, right, 3,310 tok, derives 73/4 then m+n. D28: -3/5, wrong, 15,317 tok.
3. P151, gold 11. Base b2: 4; b 0.00. TOP1: cap hit at 16,384 ("perhaps I need to consider that the answer is"). D28: cap hit.
4. P168, gold 1037. Base b3: 45; b 0.00. TOP1: 1981, wrong, boxed, 14,895 tok. D28: 0, wrong, 9,622 tok.
5. P196, gold (2,4). Base b3: "No such pairs exist"; b 1.00. TOP1: (2, 4), right, boxed after a case check. D28: (2, 4), right.
6. P209, gold ceil(n/2)+1. Base b3: n-1; b 0.00. TOP1: cap hit, gives up in words. D28: cap hit, still checking floor/ceiling forms.
7. P312, gold 1/16. Base b2: 1/6; b 0.00. TOP1: 1/70, wrong, boxed. D28: 1/16, right, boxed.
8. P334, gold 2 sqrt(10). Base b2: 8; b 0.33. TOP1: sqrt(100 + 12 sqrt(15)), wrong. D28: 2 sqrt(10), right, 7,880 tok.
9. P369, gold 76. Base b2: infinity; b 0.00. TOP1: 76, right, 11,212 tok, but the closing line asserts 76 without a derivation shown at the end. D28: 2020, cap hit.
10. P372, gold 12. Base b2: 27; b 0.00. TOP1: 28, wrong, boxed. D28: 8, wrong, boxed.

What they show: the grader scores each row as a reader would (025 = 25, (2, 4) = $(2,4)$, capped rows wrong). On
these ten, TOP1 is right on 4 (P67, P97, P196, P369) and D28 on 4 (P67, P196, P312, P334), against a second-base
mean of 0.30. TOP1 adds right answers on base-finished-wrong problems with full derivations (P97 in 3,310 tokens),
not only by finishing: the mechanism's "direction 1 finishes without adding right answers" does not describe these
rows. Both edits fail on the same hard items (P151, P168, P209, P372). TOP1's right answers are not unboxed or
format-only; its wrong finished rows are boxed wrong numbers.
