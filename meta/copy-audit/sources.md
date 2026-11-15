## Part 1. Anthropic guidance
A Fable 5.2 guide exists (undated; model announced Nov 9, 2026). Keys: PE = platform.claude.com/docs/en/build-with-claude/prompt-engineering/; F52, F51, F5 = PE + prompting-claude-fable-5-2, -5-1, -5; BP = PE + claude-prompting-best-practices; CC = code.claude.com/docs/en/best-practices.

(a) Prose
1. Fable 5.2 follows style rules closely: "a hard limit such as 'one instruction per sentence, in 20 words or fewer' can make its prose choppy." F52. quoted
2. Recommended report text: "Write for an intelligent but low-context reader… Put the key points in the first few sentences… Do not use a term or abbreviation that you made up during the work… Write mostly in the style of ASD-STE100… keep bullets for lists of separate items." Measured: less dense, fewer semicolons, shorter sentences. F52. quoted
3. "The model treats an instruction that contains 'never' as absolute." Give each rule its scope and reason. F52. quoted
4. Give the reason: the text-to-speech example; "Claude can generalize from the explanation." BP; also F5. quoted
5. "Current ones follow a plainly worded line, and piling on emphasis mostly makes Claude over-apply the rule." CC. Replace "CRITICAL: You MUST…" with "Use this tool when…". BP. quoted
6. "Being readable and being concise are different things, and readability matters more"; shorten by choosing what to include, "not to compress the writing into fragments, abbreviations, arrow chains". F5. quoted
7. "Mannered prose substitutes metaphor and flourish for direct statement… When a literal phrase is available, use it." F51. quoted
8. Say what to do, not what to avoid. "removing markdown from your prompt can reduce the volume of markdown in the output." BP. quoted
9. Examples are "one of the most reliable ways to steer" format and tone: 3–5, varied, in <example> tags. BP. quoted
10. Effort does not change reply length: "Use prompting to change the length and tone of replies." F52. quoted
11. "The vocabulary you built up while working is yours, not theirs"; "If you have to choose between short and clear, choose clear." F5. quoted

(b) Briefs and reviewers
1. Independence: a fresh reviewer "isn't swayed by the reasoning that produced the code"; "Handing the same task to a subagent doesn't make the answer any better." CC. Fresh verifiers "tend to outperform self-critique". F5. quoted
2. Scope the critic: "A reviewer that's asked to find problems will always find *something*." Review against a spec, report correctness gaps, "skip style". CC. quoted. But "only report high-severity issues" may be followed "literally"; ask for all, filter later. PE + prompting-claude-opus-5. quoted
3. A brief needs "an objective, an output format, guidance on the tools and sources to use, and clear task boundaries"; vague briefs caused duplicated work. anthropic.com/engineering/multi-agent-research-system (June 2025). quoted
4. A subagent "doesn't see your conversation history"; restate rules that must reach it. code.claude.com/docs/en/sub-agents. quoted
5. The subagent tool description should say what delegation costs, when it is worth it, and "how to brief a subagent". F52. quoted; a sample brief: not found
6. Output: "report only the failing tests with their error messages" (sub-agents page); a judge as "a single LLM call… scores from 0.0-1.0 and a pass-fail grade" (research post). quoted
7. State the purpose: "I'm working on [the larger task] for [who it's for]. They need [what the output enables]." F5. quoted

(c) Fable 5.x compared with 4.x
1. Fable 5.1 formats less; old anti-markdown blocks "can suppress structure the content needs". F51/BP. quoted
2. Fable 5.1 prose: "sentences run longer and there are fewer paragraph breaks." F51. quoted
3. Compared with Opus 4.8, one brief instruction steers Fable 5; old skills are "often too prescriptive… and can degrade output quality." F5. quoted

## Part 2. Plain English
1. NN/g, 51 users, 1997: concise + scannable + objective text had 124% better usability than promotional text. Concise alone (half the words) was 58% better, scannable 47%, objective 27%. nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/. paraphrased from the page
2. 79% of users scanned; 16% read word by word. Use plain headings, lists, one idea per paragraph. nngroup.com/articles/how-users-read-on-the-web/. paraphrased from the page
3. Users read "at most 28% of the words", probably about 20%. nngroup.com/articles/how-little-do-users-read/. quoted
4. "The first sentence of every paragraph should be the most important." nngroup.com/articles/inverted-pyramid/. quoted
5. "Start by stating your purpose and the bottom line". digital.gov/guides/plain-language/principles/organize ("adapted from PlainLanguage.gov"). quoted
6. GOV.UK: split sentences over 25 words; at most 5 sentences per paragraph; "buy" not "purchase"; explain specialist terms at first use. 80% preferred clear English; experts preferred it more. guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/. quoted
7. "Express only one idea in each sentence"; paragraphs up to 150 words, with a topic sentence. digital.gov/guides/plain-language/writing/clear-short. quoted
8. ASD-STE100 Issue 9 (2025): at most 20 words per instruction sentence, 25 in descriptions; one word, one meaning; noun clusters of 3 words or fewer; at most 6 sentences per paragraph. No measured comprehension gain is cited. en.wikipedia.org/wiki/Simplified_Technical_English. paraphrased from the page
9. Research for wider readers (Ryba et al. 2021, n=170): accessible abstracts against traditional ones scored readability 66.3% vs 44.4%, understanding 57.9% vs 47.9%, confidence 58.3% vs 44.1%. Accessible meant a stated time and place, "we", linking words, no acronyms, no noun stacks, no hedges, 110 words against 230. No difference was detected for second-language readers. frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.714321/pdf. paraphrased from the page
10. "Write for flesh-and-blood human beings who do not know your work." journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005619. quoted

## Part 3. Presenting results
1. "Focus your paper on a central contribution, which you communicate in the title"; "Tell a complete story in the abstract"; "Deliver the results as a sequence of statements, supported by figures". Mensh & Kording 2017, PLOS link above. quoted
2. Objective text was 27% more usable than promotional text; users "detest anything that seems like marketing fluff". NN/g concise article. quoted
3. Short titles that state the result were cited more than titles that state the method (423 articles). revistas.usp.br/clinics/article/view/40132. paraphrased (abstract only)
4. Journals with shorter titles get more citations per paper. doi.org/10.1098/rsos.150266. paraphrased (abstract only)
5. Across 136,615 abstracts, 1% more promotional words predicted 9–14% more citations per year. The study is correlational and not pre-registered; the authors warn that hype may "erode the collective trust in science". doi.org/10.1038/s44271-025-00293-8. quoted
6. Randomized trial, 36 readers: added hype did not change ratings of merit (P>.05). A controlled test of hype against reader trust: not found. peerreviewcongress.org/abstract/the-influence-of-promotional-language-on-evaluations-of-biomedical-literaturea-randomized-controlled-trial/. paraphrased from the page
7. "Only report work you can point to evidence for… state it plainly without hedging." F5. quoted

## Pages I could not open
royalsocietypublishing.org (403), pmc.ncbi.nlm.nih.gov (browser check), asd-ste100.org (403), the agu.org plain-language summary page (403), the Frontiers HTML page (500; I read the PDF), the Paiva full-text PDF (empty).
