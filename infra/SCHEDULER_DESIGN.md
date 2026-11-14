> Implemented in `infra/pool.py` and `tools/gpu.py`. Where the two differ, the code is current.

# GPU job scheduler on Modal — design

One Modal app, `iterate-invariant`, is the only way anyone on the team (person or agent) runs a GPU
job during the hackathon. Modal's own per-function container cap does the allocating: there is no
scheduler loop of ours.

## Requirements

1. One allocator for every person and every subagent: a team-wide cap on GPUs in use at once.
2. No single person's agents can fill the queue: a per-person cap.
3. Every job is pinned to a pushed git commit, so any result can be traced to its code.
4. Anyone can see what is queued, running and finished, by whom, and on which GPU.
5. Anyone can cancel a job. Nothing runs forever.

## Architecture

```
person / agent ──> tools/gpu.py submit ──> modal.Dict "iterate-jobs"  (job record)
                                       └─> run_<gpu>.spawn(job_id)   (Modal queues past the cap)
                                                │
                       container: unpack <sha>.tar, run cmd, write /runs/<job_id>/
                                                │
                       Volume "iterate-runs"  ·  Volume "iterate-hf-cache" (shared HF_HOME)
```

### 1. Worker functions: one per GPU class

```python
@app.function(gpu="H100", max_containers=H100_CAP, timeout=6 * 3600, retries=0,
              volumes=VOLUMES, secrets=[hf_secret])
def run_h100(job_id: str): ...
```

One function per GPU class (for example `run_h100`, `run_b200`, `run_cpu`), each with its own
`max_containers`. A call over the cap waits in Modal's input queue and starts when a container frees
up. That queue is the allocator. `retries=0`: a failed job is reported, not silently re-run.

The worker:
1. writes `status=running`, `started_at` and the actual GPU name to the job record;
2. unpacks the job's commit from the Volume `iterate-code`, where `submit` uploaded it as
   `git archive` output named `<sha>.tar`;
3. runs the job's command with `/runs/<job_id>/` as the output directory, stdout teed to
   `stdout.log` there;
4. writes `status=completed` or `failed`, `finished_at` and the exit code to the record, commits the
   volume, and re-raises any error so Modal also shows it as failed.

### 2. Job record: `modal.Dict` named `iterate-jobs`

One key per job: `job_id → {who, gpu, commit, cmd, call_id, submitted_at, started_at, finished_at,
status, exit_code}`. `who` is the submitter's `git config user.email`. The job id is
`<who-prefix>-<yyyymmdd-hhmmss>-<4 random hex>`.

The record is for listing and attribution. Whether a job is alive comes from Modal itself,
`modal.FunctionCall.from_id(call_id).get(timeout=0)`, not from heartbeats. This is the main lesson from
the old infra: its `orchestrate_tick` reaped jobs on stale heartbeats and requeued them, and that
schedule was disabled on 2026-04-29 because it "was respawning killed runs"
(`interp_research/infra/modal_app.py`).

### 3. CLI: `tools/gpu.py`

| Command | What it does |
|---|---|
| `submit --gpu h100 --timeout 2h -- python exp/train.py --lr 3e-4` | Refuses a dirty tree or an unpushed commit. Refuses when this person already has `PER_PERSON_CAP` jobs queued or running. Writes the record, spawns, prints the job id. |
| `ls [--mine] [--status running]` | Every job: who, GPU, status, age, command. Live status comes from Modal. |
| `status <job_id>` | The record, the live Modal state, and the files in `/runs/<job_id>/`. |
| `logs <job_id>` | The tail of `stdout.log` from the volume. |
| `kill <job_id>` | `FunctionCall.cancel()`, then `status=cancelled` in the record. |
| `fetch <job_id>` | Copies `/runs/<job_id>/` except checkpoints to the local `runs/<job_id>/`. |

The per-person check reads the record and then spawns, so two simultaneous submits by one person can
exceed the cap by one or two jobs. The team-wide cap is exact, because Modal enforces it.

### 4. Storage

- Volume `iterate-runs`, mounted at `/runs`: one folder per job (`STATUS`, `metrics.json`,
  `stdout.log`, outputs).
- Volume `iterate-hf-cache`, mounted at `/hf` with `HF_HOME=/hf`: each model downloads once for the
  whole team.

### 5. Image

The pinned base from `interp_research/infra/image_base.py` (exact torch pins, so Modal's layer cache
holds), plus the repo's GPU dependencies. One person redeploys when dependencies change. Code is not
baked into the image: it is uploaded per commit, so pushing code needs no redeploy.

## What is copied from `interp_research/infra/` and what is not

| Copied | Not copied, and why |
|---|---|
| `image_base.py`: pinned image recipe | `orchestrator.py`: tick, reap, requeue. Modal's queue replaces it, and its reaper respawned killed runs. |
| `registry.py`: the `modal.Dict` record idea, stripped to the fields above | GPU fallback walk in `hardware.py`: one function per class is explicit, and a job asks for one class. |
| Per-architecture `TORCHINDUCTOR_CACHE_DIR` on a volume | Phase names, ES evaluation rows, run-id regex, Gemma download: specific to the old project. |
| `hardware.normalize_gpu_name` for the record | |

## Decisions for the team

1. **GPU classes and caps.** These depend on the Modal credits the hackathon gives. Prices in the old
   `hardware.py`, dated 2026-04-27: B200 $6.25/h, H200 $4.54/h, H100 $3.95/h. Check current Modal
   pricing before setting caps.
2. **Workspace.** Every teammate joins one Modal workspace, so `modal.Function.from_name` works for
   them with their own Modal login.

## Checks before the hackathon starts

1. Submit with the team cap at 1, two jobs: the second must show `queued` until the first finishes.
2. Kill a running job: its container stops, and `ls` shows `cancelled`.
3. A job that exits non-zero shows `failed` with its exit code and log.
4. Submit from a dirty tree: refused.
