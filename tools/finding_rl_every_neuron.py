"""Copying RL's best 1 % of neurons into the base recovers only 16.1 % of RL's effect on next-word predictions.

The page of one finding, served at /finding/rl-every-neuron (view.py serves every tools/finding_<slug>.py) and reached
from its tile on /findings, which ICON draws. The picture is one lit plate holding the base model's 352,256 feed-forward
neurons, one dot each and one row per layer, beside the share of RL's effect recovered and a small curve of that share
against the share of neurons copied. The reader moves one slider, the share of neurons copied from RL into the base
(0.1 % to 100 %, the measured steps); the chosen neurons light up and the number counts to the measured value. A switch
picks how the neurons are chosen. A click on a layer row shows that layer in the side column.
Address: /finding/rl-every-neuron#<share>-<rule>/<panel or layer<n>>. The rules are in .claude/skills/finding-page/SKILL.md;
the looks are those of tools/architecture.py (.claude/skills/site-ui/SKILL.md). The numbers are those of
studies/cleanneurons/README.md, Parts T, T2 and T3.

    python3 tools/finding_rl_every_neuron.py           checks DATA and SETS against the artifacts
    python3 tools/finding_rl_every_neuron.py --write   rewrites SETS from the artifacts
"""
import json
import sys

T = "studies/cleanneurons/results/transplant/"
KEY = "closure_decisive_after_cue_half_B"  # arms.<arm>.cells.<T1|T2>.<KEY> in metrics.json
SHARES = (0.1, 0.3, 1, 3, 10)  # the measured shares of neurons, in per cent; 100 % is arm mlp

# Every number is copied from the artifacts named here. None is typed from memory. The deployed site ships only
# tools/*.py, so the copy is a literal; run this file to compare it with the artifacts.
# A pair is [text written by the base with the cue (cell T1), text written by RL (cell T2)]; the page shows its mean.
DATA = {
    "metrics": T + "curve_attr-01/metrics.json",
    "readout": T + "curve_attr-01/rank_attr_readout.json",
    "profile": T + "curve_attr-01/profile.json",
    "commit": "51b022a72c865057911e83260d2b5661adad0e59",  # run.json of curve_attr-01
    "job": "sameraslan-1114-153108-a93d",
    "command": "python -m studies.cleanneurons.jobs.transplant_curve --rank attr --commit 51b022a",
    "models": {"base": "allenai/Olmo-3-1025-7B", "rl": "allenai/Olmo-3.1-7B-RL-Zero-Math"},
    "layers": 32, "width": 11008, "neurons": 352256,
    "answers": [20, 20],  # half B of each cell (attr.half_B): the rows that score; half A ranks
    "positions": [1163, 1509],  # cells.<cell>.decisive_positions_after_cue_half_B
    # Recovered share at each of SHARES: effect = arm attr<share>, weight = top<share>, random = rnd<share>_s0 and _s1
    "effect": [[0.0535, 0.0733], [0.085, 0.1132], [0.1371, 0.1858], [0.2101, 0.2957], [0.3356, 0.4891]],
    "weight": [[0.0104, 0.0194], [0.0223, 0.0331], [0.0423, 0.058], [0.0776, 0.1056], [0.1554, 0.2091]],
    "random": [[[0.0015, 0.0024], [0.0021, 0.0018]], [[0.0037, 0.0032], [0.0035, 0.0036]], [[0.0073, 0.0103], [0.008, 0.0097]],
               [[0.0225, 0.0296], [0.0241, 0.0299]], [[0.0735, 0.0985], [0.0746, 0.0999]]],
    "mlp": [0.6772, 0.8635],  # every feed-forward neuron
    "attn": [0.4867, 0.6847],  # every attention projection, no neuron
    "groups": [[0.23, 0.4112], [0.252, 0.3198], [0.1061, 0.1419], [0.0853, 0.1302]],  # arms mlpL0-7, 8-15, 16-23, 24-31
    # rank_attr_readout.json
    "positive": 0.8822,  # fraction_of_neurons_with_positive_score
    "first_order": {"predicted": 0.542, "measured": 0.549, "total": 0.708},  # first_order_check_all_mlp, nats, half A
    "per_layer": [42, 132, 125, 180, 156, 151, 134, 129, 157, 381, 182, 140, 164, 138, 117, 106,
                  90, 64, 40, 36, 31, 34, 37, 38, 36, 28, 36, 36, 38, 91, 152, 302],  # attr1_neurons_per_layer
    "overlap": 610,  # attr1_overlap_with_top1_by_weight_change
    # profile.json: share of the squared MLP weight change per layer and in the top 1 % of neurons by weight change
    "weight_layer": [0.0305, 0.0305, 0.0302, 0.0303, 0.0304, 0.0303, 0.0306, 0.0306, 0.0309, 0.0312, 0.0312, 0.0314, 0.0314, 0.0314, 0.0315, 0.0314,
                     0.0314, 0.0315, 0.0312, 0.0312, 0.0314, 0.0314, 0.0315, 0.0316, 0.0315, 0.0316, 0.0317, 0.0318, 0.0323, 0.0324, 0.0324, 0.0315],
    "weight_top1": 0.0147,
    # The run with one constant vector per layer: bias_layer adds it to each layer's output (no weight changed)
    "vector": {"metrics": T + "curve_bias-01/metrics.json", "commit": "a2ec2c9", "bias_layer": [0.2342, 0.3118]},
    # The neurons that light up: exact for the three 1 % sets and the 100 best, from these edit files
    "sets": {"effect": T + "curve_attr-01/edit_attr1.json", "weight": T + "curve-01/edit_top1.json",
             "random": T + "curve-01/edit_rnd1_s0.json", "top100": T + "curve_attr-01/edit_attr_top100.json"},
}


def mean(v):
    """Per cent, the mean of a pair or of several pairs."""
    flat = [x for p in v for x in p] if isinstance(v[0], list) else v
    return 100 * sum(flat) / len(flat)


def pct(v):
    return f"{v:.1f} %"


ONE = {"share": 1, "best": DATA["effect"][2]}  # read by tools/findings.py for the tile's figure
BEST1 = mean(ONE["best"])  # 16.1
STOPS = [{"share": s, "neurons": round(DATA["neurons"] * s / 100), "effect": round(mean(DATA["effect"][i]), 2),
          "weight": round(mean(DATA["weight"][i]), 2), "random": round(mean(DATA["random"][i]), 2)} for i, s in enumerate(SHARES)]
STOPS.append({"share": 100, "neurons": DATA["neurons"], **{k: round(mean(DATA["mlp"]), 2) for k in ("effect", "weight", "random")}})
_V, _F = DATA["vector"], DATA["first_order"]

TITLE = "RL's change is spread out"  # the name on its tile on /findings and in the browser tab
PROBLEM = "Is the effect of training with reinforcement learning (RL) carried by a few neurons or by many?"
LINE = (f"Copying into the base model the 1 % of the RL model's neurons ranked most important recovers only {pct(BEST1)} of "
        "the difference between the two models' next-word predictions.")

# Not from our runs: the closest published results, checked in full text on 2026-11-15. Mukherjee et al. (arXiv
# 2505.11711): RL updates 5 to 30 % of parameters (Table 1: 68.5 to 96.0 % unchanged), in every layer (Fig. 3), nearly
# full rank (Table 2). Weight Patching (arXiv 2604.13694, Sec. 5) copies MLP neurons from a tuned model into its base,
# ranked by a first-order score, read out by KL; instruction tuning, no RL, no curve of concentration. Lu et al. (arXiv
# 2611.10866, Table 7): a reward-trained mask on MLP gate weights deletes under 0.05 % of weights and matches full
# fine-tuning at 7B and above (Tables 1 and 2).
PANELS = [
    ["new", "What is new",
     "It was known that RL changes weights in every layer: Mukherjee et al. (arXiv 2505.11711) find 5 to 30 % of parameters "
     "updated, spread over all layers, nearly full rank.",
     ["That counts which weights moved. We measured which neurons carry the effect, by copying them from RL into the base.",
      "The closest method, Weight Patching (arXiv 2604.13694), copies neurons from an instruction-tuned model into its base, "
      "but reports no curve of how concentrated the effect is.",
      f"New here: no small set of neurons that we found carries RL's effect. {round(100 * DATA['positive'])} % of all neurons each move the base "
      "toward RL, and their effects add up."]],
    ["why", "Why it matters",
     "A search for RL's effect on predictions inside a few neurons is unlikely to find it in this model.",
     [f"Ranking by weight change finds even less: its 1 % recovers {pct(STOPS[2]['weight'])}, a third of the best 1 %. Only "
      f"{DATA['overlap']:,} of the 3,523 neurons are in both sets.",
      f"The weight change itself is flat: every layer holds 3.0 to 3.2 % of the feed-forward change, and the top 1 % of neurons hold "
      f"{100 * DATA['weight_top1']:.1f} %.",
      f"Cheap edits that copy RL's effect may need to be spread over the whole model: one fixed vector added to each layer's output, with no weight changed, "
      f"recovers {pct(mean(_V['bias_layer']))}."]],
    ["how", "How we know",
     "We copied the weights of chosen neurons from RL into the base and measured how much of the KL divergence between the two "
     "models' next-word predictions disappeared, at the 4 % of positions where it is largest.",
     [f"The text is {2 * sum(DATA['answers'])} stored MATH-500 answers at T 1.0, half by Base + cue and half by RL. Neurons are ranked "
      f"on one half and scored on the other: {sum(DATA['positions']):,} positions.",
      f"Controls: copying every weight gives exactly RL; a random 1 % recovers {pct(STOPS[2]['random'])}.",
      f"The effects add up: on the ranking half, the neurons' first-order scores predict a drop of {_F['predicted']:.3f} nats, and "
      f"copying all of them drops {_F['measured']:.3f} nats, of {_F['total']:.3f} nats between the two models."]],
    ["limits", "What it does not show",
     "It measures how close the base's predictions come to RL's on stored answers, not accuracy on math problems.",
     ["Which dots light is exact for the three 1 % sets, which the run saved. At other shares the number lit is exact, and the "
      "dots are drawn at random within the layers of the 1 % set.",
      f"All feed-forward neurons together recover {pct(mean(DATA['mlp']))}. Attention weights alone "
      f"recover {pct(mean(DATA['attn']))}. The two shares overlap, so they sum to more than 100 %.",
      "Another ranking could find a better 1 %. One base model and its RL version were tested."]],
    ["run", "How to reproduce it",
     f"On one H100 GPU: {DATA['command']}.",
     [f"Job {DATA['job']}. Its numbers are in {DATA['metrics']} under {KEY}, each the mean of the two texts: the best 1 % "
      f"recovers {100 * ONE['best'][0]:.1f} % on base text and {100 * ONE['best'][1]:.1f} % on RL text.",
      f"The lit neurons come from the edit files of that run and of curve-01; the fixed-vector run is {_V['metrics']}, commit {_V['commit']}.",
      "python3 tools/finding_rl_every_neuron.py checks every number and every lit neuron on this page against these files."]],
]

# The neurons that light up, from the edit files of DATA["sets"]: per set, per layer the neuron indices in increasing
# order as base-36 differences, layers separated by "|". Written by --write.
SETS = {
 "effect": "4k,2a,cj,i0,fe,bz,bn,36,4b,1s,30,15,41,o,c2,61,nb,e,3z,8s,3m,3z,b3,5s,a,3l,1e,6g,ek,2u,2f,5d,ib,f4,x,59,20,bo,be,8q,h7,o|f,26,i,21,ab,12,d,2,73,8n,5t,20,z,b8,19,h,f,12,c2,15,1l,12,7n,2,1a,d,1y,v,51,1i,d,21,1y,20,h,p,65,37,47,1,1x,1s,x,1j,1u,1i,2e,y,1a,4,19,1c,b,56,1j,z,18,s,7b,4,f,1j,6c,3j,d,27,1l,4,w,1v,2h,66,d,1i,1k,1r,3b,f,2g,4d,16,2w,x,m,1e,1p,3j,fy,k,g,1u,1j,7d,32,y,7u,18,1f,24,15,2w,2n,y,3w,5l,6,3n,19,3p,34,22,2d,1q,2u,1b,f,s,1l,v,9,t,2d,1t,4j,5,b,6,c,1u,1i,22,19|q,3,3g,20,8p,c,1g,8e,4g,1m,y,1,4,a,27,1s,k,13,1r,q,n,f,2h,n,34,7c,1c,q,1q,3m,3,e,2g,3z,2d,e,22,5d,2x,1n,24,1e,k,1g,44,h,2t,j,r,1d,54,23,3b,20,7,e,20,7a,7,26,27,20,33,3q,6,2o,2w,3v,x,14,s,2b,72,2v,62,2s,4m,13,8t,35,a7,x,1f,1v,7x,1l,5,3h,39,j,8b,20,3m,17,17,2m,8,4v,3w,9,c,3m,1c,13,11,60,1,z,6v,49,1z,59,6,3,t,4,m,1h,7,8,r,42,4z,4q,8q|q,2l,1m,2p,10,1g,3q,40,p,13,1v,h,2d,5q,12,z,i,7,36,14,1t,1i,19,f,z,u,k,c,d,b,2n,b,f,1a,f,2h,1l,u,25,5k,3b,s,6,8,1b,c,5,1a,x,13,t,9,2a,v,ba,1s,c,5r,33,1h,b,c,26,e,e,2k,n,r,b,v,1d,10,c,2o,m,a,10,z,a0,7,k,c,13,g,1q,r,h,z,l,1w,c,35,3a,4,9,3k,3,s,6b,r,2e,s,s,y,2,4e,r,e,9,2i,28,4v,5u,1a,17,7,14,y,5c,25,1e,32,3,7,z,9,1s,2w,1l,2m,1l,7,2e,k,1n,m,1,44,5b,26,1g,3h,14,6,13,1w,31,4s,s,3,h,k,2,1y,23,50,w,7i,c,1o,38,6,17,c,1e,p,y,9l,b,2i,5,3,7c,12,g,1s,1c,7,49,3a|17,5,11,1g,23,42,1g,9,13,12,2j,1e,l,j,x,c,30,1v,i,o,1x,12,q,14,m,3c,p,2,53,6,1u,7b,n,e,2g,4,37,4o,3a,w,1u,k,4h,1l,32,7y,s,c,3v,2n,2m,2w,u,a,v,30,5c,15,b,11,27,1f,3q,2j,z,2r,9,g,19,1v,30,r,11,3b,3h,7,b,29,v,1,k,9,6,3k,e,d,t,1k,g,q,a,1e,1f,h,2t,6,s,13,e,6p,1y,2h,18,1f,1w,3,3l,1t,3f,3j,s,6,4f,23,48,ao,3a,2,20,1y,3d,1q,1p,17,18,7,2s,2u,32,20,z,3o,9,16,12,41,6l,19,1w,b,4o,3k,1x,8m,2v,7b,21,t,d,o,11,x,2m,g,9,3j|m,5,40,k,10,z,a,1v,2p,2r,5h,r,f,1q,7,38,30,8,1x,2n,j,4e,3,am,n,50,3y,2g,38,t,15,38,2x,1,1c,15,j,2,1j,1p,d,1h,l,h,3c,1l,g,1f,16,25,1g,5,d,5,b,34,1k,1p,29,z,d,7,s,t,a,2,l,1h,r,k,5i,4g,bf,h,q,u,b,c,3p,w,b,1k,4m,24,28,6w,8g,u,13,3h,1i,k,4d,1s,4u,1a,2a,58,u,28,3e,j,2w,1h,n,2a,33,1t,6u,4n,2q,9m,10,4e,n,37,u,i,1z,15,m,u,9,6m,1p,a,f,z,s,37,1n,57,1z,r,4j,3i,4,1t,2r,5v,14,i,2g,u,2c,r,1,21,10,9,14|1d,1k,15,2z,22,1q,1e,5,1m,1b,3b,3q,j,g,4x,1f,k,2q,65,3z,4,3b,3l,g,21,10,6d,12,3r,4,9,19,52,14,2h,3u,d,2,k,l,14,1k,91,53,z,n,4d,1p,z,4i,4,1d,1e,c,r,a,69,x,2f,1t,1q,44,q,r,1o,3o,1q,21,9,3s,1i,1i,3,33,6m,29,2q,k,2z,57,6m,71,k,1o,i,x,2e,5v,28,l,3r,1a,1p,36,1f,67,4z,j,18,70,39,b,2d,6,o,r,43,1p,2v,w,79,1v,26,1,n,30,e,23,i,t,55,7,13,5,d1,18,2e,1b,4,9z,3,z,x,11|12,13,d,2z,t,c,3,3b,1k,2o,12,1g,7b,g,26,33,1o,6,o,1y,5q,7y,37,3k,1c,5l,14,1n,q,4,c,2j,1g,3c,2o,32,8c,30,e,1u,1m,37,2r,65,15,1q,2q,y,j,4a,2e,8k,b,1,l,3,n,8,8s,1j,1y,1c,t,3,8,5z,3e,1i,1l,14,f,2j,9,2n,15,1,63,t,5y,e,n,4,19,3x,73,q,1p,z,40,46,2i,e,c,3j,a7,59,14,4k,2c,d,j,4s,8s,1i,3,2h,9,q,u,3v,j,e,j,5j,1v,2w,16,4i,r,u,2r,18,4a,5c,9r,1j,1f,1k,15|9,16,1n,q,7a,x,1y,6a,c,2t,d,1h,18,x,1e,3b,2,5,14,46,h,3y,16,6p,66,1o,1g,3q,1c,84,3y,d,3,1v,10,k,46,1z,22,l,2i,43,n,3a,2f,2t,3j,1g,1h,1x,14,u,7,m,8,16,1m,t,3m,1i,29,8,o,2d,2l,q,3,27,3e,26,b,1r,d,i,4,22,18,4j,o,u,f,1y,46,1b,i,v,6g,i,e,5,8,s,c,f,l,4t,z,1k,5t,2e,12,d,q,b,s,i,3f,39,1n,5b,g,2c,2g,6,1p,1f,10,g,i,6c,3,m,4o,2v,s,1m,15,6,3y,2c,2b,5r,46,1e,f,27,1z,8f,4m,n,n,30,29,3w,r,y,2j,34,1l,f,s,5,32,g,5b,3,2a|1c,32,28,17,f,w,l,l,7,10,d,2,z,b,h,s,g,q,14,j,e,7,8,b,w,10,2b,3,3k,1e,2f,6,5,d,i,6,w,7,1i,z,9,5,z,2,8,1a,o,8,3,b,g,39,m,3s,4,10,d,z,t,n,9,s,4,16,u,s,l,13,8,s,2,1a,o,4,k,a,1,a,17,15,z,1z,l,11,1f,e,2x,n,e,1l,o,1,h,i,13,g,q,r,e,9,1,6,9,3g,3,40,11,e,5,b,m,c,f,s,g,1o,2,i,j,w,e,9,3s,1p,g,1,e,l,6,12,1w,11,q,2j,1q,19,12,3,6,11,19,5,p,j,18,m,9,r,12,3,k,m,5,n,12,28,6,b,3h,11,o,8,b,x,7,r,1k,d,y,4x,6,3,1z,e,5,1h,1,q,8,5,d,a,u,24,1,5,k,6,14,t,4,6y,v,15,k,t,o,4,17,2,f,12,j,j,4,k,17,8,16,2,29,3,2,2,h,l,v,3,q,g,e,1,a,8,14,4,w,e,h,3,d,l,c,p,4,7,3,3c,2i,4,v,w,m,13,y,l,7,1,g,o,6,a,s,1w,i,6,n,7,18,b,16,12,k,3,18,g,6,r,6,i,c,7,c,12,1j,v,1m,5,q,6,t,l,a,e,v,e,8,d,2k,5,1a,c,1d,u,a,11,1h,7,6,4,2v,31,m,l,15,t,8,d,s,9,h,z,v,r,d,e,f,1q,45,o,1a,x,w,e,f,b,1,4,1i,f,u,z,t,1h,u,7,2s,8,l,1w,7,l,2,q,f,4,n,3m,k,1u,c,1s,24,6,36,8,14,a,11,1k,16,7,2,3,x,j,4,7,19,r,1e,f,2k,c,5,e,1o,22,g,s,5|0,25,9,p,8,3r,n,1l,1c,16,15,2u,k,5,1b,1q,6,8,l,2,1x,1o,10,1y,1z,2g,1,w,o,2f,3b,s,2i,f,1c,29,3q,d,10,v,d,e,13,n,n,3q,2d,30,w,r,4v,38,1b,ej,1e,2a,29,43,o,e,7,4g,i,s,2v,6,e,6a,7b,x,3v,5,d,h,15,u,x,c,c,3,x,2l,1t,2,12,1l,19,64,1r,c,17,3,51,y,7n,a,1o,24,f,8,18,2q,z,1l,j,15,4t,4,i,9,1i,c,5e,66,b,4g,2,1,1u,29,1x,3p,g,12,1u,40,2s,19,16,23,5,4x,1o,1i,9,42,t,1z,2y,f,2y,44,1g,s,2l,r,1f,i,46,w,1y,4,1m,25,1z,x,8,1g,b,b,1p,45,2n,e,m,1f,7q,a,x,h,s,e,f,1,27,23,3,u,10,p,2,e|8n,c4,3x,3,s,4i,2g,3i,s,f4,13,3i,12,17,1x,4m,k,7,1u,1s,3c,2w,w,7,12,25,2g,31,m,3l,76,3,q,t,11,14,19,3n,25,1l,12,2j,6,1g,6h,2m,1a,30,i,7g,1m,6,b,1g,4c,z,8,1t,d,27,1i,2v,41,a,1y,2d,h,7,6a,27,1y,i,d,x,2u,33,1a,1z,22,t,1a,1a,1r,31,a,2,1z,3y,r,u,31,11,24,9,2f,2j,1f,2c,2d,r,h,54,34,2y,16,2d,l,28,2c,2f,r,1o,6,b,a,o,4g,19,31,w,1a,1b,c,75,3t,24,1f,14,2e,h,2q,7p,1y,2n,s,29,1o,1e,4d,22|0,s,6,2f,4u,5o,1h,5,3h,4u,o,6a,1e,1h,1j,d,1t,a,j,27,10,1a,p,1m,o,p,q,22,r,1c,f,3b,2g,g,4p,1b,9,1b,8,n,6,4k,a,1x,20,p,19,1,1,3m,3s,9,5,l,1f,2e,w,9d,2d,2b,1l,j,d,2c,p,36,b,1p,8,21,21,2u,n,m,9,n,n,x,1e,5j,7j,1j,w,15,2s,5,2r,47,f,z,e,2m,31,b,1k,1a,26,2n,7,9,d,1t,2b,w,1v,11,36,2w,13,3w,1q,s,1d,j,15,t,1c,1t,2h,2l,z,o,15,2h,17,17,23,2n,3z,29,1z,b,3d,w,38,38,ba,3k,18,1z,1d,4c,b,r,1s,h,6q,f,4k,1p,25,2v,15,2,5e,15,14,5d,2u,4,39,a,i,1f|y,26,16,3a,20,1,15,2j,22,s,10,j,22,1b,i,3n,5t,3x,e,57,1w,2a,d,h,8,b,z,20,3,2j,2g,22,1b,1h,1w,56,m,l,1m,2y,u,22,34,l,y,s,35,1l,f,e,1w,5q,14,3l,7,1v,49,6j,a,3j,16,l,1h,62,3,3j,14,2i,x,1f,1h,h,4w,bg,5,20,n,42,fu,1r,25,i,1z,l,2c,c,v,4l,27,5,1,k,2q,1r,13,3,c,l,40,j,2p,25,7k,79,30,f,f,1j,p,7k,5h,1f,o,j,16,47,2y,c,t,3t,j,1,7x,2z,1v,12,8j,2e,v,1q,2m,3w,1m,j,2c,3p,2,1n|8,2l,4q,e,l,47,58,u,1b,h,5x,29,10,60,1o,1b,6,6u,f,7,1a,9,16,12,6y,73,5d,2t,46,2b,1h,9,1d,9,29,49,3a,k,22,10,28,3f,2x,1y,5v,w,bz,2v,1y,44,34,c,1w,2t,c,7x,5q,2d,8c,y,4,95,27,2i,j,1c,r,w,2s,2p,4k,w,4q,1k,29,1z,1c,s,g,b,5l,h,1w,3k,s,1h,2m,16,2w,j,8,13,2t,f,ab,h,1w,cx,10,l,2b,1p,h,3z,2u,f2,y,z,2e,27,1a,g,n,1f,2,p,6i|d9,7l,s,28,3n,6z,d,1g,18,2c,2m,1b,e,3s,1b,1,3k,3,5x,w,2,3h,2u,b,1,k,4,r,18,3i,3h,3k,79,1h,16,9r,4e,4a,1x,5l,3y,3k,1g,6w,35,4d,59,7b,1,16,2y,y,k,9,49,3u,3r,41,36,5v,3z,7,3l,w,10,36,2,2j,5,9d,4v,j,3o,h,k,2w,g,4k,u,1g,9b,88,2k,2a,2l,11,1f,1c,a,6f,w,a,63,1w,11,m,3i,10,44,2l,19,2g,2x,k,94,3|75,n,2h,3j,56,3g,1y,n,d,6x,2h,1g,52,48,66,16,j,2z,3f,3t,3t,ak,1l,3,29,q,8,8s,17,4z,3e,a9,1,54,17,aj,h2,y,t,r,1g,g,3e,6p,a,6i,1p,r,59,e,1v,16,4n,2g,1l,2p,6,1a,2s,2v,8x,7c,2k,1e,7i,w,w,e,4,22,no,1f,16,1,5s,1k,1,72,23,cf,2f,27,i,r,74,1k,v,u,1w,4a|bn,9o,22,1v,j,7,28,1x,23,1m,6s,1,5j,3j,2y,8,1t,3u,2f,75,9w,e,5k,68,3h,2c,4o,15,3,2,5,9x,a,v,2a,f,4b,1p,3r,g,7a,65,2q,bu,2h,72,8f,5k,2v,3q,h,6p,128,a1,1y,34,2j,at,81,42,hq,90,3g,5j|f,20,16,8j,8p,13,j,6m,1,gt,39,51,ad,28,1a,da,7n,hp,73,lx,hh,5o,n3,dm,9w,9o,bj,2y,l,2s,6m,1t,2g,gk,1x,1u,3l,sa,33,1g|cz,j,cf,cb,105,1j,6o,7y,2f,a6,5y,j0,7o,7g,6n,bt,5e,2g,q,ly,6g,1v,98,17,5i,7x,9z,c,9x,1x,xd,8i,35,r,2s,24|fv,q1,2q,24,1k,1s,e,dy,iu,tb,9g,5t,55,45,1m,3l,1p,1e,10x,ou,l8,23,1l,i1,f,3w,em,j8,3u,8c,21|3,15j,i2,e8,as,6,cf,7w,4d,f9,2g,au,j,6,2f,6x,8v,gg,vn,31,18j,1y,7r,4w,4n,4t,y,4,13,r,55,2r,29,75|2o,77,dr,27,94,bc,4v,x,33,ax,1b,c5,l,t,54,9,9m,p0,1d,je,ek,3e,15n,6g,4c,b4,6i,2z,12,j,dy,9g,7k,3i,co,t,6u|g1,g,vy,2j,3c,8d,u,9,5o,5e,27,7i,6b,7h,ft,1i,1c,15a,2s,c5,2q,42,bj,1m,p,fb,e,1b,82,5i,1b,1v,qe,4y,cf,5x,6e,ak|3h,ix,1q,6w,3l,w,5s,1n,bk,9g,ku,3f,7x,im,6i,1n,1,ic,8p,i,bu,30,u3,f6,31,3z,gw,1z,b0,22,86,s,1t,3k,c2,o7|6z,3i,8f,34,q1,qc,1b,56,1q,fd,p,2x,1w,nu,4c,c6,4o,et,ju,ha,ic,t6,15,di,b,1z,4o,105|3f,2m,9j,b,4e,44,z5,3,137,z,8a,4,bf,s,2s,ie,b6,2i,t5,38,3l,k,9v,1h,66,gs,11,6j,w,13,lk,iv,6g,6c,4q,bo|82,88,m3,6q,3z,95,1d,62,jt,g0,dp,gt,13,84,d9,b9,bd,18,ax,cg,2b,w,x,gj,ud,9m,1y,23,19,ic,2t,2k,26,50,15,3x|67,1e,2g,5e,27,16,3k,iy,aa,12,4l,2c,1i,36,m,6h,3q,gh,78,wf,hu,9t,ri,d5,3k,by,j,bc,8o,3j,6o,e4,aw,x,6l,3r,7v,5j|5k,1d,6u,47,5x,8w,4d,43,27,1m,1x,6s,25,2u,20,6,b,c4,1b,5,r,1e,2,5a,17,1,5q,w,45,55,c,18,t,5w,44,34,13,21,2b,t,1p,2e,1m,8b,3z,n,1e,15,2a,w,t,4h,6,1v,1p,30,20,41,3l,3i,25,1n,10,84,32,4v,k,z,1,3,y,gv,w,1b,4j,cz,f8,14,1s,1b,95,2c,7,9w,31,32,26,e,1t,2e,ga|z,24,2q,1g,n,4l,2d,10,w,14,1r,1r,u,24,8,e,1b,n,1a,14,b,7,30,4i,1l,6,2w,1a,4y,a,l,4,3h,n,2d,m,j,4o,b2,1e,m,4k,42,1g,13,w,a,k,1x,5c,3n,x,3r,1y,6e,1v,m,4,18,q,t,1o,n,b,7,i,2a,p,17,d,19,1j,a,16,5g,y,h,q,43,c,a,x,4,z,3,4,2b,y,11,5,13,3m,6,4f,1q,3p,v,2b,15,1a,7,23,10,1l,7f,1s,5e,2l,24,a7,62,17,2y,1i,2v,4i,22,y,6x,3a,1s,5b,2l,p,1t,14,58,2o,1d,35,19,1,6m,15,1t,13,1v,2i,1n,i,1z,13,a,30,1p,1,c,q,ao,2x,7,c|6,39,15,1r,d,2f,2,e,1,1m,h,y,13,6,3,m,8,1p,5,v,k,1s,2o,25,h,19,7,9,i,i,1o,1j,d,l,1d,35,24,b,z,o,v,1,1l,1i,1m,c,k,5,g,n,y,2i,24,25,1w,e,g,b,1,8,1r,1t,4,11,1p,1l,13,29,9,1r,l,b,z,h,e,2,35,c,1d,a,1g,a,x,a,s,5z,4,7,14,4,19,10,4,1,12,1,g,3,4,9,39,u,1q,26,d,o,l,7,8,a,g,2r,s,26,2q,1x,h,u,s,6,y,12,1h,b,w,4,1a,6,4,1f,2d,p,e,8,27,2,18,3s,22,v,8,6,4,i,d,17,2,2f,d,5,h,1,a,4c,p,4s,1p,3,3k,f,z,d,34,n,v,2s,6,16,e,1p,x,2k,x,1e,c,6,g,x,1j,1a,16,d,j,2y,32,6,7,5,s,4,1r,15,1a,e,k,6,2s,x,h,w,2b,6,a,6,17,l,18,v,28,4,7,6p,3,8,2k,9,34,1b,5,o,29,4,11,2,j,14,b,b,k,1o,u,12,g,g,h,x,1,5,5,1d,z,2z,b,1n,8,a,g,t,9,s,3n,y,1q,n,q,1h,o,2i,9,c,6,4,1v,3,1l,l,3,w,k,34,2,17,1,h,c,1x,3,s,8,n,s,3,i,2h,t,x,13,4,2j,1i,u,3,a,6,1q,b,31,5v,s,2,l,t",
 "weight": "2mg,o5,6z,v0,la,nd,1eo,1,mp,92|57,cv,5x,cq,6r,7n,sy,50,qp,j5,go,1s,wb,iq,2d5,d7,22,12|t,4b,7q,qs,fe,jz,2gf,a5,ei,1w6,oc|ek,1gx,3x,171,1c9,f0,82,ww,7o,7x,ez,d,1h,9n|be,8o,ah,2pa,c2,jr,1h,6b,14x,6i,4f|6b,2le,1hc,nz,dl,xy,2f,m2,p7|49,py,cw,vs,10s,e5,c7,g,kk,1nj,2e1|1e0,1dk,1ic,7e,wg,148|bz,fc,18w,18t,z0,h5,3j6|i1,dl,b5,c7,za,2l,wg,kz,1go,2q,1hw,3h,ti,2z,8o|25,9,x,7b,5u,ck,2h,1k,72,a1,3p,of,bi,a0,5p,4p,c2,6i,40,3x,2x,nl,k4,97,fc,g,71,c9,32,6k,2r,gs,v,3r,2n,v,r4,2s,2z,31|11n,11s,a5,cz,3e,s,2v,8x,6h,gx,5s,c3,1v,a9,i,5s,4,9z,9,hs,42,5o,cw,17,96,78,2t,u,a,16,94,1a,aw,r8,32,6f|y,79,9h,j,69,fu,2a,1h,u,23,u,42,3n,28,7s,t,i5,d3,8t,a,67,ky,9v,2x,3u,ce,8k,95,3v,e0,6f,v8,hv,2u,2r,90,f,8e,al,hy|9l,6c,1l,d,34,br,n,1o,7,79,c,25,p,20,1d,65,10,17,ml,55,10,bp,fw,dn,14,3f,2w,16,47,b7,e,5h,1c,12,j2,gs,1a,1i,4q,33,25,7z,3b,5,6e,2d,6w,8x,j,16,47,3a,6,26,26,4,bg,x,20,1k,3g,5x,60,33,9n|8,1h,6t,a8,4p,3c,s,16,3c,4r,10,w,1s,y,21,4e,g,2l,2f,18,b,31,59,3b,eh,7p,1o,73,3s,aq,tx,2e,96,fc,a6,1t,15,1s,1a,6n,1l,33,6d,14,3q,1s,62,80,v,2,1e,94,2u,56,2b,2b,7v,64,2s,2n,cz,cu,1o,3n,q,72|2d,4q,4o,93,g,e,26,dn,6c,5f,ai,5x,e,q,8g,s,5n,1p,3t,9t,6n,4a,1x,1c,d7,71,5,m,br,q,6q,16,4p,5j,d1,h,4,2o,1g,47,57,w,1w,2a,2,1s,w,22,8q,6o,4w,5u,b,3z,6g,jg,a,61,5k,23,1,12,t,e7,1z,6,7,87,4h|6d,s,1y,1j,8c,2c,3w,6,2u,55,27,9y,au,5z,2g,3e,61,5f,29,j,d,8u,ci,172,cn,50,7z,3o,19,cq,73,a3,1n,6b,t,9s,10,27,3z,5g,3y,al,16,1,47,1l,v,9v,49,a1,k,2j,1u,5q,3q,4k|en,8q,6q,3p,ai,e,1g,3o,7b,m,2p,2q,5n,1y,55,80,6w,22,36,1m,49,2u,78,19,fa,3y,6z,6,4o,2k,a4,w,2b,50,16,5n,3h,w,i,1a,6h,8j,z,5,g,4o,2e,d8,3n,2s,8l,23,18,5m,2m,e,16,1c,8,7,4e,5o,5e,5,2y,78,4,9m,2b,t,14,39,3h,83|f,29,1z,20,5h,ab,lw,p,o,20,1g,fe,pl,d1,9e,46,2z,9b,5a,21,2j,eb,1f,49,1s,3p,23,km,16,3b,9q,15,33,9o,19,ms,4o,3e,f3,b9,2v,9,1e,25,x,gb,34|25,8w,fi,1t,9w,7c,38,2l,5t,a4,2t,85,8j,eu,2h,k,1v,bc,a8,35,f6,5i,az,ls,5i,d0,2t,39,4o,h,jx,cr,1u,6x,20,bm,mt,3r,9t|26,8g,66,5u,5f,hi,2r,5t,l7,7q,90,9f,6y,54,4b,47,f3,1p,57,4s,98,39,c,dj,1k,2f,38,89,g,cv,f,o,1z,c,3h,p,1w,6i,3f,55,3o,4w,2n,et,2i,7m,9i,i,ih,d,2d,7m|5,1o,17,2,74,44,4m,24,5z,bc,1,20,1a,bf,25,6,4i,82,13,w,m,21,w2,46,2n,67,2n,1f,h,54,y,2e,ce,c,7q,4c,3k,p,a,6g,2a,28,57,3r,1a,6n,7,4p,2z,r,9,10,c,2j,3p,y,4t,2,61,1e,5x,38,60,bq,9y,27,aq,4s,1,4s,c,1t,1j,55,1z,27,7d,h,o,6x|0,2p,3,17,7,2s,9r,3b,26,1m,o,8n,w,y,14,3v,b,2o,99,79,1b,4s,1g,g,19,10,p,b,o,o,1b,5y,w,4y,t,f,19,4l,2l,33,1i,k,4h,2v,3j,6l,20,23,f,1o,1a,7k,4t,3,2j,dl,3k,2b,10,6h,3h,11,9,w,o,f,42,16,1a,h,r,1,6l,16,57,m,1c,i,2n,2w,1h,4u,v,g,g,1b,4e,1g,1f,4i,12,a0,x,8j,3p,98,11,17,2g,15,g,4d,c,d,c,g,5m,13,1i,4h,4k,23,1n,e,4u,5n,3j|3e,1n,13,3v,5r,r,2i,2v,21,3y,3h,1r,b,5q,2,9b,m,1w,3d,6v,h,7,16,u,7,4l,23,2c,10,5c,21,5,a,a,17,1a,p,2v,u,65,37,1w,1u,2f,2n,14,2,3h,27,7,p,t,12,2i,o,kf,d,o,ar,5x,2m,2u,4w,10,3v,9,9,1j,4o,3,2p,e,2,1n,2m,6t,p,z,g,3v,5,v,7z,8,6,1b,3d,4f,1b,61,1d,t,l,7,m,d,79,b,5u,q,1e,4,37,47,13,25,r,3p,15,7p,1y,t,3b,6,30,2t,a,a,1p,3,z,26,2y,au|42,2f,58,7,1x,29,l,3f,1x,b,4,1q,11,49,1m,b,3a,g,41,1s,26,7m,3u,m,52,3s,m,j,12,ci,1p,4g,k,1t,2g,38,5v,56,9k,6,16,19,k,68,2,bf,1a,2l,6b,36,2f,3q,1m,15,2h,1j,1t,1w,1b,m,1s,n,5o,14,50,1p,4i,12,s,2r,1d,p,p,1k,3g,3h,3c,8h,m,4,3,26,54,8,4f,1g,24,21,h,68,1n,r,29,46,77,54,1c,28,a,1x,2f,4o,20,s,5f,3n,14,2a,1l,35,30,n,1q,5d|1g,25,2g,c,1f,3d,10,10,1i,9o,30,29,1m,6o,6,2n,5m,u,s,a,8,o,p,e,8p,w,a4,31,2u,x,1,18,i,4x,a,31,a,1f,5n,2h,1o,d,8,28,2s,l,n,1,5l,4s,1r,2,19,x,c,l,13,1,8j,u,1b,5l,1w,92,10,p,6n,45,2c,z,4j,l,72,m,7,20,2k,2i,n,h,14,5v,1,22,3i,1p,r,1c,bh,z,3p,1e,1c,4,h,k,5,2h,2b,14,m,2h,12,24,2t,1y,5n,6,t,14,2k,n,3j,4b,1w,19,x,1,11,8,v,14,i,4r,1h,2b,3p,4k,3m,1k,u,5b,6,39,1z|10,n,5u,y,f,20,1w,2d,2s,2,2c,b,19,p,11,10,x,d,1,4z,5o,17,37,30,4i,32,15,5,p,1l,2g,k,1j,3,r,2x,2h,f,a,39,u,18,1k,1z,i,3a,1u,6l,r,al,1h,r,3l,3g,z,3p,1a,16,2g,6,4l,j,9,41,9,j,19,l,4l,1j,26,1f,m,1g,34,39,4,x,1k,13,15,2i,4c,3n,3r,2a,a,3r,20,42,7,w,b,k,5,c,1q,5,40,2g,1p,4f,8,2,2u,1d,5b,r,f,f,1q,63,o,a,5u,17,8,1f,2w,1m,b,1r,y,n,1e,3d,13,78,4,10,r,j,8l,c,1q,1h,17,29,27,4,v,c,3s,5w,1v,e,q,3c,6k,3d,2i,8,z,8,9,21,m,48,h,u|c,49,9,d,v,1l,12,3v,9,2r,19,3,18,2,23,f,12,6,f,20,l,17,3c,4w,15,1m,h,51,v,19,4e,7f,19,h,s,o,15,2u,f,12,1y,2v,k,8,q,1,1n,4e,1f,e,j,17,1q,8,2i,1d,9,1p,1a,r,1a,bo,13,2p,1n,1v,e,1h,a,j,r,21,s,a,7,y,2l,1,1d,1d,l,i,p,s,31,21,d,13,1a,1c,15,2c,1e,n,1v,3,7,2,4,u,q,1c,b,17,19,h,4l,2h,51,r,55,5,6,e,1,2m,30,4g,4,7b,t,30,q,k,6,2z,37,9,47,1q,7,e,b,6,1n,11,3a,6,1p,18,2d,2p,2o,a,u,1s,2d,c,m,4,3,6,6,1k,l,f,19,j,y,2u,2h,f,3g,3,1q,55,1b,5,1x,1v,18,23,1f,1d,u,28,k,2,20,1,7,l,h,23,14,3d,1a,7s,11,1p,52,b,8,q,k,4i,8,y,15,17,e,1z,d,1v|h,15,3,t,e,c,4,6,l,1h,8,f,3u,3s,1m,8,1z,16,38,2,1,2,6,o,7,1q,8,27,t,1k,9,4,r,6,17,12,r,b,k,4,15,1r,x,6,n,1d,1,d,2,f,15,i,9,4,9,g,3e,16,1n,1z,x,1x,d,l,n,11,1,2c,a,12,7,17,j,s,a,8,14,l,c,i,9,15,2f,n,7,1g,39,14,i,q,17,4,23,1b,1l,14,26,2c,g,k,c,1n,3e,1,o,m,c,1l,1m,g,7,d,3,n,1w,9,1d,p,8,3,1w,o,k,q,a,7,3,1d,2c,j,s,c,1,b,k,l,c,e,18,e,5,3j,1i,15,j,9,1e,o,r,j,1x,1q,24,11,6,1d,7,1g,1r,s,9,14,a,7,2,d,x,x,3r,2,4,g,t,18,1c,o,2a,4,10,6,c,6,2,8,17,c,n,16,2j,c,g,c,1,1,1g,1o,j,6,27,r,5,4,b,17,g,5,2,z,c,6,2l,i,c,1p,1,q,13,1r,t,8,9,20,l,r,k,z,9,a,7,p,2o,8,r,7,1,2,z,a,a,1f,6,o,1,1q,10,20,33,v,a,f,o,l,10,j,a,9,c,k,1h,m,55,1k,3,23,u,1q,26,n,l,1i,7,z,3,f,1z,m,8,1j,11,k,6,23,m,j,4e,3,9,s,10,d,6,i,7,j,w,1,d,1e,5q,l,21,k,1z,12,1e,7,f,i,k,5,3f,1f,l,f,1v,4,v,8,1a,2c,8,4,2u,a,j,11,2c,z,c,3d,c,1,6,l,5,2,2,a,7,2s,8,1c,a,i,a|i,s,s,13,7,p,1e,5,6,f,3,1h,b,j,f,9,o,e,m,3,18,r,u,31,4,g,4,1r,1y,m,e,2t,4,10,9,25,o,a,i,28,n,5,o,g,19,4,2,s,13,n,2,2k,o,2,j,i,a,z,u,1a,h,b,e,l,3i,j,1m,1,6,h,1f,9,17,2k,1j,i,13,2q,8,c,6,d,4,v,5,9,3,5,6,d,5,n,2w,b,f,8,2,g,l,q,w,s,m,2,2m,e,14,u,1k,r,2,1,a,1c,1l,f,1j,1,t,a,2a,3,4,m,j,p,h,8,18,1n,9,11,a,y,4,p,s,1i,k,4,t,7,w,8,1,t,2,n,1,2g,y,1l,b,3,3,2,5,8,9,10,1,n,7,k,s,b,2b,3,a,g,v,a,k,c,r,1b,13,a,c,d,t,5,h,5,2,z,11,s,4,1f,z,1y,4,1,x,o,h,4,7,i,1o,d,c,k,9,1l,p,3,s,u,2o,1z,3,7,s,9,1,6,d,d,6,n,c,7,9,2,6,13,2q,12,y,j,19,u,5,4,r,a,o,i,1,19,1,a,k,1,5,7,f,v,k,g,5,14,4,k,8,10,c,b,2,10,14,3,1n,1g,w,2p,4,1s,1d,i,l,16,6,9,6,b,g,r,j,4,9,3,4,v,6,q,s,11,v,c,u,13,1b,2,k,2f,5,47,g,1g,12,9,8,5,w,h,5,m,h,16,u,3,1,u,8,g,1z,f,g,27,p,2e,4,8,a,4,11,u,t,o,13,c,3,2b,d,1h,2,1h,r,y,o,9,7,3,2e,1i,h,l,1a,a,k,k,26,2,s,3,1o,p,y,v,b,4,m,24,z,2,d,u,1d,7,e,1c,t,n,7,3,5,k,d,l,8,5,e,t,c,30,g,2,1,1t,p,r,c,9,5,8,x,4,3,9,5,2,b,v,c,z,a,4,1t,g,b,9,a,p,6,l,k,3,v,9,7,3,17,5,w,11,o,14,g,7,a,3f,3,1q,9,1b,17,2,16,s,v,1,x|6,b,2,h,15,13,q,16,p,12,e,w,l,1g,u,g,n,e,a,5,l,4,3,s,e,10,9,2,8,9,f,q,3,1z,x,12,2f,l,4,f,7,p,n,f,h,e,9,9,3,3,j,8,1,15,9,v,r,1,5,11,1m,m,2,17,2,g,1,3,2,13,k,e,6,2,7,1d,k,7,3,m,8,3,12,2,1,g,2j,9,b,5,9,g,3,1,l,c,5,3,y,3,m,p,h,1,5,e,1,r,17,1f,6,3o,6,e,4,13,t,8,a,n,5,a,i,f,5,1s,3,4,5,9,n,1j,3,n,l,k,2,k,u,m,5,3,1h,c,5,z,14,b,2,1g,5,3,3,l,6,4,l,16,10,r,r,c,a,8,3u,10,1v,e,7,k,l,e,a,1,7,2,k,k,j,d,3,4,3,q,a,6,p,7,2,l,9,1j,1k,e,m,a,h,f,16,1v,9,k,w,r,k,2,1,g,j,4,c,4,r,1c,5,5,1m,7,e,d,5,1,1,v,9,7,11,g,4,1h,5,4,c,3,v,9,9,9,4,b,7,4,p,2,5,e,2,i,2,12,5,4,y,1a,j,3,t,1g,h,1k,s,1c,9,h,d,b,d,8,6,j,e,q,l,h,m,8,1j,1,p,1j,6,8,4,1v,6,r,1,b,4,2,3,14,j,7,1z,v,1m,2,2,13,e,1d,10,e,4,o,2,b,c,s,d,u,1h,m,2,3,d,s,7,5,11,h,e,u,1u,8,9,1k,10,23,7,9,g,9,1p,1p,7,17,9,o,5,12,17,2,g,e,1b,9,e,3,9,b,1q,c,1k,h,a,c,8,5,15,p,a,12,d,g,e,1k,a,27,c,c,1v,m,8,e,o,f,2d,1,l,t,b,1l,6,3,1e,3,9,9,3,8,k,g,m,5,r,8,14,8,5,s,6,t,e,4,5,d,2,k,m,p,c,3,c,g,c,c,1g,s,p,1f,1,9,b,4,s,1,b,e,l,5,4,g,a,2,6,15,j,7,2,2,1f,3,1o,u,1f,13,q,1l,d,y,d,5,a,5,r,6,9,9,e,z,d,v,h,6,17,1h,4,c,q,1,2,7,8,19,1,m,24,b,15,y,z,j,q,3,7,x,f,5,h,1,12,6,l,8,b,m,7,11,3,d,3,q,m,d,o,n,2x,o,1u,s,1,16,j,a,w,6,q,7,o,3,25,3,1,1,q,8,9,g,3,12,27,3,f,h,f,1,2,3,22,7,d,8,y,8,z,3,1e,4,3|4,t,r,n,l,b,8,t,4,8,5,f,12,4,1,2,b,15,4,4,8,1,5,k,3,1,g,1,10,k,11,g,9,11,2,3,7,i,2,6,9,q,2,d,5,5,b,2h,d,f,1i,c,k,1g,3,9,r,1d,3,7,6,c,1,o,5,17,7,p,17,4,8,9,f,6,6,k,20,x,a,d,2,l,w,f,4,8,c,h,m,h,9,c,o,7,m,f,q,r,1l,m,6,1,n,9,w,18,h,v,3,21,19,4,c,c,4,4,d,g,5,4,6,y,9,6,1,c,9,1,y,v,7,f,i,l,4,11,17,e,u,c,j,g,n,1s,4,4,9,9,5,n,j,h,g,4,8,s,p,g,2,u,3,a,f,2,1f,e,h,r,5,a,6,5,10,9,m,1,q,e,e,28,5,i,1c,z,1,1,2,16,5,t,j,u,7,3,i,8,4,d,3,f,s,7,6,1j,2,10,j,5,2,c,1b,9,a,1,2,b,5,c,1n,1j,i,a,4,c,7,8,w,g,f,4,d,7,z,i,6,7,7,2,s,o,t,19,18,t,7,6,e,18,k,e,2,1b,1i,i,26,16,2b,c,5,16,a,z,1w,1i,p,w,t,8,d,8,b,16,2,r,2,3,5,6,4,u,1w,u,a,2,19,5,8,7,4,21,4,2a,g,3m,a,b,1e,11,1,1a,19,o,a,5,6,a,5,u,d,53,27,e,11,m,7,6,f,x,b,7,7,h,c,5,2q,k,r,f,1i,4,11,3,6,1,i,r,11,5,m,2e,1,8,7,h,1n,6,1c,f,b,4,9,s,s,2,1f,14,d,v,t,9,b,b,a,7,4,8,q,2,i,l,9,1b,17,i,g,j,19,3,8,3d,r,1,2,6,12,k,9,z,m,1q,12,7,8,3,c,8,6,19,12,k,h,18,u,1,o,d,r,c,k,g,a,3,8,o,4,a,a,7,6,6,2,f,f,1x,4,1z,f,2,1g,9,7,1c,4,4,5,o,h,8,p,9,1,c,1g,1,1m,5,1,z,4,9,20,e,d,1,1t,1,g,1g,z,f,a,j,1i,3,i,12,2,1,1h,i,1,16,9,8,1,3,6,4,5,l,x,w,3,v,2,o,g,g,c,7,1,g,5,o,c,g,b,s,2,17,1,t,1e,s,c,t,5,7,d,10,2b,o,3,8,i,f,h,5,9,w,h,1i,o,p,5,17,4,x,h,28,3,15,1,k,2,5,6,a,h,f,27,f,4,w,4,c,r,2,p,7,q,1",
 "random": "6i,15,1p,dg,8e,3c,2u,p,3f,3c,15,3d,2o,u,1p,2q,4z,t,5l,2x,54,19,3s,22,2a,d,9e,3a,22,a,3,30,34,19,3,7u,4g,2d,z,1q,2z,3c,5,21,27,1f,x,1a,1t,3,5p,3,2e,45,3j,28,4f,63,3j,15,9t,d,12,b6,f,b,b,l,s,t,1y,5,1r,2k,47,k,3y,3u,1j,18,1j,g,6d,34,26,61,1y,3s,f,j,1j,21,y,d,46,s,22,29,bd,q,b,c,u,2q,1y,d5,h,1t,1n,4s,22,5|al,8h,6c,q,5i,g,2h,2s,1r,4t,y,b,u,j,1l,90,y,3t,15,56,2s,2f,46,40,2q,1,6z,3p,2g,8,f,v,1q,11,6j,1l,1,s,v,2i,a,z,6e,2,1h,r,s,8a,7,2u,7,a,o,16,9e,16,21,bv,16,1m,2x,67,1g,58,3c,1r,1y,i,24,1o,2l,1t,ak,h,8a,1w,4o,g,1w,1x,5,6l,2s,4,99,7,25,6,r,9b,2l,28,3m,i,1d,bq,2o,2d,1q,1d,9,2c,3f,61,4r|f,7,2a,1k,25,5h,e,1j,2,m,t,39,6s,c,y,6t,3o,1b,2p,bu,5,b7,y,y,1y,c,a,1m,28,g,4a,c,e,5b,8d,3,4e,4s,7,1h,6,z,6n,10,4m,6i,p,1p,24,c,1p,1f,64,63,6w,1k,v,p,1g,1j,1x,22,1i,r,4,2d,2s,4s,44,c,3,1f,2v,1u,6,1g,23,k,4,a,2s,6w,69,4f,7p,1o,4l,6h,d1,4a,b,1f,6e,5l,4y,1d,p,2u,3s,1y,o,j,1r,2b,7,2d,1t,4g,4a,1s,2w,5b|z,9,9s,ay,bu,58,4b,51,2e,1c,n,3t,26,24,15,7s,6f,1m,x,1t,80,23,40,70,11,15,1u,1,6d,2z,12,s,4o,a,38,s,5b,1c,42,4n,1v,p,4y,3j,p,43,1d,14,h,1t,t,1i,18,12,2q,3,e,5h,v,1u,5,2v,28,j,7d,1a,p,1y,r,1m,1r,g,1u,j,43,b,1d,34,2f,17,21,3r,r,q,49,2r,4,4k,g,4e,i,6,2x,g,e,v,3k,49,73,w,1c,1f,o,26,1i,13,y,h,ap,2o,m,5p,4w,s,57,8|2m,9,65,1v,29,24,2,46,j,c,c,w,5m,5,o,9,1t,51,4z,4b,54,1p,1t,4r,s,8n,ag,5,1x,ce,6s,4c,1e,48,6d,2c,2b,3v,19,1u,2z,f,h,8,5o,8l,5j,5e,6,1x,2f,c,48,3b,1t,1,1k,26,22,6,v,17,2z,b,2a,27,f,7,p,19,4p,4c,p,1c,9,i,4d,37,2m,2b,j,89,13,2q,1q,9s,r,b7,9,8,2v,1f,6q,3,4f,3q,44,4e,1f,8d,14,4,3l,6v,1v,3g,x,b,2|2k,34,d,x,3o,o,7d,5,3f,1k,1c,a0,3o,20,1m,7b,3h,3i,2i,1u,2b,3y,1r,71,2y,bh,1v,2l,4,9,1d,j,1d,32,1n,3z,7o,8o,3i,5i,3p,c,1j,13,14,2q,1k,3k,fj,4m,7k,14,11,1m,73,11,c,1o,87,7j,18,5w,6,16,24,z,9e,1x,29,a6,75,6h,25,63,p,8,61,19,8f,4d,26,4o,1m,5,4m,5s,2e|6,l,4y,3u,t,17,r,b5,18,20,g,29,4m,2,5,6i,32,1g,1w,3t,13,24,x,3w,75,1m,6,47,3,4n,23,q,2x,36,t,4b,3z,1c,2q,o,22,x,8,1k,3,23,1d,22,45,6p,8a,3z,1p,1e,2o,3j,5f,c,c,1h,3,1r,2,3b,r,48,15,3u,4b,1s,f,1s,5i,7,3n,1d,q,3t,4v,9,b,50,l,55,4,10,1v,3n,1g,1e,m,38,15,29,44,l,5,k,2g,36,n,3,11,1c,3d,3,5n,cj,1l,r,2k,x,7b,89,1y,42,1a,z,2x,1i,7e,1k,c,8,3f,c|31,43,6p,84,2u,4,s,1q,4,s,5f,1c,62,p,3k,m,2,33,2h,t,i,1k,64,42,1t,2j,d,1n,49,3d,1b,2k,20,g,3a,9b,v,34,1f,3,m,n,52,1c,2r,17,42,72,1n,7,1b,40,t,a,5x,7,3,3u,14,5v,1h,7,2b,2l,47,v,38,6i,16,l,1t,1i,v,5n,96,25,o,3w,b,1s,25,1o,3a,i,3g,28,4,19,6o,2t,2x,y,2y,99,1d,5,2a,36,q,1c,61,dc,5k,3o,3l,1g,2d,2x,f1,m|l,p,x,9,2j,10,4r,4o,3,18,d,29,4k,34,4c,1i,4b,9,69,7x,1z,l,g,1,y,79,c,o,9,3c,2o,1v,1b,46,5,c,2k,z,1q,1t,6a,g,q,1p,45,56,89,38,1w,8,i,2z,u,1w,2c,3i,3d,13,1y,e,18,1l,1y,1q,g,2g,1s,7r,i,5h,4u,11,1u,b,1k,34,11,9y,l,y,3v,17,18,w,3,6k,18,4y,4p,8,9s,3k,25,1,10,11,23,1b,6i,2v,13,17,6z,c,5n,j,d,1j,1h,1s,6u,4i,fa,9,40,2r,i,32,2r,3p|2n,1y,1j,7,m,a,1v,2g,2w,4e,3i,22,17,g,1d,28,p,17,m,l,8,59,3y,3m,64,4a,s,i,2u,1q,s,m,16,m,11,1n,2k,x,5,f,5r,2a,1s,48,22,2m,1i,5z,b,18,1y,28,2q,1x,78,x,39,2w,3z,27,4v,13,36,3k,c,37,2u,4c,83,x,y,3b,q,3v,3t,am,28,1s,31,19,22,4s,7u,8,1y,j,8,1n,h,9,2j,5x,5g,7,i,24,2u,g,18,n0,a,11,2a,2g,x,55,gm,5z,21,15,4j,13,e,t|f,1w,1k,l,39,1w,x,2k,42,e,2w,8,31,11,5i,5l,9d,1,1b,2q,2g,1d,2g,29,6f,3v,30,1m,1a,61,3q,1e,53,dw,10,a,1u,2x,2,4o,47,3m,m,19,25,s,1r,5f,2i,82,90,11,e,1t,3,5n,1v,43,4y,1k,1w,1u,2w,25,1i,3h,v,1j,1u,2n,a,1s,1o,2t,7v,l,f,14,8,2r,47,h,2g,13,m,2f,48,1q,5f,4,13,3g,a,f,3k,21,9,2o,j,13,2y,2d,n,70,t,1l,1m,3q,13,10,8,2r,3r,b,1e,4x,1r,1v,9k|ad,23,2e,3q,1i,a7,23,4x,f,13,36,1g,21,5m,1n,9,19,a5,18,2d,2h,16,11,eh,2k,dq,2f,x,1u,19,4,21,1i,6r,2,3y,l,a,3o,i,39,16,70,1l,n,34,u,36,2q,2r,36,43,49,1k,5v,5n,2t,3p,1r,1k,k,1b,t,9,8c,1o,30,40,p,85,32,44,2d,35,1h,40,b,9t,1t,3,1j,q,24,1v,4j,q,35,7,i,1j,1o,m,1d,2t,4q,37,2f,46,1x,2w,t,4z,2v|43,3j,4t,1v,16,o,42,5,41,y,g,1w,c,2,h,d,3u,53,1u,20,h,2a,a,1k,1q,j,j,62,6,51,n,7,7e,4c,2t,1s,3g,12,2c,5z,17,28,7b,8,33,28,t,1j,6,r,4p,16,4n,6e,8g,2a,56,1i,4m,2f,2,1a,45,1a,38,3f,n,2i,4l,1,s,31,e,s,r,60,4j,a,1j,6v,3l,6,6s,2,2q,k,1f,9p,e,5b,1u,s,19,4h,1f,p,73,71,q,x,3i,1j,1n,41,5a,20,37,3t,2r,3v,38,a,27,4k,g,1z,2i,1t|1,1x,45,g,4l,15,1j,7,9,4s,6,7,8,2y,2k,7,6j,q,4p,1v,t,3j,46,1t,v,69,50,h,e,4l,m,6w,i,5h,20,32,4,44,1t,49,12,f,3c,32,22,3s,x,z,q,9,3b,2o,85,18,9,6v,20,6n,j,28,r,8q,1v,1b,c,1v,11,h,16,8c,18,55,17,7l,e,34,12,20,1j,67,i,7i,1m,8k,1a,5h,56,d,17,o,5b,2e,17,g,43,x,5m,13,2,6j,14,1l,6r,25,28,4o,4f,2g,2y,7r,27,6,4k|4v,1i,x,e,76,z,l,7z,6r,v,4a,1o,4t,4m,2s,3u,6v,5,2o,7,4l,1l,4d,x,3u,12,1g,6,1d,3w,4k,4g,2j,13,v,d,f,70,15,8,7k,1v,50,64,25,1k,7,18,3i,28,3v,s,c,5k,2,c,66,24,1c,1i,b,s,4s,2h,1r,1n,2g,d,5p,j,2n,66,8,46,28,21,f,1y,18,44,e,9m,b,1o,1y,o,i,2s,9m,2l,2c,5r,1t,be,6,5d,71,5,u,4v,26,5e,6o,1g,37,54,1u|2e,4d,27,2y,3x,g,2l,8y,4w,v,4,7q,1u,l,3v,u,2t,iw,y,d,t,u,w,96,g,68,2s,5l,2k,9f,4h,1d,a,3v,s,3t,66,3p,1s,1v,5s,1s,2g,v,6,10,5n,2h,1b,y,2,ai,1b,5t,x,bn,2b,18,s,7x,3k,16,3a,1k,a8,2s,1p,3s,l,a,12,bd,y,2m,38,9,3,9,22,b,39,1,2s,c,35,v,3x,5,5g,4j,1,98,u,85,t,k,23,22,1n|1a,13,j,3,84,1h,28,14,1n,w,dp,5t,82,e,e,1,86,45,4h,8o,1o,1o,4g,40,20,z,7z,d,11,w,57,b2,8j,h,46,2w,24,4z,4e,2e,2,8,2i,1,26,8,37,d,2w,24,28,d,1y,1x,1j,bs,19,3,5,2,e,f,2u,o,5l,51,d,7n,d,d,1z,c,2a,3,h,31,15,o,2t,5m,1t,f,5s,4m,1s,2h,39,z,c,4,1p,2i,1f,1d,w,5f,2n,4b,1u,23,3p,1l,40,ad,2c,g,2x,m,2c,o,4a,s,4,4|7d,75,7x,1n,2r,m,m,e,2q,7d,2p,m,2z,2r,2,38,f,21,6e,1l,6,45,7f,1d,10,3r,5g,43,4r,10,1u,1e,1d,x,h,1b,1r,1g,1e,i,2,34,5v,k,9,l,1a,2g,3q,2g,17,b,2l,1c,8r,w,19,28,o,44,7l,46,84,l,14,3e,25,5,c,4g,39,5k,5m,4,27,4y,37,2,1y,2s,1g,1w,u,7b,1r,2c,6,w,b1,1g,3v,k,1r,1,2a,de,1f,54,12,40,31,n,1e,2p,8r,24,3b,m,3s,15,t,17|t,2e,20,21,3p,1a,6,3c,9v,5,16,i,32,3w,ha,y,5e,n,32,1z,n,36,2q,1u,11,1l,1w,b,3g,3s,4,1w,50,3z,1j,26,2a,g,7z,4b,2b,t,2r,4l,z,3,20,a5,75,31,2c,i,2s,1u,k,2b,7,34,1,2n,22,32,1h,18,2l,12,4,e,e,19,al,1q,v,4v,5b,1,8,1l,f,4j,25,1t,43,2a,3z,1d,1b,3g,26,az,l,q,9,61,10,c,37,8,3y,2i,3y,a6,6t,p,8u,b,r,2p,h,1w,4,7,36,1g,i,s|2u,f,4x,w,24,4e,1y,y,4,v,1q,u,1o,8,n,1s,18,1i,y,35,1k,v,i,5,2k,1f,25,c1,1e,3,7,1h,4x,24,j,au,1k,3j,6,f,v,4t,1x,6f,31,s,9f,2h,21,2z,w,29,6u,3,1m,1t,13,2s,s,3s,11,36,1k,1q,1z,36,1d,1k,6c,54,19,1m,1h,16,5p,4y,c,2w,q,11,h,31,2m,4n,21,25,14,45,6p,1,8h,3,4y,2c,2i,3n,1c,46,10,1k,1x,36,1t,j,nx,2z,6n,2m,3x,x,e,a0,3,15,1o|8v,p,5d,1e,1s,7f,1e,8,1a,4z,5z,3o,p,f,40,18,1z,49,4t,d,52,2m,11,g,55,2h,6b,3j,b,22,10,3z,7a,6,3,bj,d9,5k,n,11,e,b5,i,4b,x,9t,2o,20,2,1y,4q,5,1n,h,10,27,5s,c4,e,5f,1n,42,3r,42,21,2x,t,28,7,16,2c,fb,x,7n,t,2d,8,2k,u,8,38,20,52,4c,4,3y,5,7i,2w,1m,h,o,1z,1i,2c,16,2x,17,2e,z|4b,4,2g,11,1n,1e,4,d,3,ay,5o,25,41,15,8h,15,4s,e,d,13,v,2,7c,1u,1u,2i,5w,3m,7m,26,3p,1f,78,24,11,d1,y,l,1r,4p,40,1d,32,1w,q,15,4l,5z,1g,n,1w,3d,3a,1m,3b,7r,i,1j,3l,5o,5h,1m,a6,1z,m,h,5f,42,36,20,2e,1k,1d,3a,51,29,2,5w,29,6m,k,68,4r,y,b,16,2b,d2,em,2g,2x,87,z,d,3,t,11,a|24,2r,u,16,17,3m,js,7m,j,3e,p,25,1p,23,z,2y,8,5b,o,33,c,n,2n,e,4q,5,2j,2q,7q,2,35,19,28,4r,1l,4d,4k,r,1i,30,11,2r,f,6,43,1z,8,5o,1z,l,2a,22,x,38,3j,p,47,3c,5e,5,1m,5p,23,1l,6y,53,32,2n,9,l,x,c,2,1k,3c,6d,a,4a,23,1h,1j,3j,h,i,3g,34,32,13,1m,3,69,u,c,y,1h,39,5w,1g,43,3j,9,57,81,8m,2n,2i,7,b,8k,5m,r,3x,1i|18,19,a,1w,22,3i,36,44,az,2t,i,7,1k,32,24,2a,37,24,1v,3,2x,46,1m,5r,4n,8o,2h,12,e,9f,5f,19,16,2i,2j,22,4t,33,5,2z,u,d,1s,1c,48,3d,48,5,3n,1f,16,2m,64,1z,by,6t,f,5q,2u,d,4n,h4,75,2a,2n,3d,2q,2f,2u,c,2s,l,1g,2r,z,1h,f,1,23,e,y,l,1b,f,o,s,h,14,2r,51,1r,16,q,l,1j,31,2c,61,1r,1u,18,1b,7e,i,4c,5k,39,i,1p,93|17,fc,10,77,1v,19,as,67,1j,e,9t,o,1p,37,1p,3c,d,1y,x,5g,1q,3d,10,53,c,1u,1,2v,2m,2g,1v,1n,7h,3,4k,w,1,1,9,31,h,2t,43,3i,1r,1f,z,p,51,2c,1t,1e,21,n,1b,10,4f,2,k,38,2w,1e,1j,1z,13,2w,k,u,7s,10,1h,2g,8,1c,x,2n,4x,1b,d,28,e,14,8g,6m,ch,b,8,2a,11,56,22,d3,1c,1o,7o,8,25,26,2q,27,12,br,cy,1k,7,1k,6h,r|5e,6f,1v,1c,22,1p,s,5g,9z,1o,1b,55,8k,25,5j,o,2y,7t,d,2f,2y,e,2h,3o,4v,g,7,21,8c,2t,q,1e,d,10,a6,18,2,2w,3z,4y,22,5,34,17,9,7u,1o,a3,f,2d,i,92,1l,1d,c,l,3n,4o,37,2i,1t,2b,q,63,2o,3n,5,1a,a,1o,6a,39,3y,4,3u,1l,2r,a,3f,2s,31,u,6,1,3y,d5,b,9n,8j,l,k,22,6q,1z,58,l,38,g,2r,m,f,27,1,1a|9,q,m,3j,19,6m,46,30,64,p,7d,4t,hd,1v,60,1g,b,am,19,b,4d,u,6p,3c,2w,1s,3a,j,21,2,24,5f,2,1h,c,g,fl,1l,10,1o,5k,1b,12,2g,21,25,1k,b4,6v,e,3m,1d,7c,3c,1p,2s,q,28,2l,1r,1o,49,w,1q,24,34,2m,1s,34,26,40,19,3n,45,1o,16,17,c,49,i,4s,1m,4,1s,1e,g,bi,6,c,b,49,i,3f,3x,29,28,18,2a,5,24,1s,2g,2i,6,3,20,2g,2u,8|3h,18,49,1h,i,1p,2n,2m,4d,x,3,1z,9,1s,18,2a,1n,5j,4b,4y,25,5i,l,6s,2k,h,z,2g,b,1x,y,a6,2m,1l,26,y,12,w,o,e,18,u,u,h,f,ge,2a,2f,6l,11,3s,5j,1v,11,2n,3q,ap,p,4u,2p,15,5,e,w,30,1l,1y,2i,3b,4l,3a,m,b,35,7i,2t,2j,8p,6q,6b,3x,1u,1u,1o,2z,3a,dh,20,c,31,1l,e,4h,4,27,2l,f,2a,1k,39,16,43,39,3,1e,22,59,3i,47,21,1t|47,3u,7,k,16,17,x,10,3i,2h,1r,36,33,54,34,1l,h,26,38,3y,3m,8,25,d,1a,2x,r,2g,2a,7,4a,2t,2s,23,76,32,c4,c,39,k,53,br,5l,1w,29,25,x,n,55,1j,1g,4p,3x,4h,a,3z,3n,16,6l,1,15,dr,14,n,8,36,10,9,7,5i,1a,3,4m,2a,1q,4f,16,5c,32,1t,2a,7t,9k,3s,65,21,3o,43,1v,17,2x,1c,1u,5,u,cf,3w,27,4v,n,l,22|u,2l,y,n,5b,2x,1p,ax,5f,z,1y,d,1y,24,4w,36,64,2n,2g,14,24,3a,5,2d,47,1j,17,1f,1h,6,26,2r,8l,3z,11,n,t,97,s,y,6,b,7,1x,3r,16,r,2z,9u,7,1j,5,3h,4s,1m,1r,3m,1u,d,4y,1g,3,3t,u,22,2v,3,1j,2p,r,4m,2m,1q,1z,2m,22,2a,49,3z,3m,j,e,1w,u,39,3j,2n,1r,8b,m,35,ab,ch,4c,2t,10,4m,17,1w,w,e0,6,3h,7k,17,21,1o,w,k,23,1p,4e,n|17,15,1z,2f,4o,69,27,6m,6t,d,8a,1f,b,1,1j,m,1o,3c,i,4n,e,3o,1t,5,2,1h,1d,o,1z,1o,y,2d,33,3,z,1d,x,65,1l,2n,5b,j,e,u,33,1r,a6,2w,2a,26,2k,3e,q,5r,1t,s,gc,4v,50,j,2e,22,97,b,5p,5,9,8v,49,d,5,4y,3b,11,6,7,9,37,28,6g,5,t,1v,60,o,96,3y,4e,8e,1i,cu,1v,18,12,o,9f,1u,7,2x,4w,1h,1z,78,11,17,v,2d,5|c,2h,2o,y,5,p,3s,2e,2,57,3h,41,1d,1l,2a,9,3m,1o,2t,6x,k,i,z,1i,6n,2w,1e,55,3t,u,1,1r,k,n,l,4,1x,o,4r,1z,4y,1x,3e,3w,1n,6,5,1f,1j,80,63,k,2f,10,cs,43,t,2d,2q,3m,21,k,37,1m,35,2f,2u,14,20,26,42,55,2c,5i,3t,g,x,2i,3b,5l,4n,22,2r,11,5,ba,2e,7,1w,7,61,1z,y,g,3z,21,14,1n,1b,26,2,1z,42,2l,l,3b,2,y,61,1p,9a,17,3c,x,4l,2e,1o,10,5o,j",
 "top100": "34j,3o3|28m,5ox|209,bz,3i8,1wi|3z1,1zc|3p3,1ku,lk,go|2m3,5m,g9,1p2,2x8|dy,t5,2nc,1hx,q6,20o|63t,1a9|sp,r8,19s,1vg,2pt|bu,7e,ka,4g8,b1,k4|25,9,1kf,3ge,iw,wv,sw|2qj,1n2,52,13l,f4,2d,1jf|1u4,2jq,1av,20h|1zm,1jo,3ag,1ex|5sq,b|5hj,2m6|4wf|2to,a7,lb|t1,7eu|3z5,47r|8cb|3x5|6hl|4zv||iw|6ie|2df||219,ya,2xb,1zb|hu,3qa,3ol,dg|1hp,76,1t,fo,c,1n6,3b,mg,uy,jk,6w,3,2s"
}


def _encode(edit):
    out = []
    for layer in range(DATA["layers"]):
        prev, parts = 0, []
        for n in sorted(edit["copy_neurons"].get(str(layer), [])):
            d, s = n - prev, ""
            prev = n
            while True:
                d, r = divmod(d, 36)
                s = "0123456789abcdefghijklmnopqrstuvwxyz"[r] + s
                if not d:
                    break
            parts.append(s)
        out.append(",".join(parts))
    return "|".join(out)


def _build():  # SETS from the edit files; run from the repository root
    return {k: _encode(json.load(open(p))) for k, p in DATA["sets"].items()}


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Invariant: __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap">
<style>
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table
   with a cast shadow in place of the glow. The light comes from the upper left in both. A neuron copied from RL is lit
   (blue); every other neuron is a faint dot of ink. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --dot: 16, 24, 32; --dot-a: .17; --well: rgba(16, 24, 32, .045);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --dot: 201, 211, 218; --dot-a: .15; --well: rgba(0, 0, 0, .28);
  }
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 400 15px/1.5 "Archivo", ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased;
}
button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: left; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 3px; border-radius: 3px; }
.page {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 27vw); grid-template-rows: auto minmax(0, 1fr);
  gap: 0; height: 100vh; min-height: 640px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: one plate seen from slightly above, swaying a few degrees; a back face gives it depth */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 8px 40px 0 0; }
.scene { width: min(100%, 1060px); perspective: 2200px; }
.body { position: relative; transform-style: preserve-3d; }
div.back, .plate { border-radius: 28px; }
div.back { position: absolute; inset: 0; transform: translateZ(-38px); background: var(--glass-lo); border: 1px solid var(--rim-b); }
div.back::before, div.back::after { content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; }
div.back::before { opacity: var(--glow); box-shadow: 0 0 130px 8px color-mix(in srgb, var(--blue) 20%, transparent); }
div.back::after { opacity: var(--shadow); box-shadow: 18px 36px 70px -14px color-mix(in srgb, var(--ink) 24%, transparent); }
.plate {
  position: relative; overflow: hidden; display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(250px, 1fr); gap: 0 40px;
  padding: 30px 38px 26px; border: 1.7px solid transparent;
  background: radial-gradient(120% 120% at 28% 18%, var(--glass-hi), var(--glass) 46%, var(--glass-lo)) padding-box,
              linear-gradient(140deg, var(--rim-a), var(--rim-b) 56%, var(--rim-c)) border-box;
}
.spec { position: absolute; left: -4%; top: -18%; width: 58%; height: 56%; transform: rotate(-20deg); opacity: var(--spec); pointer-events: none;
  background: radial-gradient(closest-side, rgba(255, 255, 255, .12), rgba(255, 255, 255, 0)); }
.cap { position: relative; margin: 0 0 10px; font-size: 13.5px; color: var(--mute); }
.cap b { color: var(--blue); font-weight: 640; }
.fieldbox { position: relative; display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 0 10px; }
.ly { display: flex; flex-direction: column; justify-content: space-between; font-size: 12px; color: var(--faint); text-align: right; padding: 0; }
.field { position: relative; height: clamp(250px, 46vh, 430px); border-radius: 10px; background: var(--well); cursor: pointer; touch-action: pan-y; }
.field:focus:not(:focus-visible) { outline: none; }
.field canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; pointer-events: none; }
.row { position: absolute; left: -4px; right: -4px; border: 1.5px solid var(--ink); border-radius: 4px; pointer-events: none; opacity: 0; transition: opacity .2s ease; }
.row.on { opacity: .85; }

/* The one control: the share of neurons copied from RL */
.slide { position: relative; margin: 18px 0 0; padding-left: 0; }
.slide label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 4px; }
.slide label span { color: var(--mute); font-weight: 450; }
input[type=range] { -webkit-appearance: none; appearance: none; width: 100%; height: 36px; margin: 0; background: none; cursor: pointer; touch-action: pan-y; }
input[type=range]:focus { outline: none; }
input[type=range]::-webkit-slider-runnable-track { height: 3px; border-radius: 2px; background: linear-gradient(90deg, var(--blue) var(--p, 40%), color-mix(in srgb, var(--faint) 45%, transparent) var(--p, 40%)); }
input[type=range]::-moz-range-track { height: 3px; border-radius: 2px; background: color-mix(in srgb, var(--faint) 45%, transparent); }
input[type=range]::-moz-range-progress { height: 3px; background: var(--blue); }
input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 24px; height: 24px; margin-top: -10.5px; border-radius: 50%; background: radial-gradient(circle at 34% 30%, color-mix(in oklch, var(--blue), white 45%), var(--blue)); border: 2px solid var(--sheet); box-shadow: 0 0 0 6px color-mix(in srgb, var(--blue) calc(var(--bloom) * 22%), transparent); }
input[type=range]::-moz-range-thumb { width: 22px; height: 22px; border-radius: 50%; background: var(--blue); border: 2px solid var(--sheet); }
input[type=range]:focus-visible::-webkit-slider-thumb { outline: 2px solid var(--ink); outline-offset: 3px; }
input[type=range]:focus-visible::-moz-range-thumb { outline: 2px solid var(--ink); outline-offset: 3px; }
.ticks { position: relative; height: 22px; font-size: 13px; color: var(--faint); }
.ticks button { position: absolute; top: 0; transform: translateX(-50%); padding: 0 4px; font-weight: 520; white-space: nowrap; }
.ticks button:hover { color: var(--ink); }
.ticks button.on { color: var(--ink); font-weight: 700; }

/* The number and its curve */
.read { position: relative; display: flex; flex-direction: column; min-width: 0; }
.rlab { margin: 22px 0 0; font-size: 15px; font-weight: 600; line-height: 1.35; min-height: 2.7em; }
.rlab span { display: block; color: var(--mute); font-weight: 450; font-size: 13.5px; }
.big { margin: 2px 0 0; font-size: clamp(64px, 6.67vw, 112px); line-height: .98; font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; white-space: nowrap; }
.big small { font-size: .5em; font-weight: 560; letter-spacing: 0; margin-left: .08em; }
.blab { margin: 8px 0 0; font-size: 15.5px; line-height: 1.35; color: var(--ink); font-weight: 500; max-width: 30ch; }
.base { margin: 10px 0 0; font-size: 13.5px; color: var(--mute); line-height: 1.5; }
.base b { color: var(--ink); font-weight: 620; white-space: nowrap; }
.chart { flex: 1; display: flex; flex-direction: column; min-height: 210px; padding-top: 40px; }
.chart svg { width: 100%; flex: 1; min-height: 0; display: block; overflow: visible; }
.legend { display: flex; flex-wrap: wrap; gap: 4px 14px; margin: 8px 0 0 0; font-size: 12px; color: var(--mute); }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.legend span::before { content: ""; width: 16px; height: 0; border-top: 1.4px solid var(--faint); }
.legend span.on { color: var(--blue); font-weight: 640; }
.legend span.on::before { border-top: 2.6px solid var(--blue); }
.chart text { font-family: inherit; font-size: 12px; fill: var(--mute); font-stretch: 104%; }
.chart .ttl { fill: var(--ink); font-weight: 600; }
.chart .gl { stroke: var(--rule); stroke-width: 1; }
.chart .ax { stroke: var(--faint); stroke-width: 1; }
.chart .cv { fill: none; stroke: var(--faint); stroke-width: 1.4; stroke-linejoin: round; opacity: .75; }
.chart .cv.on { stroke: var(--blue); stroke-width: 2.6; opacity: 1; }
.chart .pt { fill: var(--blue); stroke: var(--sheet); stroke-width: 2; }
.chart .cl { font-weight: 560; }
.chart .cl.on { fill: var(--blue); font-weight: 680; }

.switch { display: inline-flex; margin-top: 18px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.hint { margin: 10px 0 0; max-width: 64ch; min-height: 2.9em; font-size: 13.5px; color: var(--mute); text-align: center; }

@keyframes rise { from { opacity: 0; transform: translateY(12px); } }
@keyframes fade { from { opacity: 0; } }
.enter .plate { animation: rise .9s cubic-bezier(.3, 0, .2, 1) both; }
.enter div.back { animation: fade 1.3s .2s both; }
.enter .read, .enter .slide { animation: fade .8s .6s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: max(8px, calc(clamp(20px, 7vh, 96px) - 38.5px)) 0 0 40px; border-left: 1px solid var(--rule);
}
a.back { display: inline-block; font-size: 13px; color: var(--mute); padding: 10px 0; margin: -10px 0 6px; text-decoration: none; }
a.back:hover { color: var(--ink); }
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts b { color: var(--ink); font-weight: 620; }
.facts a { color: var(--blue); }
.steps { display: flex; justify-content: space-between; margin-top: 14px; font-size: 13px; color: var(--mute); }
.steps button:hover { color: var(--ink); }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  a.back { order: 0; align-self: flex-start; margin: 14px 0 6px; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .pane { order: 4; margin-top: 26px; }
  .plate { grid-template-columns: minmax(0, 1fr); padding: 18px 16px 18px; border-radius: 22px; }
  div.back { border-radius: 22px; }
  .plate { display: flex; flex-direction: column; }
  .read { display: contents; }
  .rlab { order: 1; margin-top: 0; min-height: 0; }
  .big { order: 2; } .blab { order: 3; } .base { order: 4; }
  .fieldside { order: 5; margin-top: 18px; }
  .chart { order: 6; }
  .big { font-size: 64px; }
  .blab { max-width: none; }
  .field { height: 300px; }
  .chart { min-height: 0; padding-top: 22px; }
  .chart svg { flex: none; height: 180px; }
  .switch { display: flex; width: 100%; }
  .switch { border-radius: 26px; }
  .switch button { flex: 1; text-align: center; padding: 12px 6px; min-height: 44px; font-size: 14px; white-space: normal; line-height: 1.2; border-radius: 22px; }
  .hint { text-align: left; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a, .row { transition: none; }
}
/* When the words are taller than the window the page scrolls as a whole, so nothing is cut; the picture stays in place. */
@media (min-width: 901px) {
  .page { height: auto; min-height: max(100vh, 640px); }
  .stage { align-self: start; height: max(552.5px, calc(100vh - 87.5px)); }
  .side { overflow-y: visible; position: relative; z-index: 1; margin-bottom: -4px; }  /* -4px: a rounding overflow does not make the page scroll */
  .top { position: relative; z-index: 1; }
}
@media (min-width: 901px) and (min-height: 640px) {
  .stage { position: sticky; top: 59.5px; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof">Proof</a>
    <a href="/findings" aria-current="page">Findings</a>
  </header>
  <div class="stage" id="stage">
    <div class="scene" id="scene">
      <div class="body" id="body">
        <div class="back"></div>
        <div class="plate">
          <i class="spec"></i>
          <div class="fieldside">
            <p class="cap" id="cap"></p>
            <div class="fieldbox">
              <div class="ly" aria-hidden="true"><span>Layer 0</span><span>Layer 31</span></div>
              <div class="field" id="field" tabindex="0" role="img">
                <canvas id="dim"></canvas><canvas id="lit"></canvas><div class="row" id="row"></div>
              </div>
            </div>
            <div class="slide">
              <label for="share">Neurons copied from RL into the base <span>(log scale)</span></label>
              <input type="range" id="share" min="0" max="5" step="1" value="2">
              <div class="ticks" id="ticks"></div>
            </div>
          </div>
          <div class="read">
            <p class="rlab" id="rlab"></p>
            <p class="big" id="big" aria-live="polite"></p>
            <p class="blab">of RL's effect on next-word predictions recovered; at 100 % the base would predict exactly like RL</p>
            <p class="base" id="base"></p>
            <div class="chart" id="chart"><svg id="curve" aria-hidden="true"></svg>
              <p class="legend" aria-hidden="true"><span id="lg-effect">Largest effect</span><span id="lg-weight">Weight change</span><span id="lg-random">Random</span></p></div>
          </div>
        </div>
      </div>
    </div>
    <div class="switch" id="switch" role="group" aria-label="How the neurons are chosen">
      <button data-rule="effect" aria-pressed="false">Largest effect</button>
      <button data-rule="weight" aria-pressed="false">Largest weight change</button>
      <button data-rule="random" aria-pressed="false">Random</button>
    </div>
    <p class="hint" id="hint"></p>
  </div>
  <div class="side">
    <a class="back" href="/findings">‹ All findings</a>
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const fmt = n => Math.round(n).toLocaleString("en-US"), pct = v => v.toFixed(1) + " %";
const share = s => (s < 1 ? s.toFixed(1) : String(s)) + " %";
const L = D.layers, W = D.width, N = L * W, STOPS = C.stops, RULES = ["effect", "weight", "random"];
const NAME = { effect: "Largest effect", weight: "Largest weight change", random: "Random" };
const SAY = {
  effect: "Largest effect: neurons ranked by how far copying each one alone moves the base toward RL, on half of the answers; scored on the other half.",
  weight: "Largest weight change: the neurons whose weights RL changed the most.",
  random: "Random: neurons drawn at random, the control."
};

/* The neurons. A neuron is id = layer * W + index. Each rule has an order of all N neurons: the chosen set at a share is
   the first neurons of its order. The order starts with the rule's exact 1 % set from the run (for the largest effect,
   the 100 best first), in a fixed shuffle; then the other neurons, drawn at random with the weight of each layer in that
   1 % set. So the 1 % sets are exact, and the share lit is exact at every step. */
function decode(s) {
  const out = [];
  s.split("|").forEach((part, l) => { let n = 0; if (part) for (const d of part.split(",")) { n += parseInt(d, 36); out.push(l * W + n); } });
  return out;
}
function rng(seed) { return () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function shuffle(a, r) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
const SET = { effect: decode(C.sets.effect), weight: decode(C.sets.weight), random: decode(C.sets.random), top100: decode(C.sets.top100) };
const ORDER = {}, RANK = {};
RULES.forEach((rule, k) => {
  const r = rng(17 + k), head = new Set(SET[rule]), first = rule === "effect" ? new Set(SET.top100) : new Set();
  const per = new Float64Array(L);
  SET[rule].forEach(id => { per[Math.floor(id / W)]++; });
  const rest = [], key = new Float64Array(N);
  for (let id = 0; id < N; id++) if (!head.has(id)) { rest.push(id); key[id] = -Math.log(1 - r()) / (per[Math.floor(id / W)] + .5); }
  rest.sort((a, b) => key[a] - key[b]);
  const order = [...shuffle([...first], r), ...shuffle(SET[rule].filter(id => !first.has(id)), r), ...rest];
  ORDER[rule] = Int32Array.from(order);
  const rank = new Int32Array(N);
  order.forEach((id, i) => { rank[id] = i; });
  RANK[rule] = rank;
});
const count = s => Math.round(N * STOPS[s].share / 100);
const S = { s: 2, rule: "effect", open: null, layer: -1, g: null, from: null, t0: -1e9, n0: 0, n1: 0, shown: -1, last: 0,
  px: 0, py: 0, tx: 0, ty: 0, entered: false };

/* The field: one dot per neuron, one band per layer, layer 0 at the top. Within its layer a neuron has a cell of a fine
   grid and sits at a fixed random place inside that cell, so the field reads as dots and not as stripes; the place has
   no meaning. Drawn in device pixels with ImageData: the faint dots once per layout, the lit dots only where they change.
   A lit dot is a small square with a faint ring around it. */
function layout() {
  const box = $("field"), dpr = Math.min(3, devicePixelRatio || 1), w = Math.round(box.clientWidth * dpr), h = Math.round(box.clientHeight * dpr);
  const gap = Math.max(2, Math.round(2.2 * dpr)), band = Math.floor((h - (L - 1) * gap) / L);
  const cols = Math.ceil(Math.sqrt(W * w / band)), lines = Math.ceil(W / cols), cw = w / cols, chh = band / lines;
  const off = Math.round((h - L * band - (L - 1) * gap) / 2), top = l => l * (band + gap) + off;
  const d = Math.max(1, Math.round(dpr)), r = rng(99), pix = new Int32Array(N);
  for (let l = 0; l < L; l++) for (let n = 0; n < W; n++) {
    const x = Math.min(w - d - 1, Math.floor(((n % cols) + r()) * cw)), y = Math.min(top(l) + band - d, top(l) + Math.floor((Math.floor(n / cols) + r()) * chh));
    pix[l * W + n] = y * w + x;
  }
  S.g = { w, h, dpr, gap, band, d, top, pix };
  ["dim", "lit"].forEach(id => { $(id).width = w; $(id).height = h; });
  colors();
  drawDim();
  drawLit(true);
  placeRow();
}
function colors() {
  const cs = getComputedStyle(document.documentElement), probe = document.createElement("canvas").getContext("2d", { willReadFrequently: true });
  const rgb = v => { probe.fillStyle = v; probe.fillRect(0, 0, 1, 1); const d = probe.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2]]; };
  S.blue = rgb(cs.getPropertyValue("--blue").trim());
  S.dot = cs.getPropertyValue("--dot").split(",").map(Number);
  S.dotA = parseFloat(cs.getPropertyValue("--dot-a"));
}
function drawDim() {
  const g = S.g, ctx = $("dim").getContext("2d"), img = ctx.createImageData(g.w, g.h), px = new Uint32Array(img.data.buffer);
  const [r, gg, b] = S.dot, c = (Math.round(255 * S.dotA) << 24 | b << 16 | gg << 8 | r) >>> 0;
  for (let id = 0; id < N; id++) px[g.pix[id]] = c;
  ctx.putImageData(img, 0, 0);
}
/* Lit state of each neuron at time now: 1 if chosen. During a change, a neuron that turns on or off does so at a time
   given by its place in the order, so the light spreads over about 0.65 s. */
function litAt(id, now) {
  const rank = RANK[S.rule][id], on = rank < S.n1;
  if (!S.from) return on ? 1 : 0;
  const was = S.from.rank[id] < S.from.n;
  if (was === on) return on ? 1 : 0;
  const p = clamp((now - S.t0 - S.delay(id)) / 220, 0, 1);
  return on ? ease(p) : 1 - ease(p);
}
function drawLit(all, now = performance.now()) {
  const g = S.g, ctx = $("lit").getContext("2d");
  if (all || !S.img) { S.img = ctx.createImageData(g.w, g.h); S.px = new Uint32Array(S.img.data.buffer); }
  const px = S.px, [r, gg, b] = S.blue, w = g.w, d = g.d, rgb = (b << 16 | gg << 8 | r) >>> 0;
  const put = (id, a) => {
    const p0 = g.pix[id], core = ((Math.round(255 * a) << 24) | rgb) >>> 0, ring = Math.round(60 * a);
    for (let y = -1; y <= d; y++) for (let x = -1; x <= d; x++) {
      const q = p0 + y * w + x;
      if (q < 0 || q >= px.length) continue;
      if (y < 0 || x < 0 || y === d || x === d) { if ((px[q] >>> 24) < ring) px[q] = ((ring << 24) | rgb) >>> 0; }
      else px[q] = core;
    }
  };
  if (all) { px.fill(0); const o = ORDER[S.rule]; for (let i = 0; i < S.n1; i++) put(o[i], 1); if (S.from) S.changing.forEach(id => put(id, litAt(id, now))); }
  else S.changing.forEach(id => put(id, litAt(id, now)));
  ctx.putImageData(S.img, 0, 0);
}

/* The number, the line above it and the curve */
const X = (g, s) => g.x0 + (g.x1 - g.x0) * (Math.log10(s) + 1) / 3, Y = (g, v) => g.y0 - (g.y0 - g.y1) * v / 80;
function chart() {
  const svg = $("curve"), w = svg.clientWidth, h = svg.clientHeight, g = S.cg = { w, h, x0: 34, x1: w - 6, y0: h - 34, y1: 8 };
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
  let out = [0, 20, 40, 60, 80].map(v => `<line class="gl" x1="${g.x0}" x2="${g.x1}" y1="${Y(g, v)}" y2="${Y(g, v)}"/><text x="${g.x0 - 6}" y="${Y(g, v) + 4}" text-anchor="end">${v}</text>`).join("");
  out += STOPS.map(s => `<text x="${X(g, s.share)}" y="${g.y0 + 15}" text-anchor="middle">${s.share < 1 ? s.share.toFixed(1) : s.share}</text>`).join("");
  out += `<text class="ttl" x="${(g.x0 + g.x1) / 2}" y="${h - 2}" text-anchor="middle">Neurons copied, % (log scale)</text>`;
  out += `<text class="ttl" x="${g.x0 - 6}" y="${g.y1 - 14}" text-anchor="start" transform="translate(-28 0)">Effect recovered, %</text>`;
  RULES.forEach(rule => {
    out += `<path class="cv" id="cv-${rule}" d="M${STOPS.map(s => X(g, s.share).toFixed(1) + " " + Y(g, s[rule]).toFixed(1)).join("L")}"/>`;
  });
  out += `<circle class="pt" id="cpt" r="5.5"/>`;
  svg.innerHTML = out;
  paintChart();
}
function paintChart() {
  const g = S.cg;
  if (!g) return;
  RULES.forEach(rule => { $("cv-" + rule).classList.toggle("on", rule === S.rule); $("lg-" + rule).classList.toggle("on", rule === S.rule); });
  $("cv-" + S.rule).parentNode.appendChild($("cv-" + S.rule));
  $("cpt").parentNode.appendChild($("cpt"));
  const st = STOPS[S.s];
  $("cpt").setAttribute("cx", X(g, st.share).toFixed(1)); $("cpt").setAttribute("cy", Y(g, st[S.rule]).toFixed(1));
}
function words() {
  const st = STOPS[S.s], all = st.share === 100;
  $("rlab").innerHTML = all ? `All neurons copied<span>${fmt(N)} of ${fmt(N)}</span>`
    : `${esc(NAME[S.rule])}, ${share(st.share)} of neurons<span>${fmt(count(S.s))} of ${fmt(N)} copied from RL</span>`;
  $("base").innerHTML = all ? `Copying every weight, attention included, gives RL itself: <b>100.0 %</b>.`
    : `Random ${share(st.share)} of neurons: <b>${pct(st.random)}</b>. All neurons: <b>${pct(STOPS[5].effect)}</b>; the rest is in attention weights.`;
  $("cap").innerHTML = `${fmt(N)} neurons of the base model, one dot each, one row per layer. <b>Lit: ${fmt(count(S.s))} copied from RL.</b>`;
  $("hint").textContent = SAY[S.rule];
  $("switch").querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.rule === S.rule));
  $("ticks").querySelectorAll("button").forEach((b, i) => b.classList.toggle("on", i === S.s));
  $("share").value = S.s;
  $("share").style.setProperty("--p", (100 * S.s / 5) + "%");
  $("share").setAttribute("aria-valuetext", `${share(st.share)} of neurons, ${fmt(count(S.s))}: ${pct(st[S.rule])} of RL's effect recovered`);
  $("field").setAttribute("aria-label", `${fmt(N)} neurons, one dot per neuron and one row per layer; ${fmt(count(S.s))} lit, chosen by ${NAME[S.rule].toLowerCase()}. ` +
    "Up and down arrows choose a layer; Enter opens it.");
  paintChart();
}
function number(now) {
  const e = ease(clamp((now - S.t0) / 800, 0, 1)), v = S.n0v + (S.n1v - S.n0v) * e, txt = v.toFixed(1);
  if (txt !== S.shownTxt) { S.shownTxt = txt; $("big").innerHTML = `${txt}<small>%</small>`; }
}

/* One state: a share step and a rule. The light and the number move from the state shown to the new one. */
function setState(s, rule, instant) {
  const now = performance.now(), quick = instant || still.matches;
  const cur = S.n0v === undefined ? 0 : S.n0v + (S.n1v - S.n0v) * ease(clamp((now - S.t0) / 800, 0, 1));
  const prev = S.rank ? { rank: S.rank, n: S.n1 } : null;
  S.s = s; S.rule = rule; S.rank = RANK[rule]; S.n1 = count(s);
  S.n0v = quick ? STOPS[s][rule] : cur; S.n1v = STOPS[s][rule];
  if (!quick && prev && (prev.rank !== S.rank || prev.n !== S.n1)) {
    S.from = prev; S.t0 = now;
    if (prev.rank === S.rank) {  // the same order: only the ranks between the two counts change
      const a = Math.min(prev.n, S.n1), b = Math.max(prev.n, S.n1), o = ORDER[rule];
      S.changing = Array.from(o.subarray(a, b));
      S.delay = id => 650 * (S.rank[id] - a) / Math.max(1, b - a) * (S.n1 > prev.n ? 1 : -1) + (S.n1 > prev.n ? 0 : 650);
    } else {  // another rule: every neuron in either set may change
      const ch = [], on = new Uint8Array(N), o0 = ORDER[Object.keys(RANK).find(k => RANK[k] === prev.rank)], o1 = ORDER[rule];
      for (let i = 0; i < prev.n; i++) on[o0[i]] |= 1;
      for (let i = 0; i < S.n1; i++) on[o1[i]] |= 2;
      for (let id = 0; id < N; id++) if (on[id] === 1 || on[id] === 2) ch.push(id);
      S.changing = ch;
      const r = rng(5);
      const dl = new Float32Array(N);
      ch.forEach(id => { dl[id] = 650 * r(); });
      S.delay = id => dl[id];
    }
  } else { S.from = null; S.t0 = quick ? -1e9 : now; }
  if (S.g) drawLit(true, now);
  words();
  if (quick) number(now);
  if (S.open && S.open.startsWith("layer")) pane();
}

/* The side column: the five panels, or one layer */
function layerPane(l) {
  const n = D.per_layer[l], even = Math.round(3523 / L), wc = SET.weight.filter(id => Math.floor(id / W) === l).length;
  const top = SET.top100.filter(id => Math.floor(id / W) === l).map(id => id % W), grp = Math.floor(l / 8);
  const desc = C.described.filter(u => u.layer === l && top.includes(u.neuron));
  return `<div class="dhead"><h2>Layer ${l} of ${L}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead">This layer has ${fmt(W)} neurons. ${n} of them are in the 1 % with the largest effect; an even spread would put ${even} here.</p>` +
    `<ul class="facts"><li>${wc} of its neurons are in the 1 % with the largest weight change, and it holds ${(100 * D.weight_layer[l]).toFixed(1)} % of the feed-forward weight change.</li>` +
    `<li>Copying every neuron of layers ${8 * grp} to ${8 * grp + 7} from RL recovers <b>${pct(100 * (D.groups[grp][0] + D.groups[grp][1]) / 2)}</b> of RL's effect.</li>` +
    (top.length ? `<li>${top.length} of the 100 best neurons are in this layer${desc.length ? `; neuron ${desc[0].neuron} was described as “${esc(desc[0].text)}” ` +
      `(<a href="/finding/neurons-you-can-describe#n-${desc[0].key}">its test</a>)` : ""}.</li>` : `<li>None of the 100 best neurons is in this layer.</li>`) +
    `</ul><div class="steps"><button data-layer-step="-1">‹ Layer above</button><button data-layer-step="1">Layer below ›</button></div>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), l = S.open && S.open.startsWith("layer") ? Number(S.open.slice(5)) : -1;
  S.layer = l;
  $("pane").innerHTML = l >= 0 ? layerPane(l) : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
  placeRow();
}
function placeRow() {
  const row = $("row"), g = S.g;
  if (!g || S.layer < 0) { row.classList.remove("on"); return; }
  row.style.top = (g.top(S.layer) / g.dpr - 2) + "px";
  row.style.height = (g.band / g.dpr + 4) + "px";
  row.classList.add("on");
}
/* The address: #<share>-<rule>, then /<panel> or /layer<n>. The default state, 1 % by largest effect, has no part. */
const KEY = () => `${STOPS[S.s].share}-${S.rule}`;
function address(push) {
  const parts = [KEY() === "1-effect" ? "" : KEY(), S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/"), m = /^([\d.]+)-(effect|weight|random)$/.exec(parts[0] || "");
  const k = m ? STOPS.findIndex(s => String(s.share) === m[1]) : -1, s = k >= 0 ? k : 2, rule = m && k >= 0 ? m[2] : "effect";
  const rest = parts.find(x => C.panels.some(p => p[0] === x) || /^layer([12]?\d|3[01])$/.test(x));
  if (first === true || s !== S.s || rule !== S.rule) setState(s, rule, first === true);
  S.open = rest || null;
  pane();
}
function open(key, focus = true) {
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  if (!focus) return;
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  else if (!key) $("field").focus({ preventScroll: true });
}
function go(s, rule) {
  if (s === S.s && rule === S.rule) return;
  setState(s, rule);
  address(false);
}

/* Always on: the plate sways a few degrees and leans toward the mouse; a change of state lights or darkens neurons and
   counts the number. About 30 frames a second. With reduced motion, one still frame per state. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = now / 1000;
  S.px += (S.tx - S.px) * .08; S.py += (S.ty - S.py) * .08;
  $("body").style.transform = `rotateY(${(3.2 * Math.sin(t * .13) + 3 * S.px).toFixed(2)}deg) rotateX(${(1.6 * Math.sin(t * .09) - 2 * S.py + 2).toFixed(2)}deg)`;
  if (S.from) {
    drawLit(false, now);
    if (now - S.t0 > 650 + 260) { S.from = null; drawLit(true, now); }
  }
  number(now);
}

document.addEventListener("click", e => {
  const r = e.target.closest("[data-rule]"), o = e.target.closest("[data-open]"), t = e.target.closest("[data-tick]"), ls = e.target.closest("[data-layer-step]");
  if (r) go(S.s, r.dataset.rule);
  if (t) go(Number(t.dataset.tick), S.rule);
  if (o) { e.preventDefault(); open(o.dataset.open); }
  if (ls) { open("layer" + clamp(S.layer + Number(ls.dataset.layerStep), 0, L - 1), false); $("pane").querySelector(`[data-layer-step="${ls.dataset.layerStep}"]`).focus({ preventScroll: true }); }
});
$("share").addEventListener("input", e => go(Number(e.target.value), S.rule));
function layerAt(e) {
  const g = S.g, b = $("field").getBoundingClientRect(), y = (e.clientY - b.top) * g.dpr;
  let best = 0, d = Infinity;
  for (let l = 0; l < L; l++) { const c = g.top(l) + g.band / 2, dd = Math.abs(c - y); if (dd < d) { d = dd; best = l; } }
  return best;
}
$("field").addEventListener("click", e => {
  open("layer" + layerAt(e));
  if (narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" });
});
$("field").addEventListener("keydown", e => {
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    e.preventDefault();
    open("layer" + clamp((S.layer < 0 ? (e.key === "ArrowDown" ? -1 : L) : S.layer) + (e.key === "ArrowDown" ? 1 : -1), 0, L - 1), false);
  }
  if (e.key === "Enter") { e.preventDefault(); open("layer" + (S.layer < 0 ? 0 : S.layer)); }
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && S.open) open("");
});
addEventListener("popstate", fromHash);
addEventListener("hashchange", fromHash);
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  S.tx = 2 * (e.clientX - b.left) / b.width - 1; S.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { S.tx = S.ty = 0; });
let resizeT = 0;
new ResizeObserver(() => { clearTimeout(resizeT); resizeT = setTimeout(() => { layout(); chart(); }, 60); }).observe($("field"));
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { colors(); drawDim(); drawLit(true); });
still.addEventListener("change", () => { if (still.matches) { $("body").style.transform = "rotateX(2deg)"; setState(S.s, S.rule, true); } });

$("ticks").innerHTML = STOPS.map((s, i) => `<button data-tick="${i}" style="left:calc(12px + (100% - 24px) * ${i / 5})" tabindex="-1">${share(s.share)}</button>`).join("");
$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
fromHash(true);
layout();
chart();
$("body").style.transform = "rotateX(2deg)";
if (!still.matches) { document.body.classList.add("enter"); setTimeout(() => document.body.classList.remove("enter"), 2000); }
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab covered by one small mark per group of neurons, all faint, and a few lit ones for the best 1 %.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, cols = 9, rows = 6, half = 2.3, bright = [12, 31, 43];
  let out = kit.slab(a, b, th), lit = "";
  for (let i = 0; i < cols * rows; i++) {
    const u = a * .78 * (2 * (i % cols) / (cols - 1) - 1), v = b * .74 * (2 * Math.floor(i / cols) / (rows - 1) - 1);
    const p = kit.at(u - half, v, th / 2), q = kit.at(u + half, v, th / 2);
    if (bright.includes(i)) lit += kit.line(p, q, 1.2 + .14 * Math.sin(t * .6 + i * 1.7), "lit");
    else out += kit.line(p, q, .8, "plain", .62 + .22 * Math.sin(t * .5 + i * 2.1));
  }
  return out + lit;
}"""

# The described neurons among the 100 best, for the layer panel: key, layer, neuron and the sentence, from
# studies/cleanneurons/results/describe/attr_top100-01/descriptions_test.json (set "selected").
DESCRIBED = [
    {"key": "u00", "layer": 17, "neuron": 3660, "text": "The space (or linking token) right before a number or symbol being restated from the problem, after 'is', 'by', 'and', 'over', 'with' or '+', as in 'The answer is 3'."},
    {"key": "u01", "layer": 29, "neuron": 2637, "text": "The period that ends a sentence finishing with a computed number or expression in informal step-by-step reasoning, just before a new sentence such as 'Then', 'Wait' or 'So'."},
    {"key": "u03", "layer": 22, "neuron": 8409, "text": "The space or '{' right before a number operand that follows an operator or relation ('=', '/', '<', 'by', 'and', '\\div', '\\sqrt'), where that number was already stated nearby."},
    {"key": "u04", "layer": 19, "neuron": 10616, "text": "The space right before a number that follows an operator, comma or 'by' ('6 + 12i', 'divided by 9', '2! * 2!') inside a calculation the text is redoing."},
    {"key": "u05", "layer": 29, "neuron": 10229, "text": "An operator or relation token ('+', '=', '\\times', '\\cdot', '>', 'to') right after the first operand in a formal LaTeX-formatted solution, where a number comes next."},
    {"key": "u06", "layer": 10, "neuron": 7275, "text": "A hesitation word 'Hmm', 'Wait' or 'wait' starting a sentence right after a period or 'But', mostly just after the problem is restated in the opening reasoning."},
    {"key": "u07", "layer": 10, "neuron": 86, "text": "'Wait' opening a new paragraph after a blank line, or 'hold' after 'Wait,' or 'but', where the reasoning starts to doubt and recheck its previous step."},
    {"key": "u08", "layer": 31, "neuron": 7955, "text": "A comma, colon, '=' or 'and' in the middle of a calculation, right after a number or short phrase, where the next numeric value is about to be written."},
    {"key": "u09", "layer": 11, "neuron": 9904, "text": "A content word completing a predicate in plain-English reasoning, most often 'distribute' after 'can'/'Let me', also 'straightforward', 'inverse', 'removed', 'covered' after 'too', 'modular', 'then', 'already'."},
    {"key": "u11", "layer": 16, "neuron": 6351, "text": "The space right before a number that was already mentioned, after 'divided by', 'times', 'than', 'of', '+' or a division sign, when a calculation is restated in words."},
    {"key": "u12", "layer": 10, "neuron": 77, "text": "'Hmm', 'Wait' or 'Let' starting a sentence right after a period or question mark in the middle of an arithmetic step or after a tentative answer, opening a recheck."},
    {"key": "u13", "layer": 9, "neuron": 426, "text": "The first token of a value written right after '=' or ':' (the space, or the leading digits of a multi-digit number like '990'), or '\\text' in LaTeX."},
    {"key": "u15", "layer": 15, "neuron": 7111, "text": "The token just before the last number of a short standalone equation line (space after '-', 'by', '='), or the '!' plus blank line ending the problem statement."},
    {"key": "u18", "layer": 5, "neuron": 10160, "text": "A longer, less common content word ending a phrase in plain-English commentary ('substitutions', 'misunderstanding', 'separately', 'tedious', 'overlap', 'rounded'), or 'boxed' right after a backslash (weak)"},
    {"key": "u20", "layer": 23, "neuron": 6475, "text": "The word 'problem' in the opening 'Okay, so I have this problem (here where)' right after the question; weaker on 'approach' after 'another' and on 'miscalculation'."},
    {"key": "u22", "layer": 2, "neuron": 3032, "text": "The token 'boxed' right after a backslash, when the final answer is given, typically on the line after '**Final Answer**' or after 'is \\'."},
    {"key": "u24", "layer": 30, "neuron": 10249, "text": "The sentence-ending period (or '?', ').') after a full statement in informal reasoning, especially when doubt or a next plan follows ('Let me think', 'Wait, maybe', 'So')."},
    {"key": "u25", "layer": 11, "neuron": 3547, "text": "'Wait' or 'Hmm' opening a new paragraph, or 'let' after 'but', right after an answer has just been concluded ('the answer is 4'), starting a double-check."},
    {"key": "u26", "layer": 14, "neuron": 7514, "text": "The space before the last number of an expression or phrase ('between 6 and 7', 'x - 1', 'degree 2', 'base 2 of 64'), or 'simpl' in 'which simplifies' (weak)"},
    {"key": "u27", "layer": 12, "neuron": 5682, "text": "A short function token inside an ongoing explanation: the space after 'divided by', 'the', 'of', 'should' after 'maybe I', or the '\\[' line opening a display equation (weak)"},
    {"key": "u29", "layer": 4, "neuron": 7613, "text": "The stem 'don' or 'isn' of a negative contraction, right before the apostrophe-t, most often in 'I don't see any mistakes' or 'there isn't' near the end of the reasoning."},
    {"key": "u31", "layer": 14, "neuron": 7525, "text": "'Let' (less often 'Wait') starting a sentence right after a doubt, question or tentative answer ('...a mistake in algebra?', 'maybe another way.'), opening a recheck or a different method."},
    {"key": "u33", "layer": 5, "neuron": 6372, "text": "The interjection 'Hmm' (capitalized) starting a sentence right after a period that ends a finished computation or a stated answer, as in 'the remainder is 0. Hmm'."},
    {"key": "u34", "layer": 8, "neuron": 1033, "text": "The last word of a fixed phrase in prose: 'inverse' after 'multiplicative'/'an', 'step' after 'step by', 'thorough' after 'just to be', 'head' after 'in your', 'proportion' after 'set up a'."},
    {"key": "u35", "layer": 9, "neuron": 692, "text": "The token 'boxed' right after a backslash inside a prose sentence that states the result, almost always following 'the answer is \\' (often after 'Therefore,')."},
    {"key": "u36", "layer": 18, "neuron": 1045, "text": "The space (or '{') right before a number that follows an operator, '=', comma, 'by' or 'and' inside a calculation, as in '6 + 12i' or 'divided by 3'."},
    {"key": "u37", "layer": 9, "neuron": 7587, "text": "The token 'boxed' right after the backslash on the line following '**Final Answer**', and the word 'Answer' inside the '**Final Answer**' header itself."},
    {"key": "u38", "layer": 26, "neuron": 8438, "text": "A connective opening a sentence in informal reasoning ('So', 'But', 'but' after 'Hmm,'), or the comma right after 'Wait', 'So' or 'actually', before the clause itself begins."},
    {"key": "u41", "layer": 11, "neuron": 7824, "text": "The word 'To' that starts the clean written solution ('To solve the problem, we...') on a new paragraph right after the boxed final answer that ends the reasoning."},
    {"key": "u44", "layer": 3, "neuron": 7717, "text": "The token 'boxed' right after a backslash in the '**Final Answer**' block at the end of the reasoning, either directly under the header or after 'is \\'."},
]

PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "stops": STOPS, "sets": SETS, "described": DESCRIBED,
    "data": {k: DATA[k] for k in ("layers", "width", "per_layer", "weight_layer", "groups")}}).replace("</", "<\\/"))

if __name__ == "__main__":  # run from the repository root
    load = lambda path: json.load(open(path))
    DESC = "studies/cleanneurons/results/describe/attr_top100-01/descriptions_test.json"
    desc = [{"key": u["key"], "layer": u["layer"], "neuron": u["neuron"], "text": u["description"]}
            for u in sorted(load(DESC)["units"], key=lambda u: u["key"]) if u["set"] == "selected"]
    if sys.argv[1:] == ["--write"]:
        src = open(__file__).read()
        for name, value in (("SETS", _build()), ("DESCRIBED", desc)):
            start = src.index(f"\n{name} = ") + 1
            end = src.index("\n\n", start)
            body = json.dumps(value, ensure_ascii=False, indent=1) if name == "SETS" else \
                "[\n" + "".join("    " + json.dumps(d, ensure_ascii=False) + ",\n" for d in value) + "]"
            src = src[:start] + f"{name} = " + body + src[end:]
        open(__file__, "w").write(src)
        sys.exit("wrote SETS and DESCRIBED")
    assert SETS == _build(), "SETS differ from the edit files: run with --write"
    assert DESCRIBED == desc, "DESCRIBED differs from descriptions_test.json: run with --write"
    m, r, prof = load(DATA["metrics"]), load(DATA["readout"]), load(DATA["profile"])
    pair = lambda a: [round(m["arms"][a]["cells"][c][KEY], 4) for c in ("T1", "T2")]
    for i, s in enumerate(SHARES):
        assert DATA["effect"][i] == pair(f"attr{s:g}") and DATA["weight"][i] == pair(f"top{s:g}"), s
        assert DATA["random"][i] == [pair(f"rnd{s:g}_s0"), pair(f"rnd{s:g}_s1")], s
        assert m["arms"][f"attr{s:g}"]["neurons"] == STOPS[i]["neurons"], s
    assert DATA["mlp"] == pair("mlp") and DATA["attn"] == pair("attn")
    assert DATA["groups"] == [pair(f"mlpL{a}-{a + 7}") for a in (0, 8, 16, 24)]
    assert DATA["positions"] == [m["cells"][c]["decisive_positions_after_cue_half_B"] for c in ("T1", "T2")]
    assert DATA["answers"] == [len(m["attr"]["half_B"][c]) for c in ("T1", "T2")]
    assert (m["commit"], m["job_id"]) == (DATA["commit"], DATA["job"]) and m["controls"]["all"]["pass"]
    assert DATA["positive"] == round(r["fraction_of_neurons_with_positive_score"], 4)
    f = r["first_order_check_all_mlp"]
    assert [DATA["first_order"][k] for k in ("predicted", "measured", "total")] == [round(f[k], 3) for k in ("predicted_drop", "measured_drop", "L_half_A")]
    assert DATA["per_layer"] == r["attr1_neurons_per_layer"] and DATA["overlap"] == r["attr1_overlap_with_top1_by_weight_change"]
    assert DATA["weight_layer"] == [round(x, 4) for x in prof["share_of_sum_s_per_layer"]]
    assert DATA["weight_top1"] == round(prof["share_of_sum_s_top_percent"]["1"]["share"], 4)
    assert (prof["layers"], prof["width"], prof["neurons"]) == (DATA["layers"], DATA["width"], DATA["neurons"])
    v = load(DATA["vector"]["metrics"])
    assert DATA["vector"]["bias_layer"] == [round(v["arms"]["bias_layer"]["cells"][c][KEY], 4) for c in ("T1", "T2")]
    sets = {k: load(p) for k, p in DATA["sets"].items()}
    assert [len(sets["effect"]["copy_neurons"].get(str(l), [])) for l in range(32)] == DATA["per_layer"]
    assert len({(l, n) for l, ns in sets["effect"]["copy_neurons"].items() for n in ns} &
               {(l, n) for l, ns in sets["weight"]["copy_neurons"].items() for n in ns}) == DATA["overlap"]
    assert round(BEST1, 1) == 16.1
    print("DATA, SETS and DESCRIBED match", DATA["metrics"], "and the edit files")
