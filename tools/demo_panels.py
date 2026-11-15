"""The 15 depth panels of the /demo page (tools/demo.py), opened in the words column when a judge asks a question.

tools/demo.py puts PANEL_CSS and PANELS_JS into its page at the placeholders /*__PANEL_CSS__*/ and /*__PANELS_JS__*/.
Before PANELS_JS runs, the page defines FACTS and SOURCES (from tools/demo_facts.py: v, n, src and at per key),
esc(s), HUES, hueOf(person), ago(ns) and fv(key), and the Design page's panel classes .dhead, .lead, .facts, .rows
and .hue. PANELS maps "<step>/<detail>" to {name, lit, html(F, m)}: name is the heading that demo.py draws in .dhead
(and the label of the step's button), lit is null or the scene symbols to light, and html returns the panel body. F
is FACTS; m is the page's model of /data and may be null. Every number is read from F when the panel opens, so
editing tools/demo_facts.py (or running tools/demo_refresh.py) refreshes the panels. Each panel ends with one quiet
source line, "<source>, <Mon D, HH:MM> UTC", and at most two links of one line each. Each body fits the words column
at 1440 x 860 without scrolling, except the source list of brain/sources.
CSS here uses only selectors that start with .dp- and only the page's colour tokens.
"""

PANEL_CSS = r"""
.dp-body .lead, .dp-body .facts { max-width: none; }
.dp-body .lead { margin-top: 14px; }
.dp-body .facts { margin-top: 12px; line-height: 1.38; }
.dp-body .facts li { padding: 6px 0; }
.dp-body .rows { margin-top: 12px; }
.dp-n { color: var(--ink); font-weight: 520; }
.dp-cue { color: var(--ink); font-weight: 560; white-space: pre; }
.dp-src { margin: 10px 0 0; font-size: clamp(12px, .82vw, 15.5px); line-height: 1.4; color: var(--mute); }
.dp-src a, .dp-in a { color: inherit; text-decoration: underline; text-decoration-color: var(--faint); text-underline-offset: 2px; }
.dp-src a:hover, .dp-in a:hover { color: var(--ink); }
.dp-open { display: flex; gap: .6em; align-items: baseline; }
.dp-open::before { content: ""; flex: none; width: 9px; height: 9px; border-radius: 50%; border: 1.5px solid var(--mute); transform: translateY(1px); }
.dp-id { color: var(--mute); font-size: .9em; margin-left: .5em; }
.dp-links a { padding-top: 6px; padding-bottom: 6px; }
.dp-links a::before { top: 9px; bottom: 9px; }
.dp-body .dp-read { margin-top: 8px; }
.dp-read a { padding-top: 4px; padding-bottom: 4px; }
.dp-read a::before { top: 7px; bottom: 7px; }
.dp-read .t { -webkit-line-clamp: 1; }
.dp-case { margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--rule); font-size: clamp(13.5px, 1vw, 19px); line-height: 1.38; }
.dp-q { color: var(--mute); display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 1; overflow: hidden; }
.dp-url { display: block; margin-top: 2px; color: var(--ink); font-weight: 560; text-decoration: none; overflow-wrap: anywhere; }
.dp-url:hover { text-decoration: underline; }
.dp-did { margin: 2px 0 0; }
.dp-did a { color: inherit; }
.dp-who { color: var(--c); font-weight: 600; }
.dp-line { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0 .7em; margin-top: 2px; }
.dp-line .dp-url { display: inline; margin: 0; }
.dp-meta { font-size: .86em; color: var(--mute); }
.dp-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--blue); margin-right: 6px; vertical-align: .12em; }
.dp-group { margin-top: 18px; }
.dp-sub { margin: 14px 0 0; font-size: clamp(13px, .95vw, 18px); font-weight: 600; color: var(--mute); }
"""

PANELS_JS = r"""
const PANELS = (() => {
  // Reading F. A missing key gives null, never an exception; numbers come only from F.
  const V = (F, k) => (F && F[k] ? F[k].v : null);
  const N = (F, k) => (F && F[k] ? F[k].n : null);
  const A = (F, k) => (F && F[k] ? F[k].at : null);
  const O = (F, k) => { const v = V(F, k); return v && typeof v === "object" ? v : {}; };
  const num = x => typeof x === "number" && isFinite(x);
  // Printing. fmt never prints undefined, null or NaN.
  const fmt = x => x == null || (typeof x === "number" && !isFinite(x)) ? "not recorded" : typeof x === "number" ? (Number.isInteger(x) ? x.toLocaleString("en-US") : String(Math.round(x * 100) / 100)) : esc(String(x));
  const n = x => `<span class="dp-n">${fmt(x)}</span>`;
  const pc = x => `<span class="dp-n">${fmt(x)}%</span>`;
  const sgn = x => !num(x) ? fmt(x) : x > 0 ? "+" + fmt(x) : x < 0 ? "\u2212" + fmt(-x) : fmt(x);
  const pts = x => `<span class="dp-n">${sgn(x)}</span>`;
  const ci = a => {
    if (!Array.isArray(a) || !num(a[0]) || !num(a[1])) return "";
    const d = !Number.isInteger(a[0]) || !Number.isInteger(a[1]);
    const one = x => (x < 0 ? "\u2212" : "") + (d ? Math.abs(x).toFixed(1) : fmt(Math.abs(x)));
    return `[${one(a[0])}, ${one(a[1])}]`;
  };
  const pct = (a, b) => num(a) && num(b) && b ? Math.round(100 * a / b) : null;
  const pt = (a, total) => num(a) && num(total) && total ? Math.round(1000 * a / total) / 10 : null;  // problems as points
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const when = at => {
    const t = String(at || "").match(/(\d{4})-(\d\d)-(\d\d)[ T](\d\d:\d\d)/);
    return t ? `${MON[+t[2] - 1]} ${+t[3]}, ${t[4]} UTC` : "";
  };
  const newest = (F, keys) => keys.map(k => A(F, k)).filter(Boolean).map(s => String(s).slice(0, 16).replace("T", " ")).sort().pop();
  const ID = /\b(?:result|knowledge|work|idea|skill)-[0-9a-f]{6}\b/;
  const board = id => `<a href="/#${esc(id)}">${esc(id)}</a>`;
  const ext = (url, text) => `<a href="${esc(url)}" target="_blank" rel="noopener">${text}</a>`;
  const bare = url => String(url || "").replace(/^https?:\/\//, "").replace(/\/$/, "");
  const cueText = s => "\u201c" + esc(s == null ? "" : s).replace(/\n/g, "\\n") + "\u201d";
  const facts = list => `<ul class="facts">${list.map(x => `<li>${x}</li>`).join("")}</ul>`;
  const open = x => `<span class="dp-open"><span>${x}</span></span>`;  // one flex item, so inline numbers do not split the text
  const body = (lead, ...parts) => `<div class="dp-body"><p class="lead">${lead}</p>${parts.join("")}</div>`;

  // The quiet source line: "<source>, <Mon D, HH:MM> UTC". ids become board links; time is the newest of keys.
  const src = (label, ids, F, keys) => {
    const t = keys && keys.length ? newest(F, keys) : null;
    const list = (ids || []).map(board).join(", ");
    const head = [label, list].filter(Boolean).join(label && list ? " " : "");
    return `<p class="dp-src">${head}${t ? ", " + when(t) : ""}</p>`;
  };

  // Link rows: one line each, a fixed label, then the id or address in the quiet colour.
  const bar = who => { const h = who ? hueOf(who) : null; return h == null ? ` style="--c:var(--mute)"` : ` class="hue" style="--h:${h}"`; };
  const link = (href, label, quiet, out) => `<a href="${esc(href)}"${out ? ` target="_blank" rel="noopener"` : ""} style="--c:var(--mute)"><span class="t">${label}${quiet ? `<span class="dp-id">${quiet}</span>` : ""}</span></a>`;
  const links = list => `<div class="rows dp-links">${list.join("")}</div>`;
  const toBoard = (id, label) => link("/#" + id, esc(label), esc(id));
  const toPanel = (key, label) => link("#" + key, esc(label), "");
  const row = (href, text, meta, who, out) => {
    const tgt = out ? ` target="_blank" rel="noopener"` : "";
    return `<a${bar(who)} href="${esc(href)}"${tgt}><span class="t">${text}</span><span class="m">${meta}</span></a>`;
  };

  const recall = () => (typeof FACTS !== "undefined" && FACTS.past_cross_agent_recall && FACTS.past_cross_agent_recall.v) || {};
  const first = s => String(s || "").split(",")[0].trim();

  return {
    "problem/day1": {
      name: "Our first hours, measured", lit: null,
      html: (F, m) => body(
        `Before the speed rules existed, we counted where our agents' time went.`,
        facts([
          `One run of ${n(N(F, "shard_whole_minutes"))} harder problems took ${n(V(F, "shard_whole_minutes"))} minutes on one H100.`,
          `Agents generated that same run ${n(V(F, "day1_cell_repeats"))} times; the count is approximate, read from the command log and the board.`,
          `Agents waited for a person during ${n(V(F, "day1_wait_for_person_minutes"))} of ${n(N(F, "day1_wait_for_person_minutes"))} session minutes; this has not been measured again.`,
          `Agents checked on their GPU jobs ${n(V(F, "day1_polls"))} times with gpu.py ls or gpu.py logs.`,
        ]),
        src("board", ["result-17a66c"], F, ["day1_wait_for_person_minutes"]),
        links([toBoard("result-17a66c", "Day-1 turnaround report"), toPanel("infra/people", "Who did what")])),
    },

    "proof/turnaround": {
      name: "From claim to result", lit: ["board"],
      html: (F, m) => {
        const st = O(F, "stage_median_min"), cmp = V(F, "auto_research_comparison");
        return body(
          `The median work item took ${n(V(F, "claim_to_close_median_min"))} minutes from claim to result over ${n(N(F, "claim_to_close_median_min"))} closed items; a quarter took more than ${n(V(F, "claim_to_close_upper_quartile_min"))}.`,
          facts([
            `Items that ran GPU jobs spent a median of ${n(st.jobs)} minutes in them; how many items that is, is not recorded.`,
            `${n(V(F, "gpu_submit_commands"))} GPU job submissions came from agent sessions; of ${n(N(F, "gpu_submit_by_person_shell"))} checked, ${n(V(F, "gpu_submit_by_person_shell"))} came from a person's shell.`,
            `Ended GPU jobs used ${n(V(F, "gpu_hours"))} GPU-hours; no file records the total spend in dollars.`,
            open(cmp == null ? `A comparison with one agent on the same budget is not measured yet.` : `Against one agent on the same budget: ${fmt(cmp)}.`),
          ]),
          src("board and agent event log", [], F, ["claim_to_close_median_min", "gpu_submit_commands"]),
          links([toPanel("infra/people", "Who did what"), toPanel("problem/day1", "Our first hours, measured")]));
      },
    },

    "result/cue": {
      name: "The cue", lit: null,
      html: (F, m) => {
        const T = N(F, "math500_rl"), c = V(F, "math500_base_cue"), r = V(F, "math500_rl"), t6 = V(F, "math500_base_plain_t06");
        const tok = O(F, "math500_mean_tokens"), rd = O(F, "math500_base_cue_redraws"), lit = O(F, "cue_paper_literal_rule"), paper = O(F, "cue_paper");
        return body(
          `The cue is ${n(N(F, "cue_text"))} tokens, <span class="dp-cue">${cueText(V(F, "cue_text"))}</span>, placed at the start of the model's answer.`,
          facts([
            `Both models get the same prompt, sampling (T 1.0, top-p 1.0) and grader; base + cue writes ${n(tok.base_cue)} tokens per problem, the RL-trained model ${n(tok.rl)}.`,
            `At its best temperature, T 0.6, the base model scores ${n(t6)} of ${n(T)}; against that, the cue adds ${n(pt(c - t6, T))} of ${n(pt(r - t6, T))} points.`,
            `The cue was chosen on these ${n(T)} problems; on ${n(N(F, "hard328_rl"))} held-out harder problems base + cue scores ${n(V(F, "hard328_base_cue"))} against ${n(V(F, "hard328_rl"))} for RL.`,
            `Other samples of base + cue scored ${n(rd.lo)} to ${n(rd.hi)} of ${n(T)}, so one run moves by a few problems.`,
            `<span class="dp-in">Wang et al. (${ext(paper.url || "https://arxiv.org/abs/2610.06851", esc(String(paper.cite || "").replace(/^.*?,\s*/, "")))}) published the cue; under their answer rule our samples score ${pc(pt(lit.lo, T))} to ${pc(pt(lit.hi, T))}, below their ${pc(lit.theirs_pct)}.</span>`,
          ]),
          src("board", ["result-c36598", "result-533123", "result-60d899"]),
          links([toPanel("result/harder", "Harder problems and code"), toPanel("why/control", "How we know")]));
      },
    },

    "result/harder": {
      name: "Harder problems and code", lit: null,
      html: (F, m) => {
        const hb = V(F, "hard328_base_plain"), hc = V(F, "hard328_base_cue"), hr = V(F, "hard328_rl"), H = N(F, "hard328_rl");
        const cb = V(F, "code_base_plain"), cm = V(F, "code_base_math_cue"), cr = V(F, "code_rl"), C = N(F, "code_rl"), sd = O(F, "shard_detail");
        return body(
          `The cue gives ${pc(pct(hc - hb, hr - hb))} of RL's gain over the base model on ${n(H)} harder problems and ${pc(pct(cm - cb, cr - cb))} on ${n(C)} code problems, against ${pc(Math.round(V(F, "math500_share_of_gain_closed_pct")))} on MATH-500.`,
          facts([
            `On ${n(H)} harder problems absent from the RL training prompts, the base model solves ${n(hb)}, base + cue ${n(hc)} and the RL-trained model ${n(hr)}.`,
            `Two reruns of base + cue on those problems gave ${n(sd.right_shard4)} and ${n(sd.right_whole_h200)}, so one run moves by several problems.`,
            `Of ${n(C)} code problems the base model passes ${n(cb)}, ${n(cm)} with the Math cue and ${n(V(F, "code_base_code_cue"))} with a Code cue; the Code RL-trained model passes ${n(cr)}.`,
            open(`Only Olmo 3 7B and its RL-trained versions are measured; a second model family and a vote on code are open.`),
          ]),
          src("board", ["result-82b4dc", "result-59ed1a"], F, ["hard328_rl", "code_rl"]),
          links([toBoard("result-82b4dc", "The 328 harder problems"), toBoard("result-59ed1a", "The code pair")]));
      },
    },

    "vote/procedure": {
      name: "Under a vote", lit: null,
      html: (F, m) => {
        const vb = V(F, "vote4_restart_base"), vr = V(F, "vote4_restart_rl"), T = N(F, "vote4_restart_rl"), a = O(F, "chart_audit");
        return body(
          `A vote over 4 samples takes base + cue to ${n(vb)} of ${n(T)}; the RL-trained model reaches ${n(vr)} under the same vote.`,
          facts([
            `Both models restart answers that hit the length cap and spend about the same tokens per problem, ${n(V(F, "vote4_restart_base_tokens_per_problem"))} and ${n(V(F, "vote4_restart_rl_tokens_per_problem"))}.`,
            `RL leads by ${n(pt(vr - vb, T))} points under the vote and by ${n(V(F, "math500_gap_points"))} points ${ci(V(F, "math500_gap_ci95"))} with one sample.`,
            `The board's chart shows ${n(a.chart_best_base)} for base + cue; our audit counts ${n(a.audited_best_base)}, because the tie rule behind ${n(a.chart_best_base)} was written after reading the problems it fixes.`,
            `The vote was run on MATH-500, the set on which the cue was chosen.`,
          ]),
          src("board", ["result-5d032f", "result-e78dfe"], F, ["vote4_restart_base", "chart_audit"]),
          links([toBoard("result-5d032f", "Vote, both models"), toPanel("rules/audit", "Chart audit")]));
      },
    },

    "why/control": {
      name: "How we know", lit: null,
      html: (F, m) => {
        const rs = O(F, "anatomy_right_samples"), S = N(F, "anatomy_right_samples"), P = N(F, "reliability_share_pct"), k = num(S) && num(P) && P ? S / P : null;
        const yue = O(F, "reliability_closest_paper"), rel = (V(F, "finding_pages") || []).find(p => p.slug === "rl-reliability") || {};
        return body(
          `Each model answered ${n(P)} problems ${n(k)} times: ${n(rs.base_cue)} right answers for base + cue, ${n(rs.rl)} for the RL-trained model.`,
          facts([
            `${pc(V(F, "reliability_share_pct"))} of RL's ${n(V(F, "reliability_gap_samples"))} extra right answers are on problems base + cue solves at least once in ${n(k)} samples.`,
            `${pc(V(F, "new_problems_share_pct"))} ${ci(V(F, "new_problems_share_ci95"))} are on the ${n(V(F, "binomial_null_observed_problems"))} problems it never solves; if all problems were equally hard, chance would leave ${n(V(F, "binomial_null_expected_problems"))}.`,
            `Classed by three samples and scored on the fourth, the never-solved share is ${pc(V(F, "reliability_held_out_share_pct"))} ${ci(V(F, "reliability_held_out_ci95"))}.`,
            `Within ${n(k)} samples base + cue solves ${n(V(F, "base_cue_any_of_4_problems"))} problems against ${n(V(F, "math500_rl"))} for one RL sample: the known gap between several samples and one.`,
          ]),
          src("board", ["result-afc423"], F, ["reliability_share_pct"]),
          links([link(yue.url || "https://arxiv.org/abs/2504.13837", "Closest published result", esc(yue.cite || ""), true),
                 link("/finding/rl-reliability", esc(rel.line || "Finding page"), "finding page")]));
      },
    },

    "why/findings": {
      name: "Other findings", lit: null,
      html: (F, m) => {
        const T = N(F, "math500_base_cue");
        return body(
          `Two tests probe what the last points need: a matched weight control and a model trained by imitation only.`,
          facts([
            `Adding a quarter of the RL weight difference to the base model gives ${pts(V(F, "wdiff_quarter_points"))} points ${ci(V(F, "wdiff_quarter_ci95"))} over base + cue; a random difference of the same norm gives ${pts(V(F, "wdiff_random_control_points"))} ${ci(V(F, "wdiff_random_control_ci95"))}.`,
            `After rounding, the quarter blend lies ${n(V(F, "wdiff_quarter_norm_ratio"))} of the full difference from the base model; the extra distance is rounding noise.`,
            `Think-SFT with the cue, trained by imitation with no reward, scores ${n(V(F, "think_sft_cue_math500"))} of ${n(N(F, "think_sft_cue_math500"))}, ${pts(V(F, "think_sft_minus_rl_points"))} points ${ci(V(F, "think_sft_minus_rl_ci95"))} from RL; its traces were written by other models.`,
            `Two finding pages carry open audit caveats: What RL changed uses a borrowed lens, and Eight directions compares with the base model although the cue alone gives ${pc(pct(V(F, "math500_base_cue"), T))}.`,
          ]),
          src("board", ["result-4b0d5f"], F, ["wdiff_quarter_points", "think_sft_cue_math500"]),
          links([toBoard("result-4b0d5f", "Weight-difference blends")]));
      },
    },

    "rules/thread": {
      name: "The correction", lit: null,
      html: (F, m) => {
        const a = O(F, "retraction_claim"), b = O(F, "retraction_correction"), th = V(F, "retraction_thread") || [];
        return body(
          `A gain of ${pts(a.points)} points failed its own second draw, and the same person's agents posted the correction ${n(V(F, "retraction_minutes_between"))} minutes later.`,
          facts([
            `With 3 answers written by the RL-trained model in the base model's context, the first draw scored ${n(a.right)} of ${n(a.n)}, ${pts(a.points)} points ${ci(a.ci95)}.`,
            `With 3 other examples, the second draw scored ${n(b.right)} of ${n(b.n)}, ${pts(b.points)} points ${ci(b.ci95)}.`,
            th.length > 1 ? `An audit comment flagged the second draw at ${when(th[0].at)}, and the correction followed at ${when(th[1].at).replace(/^\w+ \d+, /, "")}.` : `The comments on the first post are on the board.`,
            `The score row of the first post, ${n(a.right)} of ${n(a.n)}, is still stored in the chart data.`,
          ]),
          src("board", ["result-6d422d", "result-5227b9"], F, ["retraction_correction"]),
          links([toBoard("result-6d422d", "The first post"), toBoard("result-5227b9", "The correction")]));
      },
    },

    "rules/audit": {
      name: "Chart audit", lit: ["board"],
      html: (F, m) => {
        const a = O(F, "chart_audit");
        return body(
          `A second agent audited our MATH-500 chart for leaks of the answer key and found none in the code.`,
          facts([
            `The grader rejected ${n(a.planted_wrong_rejected)} of ${n(a.planted_wrong)} planted wrong answers.`,
            `A regrade of ${n(a.rows_regraded)} rows gave ${n(a.regrade_mismatches)} mismatches.`,
            `The best base + cue score went from ${n(a.chart_best_base)} to ${n(a.audited_best_base)} of ${n(a.n)}. Cells whose raw answers are not in git were not recounted: ${fmt(a.not_recounted)}.`,
            `The auditor is a model of the same family as the agents, and no person hand-checked a counted sample.`,
          ]),
          src("board", ["result-e78dfe"], F, ["chart_audit"]),
          links([toBoard("result-e78dfe", "Audit of the chart")]));
      },
    },

    "rules/rejected": {
      name: "What the agents rejected", lit: ["board"],
      html: (F, m) => {
        const ids = O(F, "refuted_or_negative_result_ids"), neg = (ids.negative_headline || []).length, ref = (ids.says_refuted || []).length;
        return body(
          `The rules ask agents to post a prediction that turns out wrong as a result.`,
          facts([
            `${n(neg)} of ${n(N(F, "refuted_or_negative_results"))} results report a negative result in their first sentence.`,
            `${n(ref)} more say that at least one of their predictions was refuted, while the rest of the result may stand.`,
            `Both counts are a text match read by hand, so they are approximate.`,
            `Before any GPU job, one literature sweep closed ${n(O(F, "exa_case_best").method_families)} method families as already published.`,
          ]),
          src("board", [], F, ["refuted_or_negative_results"]),
          links([toBoard("result-8de03b", "No theory survives"), toBoard("result-60d899", "Our lead over Wang et al. is a grader effect")]));
      },
    },

    "infra/modal": {
      name: "On Modal", lit: ["board", "actor", "ext-modal"],
      html: (F, m) => {
        const pk = O(F, "gpu_peak_containers"), e = O(F, "gpu_jobs_ended"), sd = O(F, "shard_detail");
        return body(
          `Agents start GPU jobs on Modal with one command, and a job runs only from a pushed commit.`,
          facts([
            `The jobs need what a hosted API cannot serve: blended weights, zeroed neurons and the activations of both models.`,
            `${n(pk.all)} GPU containers ran at once at the peak, ${n(pk.per_workspace)} in each of the three workspaces.`,
            `${n(V(F, "gpu_hours"))} GPU-hours were used by ${n(N(F, "gpu_hours"))} ended GPU jobs; of all ${n(e.ended)} ended jobs, ${n(e.exit_nonzero)} exited with an error.`,
            `The median wait for a container was ${n(V(F, "submit_to_start_median_s"))} seconds; a quarter of the ${n(V(F, "gpu_jobs_started"))} started jobs waited over ${n(V(F, "submit_to_start_upper_quartile_min"))} minutes.`,
            `The split over ${n(sd.shards)} H100s was measured once each way: ${pc(pct(sd.gpu_min_shard4 - sd.gpu_min_whole, sd.gpu_min_whole))} more GPU minutes, and ${n(sd.right_shard4)} right against ${n(sd.right_whole)}.`,
          ]),
          src("Modal job records", [], F, ["gpu_hours"]),
          links([toBoard("result-dfe78e", "Whole run against 4 shards")]));
      },
    },

    "infra/people": {
      name: "Who did what", lit: ["board", "all-swarms"],
      html: (F, m) => {
        const hm = V(F, "human_messages"), bp = O(F, "board_posts_by_agents"), rate = V(F, "tool_calls_per_human_message");
        const lead = hm == null
          ? `${n(V(F, "people"))} people steer the agents; the count of messages they typed is not counted yet.`
          : `${n(V(F, "people"))} people typed ${n(hm)} messages; the agents made at least ${n(V(F, "agent_tool_calls"))} tool calls, about ${n(num(rate) ? Math.round(rate) : null)} per message.`;
        return body(lead,
          facts([
            `Agents posted ${n(bp.idea)} ideas, ${n(V(F, "results_on_board"))} results and ${n(bp.comment)} comments, and made ${n(V(F, "gpu_submit_commands"))} GPU job submissions.`,
            `Of ${n(N(F, "logged_commands_from_shell"))} logged board, GPU and paper commands, ${n(V(F, "logged_commands_from_shell"))} came from a person's shell.`,
            `The ${n(V(F, "people"))} people started the sessions, wrote the research direction and the rules, and approve the public finding pages.`,
            `In our first hours, agents waited for a person during ${n(V(F, "day1_wait_for_person_minutes"))} of ${n(N(F, "day1_wait_for_person_minutes"))} session minutes.`,
            `The tool-call count is a lower bound: the transcripts hold about ${pc(V(F, "transcript_coverage_pct"))} of the logged commands, and no Codex sessions.`,
          ]),
          src("agent transcripts and event log", [], F, ["human_messages", "logged_commands_from_shell"]),
          links([toBoard("result-ecbb9d", "Count of typed messages"), toPanel("proof/turnaround", "From claim to result")]));
      },
    },

    "brain/sources": {
      name: "Sources", lit: ["board", "actor", "ext-exa"],
      html: (F, m) => {
        const a = O(F, "exa_case_best"), b = O(F, "exa_case_lens"), c = O(F, "exa_case_novelty");
        const kase = (k, url, did) => `<div class="dp-case"><span class="dp-q">\u201c${esc(k.query || "")}\u201d</span>` +
          `<span class="dp-line"><a class="dp-url" href="${esc(url || "")}" target="_blank" rel="noopener">${esc(bare(url))}</a>` +
          `<span class="dp-meta"><span${bar(k.who)}><span class="dp-who">${esc(k.who || "")}</span></span>, ${when(k.searched_utc)}</span></span><p class="dp-did">${did}</p></div>`;
        const groups = {};
        (typeof SOURCES !== "undefined" ? SOURCES : []).forEach(s => {
          const host = bare(s.url).split("/")[0].replace(/^www\./, "");
          (groups[host] = groups[host] || []).push(s);
        });
        const order = Object.keys(groups).sort((x, y) => groups[y].length - groups[x].length || x.localeCompare(y));
        const list = order.map(h => `<div class="rows dp-group"><h3>${esc(h)}, ${fmt(groups[h].length)}</h3>` + groups[h].map(s =>
          row(s.url, (s.cited ? `<span class="dp-dot" aria-hidden="true"></span>` : "") + esc(bare(s.url)),
              `<b>${esc(s.who)}</b> ${esc(s.at)} UTC${s.cited ? ", cited in " + esc(s.cited) : ""}`, s.who, true)).join("") + `</div>`).join("");
        return body(
          `${n(V(F, "exa_successful_calls"))} of ${n(N(F, "exa_successful_calls"))} calls to Exa returned results for ${n(V(F, "exa_agents"))} agents, who fetched ${n(V(F, "exa_urls_fetched"))} pages.`,
          kase(a, a.paper_url, `A sweep by ${n(a.scouts)} agents, citing ${n(a.papers_cited)} papers, closed ${n(a.method_families)} method families with no GPU job (${board(a.board_item || "knowledge-d692e4")}, ${n(a.minutes_search_to_post)} minutes later).`),
          kase(b, b.source_url, `A published lens for our base model was loaded (${board(b.board_item || "knowledge-0220f1")}); a full fit still ran later.`),
          kase(c, c.source_url, `It is the closest published result on the Eight directions finding page (${board(c.also || "knowledge-9d0f85")}).`),
          facts([
            `Agents must search Exa before a new measurement, and in the theory rounds it is the model's only web access.`,
            `${n(V(F, "exa_mcp_failed_calls"))} Exa MCP calls failed with 401; early on, one person's agents used another search tool.`,
          ]),
          src("agent session transcripts", [], F, ["exa_successful_calls"]),
          list);
      },
    },

    "brain/memory": {
      name: "Shared memory", lit: ["board", "p:" + first(recall().writer), "p:" + first(recall().reader)],
      fx: "recall", writer: first(recall().writer), reader: first(recall().reader),
      html: (F, m) => {
        const r = O(F, "past_cross_agent_recall"), reader = first(r.reader), writer = first(r.writer);
        const id = (String(r.returned || "").match(ID) || ["knowledge-e6bc68"])[0];
        const pl = O(F, "past_pilot"), pd = O(F, "past_pilot_detail"), fr = O(F, "past_recall_returns_first_result");
        const fact = String(r.fact_text || "").replace(/\s+\S*$/, "");
        return body(
          `One memory on past.dev holds ${n(V(F, "past_stored_sources"))} sources and has answered ${n(V(F, "past_recalls"))} recall requests.`,
          `<div class="rows dp-read"><h3>One read across people</h3>` +
            row("/#" + id, `\u201c${esc(r.query || "")}\u201d`, `asked by <b>${esc(reader)}</b>'s agent, ${when(r.read_utc)}`, reader) +
            row("/#" + id, esc(String(r.returned || "").replace(/\s+/g, " ").trim()), `what past.dev returned`, null) +
            row("/#" + id, `${esc(id)}: ${esc(fact)}`, `written by <b>${esc(writer)}</b>'s agent, ${when(r.written_utc)}`, writer) + `</div>`,
          facts([
            `The reader opened it ${n(r.opened_after_s)} seconds later and left that paper out of its next sweep (${board(r.sweep_item || "work-6b1fa5")}).`,
            `In one pilot run on ${n(pl.questions)} templated questions, recall had the answer within ${n(V(F, "recall_max_tokens"))} tokens for ${n(pl.recall_hits_in_2000_tokens)}, a naive grep for ${n(pl.grep_hits_in_2000_tokens)} (${n(pd.grep_hit_any)} anywhere).`,
            `No write carries a per-agent identity or audience.`,
            open(`Recall for that setting returned the first post, ${n(fr.right)} of ${n(fr.n)}; whether the correction comes back too is not checked.`),
          ]),
          src("past.dev usage API", ["result-11042c"], F, ["past_recalls"]));
      },
    },

    "retro/changes": {
      name: "What the reviews changed", lit: null,
      html: (F, m) => {
        const mc = O(F, "max_containers_change"), ps = O(F, "planted_waste_skill"), pp = O(F, "planted_waste_plain");
        return body(
          `${n(V(F, "meta_review_entries"))} Retro review entries in meta/ record waste that agents found in the team's logs and what they changed.`,
          facts([
            `After a Retro review raised the Modal H100 limit from ${n(mc.from)} to ${n(mc.to)} containers, the median wait fell from ${n(V(F, "h100_wait_before_min"))} minutes (${n(N(F, "h100_wait_before_min"))} jobs) to ${n(V(F, "h100_wait_after_s"))} seconds (${n(N(F, "h100_wait_after_s"))} jobs).`,
            `That change had no control: the two periods differ in hours and load.`,
            `On planted waste, three Retro reviews cut compute per batch from ${n(ps.before_min)} to ${n(ps.after_min)} container minutes; a plain instruction went from ${n(pp.before_min)} to ${n(pp.after_min)}.`,
            `That test had ${n(N(F, "planted_waste_skill"))} runs per arm; on clean work the Retro review cut a required step and the answers went wrong.`,
            open(`An effect on the whole lab is not measured.`),
          ]),
          src("meta/ and Modal job records", [], F, ["h100_wait_after_s"]),
          links([toBoard("result-8b2682", "Planted-waste test")]));
      },
    },
  };
})();
"""
