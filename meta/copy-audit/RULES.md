# What counts as a writing issue on this site

The reader: an intelligent person who was not in the room. They may know machine learning in general, but they do
not know this team's work, its labels or its files. English may be their second language. They scan first (people
read about 20 % of the words on a web page) and read closely only what the scan made them want.

Each rule has a code. Report an issue only under a code, and only when you can say what the reader cannot do
because of it (cannot tell what was measured, has to read twice, has to guess a meaning, stops trusting the page).

## Decoding: the reader has to work out what a word stands for
- D1 Team label never explained where it is used. A name the team made up during the work ("Base + cue", "hard328",
  "restart", "cap hit", "the dial", "Think-SFT", a result id, a branch, a grader version, a file path) shown to the
  public without saying what the thing is at first use on that page.
- D2 Field term or abbreviation not explained at first use on the page (RL, SFT, top-p, residual stream, bootstrap).
  A page for researchers may keep the term; it still says once what it means.
- D3 A word that stands in for an explanation. Metaphor, slang, idiom, invented phrase or figure of speech where a
  literal phrase exists ("regime escape", "good ol' hustle", "real estate in the context", "maxxing").
- D4 Compressed phrase: stacked nouns of 4 or more words, dropped articles or verbs, telegraphic fragments, arrow
  chains, symbols in place of words, "X of Y right" style shorthand that needs the unit and the thing counted.
- D5 One thing with two names, or one name for two things, on the same page or between pages (base / Base / base
  model / untrained base; cut off / cap hit / unfinished).
- D6 Unclear reference: "it", "this", "that model", "the edit", "there" where the reader cannot tell which thing.

## Sentences
- S1 More than one idea in a sentence, or a sentence over about 25 words that a reader must parse twice. Do not
  report a long sentence that reads easily. Do not ask for choppy text.
- S2 The main point is not first: in the sentence, in the paragraph, or on the page. The reader who reads only the
  first sentence of a block should get the fact that matters and its number.
- S3 Hard word where a common one says the same ("utilise", "leverage", "prior to", "in order to").
- S4 Passive or nominal construction that hides who did what ("a comparison was performed" for "we compared").
- S5 Grammar, spelling, punctuation, article or preposition error; inconsistent spelling (US and UK mixed),
  inconsistent number and unit format ("82.0 %" and "82%"), inconsistent capitals.
- S6 Hedge or filler that carries no information ("essentially", "basically", "it is worth noting that").

## Numbers and claims
- N1 A number without what it counts, its unit, its total (n) or what it is compared with.
- N2 A claim stronger than the evidence stated beside it, or stated with no evidence beside it.
- N3 The result does not say why a reader should care: what it changes, compared with what was known.
- N4 A caveat hidden, missing where the page itself shows one is needed, or so long that it buries the result.

## Voice
- V1 Machine-sounding or selling text: slogans, clipped fragments in a row, punchline sentences, rule-of-three
  lists, "not X, but Y" constructions, rhetorical questions, bold lead-ins on every list line, words that praise
  the work ("powerful", "novel", "striking", "surprisingly") in place of the number.
- V2 Inside talk: text written for the team or for other agents, not for a visitor (process notes, references to
  "the room", to chat, to a work item, apologies, notes to self).
- V3 Tone that does not fit the page: a joke a newcomer cannot get, or a joke on a page that reports a measurement.
- V4 A title, tile line or heading that names the topic but not the result, where the result fits in the same space.

## Structure for scanning
- T1 Heading or label that does not tell the reader what is under it.
- T2 A wall of text: a paragraph over about 6 sentences, or a list written as a paragraph.
- T3 The same thing said twice on one page.
- T4 A button, link or control whose words do not say what it does or where it leads.

## Not issues
The content of quoted material (model outputs, math problems, quotations from named people, paper titles). Code
comments and Python docstrings: visitors never see them. Visual design. Whether a number is correct: do not check
numbers against artifacts, but do report a sentence whose own numbers contradict each other. A deliberate joke on a
page that says it is a joke is reported under V3 only if a newcomer cannot follow it.

## Severity
- 3: a newcomer misreads the result or cannot tell what the page claims.
- 2: a newcomer has to stop, re-read or guess, and gets there.
- 1: correct and understandable, but slower or less trustworthy than it could be.

## Output
Write your findings to the file named in your brief, one JSON object per line:
{"file": "tools/x.py", "line": 123, "where": "tile line | first sentence | panel 'How it was measured' | label | ...",
 "text": "the exact words on the page, at most 40 words", "code": "D1", "severity": 2,
 "problem": "what the reader cannot do, one sentence", "rewrite": "a plain rewrite that keeps every number and claim, or '' if you would need facts you do not have"}
Report every issue you find, including severity 1 ones. Do not filter, do not merge different places into one
line: filtering happens later in a separate pass. When the same issue repeats many times on a page (a label used
40 times), report its first use and add "repeats": the count. If a page reads well, say so in your final report and
do not invent issues to fill the list. A rewrite must be plain statement, not shorter at the cost of clarity.
