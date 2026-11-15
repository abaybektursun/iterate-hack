# Working notes: lens-diff peaks vs base errors (T1, rl_only)
Classes: E=at_error, F=at_wrong_final_answer, C=at_correct_step, U=unclear. "D" suffix = downstream of root error but local step fine.
holdRL = rl_top (8 words) contains a Wait/Hmm variant; holdBase = base_top contains one. nextRL = RL next-token top1 is hold-on?
DATA CAVEAT seen early: many big-gap peaks have rl_top = junk fragments ('brane','udence','RODUCTION',' prefixed',' unfavor') and base_top = one concentrated copy token ('53',' vertical'). Gap then comes from base concentration, no hold-on word in RL top-8.

## 4 (misread axes; gold Evelyn, base Angela). Root error ~char 1300-2500 (tok ~400-650): "the vertical axis is time, and the horizontal axis is distance".
- P1 731 gap38.0: "Wait, perhaps the graph is time on the horizontal axis and distance on the| vertical axis. But the Asymptote code says..." base raises the right reading then rejects it. E. rl_top junk (no hold), base_top ' vertical'. next both ' vertical'.
- P2 1286 gap31.7: re-reading asy loop "for each i from 1 to |7". C(D). rl_top averages/speed, no hold. next '7' both.
- P3 1074 gap26.0: "So if she ran 1.25 distance in 4.|5 time, then speed is 1.25/4.5" first speed computed with swapped axes. E. no hold either. next '5'.
## 20 (labelled slip; really misread "(1+2i)6-3i" as (1+2i)^6-3i from token ~15; gold 6+9i, base 117+41i)
- P1 13097 gap40.4: after "\boxed{117 + 41i} \" -> ")<eos>". F. rl_top has 'Wait' (3rd), base none. next ')' both.
- P2 4099 gap38.3: binomial terms "Term5 (k=|5): ...32i^5=6*32*(-i)=-192i" a real local slip (i^5=i) right after the peak, causes the "discrepancy"; not the root error. E(local). rl_top junk, base ' subtract'. next '5'.
- P3 7965 gap30.0: redoing z^3 step by step, correct. C(D). rl_top junk. next '3'.
## 36 (gold 3,5,7; base 5). Error char ~1340 (tok ~560): "[2(x-5)]^3 ... First compute 2(x-5)^3 ... Multiply by 2" (8 dropped).
- P1 1275 gap22.2: recheck of (x-7)^3 expansion "...-343.| Correct." C(D). rl_top has ' Wait' 4th; base none. next ' Correct' both.
- P2 1563 gap21.8: "...only one real root, which is x=5.\n\n|**Answer:** 5". F. both tops have Wait; RL next 'Wait' (hold-on output), base '**'.
- P3 1207 gap21.7: recheck (x-3)^3 expansion. C(D). both tops Wait. next ' ='.
## 46 (gold 6; base 12). Error char ~1345 (tok ~513): arg of (-1+i√3)/2 "is -π/3 or 5π/3" (true 2π/3) -> roots e^(5πi/6), e^(11πi/6).
- P1 3169 gap28.5: "the smallest positive integer n is 12.\n\n|**Final Answer** \boxed{12}". F. both tops ' Wait'. RL next 'Wait', base '**'.
- P2 983 gap23.9: listing arg/(2π): "(5π/3)/(2π)| = 5/6" list holds wrong 5/12, 11/12; first time denominators 12 appear. U (downstream, first use of 12). rl_top Wait, Hmm; base has ' Wait' 2nd. next ' =' both.
- P3 1799 gap20.6: tests n=6 (the gold) and rejects it: "5π/6, which is 50 degrees ... So 5π/6 is not a multiple of π/3.| Wait, but in n=6..." E (wrong value used to reject gold). rl_top Wait first; base ' similarly'. RL next ' Wait', base ' Similarly'. (base text itself wrote ' Wait' next.)
## 60 (gold (6,31,-1); base (718/53,543/53,-553/53)). Error char ~3520 (tok ~1378): "-162x² ... +99x² ... = (37x² +190x -54)" (true -63x²).
- P1 4050 gap35.8: solving wrong system "p=13 29/53. But 29 and |53 are coprime" U/D. rl_top junk, base '53'. next '53'.
- P2 5553 gap25.9: after boxed wrong triple, before "**Final Answer**". F. both tops Wait. RL next 'But', base '**'.
- P3 4696 gap22.3: "So this is the correct answer now. Therefore, the ordered triple is (718/53, |543/53" F. rl_top junk, base '543'. next '543'.
(From here: E1 = first error or first use, strict; Er = restatement of the wrong value / separate local slip; D = downstream, local step fine.)
Retro labels: 4:P1 Er,P2 C(D),P3 E1(first use). 20:P1 F,P2 Er(local slip),P3 C(D). 36: C(D),F,C(D). 46: F,U(D),Er(rejects gold with wrong value). 60: U(D),F,F.
## 62 (gold 4; base 2). Error char ~2050-2400 (tok ~680-780): "A^T A is [2*2 + 0*3, ...] = [4,0;0,4]" (true [4,6;6,13]). Note 4th peak pos 700 (gap 20.1) is right at the error.
- P1 1142 gap34.2: generic singular-value formula "...= |0. But in our case, A^T A is diagonal with entries 4 and 4". U (wrong value restated right after). rl_top NULL/determinant/entries/transpose, no hold. next '0'.
- P2 854 gap23.8: "Therefore, the minimal C is 2.\n\n|Alternatively" first commit to wrong answer, ~75 tok after error. E1. rl_top has Wait (6-8), base none. RL next 'But', base 'Alternatively'.
- P3 1694 gap22.2: "So yes, C=2. Therefore, the answer is 2.\n\n|**Final Answer**". F. both tops Wait. next '**' both.
## 64 (gold 35/64; base 35/128). Root error char ~8000 (tok ~2885): misrecalled "sin^7 x = (35 sin x - ...)/128".
- P1 8302 gap31.7: mid-list "k=5: i/(128) cos3x\n\nk=|6" inside a derivation that dropped binomial coefficients (leads to "this can't be right"). U (D, mid-enumeration). rl_top junk, base ' expansion'. next '6'.
- P2 13192 gap26.6: same kind of list "Term k=|6". U (D). rl_top junk. next '6'.
- P3 10907 gap26.3: "(2i)^7 = |128(-i) = -128i" correct. C. rl_top junk, base '128'. next '128'.
## 71 (gold 2516_8; base 1252). Error char ~700-900 (tok ~250-320): mis-copies 10101001110 as 10 digits "1 0 1 0 1 0 0 1 1 0".
- P1 2816 gap34.4: base is listing groups that give 2516 (the GOLD) "Group |2:0 0 1 →1 ... So the octal number is 2516". C (at gold, later abandoned). rl_top junk, base ' binary'. next '2'.
- P2 4928 gap26.4: listing bits "Bit 7:0\n\nBit |6:0" of the mis-copied 10-bit number. Er (restates misread). rl_top junk. next '6'.
- P3 4315 gap24.4: "octal number is 2 1 3, which is 218 in octal ... that would be |2*64=128" local slip (213->218, digit 8). Er. rl_top numbers ('218'), no hold. next '2'.
## 97 (reached gold east, then West). "West" first appears char 5744; the math-coordinate argument (-90 ≡ 270 = West) recurs to the end.
- P1 2519 gap27.3: "rotating -90 degrees (clockwise) takes her to 0 - |90 = -90 ... 270 degrees ... West" the exact wrong argument that wins at the end. Er. rl_top junk, base '90'. next '90'.
- P2 9824 gap23.7: "\boxed{West|}" F. no hold in either top-8 (eos). next '}'.
- P3 7407 gap15.3: "90 degrees clockwise: East or West? ... But in| standard compass directions, East is 90" U (confusion zone, next statement correct). no hold. next base ' reality', rl ' the'.
## 101 (gold 850; base 1700: sums 10 roots instead of 5 pairs). First "\sum_{k=0}^9" at char 9829.
- P1 3530 gap32.2: "So, the sum we need is: \sum_{k=0}^9 1/(x_k x̄_k) = \sum_{k=|0}^9 [170 - ...]" exactly the root error. E1. No hold in either top-8; base_top ' pair',' pairs',' conjug'; rl_top ' conjug',' angle'. next '0'.
- P2 7981 gap31.1: cos list with slips ("k=7: cos(15π/10)= -cos(π/10)", "k=8: cos(17π/10)= -cos(3π/10)") then "k=|9"; base itself writes "Wait, this seems inconsistent" 12 tokens later. Er (local slip). no hold in top-8 (' sum'). next '9'.
- P3 2463 gap29.1: uses slip "168|x|² -13 Re(x)+1" (true -26 Re(x), slip ~65 tok earlier): "168(t² + s) -13t +1 = |0". Er (local slip, dead-end branch). no hold. next '0'.
## 137 (gold 204_5; base 149_5). Error char ~950-1100 (tok ~300-350): reads "413_5" as digits 4135 (=541) and "2_5" as 25 (=11).
- P1 1195 gap30.2: second approach, base-5 long division with divisor 2: "2*2=4 (base |5)". C. no hold. next '5'.
- P2 4377 gap28.3: "Therefore, the answer should be 149 base |5." F. no hold (conversion words). next '5'.
- P3 1565 gap21.6: "Let's recall that in base |5, the digits must be less than 5" C(D). no hold. next '5'.
(All three 137 peaks sit on the token before "5" after "base ".)
## 159 (gold 3.21; base 3.2). Slip char 1499 (tok ~570): "b + c = 1.3 + 1.91 = 3.2". No top-3 peak near it.
- P1 64 gap20.3: opening "recalling how completing the| square works". C. rl_top junk, base ' square'. next ' square'.
- P2 2220 gap14.6: "the final answer is 3.2.\n\n|**Final Answer**" F. both tops ' Wait' first. next '**' both.
- P3 1543 gap13.8: musing about a calculus cross-check "But since the| problem asks". C(D). no hold. next ' problem'/' question'.
## 176 (gold .0000672; base 0.00000672). First error char 2544 (tok ~925): "672 divided by 10^7 is 0.00000672"; text flips between the two values for 7,000 tokens.
- P1 3063 gap31.7: long division after a local slip "312,500 *0.7=219,375" (true 218,750) ~40 tok earlier; "(312,500*0|.1=31,250)". Er(local slip). no hold; rl_top ' decimal', base ' terminating'. next '.'.
- P2 2637 gap30.0: "672 divided by 10^7 is a coefficient ... 6.72 ... 6.72 * |0.0000001 = 0.000000672" a wrong step at the peak. Er. rl_top junk, base ' fraction'. next '0'.
- P3 7385 gap29.4: sets up 21 ÷ 312,500 "312,500 is larger than |21". C(D). rl_top junk, base '21'. next '21'. (offset ambiguous: phrase occurs twice)
## 222 (gold 54; base 18). Diagram scaling muddle; correct facts in hand (diagram ABC area 0.5, factor 12, diagram CDE area would be 4.5 -> 54).
- P1 5474 gap31.0: final write-up "(x - 4, y) = k(a, |12)" in a wrong coordinate frame. U(D). no hold (' height',' vector'). next '12'.
- P2 5402 gap25.6: same write-up "(a, 12) - (0, |0)". U(D). rl_top junk. next '0'.
- P3 3942 gap20.3: "Therefore, in the diagram, area CDE is 6 (original diagram area) but| scaled up becomes 6 * 12 = 72? Wait, maybe not." wrong claim (diagram CDE area is 4.5). Er. rl_top has ' wait',' Wait'; base_top has ' wait' (8th). RL next ' wait', base ' in'.
## 242 (gold 32,348; base 32772). Errors: Taylor slip "(0.2985)^3 = 0.266612463" (true 0.0266) char ~4300; misremembered "(1.01)^30 ≈ 1.34885015241" (true 1.34785) first at char 5446 (tok ~1970); final box 32772 vs own working 32,372.
- P1 2512 gap32.2: "From some sources, (1.01)^30 is approximately 1.34885015241 ... 24,000 * 0.008 = 192\n24,000 * |0.0008" multiplying by the misremembered constant (restated 60 tok earlier). Er. no hold; rl_top ' precise',' precision',' remember'; base_top ' Express'. next '0'.
- P2 1326 gap30.6: "(0.2985)^3 = 0.266612463 / Divide by 6: ~0.0444 / Add to previous: 1.3432 + |0.0444" ~30 tok after the Taylor slip. E1(local slip). rl_top junk, base ' investment'. next '0'.
- P3 1478 gap28.3: "24,000 * 0.0006 = 14.4\n\nSo, |24,000 * 1.3876" first use of the wrong 1.3876. Er. no hold (numbers). next base '24', rl '0'.
## 272 (gold 1030; base 1130). Misread char ~560-700 (tok ~125-160): 'the repeating part is just "311," three digits ... So x = 0.1313131313...'. *** best example ***
- P1 815 gap19.6: "Therefore, the answer is 131 + 999 = 1130.\n\n|**Final Answer**" F. both tops Wait (rl also Hmm). RL next 'Wait', base '**'.
- P2 138 gap18.4: 'the repeating part is just "311," three digits. Let me write that down.\n\n|Let me denote x = 0.1331... So x = 0.1313131313...' at the misread. E1. rl_top [' Let',' Wait','Let','Wait',' let',' First',' wait','First']; base_top [' Let',' let','Let',' denote',' lets','let',' letting',' First']. RL next 'The', base 'Let' (ordinary both).
- P3 598 gap13.6: "So a + b = 131 + 999 = 1130.\n\nWait, let| me check my steps again" F (first commit). rl_top has ' hold','Hold',' Hold'; base ' me',' check'. next ' me' both.
## 279 (gold 7π; base 4π). Error char ~5806 (tok ~1742): "the largest area is between 4 and 6 (20π), the smallest is the innermost region ... 16π" while Z = 13π is smaller.
- P1 1043 gap21.6: "So from 5 to 6 is part of the annulus between 6 and |7? Wait, no." local mis-statement, base self-corrects 2 tokens later. Er (local, self-corrected; before the root error). rl_top ' Wait' first; base_top JUNK (reverse of usual). next '7' both.
- P2 2416 gap18.8: "- The annulus between |6 and 7, label Z" correct listing. C(D). no hold (' radius'). next '6'.
- P3 3036 gap17.3: speculative other reading "X:4π Y:21π Z:17.25π Then the largest area is Y,| and the smallest is X" abandoned branch. U. no hold. next base ' smallest', rl ' '.
## 372 (reached 90, then 75). 75 comes from x = 25, the solution of "sin 2x = sin(100 - 2x)" (char ~26700-27050); "angle BAC = 50 + 25 = 75" char 28686.
- P1 5722 gap40.4: Law of Sines from diagram coordinates "a / sin A = |2R". C. rl_top ' circumference',' circum',' BA' no hold; base ' angle'. next '2'.
- P2 7725 gap36.8: "Solve case 1: 2x = 100 - 2x + 360k, 4x = 100 + |360k, x = 25 + 90k" the step that yields the wrong x = 25. E1. rl_top junk (' unfavor',' prefixed'), base '360'. next '360'.
- P3 5265 gap34.3: computing AD from coordinates "sqrt[(10 - |8.2635)^2" correct. C. no hold (rl '8'). next '8'.
## 385 (gold 22; base 23). Error: rounds each amount before subtracting (91.46->91, 113.64->114). First "$91" char ~800 (tok ~270).
- P1 720 gap24.8: "So the answer is 23 euros more.\n\nAnswer:| 23" F. no hold in top-8 (eos, boxed). next base ' ', rl ' \\'.
- P2 349 gap13.0: redoing 150/1.64 "0.82*91=74.62,| 0.82*92=75.04 ... that's 91 pounds" ~80 tok after first rounding. E1 (weak). no hold (' subtract'). next ' which' both.
- P3 4 gap12.9: "Okay,| let's see" opening. C. no hold. next ' let'/' so'.
## 389 (gold √21/5; base 1). Misread char ~200 (tok ~50): "the asy code mentions a right angle at T" (it is at S).
- P1 1410 gap24.5: re-reading coordinates "R is at (2, sqrt(|21))" correct copy. C(D). rl_top junk, base '21'. next '21'.
- P2 4063 gap22.9: after "\boxed{1}\n" before "\]<eos>". F. no hold in top-8 (rl_top has ' Unsure' 7th). next '\\' both.
- P3 3499 gap15.4: "Therefore, the answer is 1 ... the hypotenuse RS is sqrt(21), but the problem states sin R = |2/5. Therefore, the figure might not be to scale" dismisses the diagram, restates 1. F. rl_top junk, base ' coordinate'. next '2'.
## 396 (gold 2; base 8). Misread char ~1150-1400 (tok ~330-400): 'the gray piece is the quadrilateral ... So the gray piece is a square' (it is the triangle (2,0),(4,2),(4,0); "e" is a different piece).
- P1 921 gap24.2: tests the gray triangle as a square "The diagonals of a square should be equal.| But in a quadrilateral..." Er (misread in use). rl_top [' here',' Wait',' wait',' Here',' Hmm',' But',' but','Wait']; base_top has ' Wait' 7th. RL next ' Wait', base ' But'.
- P2 5997 gap23.8: "Take points A(2,0), B(4,2), C(|4,0). The area is half the cross product" computes the GOLD value 2 (later discarded). C. no hold (' squares',' subdiv'). next '4'.
- P3 2356 gap16.1: "But a square must have all sides equal and all angles 90 degrees.| In this case" Er (misread in use). no hold (' here',' however'). next ' However' both.
## 403 (gold 3; base 1). Misread: compares digits position by position (1556_7 vs 1165_8) instead of shared digits. First at char ~3700-4100 (tok ~1350-1450).
- P1 2168 gap34.0: "Hence, the answer is 1.\n\n|**Final Answer**" F. both tops Wait first. RL next 'Wait', base '**'.
- P2 1867 gap28.5: "So only the first digit is same. Hence, answer is 1.\n\n|But wait" F. both tops have Wait (RL first, base 4th). RL next 'Therefore', base '**'.
- P3 1698 gap24.4: "the number of common digits is 1.\n\n|Wait, but before I finalize" F. both Wait first. RL next 'Wait', base 'But'.
## 419 (gold (-7,16,5); base (0,30,-30)). Slip char ~1100 (tok ~345): second cross-product component written "-v3 + 5v1" (true -v3 - 5v1), which makes the system look uniquely solvable.
- P1 1034 gap31.9: verifying (0,30,-30) "Equation 2: 5v1 - v3 = ... Correct.\n\nEquation |3 ... So, that works. But wait, the problem says infinite number" F (commit+check of wrong vector). no hold; rl_top ' constraints',' uniqueness'; base_top ' magnitude'. next '3'.
- P2 1710 gap31.4: "Hence, the answer is \boxed{(0,30,-30)}.\n\n|But let me just make sure" F. both tops Wait. RL next 'Wait', base '**'.
- P3 377 gap22.0: "(2v3 + 5v2, -v3 + 5v1, v2 - 2v1) ... setting up the equations: 1. 2v3 + |5v2 = 90 2. -v3 + 5v1 = 30" ~35 tok after the sign slip. E1. no hold (' scalar',' vector'). next '5'.
## 438 (gold 4; base 7). Slip char 1561 (tok ~520): "0.274 ... the last nonzero digit is 7" (reads the middle digit). No top-3 peak near it.
- P1 1082 gap26.1: incoherent tangent "since d/5^k + d/2^k = integer ... then dd/5^k| + dd/2^k must be integer". U. no hold (' might',' would'). next base ' +', rl ' would'.
- P2 1189 gap18.3: "if I think of 137/500 as (100 + 38 +1)/500| = ... = 0.278? Wait, that contradicts previous results" local slip (100+38+1=139), base catches it 30 tok later. Er(local). rl_top [' wait',' Wait',' but',' maybe',' perhaps',' somehow',' which',' Hmm']; base_top [' which',' split',' but',' divided',' Split',' equals',' simpl',' splits']. next base ' =', rl '.'.
- P3 2779 gap14.2: write-up "\frac{100 + |37 + 1}{500} = ... = 0.276. However, this split was incorrect" (100+37+1=138). Er(local). rl_top junk, base '37'. next '37'.
## 439 (gold x^8+x^7+...+1; base alternating signs). Wrong quotient from char ~958 (tok ~336). Text degenerates into run-together garble near token 9,700.
- P1 9702 gap41.0: garbled text "knowledgereazurebearis;thegasteblauburtower ... (x+1)(x^2 -x +1)(x^7 -x^6 +...-x^|2 +x -1)=x^9 +1" false factorisation inside garble. U (garbled). no hold (' division',' supply',' correctly',' correctness'). next '2'.
- P2 2168 gap36.9: test division of x^3+1 by x-1: "Multiply (x -1) by |1: x -1. Subtract: (x +0) - (x -1) =0 +1. So remainder is 1" slip 15 tok after peak (drops the +1; true remainder 2). Er(local). rl_top junk, base ' remembering'. next '1'.
- P3 3889 gap28.4: synthetic division gives "x^2+x+1, remainder 2 ... (x-1)(x^2+x+1) = x^3-1. So discrepancy here. But original polynomial is x^|3 +1" sees a discrepancy that is none (forgets the remainder). U. no hold (rl '3',' cube'). next '3'.
## 458 (gold 41; base 45). Misread char ~621 (tok ~176) onward: "N must be composite because normally they can split" (problem: this week N cannot be split, so N prime).
- P1 1738 gap19.5: "\boxed{45|}$" F. no hold. next '}$' both.
- P2 938 gap14.1: "So N is composite, and N+2 is prime. So possible N's include 9, 15, 21, etc. But since the| problem says" restates the misread 30 tok earlier. Er. no hold (' problem',' number'). next ' problem'/' number'.
- P3 1359 gap11.9: 'Let me re-read the problem. "Between 30 and 50 students showed up..." So N is in 30-50.\n\n|We need N composite and N+2 prime.' Er (restates misread right after re-reading). rl_top [' Wait',' wait',' So','Wait',' Ah',' Earlier',' Also',' Hmm']; base_top [' usual',' Wait',' Also',' Usually',' wait',' Then','Wait',' So']. next base '"', rl 'So'.
## 466 (gold 8π; base 9π). Error char ~8945-9155 (tok ~3300-3325): includes k=4, θ = 9π/9 = π (z = -1, which it had excluded) in the list of roots.
- P1 2127 gap30.3: "polynomial is (1 + z^9)/(1 + z) = |0. ... Denominator 1 + z ≠ 0, so z ≠ -1" correct (the exclusion it later forgets). C. no hold (' root'). next '0'.
- P2 3370 gap22.8: "k=7: 15pi/9 = 5pi/3\n\nk=|8: 17pi/9\n\nSo, θ's are: ... pi ..." ~50 tok after the wrong inclusion. E1. no hold (' sum','θ'). next '8'.
- P3 3322 gap22.1: "k=3: 7pi/9\n\nk=|4: 9pi/9 = pi" exactly the wrong inclusion. E1. no hold; rl_top ' angle','θ',' theta'; base_top ' root'. next '4'.
## 491 (gold 64; base 96). Misread: shoes get 3 options (none/regular/clown) although shoes are required. "neither" first at char 4925 (tok ~1290); "Shoes: 3" at char ~8100.
- P1 76 gap33.8: restating the parts list "2 sets of lips, and |2 pairs of shoes" correct. C. rl_top junk, base ' optional'. next '2'.
- P2 1890 gap27.9: 'does that affect the shoes? The problem says "Note that Mr.| Potato Head can be bald"' the shoe confusion, ~120 tok before "Shoes: 3 (none, regular, clown)". Er (weak). rl_top junk-ish (' potato','’s',' punishable'), base ' Potato'. next ' Potato'.
- P3 13 gap23.5: "Tom has this Mr.| Potato Head" opening. C. rl_top junk. next ' Potato'.
## 497 (gold 7/2; base 13/4). Error: vertex (1.5,1.5) dropped from the list: "(1.5,0.5) -> (1,2)" first at char 8182 (tok ~3000); shoelace on 7 vertices.
- P1 6175 gap41.4: shoelace re-run "x7*y8 - x8*y7 = ... = |0" mid-list; the wrong-vertex term is 5 lines (~95 tok) above. U(D). no hold (rl '0',' zero'; base ' sum'). next '0'.
- P2 6640 gap31.7: write-up "Starting from (0, |0)". C(D). no hold. next '0'.
- P3 3872 gap30.6: "3. (1.5, 0.5) 4. (1,2) ... Term3: 1.5*2 - 1*0.5 = 2.5\n\nTerm4: 1*2 - |0*2" one line after the term that uses the wrong neighbour vertex. Er. no hold (rl '0'). next '0'.
## 485 (gold 13; base 19). Misread char ~4100-4500 (tok ~1350-1500): treats the task as a Hamiltonian cycle (adds the closing leg): every route sum has 4 legs.
- P1 3390 gap43.3: "2. B-A-D-C: 6 + 5 + |4 + 5 = 20" (path is 15; the +5 is the return leg). Er (misread in use, mid-list). no hold (rl '4',' four'; base ' distance'). next '4'.
- P2 3456 gap37.9: "5. B-D-A-C: 3 + 5 + |6 + 5 = 19" same. Er. no hold (rl '6'; base ' BD'). next '6'.
- P3 3172 gap23.3: "Sixth permutation: B-D-C-A: |3+4+6+6=19 (true path 13 = GOLD) ... minimal total distance is 18? Wait, how?" Er: this very line is the gold route with an extra leg. no hold (rl '3','19','18'). next '3'.

# Controls (group both, T1; first 8: 0 25 50 75 125 150 175 200), top-3 peaks
fin = final answer or the paragraph break before it; copy = mid-expression/mid-phrase copy token; calc = middle or end of a calculation step.
- 0: P1 497 break before "Answer: (3, π/2)" fin (rl_top Alright/boxed). P2 439 "final answer is (3, π/2|)" fin. P3 187 "So the| angle" calc.
- 25: P1 3583 gap38.7 "(n + 2)(n - 1) = |0" copy, rl_top junk. P2 2295 gap35.0 after "\boxed{-2, 1}.\n\n" fin, both tops Wait, RL next 'Wait' (answer is RIGHT). P3 2499 after boxed answer, before **Final Answer** fin, both Wait.
- 50: P1 216 gap33.2 "all eight bags have the| same" copy, junk. P2 1217 after "**203**.\n\n" fin (rl boxed/Step). P3 336 "y must be at| least" copy, junk.
- 75: P1 914 break before **Answer** fin (rl ' Both'; RL next 'Both'). P2 706 "the answer should be 11/36|." fin. P3 562 "6 + 6 - 1 = 11| favorable" calc.
- 125: P1 87 "(⌈3.|6⌉)²" copy. P2 1379 break before final line, fin, rl_top 'Wait',' Wait' first, base none. P3 945 "ceiling of 3.|6" copy, junk.
- 150: P1 1085 gap35.8 and P2 740 gap35.3 "f(4, 1) = f(3, f(4, |0))" copy, junk. P3 2545 break before **Final Answer**, fin, both Wait, RL next 'But'.
- 175: P1 1572 "m= m0 + t*d ⇒| -100 + t*4" calc, rl_top wait/Wait. P2 443 "12*(8 -k|)" calc, rl hmm/Hmm/Wait/Oops, base also hmm. P3 1337 "|36 -(-2)|]=38" calc, rl wait first; base 'Wait' 4th.
- 200: P1 765 "Answer:| 40 daps" fin. P2 328 "= 14 * 3 baps| = 14 * 5 yaps" calc. P3 659 "42*(5)/3| = (42/3)*5" calc, rl has hmm/Hmm.
Control tally: top-1 fin 3, copy 4, calc 1; top-3 fin 10, copy 7, calc 7 (n=24).

# Tallies (30 failure problems, 90 peaks)
E1 (first error / first use, within ~100 tok): top-1 1, top-3 10 (9 events; 466 P2+P3 are one event).
Er (restated wrong value, misread in use, or separate local slip): top-1 7, top-3 26.
at_error = E1+Er: top-1 8, top-3 36. F: top-1 7, top-3 20. C: top-1 8, top-3 21. U: top-1 7, top-3 13.
Readouts: hold-on word in RL top-8: 22/90 (control 8/24). Also in base top-8: 16 of those 22. RL-only: 6/90 (20P1 F, 36P1 C, 62P2 E1, 272P2 E1, 279P1 Er, 438P2 Er); control 3/24.
RL top-8 = junk fragments (>=2 of brane/udence/RODUCTION/unfavor/prefixed/...): >=23/90 (top-1 8/30); control 6/24. Among gap>=30 peaks: failure 32, hold-on in RL top-8 only 3, junk >=10.
RL next-token top-1 is Wait: 9/90 (6 F, 3 Er); control 1/24 (25 P2, a right final answer). Base next-token hold-on: 0. Next tokens identical: 67/90, control 18/24.
Chance of landing in a 120-token window per peak: mean 3.6%, median 2.3% of positions; E1 observed 10/90 = 11%.
Data oddities: U+FFFD in `before` where multi-byte characters (≈, ⌈) are decoded token by token (81 of 590 T1 peaks); peaks in the last 2-5 tokens of the text (5 failure problems: 20, 97, 385, 389, 458); 439 text is garbled near token 9,700 (base output itself); offsets of before+written_next matched T1.jsonl text at every checked non-final peak.
