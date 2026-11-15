"""RL from the base model on Tinker (LoRA), one training loop with the reward as its only switch.

    python -m studies.tinkerpair.jobs.rl --out rl/grader-01 --reward grader|vote|planted [--steps 40] [--groups 32]
        [--k 8] [--cap 4096] [--lr 4e-5] [--rank 32] [--save 5,10,20,30,40] [--seed 2000000]

One step: for `groups` training problems (data/train_v1.json, in file order), `k` samples each from the current
weights with the plain prompt at T 1.0 / top-p 1.0; reward per sample; advantage = reward minus the mean reward of its
problem; loss "importance_sampling"; one Adam step. Problems, order and sampling seeds do not depend on the reward, so
step 0 samples the same requests in every arm.

Rewards:
  grader   1 when grader v3 scores the answer right against the gold answer.
  vote     1 when the answer is in the largest group of agreeing answers among the k samples of its problem
           (rlneurons analysis/day1_vote.vote; an answer that cannot be extracted gets 0). The function receives
           the texts only. No gold answer enters the update.
  planted  1 when the first sampled token is --target-token. The loop's instrument check: with a short cap the
           share of that first token must rise.
Every arm logs both the grader accuracy and the vote agreement of its samples, whichever one it trains on.

Writes results/<out>/run.json, steps.jsonl (one line per step), checkpoints.json (step -> tinker path), examples.json
and runs/tinkerpair/<out>/rollouts_<step>.jsonl (texts of the saved steps, not committed).
"""
import argparse
import json
import time

import tinker
from tinker import types

from studies.rlneurons.analysis import day1_vote
from studies.rlneurons.lib import rln4_lib as R
from studies.tinkerpair.lib import tk


def reward_grader(texts: list, gold: str) -> list:
    return [float(R.grade_v3(gold, t)["score_v3"]) for t in texts]


def reward_vote(texts: list) -> list:
    rows = [{"extracted_v3": R.extract_v3(t)[1], "score_v3": 0} for t in texts]
    v = day1_vote.vote(rows)
    win = next((g for g in v["groups"] if g[0] == v["winner"]), [])
    return [float(i in win) for i in range(len(texts))]


def datum(prompt: list, s: dict, advantage: float) -> types.Datum:
    """The format of the Tinker cookbook's rl_loop: input = prompt + all sampled tokens but the last, targets shifted by one,
    sampling log-probabilities and advantages zero over the prompt."""
    ob = len(prompt) - 1
    toks = s["tokens"]
    return types.Datum(model_input=types.ModelInput.from_ints(prompt + toks[:-1]),
                       loss_fn_inputs={"target_tokens": [0] * ob + toks, "logprobs": [0.0] * ob + s["logprobs"],
                                       "advantages": [0.0] * ob + [advantage] * len(toks)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--reward", required=True, choices=["grader", "vote", "planted"])
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--groups", type=int, default=32)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--cap", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=4e-5)
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--save", default="5,10,20,30,40")
    ap.add_argument("--seed", type=int, default=2_000_000)
    ap.add_argument("--target-token", type=int)
    a = ap.parse_args()
    save = {int(x) for x in a.save.split(",") if x}

    train = json.load(open(f"{tk.STUDY}/data/train_v1.json"))
    assert a.steps * a.groups <= len(train), "not enough training problems for one pass"
    res, raw = tk.new_run_dir(a.out)
    service = tinker.ServiceClient()
    trainer = service.create_lora_training_client(base_model=tk.MODEL, rank=a.rank, seed=a.seed).result()
    tok = trainer.get_tokenizer()
    adam = types.AdamParams(learning_rate=a.lr, beta1=0.9, beta2=0.95, eps=1e-8)
    tk.dump(f"{res}/run.json", tk.run_record({**vars(a), "loss": "importance_sampling", "train_data": "data/train_v1.json",
                                               "console": trainer.get_console_url(),
                                               "raw_answers": f"runs/tinkerpair/{a.out}/ (submitter's laptop)"}))
    ckpt, example = {}, None
    for step in range(a.steps):
        t0 = time.time()
        batch = train[step * a.groups:(step + 1) * a.groups]
        prompts = [tk.prompt_ids(tok, it["problem"], False) for it in batch]
        client = trainer.save_weights_and_get_sampling_client().result()
        outs = tk.sample(client, tok, prompts, a.k, a.cap, a.seed + step * 10_000)
        data, log = [], {"grader": [], "vote": [], "reward": [], "tokens": [], "cap": [], "groups_with_signal": 0}
        rollouts = []
        for it, prompt, seqs in zip(batch, prompts, outs):
            texts = [s["text"] for s in seqs]
            rg, rv = reward_grader(texts, it["answer"]), reward_vote(texts)
            r = {"grader": rg, "vote": rv, "planted": [float(s["tokens"][0] == a.target_token) for s in seqs]}[a.reward]
            mean = sum(r) / len(r)
            log["grader"] += rg
            log["vote"] += rv
            log["reward"] += r
            log["tokens"] += [len(s["tokens"]) for s in seqs]
            log["cap"] += [s["cap"] for s in seqs]
            log["groups_with_signal"] += any(x != mean for x in r)
            data += [datum(prompt, s, x - mean) for s, x in zip(seqs, r) if x != mean]
            rollouts += [{"step": step, "index": it["index"], "sample": j, "grader": rg[j], "vote": rv[j], "reward": r[j],
                          "tokens": len(s["tokens"]), "cap": s["cap"], "problem": it["problem"], "gold": it["answer"], "text": s["text"]}
                         for j, s in enumerate(seqs)]
        if step == 0 or step + 1 in save:
            with open(f"{raw}/rollouts_{step:03d}.jsonl", "w") as f:
                f.writelines(json.dumps(x) + "\n" for x in rollouts)
        if example is None:
            example = {"reward_1": next((x for x in rollouts if x["reward"] == 1), None),
                       "reward_0": next((x for x in rollouts if x["reward"] == 0), None)}
            tk.dump(f"{res}/examples.json", example)
        if data:
            fb = [trainer.forward_backward(data[i:i + 64], "importance_sampling") for i in range(0, len(data), 64)]
            opt = trainer.optim_step(adam)
            for f in fb:
                f.result()
            opt.result()
        n = len(log["reward"])
        line = {"step": step, "reward_mean": sum(log["reward"]) / n, "grader_accuracy": sum(log["grader"]) / n,
                "vote_agreement": sum(log["vote"]) / n, "groups_with_signal": log["groups_with_signal"], "groups": len(batch),
                "trained_sequences": len(data), "sampled_tokens": sum(log["tokens"]), "tokens_per_answer": sum(log["tokens"]) / n,
                "cap_hits": sum(log["cap"]), "seconds": round(time.time() - t0, 1)}
        with open(f"{res}/steps.jsonl", "a") as f:
            f.write(json.dumps(line) + "\n")
        print(json.dumps(line), flush=True)
        if step + 1 in save:
            ckpt[str(step + 1)] = trainer.save_weights_for_sampler(name=f"step{step + 1:03d}").result().path
            tk.dump(f"{res}/checkpoints.json", ckpt)
    ckpt["state"] = trainer.save_state(name="final").result().path
    tk.dump(f"{res}/checkpoints.json", ckpt)


if __name__ == "__main__":
    main()
