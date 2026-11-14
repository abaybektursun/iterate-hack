# Rules for this repository

This file holds rules only. [`README.md`](README.md) is the index of the repository: which studies are
live, which are closed, and where each closeout is. Closed and archived studies are not loaded by default,
because they take up context and some contain claims that their own artifacts contradict. Open one when a
plan measures the same thing, and start from its closeout.

Read the raw outputs before you explain a result. Most surprising results in machine learning have a
simple cause that is visible in the raw outputs.

## The three failures

1. Reporting a result as better than the data show, or reporting a summary instead of the artifact. A
   prediction that turns out wrong is a valid result. Report it as one.
2. Bugs, which are common. Treat every instrument as broken until you have given it an input that should
   make it fail and seen it fail.
3. Confounds, which are also common. Treat every contrast as measuring something other than its name until
   a matched control rules that out.

State every hypothesis together with the observation that would refute it. If no observation could refute
it, it is not a hypothesis. Check an elegant or unifying finding harder than an ordinary one.

## What we value in a result

Three properties: predictive (a held-out prediction comes true), novel (it is not a known result under a
new name), and practical (it beats a baseline on a measured number). Evaluate and report every result on
each of the three separately. A result does not need any of them to be reported.

## Before a measurement that will support a claim

These steps apply to a new measurement whose number will support a claim. Run a smoke job, a pipeline
check or a rerun of a known number without them.

1. Search the literature first, with the field's terms. The searches that missed papers used our own
   vocabulary. Search for the object, the method and the effect under the names the field uses. Include
   the exact phrases a paper would use, try several reformulations, and read the full text of every close
   paper. Three papers that lack the result do not show that the literature lacks it.
   From each close paper, record its experiments as well as its claims: models, data, metric, the numbers
   in its tables, and its controls. Search the conventional method's name together with each property of
   our setting. Before building a run, compare it with the closest published experiment and write down how
   it differs. If a published table already answers the question, do not run it. There is no budget for
   replications.
2. List every earlier measurement in this repository on the same models and quantities, with file paths.
   This is the one time to open closed and superseded studies, because a "superseded" banner can hide a
   finished measurement.
3. Write the measurement down before taking it: the quantity, the items, the exact names of the model
   before and after the change, how measurements are paired, how they are summarized, and which interval
   is reported.
4. Before using a GPU, run the full pipeline on the laptop with the model forward pass left out, and fix
   every error. The first GPU run reproduces one known number before any new number is trusted.
5. Freeze the thresholds on control data, then unblind once. If a rule turns out to be wrong afterwards,
   record a dated exploratory deviation. The frozen rule still decides the headline result.

## Instruments and controls

1. Every pass condition has a lower bound, an upper bound, and a branch for when the readout does not count
   (stamped `VOID` in the artifact). One-sided thresholds were the most common defect in the archived
   program.
2. Every gate has a registered input that makes it fail. Every verdict is computed from its gate results.
3. Compare a result against the strongest available null, never against zero: a positive control, a null
   or seed baseline, or a shuffle. A random-subspace null tests whether a set is aligned with the data at
   all. To claim that a set is special, compare it with a structured control from the same operator,
   matched on count and on energy.
4. Before unblinding, every instrument readout reports three numbers: the fit on both sides, a positive
   control that showed the expected effect, and the value on an identity pair. If any is missing, the
   readout does not count, and the artifact is stamped `VOID`.
5. Before freezing a rule that can end a study, check that the data can trigger it. A rule whose condition
   can never be met tests nothing, and a null test without statistical power does not show a negative
   result.
6. Save the real prompt, the real prediction and its probability next to every score, for one item scored
   correct and one scored wrong. Do not quote a number that has no saved samples.
7. Before comparing two numbers, state the units and the object of each. Two numbers computed on the same
   items can still measure different quantities.
8. Measure the effect that actually happened, not the one intended. For example, measure the weight
   update itself, not the gradient you projected.
9. Report absolute scores. A fraction of a margin hides the number and becomes very large when the
   margin is small.

## Provenance

1. Verify every number at its artifact: `metrics.json`, the weights, or git. Never verify a number from a
   summary, a memory note or an agent's report, however confident it sounds.
2. Each study keeps a claims file (named `CLAIMS_LEDGER.md` so far) with one line per claim that a
   conclusion depends on, and a status tag on each line. Prose cites the claim's ID. When an artifact
   contradicts a claim, change its tag the same day.
3. A different model reads the artifacts before any result is closed.
4. Regenerate every figure after any correction. A figure made before the correction still shows the old
   result.
5. Fail loudly. No try/except that hides an error, no synthetic fallback, and no null result reported as
   an effect.
6. Never `git add -A` or `git add .`; commit files by name.
7. Use a paper to support or dismiss a claim only after reading its full text for that specific claim. An
   abstract is enough to list a paper as unread and for nothing else, because the detail that decides the
   question is usually missing from it.

## Process

1. Rule out the simple explanation before testing a complicated one.
2. Two writers never edit the same file. When several agents write code at the same time, each one gets
   its own worktree (`../interp_research-<name>`) and branch, and none of them works in the shared main
   worktree. One session making small text edits may work on main.
3. Order work by which measurement decides the question. Write the result document after the adversarial
   audit.
4. Report a job's status only from a liveness check: a live instance ID or an artifact timestamp. If a
   job has written nothing recently, report its state as unknown. Never score a running job.
5. Estimate in GPU-hours and run counts, never in engineering time.
6. Keep science and infrastructure separate. Infrastructure incidents, cost and lifecycle go under
   `infra/**/operations/`, never into a research journal. Report finished setup work as infrastructure
   work. Report research progress only for new measurements.
7. Run the `meta-review` skill at the start of a session, after every closed result and after every fifth
   GPU run. Its entries go to `meta/META.md`.

## Persistent context is read-only

Persistent context is this file, every `.claude/` directory (skills, settings, hooks), and the
auto-memory. Agents cannot edit it; an edit is blocked. If a change should be kept, write your version to
the same path under `~/.claude/context-staging/`, which the harness never loads, and continue. Do not read
that directory otherwise. When the user asks to review staging, go through it together: approved files are
copied to their live paths, and the rest are deleted.

Everything in persistent context must stay useful for as long as the repository exists. A fact about one
study, one date, one incident or one software version goes in that study's own documents or in
`README.md`.

## Communication

1. Put the answer in the first sentence, with the number that decides it when there is one. When the user
   asks the same question again, answer it again; do not edit the document in response.
2. Write plain technical English: short sentences, one idea each, concrete nouns. Name the measure, for
   example wikitext perplexity or LIBERO success rate, instead of "damage" or "performance".
3. Use the field's real terms (matrix, rank, coordinate, basis). Do not use analogies, metaphors or
   invented terms. To simplify, cover less, and keep the real names. Use a literal phrase whenever one
   exists, because a figurative phrase adds meanings the writer did not intend.
4. State a point directly. Say what something is, and do not set it against something it is not ("X is
   not Y, it is Z"). Do not end a paragraph with a summarizing one-line maxim.
5. Keep it short: one idea, then stop. When teaching, give one idea and one check question, then wait for
   the answer.
6. Answer a user's question as a question; do not treat it as criticism. Do not open with "good catch".
   Retract only when actually wrong, once, plainly.

## Working unattended

1. In a long unattended run the user is not watching and cannot answer. For a reversible action that
   follows from the request, proceed without asking. Stop only for a destructive action or a change of
   scope that is the user's to decide.
2. In conversation, when the user describes a problem, asks a question or thinks out loud, the deliverable
   is the assessment. Report it and stop. Apply a fix when asked.
3. Do the kind of work requested, at the scope requested: when asked for a spec, deliver the spec. Do not
   narrow, widen or change the scope without saying so. Put other work worth doing at the end of the report
   as a suggestion.
4. Before ending a turn, read the last paragraph. If it describes a plan or promises work not yet done, do
   that work.
5. Before a command that changes system state, check that the evidence supports that specific action. A
   symptom that resembles a known failure can have a different cause.
6. When the user has set an active goal, that counts as approval for every step a spec marks "on the
   user's go": freeze, launch, rent, unblind. Decisions within the spec's limits belong to the
   coordinating agent and go in the journal; do not stop the work to ask about them. Ask the user only
   before a destructive action outside those limits.

## Machine and money

1. The laptop only issues commands and reads results, and it has little disk and memory. Work that runs in
   the cloud stays there: model weights, datasets, container builds, training and model forward passes
   never come to the laptop. Local work is git, text edits, reading documents and papers, dry runs without
   weights, and analysis of saved JSON results.
2. Use AWS profile `fuelos` and region `us-east-1`, stated explicitly on every call. Launch jobs with
   `./infra/aws_pg/pg`, which starts instances that terminate themselves (default `g6e.2xlarge`). The list
   of cached model weights is `infra/pg/matrix_repo_facts.json`; read it from there, never from a list
   typed by hand.
3. Use a new S3 prefix for every attempt. Save results inside the loop, not after it. Follow a job through
   the small files it writes for that purpose (`metrics.json`, `STATUS`, the heartbeat). The raw log is
   large: read its tail once to diagnose a failure, and never poll it.
4. Do residual-stream arithmetic in fp32. Save the probabilities of both token forms, `' A'` (with a
   leading space) and `'A'`, together with the model's actual top token.
5. Never use assumed LLM model names; check the current names before writing them into code.
