"""The talk as a slide deck: thirteen 16:9 slides, one figure each, very few words.

view.py serves page(...) at /demo (the stepped story of demo.py is at /demo/story) and FIGS at /demo/fig/<name>.
Each slide is a 1600 x 900 box scaled to fit the window. Keys: right arrow, Space or PageDown next; left arrow or
PageUp back; Home and End; t theme (also the button at the top right); f fullscreen; p print. A click on the right or left third of the window also
steps. The slide is in the address (/demo#finding), so Back works. Printing (p) gives one slide per page at 13.333 x
7.5 in, in the theme on screen.

Every number is read at build time from the module that holds it:
the staircase of fixes from demo_fixes.py, the two models of the gap slide and the accuracy climb from demo_ali_data.DATA['climb'], the two result pictures from demo_results.py, the review rounds
from demo_review.py (which reads proof_review_cuts_waste.DATA), the idea tree's links from proof_idea_basins.DATA['tree'] (demo_converge.py counts them live), the number of people from
demo_facts.FACTS['people']; view.py passes the list of papers. The photos are data
URIs in demo_photos.py. Eight slides show a picture in an iframe of FIGS: the two models and the bridge between them
of demo_gap.py, the accuracy climb of /demo/ali/slide3, the Design page (architecture.py), the staircase of fixes of demo_fixes.py, the two pictures of demo_results.py, the glass
columns of demo_review.py, each with its header, words column and key hidden, and the idea tree growing over the slab
of /proof/idea-basins (demo_converge.py, full-bleed). A frame with data-replay is loaded again when its slide is shown, so
its picture draws itself in front of the audience.
"""
import html
import re

import architecture
import demo
import demo_ali
import demo_ali_data
import demo_converge
import demo_facts
import demo_fixes
import demo_gap
import demo_photos
import demo_results
import demo_review
import exa_page
import pastdev
import proof_idea_basins

HOOK = "36 hours to solve recursive self-improvement"  # the opening line of the talk
TAGLINE = "Symbiotic harness for resource-constrained researchers"  # what Invariant is: after the name, under the opening line
SITE = "invariant.team"  # the address on the first and last slide
# Slide "summary": what the team did, in Samer's words, in groups of lines.
# Slide "built": what the team did, said once early and in full on the slide "summary".
BUILT_WHY = "to empower resource-constrained researchers to make novel findings"  # slide "built": under its title
BUILT = [("A symbiotic swarm", " with one shared brain"), ("More efficient", " than autoresearch"),
         ("Novel findings", " in machine learning and interpretability")]
# The harness slide's efficiency points, shown one per click beside the picture.
WINS = ["Same accuracy for 2.7× fewer tokens", "More right answers for half the tokens on harder problems",
        "It improves itself", "GPUs start in seconds", "Weights download once", "No time lost to bad machines",
        "No idle GPUs", "Agents spend few tokens on coordination", "Nothing is run twice"]
SUMMARY = [  # each line: the words in bold, then the rest
    [("Team harness", " for resource-constrained researchers"), ("Novel", ", paper-worthy findings")],
    [("More effective", " than autoresearch, less compute"), ("Improves itself", "")],
    [("Novel ideas", " with Exa search"), ("Shared brain", " with past.dev")],
    [("Swarms", " that forecast GPU prices")],
]
# The QR code of https://invariant.team (version 2, error level M) as one SVG path of unit squares on a
# 25 x 25 grid: segno.make("https://invariant.team", error="m").matrix, a square per dark module.
QR_SIZE = 25
QR_PATH = "M0 0h1v1h-1zM1 0h1v1h-1zM2 0h1v1h-1zM3 0h1v1h-1zM4 0h1v1h-1zM5 0h1v1h-1zM6 0h1v1h-1zM11 0h1v1h-1zM13 0h1v1h-1zM14 0h1v1h-1zM15 0h1v1h-1zM16 0h1v1h-1zM18 0h1v1h-1zM19 0h1v1h-1zM20 0h1v1h-1zM21 0h1v1h-1zM22 0h1v1h-1zM23 0h1v1h-1zM24 0h1v1h-1zM0 1h1v1h-1zM6 1h1v1h-1zM8 1h1v1h-1zM9 1h1v1h-1zM10 1h1v1h-1zM14 1h1v1h-1zM15 1h1v1h-1zM18 1h1v1h-1zM24 1h1v1h-1zM0 2h1v1h-1zM2 2h1v1h-1zM3 2h1v1h-1zM4 2h1v1h-1zM6 2h1v1h-1zM9 2h1v1h-1zM10 2h1v1h-1zM12 2h1v1h-1zM14 2h1v1h-1zM18 2h1v1h-1zM20 2h1v1h-1zM21 2h1v1h-1zM22 2h1v1h-1zM24 2h1v1h-1zM0 3h1v1h-1zM2 3h1v1h-1zM3 3h1v1h-1zM4 3h1v1h-1zM6 3h1v1h-1zM14 3h1v1h-1zM15 3h1v1h-1zM16 3h1v1h-1zM18 3h1v1h-1zM20 3h1v1h-1zM21 3h1v1h-1zM22 3h1v1h-1zM24 3h1v1h-1zM0 4h1v1h-1zM2 4h1v1h-1zM3 4h1v1h-1zM4 4h1v1h-1zM6 4h1v1h-1zM8 4h1v1h-1zM9 4h1v1h-1zM10 4h1v1h-1zM15 4h1v1h-1zM18 4h1v1h-1zM20 4h1v1h-1zM21 4h1v1h-1zM22 4h1v1h-1zM24 4h1v1h-1zM0 5h1v1h-1zM6 5h1v1h-1zM10 5h1v1h-1zM13 5h1v1h-1zM14 5h1v1h-1zM15 5h1v1h-1zM18 5h1v1h-1zM24 5h1v1h-1zM0 6h1v1h-1zM1 6h1v1h-1zM2 6h1v1h-1zM3 6h1v1h-1zM4 6h1v1h-1zM5 6h1v1h-1zM6 6h1v1h-1zM8 6h1v1h-1zM10 6h1v1h-1zM12 6h1v1h-1zM14 6h1v1h-1zM16 6h1v1h-1zM18 6h1v1h-1zM19 6h1v1h-1zM20 6h1v1h-1zM21 6h1v1h-1zM22 6h1v1h-1zM23 6h1v1h-1zM24 6h1v1h-1zM9 7h1v1h-1zM13 7h1v1h-1zM16 7h1v1h-1zM0 8h1v1h-1zM2 8h1v1h-1zM4 8h1v1h-1zM6 8h1v1h-1zM11 8h1v1h-1zM12 8h1v1h-1zM13 8h1v1h-1zM15 8h1v1h-1zM16 8h1v1h-1zM20 8h1v1h-1zM23 8h1v1h-1zM0 9h1v1h-1zM1 9h1v1h-1zM4 9h1v1h-1zM5 9h1v1h-1zM7 9h1v1h-1zM8 9h1v1h-1zM13 9h1v1h-1zM16 9h1v1h-1zM17 9h1v1h-1zM18 9h1v1h-1zM24 9h1v1h-1zM0 10h1v1h-1zM2 10h1v1h-1zM4 10h1v1h-1zM6 10h1v1h-1zM8 10h1v1h-1zM9 10h1v1h-1zM10 10h1v1h-1zM11 10h1v1h-1zM17 10h1v1h-1zM19 10h1v1h-1zM20 10h1v1h-1zM22 10h1v1h-1zM23 10h1v1h-1zM24 10h1v1h-1zM0 11h1v1h-1zM1 11h1v1h-1zM7 11h1v1h-1zM9 11h1v1h-1zM13 11h1v1h-1zM14 11h1v1h-1zM15 11h1v1h-1zM17 11h1v1h-1zM18 11h1v1h-1zM19 11h1v1h-1zM20 11h1v1h-1zM23 11h1v1h-1zM0 12h1v1h-1zM1 12h1v1h-1zM2 12h1v1h-1zM4 12h1v1h-1zM5 12h1v1h-1zM6 12h1v1h-1zM7 12h1v1h-1zM8 12h1v1h-1zM9 12h1v1h-1zM10 12h1v1h-1zM11 12h1v1h-1zM12 12h1v1h-1zM13 12h1v1h-1zM16 12h1v1h-1zM17 12h1v1h-1zM18 12h1v1h-1zM21 12h1v1h-1zM23 12h1v1h-1zM24 12h1v1h-1zM2 13h1v1h-1zM5 13h1v1h-1zM7 13h1v1h-1zM8 13h1v1h-1zM9 13h1v1h-1zM11 13h1v1h-1zM12 13h1v1h-1zM13 13h1v1h-1zM16 13h1v1h-1zM18 13h1v1h-1zM21 13h1v1h-1zM24 13h1v1h-1zM0 14h1v1h-1zM2 14h1v1h-1zM4 14h1v1h-1zM6 14h1v1h-1zM7 14h1v1h-1zM8 14h1v1h-1zM11 14h1v1h-1zM12 14h1v1h-1zM14 14h1v1h-1zM17 14h1v1h-1zM18 14h1v1h-1zM19 14h1v1h-1zM22 14h1v1h-1zM23 14h1v1h-1zM24 14h1v1h-1zM1 15h1v1h-1zM4 15h1v1h-1zM7 15h1v1h-1zM9 15h1v1h-1zM12 15h1v1h-1zM13 15h1v1h-1zM14 15h1v1h-1zM15 15h1v1h-1zM17 15h1v1h-1zM18 15h1v1h-1zM20 15h1v1h-1zM23 15h1v1h-1zM0 16h1v1h-1zM2 16h1v1h-1zM5 16h1v1h-1zM6 16h1v1h-1zM7 16h1v1h-1zM10 16h1v1h-1zM11 16h1v1h-1zM13 16h1v1h-1zM15 16h1v1h-1zM16 16h1v1h-1zM17 16h1v1h-1zM18 16h1v1h-1zM19 16h1v1h-1zM20 16h1v1h-1zM21 16h1v1h-1zM8 17h1v1h-1zM9 17h1v1h-1zM11 17h1v1h-1zM15 17h1v1h-1zM16 17h1v1h-1zM20 17h1v1h-1zM21 17h1v1h-1zM23 17h1v1h-1zM24 17h1v1h-1zM0 18h1v1h-1zM1 18h1v1h-1zM2 18h1v1h-1zM3 18h1v1h-1zM4 18h1v1h-1zM5 18h1v1h-1zM6 18h1v1h-1zM15 18h1v1h-1zM16 18h1v1h-1zM18 18h1v1h-1zM20 18h1v1h-1zM21 18h1v1h-1zM23 18h1v1h-1zM24 18h1v1h-1zM0 19h1v1h-1zM6 19h1v1h-1zM9 19h1v1h-1zM10 19h1v1h-1zM11 19h1v1h-1zM13 19h1v1h-1zM14 19h1v1h-1zM16 19h1v1h-1zM20 19h1v1h-1zM21 19h1v1h-1zM23 19h1v1h-1zM24 19h1v1h-1zM0 20h1v1h-1zM2 20h1v1h-1zM3 20h1v1h-1zM4 20h1v1h-1zM6 20h1v1h-1zM8 20h1v1h-1zM9 20h1v1h-1zM10 20h1v1h-1zM12 20h1v1h-1zM14 20h1v1h-1zM16 20h1v1h-1zM17 20h1v1h-1zM18 20h1v1h-1zM19 20h1v1h-1zM20 20h1v1h-1zM21 20h1v1h-1zM23 20h1v1h-1zM24 20h1v1h-1zM0 21h1v1h-1zM2 21h1v1h-1zM3 21h1v1h-1zM4 21h1v1h-1zM6 21h1v1h-1zM11 21h1v1h-1zM12 21h1v1h-1zM13 21h1v1h-1zM15 21h1v1h-1zM16 21h1v1h-1zM19 21h1v1h-1zM20 21h1v1h-1zM21 21h1v1h-1zM22 21h1v1h-1zM0 22h1v1h-1zM2 22h1v1h-1zM3 22h1v1h-1zM4 22h1v1h-1zM6 22h1v1h-1zM8 22h1v1h-1zM10 22h1v1h-1zM11 22h1v1h-1zM12 22h1v1h-1zM14 22h1v1h-1zM16 22h1v1h-1zM20 22h1v1h-1zM24 22h1v1h-1zM0 23h1v1h-1zM6 23h1v1h-1zM10 23h1v1h-1zM12 23h1v1h-1zM13 23h1v1h-1zM16 23h1v1h-1zM17 23h1v1h-1zM20 23h1v1h-1zM21 23h1v1h-1zM23 23h1v1h-1zM0 24h1v1h-1zM1 24h1v1h-1zM2 24h1v1h-1zM3 24h1v1h-1zM4 24h1v1h-1zM5 24h1v1h-1zM6 24h1v1h-1zM8 24h1v1h-1zM9 24h1v1h-1zM10 24h1v1h-1zM11 24h1v1h-1zM12 24h1v1h-1zM14 24h1v1h-1zM15 24h1v1h-1zM16 24h1v1h-1zM17 24h1v1h-1zM18 24h1v1h-1zM19 24h1v1h-1zM23 24h1v1h-1zM24 24h1v1h-1z"

# The title of each paper by its file name in view.PAPERS; paper_title falls back to the file name.
PAPER_TITLES = {"the-finish-dial.pdf": "The Finish Dial", "theories-on-trial.pdf": "Theories on Trial",
                "the-first-hundred-steps.pdf": "The First Hundred Steps", "no-early-warning.pdf": "No Early Warning",
                "two-token-limits.pdf": "Two Token Limits"}
PAPER_AUTHOR = "The Invariant Swarm"


def paper_title(name):
    """The title on a paper's sheet: its entry in PAPER_TITLES, else the words of its file name. A paper added to
    view.PAPERS with no entry here still gets a sheet, so a new paper cannot stop view.py at import."""
    return PAPER_TITLES.get(name) or name.rsplit(".", 1)[0].replace("-", " ").title()

# What the deck shares with demo.py: the Archivo link and the theme script (?theme=, then the stored choice).
FONT = re.search(r'<link rel="preconnect".*?display=swap">', demo.TEMPLATE, re.S).group(0)
THEME_JS = re.search(r"<script>\n/\* The theme before the first paint.*?</script>", demo.TEMPLATE, re.S).group(0)
TOKENS = (':root {\n  color-scheme: light;\n  ' + demo.LIGHT + '\n}\n@media (prefers-color-scheme: dark) {\n'
          '  :root:not([data-theme="light"]) {\n    color-scheme: dark;\n    ' + demo.DARK + '\n  }\n}\n'
          ':root[data-theme="dark"] {\n  color-scheme: dark;\n  ' + demo.DARK + '\n}\n')

# The two logos of architecture.py (past.dev and Exa), read from its page.
LOGOS = {m.group(1): {"box": m.group(2), "body": m.group(3)} for m in
         re.finditer(r'  (\w+): \{ box: "([^"]+)", w: [\d.]+, h: [\d.]+, base: [\d.]+, tall: [\d.]+, body: `(.*?)` \}', architecture.PAGE)}
assert set(LOGOS) == {"past", "exa"}, f"architecture.py logos changed: {sorted(LOGOS)}"


def esc(s):
    return html.escape(str(s), quote=True)


# ---------- the embedded pictures ----------
FIG_THEME = (r"""<script>
(() => { const t = new URLSearchParams(location.search).get("theme"); if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
  if (top === window) document.documentElement.style.setProperty("background", "var(--paper)", "important"); })();  // opened by itself, a see-through figure stands on its own paper
</script>""")


def embed(page, css):
    assert page.count("</head>") == 1
    return page.replace("</head>", f"<style>\n{css}\n</style>\n{FIG_THEME}\n</head>", 1)


_T = re.search(r":root \{\n  color-scheme: light dark;\n(.*?)\n\}\n@media \(prefers-color-scheme: dark\) \{\n  :root \{\n(.*?)\n  \}\n\}",
               proof_idea_basins.PAGE, re.S)
assert _T, "the tokens of proof_idea_basins.py changed"
BASIN_LIGHT, BASIN_DARK = (" ".join(t.split()) for t in _T.groups())

_TOK = re.compile(r":root \{\n  color-scheme: light dark;\n(.*?)\n\}\n@media \(prefers-color-scheme: dark\) \{\n  :root \{\n(.*?)\n  \}\n\}", re.S)


def sponsor_theme(page):
    """/exa and /pastdev follow only the system theme: their own two sets of tokens are repeated for data-theme, and
    the page stands on the deck's paper. The colour scheme stays light in both themes: a frame is see-through only while
    its page's scheme equals the frame's."""
    m = _TOK.search(page)
    assert m, "the tokens of a sponsor page changed"
    light, dark = (" ".join(t.split()) for t in m.groups())
    return f"""html, body {{ overflow: hidden; background: transparent !important; }}
:root[data-theme="light"] {{ color-scheme: light; {light} }}
:root[data-theme="dark"] {{ color-scheme: light; {light} {dark} }}"""


# The basins picture steps through its conditions by itself: the items, then the basins, then the idea tree.
BASIN_PLAY = """<script>
addEventListener("load", () => { setTimeout(() => choose(1), 1400); setTimeout(() => choose(2), 7400); });
</script>"""

FIGS = {
    # architecture.py follows only the system theme, so the deck's tokens are added for data-theme here.
    "harness": embed(architecture.PAGE, f""":root[data-theme="light"] {{ color-scheme: light; {demo.LIGHT} }}
:root[data-theme="dark"] {{ color-scheme: dark; {demo.DARK} }}
html, body {{ overflow: hidden; }}
.top, .foot, .side, .say, .part.key, .part.tool {{ display: none !important; }}
.page {{ display: block !important; height: 100vh !important; min-height: 0 !important; max-width: none !important; padding: 0 !important; }}
.stage {{ height: 100vh; padding: 0 !important; }}"""),
    # the accuracy climb of Ali's slide 3: the step line over the idea disc, without its words and its controls
    "climb": embed(demo_ali.PAGES["slide3"], """html, body { overflow: hidden; }
.top, .side, .foot { display: none !important; }
.page { padding: 0 !important; max-width: none !important; height: 100vh; }
.view { display: block !important; }
.stage { height: 100vh; padding: 0 !important; }
.stage svg { display: block; width: 100vw !important; height: 100vh !important; max-height: none !important; }"""),
    "fixes": embed(demo_fixes.PAGE, ""),
    "beyond": embed(demo_results.PAGES["beyond"], ""),
    "efficiency": embed(demo_results.PAGES["efficiency"], ""),
    "review": embed(demo_review.PAGE, ""),
    # the ideas slide: the idea tree growing over the slab of /proof/idea-basins, one self-playing canvas (demo_converge.py)
    "converge": demo_converge.PAGE,
    # Not on a slide now, kept at /demo/fig/basins: /proof/idea-basins playing by itself, the slab, the switch and the count. It opens on the board items, gathers
    # them into their basins and then lays the basins out as the rows of the idea tree (BASIN_PLAY). That page
    # follows only the system theme, so its own two sets of tokens are repeated for data-theme here.
    "basins": embed(proof_idea_basins.PAGE, f""":root[data-theme="light"] {{ color-scheme: light; {BASIN_LIGHT} }}
:root[data-theme="dark"] {{ color-scheme: dark; {BASIN_DARK} }}""" + """
html, body { overflow: hidden; }
.top, .side, .note, .key { display: none !important; }
.page { display: block !important; height: 100vh !important; min-height: 0 !important; max-width: none !important; padding: 0 !important; }
.stage { height: 100vh; padding: 0 0 14px !important; }
svg#svg { flex: 1 1 0; min-height: 0; max-height: none !important; }
.switch { margin-top: 6px !important; }""").replace("</head>", BASIN_PLAY + "\n</head>", 1),
    # the sponsors slide: the scene of /exa and the memory scene of /pastdev alone, each replaying its real cases.
    # Both pages take the deck's theme through their own tokens (sponsor_theme).
    "exa": embed(exa_page.PAGE, sponsor_theme(exa_page.PAGE) + """
header.top, .inv-home, nav, .first h1, .nums, .cases, .key, .note, section, footer { display: none !important; }
.wrap { max-width: none !important; padding: 0 !important; }
.first { padding: 0 !important; margin: 0 !important; }
.replay { display: block !important; }
.scene { height: 100vh !important; }
#sc ellipse[fill="url(#sc-floor)"] { display: none; }  /* the floor's glow is wider than the frame and would show its edge */"""),
    "pastdev": embed(pastdev.PAGE, sponsor_theme(pastdev.PAGE) + """
header.top, .inv-home, .mast, .lede, .nums, .src-line, .fig-tw, .figlab, .key, .figsay, .strip, section, .end { display: none !important; }
.page { max-width: none !important; padding: 0 !important; }
.first { padding: 0 !important; margin: 0 !important; border: 0 !important; }
.figs { display: block !important; margin: 0 !important; }
#mem { height: 100vh !important; }
.scene text { font-size: 13px !important; }
.scene text.tag { display: block !important; }"""),
    # the side note of the sponsors slide: the towers of /pastdev alone (recall against grep, 20 questions)
    "pasttw": embed(pastdev.PAGE, sponsor_theme(pastdev.PAGE) + """
header.top, .inv-home, .mast, .lede, .nums, .src-line, .fig-mem, .figlab, .key, .figsay, .strip, section, .end { display: none !important; }
.page { max-width: none !important; padding: 0 !important; }
.first { padding: 0 !important; margin: 0 !important; border: 0 !important; }
.figs { display: block !important; margin: 0 !important; }
.fig-tw { margin: 0 !important; }
#tw { height: 100vh !important; }"""),
}

# The numbers under the two sponsor figures, read from the first screens of /exa and /pastdev (label -> number).
EXA_NUMS = {label: n for n, label in re.findall(r"<li><b>(.*?)</b><span>(.*?)</span></li>", exa_page.PAGE)}
PAST_NUMS = {label: n for n, label in re.findall(r'<span class="n">(.*?)</span><span class="w">(.*?)</span>', pastdev.PAGE)}
assert {"arXiv papers surfaced", "pages read in full"} <= set(EXA_NUMS), f"the numbers row of exa_page.py changed: {sorted(EXA_NUMS)}"
assert {"memories", "median recall"} <= set(PAST_NUMS), f"the numbers row of pastdev.py changed: {sorted(PAST_NUMS)}"


# ---------- the numbers ----------

PEOPLE = demo_facts.FACTS["people"]["v"]
RL_DAYS = demo_facts.FACTS["rl_training_days"]["v"]  # see the caveat in its note
RL_GPUS = demo_facts.FACTS["rl_zero_gpus"]["v"]["total"]  # learner + actor GPUs of the RL training, Olmo 3 paper, Table 49

BASINS = proof_idea_basins.DATA  # the board items and their basins
TREE = BASINS["tree"]  # links between board items, and those that join two basins

# The accuracy climb: the plain base's first score and its record by vote after restart, and RL's best.
CLIMB = demo_ali_data.DATA["climb"]
CLIMB_LO = CLIMB["base"][0]
CLIMB_HI = next(s for s in CLIMB["base"] if s["config"].endswith("vote over 4 samples after restart"))
CLIMB_RL = max(CLIMB["rl"], key=lambda s: s["right"])
pct = lambda s: 100 * s["right"] / s["n"]
FIGS["gap"] = embed(demo_gap.page(pct(CLIMB_LO), pct(CLIMB_RL), CLIMB["bench"]), "")


# ---------- the parts drawn here ----------
def photo(uri, cls):
    if uri:
        return f'<div class="photo {cls}"><img src="{uri}" alt=""></div>'
    return f'<div class="photo {cls} empty"><span>Photo</span></div>'


def logo(name):
    L = LOGOS[name]
    return f'<svg class="logo logo-{name}" viewBox="{L["box"]}" aria-hidden="true">{L["body"]}</svg>'


def paper(name):
    lines = "".join(f'<i style="width:{w}%"></i>' for w in (92, 86, 90, 70, 88, 94, 62))
    return (f'<a class="sheet" href="/paper/{esc(name)}"><b>{esc(paper_title(name))}</b>'
            f'<span>{esc(PAPER_AUTHOR)}</span><div class="lines">{lines}</div></a>')


def hours_svg():
    """Slide "hook": 36 dots on a spiral, one per hour, twelve to a turn like a clock face. Each turn is wider than
    the one before (a loop that improves), the dots light up one by one, the 36th is the accent, and a small lit
    head then keeps travelling the spiral. With reduced motion and in print all 36 dots are lit and nothing moves."""
    import math
    n, turns = 36, 3
    at = lambda i: (-math.pi / 2 + i * 2 * math.pi * turns / n, 20 + i * 1.8)
    pts = [(r * math.cos(a), r * math.sin(a)) for a, r in (at(i) for i in range(n))]
    last = ' class="last"'
    dots = "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{2 + i * .055:.2f}" style="--i:{i}"{last if i == n - 1 else ""}/>'
                   for i, (x, y) in enumerate(pts))
    fine = [(r * math.cos(a), r * math.sin(a)) for a, r in (at(k / 8) for k in range((n - 1) * 8 + 1))]
    path = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in fine)
    head = "".join(f'<circle class="head" r="{2.6 - k * .5:.1f}" opacity="{1 - k * .3:.1f}">'
                   f'<animateMotion dur="12s" begin="{4.6 + k * .12:.2f}s" repeatCount="indefinite" path="{path}"/></circle>' for k in range(3))
    return (f'<svg class="hours" viewBox="-92 -92 184 184" role="img" aria-label="36 hours as 36 dots on a widening spiral">'
            f'{dots}{head}</svg>')


def hook_html():
    """The hook with "self-improvement" kept on one line."""
    return esc(HOOK).replace("self-improvement", '<span class="nb">self-improvement</span>')


def qr():
    """The QR code of the site: dark modules on a white tile in both themes, with the 4-module quiet zone a scanner needs."""
    q = 4
    return (f'<svg class="qr" viewBox="{-q} {-q} {QR_SIZE + 2 * q} {QR_SIZE + 2 * q}" role="img" aria-label="QR code of {SITE}">'
            f'<rect x="{-q}" y="{-q}" width="{QR_SIZE + 2 * q}" height="{QR_SIZE + 2 * q}" rx="1.5" fill="#fff"/>'
            f'<path d="{QR_PATH}" fill="#101820" shape-rendering="crispEdges"/></svg>')


def slides(papers):
    return [
        ("hook", f'<div class="mid">{hours_svg()}<h1 class="big">{hook_html()}</h1><p class="tagline"><b class="team">Invariant</b>: {esc(TAGLINE)}</p><div class="site">{qr()}<span>{esc(SITE)}</span></div></div>'),
        ("question", f'<div class="mid"><p class="sub top">{PEOPLE} independent researchers</p>'
                     '<ul class="limits"><li>Limited token budget</li><li>Limited compute</li><li>Limited people</li></ul></div>'),
        ("built", '<div class="recap"><div><h2 class="title">So we built <b class="team">Invariant</b></h2>'
                  f'<p class="sub why">{esc(BUILT_WHY)}</p></div><div class="did one">'
                  + "<ul>" + "".join(f"<li><b>{esc(bold)}</b>{esc(rest)}</li>" for bold, rest in BUILT) + "</ul>" + '</div></div>'),
        ("powered", '<div class="versus">'
                    f'<div><p class="sub">The RL-trained model</p><p class="sub by">Powered by</p><p class="gpus">{RL_GPUS} H100 GPUs</p><p class="days">{RL_DAYS} days</p></div>'
                    f'<div><p class="sub">Invariant</p><p class="sub by">Powered by</p>{photo(demo_photos.COOK, "cook")}'
                    + (f'<p class="who">{esc(demo_photos.COOK_NAME)}</p>' if demo_photos.COOK_NAME else "") + '</div></div>'),
        ("harness", '<div class="head"><h2>Invariant</h2><p class="sub">Symbiotic research swarm</p></div>'
                    '<iframe class="fig-frame harness" data-fig="harness" title="The harness" tabindex="-1"></iframe>'
                    + '<ul class="wins">' + "".join(f'<li class="step">{esc(w)}</li>' for w in WINS) + '</ul>'
                    f'<div class="tools"><span>Search {logo("exa")}</span><span>Memory {logo("past")}</span><span>GPUs <b class="word">Modal</b></span>'
                    '<span>Agents <b class="word">OpenAI</b><b class="word">Devin</b><b class="word">Anthropic</b></span></div>'),
        ("gap", '<iframe class="fig-frame gapfig" data-fig="gap" data-replay title="Base model and RL-trained model" tabindex="-1"></iframe>'),
        ("climb", f'<div class="head"><h2>No training: {pct(CLIMB_LO):.1f} % to {pct(CLIMB_HI):.0f} % on {esc(CLIMB["bench"])}</h2></div>'
                  '<iframe class="fig-frame climb" data-fig="climb" data-replay title="The accuracy climb" tabindex="-1"></iframe>'
                  '<div class="replay"><input class="seek" type="range" min="0" max="1000" step="1" value="0" aria-label="Board time">'
                  '<button class="rate" aria-pressed="false" aria-label="Half speed">0.5×</button></div>'),
        ("sponsors", '<div class="head"><h2>Search and memory before every experiment</h2></div>'
                     '<iframe class="fig-frame sponsor s-exa" data-fig="exa" data-replay title="Exa: searches at the gate before a GPU run" tabindex="-1"></iframe>'
                     '<iframe class="fig-frame sponsor s-past" data-fig="pastdev" data-replay title="past.dev: one agent writes, another reads" tabindex="-1"></iframe>'
                     '<iframe class="fig-frame s-tw" data-fig="pasttw" data-replay title="past.dev recall against grep, 20 questions" tabindex="-1"></iframe>'
                     '<p class="spon-note">Recall against grep, 20 questions</p>'
                     f'<p class="spon s-exa">{logo("exa")}<span><b>{esc(EXA_NUMS["arXiv papers surfaced"])}</b> arXiv papers surfaced · <b>{esc(EXA_NUMS["pages read in full"])}</b> pages read in full</span></p>'
                     f'<p class="spon s-past">{logo("past")}<span><b>{esc(PAST_NUMS["memories"])}</b> memories · <b>{esc(PAST_NUMS["median recall"])}</b> median recall</span></p>'),
        ("finding", '<h2 class="title top-title">Interpretable findings with hill climbing</h2>'
                    '<iframe class="fig-frame fixes" data-fig="fixes" data-replay title="One problem, four answers" tabindex="-1"></iframe>'),
        ("beyond", '<div class="head"><h2>These findings are generalizable</h2>'
                   '<p class="sub">One <b class="team">Invariant</b> method: climbed on MATH-500 only, then used unchanged on three benchmarks it never saw</p></div>'
                   '<iframe class="fig-frame wide" data-fig="beyond" data-replay title="Beyond MATH-500" tabindex="-1"></iframe>'),
        ("efficiency", f'<div class="head"><h2>Benchmarking against Karpathy\'s autoresearch</h2>'
                       f'<p class="sub">100k GitHub stars · same score with {demo_results.TOKEN_RATIO:.1f}× fewer tokens · +{demo_results.HARD_GAIN:g} points on harder problems</p></div>'
                       '<iframe class="fig-frame wide" data-fig="efficiency" data-replay title="Our harness against autoresearch" tabindex="-1"></iframe>'),
        ("proof", '<h2 class="title top-title">Its own review cuts waste</h2>'
                  '<iframe class="fig-frame review" data-fig="review" data-replay title="Container minutes per batch over review rounds" tabindex="-1"></iframe>'),
        ("ideas", f'<div class="head"><h2>Ideas cluster and converge</h2></div>'
                  '<iframe class="fig-frame tree" data-fig="converge" data-replay title="The idea tree" tabindex="-1"></iframe>'),
        ("papers", f'<div class="mid"><h2 class="title">{len(papers)} papers, written by the swarm</h2>'
                   f'<div class="sheets" style="--n:{len(papers)}">{"".join(paper(p) for p in papers)}</div></div>'),
        ("summary", '<div class="recap"><h2 class="title"><b class="team">Invariant</b></h2><div class="did">'
                    + "".join("<ul>" + "".join(f"<li><b>{esc(bold)}</b>{esc(rest)}</li>" for bold, rest in group) + "</ul>" for group in SUMMARY)
                    + '</div><p class="sub">All in under 36 hours</p></div>'),
        ("close", f'<div class="mid"><p class="end">Along the way we may have gotten some AI psychosis</p>'
                  f'{photo(demo_photos.MEDITATE, "meditate")}<p class="end">It\'s fine, we found a cure</p>'
                  f'<p class="sub faint">{esc(SITE)}</p></div>'),
    ]


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: Talk</title>
__FONT__
__THEME_JS__
<style>
__TOKENS__
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { margin: 0; height: 100%; overflow: hidden; background: var(--paper); }
body {
  color: var(--ink); font: 400 15px/1.4 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased; user-select: none;
}
a { color: inherit; text-decoration: none; }
p, h1, h2, figure { margin: 0; }

/* One slide is a 1600 x 900 box, scaled to the window (--s, set from the script). */
.slide { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; background: var(--paper);
  opacity: 0; visibility: hidden; transition: opacity .35s ease, visibility 0s linear .35s; }
.slide.on { opacity: 1; visibility: visible; transition: opacity .35s ease; }
.box { position: relative; flex: none; width: 1600px; height: 900px; transform: scale(var(--s, 1)); }
@media (prefers-reduced-motion: reduce) { .slide, .slide.on { transition: none; } }

.mid { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 30px; text-align: center; padding: 0 140px; }
.big { font-weight: 300; font-size: 76px; line-height: 1.12; letter-spacing: -.012em; max-width: 1240px; text-wrap: balance; }
.sub { font-size: 24px; font-weight: 500; color: var(--mute); }
.tagline { font-size: 38px; font-weight: 400; color: var(--mute); letter-spacing: -.004em; }  /* slide "hook": what Invariant is */
.faint { color: var(--faint); font-weight: 500; }
.top { margin-bottom: 8px; }
.title { font-weight: 300; font-size: 54px; line-height: 1.15; letter-spacing: -.008em; }
.end { font-weight: 300; font-size: 48px; margin-top: 6px; }
/* slide "summary": the name, the groups of lines in two columns, one closing line */
.recap { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; gap: 44px; padding: 0 150px; }
.recap .title { font-size: 72px; }
.recap .title .team { font-weight: 740; font-stretch: 122%; letter-spacing: .01em; }  /* the name, set as on the site header */
.did { display: grid; grid-template-columns: 1fr 1fr; gap: 40px 90px; }
.did ul { list-style: none; margin: 0; padding: 0 0 0 26px; border-left: 1px solid var(--rule); display: flex; flex-direction: column; gap: 16px; }
.did li { font-weight: 300; font-size: 36px; line-height: 1.22; color: var(--mute); }
.did li b { font-weight: 600; color: var(--ink); }
.did.one { grid-template-columns: 1fr; }
.did.one li { font-size: 46px; }
.did.one ul { gap: 22px; }
.recap .sub { font-size: 30px; }
.recap .why { margin-top: 14px; font-size: 38px; font-weight: 400; }  /* slide "built": why we built it */
.nb { white-space: nowrap; }
/* slide "hook": the 36 hours. A dot appears per hour when the slide comes on; the last one is the accent */
.hours { width: 250px; height: 250px; display: block; overflow: visible; margin-bottom: 4px; }
.hours circle { fill: var(--ink); opacity: .78; }
.hours .last { fill: var(--blue); opacity: 1; filter: drop-shadow(0 0 calc(var(--glow) * 5px) var(--blue)); }
.hours .head { fill: var(--blue); }
.slide.on .hours circle:not(.head) { animation: hour .5s both; animation-delay: calc(.35s + var(--i) * .115s); }
@keyframes hour { from { opacity: 0; transform: scale(.2); } }
.hours circle:not(.head) { transform-box: fill-box; transform-origin: center; }
@media (prefers-reduced-motion: reduce) { .slide.on .hours circle:not(.head) { animation: none; } .hours .head { display: none; } }
.site { display: flex; align-items: center; gap: 26px; margin-top: 34px; font-size: 34px; font-weight: 500; color: var(--mute); }
.qr { width: 150px; height: 150px; display: block; }
.limits { list-style: none; margin: 0; padding: 0; font-weight: 300; font-size: 68px; line-height: 1.3; letter-spacing: -.01em; }
.head { position: absolute; left: 96px; top: 72px; z-index: 1; }
.head h2 { font-weight: 300; font-size: 54px; line-height: 1.1; }
.head .sub { margin-top: 12px; }
.sub .team, .tagline .team { font-weight: 740; font-stretch: 122%; letter-spacing: .02em; color: var(--blue); }  /* the team's name, set as on the site's header */

.photo { border-radius: 2px; overflow: hidden; }
.photo img { display: block; width: 100%; height: 100%; object-fit: cover; }
.photo.cook { width: 400px; height: 436px; border-radius: 28px; }
/* slide "powered": what powered the RL training beside what powered the team, two equal columns */
.versus { position: absolute; inset: 0; display: grid; grid-template-columns: 1fr 1fr; align-items: center; padding: 0 120px; text-align: center; }
.versus > div { display: flex; flex-direction: column; align-items: center; gap: 18px; }
.versus > div + div { border-left: 1px solid var(--rule); }
.versus .by { color: var(--faint); margin-top: 22px; }
.versus .gpus { font-weight: 300; font-size: 84px; line-height: 1.1; letter-spacing: -.012em; }
.versus .days { font-weight: 300; font-size: 56px; line-height: 1.1; color: var(--mute); }
.versus .who { font-weight: 300; font-size: 44px; line-height: 1.1; }
.photo.meditate { width: 640px; height: 480px; }
.photo.empty { border: 1px dashed var(--faint); opacity: .7; display: flex; align-items: center; justify-content: center; }
.photo.empty span { font-size: 22px; font-weight: 500; color: var(--faint); }

.fig-frame { position: absolute; border: 0; background: var(--paper); pointer-events: none; color-scheme: normal; }
.fig-frame.harness { left: 40px; top: 215px; width: 1100px; height: 600px; }
.fig-frame.tree { left: 0; top: 0; width: 1600px; height: 900px; }
.fig-frame.climb { left: 370px; top: 200px; width: 860px; height: 680px; }
/* under the climb: a faint slider of board time and a half-speed button, clear under the pointer */
.replay { position: absolute; left: 430px; top: 858px; width: 740px; display: flex; align-items: center; gap: 18px; opacity: .22; transition: opacity .2s ease; z-index: 1; }
.replay:hover, .replay:focus-within { opacity: .95; }
.seek { flex: 1; min-width: 0; height: 24px; margin: 0; background: none; -webkit-appearance: none; appearance: none; cursor: pointer; --p: 0%; }
.seek::-webkit-slider-runnable-track { height: 2px; border-radius: 1px; background: linear-gradient(to right, var(--ink) var(--p), var(--faint) var(--p)); }
.seek::-moz-range-track { height: 2px; border-radius: 1px; background: var(--faint); }
.seek::-moz-range-progress { height: 2px; background: var(--ink); }
.seek::-webkit-slider-thumb { -webkit-appearance: none; width: 12px; height: 12px; margin-top: -5px; border-radius: 50%; background: var(--ink); }
.seek::-moz-range-thumb { width: 12px; height: 12px; border: 0; border-radius: 50%; background: var(--ink); }
.rate { font: inherit; font-size: 15px; font-weight: 560; color: var(--ink); background: none; border: 1px solid var(--faint); border-radius: 999px; padding: 3px 12px; cursor: pointer; }
.rate[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.fig-frame.wide { left: 220px; top: 205px; width: 1160px; height: 650px; }
/* the sponsors slide: two scenes side by side, each drawn at 580 x 446 and shown 1.04 times larger, with the towers of /pastdev as a smaller third picture on the right */
.fig-frame.sponsor { top: 228px; width: 580px; height: 446px; transform: scale(1.04); transform-origin: 0 0; background: transparent; }
.fig-frame.s-exa { left: 40px; } .fig-frame.s-past { left: 652px; }
/* the side note: the towers of /pastdev (recall against grep), smaller, to the right of the memory scene */
.fig-frame.s-tw { left: 1246px; top: 262px; width: 324px; height: 430px; background: transparent; }
.spon-note { position: absolute; left: 1246px; top: 706px; width: 324px; text-align: center; font-size: 17px; font-weight: 500; color: var(--mute); }
.spon { position: absolute; top: 772px; width: 603px; display: flex; align-items: center; justify-content: center; gap: 20px; font-size: 21px; white-space: nowrap; font-weight: 500; color: var(--mute); }
.spon.s-exa { left: 40px; } .spon.s-past { left: 652px; }
.spon b { font-weight: 640; color: var(--ink); }
.fig-frame.fixes { left: 180px; top: 140px; width: 1240px; height: 694px; }
.fig-frame.gapfig { left: 100px; top: 58px; width: 1400px; height: 784px; }
.fig-frame.review { left: 180px; top: 128px; width: 1240px; height: 744px; }
.top-title { position: absolute; left: 0; right: 0; top: 44px; text-align: center; }  /* a centred title over a picture that fills the slide */
.wins { position: absolute; left: 1160px; top: 235px; width: 400px; list-style: none; margin: 0; padding: 0 0 0 22px;
  border-left: 1px solid var(--rule); display: flex; flex-direction: column; gap: 14px; }
.wins li { font-size: 22px; font-weight: 400; line-height: 1.25; color: var(--ink); }
.step { opacity: 0; transform: translateY(6px); transition: opacity .3s ease, transform .3s ease; }
.step.in { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .step { transition: none; } }
.tools { position: absolute; left: 0; right: 0; bottom: 56px; display: flex; justify-content: center; gap: 72px; font-size: 22px; font-weight: 560; color: var(--mute); }
.tools span { display: inline-flex; align-items: center; gap: 14px; }
.logo { height: 24px; width: auto; fill: var(--ink); }
.logo-exa { height: 22px; }
.tools .word { font-size: 25px; font-weight: 640; color: var(--ink); }  /* a sponsor with no logo in architecture.py */

.sheets { display: flex; gap: 60px; margin-top: 30px; }  /* --n: the number of papers, so any number fits the slide */
/* a paper is white in both themes: the sheet carries the light values of these four tokens */
.sheet { --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --rule: #d3d9de; color: var(--ink);
  width: min(330px, calc((1380px - (var(--n) - 1) * 60px) / var(--n))); aspect-ratio: 330 / 427; background: var(--sheet); border: 1px solid var(--rule); padding: 100px 30px 0; box-sizing: border-box; text-align: left; display: flex; flex-direction: column; gap: 10px; }
.sheet b { font-size: 26px; font-weight: 560; line-height: 1.2; }
.sheet span { font-size: 16px; font-weight: 500; color: var(--mute); }
.sheet .lines { margin-top: 26px; display: flex; flex-direction: column; gap: 13px; }
.sheet .lines i { display: block; height: 2px; background: var(--rule); }

.count { position: fixed; left: 18px; bottom: 12px; font-size: 13px; color: var(--faint); opacity: .7; z-index: 2; }
/* the theme button, top right: the same switch as the key t */
.theme { position: fixed; right: 14px; top: 12px; z-index: 2; width: 36px; height: 36px; padding: 8px; border: 0; border-radius: 50%;
  background: none; color: var(--faint); opacity: .7; cursor: pointer; }
.theme svg { display: block; width: 20px; height: 20px; }
.theme:hover, .theme:focus-visible { color: var(--ink); opacity: 1; }
.theme:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }

@page { size: 13.333in 7.5in; margin: 0; }
@media print {
  .step { opacity: 1; transform: none; }
  html, body { height: auto; overflow: visible; }
  .slide.on .hours circle:not(.head) { animation: none; }
  .hours .head { display: none; }
  .count, .theme, .replay { display: none; }
  .slide { position: relative; inset: auto; display: block; width: 13.333in; height: 7.5in; overflow: hidden;
    opacity: 1; visibility: visible; transition: none; break-after: page; page-break-after: always; }
  .slide:last-child { break-after: auto; page-break-after: auto; }
  .box { transform: scale(.8) !important; transform-origin: 0 0; }
}
</style>
</head>
<body>
<main class="deck" id="deck">
__SLIDES__
</main>
<div class="count" id="count" aria-live="polite"></div>
<button class="theme" id="theme" type="button"><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7.25" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 2.75a7.25 7.25 0 0 0 0 14.5z" fill="currentColor"/></svg></button>
<script>
const SLIDES = [...document.querySelectorAll(".slide")], IDS = SLIDES.map(s => s.id);
let cur = -1;
const themeNow = () => document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

/* the box fills the window at 16:9 */
function fit() { document.documentElement.style.setProperty("--s", Math.min(innerWidth / 1600, innerHeight / 900)); }
addEventListener("resize", fit); fit();

/* the embedded pictures get the deck's theme, at load and on every change */
const frames = [...document.querySelectorAll("iframe[data-fig]")];
const syncFrame = f => { const d = f.contentDocument; if (d && d.documentElement) d.documentElement.dataset.theme = themeNow(); };
frames.forEach(f => { f.addEventListener("load", () => syncFrame(f)); f.src = `/demo/fig/${f.dataset.fig}?theme=${themeNow()}`; });
function toggleTheme() {
  const t = themeNow() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = t;
  try { localStorage.setItem("demo-theme", t); } catch (e) { /* storage blocked: the choice lasts until the page closes */ }
  frames.forEach(syncFrame);
  labelTheme();
}
const themeButton = document.getElementById("theme");
function labelTheme() { const to = themeNow() === "dark" ? "light" : "dark"; themeButton.setAttribute("aria-label", `Switch to ${to} theme`); themeButton.title = `Switch to ${to} theme`; }
themeButton.addEventListener("click", () => { toggleTheme(); themeButton.blur(); });  // blur: Space then steps the deck again
labelTheme();

/* The climb replays at twice the speed its page was designed for (0.5x: the designed speed); the slider moves its board time. */
document.querySelectorAll(".replay").forEach(box => {
  const f = box.parentNode.querySelector("iframe"), seek = box.querySelector(".seek"), rate = box.querySelector(".rate");
  const api = () => f.contentWindow && f.contentWindow.replay;
  let slow = false, held = false;
  const setSpeed = () => { const r = api(); if (r) r.speed(slow ? 1 : 2); };
  f.addEventListener("load", setSpeed);
  seek.addEventListener("pointerdown", () => { held = true; });
  seek.addEventListener("input", () => { const r = api(); if (r) r.seek(seek.value / 1000); seek.style.setProperty("--p", seek.value / 10 + "%"); });
  seek.addEventListener("change", () => { held = false; seek.blur(); });  // the arrow keys step the slides again
  rate.addEventListener("click", () => { slow = !slow; rate.setAttribute("aria-pressed", slow); setSpeed(); rate.blur(); });
  setInterval(() => { const r = api(); if (r && !held) { seek.value = Math.round(r.at() * 1000); seek.style.setProperty("--p", seek.value / 10 + "%"); } }, 200);
});

function show(i, push) {
  i = Math.max(0, Math.min(SLIDES.length - 1, i));
  if (i === cur) return;
  if (cur >= 0) SLIDES[cur].classList.remove("on");
  if (cur >= 0) SLIDES[i].querySelectorAll("iframe[data-replay]").forEach(f => f.contentWindow.location.reload());  // its picture draws itself again
  SLIDES[i].querySelectorAll(".step").forEach(x => x.classList.remove("in"));  // its points appear again, one per click
  SLIDES[i].classList.add("on"); cur = i;
  SLIDES.forEach((s, k) => s.setAttribute("aria-hidden", k === i ? "false" : "true"));
  document.getElementById("count").textContent = `${i + 1} / ${SLIDES.length}`;
  const h = "#" + IDS[i];
  if (push && h !== location.hash) history.pushState(null, "", h);
}
/* A slide with .step items shows one more per forward step and hides one per back step before the slide changes. */
function step(d) {
  const items = [...SLIDES[cur].querySelectorAll(".step")], n = items.filter(x => x.classList.contains("in")).length;
  if (d > 0 && n < items.length) { items[n].classList.add("in"); return true; }
  if (d < 0 && n > 0) { items[n - 1].classList.remove("in"); return true; }
  return false;
}
const fromHash = () => { const k = IDS.indexOf(decodeURIComponent(location.hash.slice(1))); show(k < 0 ? 0 : k, false); };
addEventListener("popstate", fromHash);
addEventListener("hashchange", fromHash);

document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key;
  if (k === "ArrowRight" || k === " " || k === "PageDown") { e.preventDefault(); if (!step(1)) show(cur + 1, true); }
  else if (k === "ArrowLeft" || k === "PageUp") { e.preventDefault(); if (!step(-1)) show(cur - 1, true); }
  else if (k === "Home") { e.preventDefault(); show(0, true); }
  else if (k === "End") { e.preventDefault(); show(SLIDES.length - 1, true); }
  else if ((k === "t" || k === "T") && !e.repeat) { e.preventDefault(); toggleTheme(); }
  else if ((k === "f" || k === "F") && !e.repeat) { e.preventDefault(); if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); }
  else if ((k === "p" || k === "P") && !e.repeat) { e.preventDefault(); window.print(); }
});
document.addEventListener("click", e => {
  if (e.target.closest("a, button, input")) return;  // the paper sheets open their PDF; the theme button switches the theme
  const x = e.clientX / innerWidth;
  if (x > 2 / 3) { if (!step(1)) show(cur + 1, true); } else if (x < 1 / 3) { if (!step(-1)) show(cur - 1, true); }
});
fromHash();
</script>
</body>
</html>
"""


def page(papers):
    """The deck, with the paper file names (view.PAPERS) written in."""
    body = "\n".join(f'<section class="slide" id="{sid}" aria-label="Slide {i + 1}"><div class="box">{inner}</div></section>'
                     for i, (sid, inner) in enumerate(slides(list(papers))))
    return (TEMPLATE.replace("__FONT__", FONT).replace("__THEME_JS__", THEME_JS).replace("__TOKENS__", TOKENS)
            .replace("__SLIDES__", body))
