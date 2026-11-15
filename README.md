# iterate-hack

Repository for the SF AI Research Hackathon (November 14-15, 2026). Several people, each running Claude agents with
subagents, work on one research direction, described in [`DIRECTION.md`](DIRECTION.md). The rules for agents are in
`AGENTS.md`. The code, inputs and readouts of the experiments the direction starts from (RLN-3, RLN-4: graders v1-v3, the
opening cue, the vLLM jobs and their Modal app) are in [`studies/rlneurons/`](studies/rlneurons/README.md).

| Store | Holds | Tool |
|---|---|---|
| Board (DynamoDB table `iterate-board`, Abay's AWS) | ideas, skills, knowledge, results, current work; votes and comments | `uv run tools/board.py` |
| Messages (same DynamoDB table) | realtime messages between agents, by channel | `uv run tools/msg.py` |
| Events and traces (S3 bucket `iterate-hack-team-769063704696`, Abay's AWS) | one record per tool command; agent transcripts | written by the tools; `uv run tools/traces.py` |
| Memory (past.dev project) | specific findings from papers and posts; board results and knowledge; everyone's Claude Code sessions | `uv run tools/paper.py`, `python3 tools/recall.py` |
| Modal (your own workspace, app `iterate-runner`) | your GPU jobs, their outputs and the model cache | `uv run tools/gpu.py` |
| vast.ai (your own account) | your private GPU rentals | `python3 tools/vast.py` |

## Setup (once per person)

Do the steps in order. Credit codes and claim links are on the hackathon platform's home page (API Keys &
Credits); they are not copied here, because this repository becomes public. Type every key in your own terminal
or a text editor, never into an agent chat, and never commit one.

| # | Provider | Shared or yours | Needed for |
|---|---|---|---|
| 1 | GitHub | shared repository | the code |
| 2 | Team AWS key | shared, from Abay | the board, messages, events and traces; ECR images |
| 3 | Modal | yours ($250 credits) | GPU jobs with `tools/gpu.py` |
| 4 | Hugging Face | yours | gated models on Modal and vast.ai |
| 5 | vast.ai | yours (optional) | cheaper private GPUs with `tools/vast.py` |
| 6 | AWS (DynamoDB, S3 and ECR) | shared, until Sunday 23:59 PST | the board, events and traces; prebuilt images with model weights, on vast.ai |
| 7 | past.dev | shared team project | `tools/paper.py`, `tools/recall.py`, session memory |
| 8 | Exa | yours ($50 credits) | web and literature search by agents (`tools/exa.py`) |
| 9 | Devin | yours (credits; the default model is free) | side work handed off by agents (`tools/devin.py`) |
| 10 | Tinker, OpenAI | yours | optional; no tool here uses them |

### 1. GitHub and the team store

```
brew install gh uv                 # or your platform's installers
gh auth login
git clone https://github.com/abaybektursun/iterate-hack.git && cd iterate-hack
git config user.email              # must be set: the part before @ is your name on the board and in job ids
```

Accept the invite to `abaybektursun/iterate-hack`. It is the only repository.

### 2. Team AWS key

Abay sends you two values privately (an access key id and a secret). Install the AWS CLI and store them under the
profile name `iterate-ecr`, in your own terminal:

```
brew install awscli
aws configure --profile iterate-ecr      # paste the two values; region us-east-1; output format: leave empty
```

Check: `uv run tools/board.py ls` exits without an error (it prints nothing when the board is empty). Every tool
here uses this profile; details in step 6.

### 3. Modal (your own workspace)

1. Create an account at https://modal.com and claim the $250 with the link on the hackathon platform.
2. Then:

```
uv tool install modal
modal token new                                      # opens the browser; pick your own workspace
modal secret create hf-token HF_TOKEN=<your token>   # the Hugging Face token of step 4
modal deploy infra/runner.py                         # your job runner; repeat after changing requirements.txt
```

Check: `uv run tools/gpu.py submit cpu --hours 0.1 -- 'python -c "import torch; print(torch.__version__)"'`,
then `uv run tools/gpu.py wait <job-id>` prints `done` and `2.15.0+cu132`. Nothing on Modal is shared: each
person's jobs, outputs and model cache are in their own workspace.

### 4. Hugging Face

Create a read token at https://huggingface.co/settings/tokens and accept the license of each gated model you
need on its model page. Modal reads it from the secret `hf-token` (step 3). On vast.ai, pass it in the command:
`'HF_TOKEN=<token> python exp/run.py'`.

### 5. vast.ai (optional, your own account)

```
uv tool install vastai
vastai set api-key <key>           # from https://cloud.vast.ai/manage-keys/
```

Add your ssh public key on the same page (`cat ~/.ssh/id_ed25519.pub`; create one with `ssh-keygen -t ed25519`),
and add credit to the account. Check: `python3 tools/vast.py offers --ram 24` lists offers.

### 6. AWS (shared: the team store and the ECR images)

The profile `iterate-ecr` of step 2 is a key in Abay's AWS account. It does two things:

- The team store: the DynamoDB table `iterate-board` holds the board, and the S3 bucket
  `iterate-hack-team-769063704696` holds the events and the traces. The key can read and write both and cannot
  delete from either.
- The prebuilt images (table under Compute, Images) in ECR, pull only. Check:
  `aws ecr describe-images --repository-name shackleton --profile iterate-ecr --query 'length(imageDetails)'`
  prints a number.

The key stops working Sunday 2026-11-15 at 23:59 PST.

### 7. past.dev (shared team memory)

Abay sends you the team's project key (`past_sk_...`) privately. In a text editor, create `~/.past/config.json`:

```json
{ "apiKey": "past_sk_...", "identity": "you@example.com", "recall": false }
```

Then `chmod 600 ~/.past/config.json`, open Claude Code in this repository, trust the folder, and accept the prompt
to install the `pastdotdev` marketplace and plugin. Check: `/pastdotdev:status` shows the key, your identity and
recall off, and `python3 tools/recall.py "test"` runs without an error. Details: "past.dev details" below. The
owner creates the team project once: sign up at https://past.dev, redeem the team credits with the code on the
hackathon platform, and create an API key.

### 8. Exa (your own key)

Sign up at https://dashboard.exa.ai, redeem the code from the hackathon platform, and create an API key. Put it
in your shell profile, not in the repository:

```
echo 'export EXA_API_KEY=<key>' >> ~/.zshrc && source ~/.zshrc
```

Agents use Exa through `tools/exa.py`, which calls Exa's HTTP API (`https://api.exa.ai`, docs:
https://docs.exa.ai). Claude Code, Codex and their subagents all run the same two commands; there is nothing to
install or approve. Do not use Exa's MCP server: it reads the key only when the agent starts, and returns 401 for
the whole session if the key was missing then.

```
python3 tools/exa.py search "<description of the page you want>" [--n 5] [--since YYYY-MM-DD] [--domain arxiv.org]
python3 tools/exa.py fetch <url> [<url> ...]
```

- `search` prints each result's date, title, URL and highlights (the passages that match the query), then the
  cost. Exa searches by meaning, so describe the page you want in a full phrase ("paper that measures restart
  sampling on MATH-500"), not keywords. `--since` keeps pages published on or after a date; `--domain` keeps one
  domain and can be repeated.
- `fetch` prints the full text of each URL. Highlights only locate a page: read it with `fetch`, in a subagent
  when it is long, before you cite it.
- One search costs about 0.007 USD and one fetched page about 0.001 USD, from your own credits. The calls show in
  your Exa dashboard, which the Exa challenge needs.

The tool takes `EXA_API_KEY` from its environment and, when the agent started before you set the key, from your
shell profile, so a running session needs no restart. Check: `python3 tools/exa.py search "test" --n 1` prints
one result.

### 9. Devin (your own login)

```
curl -fsSL https://cli.devin.ai/install.sh | bash     # or: brew install --cask devin-cli
devin auth login                                      # opens the browser
```

Check: `devin auth status` prints "Logged in", and `python3 tools/devin.py ask "Which file holds the rules for
agents?"` answers `AGENTS.md`. Agents hand side work to Devin with `tools/devin.py`: see "Devin" below.

### 10. Tinker, OpenAI (optional)

Claim each on the hackathon platform. Keep the keys in your shell profile (`TINKER_API_KEY`, `OPENAI_API_KEY`).
No tool here uses them.

### Agents

Claude Code reads `CLAUDE.md`, which loads `AGENTS.md`. Codex needs network access and a writable uv cache:
see "Codex agents" below.

## Compute

There are two ways to run a job, and both are paid by you. Both run one clean, pushed commit from the repository
root, with the root first on `PYTHONPATH`, write outputs to `$OUT_DIR`, and have the same package versions
(`requirements.txt`).

| | Modal (your workspace) | vast.ai (your account) |
|---|---|---|
| Who pays | your Modal credits | your vast.ai balance |
| GPUs | H100 (4 at once), B200 (2), cpu (8) | any single GPU on the market, often $0.15 to $0.70/h for 24 to 48 GB |
| Start | about 10 s (measured for cpu and H100) | 2 to 4 min for a new box (measured 137 to 232 s); about 4 s for the next job on the same box |
| Model weights | cached in your Volume `iterate-hf-cache`: each model downloads once | download on the box once; later jobs on that box reuse it |
| Results | your Volume `iterate-runs`; copy out with `gpu.py get` | on the box until you copy them out with `vast.py get` |
| Use it for | batch jobs, H100/B200, many jobs in parallel | interactive work, many small runs, cheaper GPUs |

Teammates cannot read your Volumes or your box. To share a result, commit its small files (metrics, samples) and
name the path in the board item.

### Modal

```
uv run tools/gpu.py submit h100 --hours 2 -- 'python exp/train.py --lr 3e-4'   # prints the job id
uv run tools/gpu.py ls                    # your jobs of the last 3 hours, any state
uv run tools/gpu.py wait <job-id>         # blocks until the job ends; prints its state and last 20 log lines
uv run tools/gpu.py logs <job-id> 50      # last 50 lines, updated every 30 s
uv run tools/gpu.py get <job-id>          # copies $OUT_DIR (outputs and log) to runs/<job-id>/
uv run tools/gpu.py kill <job-id>
uv run tools/cycle.py --hours 24          # turnaround: per job queue wait and run minutes; per work item claim -> first job -> last job -> close
```

`cycle.py` is what the team-meta-review skill starts its turnaround review from. It matches jobs to work items by git
branch, so a work item's jobs are counted only when they were submitted from the branch that posted it.

Put the command in single quotes, so `$OUT_DIR` is expanded on the job's machine and not on yours; for a command
with its own quotes, put it in a script in the repository and run that. A job over its class's limit waits in Modal's queue. A job is killed at `--hours` (default 2). The command is one
shell string, so `&&` and pipes work. Install extra packages in the command
(`'pip install -q einops && python exp/train.py'`), or add them to `requirements.txt` and run
`modal deploy infra/runner.py` again. The limits are the `max_containers` values in `infra/runner.py`.

### vast.ai

```
python3 tools/vast.py offers --ram 48             # cheapest single-GPU offers with at least 48 GB
python3 tools/vast.py up <offer-id> <offer-id> --hours 3   # rent both, keep the first good box; it destroys itself after 3 h
python3 tools/vast.py run <instance-id> -- 'python exp/run.py'     # prints the job id
python3 tools/vast.py wait <instance-id> <job-id>   # blocks until the job ends; prints its exit code and last 20 lines
python3 tools/vast.py logs <instance-id> <job-id> 50
python3 tools/vast.py get <instance-id> <job-id>  # copies $OUT_DIR (outputs and log) to runs/<job-id>/
python3 tools/vast.py ls                          # your instances, state and $/h
python3 tools/vast.py down <instance-id>
```

Setup once: `uv tool install vastai`, then `vastai set api-key <key>` in your own terminal, then add your ssh public
key at https://cloud.vast.ai/manage-keys/.

- Rent one box per working session and send every job to it. A new box costs 2 to 4 minutes; the next job on a
  box that is already up starts in seconds, and the model is already in its cache.
- Give `up` two or three offers. It rents all of them, keeps the first box that answers ssh and downloads 200 MB
  from Hugging Face at 20 MB/s or more, and destroys the others within seconds (they cost a cent or less). 9 of our
  32 earlier rentals were slow or broken hosts; with two offers one bad host no longer costs a retry.
- The deadline runs on the box with the instance's own key, so it fires with your laptop closed. Copy results out
  first: destroying deletes the disk. Stopped instances still bill storage, so `down` destroys.
- `offers` sorts by $/h and shows each host's price per GB downloaded. For a large model, add the download: 30 GB
  at $0.039/GB is $1.17.

### Images

| Image | Where | Contents |
|---|---|---|
| Modal image | `infra/runner.py` | Debian, Python 3.12, `requirements.txt` (torch 2.15.0, transformers 5.22.2, ...) |
| `pytorch/pytorch:2.15.0-cuda13.2-cudnn9-runtime` | vast.ai default | torch 2.15.0; `up` installs `requirements.txt` on top |
| ECR `shackleton:<tag>` | vast.ai, `up --image` | older images from another project, with model weights inside (below) |

The ECR images are in Abay's AWS account. Pull access ends **Sunday 2026-11-15, 23:59 PST**. Each pull is billed
to that account at about $0.09 per GB, so use an image only when its model is the one you need, and keep the box.

| Tag | Model weights inside | Size | torch / transformers |
|---|---|---|---|
| `v1-anchor-gemma2b` | google/gemma-2b | 8.3 GB | 2.11.0 / 5.15.0 |
| `v2-gauge` | google/paligemma-3b-pt-224 | 15.3 GB | 2.11.0 / 5.15.0 |
| `v1-7b` | Qwen/Qwen2.5-7B | 16.3 GB | 2.11.0 / 5.15.0 |
| `v1-14b` | Qwen/Qwen2.5-14B | 27.6 GB | 2.11.0 / 5.15.0 |
| `v1-32b` | Qwen/Qwen2.5-32B | 55.9 GB | 2.11.0 / 5.15.0 |
| `v1-72b` | Qwen/Qwen2.5-72B | 117.8 GB | 2.11.0 / 5.15.0 |
| `n13-v1` | allenai/Olmo-3-1025-7B (two revisions), allenai/Olmo-3.1-7B-RL-Zero-Math | 41.9 GB | 2.12.0 / 5.9.0 |
| `mdl-v1` | none (dependencies only) | 3.3 GB | 2.12.0 / 5.9.0 |

In the `v1-*` and `v2-gauge` images the weights are in `/models/<name>/`. In `n13-v1` they are in the image's
Hugging Face cache (`$HF_HOME`). All of them set `HF_HUB_OFFLINE=1`; unset it in the command to download anything
else. The pinned versions differ from `requirements.txt`, and `up` does not change them.

```
python3 tools/vast.py up <offer-id> --image 769063704696.dkr.ecr.us-east-1.amazonaws.com/shackleton:v1-7b
```

Setup for ECR: the AWS profile `iterate-ecr` (Setup, step 2). Pick a host with fast download (`offers` shows it): a 27.6 GB image took 38 minutes on a slow host.

## Board

```
uv run tools/board.py post work "probing layer 12 of model X for feature Y"   # prints work-3fa21c, announces it on all
uv run tools/board.py ls                  # the 50 open items with the highest score, one line each
uv run tools/board.py ls result --new --n 20   # the 20 newest results
uv run tools/board.py show result-8b1c48
uv run tools/board.py up result-8b1c48    # or down; one vote per person
uv run tools/board.py comment result-8b1c48 "reproduced on seed 2: 0.41"   # at most 280 characters
uv run tools/board.py done work-3fa21c "L12 probe: 0.41 AUC (n=500), studies/probe/results/l12/base-01"   # posts the result, closes, announces
uv run tools/board.py done work-3fa21c   # closes and announces, without a result
uv run tools/board.py done work-3fa21c "$(printf 'cue at T 0.6: 378/500 ...\nscore: base MATH-500 378/500 tokens 4690 | cue, T 0.6 / top-p 1.0')"   # a score line feeds the chart
uv run tools/board.py score result-8b1c48 base MATH-500 410/500 "cue, T 1.0 / top-p 1.0" --tokens 3933   # a score for a result already posted
uv run tools/board.py plain result-8b1c48 "<title>" "<what>" "<why>" ["<caveat>"]   # plain words for a result already posted
uv run tools/board.py plain result-8b1c48 "<title>" "<what>" "<why>" --score MATH-500 410/500   # for one score of it
uv run tools/board.py plain --file plain.json   # many at once; every entry is checked before any is written
```

People read the board page, and most of them have not seen the project. So every result says what it is in plain
words, on four lines of its text. `post` and `done` store them as `plain` rows, and the lines stay in the text:

```
title: Break vote ties with the shortest answer
what: When the 4 sampled answers have no majority, take the shortest answer that finished.
why: Not known yet.
caveat: The rule was chosen after reading the problems it fixes; the held-out estimate is 451.
score: base MATH-500 453/500 tokens 16034 | cue, T 1.0, vote over 4, ties to the shortest finished sample
```

| line | limit | content |
|---|---|---|
| `title:` | 60 characters | the change or the finding, without ids or settings |
| `what:` | 240 | one or two sentences: what was changed or tested |
| `why:` | 240 | one or two sentences: why the number moved or did not move. Only a mechanism that the result's text, its comments or its study README states or measures; otherwise exactly `Not known yet.` |
| `caveat:` | 240 | optional, one sentence: what weakens the number (fitted on the test set, one draw, within noise, a later result that refuted it) |

Lines before the first `score:` line describe the result as a whole. Lines directly after a `score:` line, up to the
next one, describe that one score: use them when one result holds several scores. A line over its limit stops the
post before anything is written. A result without `title:`, `what:` and `why:` is accepted, and `post` prints a
reminder to add them with `board.py plain`. `plain` writes the same rows for a result already posted, and a second
write for the same result and score replaces the first. The file of `plain --file` is a JSON list of
`{"item": "result-8b1c48", "title": "...", "what": "...", "why": "...", "caveat": "...", "score": {"benchmark": "MATH-500", "right": 410, "n": 500}}`,
where `caveat` and `score` are optional. A `score` must match a score row of that result.

To watch the board and the `all` channel in a browser: `uv run tools/view.py` (a local, read-only page on
http://127.0.0.1:8765). The page is written for people who have not seen the project, and it shows one line per
thing, with the rest one click away. At the top is one sentence for one benchmark (a switcher picks it, `?bench=`): the
best untrained-base score, the best RL score and the gap. Under it are the gap's 95% interval and what weakens the
score: that its last step is within noise, and the first sentence of that step's `caveat`. Then the hill-climbing
chart: every untrained-base score (`board.py score`) in the order posted with its 95% Wilson interval, the best so far
as a step line, and the best RL score as the target. A rise that does not clear the previous record's interval is drawn
faint, and the shaded area is the gap to RL. Beside the chart (under it on a narrow screen) is the ladder of record
steps, newest first, one line each: the gain in points, the step's `title`, previous best -> new best, and "within
noise". A click on a step opens it under its line (`?step=<right>`): what changed (`what`), why it works (`why`), is it
real (before and after, the interval test, the `caveat`), cost (tokens per problem, a link to the raw result) and its
settings (the configuration). A step takes these words from the `plain` row of its score, or from the row of its result
when that result holds no other step. Without a row it shows what its configuration gained and lost against the step
before, and the first sentence of the result's text. Below are two lists, one line per item: Now (open work, longest
idle first, red from 60 minutes) and Learned (results that set no record and announce nothing, by their `title`). One
row, More (`?more=`), opens one further list at a time: results that announce a page or a tool, ideas, knowledge and
skills, closed work, the messages on `all` (board.py's own announcements stay hidden until shown) and a timeline per
person. The board stores nothing that tells an announcement from a research result, so the page uses a rule on the
result's text (`ANNOUNCE` in `view.py`) and a few results may land in the wrong list. Terms such as "cue" or "cap hit"
are underlined with dots in the sentence, in an opened step and in the side panel; a click shows one sentence from
`tools/glossary.py`, where a term is added with its source. The page reads every 10 s while its tab is visible (an
unchanged board answers 304 with no body) and only rewrites what changed, so it does not move the text you are reading.
A click on an item opens its title, what, why and caveat, its full text, scores, comments and thread in a side panel
(`/#<item id>` is its link); filters are in the address too (`/?who=<name>&q=<text>`). Keys: `/` filter, `j` `k` move,
`1` `2` `3` jump to the record steps, Now and Learned, Enter opens, Esc closes, `?` lists them. The same page is public at https://monitor.invariant.team (`infra/monitor/`). The header of every page of
the site has three tabs: Board (this page, `/`), Design (`/architecture`) and Findings (`/findings`).

To see which finding raised the benchmark: `uv run tools/climb.py [benchmark] [--json]` lists, per benchmark, every
record step of that chart (a base score strictly above all earlier ones, the same rule), newest first: the gain in
points, previous best -> new best, the result id, who, the configuration and the step's title (from its `plain` row;
without one, the first line of the result's text that is not a `score:`, `title:`, `what:`, `why:` or `caveat:` line).

The tab Design is the page `/architecture` (`tools/architecture.py`): one picture of the shared work setup for
a first-time reader. The board is in the centre with one dot per live item, each person's agents are beside it with
threads to the board (the Claude mark for a Claude Code session, the OpenAI mark for a Codex session), the "Chat"
ring (messages) runs through every person's agents, and the "Retro" loop (self-review) goes around everything. What moves is real data, replayed: messages between people's agents, posts to the board. A click on a part
explains it, with live rows from the board (`/architecture#board` is its link); "Follow one result" steps through the
path of one result (arrow keys, Esc).

The tab Findings is the page `/findings` (`tools/findings.py`): one tile per finding, with a small lit icon, the
finding's title and one sentence. A tile opens the page of that finding. Every finding worth telling gets such a page:
`tools/finding_<slug>.py`, copied from `.claude/skills/finding-page/template.py`, is served at `/finding/<slug>` and
gets its tile with no other change; the module draws its own icon (`ICON`), and its panels start with "What is new" and
"Why it matters" (`.claude/skills/finding-page/SKILL.md` says when and how). `.claude/skills/site-ui/SKILL.md` holds
the rules for anything visible on the site.

`ls` and `read` print nothing when there is nothing to show; exit code 0 means they worked. `show` prints the
item's votes and comments. Claim an idea by posting a `work` item whose text contains its id, and close it with `done` when the work ends.
`post` then prints any other open work item that names the same id. If one is older than yours, close
yours and pick another idea. Post each result as a `result` item with its number and the path or URL of its
artifact. The board is a DynamoDB table. Every command reads and writes a fixed number of rows, so its time does not grow
with the board, and any number of agents can write at the same time. `ls` shows the top or newest `--n` items
(default 50), never the whole board.

## Messages

```
uv run tools/msg.py send all "328 at T 1.0 on base started: job abay-1114-1203-a1b2"   # everyone
uv run tools/msg.py send @samer.aslan "your grader change breaks exp/score.py line 40"  # one person's agents
uv run tools/msg.py send idea-3fa21c "taking the top-p half of this"                    # the thread on a board item
uv run tools/msg.py read                  # what arrived on `all` and `@<you>` since this agent last read
uv run tools/msg.py wait --timeout 300    # blocks until a message arrives (exit code 1 at the timeout)
```

In Claude Code, two hooks in `.claude/settings.json` put the team's state into the agent's context. At the start
of a session and after `/clear`, one prints the open work, the 10 newest board items and new messages. After tool
calls (at most every 20 s), the other runs `msg.py read` and adds new messages. All times are UTC. After changing a tool, run `python3 tools/selftest.py`:
it runs every board and message command as two agents against a separate test table.

A message reaches a waiting agent in under a second (measured: 0.2 s after the send returned). Each agent
session keeps its own read position, and never receives its own messages. Reading costs one query that returns
only new rows, so it stays fast at any total. The board is for what should last; messages are for coordination
in the next minutes. Messages stay in the table as part of the record.

## Devin

`tools/devin.py` hands side work to the Devin CLI (https://docs.devin.ai/cli), a second coding agent, so the
research does not wait for it: code fixes named in `meta/FAILURES.md`, chores, the analysis script for a running
job, and an independent review before a number is posted. When to use it and how to write a task:
`.claude/skills/devin/SKILL.md` (Codex: read that file).

```
python3 tools/devin.py ask "<question>"        read-only, in your checkout; waits and prints the answer
python3 tools/devin.py run <name> "<task>"     a change, in the background, in the worktree ../iterate-hack-devin-<name>
                                               on branch devin/<name>, cut from your HEAD; returns at once
python3 tools/devin.py ls                      every run: state, minutes, commits
python3 tools/devin.py wait <name>             block until the run ends, then print the report and the commits
python3 tools/devin.py show <name>             the same, without waiting
python3 tools/devin.py rm <name>               delete the worktree, the branch and the run record; refuses while
                                               the branch has work you did not merge (--force drops it)
```

- Devin runs on your laptop under your login with the model `swe-2-high`, free in the CLI until 2026-11-30.
  `--strong` uses `gpt-6-sol-high` and `--model <id>` any other (`devin models`), paid from your Devin credits.
- `ask` lets Devin read files and git history and change nothing. `run` lets it edit, run checks and commit in its
  own worktree. The tool tells it to start no job, post nothing to the board and push nothing; it reads `AGENTS.md`
  and skips the files written for Claude Code (`CLAUDE.md`, `.claude/`).
- Its report is a claim: read `git diff HEAD...devin/<name>`, run the check, then `git merge devin/<name>` and `rm`.
- Each run keeps `prompt.md`, `out.txt` and `meta.json` in `~/.cache/iterate-hack/devin/<name>/`.

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

## Telemetry and traces

Someone will analyze how the team worked, so every action leaves a record in the team store:

| Record | Where (`s3://iterate-hack-team-769063704696/` unless stated) | Written by |
|---|---|---|
| Every `board.py`, `gpu.py` and `paper.py` command: time, person, agent (claude-code or codex, with its session id, and whether it ran as a subagent), commit, full command line | `events/` | the tools, automatically, at once |
| Board items, votes and comments, with times; who closed each work item and when | the DynamoDB table `iterate-board` | `board.py` |
| Agent transcripts (Claude Code with subagents, Codex) | `traces/<who>/` | `uv run tools/traces.py push`, by each person |
| Every Modal job: submitter, commit, command, GPU, start and end times, exit code | `traces/<who>/jobs.json` | `gpu.py`, then `traces.py push` |

Claude Code runs `traces.py push` by itself: a hook starts it in the background every 10 minutes and at the end of a
session, and it uploads only changed transcripts (log: `~/.cache/iterate-hack/traces.log`). With Codex, run
`uv run tools/traces.py push` at the end of each working session. A transcript holds everything typed and
every tool output, including file contents and the instructions files the agent loaded. `push` replaces strings
that look like keys with `[REDACTED]`, but it catches common formats only. vast.ai rentals are recorded only on
your laptop, in `runs/vast/`. Read everything with `aws s3 sync s3://iterate-hack-team-769063704696/ team/`.

## Codex agents

Codex runs commands in a sandbox with no network, and every tool here needs the network. Start Codex in this
repository with network access and the uv cache inside the repository (the sandbox cannot write `~/.cache/uv`):

```
UV_CACHE_DIR=$PWD/.uv-cache codex -s workspace-write -c sandbox_workspace_write.network_access=true
```

Codex reads `AGENTS.md` for the rules; Claude Code reads the same file through `CLAUDE.md`.

## past.dev details

Each Claude Code session opened in this repository is also sent to the past.dev project when it ends,
so `recall.py` finds what other agents said and decided. Sessions in your other folders are not sent:
the plugin is enabled in this repository's `.claude/settings.json` only. Nothing is recalled
automatically. What is sent: typed prompts and the agent's prose replies. Tool calls, their output, file
contents and diffs are never sent. Strings that look like keys are redacted before they leave.

`~/.past/config.json` has this form, with permissions 600:

```json
{ "apiKey": "past_sk_...", "identity": "you@example.com", "recall": false }
```

`"recall": false` stops the plugin from adding memories to every prompt. The tools read the same file. It is one
file per machine: if you already use past.dev for another project, this replaces that connection. Codex users: see https://github.com/pastdotdev/codex-plugin.
