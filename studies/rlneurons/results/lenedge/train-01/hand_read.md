# Hand read of training turns (one reader, the agent; not a blind judge)

Source: `examples.json` of this folder. Excerpts only: 300 characters before and 500 after the first Chinese character
(flagged turns); the first 300, 300 from the middle and the last 400 characters (longest turns). Translations are mine.

## 15 flagged turns after a prompt without Chinese (the 15 lowest SHA-1 of the row id among all 266,162)

13 are from OpenThoughts3 math, 1 from OpenThoughts3 code (F1), 1 from the Python set (F13). All 15 are late in a long
English derivation (first Chinese character at token 10,890 to 28,588 of turns of 16,885 to 29,592 tokens; over all
flagged turns 264,454 of 266,162 have it inside the thinking, `readout.json`). In all 15 the same working goes on: Chinese connectives, single words or half-sentences replace
English ones, and English resumes inside the same sentence or the next line. None is a translation task, a quotation or a
Chinese answer. The English next to the switch is often clipped (one clause per line, commas for full stops).

| # | Row id (suffix) | Turn tokens | First Chinese at token | Quote | Translation |
|---|---|---|---|---|---|
| F1 | code `_87936` | 21,537 | 12,568 | "c,h,r →3 (总3) ... 加上最后的 closing bracket?" | "(3 in total) ... plus the last closing bracket?" |
| F2 | math `_252629` | 26,628 | 21,689 | "SF must still assigned to David? 不可, so only one way" | "not possible" |
| F3 | math `_647764` | 25,431 | 24,606 | "计算时，计算这个点到M=(7,0)的距离? 等一下， if we assume O 在这条垂直平分线上" | "when computing, compute the distance from this point to M? wait, if we assume O is on this perpendicular bisector" |
| F4 | math `_445721` | 29,592 | 28,588 | "故 only possible solutions are angles where ... 但 this line of reasoning indicates" | "hence ... but" |
| F5 | math `_588054` | 18,111 | 15,554 | "s2分配: suppose b2=0, c2=1 ... 假设为： 取s5： 设b5=0,c5=2 ... 则:" | "assignment of s2 ... assume: take s5: let b5=0, c5=2 ... then:" |
| F6 | math `_644629` | 23,756 | 17,476 | "from the constraints on p and q, 即: - For p and q, we had" | "that is:" |
| F7 | math `_499110` | 27,363 | 16,909 | "等待： No, the term is (1/z)*(X(z) -x₁)? 等待： 因为 X(z)=x₁ z+ x₂ z²+..., 所以 X(z) -x₁ z的开头是 x₂ z²" | "wait: ... wait: because X(z) = ..., so X(z) - x₁z starts with x₂z²" |
| F8 | math `_555415` | 20,295 | 15,887 | "Wait，going back，如果设这个圆是旁切圆，但它的中心在边上，可能需要 specific conditions." | "if we take this circle to be an excircle, but its centre is on the side, it may need" |
| F9 | math `_294882` | 27,262 | 23,834 | "b8=2325/4352, b9、b10, 等， so no direct repeat." | "and so on" |
| F10 | math `_500997` | 28,783 | 24,612 | "则 AD would be sqrt( (a-1)^2 +1) ... 很难 see. Given time invested and problem complexity, perhaps the answer is 12 or another common number" | "then ... hard to see" (the trace then guesses) |
| F11 | math `_689650` | 21,977 | 12,877 | "-5-7 -12 模12? Wait: Wait, compute step-by-step" | "mod 12?" |
| F12 | math `_711765` | 29,547 | 26,770 | "term^(9)= 约1.0202的9次,约1.02的9是约1.195 ... 估计会增长到约 e^{...} ×修正项" | "about 1.0202 to the 9th, about 1.02 to the 9th is about 1.195 ... will probably grow to about e^{...} times a correction term" |
| F13 | Python `_683af5ab` | 16,885 | 10,890 | "The reversed segment 内的连接 is: E (6) next is S (5)" | "the links inside the reversed segment" |
| F14 | math `_260538` | 24,169 | 22,194 | "方程1: a² = d² ... 因此， a² b =0, 因为a ≠0, 所以 b=0, 然而，problem states that b非零" | "equation 1 ... therefore a²b = 0, because a ≠ 0, so b = 0, however the problem states that b is non-zero" |
| F15 | math `_506958` | 20,453 | 17,171 | "but these lead to 矛盾 the condition, therefore, the problem is incorrect" | "contradict" |

This is the text the Drift hand read found in Think-SFT's own answers (`results/drift/describe-01/hand_read.md`: "因此，
x = ab + 1 ... 不，原式 ... 所以：", "Wait，我先重新看一下方程的推导"): the same connectives (因此, 所以, 等, 则, 但) inside the
same derivation, with English resuming.

## The 15 longest turns in tokens (among the 40 longest in characters of each shard)

| # | Source | Tokens | zlib ratio | What it is |
|---|---|---|---|---|
| L1 | aya (DeepSeek R1) | 101,636 | 0.027 | Arabic poem request; the thinking is tens of thousands of the tatweel character "ـ", then a normal Arabic answer |
| L2 to L10 | WildChat, 9 turns (DeepSeek R1) | 42,496 to 48,415 | 0.030 to 0.058 | comedic story requests; the thinking is one letter repeated ("OOOO...", "PPPP..."), then in 5 a normal English story (L4, L5, L7, L8, L10), in 2 a story partly in Chinese (L2, L3); in L6 and L9 the run ends with "极简主义风格，..." ("minimalist style, answer in Chinese, at most 100 characters" in L6, which then answers in Chinese) |
| L11 | aya (DeepSeek R1) | 40,104 | 0.027 | Gujarati request; the thinking is one Gujarati sign repeated, then "极" and a normal Gujarati answer |
| L12 | OpenThoughts3 science | 33,365 | 0.300 | double-bond equivalents; a normal long derivation with a final answer, 1,506 Chinese characters |
| L13 | Nemotron code | 33,339 | 0.228 | a programming problem; normal long reasoning, a final solution, no Chinese |
| L14 | OpenThoughts3 math | 33,308 | 0.248 | a logic puzzle; normal long derivation with a final answer, 1,052 Chinese characters |
| L15 | OpenThoughts3 math | 33,295 | 0.290 | a volume problem; normal long derivation with a final answer, 1,182 Chinese characters |

11 of the 15 are loops of one character in traces of DeepSeek R1 (zlib ratio under 0.06) that the repetition filter of the
data left in; they are longer than the 32,768-token training sequence. The 4 others sit at the 32K generation limit of the
QwQ-32B traces and are ordinary derivations that reach an answer. The longest turns are therefore not where the math
traces end: those end at about 33,300 tokens of this tokenizer.
