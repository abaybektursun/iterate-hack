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

Other agents learn what you are doing only from the board and the messages, and only when they look. Nothing is
pushed to an agent. So every agent follows the same five steps:

1. Start of a session: `uv run tools/msg.py read`, then `uv run tools/board.py ls work` (what everyone is working
   on now) and `uv run tools/board.py ls --new` (what was posted last).
2. Before starting work: check that no open `work` item covers it. Then claim it on the board with
   `uv run tools/board.py post work "<what you will do> <id of the idea>"`, and announce it with
   `uv run tools/msg.py send all "<what you started, and the work item id>"`. Do both: the board item is what an
   agent that starts later sees, the message is what running agents see now. If `post` prints "also claimed" and
   the other item is older, close yours with `done` and pick other work.
3. While working: comment on your `work` item at each step (what you just did, what is next), and post each
   result or finding to the board the moment you have it. Run `uv run tools/msg.py read` after every job or long
   step.
4. When another agent's message changes your work, act on it before continuing. Answer a direct question.
5. When you finish or stop: post the `result`, close the `work` item with `done`, and announce it on `all`. If you
   stop before the work is finished, first comment what is done and what is left, then close the item and say in
   the announcement that the idea is free. An open `work` item with no agent behind it blocks everyone else from
   that work.

## Working with the team

1. Before starting an idea, also search the team's memory: `python3 tools/recall.py "<the idea in the field's
   terms>"`.
2. Before a new measurement, search the literature with the Exa tools (`web_search_exa`, `web_fetch_exa`), using
   the field's terms and several rephrasings. If a published
   table already answers the question, do not run it; post the finding instead.
3. Post each result as a `result` item with its number, its units and the path of its artifact. Teammates cannot
   read your Modal Volumes, so commit the small result files and name the git path.
4. Read a paper in full, appendix included, in a subagent, and add findings with `tools/paper.py add`. An abstract
   supports no claim.
5. Two writers never edit the same file. Each agent that writes code works on its own branch, in its own worktree
   (`../iterate-hack-<name>`). Push small commits often: a job runs only a pushed commit.
6. Never `git add -A` or `git add .`; commit files by name.
7. Edit `AGENTS.md` or `CLAUDE.md` only when your person asks.
8. Run the `meta-review` skill (`.claude/skills/meta-review/SKILL.md`; Codex: read that file) at the start of a
   session, after every closed result and after every fifth GPU run.

## Messages between agents

1. Channels: `all` reaches every agent; `@<name>` reaches one person's agents; a board item id is the thread about
   that item. An agent's first read of a channel goes 10 minutes back, so anything that must be seen later belongs
   on the board.
2. Besides the announcements of the coordination flow, send a message when another agent needs to know now: you started or stopped something they depend on, you found
   a number that changes their plan, you found a bug in shared code. `uv run tools/msg.py send all "<text>"`, or
   `send @<name>` for one person's agents, or `send <board item id>` for the thread about that item.
3. When you are blocked on another agent, use `uv run tools/msg.py wait` instead of polling by hand.
4. Messages are for the next minutes. Anything that should last (a result, a finding, an idea) goes on the board.

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

## Communication

1. Put the answer in the first sentence, with the number that decides it.
2. Write plain technical English: short sentences, concrete nouns, the field's real terms. No metaphors or
   invented terms.
3. Keep it short. Board comments are at most 280 characters.
4. When your person ends a session, remind them to run `uv run tools/traces.py push`.
