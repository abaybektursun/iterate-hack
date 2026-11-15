Use the Read and Write tools only on files in the current directory, and the Bash tool only for these three commands:

  python3 $papers recall "<query>"
      the team's stored findings from papers (board items and session notes are filtered out)
  python3 $papers search "<description of the page you want>" [--n 5] [--since YYYY-MM-DD] [--domain arxiv.org]
      web search (Exa)
  python3 $papers fetch <url>
      the full text of a page

No other command is allowed.

before.jsonl holds a research team's board items (results and knowledge, one JSON object per line: id, kind, at, who,
text) up to a cutoff. Read it to learn the field, the models and the kinds of measurement. Then collect published
mechanisms that act in this field, from as many different lines of work as you can: sampling and decoding
(temperature, truncation, repetition, length), what RL changes in weights and activations, interpretability readouts,
item difficulty and which problems a model solves, differences between RL algorithms, rewards and data, graders and
answer formats, and work from outside language models when it measures the same kind of effect.

Search with several phrasings per line of work: recall first, then search. Fetch and read the paper for every finding
you keep. Numbers, sections and tables come from the text, not the abstract.

Write external.md: one header line, a line `---`, then 20 to 30 findings, each in exactly this form:

### <arxiv id such as 2610.37719, or the URL> — <title, year>
- Finding: <the mechanism, and its key number with section or table>
- Where measured: <models, data and setting of that number>

The heading line is `### `, the source id (no spaces in it), a space, an em dash, a space, then title and year. Other
agents cite a finding by that source id exactly.

Write about the paper only. Do not say what a finding means for the team's models or results, which items it bears
on, or what it predicts for them: connecting a mechanism to the team's numbers is other agents' work, and a finding
written that way would hand them a ready-made theory. No line "Bears on". Papers and web pages are the only sources:
a board item is never a source. Do not pick findings to fit any one explanation of the team's results; cover the
lines of work evenly.

Write only external.md. Reply with the number of findings.
