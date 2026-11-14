# Rules for agents in iterate-hack

Several people, each with Claude Code or Codex agents and their subagents, work on one research direction during
the SF AI Research Hackathon. `DIRECTION.md` is the research direction: read it before choosing work.
`README.md` explains every tool. This file holds the rules.

## Values

1. Speed. Cycle time decides research output. Prefer the experiment that answers in minutes over the one that
   answers in hours, and run it now.
2. Enthusiasm. Pursue the work with energy.
3. Practicality, novelty, interestingness. The goal is a novel practical win. A genuinely novel result is an
   intermediate win, and interesting results are the path to novelty.
4. The bitter lesson. Larger models and more compute win. Prefer methods that improve with scale over
   hand-engineered ones.
5. Asymmetry. We are a small team. Use flexibility, speed and overlooked opportunities that large labs pass over.
6. Clean context. Keep every agent's context small: read papers, long logs and large files in subagents, and
   bring back only what the task needs.

## The coordination flow

Other agents learn what you are doing only from the board and the messages. So every agent follows the same six
steps:

1. Start of a session: in Claude Code, a hook puts the open work, the newest board items and new messages into
   your context. Codex: run `uv run tools/board.py ls work`, `uv run tools/board.py ls --new --n 10` and
   `uv run tools/msg.py read`.
2. Before starting work: check that no open `work` item covers it. Then claim it with
   `uv run tools/board.py post work "<what you will do> <id of the idea>"`, which also announces it on `all`. If
   `post` prints "also claimed" and the other item is older, close yours with `done` and pick other work.
3. While working: comment on your `work` item at each step (what you just did, what is next), and post each
   result or finding to the board the moment you have it. Run `uv run tools/msg.py read` after every job or long
   step.
4. When another agent's message changes your work, act on it before continuing. Answer a direct question.
5. A `work` item shows its idle time in `ls work`: the minutes since it was posted or last commented on. If you
   want work whose item has been idle for 60 minutes, comment on it asking for its state (the owner gets that as
   a message). With no answer after 10 minutes, close it with `done` and claim the work yourself; both announce themselves on `all`.
6. When you finish: `uv run tools/board.py done <work id> "<result: number, units, artifact path>"` posts the
   result, closes the item and announces both on `all`, in one command. Put each accuracy on its own line of the
   result, `score: base MATH-500 378/500 tokens 4690 | cue, T 0.6 / top-p 1.0` (base or rl): the hill-climbing chart
   on https://monitor.invariant.team is drawn from these lines. If you stop before the work is finished,
   first comment what is done and what is left, then `done <work id>`; its announcement tells others the work is
   free. An open `work` item with no agent behind it blocks everyone else from
   that work.

## Working with the team

1. Before starting an idea, also search the team's memory: `python3 tools/recall.py "<the idea in the field's
   terms>"`.
2. Before a new measurement, search the literature with Exa: `python3 tools/exa.py search "<description of the
   page you want>"`, using the field's terms and several rephrasings, then `python3 tools/exa.py fetch <url>` to
   read a hit. Do not use the Exa MCP tools. If a published table already answers the question, do not run it;
   post the finding instead.
3. Post each result as a `result` item with its number, its units and the path of its artifact. Teammates cannot
   read your Modal Volumes, so commit the small result files and name the git path.
4. Read a paper in full, appendix included, in a subagent, and add findings with `tools/paper.py add`. An abstract
   supports no claim.
5. Two writers never edit the same file. Each agent that writes code works on its own branch, in its own worktree
   (`../iterate-hack-<name>`). Push small commits often: a job runs only a pushed commit. Pull often: `git pull origin
   main` before every step and after every job, so you always work on everyone's latest code.
6. Never `git add -A` or `git add .`; commit files by name.
7. Edit `AGENTS.md` or `CLAUDE.md` only when your person asks.
8. Run the `team-meta-review` skill (`.claude/skills/team-meta-review/SKILL.md`; Codex: read that file) at the start of a
   session, after every closed result and after every fifth GPU run.

## Messages between agents

1. In Claude Code, a hook (`.claude/settings.json`) runs `msg.py read` after tool calls, at most every 20 s, and puts
   new messages into your context: you do not need to poll. Codex has no such hook: run `uv run tools/msg.py read`
   after every job or long step. A comment on an item you posted also arrives as a message.
2. Channels: `all` reaches every agent; `@<name>` reaches one person's agents; a board item id is the thread about
   that item. An agent's first read of a channel goes 10 minutes back, so anything that must be seen later belongs
   on the board.
3. Besides the announcements of the coordination flow, send a message when another agent needs to know now: you started or stopped something they depend on, you found
   a number that changes their plan, you found a bug in shared code. `uv run tools/msg.py send all "<text>"`, or
   `send @<name>` for one person's agents, or `send <board item id>` for the thread about that item.
4. When you are blocked on another agent, use `uv run tools/msg.py wait` instead of polling by hand.
5. Messages are for the next minutes. Anything that should last (a result, a finding, an idea) goes on the board.

## Experiment layout

`studies/rlneurons/` is the model: copy its layout. A teammate must be able to find any number's code, inputs
and outputs from the study's `README.md` alone.

1. Every experiment lives in `studies/<study>/`. No experiment code, data or output at the repository root, in
   `tools/` or in `infra/`. Add to an existing study when the question is the same; start a new one only for a
   new question.
2. Use the same subfolders in every study: `specs/` (the plan, written before the run), `data/` (frozen inputs),
   `lib/` (shared code), `grader/`, `prep/`, `jobs/` (what runs on a GPU), `analysis/` (what reads the outputs),
   `results/`. Create only the ones you need.
3. One run is one folder, `results/<experiment>/<arm>-<nn>/`, holding `run.json` (commit, command, job id),
   `metrics.json` and the saved examples. Never write into an existing run folder: a rerun gets the next number.
4. `studies/<study>/README.md` is the index: the files, how to run them, and each number with the path of its
   artifact. Update it in the same commit as the result.
5. Never edit a file in `data/` or a grader that a posted number used. A changed input or grader is a new file
   with a new version in its name, and the result states which version it used.
6. Import shared code (graders, generation, loaders) from the study's `lib/`; do not copy it. Apart from the
   versions of rule 5, no copies of a file under another name (`_new`, `_fixed`, `_final`, `2`).
7. Commit only small files: metrics, readouts, examples. Raw generations and weights stay in the Volume or in
   `runs/` (not committed); write their location in the study's `README.md`.
8. Before closing a `work` item, delete your scratch scripts, unused code and debug output, and check that
   `git status` shows nothing left over.

## Compute

1. GPUs: `uv run tools/gpu.py` (your person's Modal workspace) or `python3 tools/vast.py` (their vast.ai
   account). Both spend their own credits. The laptop never runs a model forward pass or downloads weights.
2. On vast.ai, keep one box for the session and send every job to it. Copy results out with `get` before the
   box ends, and `down` it when you stop.
3. Before a long run, run the pipeline for a minute on the smallest setting, and check that it writes its outputs.
4. Report a job's state only from `gpu.py ls`, `vast.py ls` or the time of its newest output. Never score a job
   that is still running.
5. Before downloading a model on vast.ai, check the image table in `README.md`: some models are already in an image.
6. Never write a model name from memory. Check the exact current name on Hugging Face first.

## Results

1. Read the raw outputs before explaining a result. Most surprising results have a simple cause that is visible in
   them.
2. State every hypothesis with the observation that would refute it.
3. Treat every instrument as broken until an input that should make it fail has made it fail. Treat every contrast
   as measuring something other than its name until a matched control rules that out.
4. Compare against the strongest baseline or null available, never against zero. Report absolute numbers with
   their units and the number of items.
5. A prediction that turns out wrong is a valid result. Report it as one.
6. Save the real input, output and score of one item scored right and one scored wrong next to every number.
7. Verify a number at its artifact (the job's `$OUT_DIR`, git), not from a summary or another agent's report.
8. Fail loudly. No try/except that hides an error, no synthetic fallback.
9. A novel finding gets its own page on the team site: follow `.claude/skills/finding-page/SKILL.md`. Any change to
   the site follows `.claude/skills/site-ui/SKILL.md`.

## Communication

1. Put the answer in the first sentence, with the number that decides it.
2. Write plain technical English: short sentences, concrete nouns, the field's real terms. No metaphors or
   invented terms.
3. Keep it short. Board comments are at most 280 characters.
4. When your person ends a session, remind them to run `uv run tools/traces.py push`.
