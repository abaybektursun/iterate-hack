"""At equal weight norm, RL's 8 directions per matrix shift the residual stream at layer 24 95 times more than 8 random
directions; the filed prediction that one shared direction predicts cut-off answers was refuted.

The page of one finding, served at /finding/rl-directions-move-activations (view.py serves every tools/finding_<slug>.py)
and reached from its tile on /findings, which ICON draws. It is the companion of /finding/the-finish-dial one level down:
the same weight edits (the 8 largest directions of RL's weight change per matrix at several sizes, 8 random directions of
the same norm, Think-SFT's 8 directions, other rewards' 8 directions and parts of RL's change), measured in the model's
activations instead of its answers. Board item result-98de28.

The picture is one lit plate with one mark per edit (28). The one control is a switch of three views, and the marks travel
between them:
  size       x: the edit's weight norm (% of the weight norm of the matrices it edits); y: the RMS shift of the residual
             stream at layer 24 (log scale). The large number is RL's shift over the random edit's at size 1 (95x).
  direction  the same x; y: the cosine of the edit's mean shift with that of RL's 8 directions at size 1. The large number
             is the closest other reward (RL-Code, 0.37).
  cutoffs    x: the projection of the mean shift on one shared direction (the readout's P1); y: answers cut off at 16,384
             tokens of the 328 harder problems in the scored cell of the same edit. The large number is the refuted
             prediction's rank correlation (-0.67, predicted at most -0.8; the plain size of the mean shift gives -0.62).
A click on a mark opens that edit in the side column: what it is, its weight norm, shift, cosine, projection, its score on
the 328 harder problems and the tokens its mean shift raises and lowers most (logit lens).
Address: /finding/rl-directions-move-activations#[direction/|cutoffs/][<panel key>|<edit key>]; the default view (size)
is left out. The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md).

DATA is copied from the artifact (the deployed site ships only tools/*.py, so the copy is a literal). Run this file from
the repository root to compare every number with the readout, the job's metrics and the scored cells' readout; it fails
on any changed number:

    uv run python tools/finding_rl_directions_move_activations.py
"""
import json
import sys

RUN = "studies/rlneurons/results/xshift/run-01/"
CELLS = "studies/rlneurons/results/xreward/edits/readout.json"  # the scored cells: right and cut off on the 328

# Every number is copied from the artifacts named here. None is typed from memory.
DATA = {
    "readout": RUN + "readout.json", "metrics": RUN + "metrics.json", "run": RUN + "run.json",
    "spec": "studies/rlneurons/specs/SPEC_xshift.md", "readme": "studies/rlneurons/README.md, section 'xshift'",
    "commit": "e625d91e20525297d470895f944e4f92b1e8d4d6",  # the commit that added the readout
    "job_commit": "b0531526758164990ccffc3bd54402a9c2fbccbc", "job": "abaybektursun-1115-130144-40a0",  # run.json
    "wall_s": 1367.4,  # run.json job.wall_s
    "base_model": "allenai/Olmo-3-1025-7B", "answers_job": "abaybektursun-1114-151534-e72c",  # run.json, spec
    "layer": 24, "inputs": 48, "positions": 6144, "cap_hit_inputs": 24, "answer_tokens": 2048, "step": 16,
    "base_rms": 41.2179,  # readout base_rms_norm_at_layer: the RMS norm of the base's residual stream at layer 24
    "add_rel_match": 1.7764e-15,  # readout max_abs_add_rel_difference_from_scored_cells
    # readout P1: Spearman over the 23 non-random edits of cut-offs with the projection on the shared direction, and with
    # the plain norm of the mean shift; the spec's prediction (at most -0.8) and margin (0.05)
    "P1": {"n_edits": 23, "rho_projection": -0.6658, "rho_norm": -0.6209, "predicted": -0.8, "margin": 0.05, "refuted": True},
    "P3": {"predicted_if": 0.5, "held": False},  # spec: cosine(IF, Math 3.1) > 0.5; readout P3.held
    # the scored cells (CELLS, cells.<name>): Base + cue with no edit, and RL, on the 328 harder problems, T 1.0, one answer each
    "n": 328, "cap": 16384, "base_cue": {"right": 164, "cut": 77}, "rl": {"right": 206, "cut": 20},
    # readout edits.<key> (rounded): n_edited from metrics edits.<key>; raised and lowered: the first 6 and 4 tokens of
    # readout logit_lens.<key> (raw logit change at the last layer, with an offset shared by all tokens)
    "edits": {
        "top8xm1_math31": {"n_edited": 224, "add_rel": 0.0007406, "rms_shift": 4.4801, "mean_shift_norm": 1.4698, "frac_mean_dir": 0.1166, "cos_with_math": -0.8259, "projection_p1": -0.527666, "p1_direction": "top8_code31", "cap_hits": 96, "right_v3": 118, "raised": [[" *(", 1.635], [" (**", 1.583], ["\",\"\",", 1.566], ["@(", 1.565], [" (*", 1.563], [".*(", 1.561]], "lowered": [[" which", 0.092], ["stdexcept", 0.206], [" it", 0.249], ["cassert", 0.269]]},
        "top8x0.5_math31": {"n_edited": 224, "add_rel": 0.0003703, "rms_shift": 3.3252, "mean_shift_norm": 0.8208, "frac_mean_dir": 0.0675, "cos_with_math": 0.9266, "projection_p1": 0.302814, "p1_direction": "top8_code31", "cap_hits": 50, "right_v3": 170, "raised": [[" which", 0.112], [" it", 0.019], [" котор", 0.011], ["which", 0.002], ["stdexcept", -0.011], [" Actually", -0.012]], "lowered": [[" *(", -0.726], [" ((", -0.716], [" (**", -0.71], [".*(", -0.704]]},
        "top8_math31": {"n_edited": 224, "add_rel": 0.0007406, "rms_shift": 6.2306, "mean_shift_norm": 2.0589, "frac_mean_dir": 0.1375, "cos_with_math": 1.0, "projection_p1": 0.758751, "p1_direction": "top8_code31", "cap_hits": 46, "right_v3": 192, "raised": [[" which", 0.311], [" it", 0.106], [" actually", 0.106], ["Hmm", 0.095], [" котор", 0.087], [" perhaps", 0.06]], "lowered": [[" ((", -1.768], [".*(", -1.678], ["((", -1.612], [" (-", -1.597]]},
        "top8x1.5_math31": {"n_edited": 224, "add_rel": 0.0011109, "rms_shift": 9.3363, "mean_shift_norm": 3.6766, "frac_mean_dir": 0.1875, "cos_with_math": 0.9859, "projection_p1": 1.322696, "p1_direction": "top8_code31", "cap_hits": 25, "right_v3": 203, "raised": [[" which", 0.615], ["Hmm", 0.49], [" actually", 0.398], [" котор", 0.297], [" it", 0.291], [":variables", 0.27]], "lowered": [[" ((", -2.967], ["((", -2.697], [".*(", -2.649], ["((-", -2.582]]},
        "top8x2_math31": {"n_edited": 224, "add_rel": 0.0014812, "rms_shift": 11.9103, "mean_shift_norm": 4.864, "frac_mean_dir": 0.1937, "cos_with_math": 0.9851, "projection_p1": 1.78915, "p1_direction": "top8_code31", "cap_hits": 5, "right_v3": 190, "raised": [[" which", 1.008], [":variables", 0.687], [" котор", 0.649], [" it", 0.582], [" actually", 0.557], ["Hmm", 0.547]], "lowered": [[" ((", -3.818], ["((", -3.41], [" (-", -3.281], [".*(", -3.209]]},
        "top8x3_math31": {"n_edited": 224, "add_rel": 0.0022218, "rms_shift": 16.7716, "mean_shift_norm": 6.7428, "frac_mean_dir": 0.1814, "cos_with_math": 0.9682, "projection_p1": 2.540186, "p1_direction": "top8_code31", "cap_hits": 9, "right_v3": 117, "raised": [[" which", 2.01], [":variables", 1.878], [" котор", 1.685], [" WHICH", 1.481], ["which", 1.4], [" it", 1.395]], "lowered": [[" ((", -4.854], [" (", -4.53], [" (-", -4.345], [" (**", -4.267]]},
        "rand8xm1_math31": {"n_edited": 224, "add_rel": 0.0007406, "rms_shift": 0.0823, "mean_shift_norm": 0.0144, "frac_mean_dir": 0.0342, "cos_with_math": 0.0224, "projection_p1": 0.000291, "p1_direction": "top8_code31", "cap_hits": 71, "right_v3": 159, "raised": [[" extr", 0.005], [" wand", 0.005], ["astes", 0.005], [" amat", 0.005], [")get", 0.005], [" huh", 0.005]], "lowered": [["cho", -0.005], [" cuanto", -0.005], ["hipster", -0.005], ["enger", -0.005]]},
        "rand8_math31": {"n_edited": 224, "add_rel": 0.0007406, "rms_shift": 0.0655, "mean_shift_norm": 0.0144, "frac_mean_dir": 0.0505, "cos_with_math": -0.0228, "projection_p1": -0.000289, "p1_direction": "top8_code31", "cap_hits": 67, "right_v3": 158, "raised": [["cho", 0.005], [" cuanto", 0.005], ["enger", 0.005], ["hipster", 0.005], ["ler", 0.005], [" theat", 0.005]], "lowered": [[" extr", -0.005], [" wand", -0.005], ["astes", -0.005], [" amat", -0.005]]},
        "rand8x1.5_math31": {"n_edited": 224, "add_rel": 0.0011109, "rms_shift": 0.0951, "mean_shift_norm": 0.0216, "frac_mean_dir": 0.0537, "cos_with_math": -0.023, "projection_p1": -0.000435, "p1_direction": "top8_code31", "cap_hits": 74, "right_v3": 159, "raised": [["cho", 0.008], [" cuanto", 0.007], ["enger", 0.007], ["hipster", 0.007], ["ler", 0.007], [" theat", 0.007]], "lowered": [[" extr", -0.008], [" wand", -0.008], ["astes", -0.007], [" amat", -0.007]]},
        "rand8x2_math31": {"n_edited": 224, "add_rel": 0.0014812, "rms_shift": 0.1241, "mean_shift_norm": 0.0287, "frac_mean_dir": 0.056, "cos_with_math": -0.0231, "projection_p1": -0.000583, "p1_direction": "top8_code31", "cap_hits": 70, "right_v3": 167, "raised": [["cho", 0.011], [" cuanto", 0.01], ["enger", 0.009], ["hipster", 0.009], ["ler", 0.009], [" theat", 0.009]], "lowered": [[" extr", -0.01], [" wand", -0.01], ["astes", -0.01], [" amat", -0.009]]},
        "rand8x3_math31": {"n_edited": 224, "add_rel": 0.0022218, "rms_shift": 0.1809, "mean_shift_norm": 0.0431, "frac_mean_dir": 0.0591, "cos_with_math": -0.0233, "projection_p1": -0.000884, "p1_direction": "top8_code31", "cap_hits": 79, "right_v3": 163, "raised": [["cho", 0.016], [" cuanto", 0.015], ["enger", 0.014], ["hipster", 0.014], ["ler", 0.014], [" theat", 0.014]], "lowered": [[" extr", -0.016], [" wand", -0.015], ["astes", -0.014], [" amat", -0.014]]},
        "top1_math31": {"n_edited": 224, "add_rel": 0.0004826, "rms_shift": 3.5096, "mean_shift_norm": 1.2103, "frac_mean_dir": 0.1299, "cos_with_math": 0.8265, "projection_p1": 0.407119, "p1_direction": "top8_code31", "cap_hits": 51, "right_v3": 181, "raised": [[" котор", 0.131], [" iParam", 0.118], [":variables", 0.117], ["which", 0.086], [" which", 0.078], [" WHICH", 0.077]], "lowered": [[" (", -1.373], [" ((", -1.117], ["*(", -1.092], [" (**", -1.087]]},
        "top1x2_math31": {"n_edited": 224, "add_rel": 0.0009652, "rms_shift": 6.4199, "mean_shift_norm": 2.5805, "frac_mean_dir": 0.1775, "cos_with_math": 0.854, "projection_p1": 0.867222, "p1_direction": "top8_code31", "cap_hits": 23, "right_v3": 184, "raised": [[":variables", 0.511], [" котор", 0.499], [" iParam", 0.466], [" WHICH", 0.425], ["which", 0.421], [" which", 0.394]], "lowered": [[" (", -2.68], [" ((", -2.128], [" (-", -2.069], ["*(", -2.059]]},
        "top1x3_math31": {"n_edited": 224, "add_rel": 0.0014478, "rms_shift": 10.1239, "mean_shift_norm": 4.2392, "frac_mean_dir": 0.1947, "cos_with_math": 0.8911, "projection_p1": 1.424644, "p1_direction": "top8_code31", "cap_hits": 10, "right_v3": 168, "raised": [[":variables", 1.199], [" котор", 1.125], [" WHICH", 1.052], [" iParam", 1.03], [" which", 1.016], ["which", 1.015]], "lowered": [[" (", -3.958], [" ((", -3.15], [" (-", -3.017], [" (**", -2.952]]},
        "top64_math31": {"n_edited": 224, "add_rel": 0.0011463, "rms_shift": 8.5086, "mean_shift_norm": 3.244, "frac_mean_dir": 0.1835, "cos_with_math": 0.956, "projection_p1": 1.143431, "p1_direction": "top8_code31", "cap_hits": 42, "right_v3": 200, "raised": [["Hmm", 0.633], [" actually", 0.398], [" which", 0.32], [" Hmm", 0.204], [" perhaps", 0.178], [" ?\n\n", 0.12]], "lowered": [[" ((", -2.691], [".*(", -2.565], ["((-", -2.48], ["((", -2.472]]},
        "top8attn_math31": {"n_edited": 128, "add_rel": 0.0010297, "rms_shift": 3.5874, "mean_shift_norm": 0.9523, "frac_mean_dir": 0.082, "cos_with_math": 0.96, "projection_p1": 0.334587, "p1_direction": "top8_code31", "cap_hits": 59, "right_v3": 178, "raised": [[" which", 0.058], [" котор", -0.05], [" it", -0.052], [" actually", -0.082], ["stdexcept", -0.084], [" Actually", -0.086]], "lowered": [[".*(", -0.946], [" ((", -0.926], [" *(", -0.912], ["@(", -0.907]]},
        "top8mlp_math31": {"n_edited": 96, "add_rel": 0.0005945, "rms_shift": 3.0471, "mean_shift_norm": 0.7532, "frac_mean_dir": 0.067, "cos_with_math": 0.8693, "projection_p1": 0.283245, "p1_direction": "top8_code31", "cap_hits": 40, "right_v3": 181, "raised": [[" which", 0.165], ["which", 0.096], [" it", 0.089], [" котор", 0.069], [" something", 0.068], [" WHICH", 0.061]], "lowered": [[" *(", -0.568], [" (", -0.563], [" square", -0.562], [" ((", -0.55]]},
        "top8x1.5_L0-10_math31": {"n_edited": 77, "add_rel": 0.001066, "rms_shift": 6.2262, "mean_shift_norm": 1.8404, "frac_mean_dir": 0.1698, "cos_with_math": 0.6695, "projection_p1": 0.364967, "p1_direction": "top8_code31", "cap_hits": 98, "right_v3": 184, "raised": [["Hmm", 1.271], [",…", 1.096], [" ?\n\n", 1.066], ["!.\n\n", 1.036], ["?\n\n", 1.026], ["?)\n\n", 1.001]], "lowered": [[" jt", -0.459], ["+w", -0.445], ["-validate", -0.443], [")((((", -0.437]]},
        "top8x1.5_L11-21_math31": {"n_edited": 77, "add_rel": 0.001012, "rms_shift": 4.4128, "mean_shift_norm": 1.789, "frac_mean_dir": 0.181, "cos_with_math": 0.8185, "projection_p1": 0.651632, "p1_direction": "top8_code31", "cap_hits": 49, "right_v3": 183, "raised": [[" Actually", 0.23], [" actually", 0.193], [" ought", 0.178], [" succeeds", 0.177], [" presently", 0.17], [" —", 0.169]], "lowered": [[" midpoint", -0.457], [" +/-", -0.441], ["/-", -0.433], ["~-", -0.433]]},
        "top8x1.5_L22-31_math31": {"n_edited": 70, "add_rel": 0.001255, "rms_shift": 0.8252, "mean_shift_norm": 0.6461, "frac_mean_dir": 0.645, "cos_with_math": 0.5494, "projection_p1": 0.103687, "p1_direction": "top8_code31", "cap_hits": 57, "right_v3": 166, "raised": [[" which", -0.064], [" x", -0.072], ["stdexcept", -0.153], [" котор", -0.158], ["\tx", -0.177], ["_x", -0.183]], "lowered": [[" (**", -1.997], [" (“", -1.961], [" (", -1.915], [" (*", -1.897]]},
        "top8_code31": {"n_edited": 224, "add_rel": 0.0006388, "rms_shift": 3.6511, "mean_shift_norm": 1.0528, "frac_mean_dir": 0.0921, "cos_with_math": 0.3685, "projection_p1": 0.387982, "p1_direction": "top8_math31", "cap_hits": 41, "right_v3": 178, "raised": [[" perhaps", -0.176], [".", -0.182], ["Perhaps", -0.229], ["stdexcept", -0.257], [" 설정", -0.263], [" relent", -0.264]], "lowered": [[" sum", -1.339], [" +(", -1.336], [" ((((", -1.326], [" -(", -1.311]]},
        "top8_code30": {"n_edited": 224, "add_rel": 0.0010675, "rms_shift": 4.9785, "mean_shift_norm": 1.8199, "frac_mean_dir": 0.1623, "cos_with_math": 0.1831, "projection_p1": 0.33317, "p1_direction": "top8_math31", "cap_hits": 23, "right_v3": 173, "raised": [[" all", 4.166], [",", 3.96], [" ", 3.772], [" a", 3.684], [" the", 3.622], [" in", 3.461]], "lowered": [["#ad", -2.646], ["#ac", -2.626], [",eg", -2.615], ["#ga", -2.594]]},
        "top8_math30": {"n_edited": 224, "add_rel": 0.0007838, "rms_shift": 5.2252, "mean_shift_norm": 1.9447, "frac_mean_dir": 0.1568, "cos_with_math": 0.2934, "projection_p1": 0.570591, "p1_direction": "top8_math31", "cap_hits": 43, "right_v3": 182, "raised": [[".", 2.596], [".\n\n", 2.314], [" that", 2.061], [" the", 2.043], [" in", 1.902], [" and", 1.815]], "lowered": [["#ab", -5.035], ["#ac", -4.922], ["!,\n", -4.812], ["#ad", -4.76]]},
        "top8_if30": {"n_edited": 224, "add_rel": 0.0010725, "rms_shift": 2.1376, "mean_shift_norm": 0.6937, "frac_mean_dir": 0.1378, "cos_with_math": 0.0883, "projection_p1": 0.061247, "p1_direction": "top8_math31", "cap_hits": 41, "right_v3": 155, "raised": [["<|endoftext|>", 0.017], [",", -0.078], [" is", -0.101], [".", -0.119], ["�", -0.12], [" ", -0.123]], "lowered": [["...\n\n\n\n", -1.231], [".OS", -1.089], ["#ab", -1.079], ["#ac", -1.077]]},
        "top8_general30": {"n_edited": 224, "add_rel": 0.0003773, "rms_shift": 1.2142, "mean_shift_norm": 0.4534, "frac_mean_dir": 0.1538, "cos_with_math": 0.2396, "projection_p1": 0.108647, "p1_direction": "top8_math31", "cap_hits": 88, "right_v3": 164, "raised": [[",", -0.03], [".", -0.146], [" the", -0.195], [" ", -0.195], [" (", -0.225], [" and", -0.229]], "lowered": [["->\n", -1.234], ["?,\n", -1.219], ["#ac", -1.216], [".Ma", -1.207]]},
        "top8x0.02_think_sft": {"n_edited": 224, "add_rel": 0.0007365, "rms_shift": 0.7487, "mean_shift_norm": 0.0647, "frac_mean_dir": 0.0179, "cos_with_math": -0.0198, "projection_p1": -0.001283, "p1_direction": "top8_math31", "cap_hits": 75, "right_v3": 156, "raised": [[" (", 0.279], [" ", 0.261], [",", 0.248], [" -", 0.232], [" in", 0.226], [" x", 0.223]], "lowered": [["IFn", -0.06], ["););\n", -0.059], ["@dynamic", -0.058], ["{EIF", -0.057]]},
        "proj_math31_code30": {"n_edited": 224, "add_rel": 0.0004038, "rms_shift": 3.0249, "mean_shift_norm": 0.7544, "frac_mean_dir": 0.0697, "cos_with_math": 0.8776, "projection_p1": 0.268702, "p1_direction": "top8_code31", "cap_hits": 54, "right_v3": 171, "raised": [[" which", 0.115], ["which", 0.038], [" котор", 0.036], [" it", 0.033], [" WHICH", 0.014], ["stdexcept", -0.003]], "lowered": [[" (", -0.691], [" (**", -0.686], [" *(", -0.668], [" edge", -0.665]]},
        "projc_math31_code30": {"n_edited": 224, "add_rel": 0.0006208, "rms_shift": 3.7791, "mean_shift_norm": 0.9718, "frac_mean_dir": 0.0807, "cos_with_math": 0.9747, "projection_p1": 0.364974, "p1_direction": "top8_code31", "cap_hits": 69, "right_v3": 176, "raised": [[" which", 0.088], [" actually", 0.004], [" perhaps", -0.008], [" it", -0.011], [" \n\n", -0.019], [" Actually", -0.028]], "lowered": [[".*(", -0.877], [" ((", -0.866], [" *(", -0.84], ["@(", -0.812]]},
    },
}

_E = DATA["edits"]
RATIO = _E["top8_math31"]["rms_shift"] / _E["rand8_math31"]["rms_shift"]  # 95.1
_SIZE = {"top8xm1_math31": -1, "top8x0.5_math31": 0.5, "top8_math31": 1, "top8x1.5_math31": 1.5, "top8x2_math31": 2, "top8x3_math31": 3}
_PAIR = {"top8xm1_math31": "rand8xm1_math31", "top8_math31": "rand8_math31", "top8x1.5_math31": "rand8x1.5_math31",
         "top8x2_math31": "rand8x2_math31", "top8x3_math31": "rand8x3_math31"}  # RL's directions and the random edit of the same norm
_TIMES = {k: _E[k]["rms_shift"] / _E[r]["rms_shift"] for k, r in _PAIR.items()}
_m = lambda x: str(x).replace("-", "−")  # the minus sign of the site
_c = lambda k: _m(f"{_E[k]['cos_with_math']:.2f}")
_cos_pos = [_E[k]["cos_with_math"] for k in ("top8x0.5_math31", "top8x1.5_math31", "top8x2_math31", "top8x3_math31")]
_frac = [_E[k]["frac_mean_dir"] for k in _SIZE]
_P, _B, _RL = DATA["P1"], DATA["base_cue"], DATA["rl"]
_rp, _rn = (_m(f"{_P[k]:.2f}") for k in ("rho_projection", "rho_norm"))  # −0.67, −0.62
_r = lambda k: _E[k]["rms_shift"]
_pct = lambda k: f"{100 * _E[k]['add_rel']:.3f} %"

TITLE = "RL directions move activations"  # the name on its tile on /findings and in the browser tab
PROBLEM = ("Does the weight change from training with reinforcement learning (RL) move the model's activations more than "
           "a random weight change of the same size?")
LINE = (f"At equal weight norm, the 8 largest directions of RL's weight change in each weight matrix shift the activations "
        f"{round(RATIO)} times more than 8 random directions.")

# The edits in the order of the side column's Previous and Next: [readout key, group, label on the picture, name, what it
# is]. Groups: rl (RL's 8 directions at a size), rand (the control), sft (Think-SFT), reward (another reward's 8
# directions), part (a part or variant of RL's change).
_RLW = "The 8 largest directions of RL's weight change in each of the 224 weight matrices"
_RW = "A random rank-8 change in each of the 224 matrices, with the norm of RL's 8 directions at size"
_OW = "The 8 largest directions per matrix of the weight change of"
EDITS = [
    ["top8_math31", "rl", "1", "RL's 8 directions, size 1", f"{_RLW}, added to the base at size 1."],
    ["top8x0.5_math31", "rl", "0.5", "RL's 8 directions, size 0.5", f"{_RLW}, multiplied by 0.5 and added to the base."],
    ["top8x1.5_math31", "rl", "1.5", "RL's 8 directions, size 1.5", f"{_RLW}, multiplied by 1.5 and added to the base."],
    ["top8x2_math31", "rl", "2", "RL's 8 directions, size 2", f"{_RLW}, multiplied by 2 and added to the base."],
    ["top8x3_math31", "rl", "3", "RL's 8 directions, size 3", f"{_RLW}, multiplied by 3 and added to the base."],
    ["top8xm1_math31", "rl", "−1", "RL's 8 directions, size −1", f"{_RLW}, subtracted from the base (size −1)."],
    ["rand8_math31", "rand", "", "8 random directions, size 1", f"{_RW} 1: the control."],
    ["rand8x1.5_math31", "rand", "", "8 random directions, size 1.5", f"{_RW} 1.5: the control."],
    ["rand8x2_math31", "rand", "", "8 random directions, size 2", f"{_RW} 2: the control."],
    ["rand8x3_math31", "rand", "", "8 random directions, size 3", f"{_RW} 3: the control."],
    ["rand8xm1_math31", "rand", "", "8 random directions, size −1", f"{_RW} −1, subtracted: the control."],
    ["top8x0.02_think_sft", "sft", "Think-SFT", "Think-SFT's 8 directions",
     f"{_OW} Think-SFT (Olmo-3-7B-Think-SFT), multiplied by 0.02 to match the norm of RL's 8 directions at size 1."],
    ["top8_code31", "reward", "RL-Code", "RL-Code's 8 directions", f"{_OW} RL-Code (Olmo-3.1-7B-RL-Zero-Code), size 1."],
    ["top8_math30", "reward", "Math 3.0", "Math 3.0's 8 directions", f"{_OW} Olmo-3-7B-RL-Zero-Math (Math 3.0), size 1."],
    ["top8_code30", "reward", "Code 3.0", "Code 3.0's 8 directions", f"{_OW} Olmo-3-7B-RL-Zero-Code (Code 3.0), size 1."],
    ["top8_general30", "reward", "General", "General's 8 directions", f"{_OW} Olmo-3-7B-RL-Zero-General (General), size 1."],
    ["top8_if30", "reward", "IF", "IF's 8 directions", f"{_OW} Olmo-3-7B-RL-Zero-IF (IF), size 1."],
    ["top1_math31", "part", "", "RL's largest direction, size 1", "Only the largest direction of RL's change in each matrix, at size 1."],
    ["top1x2_math31", "part", "", "RL's largest direction, size 2", "Only the largest direction of RL's change in each matrix, multiplied by 2."],
    ["top1x3_math31", "part", "", "RL's largest direction, size 3", "Only the largest direction of RL's change in each matrix, multiplied by 3."],
    ["top64_math31", "part", "", "RL's 64 directions, size 1", "The 64 largest directions of RL's change in each matrix, at size 1."],
    ["top8attn_math31", "part", "", "RL's 8 directions, attention only", "RL's 8 directions at size 1 in the 128 attention matrices only."],
    ["top8mlp_math31", "part", "", "RL's 8 directions, feed-forward only", "RL's 8 directions at size 1 in the 96 feed-forward matrices only."],
    ["top8x1.5_L0-10_math31", "part", "Layers 0 to 10", "RL's 8 directions, layers 0 to 10", "RL's 8 directions at size 1.5 in layers 0 to 10 only (77 matrices)."],
    ["top8x1.5_L11-21_math31", "part", "", "RL's 8 directions, layers 11 to 21", "RL's 8 directions at size 1.5 in layers 11 to 21 only (77 matrices)."],
    ["top8x1.5_L22-31_math31", "part", "", "RL's 8 directions, layers 22 to 31", "RL's 8 directions at size 1.5 in layers 22 to 31 only (70 matrices)."],
    ["proj_math31_code30", "part", "", "RL's 8 directions, part shared with Code 3.0",
     "The part of RL's 8 directions per matrix that reads from the input directions of Code 3.0's 8 directions, at its own norm."],
    ["projc_math31_code30", "part", "", "RL's 8 directions, rest",
     "RL's 8 directions per matrix without the part shared with Code 3.0, at its own norm."],
]

# The readout beside the picture, one per view: the large number (value, decimals, suffix), two lines under it, then the
# lines of the state. Computed from DATA.
READ = {
    "size": {"big": round(RATIO), "dec": 0, "suffix": "×",
             "u": ["times the shift of a random edit", "of the same weight norm, layer 24"],
             "lines": [f"RL's 8 directions: {_r('top8_math31'):.2f} RMS", f"8 random directions: {_r('rand8_math31'):.3f} RMS",
                       f"Think-SFT's 8 directions: {_r('top8x0.02_think_sft'):.2f} RMS",
                       f"Each {_pct('top8_math31')} of the weight norm.", f"Base residual norm: {DATA['base_rms']:.1f}."]},
    "direction": {"big": round(_E["top8_code31"]["cos_with_math"], 2), "dec": 2, "suffix": "",
                  "u": ["cosine with RL's mean shift:", "RL-Code, the closest other reward"],
                  "lines": [f"RL at sizes 0.5 to 3: {min(_cos_pos):.2f} to {max(_cos_pos):.2f}", f"RL at size −1: {_c('top8xm1_math31')}",
                            f"Math 3.0 {_c('top8_math30')} · General {_c('top8_general30')} · IF {_c('top8_if30')}",
                            f"Think-SFT {_c('top8x0.02_think_sft')} · random about 0",
                            f"Predicted for IF: above {DATA['P3']['predicted_if']}. Refuted."]},
    "cutoffs": {"big": round(_P["rho_projection"], 2), "dec": 2, "suffix": "",
                "u": ["rank correlation with cut-off", f"answers, {_P['n_edits']} edits that are not random"],
                "lines": [f"Predicted: at most {_m(_P['predicted'])}. Refuted.", f"Size of the mean shift alone: {_rn}.",
                          f"Within the plan's {_P['margin']} margin: no gain.",
                          f"Base + cue: {_B['cut']} cut off · RL: {_RL['cut']}", f"{DATA['n']} harder problems, T 1.0"]},
}

# Not from our runs: the closest published result, fetched with tools/exa.py (arXiv 2607.01125, ZO-Act, section 3
# Methodology): a weight perturbation outside the dominant subspace of a layer's inputs is "largely suppressed by the
# small singular values" of the inputs and "has limited effect on the layer output".
_FIN = "/finding/the-finish-dial"
PANELS = [
    ["new", "What is new",
     "A weight change moves a layer's output only through the inputs the layer receives: ZO-Act (arXiv 2607.01125, section 3) "
     "notes that changes outside the main input directions have limited effect. New here: RL's own 8 largest directions per "
     "matrix line up with the inputs that the base model's activations supply, so they move the layer's output.",
     [f"At {_pct('top8_math31')} of the weight norm, RL's 8 directions shift the residual stream at layer {DATA['layer']} by "
      f"{_r('top8_math31'):.2f} (RMS over {DATA['positions']:,} positions); 8 random directions of the same norm by "
      f"{_r('rand8_math31'):.3f}, {round(RATIO)} times less. The base's residual stream there has norm {DATA['base_rms']:.1f}.",
      f"The 8 largest directions of the imitation-trained model (Think-SFT), scaled to the same norm, shift it by {_r('top8x0.02_think_sft'):.2f}: "
      f"{_r('top8_math31') / _r('top8x0.02_think_sft'):.1f} times less than RL's.",
      f"The page \"The finish dial\" shows what the same edits do to the answers: RL's 8 directions at 1.5 times their size "
      f"bring the base model with the opening cue "
      f"to {_E['top8x1.5_math31']['right_v3']} of {DATA['n']} harder problems right, with {_E['top8x1.5_math31']['cap_hits']} "
      "cut off."],
     [_FIN, "The finish dial: the same edits on the answers ›"]],
    ["why", "Why it matters",
     "The 8 directions that set how often answers finish act on inputs the base model already produces; a change of the same "
     "size in a random direction barely moves the model.",
     ["This narrows where a method without reward has to look: among the directions the base's own activations occupy, not "
      "anywhere in weight space.",
      f"Models trained with other rewards move the residual stream each in its own way. The mean shift of the 8 directions "
      f"of RL-Code (trained on code) has cosine {_c('top8_code31')} with RL's; RL-Zero-Math 3.0 {_c('top8_math30')}, "
      f"General (general chat) {_c('top8_general30')}, IF (instruction following) {_c('top8_if30')}.",
      "Still open: which input directions RL's change reads, and whether they can be found from the base's activations "
      "alone."]],
    ["how", "How we know",
     f"We ran {DATA['inputs']} stored answers of Base + cue to the {DATA['n']} harder problems through the base model and "
     "through each of 28 weight edits, without generating, and compared the residual stream. Of these answers "
     f"{DATA['cap_hit_inputs']} were cut off and {DATA['inputs'] - DATA['cap_hit_inputs']} finished; we used the first "
     f"{DATA['answer_tokens']:,} tokens of each.",
     [f"Shift = edited minus base residual stream at layer {DATA['layer']} (fixed before the run), at every "
      f"{DATA['step']}th answer token: {DATA['positions']:,} positions. Size is the RMS of its norm over positions.",
      f"At sizes 1, 1.5, 2 and 3, RL's shift is {', '.join(str(round(_TIMES[k])) for k in ('top8_math31', 'top8x1.5_math31', 'top8x2_math31'))} "
      f"and {round(_TIMES['top8x3_math31'])} times the random edit's of the same norm; at size −1, "
      f"{round(_TIMES['top8xm1_math31'])} times.",
      f"An edit of layers 22 to 31 at size 1.5 shifts layer 24 by {_r('top8x1.5_L22-31_math31'):.2f}, against "
      f"{_r('top8x1.5_math31'):.2f} for all layers: most of the shift builds up in the layers below 24.",
      "Each edit is exactly the weight change of a model whose answers were scored on the page \"The finish dial\" (or "
      f"of one of its controls); its norm matches that model's to {DATA['add_rel_match']:.0e} (relative). Cut-off counts "
      "come from those scored models: Base + cue with the edit, the "
      f"{DATA['n']} harder problems, one answer each, T 1.0, cut off at {DATA['cap']:,} tokens.",
      "Selftests on the real model passed before the run: a zero edit shifts nothing, the weights are restored exactly, and "
      "a planted direction is found with cosine 1.0000."]],
    ["limits", "What it does not show",
     "The prediction filed before the run failed: one shared direction does not predict cut-off answers better than the plain size of the "
     "shift.",
     [f"Over the {_P['n_edits']} edits that are not random, the rank correlation of the projection on the shared direction "
      f"with cut-offs is {_rp}; the plan predicted at most {_m(_P['predicted'])}. The size of the mean shift alone gives "
      f"{_rn}, within the margin of {_P['margin']} that the plan set, so the shared direction adds nothing.",
      f"The mean direction holds only {100 * min(_frac):.0f} to {100 * max(_frac):.0f} % of the summed squared shift of RL's "
      "directions at sizes −1 to 3: most of the shift differs from one position to the next.",
      f"RL's directions in layers 0 to 10 at size 1.5 shift layer 24 by {_r('top8x1.5_L0-10_math31'):.2f}, as much as all "
      f"layers at size 1, yet leave {_E['top8x1.5_L0-10_math31']['cap_hits']} answers cut off, more than Base + cue's {_B['cut']}.",
      f"The prediction that other rewards share RL's direction failed for IF: cosine {_c('top8_if30')}, predicted above "
      f"{DATA['P3']['predicted_if']}.",
      "The base model ran in 32-bit floating point with the edit added exactly. The scored models stored their weights in "
      "16-bit floating point (BF16) with stochastic rounding, so their edits carry rounding noise of about the edit's own "
      "size. This noise may weaken the link between the shifts measured here and their cut-off counts.",
      f"{DATA['inputs']} answers and one layer. The answers are Base + cue's own text, not the edited models' answers."]],
    ["run", "How to reproduce it",
     f"One GPU job computes every number: python -m studies.rlneurons.jobs.xshift --commit {DATA['job_commit'][:7]}, then "
     "the numpy readout studies/rlneurons/analysis/xshift.py.",
     [f"Job {DATA['job']}, one H100, {DATA['wall_s'] / 60:.0f} minutes; the plan, written before the run: {DATA['spec']}.",
      f"Readout: {DATA['readout']} (commit {DATA['commit'][:7]}); {DATA['readme']}.",
      "uv run python tools/finding_rl_directions_move_activations.py checks every number on this page against the readout."]],
]

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
/* The tokens and the light of tools/architecture.py: one lit plate, glass in a dark room, porcelain on a grey table with
   a cast shadow in place of the glow. The light comes from the upper left in both. RL's directions are lit (blue). */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --base-tone: #6b7882; --grid: rgba(16, 24, 32, .08);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --base-tone: #b7c2ca; --grid: rgba(255, 255, 255, .06);
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
  gap: 0; height: 100vh; min-height: 620px; max-width: 1840px; margin: 0 auto; padding: 20px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: one plate with one mark per weight edit, the readout beside the chart, and the one control under it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
.cap0 { margin: 0 0 4px 2.4%; font-size: 13px; line-height: 1.4; color: var(--mute); max-width: 76ch; }
svg { width: 100%; max-height: calc(100vh - 250px); display: block; overflow: visible; touch-action: pan-y; cursor: default; user-select: none; -webkit-user-select: none; }
svg:focus:not(:focus-visible) { outline: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.frame { fill: none; stroke: var(--faint); stroke-width: 1; opacity: .55; }
.grid { fill: none; stroke: var(--grid); stroke-width: 1; }
.tick { fill: var(--faint) !important; font-weight: 520; }
.title { fill: var(--mute) !important; font-weight: 600; }
.refl { fill: none; stroke: var(--mute); stroke-width: 1; stroke-dasharray: 4 4; opacity: .7; }
.reft { fill: var(--mute) !important; font-weight: 600; }
.m { stroke-linecap: round; transition: opacity .3s ease; }
.m.rl { fill: var(--blue); }
.m.part { fill: none; stroke: var(--blue); stroke-width: 1.4; opacity: .72; }
.m.reward { fill: var(--base-tone); opacity: .9; }
.m.sft { fill: var(--sheet); stroke: var(--ink); stroke-width: 1.9; }
.m.rand { fill: none; stroke: var(--base-tone); stroke-width: 1.4; }
.mh { fill: var(--blue); opacity: calc(var(--bloom) * .16); transition: opacity .3s ease; }
.ml { font-weight: 560; fill: var(--mute) !important; transition: opacity .3s ease; }
.ml.rl { fill: var(--blue) !important; font-weight: 640; }
.ml.sft, .ml.reward { fill: var(--ink) !important; }
.sr { fill: none; stroke-linecap: round; stroke-linejoin: round; transition: opacity .3s ease; }
.sr.rl { stroke: var(--blue); stroke-width: 2.2; }
.sr.rlg { stroke: var(--blue); stroke-width: 9; opacity: calc(var(--bloom) * .12); }
.sr.rand { stroke: var(--base-tone); stroke-width: 1.4; stroke-dasharray: 4 4; opacity: .8; }
.sl { font-weight: 640; }
.sl.rl { fill: var(--blue) !important; } .sl.rand { fill: var(--mute) !important; }
.br { fill: none; stroke: var(--ink); stroke-width: 1.3; }
.brt { font-weight: 700; letter-spacing: -.02em; }
.sel { fill: none; stroke: var(--ink); stroke-width: 1.6; }
.selh { fill: var(--blue); opacity: calc(var(--bloom) * .2); }
.big { font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; }
.lab { fill: var(--mute) !important; font-weight: 520; }
.lab.em { fill: var(--ink) !important; font-weight: 620; }
.keyt { fill: var(--mute) !important; font-weight: 520; }

/* The control: one switch of three views */
.control { align-self: center; display: flex; flex-direction: column; align-items: center; margin-top: 14px; }
.switch { display: inline-flex; border: 1px solid var(--ink); border-radius: 999px; padding: 3px; }
.switch button { padding: 7px 18px; border-radius: 999px; font-weight: 600; font-size: 14.5px; white-space: nowrap; transition: background .2s ease, color .2s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.hint { margin: 10px 0 0; font-size: 13.5px; color: var(--mute); text-align: center; max-width: 70ch; min-height: 2.8em; }

/* One drawn entrance, then only the slow sway and what the reader changes */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .axes { animation: fade .8s .3s both; }
.enter .read { animation: fade .7s .5s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.paper { margin: 18px 0 0; font-size: 15px; }
.paper a { color: var(--mute); text-decoration: none; border-bottom: 1px solid currentColor; padding-bottom: 1px; }
.paper a:hover, .paper a:focus-visible { color: inherit; }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 0 6px 12px 0; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.lead.q { font-size: 15.5px; line-height: 1.45; color: var(--mute); max-width: 44ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.vals { list-style: none; margin: 16px 0 0; padding: 0; font-size: 14px; color: var(--mute); max-width: 44ch; }
.vals li { display: grid; grid-template-columns: 10.5em 1fr; align-items: baseline; gap: 12px; padding: 7px 0; border-top: 1px solid var(--rule); }
.vals b { color: var(--ink); font-weight: 650; }
.vals b.rl { color: var(--blue); }
.sub { margin: 18px 0 0; font-size: 13px; color: var(--mute); max-width: 44ch; }
.sub b { color: var(--ink); font-weight: 640; }
.toks { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 0; padding: 0; list-style: none; max-width: 44ch; }
.toks li { font-size: 13.5px; padding: 3px 9px; border-radius: 999px; border: 1px solid var(--rule); color: var(--ink); white-space: nowrap; }
.toks li small { color: var(--faint); font-size: 12px; margin-left: 5px; }
.toks.up li { border-color: color-mix(in oklab, var(--blue) 45%, transparent); }
.steps { display: flex; justify-content: space-between; margin-top: 16px; font-size: 13px; color: var(--mute); }
.steps button:hover { color: var(--ink); }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: block; }
  .cap0 { margin: 0 0 8px; }
  .pane { order: 4; margin-top: 22px; }
  .paper { order: 5; }
  svg { max-height: none; }
  .control { width: 100%; }
  .switch { display: grid; grid-template-columns: 1fr 1fr 1fr; border-radius: 22px; width: 100%; }
  .switch button { text-align: center; white-space: normal; line-height: 1.2; padding: 8px 6px; font-size: 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a, .m, .mh, .ml, .sr { transition: none; }
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
    <p class="cap0">One mark per weight edit added to the base, measured on 48 stored answers. Residual stream: the model's running internal state at a layer.</p>
    <svg id="svg" role="img" tabindex="0"></svg>
    <div class="control">
      <div class="switch" role="group" aria-label="What the picture shows">
        <button data-view="size" aria-pressed="true">Size of the shift</button>
        <button data-view="direction" aria-pressed="false">Its direction</button>
        <button data-view="cutoffs" aria-pressed="false">Cut-off answers</button>
      </div>
      <p class="hint" id="hint"></p>
    </div>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
    <p class="paper"><a href="/finding/the-finish-dial">The finish dial: the same edits on the answers ›</a></p>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2, clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const num = v => String(v).replace("-", "−"), LOG = Math.log10;

/* The 28 edits, in the order of the side column (C.edits: key, group, label, name, what), each with its readout row. */
const M = C.edits.map(([key, group, label, name, what], j) => ({ key, group, label, name, what, j, ...D.edits[key] }));
const IDX = Object.fromEntries(M.map((m, j) => [m.key, j]));
const ORDER = ["part", "reward", "rand", "sft", "rl"];  // drawn back to front
const VIEWS = ["size", "direction", "cutoffs"];
const RL_LINE = ["top8x0.5_math31", "top8_math31", "top8x1.5_math31", "top8x2_math31", "top8x3_math31"];
const RAND_LINE = ["rand8_math31", "rand8x1.5_math31", "rand8x2_math31", "rand8x3_math31"];

/* The three views: what x and y show, their ranges and ticks, and the reference lines. */
const pc = m => 100 * m.add_rel;
const AX = {
  size: { x: pc, xd: [0, .235], xt: [0, .05, .1, .15, .2], xf: v => v ? `${v.toFixed(2)} %` : "0",
    xl: "Size of the weight change, % of the weight norm", y: m => LOG(m.rms_shift), yd: [LOG(.03), LOG(70)],
    yt: [.1, 1, 10].map(LOG), yf: v => String(Math.round(10 ** v * 10) / 10), yl: "Shift of the residual stream at layer 24, RMS (log scale)", ys: "Residual stream shift, layer 24 (log scale)",
    refs: [{ v: LOG(D.base_rms), t: `Base residual norm ${D.base_rms.toFixed(1)}` }],
    hint: "Higher: the edit moves the model's internal state more. At the same weight norm, the random directions stay near the floor." },
  direction: { x: pc, xd: [0, .235], xt: [0, .05, .1, .15, .2], xf: v => v ? `${v.toFixed(2)} %` : "0",
    xl: "Size of the weight change, % of the weight norm", y: m => m.cos_with_math, yd: [-1.08, 1.08],
    yt: [-1, -.5, 0, .5, 1], yf: v => num(v), yl: "Cosine of the mean shift with RL's at size 1",
    refs: [{ v: 0, t: "" }],
    hint: "Higher: the edit moves the internal state the same way as RL's 8 directions. Other rewards' directions point elsewhere." },
  cutoffs: { x: m => m.projection_p1, xd: [-.8, 2.8], xt: [-.5, 0, 1, 2], xf: v => num(v),
    xl: "Projection of the mean shift on one shared direction", xs: "Projection on one shared direction", y: m => m.cap_hits, yd: [0, 105],
    yt: [0, 25, 50, 75, 100], yf: String, yl: `Answers cut off at 16,384 tokens, of ${D.n} harder problems`, ys: `Cut off at 16,384 tokens, of ${D.n}`,
    refs: [{ v: D.base_cue.cut, t: `Base + cue ${D.base_cue.cut}` }, { v: D.rl.cut, t: `RL ${D.rl.cut}` }],
    hint: "The prediction: edits that push further along one shared direction leave fewer answers cut off. It did no better than the plain size of the shift." },
};
/* Where a mark's label sits, per view: [dx, dy, anchor] in units of the small type; null hides it. */
const LAB = {
  rl: { size: [0, -1.05, "middle"], direction: [0, 1.6, "middle"], cutoffs: [.75, -.5, "start"] },
  "top8xm1_math31": { size: [0, 1.6, "middle"], direction: [.8, .35, "start"], cutoffs: [-.8, .35, "end"] },
  sft: { size: [.8, .35, "start"], direction: [-.8, 1.1, "end"], cutoffs: [-.8, .35, "end"] },
  reward: { size: null, direction: [.75, .35, "start"], cutoffs: null },
  "top8x1.5_L0-10_math31": { size: null, direction: null, cutoffs: [.8, .35, "start"] },
};
const labAt = (m, v) => S.g.phone && v === "cutoffs" && m.group === "sft" ? null : (LAB[m.key] || LAB[m.group] || {})[v] || null;  // on a phone the key names Think-SFT there

/* Geometry: the plate and the chart in a small 3D space around the plate's centre (x right, y down, z toward the viewer).
   The chart on the left, the readout on the right (on a phone, the readout above the chart). */
function geo() {
  const ph = narrow.matches;
  const g = ph
    ? { w: 480, h: 900, cx: 240, D: 2400, r: 22, deep: 30, blur: 12, X0: 84, X1: 450, Y0: 404, Y1: 696, fs: 18, fsm: 17, fb: 84,
        mr: 1.3, rx: 30, bigY: 108, uY: [144, 168], lY: [208, 233, 258, 283, 308], ylY: 364, tickY: 724, titleY: 756,
        key: { y: 800, cols: 2 }, hit: 24, phone: true }
    : { w: 1000, h: 640, cx: 500, D: 2200, r: 30, deep: 40, blur: 16, X0: 112, X1: 618, Y0: 80, Y1: 474, fs: 15, fsm: 13,
        fb: 104, mr: 1, rx: 676, bigY: 176, uY: [210, 230], lY: [276, 300, 324, 348, 372], ylY: 54, tickY: 498, titleY: 528,
        key: { y: 584, cols: 5 }, hit: 16 };
  g.cy = g.h / 2;
  g.a = ph ? [6, 8, g.w - 6, g.h - 8] : [24, 18, g.w - 24, g.h - 18];
  g.X = (v, x) => g.X0 + (clamp(x, ...AX[v].xd) - AX[v].xd[0]) / (AX[v].xd[1] - AX[v].xd[0]) * (g.X1 - g.X0);
  g.Y = (v, y) => g.Y1 - (clamp(y, ...AX[v].yd) - AX[v].yd[0]) / (AX[v].yd[1] - AX[v].yd[0]) * (g.Y1 - g.Y0);
  return g;
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k];
}
function rounded(g, [x0, y0, x1, y1], r, z) {  // a rounded rectangle at depth z
  const p = [], corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}
const line = pts => pts.length ? "M" + pts.map(q => f(q[0]) + " " + f(q[1])).join("L") : "";
const KEY = [["rl", "RL's 8 directions"], ["part", "Parts of RL's change"], ["reward", "Other rewards"],
  ["sft", "Think-SFT"], ["rand", "Random, same norm"]];
const RADIUS = { rl: 6.5, part: 4.4, reward: 5.4, sft: 5.6, rand: 4.2 };

const S = { view: "size", prev: "size", t0: -1e9, dur: 720, stag: 14, open: null, g: null, el: {}, shown: {}, from: [], to: [], rank: [],
  scr: [], last: 0, t: 0, touched: false, keyX: [] };

function build() {
  const g = S.g = geo(), svg = $("svg"), [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  const axes = VIEWS.map(v => { const A = AX[v]; return `<g id="ax-${v}" opacity="0"><path class="grid" id="gr-${v}"/>` +
    A.yt.map((_, i) => `<text class="tick" id="ty-${v}-${i}" font-size="${g.fsm}" text-anchor="end">${esc(A.yf(A.yt[i]))}</text>`).join("") +
    A.xt.map((_, i) => `<text class="tick" id="tx-${v}-${i}" font-size="${g.fsm}" text-anchor="middle">${esc(A.xf(A.xt[i]))}</text>`).join("") +
    A.refs.map((r, i) => `<path class="refl" id="rf-${v}-${i}"/><text class="reft" id="rt-${v}-${i}" font-size="${g.fsm}" text-anchor="end">${esc(r.t)}</text>`).join("") +
    `<text class="title" id="yl-${v}" font-size="${g.fsm}">${esc(g.phone && A.ys || A.yl)}</text>` +
    `<text class="title" id="xl-${v}" font-size="${g.fsm}" text-anchor="middle">${esc(g.phone && A.xs || A.xl)}</text></g>`; }).join("");
  const order = M.map((_, k) => k).sort((a, b) => ORDER.indexOf(M[a].group) - ORDER.indexOf(M[b].group));
  const marks = order.map(k => { const m = M[k], r = RADIUS[m.group] * g.mr;
    return (m.group === "rl" ? `<circle class="mh" id="mh${k}" r="${f(r * 2)}"/>` : "") + `<circle class="m ${m.group}" id="m${k}" r="${f(r)}"/>`; }).join("");
  const labels = M.map((m, k) => m.label ? `<text class="ml ${m.group}" id="ml${k}" font-size="${g.fsm}">${esc(m.label)}</text>` : "").join("");
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${f(g.cy)}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .04)}" width="${aw}" height="${f(ah)}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .3)}" cy="${f(ay0 + ah * .24)}" rx="${f(aw * .3)}" ry="${f(ah * .2)}" transform="rotate(-14 ${f(ax0 + aw * .3)} ${f(ay0 + ah * .24)})" fill="url(#spec)"/>` +
    `<g class="axes"><path class="frame" id="frame"/>${axes}</g>` +
    `<g class="data"><path class="sr rlg" id="srg"/><path class="sr rand" id="srr"/><path class="sr rl" id="srl"/>` +
    `<circle class="selh" id="selh" r="0"/>${marks}<circle class="sel" id="sel" r="0"/>${labels}` +
    `<text class="sl rl" id="slr" font-size="${g.fsm}">RL's 8 directions${g.phone ? "" : ", by size"}</text><text class="sl rand" id="sla" font-size="${g.fsm}" text-anchor="end">8 random directions</text>` +
    `<path class="br" id="br"/><text class="brt" id="brt" font-size="${f(g.fs * 1.5)}" text-anchor="end"></text></g>` +
    `<g class="read"><text class="big" id="big" font-size="${g.fb}"></text>` +
    `<text class="lab em" id="u0" font-size="${g.fs}"></text><text class="lab" id="u1" font-size="${g.fs}"></text>` +
    [0, 1, 2, 3, 4].map(i => `<text class="lab${i === 0 ? " em" : ""}" id="l${i}" font-size="${g.fs * .96}"></text>`).join("") + `</g>` +
    `<g class="key">${KEY.map(([grp, t], i) => `<circle class="m ${grp}" id="kg${i}" r="${f(RADIUS[grp] * g.mr)}"/><text class="keyt" id="kt${i}" font-size="${g.fsm}">${esc(t)}</text>`).join("")}</g>`;
  S.el = {}; S.shown = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  measureKey();
}
function measureKey() {  // the key's entries centred in rows: one row on a desktop, rows of at most 3 on a phone
  const g = S.g, K = g.key, gap = 22 * g.mr, w = KEY.map((_, i) => (S.el["kt" + i].getComputedTextLength() || 120) + 13 * g.mr + gap);
  S.keyX = [];
  for (let i0 = 0, row = 0; i0 < KEY.length; i0 += K.cols, row++) {
    const ws = w.slice(i0, i0 + K.cols), total = ws.reduce((a, b) => a + b, 0) - gap;
    let x = (g.w - total) / 2 + 5 * g.mr;
    ws.forEach(wi => { S.keyX.push([x, K.y + row * 32]); x += wi; });
  }
}

/* Where each mark is in its change: it travels from its old place to its new one along an eased path, lifting toward the
   viewer on the way; it starts 14 ms later per place from the left and takes 0.72 s. */
function markAt(k, now) {
  const p = clamp((now - S.t0 - S.stag * S.rank[k]) / S.dur, 0, 1), e = ease(p), a = S.from[k], b = S.to[k];
  const moved = a[0] !== b[0] || a[1] !== b[1];
  return { x: mix(a[0], b[0], e), y: mix(a[1], b[1], e), z: moved ? 26 * Math.sin(Math.PI * p) : 0 };
}
const target = v => M.map(m => [S.g.X(v, AX[v].x(m)), S.g.Y(v, AX[v].y(m))]);
const fmtBig = (R, x) => `${num(x.toFixed(R.dec))}${R.suffix}`;

function place(t, now) {
  const g = S.g, E = S.el, at = (el, q, dy) => { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1] + (dy || 0))); };
  const text = (id, v) => { if (S.shown[id] !== v) { E[id].textContent = S.shown[id] = v; } };
  const P = (x, y, z = 6) => proj(g, x, y, z);
  E.back.setAttribute("d", rounded(g, g.a, g.r, -g.deep));
  E.plate.setAttribute("d", rounded(g, g.a, g.r, 0));
  E.frame.setAttribute("d", line([P(g.X0, g.Y0 - 8), P(g.X0, g.Y1), P(g.X1 + 8, g.Y1)]));
  const e = ease(clamp((now - S.t0) / 700, 0, 1));
  const op = v => v === S.view ? (S.prev === v ? 1 : clamp(2 * e - 1, 0, 1)) : v === S.prev ? clamp(1 - 2 * e, 0, 1) : 0;  // the old axes go, then the new ones come

  // The axes of each view cross-fade; only a visible one is placed.
  VIEWS.forEach(v => {
    const o = op(v), A = AX[v], G = E["ax-" + v];
    if (S.shown["o" + v] !== o.toFixed(3)) { G.setAttribute("opacity", o.toFixed(3)); S.shown["o" + v] = o.toFixed(3); }
    if (o < .005) return;
    E["gr-" + v].setAttribute("d", A.yt.map(y => line([P(g.X0, g.Y(v, y), 4), P(g.X1, g.Y(v, y), 4)])).join(""));
    A.yt.forEach((y, i) => at(E[`ty-${v}-${i}`], P(g.X0 - 10, g.Y(v, y)), g.fsm * .35));
    A.xt.forEach((x, i) => at(E[`tx-${v}-${i}`], P(g.X(v, x), g.tickY)));
    A.refs.forEach((r, i) => { const y = g.Y(v, r.v); E[`rf-${v}-${i}`].setAttribute("d", line([P(g.X0, y, 5), P(g.X1, y, 5)])); at(E[`rt-${v}-${i}`], P(g.X1 - 4, y - 6, 5)); });
    at(E["yl-" + v], P(g.phone ? g.X0 - 50 : 40, g.ylY));
    at(E["xl-" + v], P((g.X0 + g.X1) / 2, g.titleY));
  });

  // The marks, their labels and the two lines through RL's sizes and the random sizes.
  const sel = S.open != null && IDX[S.open] != null ? IDX[S.open] : -1;
  M.forEach((m, k) => {
    const q = markAt(k, now), s = P(q.x, q.y, 8 + q.z), c = E["m" + k], dim = sel >= 0 && sel !== k;
    S.scr[k] = s;
    c.setAttribute("cx", f(s[0])); c.setAttribute("cy", f(s[1]));
    c.style.opacity = dim ? ".22" : "";
    if (E["mh" + k]) { E["mh" + k].setAttribute("cx", f(s[0])); E["mh" + k].setAttribute("cy", f(s[1])); E["mh" + k].style.opacity = dim ? "0" : ""; }
    const L = E["ml" + k];
    if (!L) return;
    // a label shown in both views slides to its new side; one shown in one view only fades in or out
    const a = labAt(m, S.prev), b = labAt(m, S.view);
    if (!a && !b) { L.style.opacity = "0"; return; }
    const lo = b ? (a ? 1 : e) : 1 - e;
    const pos = b || a, dx = a && b ? mix(a[0], b[0], e) : pos[0], dy = a && b ? mix(a[1], b[1], e) : pos[1];
    L.setAttribute("text-anchor", (e < .5 && a ? a : pos)[2]);
    at(L, [s[0] + dx * g.fsm, s[1] + dy * g.fsm]);
    L.style.opacity = dim ? String(.22 * lo) : String(lo);
  });
  const pts = keys => keys.map(k => S.scr[IDX[k]]);
  E.srl.setAttribute("d", line(pts(RL_LINE))); E.srg.setAttribute("d", line(pts(RL_LINE))); E.srr.setAttribute("d", line(pts(RAND_LINE)));
  const lineOp = sel >= 0 ? ".25" : "";
  [E.srl, E.srg, E.srr].forEach(el => { el.style.opacity = lineOp; });
  { // RL's line is named under its last segment (above it in the cut-off view); the random line above its end (under it in the direction view)
    const a2 = S.scr[IDX["top8x2_math31"]], a3 = S.scr[IDX["top8x3_math31"]], b = S.scr[IDX["rand8x3_math31"]];
    const dyOf = (tab, v) => tab[v] * g.fsm, RLD = { size: 1.9, direction: 1.9, cutoffs: -1.2 }, RAD2 = { size: -1.1, direction: 1.6, cutoffs: 1.6 };
    // in the cut-off view it sits right of the segment from size 1 to 1.5, where the plate is empty
    const a1 = S.scr[IDX["top8_math31"]], a15 = S.scr[IDX["top8x1.5_math31"]];
    const spot = v => v === "cutoffs" ? [(a1[0] + a15[0]) / 2 + g.fsm * 7.6, (a1[1] + a15[1]) / 2 + g.fsm * .3] : [(a2[0] + a3[0]) / 2, (a2[1] + a3[1]) / 2 + dyOf(RLD, v)];
    const sp = spot(S.prev), sv = spot(S.view);
    at(E.slr, [mix(sp[0], sv[0], e), mix(sp[1], sv[1], e)]); E.slr.setAttribute("text-anchor", "middle");
    at(E.sla, [b[0] + g.fsm * .3, b[1] + mix(dyOf(RAD2, S.prev), dyOf(RAD2, S.view), e)]);
    const vis = v => (v === "cutoffs" ? 0 : 1), so = mix(vis(S.prev), vis(S.view), e);
    const rv = v => (g.phone && v === "cutoffs" ? 0 : 1);  // on a phone the cut-off view has no room for RL's line name
    E.slr.style.opacity = String(mix(rv(S.prev), rv(S.view), e) * (sel >= 0 ? .22 : 1)); E.sla.style.opacity = String(so * (sel >= 0 ? .22 : 1)); }
  if (sel >= 0) {
    const s = S.scr[sel];
    E.sel.setAttribute("cx", f(s[0])); E.sel.setAttribute("cy", f(s[1])); E.sel.setAttribute("r", f(12 * g.mr));
    E.selh.setAttribute("cx", f(s[0])); E.selh.setAttribute("cy", f(s[1]));
    E.selh.setAttribute("r", f(g.mr * (still.matches ? 18 : 18 + 2.5 * Math.sin(t * 1.6))));
  } else { E.sel.setAttribute("r", "0"); E.selh.setAttribute("r", "0"); }

  // The bracket of the size view: RL's 8 directions at size 1 against the random edit of the same norm.
  { const a = S.scr[IDX["top8_math31"]], b = S.scr[IDX["rand8_math31"]], x = Math.min(a[0], b[0]) - 14 * g.mr;
    const o = S.view === "size" && S.prev === "size" ? 1 : S.view === "size" ? e : S.prev === "size" ? 1 - e : 0;
    E.br.setAttribute("d", `M${f(x + 5)} ${f(a[1])}H${f(x)}V${f(b[1])}H${f(x + 5)}`);
    at(E.brt, [x - 7, (a[1] + b[1]) / 2], g.fs * .5);
    text("brt", C.read.size.big + "×");
    const bo = o * (sel >= 0 ? .22 : 1);
    E.br.style.opacity = bo.toFixed(3); E.brt.style.opacity = bo.toFixed(3); }

  // The readout: the words of the view arrive with its number, which counts from 0 and stops within 0.9 s.
  const R = C.read[S.view], pc2 = ease(clamp((now - S.t0 - (S.rise ? 350 : 0)) / 900, 0, 1));
  text("big", fmtBig(R, R.big * pc2));
  at(E.big, P(g.rx, g.bigY, 10));
  text("u0", R.u[0]); text("u1", R.u[1]);
  at(E.u0, P(g.rx + 4, g.uY[0], 10)); at(E.u1, P(g.rx + 4, g.uY[1], 10));
  R.lines.forEach((s, i) => { text("l" + i, s); at(E["l" + i], P(g.rx + 4, g.lY[i], 10)); });

  // The key.
  KEY.forEach((_, i) => { const [x, y] = S.keyX[i], c = P(x, y, 6), tt = P(x + 13 * g.mr, y, 6);
    E["kg" + i].setAttribute("cx", f(c[0])); E["kg" + i].setAttribute("cy", f(c[1])); at(E["kt" + i], tt, g.fsm * .35); });
}

/* Always on: the plate sways by a few degrees and leans toward the mouse. About 30 frames a second. With reduced motion
   the page shows one still frame per state. */
function frame(now) {
  requestAnimationFrame(frame);
  if (still.matches || now - S.last < 30) return;
  S.last = now;
  const t = S.t = now / 1000;
  V.px += (V.tx - V.px) * .1; V.py += (V.ty - V.py) * .1;
  aim(4 * Math.sin(t * .13) + 3.5 * V.px, 2 * Math.sin(t * .09) - 2 * V.py);
  place(t, now);
}

function setView(view, opts = {}) {
  const now = performance.now(), quick = still.matches || opts.instant;
  const cur = quick || !S.to.length ? null : M.map((_, k) => markAt(k, now));
  S.to = target(view);
  S.from = cur ? cur.map(q => [q.x, q.y]) : opts.rise && !quick ? S.to.map(([x]) => [x, S.g.Y1]) : S.to.slice();
  M.map((_, k) => k).sort((a, b) => S.to[a][0] - S.to[b][0] || a - b).forEach((k, r) => { S.rank[k] = r; });
  S.rise = !!opts.rise && !quick;
  S.dur = S.rise ? 1050 : 720; S.stag = S.rise ? 22 : 14;
  S.prev = quick ? view : S.view; S.view = view;
  S.t0 = quick ? -1e9 : now + (S.rise ? 500 : 0);
  document.querySelectorAll("[data-view]").forEach(b => b.setAttribute("aria-pressed", b.dataset.view === view));
  if (S.shown.hint !== view) {
    S.shown.hint = view; $("hint").textContent = AX[view].hint;
    if (!quick) $("hint").animate([{ opacity: 0 }, { opacity: 1 }], { duration: 500, easing: "ease-out" });
  }
  const R = C.read[view];
  $("svg").setAttribute("aria-label", `${M.length} weight edits, one mark each. ${AX[view].yl} against ${AX[view].xl.toLowerCase()}. ` +
    `${fmtBig(R, R.big)} ${R.u.join(" ")}. ${R.lines.join(" ")} Arrow keys change the view; Enter opens RL's 8 directions at size 1.`);
  if (still.matches) { aim(0, 0); place(0, now); }
}

/* The side column: the five panels, or one edit. */
const sig = (x, d = 2) => num(x.toFixed(d));
const tok = s => s.replace(/\n/g, "↵").replace(/\t/g, "⇥").trim() || "␣";
const lv = v => num((v > 0 ? "+" : "") + (Math.abs(v) < .1 ? v.toFixed(3) : v.toFixed(2)));
function editPane(j) {
  const m = M[j], pair = C.pair[m.key], twin = C.twin[m.key];
  const rows = [
    ["Weight change", `<b>${(100 * m.add_rel).toFixed(3)} %</b> of the weight norm of its ${m.n_edited} matrices`],
    ["Shift at layer 24", `<b class="${m.group === "rl" ? "rl" : ""}">${sig(m.rms_shift, m.rms_shift < 1 ? 3 : 2)}</b> RMS; the base's residual norm is ${D.base_rms.toFixed(1)}`],
  ];
  if (pair) rows.push(["Random, same norm", `<b>${sig(M[IDX[pair]].rms_shift, 3)}</b>: ${Math.round(m.rms_shift / M[IDX[pair]].rms_shift)} times less`]);
  if (twin) rows.push(["RL's 8, same size", `<b>${sig(M[IDX[twin]].rms_shift)}</b>: ${Math.round(M[IDX[twin]].rms_shift / m.rms_shift)} times more`]);
  rows.push(["Mean shift", `<b>${sig(m.mean_shift_norm, m.mean_shift_norm < .1 ? 3 : 2)}</b>; ${(100 * m.frac_mean_dir).toFixed(0)} % of the shift lies along it`],
    ["Cosine with RL's mean shift", `<b>${sig(m.cos_with_math)}</b>`],
    ["Projection on the shared direction", `<b>${sig(m.projection_p1, Math.abs(m.projection_p1) < .01 ? 4 : 2)}</b> (on ${m.p1_direction === "top8_code31" ? "RL-Code's" : "RL's"} mean shift)`],
    [`${D.n} harder problems`, `<b>${m.right_v3} of ${D.n}</b> right, <b>${m.cap_hits}</b> cut off at 16,384 tokens`]);
  const chips = (xs, cls) => `<ul class="toks ${cls}">${xs.map(([t, v]) => `<li>${esc(tok(t))}<small>${lv(v)}</small></li>`).join("")}</ul>`;
  return `<div><div class="dhead"><h2>${esc(m.name)}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead q">${esc(m.what)}</p>` +
    `<ul class="vals">${rows.map(([a, b]) => `<li><span>${a}</span><span>${b}</span></li>`).join("")}</ul>` +
    `<p class="sub">The score is Base + cue with this edit, one answer per problem, T 1.0. The shift is measured on ${D.inputs} stored Base + cue answers, ${D.positions.toLocaleString("en-US")} positions.</p>` +
    `<p class="sub"><b>Logit lens.</b> The tokens the mean shift at the last layer raises most:</p>${chips(m.raised, "up")}` +
    `<p class="sub">and lowers most (raw logit change; all tokens share an offset):</p>${chips(m.lowered, "")}` +
    `<div class="steps"><button data-step="-1">‹ Previous edit</button><button data-step="1">Next edit ›</button></div></div>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open), j = S.open != null && IDX[S.open] != null ? IDX[S.open] : -1;
  $("pane").innerHTML = j >= 0 ? editPane(j) : p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>` + (p[4] ? `<p class="paper"><a href="${esc(p[4][0])}">${esc(p[4][1])}</a></p>` : "")
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
/* The view and what is open are one value in the address: #[direction/|cutoffs/][<panel>|<edit key>]. */
function address(push) {
  const parts = [S.view === "size" ? "" : S.view, S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const view = VIEWS.find(v => parts.includes(v)) || "size";
  S.open = parts.find(x => C.panels.some(p => p[0] === x) || IDX[x] != null) || null;
  if (first === true) setView(view, { instant: view !== "size" || !!S.open, rise: view === "size" && !S.open });
  else if (view !== S.view) setView(view);
  pane();
  if (still.matches) place(0, performance.now());
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ behavior: still.matches ? "auto" : "smooth", block: "start" }); };
function open(key) {
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  if (still.matches) place(0, performance.now());
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  else if (!key) $("svg").focus({ preventScroll: true });
}
function go(view) {
  S.touched = true;
  if (view === S.view) return;
  setView(view);
  address(false);
}

const svg = $("svg");
function svgPoint(e) { const m = svg.getScreenCTM().inverse(); return [m.a * e.clientX + m.c * e.clientY + m.e, m.b * e.clientX + m.d * e.clientY + m.f]; }
function nearest([x, y]) {
  let best = -1, bd = S.g.hit ** 2;
  S.scr.forEach((q, k) => { const d = (q[0] - x) ** 2 + (q[1] - y) ** 2; if (d < bd) { bd = d; best = k; } });
  return best;
}
svg.addEventListener("pointermove", e => { if (e.pointerType === "mouse") svg.style.cursor = nearest(svgPoint(e)) >= 0 ? "pointer" : "default"; });
svg.addEventListener("click", e => { const k = nearest(svgPoint(e)); if (k >= 0) { S.touched = true; open(M[k].key); show(); } });
document.addEventListener("click", e => {
  const v = e.target.closest("[data-view]"), o = e.target.closest("[data-open]"), s = e.target.closest("[data-step]");
  if (v) go(v.dataset.view);
  if (o) open(o.dataset.open);
  if (s) {
    const n = (IDX[S.open] + Number(s.dataset.step) + M.length) % M.length;
    open(M[n].key);
    $("pane").querySelector(`[data-step="${s.dataset.step}"]`).focus({ preventScroll: true });
  }
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey || /INPUT|TEXTAREA/.test(document.activeElement.tagName)) return;
  if (e.key === "Escape" && S.open) open("");
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") go(VIEWS[(VIEWS.indexOf(S.view) + (e.key === "ArrowRight" ? 1 : 2)) % 3]);
  if (e.key === "Enter" && document.activeElement === svg) { e.preventDefault(); open(M[0].key); show(); }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); setView(S.view, { instant: true }); place(S.t, performance.now()); });
still.addEventListener("change", () => { if (still.matches) { setView(S.view, { instant: true }); aim(0, 0); place(0, performance.now()); } });
document.fonts.ready.then(() => { measureKey(); S.shown = { hint: S.shown.hint }; place(S.t, performance.now()); });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1; V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
build();
aim(0, 0);
fromHash(true);
place(0, performance.now());
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
"""

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's picture reduced to a
# glass slab with a rising row of lit marks (RL's directions at growing sizes) over a flat row of plain marks on the floor
# (random directions of the same sizes). The lit row rises and settles about every 16 s.
ICON = r"""(kit, t, tilt) => {
  const th = 5, T = Number(t) || 0, s = .62 + .38 * Math.cos(T * .4);
  let out = kit.slab(44, 38, th) + kit.line(kit.at(-36, 24, th / 2), kit.at(36, 24, th / 2), .7, "plain", .8);
  for (let c = 0; c < 6; c++) {
    const u = -30 + c * 12, v = 18 - (16 + c * 5.5) * s;
    out += kit.line(kit.at(u - 1.2, 19, th / 2), kit.at(u + 1.2, 19, th / 2), 2.2, "plain", .7);
    out += kit.line(kit.at(u - 1.6, v, th / 2), kit.at(u + 1.6, v, th / 2), 3.6, "lit", 1);
  }
  return out;
}"""

_RAND_OF = {v: k for k, v in _PAIR.items()}
PAGE = PAGE.replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "edits": EDITS, "read": READ, "pair": _PAIR, "twin": _RAND_OF,
    "data": {k: DATA[k] for k in ("edits", "base_rms", "n", "inputs", "positions", "base_cue", "rl")}}, ensure_ascii=False))


def _spearman(a, b):  # rank correlation with average ranks for ties
    def ranks(x):
        order = sorted(range(len(x)), key=lambda i: x[i])
        r = [0.0] * len(x)
        i = 0
        while i < len(x):
            j = i
            while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
                j += 1
            for q in range(i, j + 1):
                r[order[q]] = (i + j) / 2
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return cov / (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** .5


if __name__ == "__main__":  # run from the repository root: every number of DATA against the artifacts; fails on a change
    ro, me, run = json.load(open(DATA["readout"])), json.load(open(DATA["metrics"])), json.load(open(DATA["run"]))
    cells = json.load(open(CELLS))["cells"]
    j = run["job"]
    assert (ro["job_id"], j["commit"], round(j["wall_s"], 1), j["models"]["base"]["repo"]) == \
        (DATA["job"], DATA["job_commit"], DATA["wall_s"], DATA["base_model"]), j
    assert DATA["answers_job"] in j["answers"]
    assert (ro["layer"], ro["inputs"], ro["positions"]["all"], ro["positions"]["cap_hit"], me["max_tokens"], me["step"]) == \
        (DATA["layer"], DATA["inputs"], DATA["positions"], DATA["cap_hit_inputs"] * DATA["positions"] // DATA["inputs"], DATA["answer_tokens"], DATA["step"])
    assert sum(i["cap_hit"] for i in me["inputs"]) == DATA["cap_hit_inputs"]
    assert round(ro["base_rms_norm_at_layer"], 4) == DATA["base_rms"] and float(f"{ro['max_abs_add_rel_difference_from_scored_cells']:.4e}") == DATA["add_rel_match"]
    assert all(t["pass"] for t in me["selftest"].values()), me["selftest"]
    P = ro["P1"]
    assert (P["n_edits"], round(P["rho_projection"], 4), round(P["rho_norm"], 4), P["refuted"], P["held"]) == \
        (DATA["P1"]["n_edits"], DATA["P1"]["rho_projection"], DATA["P1"]["rho_norm"], True, False), P
    assert ro["P3"]["held"] == DATA["P3"]["held"] and round(ro["P3"]["cos_if30_math31"], 4) == _E["top8_if30"]["cos_with_math"]
    spec = open(DATA["spec"]).read()
    assert "is at most -0.8" in spec and "|rho_norm| >= |rho_proj| - 0.05" in spec and "cosine(IF, Math 3.1) > 0.5" in spec
    assert set(_E) == set(ro["edits"]) == {e[0] for e in EDITS} and len(EDITS) == 28
    rnd = {"add_rel": 7, "rms_shift": 4, "mean_shift_norm": 4, "frac_mean_dir": 4, "cos_with_math": 4, "projection_p1": 6}
    for k, d in _E.items():
        e, L = ro["edits"][k], ro["logit_lens"][k]
        for field, n in rnd.items():
            assert round(e[field], n) == d[field], (k, field, e[field], d[field])
        assert (e["p1_direction"], e["cap_hits"], e["right_v3"], me["edits"][k]["n_edited"]) == \
            (d["p1_direction"], d["cap_hits"], d["right_v3"], d["n_edited"]), k
        assert (cells[k]["cap_hits"], cells[k]["right_v3"]) == (d["cap_hits"], d["right_v3"]), k  # the scored cell
        assert [[t, round(v, 3)] for t, v in L["raised"][:6]] == d["raised"] and [[t, round(v, 3)] for t, v in L["lowered"][:4]] == d["lowered"], k
    for name, cell in (("base_cue", "base_cue_T1"), ("rl", "rl_plain_T1")):
        c = cells[cell]
        assert (c["right_v3"], c["cap_hits"]) == (DATA[name]["right"], DATA[name]["cut"]), (name, c)
    # P1 again from the rows on the page: the 23 non-random edits
    rows = [d for k, d in _E.items() if not k.startswith("rand8")]
    assert len(rows) == DATA["P1"]["n_edits"]
    cut = [d["cap_hits"] for d in rows]
    assert round(_spearman([d["projection_p1"] for d in rows], cut), 3) == round(P["rho_projection"], 3)
    assert round(_spearman([d["mean_shift_norm"] for d in rows], cut), 3) == round(P["rho_norm"], 3)
    # the headline: 95 times, 6.23 against 0.066 at equal weight norm; the README says the same
    assert round(RATIO) == 95 and _E["top8_math31"]["add_rel"] == _E["rand8_math31"]["add_rel"]
    readme = open("studies/rlneurons/README.md").read()
    assert "moves the residual 95 times less" in readme and "RMS shift 0.066 against 6.23" in readme and "Think-SFT at 0.02, also norm-matched: 0.75" in readme
    assert f"{_r('rand8_math31'):.3f}" == "0.066" and f"{_r('top8_math31'):.2f}" == "6.23" and f"{_r('top8x0.02_think_sft'):.2f}" == "0.75"
    assert (f"{min(_cos_pos):.2f}", f"{max(_cos_pos):.2f}", _c("top8xm1_math31")) == ("0.93", "0.99", "−0.83")
    assert (round(100 * min(_frac)), round(100 * max(_frac))) == (7, 19)
    print("DATA matches", DATA["readout"], DATA["metrics"], DATA["run"], "and", CELLS)
    sys.exit(0)
