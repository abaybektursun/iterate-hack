# karpcap-01: 10 raw rows read (first 10 of the 42 lost problems, by index)

Lost = Karpathy vote wrong and the cued base right on >= 2 of 4 samples (attempt 0, T 1.0, cap 16,384). Each line:
problem, gold, Karpathy winning answer, k, the cued base's 4 samples as (generated tokens, answer, score), long_only
(1 = every right base sample is longer than 4,096 tokens).

1. 58: gold 024, Karpathy "1"; base (16384, Answer, 0) (11148, 24, 1) (13245, 24, 1) (16384, -, 0); long_only 1.
2. 66: gold 721, Karpathy "$Answer (without quotes)$"; base right at 9,178 and 10,520 tokens; long_only 1.
3. 68: gold 809, Karpathy "505"; base right at 9,475, 6,008, 7,159; long_only 1.
4. 71: gold 294, Karpathy "1820"; base right 4 of 4, at 6,032 to 9,920 tokens; long_only 1.
5. 83: gold 045, Karpathy "1"; base right at 12,564 and 9,520; long_only 1.
6. 86: gold 055, Karpathy "2024"; base right 3 of 4 at 7,552 to 8,905; long_only 1.
7. 91: gold 588, Karpathy "The area of heptagon AFNBCEM is 288."; base right at 6,796 and 6,962; long_only 1.
8. 92: gold 16, Karpathy "$0$"; base right at 4,949 and 4,950 (just over the cap); long_only 1.
9. 94: gold 279, Karpathy "$N - 2025 = 0$"; base right 3 of 4 at 12,703 to 15,690; long_only 1.
10. 97: gold 77, Karpathy "5"; base right at 3,964 and 2,608; long_only 0 (a short right route exists and the vote still lost).

What they show: 9 of 10 lost problems have only right routes longer than 4,096 tokens, most of them 6,000 to 13,000,
far past the cap. The Karpathy winners look like what a cut sample writes when asked "Answer:" at its limit: small
numbers (1, 0, 5), the problem's year (2024), a restated equation, the word "Answer". Over all 42 lost problems, 13
winners are not a plain integer and 8 are 0, 1 or 2. This is consistent with a: the right votes never arrive because
every right route is cut, and the vote falls to half-weight guesses.
