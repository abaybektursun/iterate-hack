# codepass-01: 10 raw rows read

Rows from `runs/<job>/answers.jsonl` (random 1.5x abaybektursun-1115-101457-ef2c, Code 1.5x abaybektursun-1115-101434-4511,
Math 1.5x abaybektursun-1115-101508-33f0). Selected as the first problems (by uid) of each discordant kind.

1. HumanEval/102, Code passes, random fails: random sorts x, y with min/max; Code returns -1 when x > y, which the spec asks. Logic, not format.
2. HumanEval/111, Code passes, random fails: random counts characters with Counter (spaces included); Code splits into words. Logic.
3. HumanEval/115, Code passes, random fails: Code sums ceil(count/capacity) per row; random's program fails an exact-match test. Logic.
4. HumanEval/119, Code passes, random fails: both write a balance checker; random's fails an assertion on a test pair. Logic.
5. HumanEval/101, Math passes, random fails: random splits with the regex `(?:, | )` and misses a bare comma case; Math's program passes.
6. HumanEval/102, Math passes, random fails: Math handles x > y as Code does (same problem as row 1).
7. HumanEval/111, Math passes, random fails: Math counts words (same problem as row 2).
8. HumanEval/106, Code fails, random passes: Code's factorial/sum list fails an exact-match test; random's passes.
9. HumanEval/108, Code fails, random passes: Code skips negative numbers (only `num > 0` counted with signed digits); random handles the sign.
10. HumanEval/124, Code fails, random passes: Code's date validator fails a test; random's passes.

What they show: all failures are AssertionError on the benchmark tests (exit 1), so among finished answers with a block
the difference is program correctness, not format or timeouts. The grader fails wrong programs and passes right ones
(rows 1, 2 differ in one condition and score as expected). Math's directions also fix logic on some problems (rows 5-7);
the count decides how often: on problems random finished with a block, Code gains 68 and loses 29 against random, Math
gains 64 and loses 50.
