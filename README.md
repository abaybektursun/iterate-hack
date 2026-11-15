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
uv run tools/gpu.py deploy                           # your job runner; again whenever infra/runner.py changes
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
`uv run tools/gpu.py deploy` again. The limits are the `max_containers` values in `infra/runner.py`. The class
`short` takes jobs of `--hours 0.5` at most in a queue of their own; it holds no GPUs back by default, since
2 reserved H100s sat idle while long jobs waited (meta/reviews/abaybektursun/20261115-0702). `submit` refuses
to run while the runner deployed in your workspace is not the `infra/runner.py` of the commit; `gpu.py deploy` fixes that.

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
thing, with the rest one click away. At the top are two lines: what changed since your last visit (new results, closed
work, work newly idle over an hour), and one sentence on the board: open work items, from how many people, how many are
idle over an hour (a click shows only those, `?idle=1`) and how long ago the last result came (a click opens it). Under
a switcher that picks one benchmark (`?bench=`) is a thin bar from 0 % to the best RL score: the best untrained-base
score at its left, the RL score at its right, one blue segment per record step (faint when the step is within noise)
and the points still missing to RL as the empty rest. A click on a segment opens that step. Then the hill-climbing
chart: every untrained-base score (`board.py score`) in the order posted with its 95% Wilson interval, the best so far
as a step line, and the best RL score as the target. A rise that does not clear the previous record's interval is drawn
faint, and the shaded area is the gap to RL. Beside the chart (under it on a narrow screen) is the ladder of record
steps, newest first, one line each: the gain in points, the step's `title`, previous best -> new best, and "within
noise"; the RL line at the top carries the 95% interval of the gap. A click on a step opens it under its line (`?step=<right>`): what changed (`what`), why it works (`why`), is it
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
the site has three tabs: Board (this page, `/`), Proof (`/proof`) and Findings (`/findings`).

The home page is https://invariant.team (`tools/home.py`; the same Lambda, which answers `/` with it when the host is
`invariant.team`, and `/home` on any host). It leads to every page of the monitor: Findings, Board, Proof, Talk
(`/demo`), Papers, the GPU price challenge (gpu.invariant.team, the team's entry to the hackathon's challenge; under Results), Lab, Exa, past.dev and Psychosis. Its picture is a dial: a lit glass
body with a ring around it and one bead per page. A click on a bead or the arrow keys turn the dial to a page
(`/#<page>`); a click on the body or the button opens it. Beside the picture are one sentence with the Board's live
MATH-500 scores (the first and the best untrained-base score and the best RL score in the `scores` rows of `/data`; the
words "a prompt cue and a vote" only when the best base row's configuration names them; no numbers before the first
read), one line with the live number of people, the button, and a numbered table of contents of the three sections
below. Each group has a muted hue (`TH`: Results blue, How we work teal, Tools and extras amber) used only for small marks,
and each page an abstract object of glass planes and hairlines (`ART`); the dial's body shows the selected page's object
and the ring is tinted by group. Below the dial each section has its number, name and sentence, then one row per page
with its object, name, line and live count.
About every 2.5 s one of the newest 40 board posts runs to the Board bead as a pulse in its author's color, named in the
line under the picture. A new page of the site is one entry in `PAGES` of `home.py`. As a page is sent, `view.py` (`chrome`) makes the name "Invariant" in its header a link to the home page and replaces
the header's links with one set, the same on every page (`NAV_TABS`): Findings, Papers, Board, Proof, in the order of the
home page's sections, then "All pages" (the home page's list of every page), with the current tab marked; the deck
(`/demo`) keeps its own header. A page that is none of the four tabs adds its name (at 400 px and below the name stays and "All pages" goes); at 520 px and below every page's header is one row of the same size, and a status in it is its dot alone unless it reports a problem; a page with no header gets a small link "Invariant" at the middle of its right edge; pinch
zoom is never switched off. An unknown address answers a short page with the header and links, and every address of invariant.team
other than `/` and `/data` redirects to the monitor. The page `/team` (`tools/people.py`) lists the team: its three
names are placeholders, each with the one line "Details to be added" until the people fill `PEOPLE` in; a filled field
shows as its own row.

The page `/papers` (`tools/papers.py`) is the paper loop: the names of its six steps in the words column (below the sheets
where the page is one column; a click on a step opens its sentence) and the papers of `view.PAPERS` as one flat row of sheets in the order written. One sheet is open, wide and
lit, and shows the paper's claim, why the loop picked it, how it was checked, its length and the button that opens the
PDF. The other sheets are closed to a strip with their number and title; a click on one, or the left and right arrow
keys, opens it (one width transition and a fade of the text, nothing in depth), and the address names it (`/papers#no-early-warning`). Below 1240 px every sheet is shown
in full, one after the other. A new paper gets its row in `ROWS` of `papers.py` (without one it still gets a sheet with its title). The domain is the stack parameter
`HomeDomainName` (`infra/monitor/deploy.sh monitor.invariant.team <zone id> invariant.team`).
Every page has the same tab icon, `/favicon.svg`: `view.py` holds the SVG and writes the link to it into each page as
it is sent, so a page module holds no icon.

To see which finding raised the benchmark: `uv run tools/climb.py [benchmark] [--json]` lists, per benchmark, every
record step of that chart (a base score strictly above all earlier ones, the same rule), newest first: the gain in
points, previous best -> new best, the result id, who, the configuration and the step's title (from its `plain` row;
without one, the first line of the result's text that is not a `score:`, `title:`, `what:`, `why:` or `caveat:` line).

`tools/architecture.py` was the tab Design until 2026-11-15; `/architecture` now leads to `/demo#harness`, the deck
slide that shows its picture (`/demo/fig/harness`), and the module stays as the site's visual reference (its tokens,
light, `world` and `proj`). The picture is one picture of the shared work setup for a first-time reader. The board is in the centre with one dot per live item, each person's agents are beside it with
threads to the board (the Claude mark for a Claude Code session, the OpenAI mark for a Codex session), the "Chat"
ring (messages) runs through every person's agents, and the "Retro" loop (self-review) goes around everything. What moves is real data, replayed: messages between people's agents, posts to the board. While one plays, its
first words are typed beside the person whose agent wrote it, with its age ("4 min ago", or "now"), and the status at
the top right counts the seconds since the last post. A click on a part
explains it, with live rows from the board; "Follow one result" steps through the
path of one result (arrow keys, Esc). The logos of past.dev (the team's memory) and Exa (web and literature search)
sit on the key's row at the bottom, and a click on either explains how agents use it.

The tab Findings is the page `/findings` (`tools/findings.py`). Its first view is the research question and one
picture of it: a glass rail of MATH-500 scores (T 1.0) on which the base model's scores without reward (Base, Base +
cue, restart, vote over 4 samples, vote after restart) are drawn in one after another against RL's (one sample, then
the same vote and restarts), with the points by which RL still leads with the same vote and restarts counted once to
that value under it and one sentence on what remains; the entrance takes about 2 s. Every mark opens the finding it
comes from (Tab and Enter work). The marks are read from the finding modules' own values and from the board's score rows
(result-5d032f, the honest best after board result-e78dfe); `view.py` writes the rows and those two scores into the
page at its first request (`findings.resolve`), so the page reads nothing after it loads. `TABLE` in
`tools/findings.py` names, per finding, its group, its figure and its marks. Under the picture the findings are rows in
groups headed by the questions of the story (What needs no reward? How does RL change the answers? Where does RL's
change sit in the weights?), each with its effect size as one figure with its unit and a short tag for its set, its
title, its sentence and its icon; a finding that `TABLE` does not name appears in the last group, "New". Every finding worth telling gets such a page:
`tools/finding_<slug>.py`, copied from `.claude/skills/finding-page/template.py`, is served at `/finding/<slug>` and
gets its tile with no other change; the module draws its own icon (`ICON`), and its panels start with "What is new" and
"Why it matters" (`.claude/skills/finding-page/SKILL.md` says when and how). `.claude/skills/site-ui/SKILL.md` holds
the rules for anything visible on the site.

`view.py` adds one script, `tools/sitekit.py`, to every finding page and to `/findings` as it serves them; the page
modules need no change. In the question, the sentence, the picture's HTML labels and each opened panel, the first use of
a term of `tools/glossary.py` gets a dotted underline, and a click, Enter or Space shows its one-sentence definition
(Esc or a click elsewhere closes it). The text of every element with the attribute `data-math` (problem texts and
answers) is turned from LaTeX into readable text: `$\frac{1}{k^2}$` reads 1/k², `\sqrt{37}` reads √37, an `[asy]`
picture reads [diagram]. `uv run tools/sitekit.py` checks that this keeps every digit and letter of the 1,389 problem
and answer texts of two finding modules (needs node).

The tab Proof is the page `/proof`: the same page as one list of rows with no picture, for the experiments that test the team's method itself and
not the research question. Each is a module `tools/proof_<slug>.py`, made like a finding page and served at
`/proof/<slug>`. The first is `tools/proof_review_cuts_waste.py` (the planted-waste test of the `team-meta-review`
skill, `studies/metaharness/`).
The second is `tools/proof_idea_basins.py` (`/proof/idea-basins`): the 515 board items of the snapshot of 15 November
2026, 19:42 UTC, as dots on a glass slab with a faint relief, in three conditions: the items in the order they were
posted, the items in the 12 idea basins a judge model grouped them into, and the idea tree (one row per basin, a line
from each item to the earlier items it builds on; 269 of 914 links join two basins). Its numbers and its layout, which
holds no board text, come from `studies/basins` on branch `ali/basins` (`results/swarm/main-03/summary.json`,
`analysis/swarm_nested_layout.py`).

The page `/values` (`tools/values.py`; not a header tab, reached from the home dial) holds the six values the team
works by, in the order of AGENTS.md: Speed, Enthusiasm, Practicality, novelty and interestingness, The bitter lesson,
Asymmetry and Clean context. The picture is a hexagonal glass prism with one face per value: one beam enters its top
and leaves as six rays, one through each face to a bead naming a value. A click on a bead or a face, the arrow keys or
the buttons select a value (`/values#speed`); its face turns to the front, and the column shows its sentences, its
quotes with their sources and its line of AGENTS.md. The words are the person's own; nothing on the page is data.

The page `/psychosis`, "AI Psychosis detox" (the counterpart of the Lab page, "AI Psychosis maxxing"), is a joke about ourselves (`tools/psychosis.py`; not a header tab): an overdone meditation game
of 6 levels, each ending in a boss that changes its words after the first hit. Hold Space, or press and hold, to breathe in and let go to breathe out, so that the
white ring follows the blue one. A breath that follows it scores, raises the streak multiplier, charges the Om (key O)
and sends out a wave that releases thoughts into their letters. The thoughts are bodies that collide: written jokes,
real messages and result titles of the board (blue dot), and from level 2 on fast pings, hype that grows and reviewers
that take two waves. A thought that reaches the meditator is believed and moves the diagnosis up; the fifth ends the
session. A click on a thought brings it back as 3 subagents. After each boss the player picks one of three practices
that stay (keys 1 to 3); on level 5 the blue ring fades during the breath out; after level 6 the retreat can go on without end. "Use the microphone" makes sound at the microphone the breath out and silence the breath in (nothing is recorded or sent). Three power-ups, a spoken guide and music
that follows the breath (M mutes). A WebGL shader draws the picture: fog, glow, ripples under each wave and a colour
split. The end screen gives score, rank, the breaths by grade, achievements and what the agents posted meanwhile.

The page `/demo` is the talk as a slide deck (`tools/demo_deck.py`; not a header tab): sixteen 16:9 slides, each one
figure with a few words, `#hook`, `#question`, `#built`, `#gap`, `#powered`, `#climb`, `#harness`, `#sponsors`, `#finding`, `#beyond`, `#efficiency`,
`#proof`, `#ideas`, `#papers`, `#summary` and `#close` (`/demo#finding` opens that slide, and Back works). The right arrow, Space or PageDown go on, the left arrow or
PageUp go back, Home and End jump, a click on the right or left third of the window steps, `t` or the button at the top right changes the theme
(`?theme=dark` in the address too), `f` is fullscreen and `p` prints: one slide per page at 13.333 x 7.5 in, in the
theme on screen, so print to PDF from the dark page for a dark PDF. The hook sentence is the constant `HOOK` in
`tools/demo_deck.py`, with the line under it (the name, then `TAGLINE`); the first slide also shows the address invariant.team and its QR code (`QR_PATH`, made with
segno). The slide `#gap` shows `/demo/fig/gap` (`tools/demo_gap.py`): the untrained base model and the RL-trained model as two glass pillars as high as their MATH-500 scores (the first base record and RL's best of `demo_ali_data` `climb`), the same small robot on each, unlit and lit; on load a staircase bridge of dashed planks appears between the two tops and the base robot hops onto the first two. The slide `#powered` sets the 72 H100 GPUs of the RL training (`FACTS['rl_zero_gpus']`, Olmo 3 paper, Table
49) beside the photo and name of the cook who fed the team. The two photos (cook, meditation) are the strings `COOK`
and `MEDITATE` in `tools/demo_photos.py`, with her name in `COOK_NAME`,
each a `data:image/jpeg;base64,...` URI (the deploy ships only `tools/*.py`); while one is empty its slide shows an
empty frame. The slide `#harness` shows the picture of `tools/architecture.py` in an iframe of `/demo/fig/harness`: that
page with its header, words column and key hidden (`demo_deck.FIGS`). The slide `#ideas` is full-bleed
`/demo/fig/converge` (`tools/demo_converge.py`): one canvas that plays by itself. On the glass slab of
`/proof/idea-basins` the board items of `tools/proof_idea_basins.py` (515) pop in, in posting order, and a lit head runs along an arc from each earlier
item an item builds on (tall and blue between two basins), while a count adds up the links that join two basins, ending
at that file's `DATA['tree']` (269 of 914); then real cross-basin links and convergence bursts (items that build on three or more basins) replay
until the tree grows again. `/demo/fig/basins` (`/proof/idea-basins` stepping from the items to their basins to the
idea tree) is still served and is on no slide. The slide `#sponsors` shows the scene of `/exa` and the memory scene of `/pastdev` side by side in iframes of
`/demo/fig/exa` and `/demo/fig/pastdev` (those pages with everything but the scene hidden; the dark deck shows them
inverted), each replaying its real cases, with two numbers under each read from the pages' own number rows. To the right of the memory scene, smaller, is `/demo/fig/pasttw`: the towers of `/pastdev` alone (recall against grep, 20 questions). The slide `#finding` shows `/demo/fig/fixes` (`tools/demo_fixes.py`): one MATH-500 problem
answered four ways, each answer a glass sheet on a step as high as its configuration's score (base model, 3 opening
tokens, sampling at T 1.0, 8 directions in the weights), with every quoted word checked against its run by
`PYTHONPATH=.:tools python3 tools/demo_fixes.py`. The slide `#proof` shows `/demo/fig/review` (`tools/demo_review.py`): four glass
columns on a glass slab, one per review round of the team-meta-review skill, each as high as the container minutes one
batch costs after that round, with the part that produced an answer lit and the rest, the waste, plain glass (the row under
the slab gives the formula: waste = total container min − answer min); on load each round cuts the columns to its
right, and a hollow dotted column at the end is the same model after three rounds with a plain instruction. Every number is read when the page is built: the staircase's scores from
`tools/demo_fixes.py`, the comparison with Karpathy's autoresearch loop from
`FACTS['auto_research_comparison']` in `tools/demo_facts.py` (from `studies/autobench`), the review rounds from
`tools/proof_review_cuts_waste.py` (through `tools/demo_review.py`), the links of the idea tree from `tools/proof_idea_basins.py`
(`DATA['tree']`), the number of people from `FACTS['people']`, and the papers from `tools/view.py`.

The stepped story of the talk is at `/demo/story`: one story over the picture of `tools/architecture.py`, with a sentence and a fact
line per step in the words column (arrow keys step, Esc closes; `/demo/story#<step>` links to a step). The 12
steps, in order: `#nanolab`, `#problem`, `#claim`, `#proof`, `#result`, `#vote`, `#why`, `#rules`, `#infra`, `#brain`,
`#retro`, `#watch`. A click on a part of the picture or on a question under the fact line opens one of 15 depth panels
(`/demo/story#result/cue`): one sentence, a few fact rows with their caveats, one source line and at most two links. The
panels are `problem/day1`, `proof/turnaround`, `result/cue`, `result/harder`, `vote/procedure`, `why/control`,
`why/findings`, `rules/thread`, `rules/audit`, `rules/rejected`, `infra/modal`, `infra/people`, `brain/sources`,
`brain/memory` and `retro/changes`; each fits the words column at 1440 x 860 without scrolling, except the list of
pages under `brain/sources`. Three modules hold the page: `tools/demo.py` (the page and its steps),
`tools/demo_panels.py` (the depth panels) and `tools/demo_facts.py` (`FACTS`, every number with its source, and
`SOURCES`, the pages read through Exa). No number is typed into the page code. Just before the talk, run
`uv run tools/demo_refresh.py`: it recounts the numbers that change by the hour (results on the board and per UTC
hour, hours since the first board item, the median from claim to result from `tools/cycle.py`, GPU job submissions,
agent sessions and logged commands from the event log, per-person counts), rewrites only those values in
`tools/demo_facts.py`, prints a before and after table and stops with an error if any count fails. Then restart
`uv run tools/view.py`. Every other number comes from a frozen artifact; to change one, open the file named in its
`src` and edit `v`, `n` and `at`. A key's `note` holds the caveats for the presenters and is not sent to the browser.

The pages `/demo/ali/slide1`, `/demo/ali/slide2` and `/demo/ali/slide3` are Ali's part of the talk (`/demo/ali` leads
to the first; they are not linked from the header). Slide 1 is the idea map: the board items of one snapshot as a
relief on a lit disc, one hill per cluster of ideas, each person's agents moving between the hills as board time is
replayed (a ring around the disc, a slider and a speed button move the time). Slide 2 is the idea tree: the same items
with a line to every item each one builds on, and a click lights one item's lineage. Slide 3 is the accuracy: the best
MATH-500 score of the untrained base as a step line over board time above the disc, against RL's best, with each
record tied to the result that set it and the record steps as rows in the board's plain words. The arrow keys change
the slide. `tools/demo_ali.py` holds the three pages and `tools/demo_ali_data.py` every number on them. The data file
is written by `python3 studies/basins/analysis/slide_data.py <run folder>` from one run of the swarm idea map
(`studies/basins/results/swarm/main-04` on the branch `ali/basins`: 515 board items at 19:42 UTC on 15 Nov) and from the board's score rows, read from `/data` at the time each slide names. The
record steps follow the rule of `tools/climb.py`. To refresh the numbers, run the script again and merge.

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
calls (at most every 20 s), the other runs `msg.py read` and adds new messages. A third, at the end of each turn,
refuses once to let the turn end while a GPU job this session submitted is queued or running and no `gpu.py wait`
runs for it (`gpu.py stophook`): start the wait in the background, and the finished job wakes the agent. All times are UTC. After changing a tool, run `python3 tools/selftest.py`:
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

## Exa challenge

Where Exa is called:
- `tools/exa.py`, `call()` (lines 25 to 29): `POST https://api.exa.ai/search` (with highlights) and
  `POST https://api.exa.ai/contents` (full text).
- In every agent's work cycle: `AGENTS.md`, "Working with the team", rule 2. Before a new measurement an agent searches
  with Exa, and when a published table already answers the question it posts the finding and runs nothing.
- In a scripted loop: `studies/theory/lib/round.py`, function `external()`, a stage of every round version (`ALL`). The model may run only
  `studies/theory/lib/papers.py`, which offers a paper-only recall and `tools/exa.py` search and fetch, so Exa is its only
  route to the web. Rounds 2 and 3 wrote 53 published findings (`studies/theory/results/engine/round-02/external.md`,
  `round-03/external.md`).
- Before a finding page: `.claude/skills/finding-page/SKILL.md`, step 2 asks for an Exa search for earlier reports.

What a search changed: on Nov 14 at 20:58 UTC one search in a literature sweep by 5 agents returned arXiv 2610.24663.
14 minutes later board item knowledge-d692e4, citing 7 papers, listed seven method families as already published, and
none of them was run. The page `/demo/story#brain/sources` shows this case and two more, and the 125 pages fetched through Exa,
each with its agent, time and the board item that cites it (`tools/demo_facts.py`, `SOURCES`).

Counts and limits: 172 of 199 HTTP calls to Exa returned results, from 59 main agents and subagents (counted from the
session transcripts up to 05:25 UTC; the Exa dashboards hold the authoritative count). 98 calls through the Exa MCP failed
with a 401 error, which is why the agents call the HTTP API. Early on, one person's agents had no Exa key and used another
search tool. No count of GPU jobs avoided by a search exists.

The page `/exa` (`tools/exa_page.py`; not a header tab; the site's tokens, typeface and header since 2026-11-15) shows
four searches that changed a decision, and what the agents got from Exa up to Nov 15 15:29 UTC, without the number of
calls. Its first screen is five numbers and one 3D scene of the four searches: a track with the stations Idea, Exa, GPU run and
Board, a porcelain gate at Exa, and above it one dot for each of the 677 distinct pages Exa returned
(`distinct_urls_in_search_results`). Each case is replayed: slabs (the ideas) reach the gate, a beam lights the pages
Exa returned, and the slabs stop at the gate, pass smaller, or go to the Board over the GPU run. The buttons 1 to 4
choose a case (`/exa#search-2`), and each source in the caption is a link. Its numbers come from
`studies/metaharness/results/exa_count-01/summary.json`, written by `studies/metaharness/analysis/exa_count.py`: 381 calls
to Exa returned (237 searches, 144 page reads) from 61 agents in 20 sessions; 193 more stopped at a missing key on one
laptop; 59 MCP calls returned 401. This count expands shell loops and reads other transcripts than the count above, so
the two do not reconcile. The theory engine's external stage has now written 163 published findings (rounds 02 to 07).

## past.dev challenge

### Agents

One past.dev project for the team. Identity: one per person (`~/.past/config.json`); all agents of a person share it.
No audiences are set, so every identity reads the whole project.

| Agent | Writes | Reads | Identity | Read by |
|---|---|---|---|---|
| Paper reader (a subagent, one per paper) | one data point per finding with `uv run tools/paper.py add`; `metadata.who` names the person | nothing | its person's (`~/.past/config.json`, read by `tools/past.py`) | every identity (no audiences) |
| Research agent (a Claude Code session; 63 sessions in the event log) | every board `result` and `knowledge` post, through `tools/board.py` | `python3 tools/recall.py "<idea>"` before it starts an idea (`AGENTS.md`, "Working with the team", rule 1), at most 2,000 tokens | its person's | every identity |
| Session plugin (at the end of a session) | typed prompts and prose replies; 7 sessions are stored | nothing: automatic recall is off | its person's | every identity |
| Theory generator (headless, `studies/theory/lib/round.py`) | nothing | recall through `studies/theory/lib/papers.py`, which keeps only entries whose every source is a paper or web page | its person's (reads only) | writes nothing |

### Layers

| Layer | Holds | Why this layer |
|---|---|---|
| Board (DynamoDB) | the state of the work: open work, ideas, results, votes, comments | agents need exact, current state and atomic claims |
| past.dev | findings from papers (604 from 125 papers), board results and knowledge (145), sessions (7) | the question "has anyone tried or read this" comes in new words each time; search by meaning with a dated source answers it within 2,000 tokens |
| Markdown in git (`studies/*/README.md`, `meta/`) | each number with its artifact path; each person's review notes | a number has to sit next to its code and commit |
| Session context (a hook) | the newest board items at the start of a session | every agent must see them, with no call |

Recall is on demand, never automatic, to keep each agent's context small. The one read boundary the work needed
(theory generators must not see board results, which hold held-out numbers) is a filter in our code
(`studies/theory/lib/papers.py`) rather than a past.dev audience.

### Results

No expected result was written down before the run. The rule (`AGENTS.md`, rule 1) is that an agent checks the team's
memory before it starts an idea.

- 571 recalls and 757 stored sources by 05:25 UTC (past.dev usage API); 373 ms at the median on past.dev's side; 0.84
  USD of credits.
- One traced read across people: on Nov 15 at 03:13 UTC abaybektursun's agent asked "Goodfire interpretability weight
  space programming papers read". past.dev returned sameraslan's board item knowledge-e6bc68, written at 21:45 UTC the
  day before. The agent opened it 11 seconds later and started a reading sweep that leaves that paper out (work-6b1fa5).
- Pilot, `studies/metaharness/results/recall_pilot/recall_vs_grep-01/`: on 20 templated known-answer questions, in one
  run, recall had the answer within 2,000 tokens for 20, one naive grep over 271 transcripts for 6 (17 anywhere in its
  output).
- Whether memory improved the research result is not measured: no arm ran without it.

The page `/pastdev` (`tools/pastdev.py`; not a header tab; the site's tokens, typeface and header since 2026-11-15; blue for what
past.dev returned) shows this on its first screen: four usage numbers and two 3D scenes side by side. The first is the memory as a disc with one dot per stored source (854:
616 paper findings, 227 board posts, 11 sessions), the agents that write behind it and the agents that read in front,
the theory generator joined to the paper sector only. It replays four real reads (`/pastdev#read-1` is the read across
two people above): the write, the question, the returned source in blue. The second draws the pilot: per method, 20
cubes for the 20 questions and a stack of slabs of 2,000 tokens, 1 slab for recall and 61 for grep.

### Caveats

- No read boundary inside past.dev: writes carry no per-agent identity or audience, and every identity reads everything.
- A corrected number is not replaced. Result-6d422d (435 of 497) was corrected by a new item, result-5227b9. Asked for
  that configuration in the pilot, recall returned the first post; whether it also returns the correction is not
  checked. We never wrote the correction as an update of the first data point.
- Session memory is small: 7 sessions are stored.
- Stored sessions hold the typed prompts of the three of us, so they can contain personal text, and every identity can read them.
- Our event log does not record recalls. The 571 is past.dev's count; 145 of them are visible as agent commands in
  transcripts.
- Ingestion ran about 1 minute behind, and 10 to 15 minutes when 30 to 40 items were queued (past.dev usage API).
- The pilot is 20 templated questions, one run, retrieval only, against one naive grep over a different corpus.
- Duplicate runs happened anyway: in the first hours one run was generated about 5 times.

## Modal

Almost every GPU number in this repository came from a Modal job that an agent started; the exception is one vast.ai job
(abaybektursun-1114-203934-5e03, `studies/rlneurons/README.md`).

- `infra/runner.py`: one app, one function per job class (`h100`; `short`, an H100 queue for jobs of at most 30 minutes;
  `b200`; `cpu`), one container per job, three Volumes (code by commit, outputs, model cache) and one Dict as the job
  registry. The H100 limit is read at deploy time from `ITERATE_MAX_H100`, default 10 per workspace.
- `uv run tools/gpu.py submit h100 -- '<command>'` refuses a dirty tree or an unpushed commit, uploads that commit as a
  tar to a Volume and spawns the function, so each job runs one pushed commit.
- What a hosted API cannot serve: the jobs run blended weights, zeroed neurons, and read the activations of both models.
- Who submits: 430 GPU job submissions by 07:20 UTC, all from agent sessions; none of the 430 carries the label that
  `tools/events.py` gives a command typed in a plain shell.
- Use, from the job records up to 05:42 UTC: 258 jobs started, a median of 5 seconds from submit to container and a
  quarter over 14.3 minutes, a peak of 30 GPU containers at once (10 in each of three workspaces), and 58 GPU-hours over
  179 ended GPU jobs.
- The lab tuned its own setup from the job records: after a Retro review raised the H100 `max_containers` from 4 to 20 (deployed at 02:31 UTC),
  the median H100 wait fell from 3.5 minutes (113 jobs) to 5 seconds (94 jobs), in different hours with no control. One
  run split over 4 H100s took 15.6 minutes against 51.5, measured once each way, with 17% more GPU minutes.
- Limits: 29 of 220 ended jobs exited with an error; no Sandboxes and no web endpoint are used.
