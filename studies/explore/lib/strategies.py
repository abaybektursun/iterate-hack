"""Exploration strategies at a matched budget of submissions. Each one only decides, before every model call,
which chat history and which starting program the call gets (see lib/loop.py).

single    one agent, one growing chat for the whole budget (the anchoring baseline).
parallel  K independent agents, budget split evenly; best of all (best-of-K at matched budget).
fnf       Fork-and-Flush (2610.07447): at 0 %, 33 % and 66 % of the budget, K branches start from the best program
          so far with an empty chat, about 6 % of the budget each; the best branch becomes the leader, keeping its own
          chat, and continues alone until the next fork.
forget    Forgetting (2610.20563): K agents that see the team's best submissions (agent, score, idea) in every
          feedback; every quarter of the budget all chats are discarded and every agent restarts from the best
          program so far.
fnf_keep  Ablation of fnf: the same forks, but each branch keeps a copy of the leader's chat (the best program and
          its score are appended as a new message), so the fork happens without the flush.
basin     Ours: K agents with growing chats (as parallel). After every round an LLM judge (lib/basins.py) labels the
          new submissions by approach basin. An agent whose last `window` submissions all sit in one basin without a
          new team best is flushed: a fresh chat from the best program of another basin (the overall best if there is
          none), told which basins the team already tried and their best scores.
randflush Control for basin: the same agents, judge and flush message, but flushes happen at random (agent,
          round) slots, as many as `flushes` (set it to the count a basin run made).
rebase    Control for the flush: one growing chat as single, but every `period` submissions the feedback also
          shows the best program so far and asks to continue from it. Rollback without clearing the chat.
fnf_assign  Ours: fnf, but before each fork one call to `list_model` lists K different methods, given the task,
          the best program and the methods assigned before with their best scores. Each fresh branch is told to
          implement one of them. The list calls are extra to the budget; their cost is in metrics.json (list_usd).
single_list  Control for fnf_assign: one growing chat as single, no fork and no flush. At the fnf fork points (0, 33
          and 66 % of the budget) the same list call is made and its K methods are shown to the chat, which is
          asked to pick one. Separates the method list from the fork structure.
tree      Archive tree (DGM 2505.22954 parent rule): every step picks a parent from all valid submissions with weight
          sigmoid(10 * (rank score - 0.5)) / (1 + children), and starts a fresh chat from it.
basin     Ours: K agents with growing chats; every `check` submissions an online judge groups the recent ideas into
          basins. When an agent's last `window` submissions sit in one basin with no new best, that agent is flushed
          and restarted from the best program of a different basin, told which basins were already tried.
"""
import copy
import json
import math
import random
import re

from studies.explore.lib.basins import Labeler
from studies.explore.lib.loop import chat, cost, first_message


def fresh(run, code=None, score=None):
    """A new chat opening on `code` (default: the best program so far, starter included)."""
    if code is None:
        code, score, _ = run.base()
    return [{"role": "user", "content": first_message(run.task, code, score)}]


def single(run, **_):
    s = fresh(run)
    parent = "start"
    while run.left() > 0:
        parent = run.step(s, "a0", parent)["id"]


def rebase(run, period=None, **_):
    """period: submissions between rollbacks (default: a quarter of the budget, the forget arm's period)."""
    period = period or max(1, run.budget // 4)
    s = fresh(run)
    parent = "start"
    while run.left() > 0:
        parent = run.step(s, "a0", parent)["id"]
        if len(run.archive) % period == 0 and run.left() > 0:
            code, score, parent = run.base()
            s[-1]["content"] += (f"\n\nBEST PROGRAM SO FAR (validation score {score}):\n```python\n{code}\n```\n"
                                 "Continue from this program.")
            run.rebases.append({"after": len(run.archive), "from": parent})


LIST_PROMPT = """TASK:
{spec}

BEST PROGRAM SO FAR (validation score {score}):
```python
{code}
```

METHODS ALREADY ASSIGNED (best validation score reached under each):
{ledger}

List {k} METHODS for the next versions of this program. A method is the algorithmic approach (how the solution is
constructed or searched), not parameter values. The {k} methods must differ from each other in approach and from the
methods already assigned, unless one of those is clearly worth continuing. Each method: one sentence that a
programmer can implement. Reply with JSON only: ["<method 1>", ..., "<method {k}>"]"""


def list_methods(run, k, list_model, code, score, fork_no):
    done = {}
    for a in run.assignments:
        if a["branch"] is None:  # single_list: offered to one chat, so no score belongs to one method
            done[a["method"]] = "offered before"
            continue
        rows = [r["score"] for r in run.archive if r["branch"] == a["branch"] and r["valid"]]
        done[a["method"]] = f"best {max(rows)}" if rows else "no valid program"
    ledger = "\n".join(f"- {m} ({v})" for m, v in done.items()) or "(none yet)"
    msg = LIST_PROMPT.format(spec=run.task.spec, score=score, code=code, ledger=ledger, k=k)
    text, usage = chat([{"role": "user", "content": msg}], list_model)
    run.list_usd += cost(usage, list_model)
    methods = json.loads(re.search(r"\[.*\]", text, re.S).group(0))
    assert len(methods) == k and all(isinstance(m, str) for m in methods), f"bad method list: {text[:400]}"
    print(f"[fnf_assign fork {fork_no}] {list_model} methods: {methods}", flush=True)
    return methods


def single_list(run, k=4, forks=(0, 1 / 3, 2 / 3), list_model=None, **_):
    points = [round(f * run.budget) for f in forks]
    s, parent = None, "start"
    while run.left() > 0:
        if points and len(run.archive) >= points[0]:
            fork_no = len(forks) - len(points)
            points.pop(0)
            code, score, _ = run.base()
            methods = list_methods(run, k, list_model or run.model, code, score, fork_no)
            note = ("Methods to consider for your next versions (pick one):\n"
                    + "\n".join(f"{i + 1}. {m}" for i, m in enumerate(methods)) + "\n")
            if s is None:
                s = [{"role": "user", "content": first_message(run.task, code, score, note)}]
            else:
                s[-1]["content"] += "\n\n" + note
            run.assignments += [{"fork": fork_no, "branch": None, "method": m, "list_model": list_model or run.model}
                                for m in methods]
        parent = run.step(s, "a0", parent)["id"]


def parallel(run, k=4, **_):
    sessions = [fresh(run) for _ in range(k)]
    last = ["start"] * k
    while run.left() > 0:  # round robin, so a stopped run still has K comparable agents
        for i in range(k):
            if run.left() <= 0:
                break
            last[i] = run.step(sessions[i], f"a{i}", last[i])["id"]


def fnf(run, k=4, forks=(0, 1 / 3, 2 / 3), branch_steps=None, flush=True, assign=False, list_model=None, **_):
    """branch_steps: submissions per branch at each fork (default: 6% of the budget, as in the paper's 0.06B)."""
    branch_steps = branch_steps or max(1, round(0.06 * run.budget))
    leader, lead_last = None, None  # set by the opening fork at 0 %
    points = [round(f * run.budget) for f in forks]
    fork_no = 0
    while run.left() > 0:
        if fork_no < len(points) and len(run.archive) >= points[fork_no]:
            code, score, bid = run.base()
            branches = []
            methods = list_methods(run, k, list_model or run.model, code, score, fork_no) if assign else None
            for b in range(k):
                s = fresh(run, code, score)
                if assign:
                    s = [{"role": "user", "content": first_message(
                        run.task, code, score, f"Use this method for your next versions: {methods[b]}\n")}]
                    run.assignments.append({"fork": fork_no, "branch": f"f{fork_no}b{b}", "method": methods[b],
                                            "list_model": list_model or run.model})
                if not flush and leader is not None:  # fork without flush: the branch keeps the leader's history
                    s = copy.deepcopy(leader) + s
                last = bid
                for _ in range(branch_steps):
                    if run.left() <= 0:
                        break
                    last = run.step(s, "lead", last, branch=f"f{fork_no}b{b}")["id"]
                branches.append((run.best([r for r in run.archive if r["branch"] == f"f{fork_no}b{b}"]), s, last))
            ok = [x for x in branches if x[0]]
            if ok:
                _, leader, lead_last = max(ok, key=lambda x: x[0]["score"])
            elif leader is None:  # no valid branch at the opening fork: the leader starts from the best program
                leader, lead_last = fresh(run), bid
            fork_no += 1
            continue
        lead_last = run.step(leader, "lead", lead_last)["id"]


def forget(run, k=4, period=None, **_):
    """period: submissions between forgets (default: a quarter of the budget)."""
    period = period or max(k, run.budget // 4)
    run.peers = True
    epoch = 0
    while run.left() > 0:
        _, _, bid = run.base()
        sessions = [fresh(run) for _ in range(k)]
        last = [bid] * k
        start = len(run.archive)
        while run.left() > 0 and len(run.archive) - start < period:
            for i in range(k):
                if run.left() <= 0 or len(run.archive) - start >= period:
                    break
                last[i] = run.step(sessions[i], f"a{i}", last[i], branch=f"e{epoch}")["id"]
        epoch += 1


def fnf_keep(run, **kw):
    fnf(run, flush=False, **kw)


def fnf_assign(run, **kw):
    fnf(run, assign=True, **kw)


def _flush_note(run, lab, stuck=None):
    best = {}
    for r in run.archive:
        b = lab.label.get(r["id"])
        if b and r["valid"]:
            best[b] = max(best.get(b, float("-inf")), r["score"])
    tried = "; ".join(f"{b} (best {v})" for b, v in sorted(best.items(), key=lambda x: -x[1])) or "none valid yet"
    stuck_s = f"The approach '{stuck}' has stopped improving. " if stuck else ""
    return f"{stuck_s}Approaches the team already tried: {tried}. Consider a different approach.\n"


def _restart_from(run, lab, avoid):
    """(code, score, id) of the best valid program outside basin `avoid` that beats nothing in particular; the
    overall best (starter included) if every valid program is in `avoid`."""
    other = [r for r in run.archive if r["valid"] and lab.label.get(r["id"]) not in (None, avoid)]
    if other:
        b = max(other, key=lambda r: r["score"])
        return b["code"], b["score"], b["id"]
    return run.base()


def _flushing(run, k, window, trigger, **_):
    """Shared loop of basin and randflush. trigger(i, rnd, own) -> stuck basin name or None (no flush) or "" (flush
    with no basin named)."""
    lab = Labeler(run.task.spec.splitlines()[0])
    run.labeler = lab
    sessions, last = [fresh(run) for _ in range(k)], ["start"] * k
    own = [[] for _ in range(k)]  # each agent's submissions since its last flush
    epoch, rnd = [0] * k, 0
    while run.left() > 0:
        for i in range(k):
            if run.left() <= 0:
                break
            row = run.step(sessions[i], f"a{i}", last[i], branch=f"a{i}e{epoch[i]}")
            last[i] = row["id"]
            own[i].append(row)
        lab.add(run.archive)
        rnd += 1
        for i in range(k):
            stuck = trigger(i, rnd, own[i])
            if stuck is None:
                continue
            code, score, pid = _restart_from(run, lab, stuck)
            sessions[i] = [{"role": "user", "content": first_message(run.task, code, score, _flush_note(run, lab, stuck))}]
            last[i], own[i] = pid, []
            epoch[i] += 1
            run.flushes.append({"agent": f"a{i}", "round": rnd, "after": len(run.archive), "stuck": stuck,
                                "restart_from": pid})


def basin(run, k=4, window=4, **kw):
    def trigger(i, rnd, own):
        if len(own) < window:
            return None
        tail = own[-window:]
        labels = {run.labeler.label.get(r["id"]) for r in tail}
        team_best_before = max([run.task.starter_score] + [r["score"] for r in run.archive
                                                          if r["valid"] and r["step"] < tail[0]["step"]])
        new_best = any(r["valid"] and r["score"] > team_best_before for r in tail)
        return labels.pop() if len(labels) == 1 and not new_best else None
    _flushing(run, k, window, trigger, **kw)


def randflush(run, k=4, flushes=0, seed=0, **kw):
    rounds = run.budget // k
    rng = random.Random(1000 + seed)
    slots = set(rng.sample([(i, r) for r in range(1, rounds) for i in range(k)], flushes))

    def trigger(i, rnd, own):
        if (i, rnd) not in slots:
            return None
        labels = [run.labeler.label.get(r["id"]) for r in own[-4:]]
        return max(set(labels), key=labels.count) if labels else ""  # name the agent's recent basin, as basin does
    _flushing(run, k, 4, trigger, **kw)


def tree(run, seed=0, **_):
    rng = random.Random(seed)
    children = {}
    while run.left() > 0:
        ok = [r for r in run.archive if r["valid"]]
        if not ok:
            parent, base, score = "start", run.task.starter, run.task.starter_score
        else:
            order = sorted(ok, key=lambda r: r["score"])
            rank = {r["id"]: i / max(1, len(order) - 1) for i, r in enumerate(order)}
            w = [1 / (1 + math.exp(-10 * (rank[r["id"]] - 0.5))) / (1 + children.get(r["id"], 0)) for r in ok]
            p = rng.choices(ok, weights=w)[0]
            parent, base, score = p["id"], p["code"], p["score"]
            children[parent] = children.get(parent, 0) + 1
        run.step(fresh(run, base, score), "t", parent)


STRATEGIES = {"single_list": single_list, "rebase": rebase, "fnf_assign": fnf_assign, "single": single, "parallel": parallel, "fnf": fnf, "fnf_keep": fnf_keep, "forget": forget,
              "basin": basin, "randflush": randflush, "tree": tree}
