"""The 14 depth panels of the /demo page (tools/demo.py), opened in the words column when a judge asks a question.

tools/demo.py puts PANEL_CSS and PANELS_JS into its page at the placeholders /*__PANEL_CSS__*/ and /*__PANELS_JS__*/.
Before PANELS_JS runs, the page defines FACTS and SOURCES (from tools/demo_facts.py: v, n, src and at per key),
esc(s), HUES, hueOf(person), ago(ns) and fv(key), and the Design page's panel classes .dhead, .lead, .facts, .rows
and .hue. PANELS maps "<step>/<detail>" to {name, lit, html(F, m)}: name is the heading that demo.py draws in .dhead,
lit is null or the scene symbols to light, and html returns the panel body. F is FACTS; m is the page's model of
/data and may be null. Every number is read from F when the panel opens, so editing tools/demo_facts.py refreshes
the panels, and each panel ends its facts with one quiet line that names where and when its numbers were measured.
CSS here uses only selectors that start with .dp- and only the page's colour tokens.
"""

PANEL_CSS = r"""
.dp-n { color: var(--ink); font-weight: 520; }
.dp-cue { color: var(--ink); font-weight: 560; white-space: pre; }
.dp-src { margin: 14px 0 0; font-size: clamp(12px, .82vw, 15.5px); line-height: 1.45; color: var(--mute); max-width: 46ch; overflow-wrap: anywhere; }
.dp-src a { color: inherit; text-decoration: underline; text-decoration-color: var(--rule); text-underline-offset: 2px; }
.dp-src a:hover { color: var(--ink); }
.dp-in a { color: var(--ink); text-decoration: underline; text-decoration-color: var(--faint); text-underline-offset: 2px; }
.dp-open { display: flex; gap: .6em; align-items: baseline; }
.dp-open::before { content: ""; flex: none; width: 9px; height: 9px; border-radius: 50%; border: 1.5px solid var(--mute); transform: translateY(1px); }
.dp-long .t { -webkit-line-clamp: 3; }
.dp-two .t { -webkit-line-clamp: 2; }
.dp-case { margin-top: 16px; padding-top: 10px; border-top: 1px solid var(--rule); font-size: clamp(14.5px, 1.1vw, 21px); line-height: 1.4; max-width: 44ch; }
.dp-case:first-of-type { margin-top: 18px; }
.dp-q { color: var(--mute); display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
.dp-url { display: block; margin-top: 4px; color: var(--ink); font-weight: 560; text-decoration: none; overflow-wrap: anywhere; }
.dp-url:hover { text-decoration: underline; }
.dp-did { margin: 4px 0 0; }
.dp-did a { color: inherit; }
.dp-who { color: var(--c); font-weight: 600; }
.dp-meta { display: block; margin-top: 2px; font-size: .86em; color: var(--mute); }
.dp-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--blue); margin-right: 6px; vertical-align: .12em; }
.dp-group { margin-top: 18px; }
"""

PANELS_JS = r"""
const PANELS = (() => {
  // Formatting. Numbers come only from F; these helpers only print them.
  const V = (F, k) => (F[k] ? F[k].v : null);
  const fmt = x => x == null ? "not recorded" : typeof x === "number" ? (Number.isInteger(x) ? x.toLocaleString("en-US") : String(Math.round(x * 100) / 100)) : esc(String(x));
  const n = x => `<span class="dp-n">${fmt(x)}</span>`;
  const sgn = x => x > 0 ? "+" + fmt(x) : x < 0 ? "\u2212" + fmt(-x) : fmt(x);
  const pts = x => `<span class="dp-n">${sgn(x)}</span>`;
  const neg = x => x < 0 ? "\u2212" + fmt(-x) : fmt(x);
  const ci = a => `[${neg(a[0])}, ${neg(a[1])}]`;
  const pct = (a, b) => Math.round(100 * a / b);
  const pt = (a, total) => Math.round(1000 * a / total) / 10;  // a count of problems as points of a total
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const when = at => {
    const t = String(at || "").match(/(\d{4})-(\d\d)-(\d\d)[ T](\d\d:\d\d)/);
    return t ? `${MON[+t[2] - 1]} ${+t[3]}, ${t[4]} UTC` : esc(String(at || ""));
  };
  const ID = /\b(?:result|knowledge|work|idea|skill)-[0-9a-f]{6}\b/g;
  const board = id => `<a href="/#${id}">${id}</a>`;
  const ext = (url, text) => `<a href="${esc(url)}" target="_blank" rel="noopener">${text}</a>`;
  const bare = url => String(url).replace(/^https?:\/\//, "").replace(/\/$/, "");
  const cueText = s => "\u201c" + esc(s).replace(/\n/g, "\\n") + "\u201d";
  const facts = list => `<ul class="facts">${list.map(x => `<li>${x}</li>`).join("")}</ul>`;
  const open = x => `<span class="dp-open">${x}</span>`;

  // The quiet line: where and when the panel's numbers were measured, read from each key's src and at.
  function where(F, keys) {
    const parts = [], seen = new Set(), ids = new Set(), times = [];
    const add = s => { if (s && !seen.has(s)) { seen.add(s); parts.push(esc(s)); } };
    keys.forEach(k => {
      const f = F[k];
      if (!f) return;
      if (f.at) times.push(String(f.at).slice(0, 16));
      if (/team\.Store/.test(f.src || "")) return add("the team event log");
      String(f.src || "").split(/;\s*(?![^()]*\))/).forEach(p => {
        p = p.trim().replace(/^[a-z_]+:\s+/, "");
        if (!p || /^live\b/.test(p)) return;
        (p.match(ID) || []).forEach(i => ids.add(i));
        if (/^board\b/.test(p) || /^derived/.test(p)) return;
        const file = p.match(/^((?:studies|tools|meta|infra)\/[^\s,:()]+|AGENTS\.md|README\.md)/);
        if (file) return add(file[1]);
        if (/event log/.test(p)) return add("the team event log");
        if (/transcript/.test(p) && !/\b[0-9a-f]{8}\b/.test(p)) return add("the agents' session transcripts in the team store");
        if (/^(uv run|python3|git|grep) /.test(p)) return add(p.replace(/\s*[(|].*$/, ""));
        add(p.replace(/\s*\(.*$/, "").replace(/:\s.*$/, "").replace(/^counted from /, ""));
      });
    });
    times.sort();
    const lo = times[0], hi = times[times.length - 1];
    const t = !times.length ? "" : lo === hi ? when(lo) : lo.slice(0, 10) === hi.slice(0, 10) ? when(lo).replace(" UTC", "") + " to " + hi.slice(11, 16) + " UTC" : `${when(lo)} to ${when(hi)}`;
    const list = parts.concat([...ids].map(board));
    return `<p class="dp-src">Measured ${t}. From ${list.join(", ")}.</p>`;
  }

  // Link rows in the Design page's .rows style; the bar at the left is the person's colour, or --mute.
  const bar = who => { const h = who ? hueOf(who) : null; return h == null ? ` style="--c:var(--mute)"` : ` class="hue" style="--h:${h}"`; };
  const row = (href, text, meta, who, out, cls) => {
    const tgt = out ? ` target="_blank" rel="noopener"` : "";
    const c = bar(who);
    const klass = cls ? (c.startsWith(" class=") ? c.replace('class="hue"', `class="hue ${cls}"`) : ` class="${cls}"` + c) : c;
    return `<a${klass} href="${esc(href)}"${tgt}><span class="t">${text}</span><span class="m">${meta}</span></a>`;
  };
  const item = (m, id) => (m && m.live ? m.live.find(i => i.id === id) : null);
  const boardRow = (m, id, fallback) => {
    const it = item(m, id);
    return it ? row("/#" + id, esc(it.text), `<b>${esc(it.who)}</b> ${id}, ${ago(it.at_ns)}`, it.who)
              : row("/#" + id, fallback ? esc(fallback) : id, fallback ? `Board item ${id}` : "Opens on the board", null);
  };
  const rows = (title, list) => list.length ? `<div class="rows"><h3>${esc(title)}</h3>${list.join("")}</div>` : "";

  const recall = () => (typeof FACTS !== "undefined" && FACTS.past_cross_agent_recall ? FACTS.past_cross_agent_recall.v : {});
  const first = s => String(s || "").split(",")[0].trim();

  return {
    "problem/day1": {
      name: "Our first hours, measured", lit: null,
      html: (F, m) => {
        const c = F.day1_cell_minutes, w = F.day1_wait_for_person_minutes;
        return `<p class="lead">Before the speed rules existed, our own agents lost time in ways we could count.</p>` + facts([
          `One cell of ${n(c.n)} hard problems took ${n(c.v)} minutes on one H100.`,
          `Agents generated that same cell ${n(V(F, "day1_cell_repeats"))} times. This count is approximate: it was read from the command log and the board.`,
          `Agents waited for a person during ${n(w.v)} of ${n(w.n)} session minutes.`,
          `Agents checked on their GPU jobs ${n(V(F, "day1_polls"))} times with \u201cgpu.py ls\u201d or \u201cgpu.py logs\u201d.`,
        ]) + where(F, ["day1_cell_minutes", "day1_cell_repeats", "day1_wait_for_person_minutes", "day1_polls"]) +
          rows("On the board", [boardRow(m, "result-17a66c", "The Day-1 turnaround report")]);
      },
    },

    "proof/turnaround": {
      name: "From claim to result", lit: ["board"],
      html: (F, m) => {
        const med = F.claim_to_close_median_min, s = V(F, "stage_median_min"), pp = V(F, "per_person") || {};
        return `<p class="lead">The median work item took ${n(med.v)} minutes from its claim to its result, over ${n(med.n)} closed items.</p>` + facts([
          `A quarter of the items took longer than ${n(V(F, "claim_to_close_upper_quartile_min"))} minutes.`,
          `By stage, the medians are ${n(s.to_job)} minutes to the first GPU job, ${n(s.jobs)} minutes of GPU jobs and ${n(s.to_answer)} minutes from the last job to the answer, over the items that had GPU jobs.`,
          `The team store holds ${n(V(F, "gpu_job_records"))} GPU job records and ${n(V(F, "tool_commands_logged"))} logged commands of board.py, gpu.py and paper.py.`,
          open(`A comparison with one agent on the same budget is not measured yet, and no file records the total spend.`),
        ]) + where(F, ["claim_to_close_median_min", "claim_to_close_upper_quartile_min", "stage_median_min", "gpu_job_records", "tool_commands_logged", "per_person"]) +
          rows("People", Object.keys(pp).sort().map(p => row(`/?who=${encodeURIComponent(p)}`,
            `${fmt(pp[p].results)} results, ${fmt(pp[p].agent_sessions)} main agent sessions, ${fmt(pp[p].gpu_jobs)} GPU jobs`, `<b>${esc(p)}</b>`, p)));
      },
    },

    "result/cue": {
      name: "The cue", lit: null,
      html: (F, m) => {
        const cue = F.cue_text, b = V(F, "math500_base_plain"), c = V(F, "math500_base_cue"), r = V(F, "math500_rl"), N = F.math500_rl.n;
        const rd = V(F, "math500_base_cue_redraws"), t6 = V(F, "math500_base_plain_t06"), tok = V(F, "math500_mean_tokens");
        const lit = V(F, "cue_paper_literal_rule"), paper = V(F, "cue_paper"), h = F.hard328_rl.n;
        return `<p class="lead">The cue is ${n(cue.n)} tokens, <span class="dp-cue">${cueText(cue.v)}</span>, placed at the start of the model's answer.</p>` + facts([
          `All three bars share the prompt, the sampling (T 1.0, top-p 1.0), one sample per problem and grader v3. They come from our earlier study; re-measured during the event, the cued base scored ${n(rd.lo)} to ${n(rd.hi)} of ${n(N)}.`,
          `The cue was chosen on these ${n(N)} problems. On ${n(h)} held-out harder problems, scored once: ${n(V(F, "hard328_base_plain"))} plain, ${n(V(F, "hard328_base_cue"))} with the cue, ${n(V(F, "hard328_rl"))} for RL.`,
          `Against the plain base at T 0.6 (${n(t6)}), the cue adds ${n(pt(c - t6, N))} of ${n(pt(r - t6, N))} points, and it uses fewer tokens than RL: ${n(tok.base_cue)} against ${n(tok.rl)} per problem.`,
          `<span class="dp-in">Wang et al. published the cue (${ext(paper.url, esc(paper.cite.replace(/^.*?,\s*/, "")))}). Under their literal answer rule ours scores ${n(lit.lo)} to ${n(lit.hi)}, below their ${n(lit.theirs_pct)}%, so our higher number is a grader effect. New here: one procedure for both models on the Olmo 3.1 pair (RL leads by ${pts(V(F, "math500_gap_points"))} points ${ci(V(F, "math500_gap_ci95"))}), the split of the gap with a null control, and a dose test in weight space.</span>`,
        ]) + where(F, ["cue_text", "math500_base_plain", "math500_base_cue", "math500_rl", "math500_base_cue_redraws", "hard328_base_plain", "hard328_base_cue", "hard328_rl",
                       "math500_base_plain_t06", "math500_mean_tokens", "cue_paper_literal_rule", "math500_gap_points"]) +
          rows("Sources", [boardRow(m, "result-60d899", "Our lead over Wang et al. is a grader effect"), row(paper.url, esc(paper.title), esc(paper.cite), null, true)]);
      },
    },

    "result/harder": {
      name: "Harder problems and code", lit: null,
      html: (F, m) => {
        const hb = V(F, "hard328_base_plain"), hc = V(F, "hard328_base_cue"), hr = V(F, "hard328_rl"), H = F.hard328_rl.n;
        const cb = V(F, "code_base_plain"), cm = V(F, "code_base_math_cue"), cc = V(F, "code_base_code_cue"), cr = V(F, "code_rl"), C = F.code_rl.n;
        const other = V(F, "shard_detail");
        return `<p class="lead">The cue closes ${n(pct(hc - hb, hr - hb))}% of the gap on ${n(H)} harder problems and ${n(pct(cm - cb, cr - cb))}% on ${n(C)} code problems.</p>` + facts([
          `The ${n(H)} harder problems are absent from the RL training prompts and were scored once: ${n(hb)} plain, ${n(hc)} with the cue and ${n(hr)} for RL. Two other runs of the cue cell gave ${n(other.right_whole_h200)} and ${n(other.right_shard4)}, so one run moves by several problems.`,
          `On ${n(C)} code problems (HumanEval+ and MBPP+) the base passes ${n(cb)} plain, ${n(cm)} with the same Math cue and ${n(cc)} with a longer Code cue; the Code RL model passes ${n(cr)}. A vote was not run on code.`,
          open(`Only one model pair is measured, Olmo 3 7B and its RL versions, so whether the cue works on a second model family is open.`),
        ]) + where(F, ["hard328_base_plain", "hard328_base_cue", "hard328_rl", "shard_detail", "code_base_plain", "code_base_math_cue", "code_base_code_cue", "code_rl"]) +
          rows("On the board", [boardRow(m, "result-099916", "The plain base on the 328"), boardRow(m, "result-82b4dc", "Base with the cue and RL on the 328"), boardRow(m, "result-59ed1a", "The code pair")]);
      },
    },

    "result/vote": {
      name: "Under a vote", lit: null,
      html: (F, m) => {
        const vb = V(F, "vote4_restart_base"), vr = V(F, "vote4_restart_rl"), N = F.vote4_restart_rl.n, a = V(F, "chart_audit");
        return `<p class="lead">With a vote over 4 samples, after restarting answers that hit the length cap, the base with the cue reaches ${n(vb)} of ${n(N)} and RL ${n(vr)}.</p>` + facts([
          `Both models get the same procedure and about the same budget: ${n(V(F, "vote4_restart_base_tokens_per_problem"))} and ${n(V(F, "vote4_restart_rl_tokens_per_problem"))} tokens per problem.`,
          `RL stays ${n(pt(vr - vb, N))} points ahead, so the vote does not close the gap.`,
          `The chart on the board shows ${n(a.chart_best_base)} for the base. Our own audit reads it as ${n(a.audited_best_base)}, because the tie rule behind ${n(a.chart_best_base)} was chosen after reading the problems it fixes.`,
        ]) + where(F, ["vote4_restart_base", "vote4_restart_rl", "vote4_restart_base_tokens_per_problem", "chart_audit"]) +
          rows("On the board", [boardRow(m, "result-5d032f", "Vote over 4 after restart, both models"), boardRow(m, "result-e78dfe", "Audit of the MATH-500 chart")]);
      },
    },

    "why/control": {
      name: "How we know", lit: null,
      html: (F, m) => {
        const rs = V(F, "anatomy_right_samples"), S = F.anatomy_right_samples.n, P = F.reliability_share_pct.n, k = S / P;
        const yue = V(F, "reliability_closest_paper"), pages = V(F, "finding_pages") || [], rel = pages.find(p => p.slug === "rl-reliability") || {};
        return `<p class="lead">Each of the ${n(P)} problems was sampled ${n(k)} times with each model: ${n(rs.base_cue)} and ${n(rs.rl)} right of ${n(S)}.</p>` + facts([
          `${n(V(F, "reliability_share_pct"))}% of the ${n(V(F, "reliability_gap_samples"))} extra right answers of RL are on problems the base solves at least once in ${n(k)}; ${n(V(F, "new_problems_share_pct"))}% ${ci(V(F, "new_problems_share_ci95"))} are on problems it never solves.`,
          `Equal difficulty would predict ${n(V(F, "binomial_null_expected_problems"))} problems missed in all ${n(k)} samples; we observe ${n(V(F, "binomial_null_observed_problems"))}. Scored on a held-out sample, the never-solved share is ${n(V(F, "reliability_held_out_share_pct"))}% ${ci(V(F, "reliability_held_out_ci95"))}.`,
          `<span class="dp-in">The closest published result is ${ext(yue.url, esc(yue.cite))}. Within ${n(k)} samples the cued base solves ${n(V(F, "base_cue_any_of_4_problems"))} problems, against ${n(V(F, "math500_rl"))} for one RL sample, so much of the split is the known gap between several samples and one.</span>`,
          `New here: this split with its null control, and a dose test. A quarter of the RL weight difference gives ${pts(V(F, "wdiff_quarter_points"))} points ${ci(V(F, "wdiff_quarter_ci95"))}, a random one of the same norm ${pts(V(F, "wdiff_random_control_points"))} ${ci(V(F, "wdiff_random_control_ci95"))}; after rounding, that blend sits ${n(V(F, "wdiff_quarter_norm_ratio"))} of the way to RL.`,
        ]) + where(F, ["anatomy_right_samples", "reliability_share_pct", "new_problems_share_pct", "binomial_null_expected_problems", "reliability_held_out_share_pct",
                       "base_cue_any_of_4_problems", "reliability_closest_paper", "wdiff_quarter_points", "wdiff_quarter_norm_ratio"]) +
          rows("Read more", [row("/finding/rl-reliability", esc(rel.title || "Reliability"), "Finding page", null), boardRow(m, "result-afc423", "The anatomy of the gap")]);
      },
    },

    "why/findings": {
      name: "Other findings", lit: null,
      html: (F, m) => {
        const pages = V(F, "finding_pages") || [], pg = s => pages.find(p => p.slug === s) || { title: s, line: "" };
        const w = pg("rl-wait-habit"), e = pg("eight-directions"), N = F.math500_base_cue.n;
        return `<p class="lead">Two more findings have their own pages, and each has an open caveat.</p>` + facts([
          `${esc(w.title)}: \u201c${esc(w.line)}\u201d That rate comes from a lens borrowed from another model, and lenses matched to each model give a different rate.`,
          `${esc(e.title)}: \u201c${esc(e.line)}\u201d That rise starts from the plain base. The cue alone already gives ${n(pct(V(F, "math500_base_cue"), N))}%, and against the cued base the gain is not yet significant.`,
          `A quarter of the RL weight difference, added to the base, gives ${pts(V(F, "wdiff_quarter_points"))} points ${ci(V(F, "wdiff_quarter_ci95"))} over the base with the cue; a random difference of the same norm gives ${pts(V(F, "wdiff_random_control_points"))} ${ci(V(F, "wdiff_random_control_ci95"))}. After rounding, that blend sits ${n(V(F, "wdiff_quarter_norm_ratio"))} of the way to RL.`,
        ]) + where(F, ["finding_pages", "math500_base_cue", "wdiff_quarter_points", "wdiff_random_control_points", "wdiff_quarter_norm_ratio"]) +
          rows("On the board", [boardRow(m, "result-4b0d5f", "Blends of the RL weight difference")]);
      },
    },

    "rules/thread": {
      name: "The thread", lit: null,
      html: (F, m) => {
        const a = V(F, "retraction_claim"), b = V(F, "retraction_correction"), who = V(F, "retraction_who"), th = V(F, "retraction_thread") || [];
        const cut = s => esc(s) + (/[.)]$/.test(String(s).trim()) ? "" : "\u2026");
        return `<p class="lead">The agent that posted ${pts(a.points)} points ran a second draw and retracted the result ${n(V(F, "retraction_minutes_between"))} minutes later.</p>` + facts([
          `First draw: with 3 answers written by the RL model placed in the base model's context, ${n(a.right)} of ${n(a.n)} right, ${pts(a.points)} points ${ci(a.ci95)}. It was one draw of 3 examples.`,
          `Second draw of 3 other examples: ${n(b.right)} of ${n(b.n)} right, ${pts(b.points)} points ${ci(b.ci95)}.`,
          `The score row of the first post, ${n(a.right)} of ${n(a.n)}, is still stored in the chart data.`,
        ]) + where(F, ["retraction_claim", "retraction_correction", "retraction_thread", "retraction_minutes_between"]) +
          rows("Comments on " + a.id, th.map(c => row("/#" + a.id, cut(c.text), `Comment, ${when(c.at)}`, null, false, "dp-long")));
      },
    },

    "rules/audit": {
      name: "The audit of our chart", lit: ["board"],
      html: (F, m) => {
        const a = V(F, "chart_audit");
        return `<p class="lead">A second agent audited our own hill-climbing chart for leaks of the answer key.</p>` + facts([
          `It read the code of the prompt, the cue, the restart, the vote and the tie-break, and found no leak.`,
          `The grader rejected ${n(a.planted_wrong_rejected)} of ${n(a.planted_wrong)} planted wrong answers, and a regrade of ${n(a.rows_regraded)} rows gave ${n(a.regrade_mismatches)} mismatches.`,
          `It read the best base score down from ${n(a.chart_best_base)} to ${n(a.audited_best_base)} of ${n(a.n)}. Some cells could not be recounted, because their raw answers are not in git.`,
          `The auditor is a model of the same family as the agents, and no person hand-checked a counted sample.`,
        ]) + where(F, ["chart_audit"]) + rows("On the board", [boardRow(m, a.id, "Audit of the MATH-500 chart")]);
      },
    },

    "rules/rejected": {
      name: "What the swarm rejected", lit: ["board"],
      html: (F, m) => {
        const r = F.refuted_or_negative_results, ids = V(F, "refuted_or_negative_result_ids"), rules = V(F, "agents_md_rules") || [];
        return `<p class="lead">Every hypothesis is posted with the observation that would refute it, and a refuted prediction is posted as a result.</p>` + facts([
          `Of the ${n(r.n)} results at ${when(r.at)}, ${n(ids.says_refuted.length)} report a refuted prediction and ${n(ids.negative_headline.length)} report a negative result. The count is approximate (a text match, read by hand), and a refuted result has at least one failed prediction while the rest of it may stand.`,
          `The rules in AGENTS.md say: \u201c${esc(rules[0])}\u201d and \u201c${esc(rules[2])}\u201d`,
        ]) + where(F, ["refuted_or_negative_results", "agents_md_rules"]) +
          rows("Negative results", ids.negative_headline.map(id => boardRow(m, id)));
      },
    },

    "infra/modal": {
      name: "On Modal", lit: ["board", "actor", "ext-modal"],
      html: (F, m) => {
        const pk = V(F, "gpu_peak_containers"), e = V(F, "gpu_jobs_ended"), sh = V(F, "shard_detail"), W = V(F, "shard_whole_minutes"), Q = V(F, "shard_4_minutes");
        return `<p class="lead">Agents start their own GPU jobs with one command, and a job runs only from a pushed commit, so the code behind every result can be found later.</p>` + facts([
          `${n(V(F, "gpu_submit_commands"))} launches came from agent sessions. None carries the label that tools/events.py gives a command typed in a plain shell.`,
          `Of ${n(V(F, "gpu_job_records"))} job records, ${n(V(F, "gpu_jobs_started"))} started, after a median wait of ${n(V(F, "submit_to_start_median_s"))} seconds; a quarter waited over ${n(V(F, "submit_to_start_upper_quartile_min"))} minutes. At the peak ${n(pk.all)} GPU containers ran at once, ${n(pk.per_workspace)} per workspace.`,
          `Ended jobs used ${n(V(F, "gpu_hours"))} GPU-hours over ${n(F.gpu_hours.n)} GPU jobs. Of ${n(e.ended)} ended jobs, ${n(e.exit_nonzero)} exited with an error, and ${n(e.cancelled)} were cancelled.`,
          `Splitting one cell of ${n(F.shard_4_minutes.n)} problems over ${n(sh.shards)} H100s cut it from ${n(W)} to ${n(Q)} minutes and used ${n(sh.gpu_min_shard4)} GPU minutes against ${n(sh.gpu_min_whole)} (${n(pct(sh.gpu_min_shard4 - sh.gpu_min_whole, sh.gpu_min_whole))}% more). Measured once each way: ${n(sh.right_whole)} against ${n(sh.right_shard4)} right, about the spread of two whole runs (${n(sh.right_whole)} and ${n(sh.right_whole_h200)}).`,
        ]) + where(F, ["gpu_submit_commands", "gpu_submit_by_person_shell", "gpu_job_records", "submit_to_start_median_s", "gpu_peak_containers", "gpu_hours", "gpu_jobs_ended", "shard_detail", "pushed_commit_rule"]) +
          rows("On the board", [boardRow(m, "result-dfe78e", "Replay of one cell: whole and in 4 shards")]);
      },
    },

    "brain/sources": {
      name: "Sources", lit: ["board", "actor", "ext-exa"],
      html: (F, m) => {
        const A = V(F, "exa_case_best"), B = V(F, "exa_case_lens"), C = V(F, "exa_case_novelty"), calls = F.exa_successful_calls;
        const kase = (c, url, did) => `<div class="dp-case"><span class="dp-q">\u201c${esc(c.query)}\u201d</span>` +
          `<a class="dp-url" href="${esc(url)}" target="_blank" rel="noopener">${esc(bare(url))}</a>` +
          `<p class="dp-did">${did}</p><span class="dp-meta"><span${bar(c.who)}><span class="dp-who">${esc(c.who)}</span></span>'s agent searched, ${when(c.searched_utc)}</span></div>`;
        const groups = {};
        (typeof SOURCES !== "undefined" ? SOURCES : []).forEach(s => {
          const host = bare(s.url).split("/")[0].replace(/^www\./, "");
          (groups[host] = groups[host] || []).push(s);
        });
        const order = Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length || a.localeCompare(b));
        const list = order.map(h => `<div class="rows dp-group"><h3>${esc(h)}, ${fmt(groups[h].length)}</h3>` + groups[h].map(s =>
          row(s.url, (s.cited ? `<span class="dp-dot" aria-hidden="true"></span>` : "") + esc(bare(s.url)),
              `<b>${esc(s.who)}</b> ${esc(s.at)} UTC${s.cited ? ", cited in " + esc(s.cited) : ""}`, s.who, true)).join("") + `</div>`).join("");
        return `<p class="lead">Agents read ${n(V(F, "exa_urls_fetched"))} pages through Exa before spending GPU time. Three of them changed what an agent did.</p>` +
          kase(A, A.paper_url, `Its tables and those of other papers closed ${n(A.method_families)} method families with no GPU job: ${board(A.board_item)} listed them as published ${n(A.minutes_search_to_post)} minutes after the search.`) +
          kase(B, B.source_url, `A published lens for our exact base model was loaded rather than fitted (${board(B.board_item)}). A full fit of the base still ran later.`) +
          kase(C, C.source_url, `It is the closest published result named on the Eight directions finding page (${board(C.also)}).`) +
          facts([
            `${n(calls.v)} of ${n(calls.n)} HTTP calls to Exa returned results, made by ${n(V(F, "exa_agents"))} main agents and subagents. They were counted from the session transcripts; the Exa dashboards hold the authoritative count.`,
            `${n(V(F, "exa_mcp_failed_calls"))} calls through the Exa MCP failed with a 401 error, so the agents call the HTTP API through tools/exa.py. Early on one person's agents had no Exa key and used another search tool.`,
          ]) + where(F, ["exa_urls_fetched", "exa_case_best", "exa_case_lens", "exa_case_novelty", "exa_successful_calls", "exa_agents", "exa_mcp_failed_calls"]) + list;
      },
    },

    "brain/memory": {
      name: "Shared memory", lit: ["board", "p:" + first(recall().writer), "p:" + first(recall().reader)],
      fx: "recall", writer: first(recall().writer), reader: first(recall().reader),
      html: (F, m) => {
        const r = V(F, "past_cross_agent_recall"), reader = first(r.reader), writer = first(r.writer);
        const id = (String(r.returned).match(ID) || [""])[0];
        const pl = V(F, "past_pilot"), pd = V(F, "past_pilot_detail");
        const used = String(r.used || "");
        return `<p class="lead">Every result and every finding from a paper goes into one memory on past.dev, and an agent asks it before it starts an idea.</p>` +
          `<div class="rows"><h3>One read across people</h3>` +
          row("/#" + id, `\u201c${esc(r.query)}\u201d`, `<b>${esc(reader)}</b>'s agent asked, ${when(r.read_utc)}`, reader, false, "dp-two") +
          row("/#" + id, esc(String(r.returned).replace(/\s+/g, " ").trim()), `past.dev returned it, with its source`, null, false, "dp-long") +
          row("/#" + id, `${id}: ${esc(r.fact_text)}\u2026`, `written by <b>${esc(writer)}</b>'s agent, ${when(r.written_utc)}`, writer, false, "dp-two") + `</div>` +
          facts([
            `What the reader did next: ${esc(used.charAt(0).toLowerCase() + used.slice(1))}`,
            `${n(V(F, "past_recalls"))} recalls and ${n(V(F, "past_stored_sources"))} stored sources so far. Whether a recall returns a correction ahead of the result it retracts is not checked yet.`,
            `Agents recall on demand with tools/recall.py, never automatically: ${n(V(F, "past_recall_p50_ms"))} ms at the median on past.dev's side, at most ${n(V(F, "recall_max_tokens"))} tokens, ${n(V(F, "past_memory_cost_usd"))} USD of credits in all.`,
            `A pilot of ${n(pl.questions)} templated questions, one run, retrieval only: recall had the answer inside ${n(V(F, "recall_max_tokens"))} tokens for ${n(pl.recall_hits_in_2000_tokens)}, one naive grep over ${n(pd.corpus_files)} transcripts for ${n(pl.grep_hits_in_2000_tokens)} (${n(pd.grep_hit_any)} anywhere in its output). Median ${n(pl.recall_median_s)} s against ${n(pl.grep_median_s)} s.`,
          ]) + where(F, ["past_cross_agent_recall", "past_recalls", "past_recall_p50_ms", "recall_max_tokens", "past_pilot"]);
      },
    },

    "retro/changes": {
      name: "What the reviews changed", lit: null,
      html: (F, m) => {
        const ch = V(F, "meta_changes") || [], mc = V(F, "max_containers_change"), r = ch[1] || {}, ps = V(F, "planted_waste_skill"), pp = V(F, "planted_waste_plain");
        return `<p class="lead">After each closed result an agent reviews the team's logs for waste and records what to change; ${n(V(F, "meta_review_entries"))} reviews are written down in meta/.</p>` + facts([
          `A review raised the H100 container limit from ${n(mc.from)} to ${n(mc.to)}, and the median H100 wait went from ${n(V(F, "h100_wait_before_min"))} minutes (${n(F.h100_wait_before_min.n)} jobs) to ${n(V(F, "h100_wait_after_s"))} seconds (${n(F.h100_wait_after_s.n)} jobs). The hours differ in load, and no control was run.`,
          `${esc(r.change)}. Before: ${esc(r.before)}. After: ${esc(r.after)}. This covers one class of failure.`,
          `On planted waste, three review rounds cut compute per batch from ${n(ps.before_min)} to ${n(ps.after_min)} container minutes, against ${n(pp.before_min)} to ${n(pp.after_min)} for a plain instruction. ${esc(V(F, "planted_waste_caveat"))}`,
          open(`Each change has one reading before and one after, and whether the changes help the lab overall has not been measured yet.`),
        ]) + where(F, ["max_containers_change", "h100_wait_before_min", "h100_wait_after_s", "meta_changes", "planted_waste_skill", "planted_waste_caveat", "meta_review_entries"]) +
          rows("On the board", [boardRow(m, "result-8b2682", "The planted-waste test")]);
      },
    },
  };
})();
"""
