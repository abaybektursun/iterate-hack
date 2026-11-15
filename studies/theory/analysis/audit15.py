"""Audit 15: recompute four round-15 numbers from stored rows, written without reading the tests' scripts.

Run from the repository root: uv run --no-project --with numpy --with math-verify==0.9.0 python studies/theory/analysis/audit15.py
Raw texts (not in git) are read from RAW below for the seed-sharing checks.
"""
import hashlib, json, re, sys
from collections import Counter, defaultdict
import numpy as np
from math_verify import parse, verify

RES = 'studies/rlneurons/results/'
RAW = sys.argv[1] if len(sys.argv) > 1 else '/Users/abaybektursun/projects/iterate-hack/runs/'
SHOTS = '/Users/abaybektursun/projects/iterate-hack-shots/runs/cap32_base_cue_joined/answers.jsonl'
OUT = 'studies/theory/results/direct/audit15-01/'
rng = np.random.default_rng(15)
out = {}


def jl(p):
    return [json.loads(l) for l in open(p)]


def grid(rows):  # attempt-0 rows -> {problem: [row of sample 0..3]}
    g = defaultdict(dict)
    for r in rows:
        if r.get('attempt', 0) == 0 and r['sample'] < 4:
            assert r['sample'] not in g[r['problem_index']]
            g[r['problem_index']][r['sample']] = r
    return {p: [d[s] for s in range(4)] for p, d in g.items() if len(d) == 4}


def boot(f, n, B=10000):
    idx = rng.integers(0, n, (B, n))
    v = np.array([f(i) for i in idx])
    return [round(float(np.percentile(v, 5)), 4), round(float(np.percentile(v, 95)), 4)]


def norm(a):
    a = a.replace('\\left', '').replace('\\right', '').replace('\\dfrac', '\\frac').replace('\\tfrac', '\\frac')
    a = re.sub(r'\\text\{\s*([^}]*)\}', r'\1', a)
    a = re.sub(r'\\[,;!: ]|\s|\$|\^\{?\\circ\}?', '', a)
    return a.rstrip('.')


_mv = {}
def same(a, b, mode):
    if mode == 'string':
        return norm(a) == norm(b)
    k = (a, b)
    if k not in _mv:
        _mv[k] = norm(a) == norm(b) or bool(verify(parse('$' + a + '$'), parse('$' + b + '$')))
    return _mv[k]


def keys(samples, abstain_cap, merge, mode):
    """One key per sample: 'R' right, None abstains, else an id of its wrong-answer group."""
    ks, reps = [], []
    for r in samples:
        if not r['extracted_v3'] or (abstain_cap and r['cap_hit']):
            ks.append(None)
        elif r['score_v3'] == 1:
            ks.append('R')
        elif merge:
            ks.append('W')
        else:
            j = next((i for i, a in enumerate(reps) if same(a, r['extracted_v3'], mode)), None)
            if j is None:
                reps.append(r['extracted_v3']); j = len(reps) - 1
            ks.append(j)
    return ks


def vote(ks):  # plurality, uniform tie break = mean over all 24 orders of 'first seen wins'
    c = Counter(k for k in ks if k is not None)
    if not c:
        return 0.0
    m = max(c.values()); top = [k for k, v in c.items() if v == m]
    return 1 / len(top) if 'R' in top else 0.0


def wrong_pair_agree(g, mode):
    a = t = 0
    for s in g.values():
        w = [r['extracted_v3'] for r in s if r['extracted_v3'] and r['score_v3'] == 0 and not r['cap_hit']]
        for i in range(len(w)):
            for j in range(i + 1, len(w)):
                t += 1; a += same(w[i], w[j], mode)
    return round(a / t, 3), t


# ---------- 1. merge328 ----------
base = jl(RES + 'day1_3/hard328_base_cue_s4r2-01/rows.jsonl')
gb = grid(base)
assert len(gb) == 328
kept = [p for p, s in gb.items() if any(r['score_v3'] == 1 for r in s)
        and any(r['score_v3'] == 0 and r['extracted_v3'] and not r['cap_hit'] for r in s)]
m1 = {'n': len(kept)}
for mode in ('string', 'mathverify'):
    d = np.array([vote(keys(gb[p], True, False, mode)) - vote(keys(gb[p], True, True, mode)) for p in kept])
    m1[mode] = {'D': round(d.mean(), 4), 'ci90': boot(lambda i: d[i].mean(), len(d)),
                'D_gt0': int((d > 0).sum()), 'D_eq0': int((d == 0).sum()), 'D_lt0': int((d < 0).sum())}
    # team abstention rule (cap hits with an answer vote) as a cap-choice check
    d2 = np.array([vote(keys(gb[p], False, False, mode)) - vote(keys(gb[p], False, True, mode)) for p in kept])
    m1[mode]['D_cap_hits_vote'] = round(d2.mean(), 4)
    m1[mode]['wrong_pair_agree_hard328'] = wrong_pair_agree(gb, mode)
    # all-pairs-of-wrong-answers-differ planted check: D can only rise
m1['planted_all_wrong_same_key_D'] = float(np.mean([vote(keys(gb[p], True, True, 'string')) - vote(keys(gb[p], True, True, 'string')) for p in kept]))
m1['team_vote_stored_order_check'] = None  # not reproduced: the order-averaged rule is the deciding one
ex = [p for p in kept if vote(keys(gb[p], True, False, 'mathverify')) != vote(keys(gb[p], True, True, 'mathverify'))]
same_ = [p for p in kept if p not in ex]
m1['example_changes'] = {'problem': ex[0], 'answers': [(r['extracted_v3'], r['score_v3'], r['cap_hit']) for r in gb[ex[0]]], 'gold': gb[ex[0]][0]['gold']}
m1['example_no_change'] = {'problem': same_[0], 'answers': [(r['extracted_v3'], r['score_v3'], r['cap_hit']) for r in gb[same_[0]]], 'gold': gb[same_[0]][0]['gold']}
out['merge328'] = m1

# ---------- 2. s100vote ----------
s0 = {r['problem_index']: dict(r, sample=0, attempt=0) for r in json.load(open(RES + 'ckptcue/s0100_plain-01/per_problem.json'))}
s123 = jl(RES + 'ckptcue/s0100_plain_s123-01/rows.jsonl')
g100 = grid(list(s0.values()) + s123)
assert len(g100) == 500
assert [sum(g100[p][s]['score_v3'] for p in g100) for s in range(4)] == [418, 411, 422, 419]
cells = {'s100': g100, 'base_cue': grid(jl(RES + 'day1_3/math500_base_cue-01/rows.jsonl')),
         'rl_final': grid(jl(RES + 'day1_3/math500_rl-01/rows.jsonl'))}
m2 = {}
per = {}
for name, g in cells.items():
    assert len(g) == 500, name
    ps = sorted(g)
    v = np.array([vote(keys(g[p], False, False, 'mathverify')) for p in ps])
    sg = np.array([np.mean([r['score_v3'] for r in g[p]]) for p in ps])
    k = np.array([sum(r['score_v3'] for r in g[p]) for p in ps])
    noans = np.array([sum(not r['extracted_v3'] for r in g[p]) for p in ps])
    gain = 100 * (v - sg)
    per[name] = (k, gain)
    m2[name] = {'vote': round(v.sum(), 2), 'single_mean': round(sg.sum(), 2), 'G_points': round(gain.mean(), 3),
                'ci90': boot(lambda i: gain[i].mean(), 500),
                'G_from_problems_with_no_finished_wrong': round(gain[[all(r['score_v3'] == 1 or not r['extracted_v3'] for r in g[p]) for p in ps]].sum() / 500, 3),
                'rows_no_answer': int(noans.sum()), 'wrong_pair_agree': wrong_pair_agree(g, 'mathverify'),
                'k_hist': np.bincount(k, minlength=5).tolist()}
# accuracy-matched null: final RL's mean gain at each right count k (0-4) applied to step 100's k distribution
for ref in ('rl_final', 'base_cue'):
    kr, gr = per[ref]
    gk = {kk: gr[kr == kk].mean() for kk in range(5)}
    k1, _ = per['s100']
    m2[f'null_G_s100_with_{ref}_gain_per_k'] = round(float(np.mean([gk[kk] for kk in k1])), 3)
    k1, _ = per['rl_final']
    m2[f'check_G_rl_with_{ref}_gain_per_k'] = round(float(np.mean([gk[kk] for kk in k1])), 3)
# step 100's gain minus the accuracy-matched null, resampling step-100 and final-RL problems independently
k1, g1 = per['s100']; kr, gr_ = per['rl_final']
def excess(i, j):
    gk = np.array([gr_[j][kr[j] == kk].mean() if (kr[j] == kk).any() else 0.0 for kk in range(5)])
    return g1[i].mean() - gk[k1[i]].mean()
ij = rng.integers(0, 500, (2000, 2, 500))
xs = np.array([excess(a, c) for a, c in ij])
m2['s100_G_minus_rl_k_matched_null'] = {'value': round(excess(np.arange(500), np.arange(500)), 3),
                                         'ci90': [round(float(np.percentile(xs, 5)), 3), round(float(np.percentile(xs, 95)), 3)]}
pv = [p for p in sorted(g100) if vote(keys(g100[p], False, False, 'mathverify')) == 1 and sum(r['score_v3'] for r in g100[p]) < 4]
pw = [p for p in sorted(g100) if vote(keys(g100[p], False, False, 'mathverify')) == 0 and sum(r['score_v3'] for r in g100[p]) > 0]
m2['example_vote_right'] = {'problem': pv[0], 'answers': [(r['extracted_v3'], r['score_v3']) for r in g100[pv[0]]]}
m2['example_vote_wrong'] = {'problem': pw[0], 'answers': [(r['extracted_v3'], r['score_v3']) for r in g100[pw[0]]]} if pw else None
out['s100vote'] = m2

# ---------- 3 and 4. edit vs RL on base-0-of-4 hard328 ----------
ge = grid(jl(RES + 'day1_3/hard328_top8x1.5_cue_s4-01/rows.jsonl'))
rl_rows = jl(RES + 'day1_3/hard328_rl_plain_s4r2-01/rows.jsonl')
gr = grid(rl_rows)
sel = sorted(p for p, s in gb.items() if sum(r['score_v3'] for r in s) == 0 and p in ge and p in gr)
assert sel == sorted(p for p, s in gb.items() if sum(r['score_v3'] for r in s) == 0)
e = np.array([np.mean([r['score_v3'] for r in ge[p]]) for p in sel])
r_ = np.array([np.mean([r['score_v3'] for r in gr[p]]) for p in sel])
n = len(sel)
m3 = {'n': n, 'E': round(e.mean(), 4), 'R': round(r_.mean(), 4), 'E_right': int(round(e.sum() * 4)), 'R_right': int(round(r_.sum() * 4)),
      'D': round((e - r_).mean(), 4), 'ci90': boot(lambda i: (e[i] - r_[i]).mean(), n),
      'cap_hits_of_4n': {nm: sum(r['cap_hit'] for p in sel for r in g[p]) for nm, g in (('base', gb), ('edit', ge), ('rl', gr))},
      'mean_n_new': {nm: round(float(np.mean([r['n_new'] for p in sel for r in g[p]])), 0) for nm, g in (('base', gb), ('edit', ge), ('rl', gr))}}

# fresh base samples: restarts (attempt>0) and the cap32 sample cut at 16,384 when its text is fresh
raw_base = {(a['problem_index'], a['sample'], a['attempt']): a['text'] for a in map(json.loads, open(RAW + 'abaybektursun-1114-200457-e8e6/answers.jsonl'))}
cap32 = {r['problem_index']: r for r in jl(RES + 'cap32/rows-02/base_cue.jsonl')}
c32txt = {a['problem_index']: a['text'] for a in map(json.loads, open(SHOTS))}
fresh, prefix_same = {}, []
for p in sel:
    t32, t0 = c32txt[p], raw_base[(p, 0, 0)]
    lp = len(t0) if t32.startswith(t0) else next(i for i, (x, y) in enumerate(zip(t32, t0)) if x != y)
    prefix_same.append(lp / max(len(t0), 1))
    hs = {hashlib.sha256(raw_base[(p, s, 0)].encode()).hexdigest() for s in range(4)}
    fresh[p] = hashlib.sha256(t32.encode()).hexdigest() not in hs
c32right = lambda p: int(cap32[p]['score_v3'] == 1 and cap32[p]['n_new'] <= 16384 and not cap32[p]['cap_hit'])
m3['cap32_text_shares_prefix_with_s4r2_sample0'] = {'median_share_of_sample0_chars': round(float(np.median(prefix_same)), 3),
                                                     'problems_prefix_ge_99pct': int(sum(x >= 0.99 for x in prefix_same)), 'n': n,
                                                     'not_fresh_by_sha': int(sum(not v for v in fresh.values()))}
rest = defaultdict(list)
for r in base:
    if r['attempt'] > 0 and r['problem_index'] in sel:
        rest[r['problem_index']].append(r['score_v3'])
bnull = {p: rest[p] + ([c32right(p)] if fresh[p] else []) for p in sel}
pn = [i for i, p in enumerate(sel) if bnull[p]]
b = np.array([np.mean(bnull[sel[i]]) for i in pn])
m3['null_D0'] = {'n': len(pn), 'value': round((b - r_[pn]).mean(), 4), 'ci90': boot(lambda i: (b[i] - r_[pn][i]).mean(), len(pn)),
                 'base_fresh_right': int(sum(sum(v) for v in bnull.values())), 'base_fresh_samples': int(sum(len(v) for v in bnull.values()))}
m3['D_on_same_problems_as_null'] = round((e[pn] - r_[pn]).mean(), 4)
m3['D_minus_null_E_minus_fresh_base'] = {'value': round((e[pn] - b).mean(), 4), 'ci90': boot(lambda i: (e[pn][i] - b[i]).mean(), len(pn))}

# seed coupling: edit and RL share seeds (3,000,000 + 10,000 s + index) with the cued base. Score agreement of sample s
# with the base's sample s (same seed) against the base's sample s+1 (other seed), over all 328 problems.
def coupling(g):
    ps = sorted(set(g) & set(gb))
    same_ = np.mean([g[p][s]['score_v3'] == gb[p][s]['score_v3'] for p in ps for s in range(4)])
    other = np.mean([g[p][s]['score_v3'] == gb[p][(s + 1) % 4]['score_v3'] for p in ps for s in range(4)])
    nn = np.mean([g[p][s]['n_new'] == gb[p][s]['n_new'] for p in ps for s in range(4)])
    return {'agree_same_seed': round(float(same_), 4), 'agree_other_seed': round(float(other), 4), 'n_new_identical_share': round(float(nn), 4)}
m3['seed_coupling_vs_base'] = {'edit': coupling(ge), 'rl': coupling(gr)}
raw_edit = {(a['problem_index'], a['sample']): a['text'] for a in map(json.loads, open(RAW + 'abaybektursun-1115-055641-b417/answers.jsonl'))}
raw_rl = {(a['problem_index'], a['sample']): a['text'] for a in map(json.loads, open(RAW + 'abaybektursun-1114-200505-5ff2/answers.jsonl')) if a['attempt'] == 0}
def lcp(a, b):
    return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
m3['median_common_prefix_chars_with_base_same_seed'] = {
    'edit': int(np.median([lcp(raw_edit[(p, s)], raw_base[(p, s, 0)]) for p in sel for s in range(4)])),
    'rl': int(np.median([lcp(raw_rl[(p, s)], raw_base[(p, s, 0)]) for p in sel for s in range(4)]))}
# grader check: the same selection and D with grader v2 (score_v2 in the raw answers)
v2 = lambda path, a0: {(a['problem_index'], a['sample']): a['score_v2'] for a in map(json.loads, open(RAW + path)) if a.get('attempt', 0) == 0 or not a0}
vb, ve, vr = (v2(pth, True) for pth in ('abaybektursun-1114-200457-e8e6/answers.jsonl', 'abaybektursun-1115-055641-b417/answers.jsonl', 'abaybektursun-1114-200505-5ff2/answers.jsonl'))
sel2 = [p for p in gb if sum(vb[(p, s)] for s in range(4)) == 0]
d2 = np.array([np.mean([ve[(p, s)] for s in range(4)]) - np.mean([vr[(p, s)] for s in range(4)]) for p in sel2])
m3['grader_v2'] = {'n': len(sel2), 'D': round(d2.mean(), 4), 'ci90': boot(lambda i: d2[i].mean(), len(d2))}
er = next((p, s) for p in sel for s in range(4) if ge[p][s]['score_v3'] == 1)
ew = next((p, s) for p in sel for s in range(4) if ge[p][s]['score_v3'] == 0 and ge[p][s]['extracted_v3'])
m3['example_edit_right'] = {'problem': er[0], 'sample': er[1], 'gold': ge[er[0]][0]['gold'], 'extracted': ge[er[0]][er[1]]['extracted_v3'], 'tail': raw_edit[er][-300:]}
m3['example_edit_wrong'] = {'problem': ew[0], 'sample': ew[1], 'gold': ge[ew[0]][0]['gold'], 'extracted': ge[ew[0]][ew[1]]['extracted_v3'], 'tail': raw_edit[ew][-300:]}
out['edit0of4'] = m3

# 4. d1: S = (E - B) / (R - B), B = fresh cap32 sample cut at 16,384
fi = [i for i, p in enumerate(sel) if fresh[p]]
bb = np.array([c32right(sel[i]) for i in fi]); ee, rr = e[fi], r_[fi]
S = lambda i: (ee[i].mean() - bb[i].mean()) / (rr[i].mean() - bb[i].mean())
bb32 = np.array([int(cap32[sel[i]]['score_v3'] == 1) for i in fi])
out['d1'] = {'n': len(fi), 'E': round(ee.mean(), 4), 'R': round(rr.mean(), 4), 'B': round(bb.mean(), 4), 'B_right': int(bb.sum()),
             'S': round(S(np.arange(len(fi))), 4), 'ci90': boot(S, len(fi)),
             'R_minus_B': round(rr.mean() - bb.mean(), 4), 'R_minus_B_ci90': boot(lambda i: rr[i].mean() - bb[i].mean(), len(fi)),
             'S_with_B_from_restarts_and_cap32': round((e[pn].mean() - b.mean()) / (r_[pn].mean() - b.mean()), 4),
             'S_cap32_full_32k': round((ee.mean() - bb32.mean()) / (rr.mean() - bb32.mean()), 4),
             'B_32k_right': int(bb32.sum())}

import os
os.makedirs(OUT, exist_ok=True)
json.dump(out, open(OUT + 'metrics.json', 'w'), indent=1, default=lambda x: x.item() if hasattr(x, 'item') else str(x))
print(json.dumps(out, indent=1, default=lambda x: x.item() if hasattr(x, 'item') else str(x)))
