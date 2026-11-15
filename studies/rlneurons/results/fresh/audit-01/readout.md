# fresh2026 rescored on the audited sets (stored rows, no model run; T 1.0 / top-p 1.0, grader v3, 4 samples)

Right answers of n. Vote over 4: in the stored sample order (as posted) and as the expectation under a random tie-break.

| set | n | model | one sample (mean of 4) | vote, stored order | vote, expected |
|---|---|---|---|---|---|
| a: all 136 | 136 | Think-SFT + cue | 60.0 | 75 | 75.5 |
| a: all 136 | 136 | RL plain | 50.5 | 57 | 55.8 |
| a: all 136 | 136 | base + cue | 29.5 | 38 | 38.8 |
| a: all 136 | 136 | Think-SFT + cue, cap 32,768 | 70.2 | 75 | 75.8 |
| a: all 136 | 136 | the same answers cut at 16,384 | 59.0 | 73 | 72.2 |
| b: without the problems whose v1 statement or answer is wrong | 136 | Think-SFT + cue | 60.0 | 75 | 75.5 |
| b: without the problems whose v1 statement or answer is wrong | 136 | RL plain | 50.5 | 57 | 55.8 |
| b: without the problems whose v1 statement or answer is wrong | 136 | base + cue | 29.5 | 38 | 38.8 |
| b: without the problems whose v1 statement or answer is wrong | 136 | Think-SFT + cue, cap 32,768 | 70.2 | 75 | 75.8 |
| b: without the problems whose v1 statement or answer is wrong | 136 | the same answers cut at 16,384 | 59.0 | 73 | 72.2 |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | Think-SFT + cue | 57.8 | 72 | 72.5 |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | RL plain | 48.8 | 55 | 53.8 |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | base + cue | 29.0 | 38 | 38.6 |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | Think-SFT + cue, cap 32,768 | 67.0 | 72 | 72.8 |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | the same answers cut at 16,384 | 56.0 | 69 | 68.2 |
| the 77 transcribed | 77 | Think-SFT + cue | 37.2 | 46 | 46.0 |
| the 77 transcribed | 77 | RL plain | 32.8 | 35 | 33.8 |
| the 77 transcribed | 77 | base + cue | 19.8 | 25 | 25.6 |
| the 77 transcribed | 77 | Think-SFT + cue, cap 32,768 | 42.2 | 44 | 44.5 |
| the 77 transcribed | 77 | the same answers cut at 16,384 | 36.2 | 44 | 43.2 |
| the 77 transcribed without the v1-wrong problems | 77 | Think-SFT + cue | 37.2 | 46 | 46.0 |
| the 77 transcribed without the v1-wrong problems | 77 | RL plain | 32.8 | 35 | 33.8 |
| the 77 transcribed without the v1-wrong problems | 77 | base + cue | 19.8 | 25 | 25.6 |
| the 77 transcribed without the v1-wrong problems | 77 | Think-SFT + cue, cap 32,768 | 42.2 | 44 | 44.5 |
| the 77 transcribed without the v1-wrong problems | 77 | the same answers cut at 16,384 | 36.2 | 44 | 43.2 |
| the transcribed problems identical after normalisation | 73 | Think-SFT + cue | 35.0 | 43 | 43.0 |
| the transcribed problems identical after normalisation | 73 | RL plain | 31.0 | 33 | 31.8 |
| the transcribed problems identical after normalisation | 73 | base + cue | 19.2 | 25 | 25.3 |
| the transcribed problems identical after normalisation | 73 | Think-SFT + cue, cap 32,768 | 39.0 | 41 | 41.5 |
| the transcribed problems identical after normalisation | 73 | the same answers cut at 16,384 | 33.2 | 40 | 39.2 |

Differences in points [95 %], paired bootstrap over problems, 5,000 resamples.

| set | n | difference | one sample | vote, stored order | vote, expected |
|---|---|---|---|---|---|
| a: all 136 | 136 | Think-SFT + cue minus RL plain | +7.0 [+3.1, +11.0] | +13.2 [+7.4, +19.1] | +14.5 [+8.5, +20.6] |
| a: all 136 | 136 | Think-SFT + cue minus base + cue | +22.4 [+17.5, +27.8] | +27.2 [+19.9, +35.3] | +27.0 [+20.0, +34.4] |
| a: all 136 | 136 | RL plain minus base + cue | +15.4 [+11.4, +19.9] | +14.0 [+8.1, +19.9] | +12.4 [+7.5, +17.9] |
| a: all 136 | 136 | Think-SFT + cue, cap 32,768 minus RL plain | +14.5 [+9.9, +19.1] | +13.2 [+6.6, +19.9] | +14.7 [+8.6, +21.1] |
| a: all 136 | 136 | the same answers cut at 16,384 minus RL plain | +6.2 [+2.0, +10.5] | +11.8 [+5.1, +18.4] | +12.1 [+5.9, +18.5] |
| b: without the problems whose v1 statement or answer is wrong | 136 | Think-SFT + cue minus RL plain | +7.0 [+3.1, +11.0] | +13.2 [+7.4, +19.1] | +14.5 [+8.5, +20.6] |
| b: without the problems whose v1 statement or answer is wrong | 136 | Think-SFT + cue minus base + cue | +22.4 [+17.5, +27.8] | +27.2 [+19.9, +35.3] | +27.0 [+20.0, +34.4] |
| b: without the problems whose v1 statement or answer is wrong | 136 | RL plain minus base + cue | +15.4 [+11.4, +19.9] | +14.0 [+8.1, +19.9] | +12.4 [+7.5, +17.9] |
| b: without the problems whose v1 statement or answer is wrong | 136 | Think-SFT + cue, cap 32,768 minus RL plain | +14.5 [+9.9, +19.1] | +13.2 [+6.6, +19.9] | +14.7 [+8.6, +21.1] |
| b: without the problems whose v1 statement or answer is wrong | 136 | the same answers cut at 16,384 minus RL plain | +6.2 [+2.0, +10.5] | +11.8 [+5.1, +18.4] | +12.1 [+5.9, +18.5] |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | Think-SFT + cue minus RL plain | +6.8 [+3.0, +11.0] | +12.9 [+6.8, +19.7] | +14.2 [+7.7, +20.8] |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | Think-SFT + cue minus base + cue | +21.8 [+16.7, +27.3] | +25.8 [+18.2, +33.3] | +25.7 [+18.6, +33.1] |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | RL plain minus base + cue | +15.0 [+11.0, +19.3] | +12.9 [+6.8, +18.9] | +11.5 [+6.6, +16.8] |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | Think-SFT + cue, cap 32,768 minus RL plain | +13.8 [+9.5, +18.8] | +12.9 [+6.1, +19.7] | +14.4 [+8.4, +21.0] |
| c: the 59 from Hugging Face + the transcribed problems identical after normalisation | 132 | the same answers cut at 16,384 minus RL plain | +5.5 [+1.3, +9.5] | +10.6 [+3.8, +17.4] | +10.9 [+4.6, +17.3] |
| the 77 transcribed | 77 | Think-SFT + cue minus RL plain | +5.8 [+1.3, +10.7] | +14.3 [+6.5, +23.4] | +15.8 [+7.7, +24.6] |
| the 77 transcribed | 77 | Think-SFT + cue minus base + cue | +22.7 [+16.2, +29.2] | +27.3 [+16.9, +37.7] | +26.5 [+17.1, +36.3] |
| the 77 transcribed | 77 | RL plain minus base + cue | +16.9 [+11.0, +23.4] | +13.0 [+5.2, +22.1] | +10.7 [+4.4, +18.1] |
| the 77 transcribed | 77 | Think-SFT + cue, cap 32,768 minus RL plain | +12.3 [+7.5, +17.9] | +11.7 [+3.9, +19.5] | +13.9 [+7.1, +21.3] |
| the 77 transcribed | 77 | the same answers cut at 16,384 minus RL plain | +4.5 [+0.3, +9.4] | +11.7 [+3.9, +19.5] | +12.1 [+5.7, +19.3] |
| the 77 transcribed without the v1-wrong problems | 77 | Think-SFT + cue minus RL plain | +5.8 [+1.3, +10.7] | +14.3 [+6.5, +23.4] | +15.8 [+7.7, +24.6] |
| the 77 transcribed without the v1-wrong problems | 77 | Think-SFT + cue minus base + cue | +22.7 [+16.2, +29.2] | +27.3 [+16.9, +37.7] | +26.5 [+17.1, +36.3] |
| the 77 transcribed without the v1-wrong problems | 77 | RL plain minus base + cue | +16.9 [+11.0, +23.4] | +13.0 [+5.2, +22.1] | +10.7 [+4.4, +18.1] |
| the 77 transcribed without the v1-wrong problems | 77 | Think-SFT + cue, cap 32,768 minus RL plain | +12.3 [+7.5, +17.9] | +11.7 [+3.9, +19.5] | +13.9 [+7.1, +21.3] |
| the 77 transcribed without the v1-wrong problems | 77 | the same answers cut at 16,384 minus RL plain | +4.5 [+0.3, +9.4] | +11.7 [+3.9, +19.5] | +12.1 [+5.7, +19.3] |
| the transcribed problems identical after normalisation | 73 | Think-SFT + cue minus RL plain | +5.5 [+1.0, +10.3] | +13.7 [+5.5, +21.9] | +15.3 [+6.7, +24.0] |
| the transcribed problems identical after normalisation | 73 | Think-SFT + cue minus base + cue | +21.6 [+15.4, +28.1] | +24.7 [+15.1, +35.6] | +24.2 [+15.0, +34.1] |
| the transcribed problems identical after normalisation | 73 | RL plain minus base + cue | +16.1 [+10.6, +21.9] | +11.0 [+2.7, +19.2] | +8.9 [+3.0, +15.2] |
| the transcribed problems identical after normalisation | 73 | Think-SFT + cue, cap 32,768 minus RL plain | +11.0 [+6.2, +16.4] | +11.0 [+2.7, +19.2] | +13.2 [+6.5, +21.0] |
| the transcribed problems identical after normalisation | 73 | the same answers cut at 16,384 minus RL plain | +3.1 [-0.7, +7.2] | +9.6 [+1.4, +17.8] | +10.0 [+4.0, +16.9] |
