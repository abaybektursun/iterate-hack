# sitelab: interactive 3D pictures of the team's work

Question: which pictures of the agents and the work, built only from real data, are worth a place on the team site?
Twelve prototypes, one idea each. Live at https://monitor.invariant.team/lab/ (`tools/view.py` serves this folder at
`/lab/`; `infra/monitor/deploy.sh` puts `index.html` and each prototype's `index.html` and `data.json` into the zip).

Local: `python3 studies/sitelab/serve.py` then http://127.0.0.1:8777/ (passes `/data` through to the site).

| Prototype (`prototypes/<slug>/`) | Picture | Data |
|---|---|---|
| score-terrain | posted scores as a plaster relief, one benchmark at a time | live `/data` scores |
| problem-field | one bead per problem, moving between right and wrong under two configurations | per-problem rows (`build.py`) |
| trace-ribbons | each agent transcript as a wire, tool calls as beads | one laptop's Claude Code transcripts, labels redacted (`build.py`) |
| physics-board | the board as rigid bodies in a tray | live `/data` |
| weight-space | every model made by weight arithmetic, with a dial over the edit size | rlneurons readouts (`build.py`) |
| lineage | which item cites which, regrown over time | board table, finding pages, theory rounds (`build.py`) |
| token-flow | answers as grain streams that finish or hit the token cap | rows of hard328 at cap 16,384 and 32,768 (`build.py`) |
| forecast-range | theories' forecasts against the measured numbers, round by round | studies/theory rounds and forecast runs (`build.py`) |
| time-helix | items, messages, commits, GPU jobs and scores on one helix, one turn per hour | board, events, git log, job records (`build.py`) |
| crystal | one crystal per result, grown by a stated rule | live `/data`, finding pages (`build.py`) |
| repo-city | the repository's history as a model city | `git log --numstat` (`build.py`) |
| model-interior | the 32 layers with the RL weight change, its top directions and the loop neurons | rlneurons and cleanneurons readouts (`build.py`) |

Each `data.json` is rebuilt with `uv run studies/sitelab/prototypes/<slug>/build.py`. Checked only as headless stills:
motion, hover, drag and frame rate have not been watched in a browser. The pages use a serif face and a brass accent,
which differs from the site's rules in `.claude/skills/site-ui/SKILL.md`.
