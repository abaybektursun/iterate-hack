# iterate-hack

Repository for the SF AI Research Hackathon (November 14-15, 2026). Several people, each running Claude agents with
subagents, work on one research direction, described in [`DIRECTION.md`](DIRECTION.md). The rules for agents are in
`AGENTS.md`.

| Store | Holds | Tool |
|---|---|---|
| Team store (private repository `abaybektursun/iterate-hack-team`) | the board, the events, the traces, shared credentials | `uv run tools/board.py`, `tools/traces.py`, `tools/shared.py` |
| Memory (past.dev project) | specific findings from papers and posts; everyone's Claude Code sessions | `uv run tools/paper.py`, `python3 tools/recall.py` |
| Modal (your own workspace, app `iterate-runner`) | your GPU jobs, their outputs and the model cache | `uv run tools/gpu.py` |
| vast.ai (your own account) | your private GPU rentals | `python3 tools/vast.py` |

## Setup (once per person)

Do the steps in order. Credit codes and claim links are on the hackathon platform's home page (API Keys &
Credits); they are not copied here, because this repository becomes public. Type every key in your own terminal
or a text editor, never into an agent chat, and never commit one.

| # | Provider | Shared or yours | Needed for |
|---|---|---|---|
| 1 | GitHub | shared repositories | the code and the team store (board, events, traces, shared keys) |
| 2 | Shared keys (`tools/shared.py`) | shared | ECR images, past.dev memory |
| 3 | Modal | yours ($250 credits) | GPU jobs with `tools/gpu.py` |
| 4 | Hugging Face | yours | gated models on Modal and vast.ai |
| 5 | vast.ai | yours (optional) | cheaper private GPUs with `tools/vast.py` |
| 6 | AWS ECR | shared, read-only, until Sunday 23:59 PST | prebuilt images with model weights, on vast.ai |
| 7 | past.dev | shared team project | `tools/paper.py`, `tools/recall.py`, session memory |
| 8 | Exa | yours ($50 credits) | web search by agents |
| 9 | Tinker, Devin, OpenAI | yours | optional; no tool here uses them |

### 1. GitHub and the team store

```
brew install gh uv                 # or your platform's installers
gh auth login
git clone https://github.com/abaybektursun/iterate-hack.git && cd iterate-hack
git config user.email              # must be set: the part before @ is your name on the board and in job ids
```

Accept two invites: `abaybektursun/iterate-hack` (this code) and `abaybektursun/iterate-hack-team` (the private
team store). The team store is cloned to `~/.iterate-hack-team` the first time a tool needs it. Check:
`uv run tools/board.py ls` prints the board (nothing, when it is empty) without an error.

### 2. Shared keys

```
uv run tools/shared.py setup
```

It reads the keys the team shares from the team store and installs them: the AWS profile `iterate-ecr` (step 6)
and `~/.past/config.json` (step 7). It prints what is not shared yet. The owner adds a key with
`uv run tools/shared.py put ecr <key.json>` or `uv run tools/shared.py put past` (typed at a hidden prompt).

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

### 6. AWS ECR (shared, read-only)

The prebuilt images (table under Compute, Images) are in Abay's AWS account. Install the AWS CLI
(`brew install awscli`); step 2 already wrote the profile `iterate-ecr`. Check:
`aws ecr describe-images --repository-name shackleton --profile iterate-ecr --query 'length(imageDetails)'`
prints a number. The key can only pull images, and it stops working Sunday 2026-11-15 at 23:59 PST.

### 7. past.dev (shared team memory)

Step 2 wrote `~/.past/config.json` with the team's project key, your git email as identity, and recall off. Then
open Claude Code in this repository, trust the folder, and accept the prompt to install the `pastdotdev`
marketplace and plugin. Check: `/pastdotdev:status` shows the key, your identity and recall off, and
`python3 tools/recall.py "test"` runs without an error. Details and what is sent: "past.dev details" below.
The owner creates the team project once: sign up at https://past.dev, redeem the team credits with the code on
the hackathon platform, create an API key, and run `uv run tools/shared.py put past`.

### 8. Exa (your own key)

Sign up at https://dashboard.exa.ai, redeem the code from the hackathon platform, and create an API key. Put it
in your shell profile, not in the repository:

```
echo 'export EXA_API_KEY=<key>' >> ~/.zshrc && source ~/.zshrc
```

Check:

```
curl -s https://api.exa.ai/search -H "x-api-key: $EXA_API_KEY" -H 'content-type: application/json' \
  -d '{"query": "Olmo 3 RL-Zero math", "numResults": 3}' | head -c 300
```

No tool in this repository calls Exa yet; agents call the API directly (docs: https://docs.exa.ai).

### 9. Tinker, Devin, OpenAI (optional)

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
```

A job over its class's limit waits in Modal's queue. A job is killed at `--hours` (default 2). The command is one
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

Setup for ECR: `uv run tools/shared.py setup` writes the AWS profile `iterate-ecr`. Pick a host with fast download (`offers` shows it): a 27.6 GB image took 38 minutes on a slow host.

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
artifact. Each item, vote and comment is its own file in the team store, and every write is a pushed commit, so any number
of agents can write at the same time. A write takes 2 to 3 s.

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

| Record | Where in `iterate-hack-team` | Written by |
|---|---|---|
| Every `board.py`, `gpu.py` and `paper.py` command: time, person, agent (claude-code or codex, with its session id, and whether it ran as a subagent), commit, full command line | `events/` | the tools, automatically; pushed with the next board write or `traces.py push` |
| Board items, votes and comments, with times; who closed each work item and when | `board/` (and the git history) | `board.py` |
| Agent transcripts (Claude Code with subagents, Codex) | `traces/<who>/` | `uv run tools/traces.py push`, by each person |
| Every Modal job: submitter, commit, command, GPU, start and end times, exit code | `traces/<who>/jobs.json` | `gpu.py`, then `traces.py push` |

Run `uv run tools/traces.py push` at the end of each working session. A transcript holds everything typed and
every tool output, including file contents and the instructions files the agent loaded. `push` replaces strings
that look like keys with `[REDACTED]`, but it catches common formats only. vast.ai rentals are recorded only on
your laptop, in `runs/vast/`.

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
file per machine: `shared.py setup` leaves an existing file unchanged, so if you already use past.dev for another
project, edit the file by hand. Codex users: see https://github.com/pastdotdev/codex-plugin.
