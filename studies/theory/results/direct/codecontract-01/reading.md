Ten base failures that Code top-8 1x fixes, drawn at random (seed 1) from the 100, read in runs/<job>/answers.jsonl
(base = abaybektursun-1114-170304-c03c, top8 = abaybektursun-1115-101423-4a7d). Class = the frozen contract classifier; k2 =
passes in the Math-cue base and random 1.5x cells.

1. HumanEval/162, logic, k2 2: base forgot `import hashlib` (NameError); top8 imports it. A finishing slip the base avoids elsewhere.
2. Mbpp/592, no_entry, k2 1: base defines `sum_of_product`, tests call `sum_Of_product` (15,372 tokens); top8 uses the test's name. A real contract fix.
3. Mbpp/90, logic, k2 1: base returns the longest word, not its length, and leaves a failing assert in the block; top8 returns the length. Logic.
4. HumanEval/129, unparsable, k2 1: base block holds prose inside the code (SyntaxError), 11,587 tokens; top8 writes a clean block.
5. HumanEval/99, cap_hit, k2 2: base runs to the 16,384 cap with no block; top8 finishes at 5,460 tokens.
6. HumanEval/157, logic, k2 2: base has a typo `returnFalse` (NameError); top8 writes a short correct function.
7. Mbpp/557, no_block, k2 1: base stops after 420 tokens of reasoning with no block; top8 writes the block.
8. Mbpp/448, logic, k2 0: base gets the Perrin sum's small cases wrong (5 vs 3); top8 handles them. Logic the base never gets.
9. Mbpp/465, logic, k2 0: base drops empty dicts too (`if v`); top8 uses `is not None`. Logic.
10. Mbpp/641, logic, k2 1: base uses the wrong nonagonal formula (405 vs 325); top8 the right one.

What they show: 4 of 10 are contract failures by the frozen rule (2, 4, 5, 7), about the 43 % share of all 100 fixes; 6 are
plain logic or slips. Two "logic" rows (1, 6) are NameErrors (missing import, typo) that a broader contract definition could
count; counting every base NameError as contract moves S_top8 to 0.49 and S_rand to 0.41, so verdict a does not change. 8 of
10 have k2 >= 1: the base solves them in another sample, as rival b says; rows 8 and 9 (k2 0) are the logic fixes the base
never makes in the stored samples.
