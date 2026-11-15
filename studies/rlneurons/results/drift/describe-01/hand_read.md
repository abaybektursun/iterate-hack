# Hand read of 20 Think-SFT samples with a switch (the 20 of `examples.json`, drawn with seed 0)

Read by the agent that ran the study (Claude), not by a blind judge; translations are the agent's. Item numbers are the
positions in `examples.json` (8 hard328, 8 fresh2026, 4 from the 32,768 sample).

What the text is doing at the first switch:

- 15 of 20: the same working goes on (arithmetic, a case split, a substitution) and Chinese connectives or half-sentences
  replace English ones inside it. The mathematics, the numbers and most nouns stay in English or LaTeX. Items 0, 1, 2, 3, 5,
  6, 9, 11, 12, 13, 14, 15, 16, 18, 19.
- 4 of 20: one stray non-Latin word or fragment inside an English sentence, then English again. Items 4 (Arabic), 7
  (Russian), 8, 10.
- 1 of 20: the sample gives up and guesses an answer, in Chinese. Item 17.
- 0 of 20: a loop, a change of topic, or text unrelated to the problem.

In 18 of 20 English resumes within 1,000 characters (the detector's `back`), and Chinese words then keep coming back: 10 of
the 20 have more than one episode. The English next to a switch is often already broken ("Thus a=10 not version",
"slogan3: D4 must be pointing to", "cob x_A + siny A y_A").

| Item | Cell, problem, sample | Start token, outcome | Quote | Translation | Doing |
|---|---|---|---|---|---|
| 0 | hard328 61, s1 | 13,584, cap hit | "要与之转换为1,089分母 ... 但是这是分数的计算" | "to convert it to denominator 1,089 ... but this is a calculation with fractions" | arithmetic on fractions |
| 1 | hard328 66, s0 | 14,310, finished right | "S(a)的最大值在a=2精确。这表明当a=2时，才是最大值" | "the maximum of S(a) is exactly at a = 2. This shows the maximum is only at a = 2" | checking a numeric estimate against calculus |
| 2 | hard328 81, s3 | 14,323, cap hit | "具体来说， for a dodecagon：" | "concretely, for a dodecagon:" | case work on chords |
| 3 | hard328 170, s2 | 16,025, cap hit | "等, another approach ... 注意 node7只能连接1和2. 因此，" | "wait, another approach ... note node 7 can only connect to 1 and 2. Therefore," | new attempt after "this is getting too confusing" |
| 4 | hard328 172, s3 | 1,529, cap hit | "such subsets are called \"انضمامات\" or connected" | Arabic, roughly "joinings" | one stray word, English goes on |
| 5 | hard328 215, s2 | 16,252, cap hit | "(继续到5). 从4到5 ... 因此从5可到6。" | "(continue to 5). From 4 to 5 ... so from 5 one can reach 6." | enumerating paths in a grid |
| 6 | hard328 267, s2 | 15,565, cap hit | "Wait，我先重新看一下方程的推导." | "Wait, let me first look at the derivation of the equation again." | re-checking a derivation |
| 7 | hard328 342, s1 | 13,257, cap hit, right answer in the text | "my previous assumption of s=1/2 was академ, even though angle didn't match" | Russian fragment "academ(ic)" | one stray word |
| 8 | fresh 43, s1 | 11,957, finished wrong | "the interval只出现这段边被切割的 so the side that includes" | "only this stretch of edge is cut" | counting arcs of a polygon |
| 9 | fresh 81, s0 | 12,994, cap hit | "因此， x = ab +1 ... 不，原式 ... 所以：" | "therefore, ... no, the original expression ... so:" | substitution in a system |
| 10 | fresh 83, s1 | 16,258, cap hit | "13/(1001×11×7后得到77?)" | "after which one gets 77?" | common denominators |
| 11 | fresh 88, s2 | 10,200, cap hit | "一个 buy remains? 一个 no, 因为我们 have to use up all 2). 等等， this is getting complicated." | "one buy remains? one, no, because we have to use up all 2. Wait, this is getting complicated." | setting up a DP |
| 12 | fresh 97, s0 | 15,539, cap hit | "合计: ... 接近50上，近2的根。 Wait 我可能计算错误了" | "total: ... close to 50, a root near 2. Wait, I may have miscalculated" | numeric root finding |
| 13 | fresh 98, s0 | 13,349, cap hit | "贡献 to mutual edges ... 需要 previous direction (D3) and current D4" | "contribution to mutual edges ... needs the previous direction" | DP transitions |
| 14 | fresh 116, s3 | 13,009, finished right | "剩下的beads in25 ... 等等" | "the remaining beads in 25 ... wait" | placing beads by position |
| 15 | fresh 131, s2 | 15,915, cap hit | "故, x_A²+y_A²=... 因为 ... 所以: ... 因此," | "hence, ... because ... so: ... therefore," | expanding a circle equation |
| 16 | 32k 81 | 12,131, finished wrong at 20,659 | "但绝对: ... steps (它们的之间的角度差异是90 degrees): 注意," | "but absolutely: ... (the angle difference between them is 90 degrees): note," | tabulating step pairs |
| 17 | 32k 98 | 30,174, finished wrong at 31,639 | "最终，考虑到问题的结构和所需的答案形式，可能正确的答案是 ... 但没有依据。" | "In the end, given the structure of the problem and the required form of the answer, the right answer may be ... but there is no basis for it." | gives up and guesses |
| 18 | 32k 308 | 20,219, finished right at 21,035 | "方程2:13d +bc=333 ... 代入 equation2方程 ... 移动 all到等式左边" | "equation 2: ... substitute into equation 2 ... move all to the left side" | solving a Diophantine system |
| 19 | 32k 342 | 19,368, finished wrong at 28,625 | "检查 equation1: ... ≈-1成立！ Hey! It works! ... 因此, the angle a=0.5 radians" | "check equation 1: ... holds! ... therefore," | verifying a numeric guess |
