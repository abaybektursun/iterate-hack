# bash meta/reviews/abaybektursun/20261115-1933/resume_test.sh <empty scratch dir> > meta/reviews/abaybektursun/20261115-1933/after.txt 2>&1
# Dry runs of run_cell.py (stand-in engine: no vLLM, no weights, no GPU; the tokenizer comes from the local cache).
# 1. no --resume, the cut shard's settings: rows must equal before.txt's run (same 504 requests, same counts).
# 2. --resume on the real cut shard ih-1115-161910-44ea (493 of 504 rows): only the 11 missing requests are sent.
# 3. --restarts 2: a run cut after 25 rows is resumed; every attempt chain must be complete, with no duplicate row.
# 4. inputs that must fail: another seed, a duplicated row.
set -euo pipefail
T=$1; B=${BEFORE:?the before run folder}
SHA=4c020cef158f25da0a2f250f8238ededdaf55da6
CELL="--model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --samples 8 --shard 0/8 --dry-run --commit $SHA"
run() { HF_HUB_OFFLINE=1 PYTHONPATH=. uv run -q --no-project --with torch==2.15.0 --with transformers==5.22.2 --with math-verify==0.9.0 \
          --with huggingface_hub python -m studies.rlneurons.jobs.run_cell "$@" > "$T/last.log" 2>&1; }
count() { python3 -c "import json,sys;c=json.load(open(sys.argv[1]))['counts'];print({k:c[k] for k in ('n','n_planned','correct_v3','cap_hits','restarts','generated_tokens')})" "$1"; }

echo "== 1. no --resume"; run $CELL --seed 41040000 --out "$T/plain"; count "$T/plain/metrics.json"
python3 - "$B/answers.jsonl" "$T/plain/answers.jsonl" <<'EOF'
import json, sys
a, b = ([{k: v for k, v in json.loads(l).items() if k != "utc"} for l in open(p)] for p in sys.argv[1:])
print("rows equal to before (utc left out):", a == b, len(a), len(b))
EOF

echo "== 2. --resume runs/ih-1115-161910-44ea"; run $CELL --seed 41040000 --resume runs/ih-1115-161910-44ea --out "$T/resumed"; count "$T/resumed/metrics.json"
python3 - runs/ih-1115-161910-44ea/answers.jsonl "$T/resumed/answers.jsonl" "$T/plain/answers.jsonl" <<'EOF'
import json, sys
old, new, full = ([json.loads(l) for l in open(p)] for p in sys.argv[1:])
key = lambda r: (r["problem_index"], r["sample"], r["attempt"])
print("old rows copied unchanged:", new[:len(old)] == old, len(old))
print("requests sent:", len(new) - len(old))
print("keys equal to a full run's:", sorted(map(key, new)) == sorted(map(key, full)), "duplicates:", len(new) - len(set(map(key, new))))
EOF

echo "== 3. --restarts 2, cut after 25 rows, resumed"
R="--model base --prompt cue --set math500 --temperature 1.0 --top-p 1.0 --samples 2 --restarts 2 --n 30 --dry-run --commit $SHA --seed 41040000"
run $R --out "$T/r_full"; mkdir "$T/r_cut"; head -25 "$T/r_full/answers.jsonl" > "$T/r_cut/answers.jsonl"; cp "$T/r_full/metrics.json" "$T/r_cut/"
run $R --resume "$T/r_cut" --out "$T/r_res"; count "$T/r_res/metrics.json"
python3 - "$T/r_res/answers.jsonl" "$T/r_cut/answers.jsonl" <<'EOF'
import json, sys
rows, cut = ([json.loads(l) for l in open(p)] for p in sys.argv[1:])
chains = {}
for r in rows:
    chains.setdefault((r["problem_index"], r["sample"]), []).append(r)
ok = all(sorted(x["attempt"] for x in ch) == list(range(len(ch))) and
         all(x["cap_hit"] for x in sorted(ch, key=lambda x: x["attempt"])[:-1]) and
         (not max(ch, key=lambda x: x["attempt"])["cap_hit"] or len(ch) == 3) for ch in chains.values())
print("chains:", len(chains), "of 60; every chain complete:", ok, "; rows:", len(rows), "; first 25 rows kept:", rows[:25] == cut)
EOF

echo "== 4. inputs that must fail"
run $CELL --seed 41040001 --resume runs/ih-1115-161910-44ea --out "$T/f_seed" && echo "another seed: NOT REFUSED" || { echo -n "another seed refused: "; grep AssertionError "$T/last.log"; }
mkdir "$T/dup"; cp runs/ih-1115-161910-44ea/metrics.json "$T/dup/"; { cat runs/ih-1115-161910-44ea/answers.jsonl; head -1 runs/ih-1115-161910-44ea/answers.jsonl; } > "$T/dup/answers.jsonl"
run $CELL --seed 41040000 --resume "$T/dup" --out "$T/f_dup" && echo "duplicate row: NOT REFUSED" || { echo -n "duplicate row refused: "; grep AssertionError "$T/last.log"; }
