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
tree      Archive tree (DGM 2505.22954 parent rule): every step picks a parent from all valid submissions with weight
          sigmoid(10 * (rank score - 0.5)) / (1 + children), and starts a fresh chat from it.
basin     Ours: K agents with growing chats; every `check` submissions an online judge groups the recent ideas into
          basins. When an agent's last `window` submissions sit in one basin with no new best, that agent is flushed
          and restarted from the best program of a different basin, told which basins were already tried.
"""
import math
import random

from studies.explore.lib.loop import first_message


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


def parallel(run, k=4, **_):
    sessions = [fresh(run) for _ in range(k)]
    last = ["start"] * k
    while run.left() > 0:  # round robin, so a stopped run still has K comparable agents
        for i in range(k):
            if run.left() <= 0:
                break
            last[i] = run.step(sessions[i], f"a{i}", last[i])["id"]


def fnf(run, k=4, forks=(0, 1 / 3, 2 / 3), branch_steps=None, **_):
    """branch_steps: submissions per branch at each fork (default: 6% of the budget, as in the paper's 0.06B)."""
    branch_steps = branch_steps or max(1, round(0.06 * run.budget))
    leader, lead_last = None, None  # set by the opening fork at 0 %
    points = [round(f * run.budget) for f in forks]
    fork_no = 0
    while run.left() > 0:
        if fork_no < len(points) and len(run.archive) >= points[fork_no]:
            code, score, bid = run.base()
            branches = []
            for b in range(k):
                s = fresh(run, code, score)
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


STRATEGIES = {"single": single, "parallel": parallel, "fnf": fnf, "forget": forget, "tree": tree}
