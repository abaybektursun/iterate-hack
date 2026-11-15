"""From a one-sentence description alone, a blind reader finds a neuron's firings 90.7 % of the time.

The page of one finding, served at /finding/neurons-you-can-describe (view.py serves every tools/finding_<slug>.py)
and reached from its tile on /findings, which ICON draws. The picture is one lit plate. On the left, the blind
description test itself on one of three neurons: the sentence written for the neuron and 8 of its real test snippets;
the reader picks the 4 on which they expect the neuron to fire at the underlined token, then reveals the key and sees
their score next to the blind reader's score on the same neuron. On the right, the test's result from the start: one dot
per tested neuron at its score, 30 neurons that matter for RL against 15 random ones, and chance. A click on a dot shows
that neuron's sentence in the side column. Address: /finding/neurons-you-can-describe#<neuron>/<neuron>=<picks>[r]/...
then /<panel> or /n-<neuron>. The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of
tools/architecture.py (.claude/skills/site-ui/SKILL.md).

    python3 tools/finding_neurons_you_can_describe.py    checks DATA against the artifacts it was copied from
"""
import json
import re

TITLE = "Neurons you can describe"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Can one sentence say what a neuron does?"

# Every number is copied from the artifacts named here. None is typed from memory. The deployed site ships only
# tools/*.py, so the copy is a literal; run this file to compare it with the artifacts.
DATA = {
    "artifact": "studies/cleanneurons/results/describe/attr_top100-01/descriptions_test.json",
    "examples": "studies/cleanneurons/results/describe/attr_top100-01/page_examples.json",
    "density": "studies/cleanneurons/results/describe/attr_top100-01/density_readout.json",
    "run": "studies/cleanneurons/results/describe/attr_top100-01/run.json",
    "commit": "2dd4da7d5b66ae79c2841418085ea12656a26fcc",
    "job": "sameraslan-1114-154532-cdc8",
    "command": "python -m studies.cleanneurons.jobs.describe_neurons --commit 2dd4da7d5b66ae79c2841418085ea12656a26fcc --edit studies/cleanneurons/results/transplant/curve_attr-01/edit_attr_top100.json",
    # The protocol of studies/cleanneurons/analysis/describe_test.py: first10, then heldout10 and random10.
    "test": {"described_from": 10, "snippets": 20, "fire": 10},
    "chance": 0.5,
    "sets": {"selected": {"units": 30, "mean_accuracy": 0.9066666666666666, "ci95": [0.8600000000000001, 0.9466666666666667]},
             "reference": {"units": 15, "mean_accuracy": 0.7133333333333333, "ci95": [0.6000000000000001, 0.8133333333333334]}},
    # density_readout.json: of 100 neurons each, how many are beyond their layer's 97th percentile at more than half of
    # all positions (selected: the 100 with the largest effect; reference: 100 layer-matched random neurons)
    "always_on": {"selected": 44, "reference": 1, "positions": 131397},
    # The 45 tested neurons, by accuracy and then key: key, set (s selected, r reference), accuracy, layer, neuron,
    # pole (+ the strongest positive activations, - the strongest negative ones) and the sentence. One dot each.
    "ring": [
        ["u01", "s", 1.0, 29, 2637, "+", "The period that ends a sentence finishing with a computed number or expression in informal step-by-step reasoning, just before a new sentence such as 'Then', 'Wait' or 'So'."],
        ["u04", "s", 1.0, 19, 10616, "-", "The space right before a number that follows an operator, comma or 'by' ('6 + 12i', 'divided by 9', '2! * 2!') inside a calculation the text is redoing."],
        ["u06", "s", 1.0, 10, 7275, "+", "A hesitation word 'Hmm', 'Wait' or 'wait' starting a sentence right after a period or 'But', mostly just after the problem is restated in the opening reasoning."],
        ["u09", "s", 1.0, 11, 9904, "-", "A content word completing a predicate in plain-English reasoning, most often 'distribute' after 'can'/'Let me', also 'straightforward', 'inverse', 'removed', 'covered' after 'too', 'modular', 'then', 'already'."],
        ["u20", "s", 1.0, 23, 6475, "+", "The word 'problem' in the opening 'Okay, so I have this problem (here where)' right after the question; weaker on 'approach' after 'another' and on 'miscalculation'."],
        ["u22", "s", 1.0, 2, 3032, "-", "The token 'boxed' right after a backslash, when the final answer is given, typically on the line after '**Final Answer**' or after 'is \\'."],
        ["u24", "s", 1.0, 30, 10249, "-", "The sentence-ending period (or '?', ').') after a full statement in informal reasoning, especially when doubt or a next plan follows ('Let me think', 'Wait, maybe', 'So')."],
        ["u25", "s", 1.0, 11, 3547, "+", "'Wait' or 'Hmm' opening a new paragraph, or 'let' after 'but', right after an answer has just been concluded ('the answer is 4'), starting a double-check."],
        ["u29", "s", 1.0, 4, 7613, "-", "The stem 'don' or 'isn' of a negative contraction, right before the apostrophe-t, most often in 'I don't see any mistakes' or 'there isn't' near the end of the reasoning."],
        ["u31", "s", 1.0, 14, 7525, "+", "'Let' (less often 'Wait') starting a sentence right after a doubt, question or tentative answer ('...a mistake in algebra?', 'maybe another way.'), opening a recheck or a different method."],
        ["u33", "s", 1.0, 5, 6372, "+", "The interjection 'Hmm' (capitalized) starting a sentence right after a period that ends a finished computation or a stated answer, as in 'the remainder is 0. Hmm'."],
        ["u34", "s", 1.0, 8, 1033, "-", "The last word of a fixed phrase in prose: 'inverse' after 'multiplicative'/'an', 'step' after 'step by', 'thorough' after 'just to be', 'head' after 'in your', 'proportion' after 'set up a'."],
        ["u37", "s", 1.0, 9, 7587, "-", "The token 'boxed' right after the backslash on the line following '**Final Answer**', and the word 'Answer' inside the '**Final Answer**' header itself."],
        ["u41", "s", 1.0, 11, 7824, "-", "The word 'To' that starts the clean written solution ('To solve the problem, we...') on a new paragraph right after the boxed final answer that ends the reasoning."],
        ["u44", "s", 1.0, 3, 7717, "-", "The token 'boxed' right after a backslash in the '**Final Answer**' block at the end of the reasoning, either directly under the header or after 'is \\'."],
        ["u00", "s", 0.9, 17, 3660, "+", "The space (or linking token) right before a number or symbol being restated from the problem, after 'is', 'by', 'and', 'over', 'with' or '+', as in 'The answer is 3'."],
        ["u02", "r", 0.9, 2, 10779, "+", "The second word-piece of a math word, most often 'els' in 'cancels' (e.g. 'the 3 cancels'), also '-values' after 'y' and 'coefficients' after 'leading'."],
        ["u03", "s", 0.9, 22, 8409, "+", "The space or '{' right before a number operand that follows an operator or relation ('=', '/', '<', 'by', 'and', '\\div', '\\sqrt'), where that number was already stated nearby."],
        ["u05", "s", 0.9, 29, 10229, "-", "An operator or relation token ('+', '=', '\\times', '\\cdot', '>', 'to') right after the first operand in a formal LaTeX-formatted solution, where a number comes next."],
        ["u08", "s", 0.9, 31, 7955, "+", "A comma, colon, '=' or 'and' in the middle of a calculation, right after a number or short phrase, where the next numeric value is about to be written."],
        ["u12", "s", 0.9, 10, 77, "+", "'Hmm', 'Wait' or 'Let' starting a sentence right after a period or question mark in the middle of an arithmetic step or after a tentative answer, opening a recheck."],
        ["u13", "s", 0.9, 9, 426, "-", "The first token of a value written right after '=' or ':' (the space, or the leading digits of a multi-digit number like '990'), or '\\text' in LaTeX."],
        ["u14", "r", 0.9, 29, 5801, "-", "'be' after 'can' or 'can sometimes' in a general remark about a topic ('repeating decimals can sometimes be'), less often 'is', 'as' or 'one' after a general subject."],
        ["u17", "r", 0.9, 19, 1572, "+", "A transitive verb of transformation ('convert', 'express', 'relate', 'divide', 'arranging') right after 'to', 'can' or its subject, before the object it acts on is named."],
        ["u18", "s", 0.9, 5, 10160, "+", "A longer, less common content word ending a phrase in plain-English commentary ('substitutions', 'misunderstanding', 'separately', 'tedious', 'overlap', 'rounded'), or 'boxed' right after a backslash (weak)"],
        ["u19", "r", 0.9, 13, 1240, "-", "A token inside a value being stated for a quantity: the '/' or '}{' of a fraction ('37/8', '11/4'), or the number right after 'is', 'becomes', 'have' or '='."],
        ["u32", "r", 0.9, 14, 6621, "+", "'write', 'down', 'note' or 'formal' inside 'Let me write that (down)', 'Let's note that', 'Let me formalize', and the second 'step' of 'step by step'."],
        ["u36", "s", 0.9, 18, 1045, "-", "The space (or '{') right before a number that follows an operator, '=', comma, 'by' or 'and' inside a calculation, as in '6 + 12i' or 'divided by 3'."],
        ["u40", "r", 0.9, 17, 3970, "-", "The last token (noun, number or comma) of a clause stating a condition or general premise ('if they have coins,', 'when x is 0'), before its consequence."],
        ["u07", "s", 0.8, 10, 86, "+", "'Wait' opening a new paragraph after a blank line, or 'hold' after 'Wait,' or 'but', where the reasoning starts to doubt and recheck its previous step."],
        ["u10", "r", 0.8, 7, 8768, "-", "The word completing a stock phrase that states a general math rule: 'highest power of 2', 'expression inside must', 'greater than or equal', 'the bases', 'linear congr' (weak)"],
        ["u21", "r", 0.8, 4, 4958, "-", "The token completing a predictable continuation: 'quadrant' after 'fourth'/'first', 'equal' after 'less than or', or a three-digit number repeated from the arithmetic just done (weak)"],
        ["u26", "s", 0.8, 14, 7514, "-", "The space before the last number of an expression or phrase ('between 6 and 7', 'x - 1', 'degree 2', 'base 2 of 64'), or 'simpl' in 'which simplifies' (weak)"],
        ["u35", "s", 0.8, 9, 692, "-", "The token 'boxed' right after a backslash inside a prose sentence that states the result, almost always following 'the answer is \\' (often after 'Therefore,')."],
        ["u11", "s", 0.7, 16, 6351, "+", "The space right before a number that was already mentioned, after 'divided by', 'times', 'than', 'of', '+' or a division sign, when a calculation is restated in words."],
        ["u23", "r", 0.7, 10, 5485, "+", "The noun 'terms' (also 'parts', 'power', 'number') right after a modifier naming its kind, as in 't³ terms', 'common terms', 'real parts', 'highest power', 'mixed number'."],
        ["u27", "s", 0.7, 12, 5682, "+", "A short function token inside an ongoing explanation: the space after 'divided by', 'the', 'of', 'should' after 'maybe I', or the '\\[' line opening a display equation (weak)"],
        ["u43", "r", 0.7, 0, 9363, "-", "The plural noun right after 'of', chiefly in 'the number of digits / ways / students' and 'the sum of the digits'; weaker on 'them' or 'these' after 'of'."],
        ["u15", "s", 0.6, 15, 7111, "-", "The token just before the last number of a short standalone equation line (space after '-', 'by', '='), or the '!' plus blank line ending the problem statement."],
        ["u16", "r", 0.6, 11, 1557, "+", "The last word of a compound math term: 'value' in 'place value', 'factors' in 'prime factors', 'part' in 'repeating part', '-coordinate' after 'y', 'digits' after 'sum of its'."],
        ["u28", "r", 0.6, 27, 4956, "-", "The first word of the main statement right after a lead-in such as 'So', 'So,', 'First,', 'Then,', 'the domain is', 'the product of': usually 'the', 'we', 'x' or a number."],
        ["u38", "s", 0.6, 26, 8438, "-", "A connective opening a sentence in informal reasoning ('So', 'But', 'but' after 'Hmm,'), or the comma right after 'Wait', 'So' or 'actually', before the clause itself begins."],
        ["u39", "r", 0.5, 12, 10156, "-", "A token inside the second item of a pair mirroring an earlier one: 'b' in '-(b × a)', the comma in '(-2, 7)', 'A' in 'through A and B' (weak)"],
        ["u30", "r", 0.4, 31, 3455, "-", "'the' (less often 'a', 'is') right after a short connective such as 'In', 'so', 'or', 'then', 'All', starting a noun phrase naming a math object; also ':' before a computation."],
        ["u42", "r", 0.2, 9, 2589, "-", "A remainder or modulus token in modular arithmetic ('mod', '≡', the residue after '≡' or 'mod7 is'), or the repeating digits after a decimal point ('33.333') (weak)"],
    ],
    # Three neurons to try, from page_examples.json: per snippet its id in the test, whether the neuron fires, the text
    # with the marked token between << and >>.
    "seed": 0,
    "units": [
        {"key": "u06", "set": "selected", "layer": 10, "neuron": 7275, "pole": "+", "blind_accuracy": 1.0,
         "description": "A hesitation word 'Hmm', 'Wait' or 'wait' starting a sentence right after a period or 'But', mostly just after the problem is restated in the opening reasoning.",
         "snippets": [
             [0, True, "… an expression x² - 4x + 4.<< Wait>> a second, that looks familiar. …"],
             [3, False, "… possibility that I misread the original problem<<?>> Let me check again. The …"],
             [4, True, "… 3i. Let me write that out properly.<< Wait>>, is the multiplication by …"],
             [5, False, "… an integer k where kⁿ = 2²⁴<<.>> So, essentially, we need to …"],
             [12, False, "… is f(-1) if g(x) = f(x +<< >>1), but in this case, …"],
             [14, True, "… \\( b \\) are positive real numbers.<< Hmm>>, let me think about …"],
             [16, False, "… is 2000 calories. So, the answer is<< >>2000. Answer: \\boxed{2000}<|endoftext|>"],
             [17, True, "… 1 make 2²⁴ a perfect nᵗʰ power.<< Hmm>>, so we need to …"],
         ]},
        {"key": "u23", "set": "reference", "layer": 10, "neuron": 5485, "pole": "+", "blind_accuracy": 0.7,
         "description": "The noun 'terms' (also 'parts', 'power', 'number') right after a modifier naming its kind, as in 't³ terms', 'common terms', 'real parts', 'highest power', 'mixed number'.",
         "snippets": [
             [0, True, "… 15.975. So, 15 and 39/40, since 39<</>>40 is 0.975. So, that's …"],
             [4, True, "… combine like terms. Start with the x^4<< term>>: 3x^4. x^3 term: -12x^3. …"],
             [10, True, "… +36i -15i². Combine like terms: The real<< parts>>: 48 -15i². Since i² …"],
             [15, False, "… since x = 0 and y > <<0>>, it's in the first …"],
             [16, False, "… since in math, fractions are preferred over<< repeating>> decimals. Let me check examples …"],
             [17, False, "… I can write each number as a<< decimal>> and perform the operations, then …"],
             [18, False, "… \\] Thus, the sum of the coefficients<< of>> \\( g(x) \\) is \\( …"],
             [19, True, "… need to break them down into prime<< factors>>. 3 is a prime …"],
         ]},
        {"key": "u42", "set": "reference", "layer": 9, "neuron": 2589, "pole": "-", "blind_accuracy": 0.2,
         "description": "A remainder or modulus token in modular arithmetic ('mod', '≡', the residue after '≡' or 'mod7 is'), or the repeating digits after a decimal point ('33.333') (weak)",
         "snippets": [
             [2, False, "… digit: 5 (after borrowing) - 6. Can<<'t>> do that, need to borrow …"],
             [3, True, "… so sqrt(45) is between 6 and 7.<< Specifically>>, 6.7^2 is 44.89, because …"],
             [7, True, "… θ since it's already in the correct<< quadrant>>. So the final answer …"],
             [8, True, "… be an isosceles triangle. But wait, how<< exactly>> do I calculate the area …"],
             [9, False, "… So that would be 7 units (<<1>> block + 6 girls) arrange …"],
             [12, False, "… then starting from day 3: 3, 6,<< >>9, 12, 15, 18, 21, …"],
             [14, False, "… of each prime factor: \\(2^2 \\times 3<< \\>>times 5\\). - Calculate \\(2^2 …"],
             [18, True, "… days. Therefore, 9*4=36. Alternatively, if she could<< start>> at day 1, but since …"],
         ]},
    ],
}

_S, _R, _T, _A = DATA["sets"]["selected"], DATA["sets"]["reference"], DATA["test"], DATA["always_on"]
_p = lambda v: f"{100 * v:.1f}"  # a share as a percentage with one decimal
LINE = (f"Given only a one-sentence description, a second model sorts {_p(_S['mean_accuracy'])} % of new text snippets right "
        f"(the neuron fires there or not) for the neurons that matter most to what reinforcement learning (RL) changed, against "
        f"{_p(_R['mean_accuracy'])} % for random neurons and {_p(DATA['chance'])} % by chance.")


def _clean(s):
    """Readable text for a snippet: LaTeX delimiters and the end-of-text token removed, a few commands as symbols. The
    marked token itself is never changed. The test readers saw the raw text."""
    s = s.replace("<|endoftext|>", " [end of the answer]")
    s = re.sub(r"\\boxed\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[()\[\]]", "", s).replace("\\times", "×").replace("\\cdot", "·")
    s = re.sub(r"\^2(?!\d)", "²", s).replace("^3", "³").replace("^4", "⁴")
    return re.sub(r"\s+", " ", s).strip(" ") if s.strip() else s


def _shown(text):
    """[before, token, after] of a snippet for the page, the token's leading space kept outside the highlight."""
    a = text.index("<<")
    b = text.index(">>", a)
    tok = text[a + 2:b]
    lead = tok[:len(tok) - len(tok.lstrip())] if tok.strip() else ""
    before, after = _clean(text[:a]), _clean(text[b + 2:])
    return [before + (" " if lead or (text[a - 1:a] == " ") else ""), tok[len(lead):], (" " if text[b + 2:b + 3] == " " else "") + after]


QUIZ = [{**{k: u[k] for k in ("key", "set", "layer", "neuron", "pole", "blind_accuracy", "description")},
         "snippets": [[fires, *_shown(text)] for _, fires, text in u["snippets"]]} for u in DATA["units"]]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
# Not from our run, checked in full text on 2026-11-15: Goodfire, "Neurons as an Interpretable Basis"
# (goodfire.com/research/neurons-as-an-interpretable-basis, 10 November 2026), Table 3: a judge picks the firing snippet
# of a pair, 0.946 over all bands against random text and 0.885 against text of the same expert, 496 neuron poles of
# Qwen3.6-35B-A3B. Detection scoring: Paulo et al., arXiv 2410.13928, Sec. 3.3.1. Batutin
# (andriybatutin.substack.com/p/we-tried-to-confirm-neural-networks, 19 October 2026), on Qwen3-0.6B and 1.7B: labels
# predict the extreme top activations (r 0.26) and not the 1 to 10 % band (r 0.02).
PANELS = [
    ["new", "What is new",
     f"New here: the neurons that matter most for what RL changed in Olmo 3 7B are easier to describe than random neurons of the "
     f"same layers, {_p(_S['mean_accuracy'])} % against {_p(_R['mean_accuracy'])} %.",
     ["The test itself is established: in a study by the company Goodfire, an AI judge given a neuron's description picks the "
      "snippet where the neuron fires, out of a pair with one random snippet, 94.6 % of the time, on 496 descriptions (each of "
      "one sign of a neuron's activation) in a 35B mixture-of-experts model.",
      "Our test follows the same idea, detection scoring (Paulo et al., arXiv 2410.13928): the reader sees only the sentence and "
      f"picks {_T['fire']} firing snippets of {_T['snippets']}.",
      "A study of Qwen3-0.6B and 1.7B (Batutin, 19 October 2026) found that neuron labels predict only the strongest "
      "activations. This test also uses only the strongest."]],
    ["why", "Why it matters",
     f"One sentence is enough for another model to find where the neurons that matter most for RL's change fire: {_p(_S['mean_accuracy'])} % of snippets sorted right on average.",
     ["Many of the sentences describe how the model reasons rather than math: “Hmm” or “Wait” starting a sentence (layer 10, neuron 7275, sorted 100.0 % right), "
      "or the period before “Then”, “Wait” or “So” (layer 29, neuron 2637, 100.0 %).",
      f"{_A['selected']} of the 100 neurons that matter most are active almost everywhere, against {_A['reference']} of 100 random neurons "
      "of the same layers.",
      "These neurons carry only part of what RL changed: copying the 1 % of neurons with the largest effect from the RL model "
      "into the base model recovers 16.1 % of RL's effect (see the finding “RL's change is spread out”)."]],
    ["how", "How we know",
     f"One reader wrote a sentence from the {_T['described_from']} snippets where a neuron fires most. A second reader, the blind reader, given only "
     f"that sentence, picked which {_T['fire']} of {_T['snippets']} new snippets fire; the other {_T['snippets'] - _T['fire']} are "
     "random places in the same texts.",
     [f"Neurons of allenai/Olmo-3-1025-7B: {_S['units']} of the 100 that matter most for RL's change (the 100 that, copied from the RL model into the base model, move its outputs most toward the RL model) scored "
      f"{_p(_S['mean_accuracy'])} % (95 % interval {_p(_S['ci95'][0])} to {_p(_S['ci95'][1])}); {_R['units']} random neurons of the "
      f"same layers scored {_p(_R['mean_accuracy'])} % ({_p(_R['ci95'][0])} to {_p(_R['ci95'][1])}). Picking at random scores "
      f"{_p(DATA['chance'])} %.",
      "Both readers were instances of the language model Claude. The second never saw which snippets fire or which neurons were random.",
      "A score counts every snippet sorted right: a firing snippet picked, or a random one left out."]],
    ["limits", "What it does not show",
     "The test uses only each neuron's strongest firings. A sentence can pass it while the neuron's weaker firings follow no "
     "describable rule.",
     ["The reader that wrote the sentences and the reader that was tested are the same kind of model, so a person might score lower.",
      f"Each sentence describes one side of a neuron: where its activation is most positive or, for some neurons, most negative. "
      f"In all, {_S['units'] + _R['units']} of the model's 352,256 neurons were tested.",
      "The test says nothing about changing the model's behavior with these neurons."]],
    ["run", "How to reproduce it",
     "Run studies/cleanneurons/analysis/describe_test.py prep on the output of the GPU job, have two readers write "
     "descriptions.json and predictions.json, then run describe_test.py score.",
     [f"The GPU job was {DATA['job']} at commit {DATA['commit'][:7]}: {DATA['command'].replace(DATA['commit'], DATA['commit'][:7])}.",
      f"The scores and all {_S['units'] + _R['units']} sentences are in {DATA['artifact']}.",
      f"The snippets on this page are in {DATA['examples']}: 8 of each neuron's {_T['snippets']}, drawn with seed {DATA['seed']}. "
      "python3 tools/finding_neurons_you_can_describe.py checks the page against these files."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab seen from slightly above with five snippets as lines of words, one of them bright: the
# snippet where the neuron fires.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, pick = 2;
  const rows = [[[-.8, -.36], [-.24, .1], [.22, .62]], [[-.8, -.12], [0, .42]], [[-.8, -.46], [-.34, .24], [.36, .7]],
    [[-.8, -.2], [-.08, .3], [.42, .8]], [[-.8, -.5], [-.38, .06]]];  // each row: its words, from and to, in half widths
  let out = kit.slab(a, b, th);
  rows.forEach((words, i) => {
    const v = b * .68 * (2 * i / (rows.length - 1) - 1), lit = i === pick;
    for (const [from, to] of words)
      out += kit.line(kit.at(a * from, v, th / 2), kit.at(a * to, v, th / 2), lit ? 1.4 + .16 * Math.sin(t * .6) : .9, lit ? "lit" : "plain", lit ? 1 : .7);
  });
  return out;
}"""

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the light of tools/architecture.py: one lit glass plate in a dark room, the same object as white
   porcelain with a cast shadow in light. The light comes from the upper left in both. Blue is the reader's own pick and a
   firing token; red is a wrong pick. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34; --on-blue: #fff;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --line: color-mix(in srgb, var(--ink) 12%, transparent); --tap: color-mix(in srgb, var(--ink) 4%, transparent);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c; --on-blue: #080c11;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --tap: rgba(255, 255, 255, .035);
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper); overflow-x: clip;
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
button:disabled { cursor: default; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.page {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 27vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0; height: 100vh; min-height: 820px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 24px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: one plate, swaying a few degrees, with the test on the left and its result on the right */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; align-items: center; justify-content: safe center; padding: 14px 40px 0 0; }
.scene { width: min(100%, 1080px); perspective: 2400px; }
.body { position: relative; transform-style: preserve-3d; }
.back, .plate { border-radius: 26px; }
.back { position: absolute; inset: 0; transform: translateZ(-36px); background: var(--glass-lo); border: 1px solid var(--rim-b); }
.back::before, .back::after { content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; }
.back::before { opacity: var(--glow); box-shadow: 0 0 130px 8px color-mix(in srgb, var(--blue) 20%, transparent); }
.back::after { opacity: var(--shadow); box-shadow: 18px 36px 70px -14px color-mix(in srgb, var(--ink) 24%, transparent); }
.plate {
  position: relative; overflow: hidden; display: grid; grid-template-columns: minmax(0, 1.72fr) minmax(250px, 1fr); gap: 0 36px;
  padding: 22px 30px 18px; border: 1.7px solid transparent;
  background: radial-gradient(120% 120% at 28% 18%, var(--glass-hi), var(--glass) 46%, var(--glass-lo)) padding-box,
              linear-gradient(140deg, var(--rim-a), var(--rim-b) 56%, var(--rim-c)) border-box;
}
.spec { position: absolute; left: -4%; top: -18%; width: 58%; height: 56%; transform: rotate(-20deg); opacity: var(--spec); pointer-events: none;
  background: radial-gradient(closest-side, rgba(255, 255, 255, .12), rgba(255, 255, 255, 0)); }

/* The test */
.quiz { position: relative; min-width: 0; }
.qtop { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; font-size: 13.5px; color: var(--mute); }
.qtop b { color: var(--ink); font-weight: 650; }
.who { text-align: right; }
.sentence { margin: 6px 0 0; font-size: clamp(17px, 1.32vw, 21px); line-height: 1.3; font-weight: 420; font-stretch: 103%; letter-spacing: -.005em; min-height: 3.9em; }
.sentence::before { content: "\201C"; } .sentence::after { content: "\201D"; }
.ask { margin: 8px 0 8px; font-size: 14px; font-weight: 600; }
.ask span { display: block; color: var(--mute); font-weight: 450; font-size: 13.5px; }
.snips { list-style: none; margin: 0; padding: 0; display: grid; gap: 4px; }
.snip { display: flex; align-items: center; gap: 12px; width: 100%; min-height: 38px; padding: 6px 12px; border-radius: 9px; background: var(--tap);
  border: 1px solid var(--line); font-size: 14.5px; line-height: 1.36; transition: border-color .15s ease, background .15s ease, opacity .3s ease; }
.snip:hover:not(:disabled) { border-color: var(--faint); }
.tick { flex: none; width: 18px; height: 18px; border-radius: 50%; border: 1.6px solid var(--faint); display: grid; place-items: center; font-size: 12px; font-weight: 800; color: var(--on-blue); transition: background .15s ease, border-color .15s ease; }
.txt { color: color-mix(in srgb, var(--ink) 82%, transparent); overflow-wrap: anywhere; min-width: 0; transition: color .3s ease, opacity .3s ease; }
.txt mark { color: var(--ink); background: none; font-weight: 640; border-bottom: 2px solid var(--ink); padding: 0 1px; border-radius: 3px 3px 0 0; transition: background .35s ease, color .35s ease, border-color .35s ease; }
.txt mark.gap { padding: 0 5px; }
.snip[aria-pressed="true"] { border-color: var(--blue); background: color-mix(in srgb, var(--blue) 9%, transparent); }
.snip[aria-pressed="true"] .tick { background: var(--blue); border-color: var(--blue); }
.snip[aria-pressed="true"] .txt { color: var(--ink); }
.snip.fires .txt { color: var(--ink); }
.snip.fires mark { background: var(--blue); color: var(--on-blue); border-color: var(--blue); }
.snip.quiet .txt { opacity: .55; }
.snip.right .tick { background: var(--blue); border-color: var(--blue); }
.snip.wrong { border-color: var(--red); background: color-mix(in srgb, var(--red) 8%, transparent); }
.snip.wrong .tick { background: var(--red); border-color: var(--red); }
.snip.miss .tick { border-color: var(--blue); border-style: dashed; }
.snip:disabled[aria-pressed="false"]:not(.fires) { background: transparent; }
.acts { display: flex; align-items: center; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
.act { min-width: 172px; padding: 10px 22px; border-radius: 999px; text-align: center; font-weight: 640; font-size: 15px; border: 1px solid var(--faint); transition: background .15s ease, color .15s ease; }
.act:disabled { color: var(--mute); border-color: var(--rule); }
.act.go { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.act.go:hover { background: var(--blue); border-color: var(--blue); color: var(--on-blue); }
.step { padding: 11px 14px; border-radius: 999px; font-weight: 600; font-size: 14.5px; color: var(--mute); }
.step:hover { color: var(--ink); }
.dots { display: inline-flex; gap: 6px; margin-left: auto; align-items: center; }
.dots button { width: 26px; height: 26px; display: grid; place-items: center; border-radius: 50%; }
.dots i { width: 9px; height: 9px; border-radius: 50%; border: 1.5px solid var(--faint); }
.dots .part i { background: color-mix(in srgb, var(--blue) 45%, transparent); border-color: var(--blue); }
.dots .done i { background: var(--blue); border-color: var(--blue); }
.dots .here i { outline: 1.5px solid var(--ink); outline-offset: 3px; }
.mine { display: flex; flex-wrap: wrap; gap: 4px 26px; align-items: baseline; margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--line); min-height: 40px; font-size: 13.5px; color: var(--mute); }
.mine .v { font-size: 22px; font-weight: 680; letter-spacing: -.02em; color: var(--ink); margin-right: 6px; }
.mine .you .v { color: var(--blue); }
.mine .wait { font-size: 13.5px; }
.key { display: flex; flex-wrap: wrap; gap: 4px 18px; margin-top: 8px; font-size: 12.5px; color: var(--mute); min-height: 20px; transition: opacity .3s ease; }
.key span { display: inline-flex; align-items: center; gap: 6px; }
.key .k-fire { width: 22px; height: 12px; border-radius: 3px; background: var(--blue); }
.key .k-right, .key .k-wrong, .key .k-miss { width: 12px; height: 12px; border-radius: 50%; background: var(--blue); }
.key .k-wrong { background: var(--red); }
.key .k-miss { background: none; border: 1.5px dashed var(--blue); }

/* The result of the test, shown from the start */
.score { position: relative; min-width: 0; display: flex; flex-direction: column; }
.big { margin: 4px 0 0; font-size: clamp(60px, 6vw, 104px); line-height: .98; font-weight: 660; letter-spacing: -.035em; white-space: nowrap; }
.big small { font-size: .5em; font-weight: 560; letter-spacing: 0; margin-left: .08em; }
.blab { margin: 8px 0 0; font-size: 15px; line-height: 1.35; font-weight: 500; max-width: 30ch; }
.strip { margin-top: 18px; }
.strip svg { width: 100%; display: block; overflow: visible; border-radius: 6px; }
.strip svg:focus:not(:focus-visible) { outline: none; }
.strip text { font-family: inherit; font-size: 12.5px; fill: var(--mute); font-stretch: 104%; }
.strip .rl { fill: var(--ink); font-weight: 620; font-size: 13.5px; }
.strip .mv { fill: var(--ink); font-weight: 700; font-size: 13.5px; }
.strip .ax { stroke: var(--rule); stroke-width: 1; }
.strip .ch { stroke: var(--faint); stroke-width: 1.2; stroke-dasharray: 3 4; }
.strip .mt { stroke: var(--ink); stroke-width: 2; }
.strip .d { fill: var(--ink); }
.strip .d.r { fill: none; stroke: var(--ink); stroke-width: 1.4; }
.strip .d.sel { fill: var(--blue); stroke: var(--blue); }
.strip .hit { fill: transparent; cursor: pointer; pointer-events: all; }
.strip .ring { fill: none; stroke: var(--blue); stroke-width: 2; opacity: 0; transition: opacity .3s ease; }
.strip .ring.on { opacity: 1; }
.strip .you { fill: var(--blue); }
.strip .them { fill: none; stroke: var(--ink); stroke-width: 2; }
.strip .yl { fill: var(--blue); font-weight: 700; font-size: 13px; }
.strip .tl { fill: var(--ink); font-weight: 600; font-size: 13px; }
.strip .row-this { transition: opacity .4s ease; }
.hint { margin: 12px 0 0; font-size: 13px; color: var(--mute); }

@keyframes rise { from { opacity: 0; transform: translateY(12px); } }
@keyframes fade { from { opacity: 0; } }
.enter .plate { animation: rise .9s cubic-bezier(.3, 0, .2, 1) both; }
.enter .back { animation: fade 1.3s .2s both; }
.enter .score { animation: fade .8s .5s both; }

/* The words */
.side { min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none; padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule); }
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts b { color: var(--ink); font-weight: 620; }
.facts .tryit { color: var(--blue); font-weight: 600; }
@media (max-width: 900px) {
  /* On a phone: the problem, the finding, the result of the test, the test, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .pane { order: 4; margin-top: 26px; }
  .plate { display: flex; flex-direction: column; padding: 18px 14px 16px; border-radius: 22px; }
  .back { border-radius: 22px; }
  .score { order: -1; padding: 0 2px 18px; margin-bottom: 18px; border-bottom: 1px solid var(--line); }
  .big { font-size: 60px; }
  .blab { max-width: none; }
  .sentence { min-height: 0; font-size: 18px; }
  .snip { font-size: 14.5px; min-height: 48px; padding: 9px 10px; }
  .act { flex: 1 1 100%; min-width: 0; padding: 12px 18px; }
  .step { padding-left: 4px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .snip, .tick, .txt, .txt mark, .act, .ring, .row-this, .key { transition: none !important; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage" id="stage">
    <div class="scene">
      <div class="body" id="body">
        <div class="back"></div>
        <div class="plate">
          <i class="spec"></i>
          <section class="quiz" aria-label="Try the blind test">
            <div class="qtop"><span id="which"></span><span class="who" id="who"></span></div>
            <p class="sentence" id="sentence"></p>
            <p class="ask" id="ask"></p>
            <ol class="snips" id="snips"></ol>
            <div class="acts">
              <button class="act" id="act"></button>
              <button class="step" data-turn="1" id="next">Next neuron ›</button>
              <span class="dots" id="dots" role="group" aria-label="The three neurons"></span>
            </div>
            <div class="mine" id="mine" aria-live="polite"></div>
            <div class="key" id="key"></div>
          </section>
          <section class="score" aria-label="Result of the test">
            <p class="big" id="big"></p>
            <p class="blab" id="blab"></p>
            <div class="strip"><svg id="strip" tabindex="0" role="group" aria-label="One dot per tested neuron, at its score. Left and right arrows open one neuron after another."></svg></div>
            <p class="hint">One dot per tested neuron, at the share of its 20 snippets sorted right; the solid line is the mean, the dotted line chance. Click a dot to read its sentence.</p>
          </section>
        </div>
      </div>
    </div>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, Q = C.quiz, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const pct = v => (100 * v).toFixed(1) + " %";
const RING = D.ring.map(([key, set, acc, layer, neuron, pole, text]) => ({ key, set, acc, layer, neuron, pole, text }));
const NEED = 4;
/* The state: the neuron on the plate, and for each of the three its picks and whether its key is shown. All of it is in
   the address, so moving to another neuron keeps the picks, and a reload restores them. */
const S = { u: 0, picks: Q.map(() => new Set()), shown: Q.map(() => false), open: null, t0: -1e9, px: 0, py: 0, tx: 0, ty: 0, last: 0 };
const unit = () => Q[S.u], hits = k => [...S.picks[k]].filter(i => Q[k].snippets[i][0]).length;
const right = k => 2 * hits(k);  // of 8: firing snippets picked plus quiet snippets left out (4 picks of 8, 4 fire)

function sheet() {
  const u = unit(), k = S.u, shown = S.shown[k];
  $("which").innerHTML = `<b>Neuron ${k + 1} of ${Q.length}</b>`;
  $("who").textContent = shown ? `Layer ${u.layer}, neuron ${u.neuron}: ${u.set === "selected" ? "one of the 30 that matter for RL" : "a random neuron"}` : "";
  $("sentence").textContent = u.description;
  $("ask").innerHTML = `Pick the ${NEED} snippets where you think this neuron fires on the underlined token.` +
    (u.pole === "-" ? `<span>This sentence describes where its activation is most negative; here “fires” means that.</span>` : "");
  $("snips").innerHTML = u.snippets.map(([fires, a, tok, b], i) =>
    `<li><button class="snip" data-snip="${i}" aria-pressed="false"><i class="tick" aria-hidden="true"></i>` +
    `<span class="txt"><span data-math>${esc(a)}</span><mark${tok.trim() ? "" : ' class="gap"'}>${esc(tok)}</mark><span data-math>${esc(b)}</span></span><span class="sr"></span></button></li>`).join("");
  mark(false);
}
/* The marks of the sheet in the current state. With reveal true the key lights one snippet after another. */
function mark(reveal) {
  const u = unit(), k = S.u, shown = S.shown[k], p = S.picks[k], left = NEED - p.size;
  document.querySelectorAll(".snip").forEach((b, i) => {
    const on = p.has(i), f = u.snippets[i][0];
    const set = () => {
      b.className = "snip" + (shown ? (f ? " fires" : " quiet") + (on ? (f ? " right" : " wrong") : f ? " miss" : "") : "");
      b.querySelector(".tick").textContent = shown && on ? (f ? "✓" : "✕") : "";
    };
    b.setAttribute("aria-pressed", on);
    b.disabled = shown;
    b.querySelector(".sr").textContent = shown ? (f ? ", fires" : ", does not fire") + (on ? (f ? ", your pick, right" : ", your pick, wrong") : "") : "";
    if (reveal && !still.matches) setTimeout(set, 70 * i); else set();
  });
  const act = $("act");
  act.textContent = shown ? "Hide the key" : left ? `Pick ${left} more` : "Reveal the key";
  act.disabled = !shown && left > 0;
  act.className = "act" + (!shown && !left ? " go" : "");
  $("next").textContent = S.u === Q.length - 1 ? "‹ First neuron" : "Next neuron ›";
  $("dots").innerHTML = Q.map((q, j) => `<button data-go="${j}" class="${S.shown[j] ? "done" : S.picks[j].size ? "part" : ""}${j === S.u ? " here" : ""}" ` +
    `aria-label="Neuron ${j + 1}${S.shown[j] ? ", key shown" : S.picks[j].size ? `, ${S.picks[j].size} picked` : ""}"${j === S.u ? ' aria-current="true"' : ""}><i></i></button>`).join("");
  $("key").innerHTML = shown ? `<span><i class="k-fire"></i>Token where it fires</span><span><i class="k-right"></i>Your pick, right</span>` +
    `<span><i class="k-wrong"></i>Your pick, wrong</span><span><i class="k-miss"></i>Fires, not picked</span>` : "";
  score(reveal);
  strip();
}
/* Your score on these 8 snippets beside the blind reader's on all 20 of this neuron; it counts up after a reveal. */
function score(reveal) {
  const k = S.u, u = unit();
  if (!S.shown[k]) {
    $("mine").innerHTML = `<span class="wait">Your score on these 8 snippets appears here, next to the blind reader's score on this neuron.</span>`;
    return;
  }
  const you = right(k) / 8, them = u.blind_accuracy;
  $("mine").innerHTML = `<span class="you"><span class="v" id="vyou">${pct(you)}</span>You, ${right(k)} of 8 snippets right</span>` +
    `<span><span class="v" id="vthem">${pct(them)}</span>Blind reader on this neuron, ${Math.round(20 * them)} of 20 right</span>`;
  if (reveal && !still.matches) { S.t0 = performance.now(); S.count = [you, them]; }
}
function counting(now) {
  if (!S.count) return;
  const e = ease(clamp((now - S.t0 - 300) / 800, 0, 1));
  if ($("vyou")) $("vyou").textContent = pct(S.count[0] * e);
  if ($("vthem")) $("vthem").textContent = pct(S.count[1] * e);
  if (e >= 1) S.count = null;
}

/* The result: two rows of dots, one per tested neuron at its score, stacked where scores are equal, with the mean of each
   row; chance as a dashed line; and, once a key is shown, this neuron: you and the blind reader. */
function strip() {
  const svg = $("strip"), w = svg.clientWidth || 300, small = w < 340, u = unit(), k = S.u, shown = S.shown[k];
  const x0 = 4, x1 = w - 8, X = v => x0 + (x1 - x0) * v, pitch = small ? 8 : 8.6, r = small ? 3.2 : 3.6;
  const rows = [["s", `Neurons that matter most for RL, ${D.sets.selected.units}`, D.sets.selected.mean_accuracy], ["r", `Random neurons, ${D.sets.reference.units}`, D.sets.reference.mean_accuracy]];
  let y = 18, out = "";
  const sel = S.open && S.open.startsWith("n-") ? S.open.slice(2) : null;
  rows.forEach(([set, name, m]) => {
    const dots = RING.filter(d => d.set === set), tall = Math.max(...Object.values(dots.reduce((a, d) => (a[d.acc] = (a[d.acc] || 0) + 1, a), {})));
    out += `<text class="rl" x="${x0}" y="${y}">${esc(name)}</text><text class="mv" x="${x1}" y="${y}" text-anchor="end">mean ${pct(m)}</text>`;
    const base = y + 14 + tall * pitch, seen = {};
    dots.forEach(d => {
      const n = seen[d.acc] = (seen[d.acc] || 0) + 1, cx = X(d.acc), cy = base - (n - .5) * pitch, cur = shown && d.key === u.key;
      out += `<circle class="d ${set}${d.key === sel ? " sel" : ""}" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${r}"/>` +
        `<circle class="ring${cur ? " on" : ""}" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${r + 4}"/>` +
        `<rect class="hit" data-n="${d.key}" x="${(cx - pitch / 2 - 2).toFixed(1)}" y="${(cy - pitch / 2).toFixed(1)}" width="${pitch + 4}" height="${pitch}" tabindex="-1"/>`;
    });
    out += `<line class="ax" x1="${x0}" x2="${x1}" y1="${base + 3}" y2="${base + 3}"/>` +
      `<line class="mt" x1="${X(m)}" x2="${X(m)}" y1="${base - tall * pitch - 2}" y2="${base + 9}"/>`;
    y = base + 34;
  });
  const top = 4, bottom = y - 30;
  out = `<line class="ch" x1="${X(D.chance)}" x2="${X(D.chance)}" y1="${top + 22}" y2="${bottom + 4}"/>` + out;
  const ty = bottom + 22;
  out += [0, .5, 1].map(v => `<text x="${X(v)}" y="${ty}" text-anchor="${v ? v === 1 ? "end" : "middle" : "start"}">${v === .5 ? "50 %, chance" : 100 * v + " %"}</text>`).join("");
  // this neuron, once its key is shown
  const yy = ty + 40;
  if (shown) {
    const you = right(k) / 8, them = u.blind_accuracy;
    out += `<g class="row-this"><text class="rl" x="${x0}" y="${yy - 8}">This neuron</text>` +
      `<line class="ax" x1="${x0}" x2="${x1}" y1="${yy + 22}" y2="${yy + 22}"/>` +
      `<circle class="them" cx="${X(them)}" cy="${yy + 22}" r="6.5"/><circle class="you" cx="${X(you)}" cy="${yy + 22}" r="5"/>` +
      `<text class="tl" x="${X(them)}" y="${yy + 44}" text-anchor="${them > .8 ? "end" : them < .2 ? "start" : "middle"}">Blind reader ${pct(them)}</text>` +
      `<text class="yl" x="${X(you)}" y="${yy + 11}" text-anchor="${you > .8 ? "end" : you < .2 ? "start" : "middle"}">You ${pct(you)}</text></g>`;
  }
  const h = yy + (shown ? 60 : 0);
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
  svg.setAttribute("height", h);
  svg.innerHTML = out;
}

function neuronPane(key) {
  const d = RING.find(x => x.key === key), q = Q.findIndex(x => x.key === key);
  return `<div class="dhead"><h2>Layer ${d.layer}, neuron ${d.neuron}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead">“${esc(d.text)}”</p><ul class="facts">` +
    `<li>${d.set === "s" ? "One of the 30 tested neurons that matter most for RL (of the 100 with the largest effect)." : "One of the 15 random neurons, from the same layers."}</li>` +
    `<li>From this sentence alone, the blind reader sorted <b>${Math.round(20 * d.acc)} of 20</b> snippets right: ${pct(d.acc)}.</li>` +
    `<li>The sentence describes where its activation is most ${d.pole === "+" ? "positive" : "negative"}.</li>` +
    (q >= 0 ? `<li><button class="tryit" data-go="${q}">Try the test on this neuron ›</button></li>` : "") + `</ul>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), n = S.open && S.open.startsWith("n-") && RING.some(d => "n-" + d.key === S.open);
  $("pane").innerHTML = n ? neuronPane(S.open.slice(2)) : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(f => `<li>${esc(f)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
  strip();
}
/* The address: #<neuron on the plate>, then <neuron>=<picks> with r when its key is shown, for each neuron with picks,
   then the open panel or n-<neuron>. */
function address(push) {
  const parts = [S.u ? Q[S.u].key : ""];
  Q.forEach((q, j) => { if (S.picks[j].size || S.shown[j]) parts.push(`${q.key}=${[...S.picks[j]].sort().join(".")}${S.shown[j] ? "r" : ""}`); });
  if (S.open) parts.push(S.open);
  const h = parts.filter(Boolean).join("/"), url = h ? "#" + (parts[0] ? h : Q[0].key + "/" + h) : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash() {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/").filter(Boolean);
  const u = Q.findIndex(q => q.key === parts[0]);
  S.u = u >= 0 ? u : 0;
  Q.forEach((q, j) => { S.picks[j] = new Set(); S.shown[j] = false; });
  S.open = null;
  for (const x of parts) {
    const m = /^(u\d\d)=([\d.]*)(r?)$/.exec(x), j = m ? Q.findIndex(q => q.key === m[1]) : -1;
    if (j >= 0) {
      m[2].split(".").filter(Boolean).map(Number).filter(i => i >= 0 && i < 8).slice(0, NEED).forEach(i => S.picks[j].add(i));
      S.shown[j] = !!m[3] && S.picks[j].size === NEED;
    } else if (C.panels.some(p => p[0] === x) || (x.startsWith("n-") && RING.some(d => "n-" + d.key === x))) S.open = x;
  }
  sheet(); pane();
}
function open(key) {
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  if (key && narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" });
}
function goTo(j, focusSheet) {
  S.u = (j + Q.length) % Q.length;
  sheet();
  address(false);
  if (focusSheet) $("act").focus({ preventScroll: true });
  if (narrow.matches && focusSheet) $("sentence").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "center" });
}

document.addEventListener("click", e => {
  const s = e.target.closest("[data-snip]"), o = e.target.closest("[data-open]"), t = e.target.closest("[data-turn]");
  const g = e.target.closest("[data-go]"), n = e.target.closest("[data-n]");
  if (s && !S.shown[S.u]) {
    const i = Number(s.dataset.snip), p = S.picks[S.u];
    if (p.has(i)) p.delete(i); else if (p.size < NEED) p.add(i);
    else { s.animate?.([{ transform: "translateX(0)" }, { transform: "translateX(4px)" }, { transform: "translateX(0)" }], { duration: 180 }); }
    mark(false); address(false);
  }
  if (t) goTo(S.u + Number(t.dataset.turn), false);
  if (g) goTo(Number(g.dataset.go), true);
  if (n) open("n-" + n.dataset.n);
  if (e.target.closest("#act")) {
    S.shown[S.u] = !S.shown[S.u];
    mark(S.shown[S.u]); address(false);
  }
  if (o) { e.preventDefault(); open(o.dataset.open); }
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && S.open) open("");
});
$("strip").addEventListener("keydown", e => {  // the dots by keyboard: one neuron after another, in the order of their score
  if (!["ArrowRight", "ArrowLeft", "Enter"].includes(e.key)) return;
  e.preventDefault();
  const at = S.open && S.open.startsWith("n-") ? RING.findIndex(d => "n-" + d.key === S.open) : -1;
  const j = e.key === "Enter" ? Math.max(0, at) : (at + (e.key === "ArrowRight" ? 1 : -1) + RING.length) % RING.length;
  S.open = "n-" + RING[j].key; address(true); pane();
});
addEventListener("popstate", fromHash);
addEventListener("hashchange", fromHash);
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  S.tx = 2 * (e.clientX - b.left) / b.width - 1; S.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { S.tx = S.ty = 0; });
new ResizeObserver(() => strip()).observe($("strip").parentNode);
/* Always on: the plate sways a few degrees and leans toward the mouse; after a reveal the scores count up. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = now / 1000;
  S.px += (S.tx - S.px) * .08; S.py += (S.ty - S.py) * .08;
  $("body").style.transform = `rotateY(${(2.4 * Math.sin(t * .13) + 2.2 * S.px).toFixed(2)}deg) rotateX(${(1.2 * Math.sin(t * .09) - 1.6 * S.py + 1.5).toFixed(2)}deg)`;
  counting(now);
}
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
$("big").innerHTML = `${(100 * D.sets.selected.mean_accuracy).toFixed(1)}<small>%</small>`;
$("blab").textContent = `of test snippets sorted right (the neuron fires there or not) by a blind reader, on ${D.sets.selected.units} of the 100 neurons that matter most for RL's change. Random neurons score ${pct(D.sets.reference.mean_accuracy)}; chance is ${pct(D.chance)}.`;
fromHash();
$("body").style.transform = "rotateX(1.5deg)";
if (!still.matches) { document.body.classList.add("enter"); setTimeout(() => document.body.classList.remove("enter"), 2000); }
requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "quiz": QUIZ,
    "data": {k: DATA[k] for k in ("sets", "chance", "ring")}}, ensure_ascii=False).replace("</", "<\\/"))


if __name__ == "__main__":  # DATA against its artifacts; run from the repository root
    test, page = json.load(open(DATA["artifact"])), json.load(open(DATA["examples"]))
    run, dens = json.load(open(DATA["run"])), json.load(open(DATA["density"]))
    assert (DATA["chance"], DATA["sets"]) == (test["chance"], test["sets"]), "set means or intervals differ"
    assert DATA["ring"] == [[u["key"], u["set"][0], u["accuracy"], u["layer"], u["neuron"], u["pole"], u["description"]]
                            for u in sorted(test["units"], key=lambda u: (-u["accuracy"], u["key"]))], "unit scores differ"
    assert (DATA["commit"], DATA["job"], DATA["command"]) == (run["commit"], run["job_id"], run["command"]), "run differs"
    k = "on_beyond_p97_at_more_than_half_of_positions"
    assert DATA["always_on"] == {"selected": dens["selected"][k], "reference": dens["reference"][k], "positions": dens["positions"]}
    assert DATA["seed"] == page["seed"] and len(DATA["units"]) == len(page["units"])
    for mine, u in zip(DATA["units"], page["units"]):
        scored = next(x for x in test["units"] if x["key"] == u["key"])
        for f in ("key", "set", "layer", "neuron", "pole", "description"):
            assert mine[f] == u[f] == scored[f], (u["key"], f)
        assert mine["blind_accuracy"] == u["blind_accuracy"] == scored["accuracy"], u["key"]
        assert mine["snippets"] == [[s["id"], s["fires"], s["text"]] for s in u["snippets"]], u["key"]
        assert sum(s[1] for s in mine["snippets"]) == 4, u["key"]
    for q in QUIZ:
        for s in q["snippets"]:
            print(q["key"], s[0], repr(s[1] + "[" + s[2] + "]" + s[3]))
    print("DATA matches", DATA["artifact"], DATA["examples"], "and", DATA["density"])
