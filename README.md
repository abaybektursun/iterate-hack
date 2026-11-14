# iterate_invariant

Repository for the iterate_invariant hackathon. Several people, each running Claude agents with
subagents, work on one research direction. The agents coordinate through two shared stores:

| Store | Holds | Tool |
|---|---|---|
| Board (Modal Dict `iterate-board`) | ideas, skills, knowledge, results, current work; votes and comments | `uv run tools/board.py` |
| Memory (past.dev project) | specific findings from papers and posts; everyone's Claude Code sessions | `uv run tools/paper.py`, `python3 tools/recall.py` |
| GPU pool (Modal app `iterate-pool`) | every GPU job, queued and capped team-wide | `uv run tools/gpu.py` |

## GPU pool

```
uv run tools/gpu.py submit h100 --hours 2 -- 'python exp/train.py --lr 3e-4'   # prints the job id
uv run tools/gpu.py ls                    # the whole team's jobs of the last 3 hours, any state
uv run tools/gpu.py wait <job-id>         # blocks until the job ends; prints its state and last 20 log lines
uv run tools/gpu.py logs <job-id> 50      # last 50 lines, updated every 30 s
uv run tools/gpu.py kill <job-id>
mkdir -p runs && modal volume get iterate-runs <job-id> runs/
```

Classes and team-wide caps (`infra/pool.py`): `h100` 4, `b200` 2, `cpu` 8 containers. A job over its
class's cap waits in Modal's queue. Each person can have 4 jobs queued or running. A job runs the current
commit, which must be clean and pushed, from the repository root, and writes its outputs to `$OUT_DIR`.
It is killed at `--hours` (default 2). The command is one shell string, so `&&` and pipes work. A cpu job
starts within seconds when the class has room. The image pins torch, transformers, accelerate, safetensors,
numpy, datasets, scikit-learn, scipy, pandas and matplotlib. For anything else, install it in the command
(`'pip install -q einops && python exp/train.py'`), or add it to `infra/pool.py` and run
`modal deploy infra/pool.py` while no jobs are queued.

## Board

```
uv run tools/board.py post work "probing layer 12 of model X for feature Y"   # prints work-3fa21c
uv run tools/board.py ls                  # every open item, highest score first, one line each
uv run tools/board.py ls result
uv run tools/board.py show result-8b1c48
uv run tools/board.py up result-8b1c48    # or down; one vote per person
uv run tools/board.py comment result-8b1c48 "reproduced on seed 2: 0.41"   # at most 280 characters
uv run tools/board.py done work-3fa21c
```

Claim an idea by posting a `work` item that names its id, and close it with `done` when the work ends.
`post` then prints any other open work item that names the same id. If one is older than yours, close
yours and pick another idea. Post each result as a `result` item with its number and the path or URL of its
artifact. Each item, vote and comment is stored under its own key, so any number of agents can write at
the same time. Each command takes about 0.2 s. Modal deletes an entry after 7 days with no reads or
writes. Requires membership in the team's Modal workspace (`modal token new`).

## Findings from papers and posts

Agents tend to read the abstract and the headings and guess the results. Here a paper is downloaded and
read in full, appendix included, and only specific results go into memory.

1. Download: `uv run tools/paper.py fetch 2401.12345` (arXiv), or
   `uv run tools/paper.py fetch <url> --title "<title>" --date YYYY-MM-DD` (any PDF or web page).
   This writes `papers/<paper-id>.txt` with `[page N]` markers.
2. Read the whole text file, appendix included. Do it in a subagent, so the paper does not fill the
   main agent's context; the subagent returns only the ids of the findings it added.
3. Add each relevant result as one finding: the setup, the numbers, and what it means for our
   question, with the exact words from the paper that support it:

   ```
   uv run tools/paper.py add arxiv-1706.03762 --where "Section 6.1, Table 2" \
     --quote "establishing a new state-of-the-art BLEU score of 28.4" \
     "Transformer (big) reaches 28.4 BLEU on WMT14 En-De, 2.0 above the best previous model."
   ```

   `add` refuses a quote that is not in the paper's text, or that is shorter than 30 letters and digits.
4. Before starting on an idea, search: `python3 tools/recall.py "<the idea, in the field's own terms>"`.

## past.dev setup (once per person)

Each Claude Code session opened in this repository is also sent to the past.dev project when it ends,
so `recall.py` finds what other agents said and decided. Sessions in your other folders are not sent:
the plugin is enabled in this repository's `.claude/settings.json` only. Nothing is recalled
automatically. What is sent: typed prompts and the agent's prose replies. Tool calls, their output, file
contents and diffs are never sent. Strings that look like keys are redacted before they leave.

1. Get a project key (`past_sk_...`) from the organizer, privately.
2. Open Claude Code in this repository and trust the folder. Accept the prompt to install the
   `pastdotdev` marketplace and plugin.
3. In a text editor (not in a chat), create `~/.past/config.json`:

   ```json
   { "apiKey": "past_sk_...", "identity": "you@example.com", "recall": false }
   ```

   Then `chmod 600 ~/.past/config.json`. `"recall": false` stops the plugin from adding memories to
   every prompt. The tools read the same file. Never paste the key into a chat or commit it.
4. Run `/pastdotdev:status`: it should show the key, your identity, and recall off.

`~/.past/config.json` is one file per machine. If you already use past.dev for another project, this
replaces that connection. Codex users: see https://github.com/pastdotdev/codex-plugin.
