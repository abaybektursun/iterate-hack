# karpagree-01: 10 raw rows read (first 10 of the 42 lost problems, by index)

Same rows as karpcap-01/reading.md, read for b's claim (agreeing short finished wrong answers). Each line: problem,
Karpathy winning answer, the cued base's finished wrong answers over all attempts of samples 0-3, agreement.

1. 58: Karpathy "1"; base wrong ["729"]; no agreement.
2. 66: Karpathy "$Answer (without quotes)$"; base wrong ["673", "16011"]; no agreement (the winner is not an answer).
3. 68: Karpathy "505"; base has no finished wrong answer.
4. 71: Karpathy "1820"; base has no finished wrong answer (4 of 4 right).
5. 83: Karpathy "1"; base wrong ["55"]; no agreement.
6. 86: Karpathy "2024"; base wrong ["72"]; no agreement.
7. 91: Karpathy "The area of heptagon AFNBCEM is 288."; base wrong ["576", "648"]; no agreement.
8. 92: Karpathy "$0$"; base wrong ["378", "3"]; no agreement.
9. 94: Karpathy "$N - 2025 = 0$"; base wrong ["-2025"]; no agreement by the grader (the same number inside an equation).
10. 97: Karpathy "5"; base wrong ["-\dfrac{73}{4}", "73"]; no agreement.

What they show: none of these 10 winners agrees with a base wrong answer; several are not answers at all (a word, a
sentence, an equation), which a finished short wrong solution would rarely produce and a cut sample asked "Answer:"
does. Over the 42 lost problems, 27 have base wrong answers to compare and in 19 of them the Karpathy winner matches
none. The pooled agreement A_K = 0.23 (39 pairs) against A_B = 0.17 (12 pairs) is driven by a few small-integer
values (problem 135: Karpathy "$1$", base wrong ["0", "1"]). Against b.
