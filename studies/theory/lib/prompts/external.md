Use the Read and Write tools only on files in the current directory, and the Bash tool only for these three commands:

  python3 $papers recall "<query>"
      the team's stored findings from papers (board items and session notes are filtered out)
  python3 $papers search "<description of the page you want>" [--n 5] [--since YYYY-MM-DD] [--domain arxiv.org]
      web search (Exa)
  python3 $papers fetch <url>
      the full text of a page

No other command is allowed.

before.jsonl holds a research team's board items (results and knowledge, one JSON object per line: id, kind, at, who,
text) up to a cutoff. Your job: find published mechanisms that could explain its least-explained results.

1. Read before.jsonl. Pick 6 to 10 results the items leave unexplained: surprises, refuted hypotheses, controls that
   did as well as the treatment, differences between settings that no item accounts for.
2. For each, search by mechanism in the field's terms, with several phrasings: recall first, then search. Fetch and
   read the paper for every finding you keep. Numbers, sections and tables come from the text, not the abstract.
3. Write external.md: a short header (one line per unexplained result, with its item ids), a line `---`, then 20 to
   30 findings, each in exactly this form:

### <arxiv id such as 2610.37719, or the URL> — <title, year>
- Finding: <the mechanism and its numbers, with section or table>
- Bears on: <item ids, and what the finding predicts for the team's setting that no item reports>
- Already cited by the team: yes/no

The heading line is `### `, the source id (no spaces in it), a space, an em dash, a space, then title and year. Other
agents cite a finding by that source id exactly.

Papers and web pages are the only sources: a board item is never a source. Prefer mechanisms that make a quantitative
prediction. Include findings that contradict the team's current explanations.

Write only external.md. Reply with the number of findings.
