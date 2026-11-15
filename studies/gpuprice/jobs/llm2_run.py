"""LLM adjuster arm (llm2): one plain completion per (series, origin) that adjusts the ens-05 quantiles. Laptop, hosted API.

  R="runs/gpuprice/.venv/bin/python -I -B studies/gpuprice/jobs/llm2_run.py"
  $R --model claude-sonnet-5-5 --variant adj --origins pilot [--effort low] [--limit 4]
  $R --model claude-fable-5-2 --variant adj --origins locked --base runs/gpuprice/spec2/candidate.csv --cells <dev cells>,runs/gpuprice/spec2/cells_candidate.csv
  $R --model claude-fable-5-2 --variant adj --origins event --base studies/gpuprice/results/submission/forecast_2026-11-06.csv --cells <dev cells>,<locked cells> \
     [--replay studies/gpuprice/results/llm2/event_fable_adj.jsonl]       no API call: the stored responses, each checked against the rebuilt prompt

No tool, no search: the request holds a system prompt, one user message (llm2_context.build, rows dated <= origin only) and a
JSON schema. Every raw response is appended to <--out, default runs/gpuprice/llm2>/<variant>/<model>.jsonl keyed by (model, series, origin);
a cached key is never called again. Spend is summed from the usage of every cached response of the provider and checked
against the cap before the batch (estimate from token counts) and after every call.
"""
import argparse, concurrent.futures as cf, datetime as dt, glob, json, pathlib, statistics, sys, threading, time
import anthropic

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import llm2_context as ctx

# id (GET /v1/models, 2026-11-14) -> (USD per million input tokens, output tokens, training data cutoff). Cutoffs and prices:
# https://platform.claude.com/docs/en/about-claude/models/overview (fetched 2026-11-14): "Training data cutoff Jun 2026" for all four.
MODELS = {"claude-fable-5-2": (8.0, 40.0, "2026-06"), "claude-opus-5-5": (4.0, 20.0, "2026-06"),
          "claude-sonnet-5-5": (2.0, 10.0, "2026-06"), "claude-haiku-5-5": (0.10, 0.50, "2026-06")}
CAP_USD = 34.5                                  # Anthropic cap of the whole llm2 arm: 25 for the development runs + 8 for SPEC3 (locked, event)
OUT = pathlib.Path("runs/gpuprice/llm2")
PILOT = ["2026-10-01", "2026-10-07", "2026-10-13", "2026-10-19", "2026-10-25", "2026-10-30"]

Q = {"type": "object", "properties": {k: {"type": "number"} for k in ("q10", "q50", "q90")}, "required": ["q10", "q50", "q90"],
     "additionalProperties": False}
SCHEMA_Q = {"type": "object", "properties": {"reason": {"type": "string"}, "h1": Q, "h3": Q, "h7": Q},
            "required": ["reason", "h1", "h3", "h7"], "additionalProperties": False}
P = {"type": "object", "properties": {k: {"type": "number"} for k in ("p_lower", "p_higher", "level_if_lower", "level_if_higher")},
     "required": ["p_lower", "p_higher", "level_if_lower", "level_if_higher"], "additionalProperties": False}
SCHEMA_P = {"type": "object", "properties": {"reason": {"type": "string"}, "h1": P, "h3": P, "h7": P},
            "required": ["reason", "h1", "h3", "h7"], "additionalProperties": False}

INTRO = ("You review quantile forecasts of GPU rental price medians. For one daily series you get its history, the posted price of "
         "each listing, the same GPU in another tracker when there is one, and a base forecast: the 10%, 50% and 90% quantiles of "
         "the median 1, 3 and 7 days ahead, made by a statistical ensemble (a time-series foundation model on each listing and a "
         "listing-level simulator). The forecast is scored by pinball loss in USD against the realised median.\n"
         "How the median moves: it is the middle of about 3 to 15 listings. It changes when a listing near the middle reprices, or "
         "when a listing enters or leaves and the middle shifts to a neighbour's price (an even count gives the mean of the two "
         "middle prices). Most days it does not change. Some listings reprice by a small amount every day for weeks; most are flat "
         "for weeks and then step.\n")
SYSTEM = {
    "echo": INTRO + "Instrument check: return the base forecast exactly as given, every digit unchanged. reason: the word echo.",
    "adj": INTRO + (
        "Task: return adjusted quantiles for the three horizons. The base forecast is strong: across series it beats the flat "
        "last value by 30% of pinball loss, and its errors are concentrated on days when the median changes. Change a quantile "
        "only where the data in front of you gives a concrete reason the ensemble is likely to have missed or mis-sized, for "
        "example: a listing at or next to the middle that drifts daily, so the median will follow it by a computable amount; a "
        "listing whose return or exit would move the middle to a known neighbouring price; the record showing actuals falling "
        "on one side of the band. Compute the median you expect from the listing prices when you can. Where you have no such "
        "reason, return the base numbers unchanged. Keep q10 <= q50 <= q90. reason: at most 40 words, naming what you changed "
        "and the evidence, or \"unchanged\"."),
    "prob": INTRO + (
        "Task: do not restate the forecast. For each horizon give your own probabilities for where the median will be on the "
        "target date relative to the latest median: p_lower (strictly below it), p_higher (strictly above it); the rest is the "
        "probability that it is exactly unchanged. Also give level_if_lower and level_if_higher: the median you expect on the "
        "target date if it has moved in that direction, computed from the listing prices when you can (which listing or "
        "neighbouring pair becomes the middle). Use the base forecast and its record as evidence. reason: at most 40 words."),
}
SCHEMAS = {"echo": SCHEMA_Q, "adj": SCHEMA_Q, "prob": SCHEMA_P}
PARTS = {"echo": ("listings", "other", "record"), "adj": ("listings", "other", "record"), "prob": ("listings", "other", "record")}


def spent():
    """USD of every cached Anthropic response of this arm."""
    usd = 0.0
    for f in glob.glob(str(OUT / "*" / "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            pi, po, _ = MODELS[r["model"]]
            usd += (r["usage"]["input_tokens"] * pi + r["usage"]["output_tokens"] * po) / 1e6 * (0.5 if r.get("batch") else 1.0)
    return usd


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS)); ap.add_argument("--variant", required=True, choices=sorted(SYSTEM))
    ap.add_argument("--origins", default="pilot", help="pilot, dev, locked (2026-10-31..2026-11-05), event (2026-11-06), or a comma list of development origins")
    ap.add_argument("--base", default=f"{ctx.BASE}/forecast.csv", help="the forecast to adjust")
    ap.add_argument("--cells", default=f"{ctx.BASE}/cells.csv", help="comma list: scored cells of the base forecaster, shown as its record (target <= origin only)")
    ap.add_argument("--out", default=str(OUT), help="cache directory")
    ap.add_argument("--replay", help="jsonl of stored responses: no API call; fails if a key is missing or its prompt differs")
    ap.add_argument("--effort", default="low"); ap.add_argument("--limit", type=int); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--series", default=None, help="comma list; default all 37")
    ap.add_argument("--batch", action="store_true", help="Message Batches API: half price, asynchronous")
    ap.add_argument("--out-tokens", type=int, default=1500, help="assumed output tokens per call for the estimate")
    a = ap.parse_args()
    OUT = pathlib.Path(a.out)
    named = {"pilot": PILOT, "dev": ctx.fm2_lib.DEV, "locked": ctx.fm2_lib.LOCKED, "event": [ctx.fm2_lib.EVENT]}
    origins = named[a.origins] if a.origins in named else a.origins.split(",")
    assert a.origins in ("locked", "event") or all(o in ctx.fm2_lib.DEV for o in origins), "origins after the development window only by name"
    pi, po, cutoff = MODELS[a.model]
    assert cutoff < min(origins)[:7], "model training cutoff is not before the origin"
    D = ctx.load(a.base, tuple(a.cells.split(",")), dt.date.fromisoformat(max(origins)))
    series = a.series.split(",") if a.series else list(D["cat"].index)
    path = OUT / a.variant / f"{a.model}.jsonl"; path.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["series_id"], r["origin_date"]) for r in map(json.loads, open(path))} if path.exists() else set()
    todo = [(s, o) for o in origins for s in series if (s, o) not in done][: a.limit]
    print(f"{len(done)} cached, {len(todo)} to call")
    if not todo:
        return
    jobs = [(s, o, ctx.build(D, s, dt.date.fromisoformat(o), parts=PARTS[a.variant])) for s, o in todo]
    for s, o, c in jobs:
        assert "@" not in c["text"] and "http" not in c["text"]            # price data only
    if a.replay:
        stored = {(r["model"], r["variant"], r["series_id"], r["origin_date"]): r for r in map(json.loads, open(a.replay))}
        with open(path, "a") as f:
            for s, o, c in jobs:
                r = stored[(a.model, a.variant, s, o)]                       # KeyError: the response is not stored
                assert r["prompt"] == c["text"] and r["system"] == SYSTEM[a.variant], f"{s} {o}: the stored response answers another prompt"
                f.write(json.dumps(r) + "\n")
        print(f"replayed {len(jobs)} stored responses from {a.replay}, no API call")
        return
    client = anthropic.Anthropic(max_retries=0)
    sample = jobs[:: max(1, len(jobs) // 12)][:12]
    n_in = statistics.mean(client.messages.count_tokens(model=a.model, system=SYSTEM[a.variant], messages=[{"role": "user", "content": c["text"]}]).input_tokens
               for _, _, c in sample)
    est, before = len(jobs) * (n_in * pi + a.out_tokens * po) / 1e6 * (0.5 if a.batch else 1.0), spent()
    print(f"spent so far ${before:.2f}; estimate for this batch ${est:.2f} ({n_in:.0f} input tokens mean of {len(sample)} sampled prompts, {a.out_tokens} output assumed)")
    assert before + est <= CAP_USD, "the batch would pass the cap"
    lock, stop = threading.Lock(), threading.Event()

    def params(c):
        return dict(model=a.model, max_tokens=8000, system=SYSTEM[a.variant], messages=[{"role": "user", "content": c["text"]}],
                    output_config={"effort": a.effort, "format": {"type": "json_schema", "schema": SCHEMAS[a.variant]}})

    def save(job, m, batch=None):
        s, o, c = job
        assert m.stop_reason == "end_turn", f"{s} {o}: stop_reason {m.stop_reason}"
        text = "".join(b.text for b in m.content if b.type == "text")
        rec = {"model": m.model, "variant": a.variant, "effort": a.effort, "series_id": s, "origin_date": o, "last_value": c["last_value"], "base_file": a.base,
               "base": {str(k): v for k, v in c["base"].items()}, "system": SYSTEM[a.variant], "prompt": c["text"], "raw": text,
               "usage": {"input_tokens": m.usage.input_tokens, "output_tokens": m.usage.output_tokens}, "id": m.id, "batch": batch}
        assert m.model == a.model
        with lock:
            with open(path, "a") as f:
                f.write(json.dumps(rec) + "\n")
            if spent() > CAP_USD:
                stop.set()

    def call(job):
        if stop.is_set():
            return
        for attempt in range(8):
            try:
                m = client.messages.create(**params(job[2]))
                break
            except (anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError) as e:
                print(f"retry {attempt + 1} {job[0]} {job[1]}: {type(e).__name__}", flush=True)
                time.sleep(min(60, 5 * 2 ** attempt))
        else:
            raise RuntimeError(f"gave up on {job[0]} {job[1]}")
        save(job, m)

    if a.batch:
        b = client.messages.batches.create(requests=[{"custom_id": f"r{i}", "params": params(j[2])} for i, j in enumerate(jobs)])
        print("batch", b.id, flush=True)
        (path.parent / f"{a.model}.batches.txt").open("a").write(f"{b.id} {len(jobs)} {dt.datetime.now().isoformat(timespec='seconds')}\n")
        while b.processing_status != "ended":
            time.sleep(30)
            b = client.messages.batches.retrieve(b.id)
            print(b.processing_status, b.request_counts, flush=True)
        failed = []
        for r in client.messages.batches.results(b.id):
            if r.result.type == "succeeded":
                save(jobs[int(r.custom_id[1:])], r.result.message, batch=b.id)
            else:
                failed.append((r.custom_id, r.result))
        assert not failed, failed
        print(f"done; spent ${spent():.2f} in all, ${spent() - before:.2f} on this batch")
        return
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for i, _ in enumerate(ex.map(call, jobs)):
            if i % 25 == 24:
                print(f"{i + 1}/{len(jobs)} ${spent():.2f}", flush=True)
    assert not stop.is_set(), "stopped at the cap"
    print(f"done; spent ${spent():.2f} in all, ${spent() - before:.2f} on this batch")


if __name__ == "__main__":
    main()
