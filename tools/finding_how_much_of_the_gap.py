"""All 49 configurations on the 328 harder problems on one scale: the share of the gap from Base + cue to RL that each closes.

The page of one finding, served at /finding/how-much-of-the-gap (view.py serves every tools/finding_<slug>.py) and
reached from its tile on /findings, which ICON draws. The picture is one lit plate holding a forest plot: one axis, the
share of the gap closed (0 % = Base + cue, 100 % = RL, in the row's comparison), and one row per configuration with its
95 % interval, grouped by family (Base + cue rules on untrained weights, weight edits, Think-SFT, RL, hand-offs and mixed
votes). The reader's one control switches the comparison: one sample, the vote over 4 samples, or the configurations that
spend at most the tokens of one RL sample. Rows that stay travel to their new values, rows that leave fade, new rows grow
out of the 0 % line. The large number is the best configuration with no reward-trained weights among those measured on
the 4 stored samples per problem, with the best rule on untrained weights beside it. A click on a row shows that
configuration in the side column. Address: /finding/how-much-of-the-gap#<one|vote|tokens>/<configuration>/<panel>.
The rules are in .claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py
(.claude/skills/site-ui/SKILL.md). Study: studies/rlneurons, README section "All configurations on the 328 in one
table"; board result-389164.

    uv run tools/finding_how_much_of_the_gap.py    checks DATA against the artifact it was copied from
"""
import json

RUN = "studies/rlneurons/results/table/hard328-01/"

# Every number is copied from table.json of the run folder; none is typed from memory. The deployed site ships only
# tools/*.py, so the copy is a literal; run this file to compare it with the artifact. One row per row of table.json:
# id (key in the address), key, name, family, n (n_samples), reward, chosen (chosen_on_328), source, right, wrong,
# abst (abstained), acc (accuracy percent and interval95), share (share percent and interval95), tokens (per problem),
# mult (token_multiple x and interval95, when stored), vs_rl (minus_rl_single points and interval95), cap_hits.
DATA = {
    "artifact": RUN + "table.json",
    "commit": "cd9f309",  # the commit that added the run folder to main
    "code_commit": "5c8a97e",  # run.json commit: analysis/config_table.py
    "command": "python -m studies.rlneurons.analysis.config_table --out studies/rlneurons/results/table/hard328-01",
    "n": 328,
    "cap_L": 14028,
    "rows": [
        {"id": "base-single", "key": "base|single", "name": "base + cue, one sample (mean of 4)", "family": "single", "n": 1, "reward": "no", "chosen": "no", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 158.5, "wrong": 103.5, "abst": 66.0, "acc": [48.32, 43.52, 53.05], "share": [0.0, 0.0, 0.0], "tokens": 9225, "mult": [0.989, 0.964, 1.015], "vs_rl": [-12.65, -15.47, -10.06]},
        {"id": "base-restart", "key": "base|restart", "name": "base + cue, one sample, restart after a cap hit (mean of 4)", "family": "single", "n": 1, "reward": "no", "chosen": "no", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 167.0, "wrong": 135.0, "abst": 26.0, "acc": [50.91, 46.11, 55.64], "share": [20.48, 13.45, 28.83], "tokens": 13827, "mult": [1.483, 1.4, 1.566], "vs_rl": [-10.06, -12.65, -7.62]},
        {"id": "base-vote4", "key": "base|vote4", "name": "base + cue, vote over 4", "family": "vote", "n": 4, "reward": "no", "chosen": "no", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 192.0, "wrong": 124.0, "abst": 12.0, "acc": [58.54, 53.05, 64.02], "share": [0.0, 0.0, 0.0], "tokens": 36902, "mult": [3.957, 3.856, 4.061], "vs_rl": [-2.44, -5.64, 0.61]},
        {"id": "base-vote4-restart", "key": "base|vote4_restart", "name": "base + cue, vote over 4 after restart", "family": "vote", "n": 4, "reward": "no", "chosen": "no", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 195.0, "wrong": 132.0, "abst": 1.0, "acc": [59.45, 53.96, 64.94], "share": [10.34, -7.9, 29.17], "tokens": 55306, "mult": [5.931, 5.6, 6.266], "vs_rl": [-1.52, -4.8, 1.6]},
        {"id": "base-vote4-short", "key": "base|vote4_short", "name": "base + cue, vote over 4, ties to the shortest", "family": "vote", "n": 4, "reward": "no", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 191.0, "wrong": 125.0, "abst": 12.0, "acc": [58.23, 52.74, 63.72], "share": [-3.45, -29.17, 16.67], "tokens": 36902, "mult": [3.957, 3.856, 4.061], "vs_rl": [-2.74, -5.87, 0.23]},
        {"id": "base-vote4-restart-short", "key": "base|vote4_restart_short", "name": "base + cue, vote over 4 after restart, ties to the shortest", "family": "vote", "n": 4, "reward": "no", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 199.0, "wrong": 128.0, "abst": 1.0, "acc": [60.67, 55.18, 66.16], "share": [24.14, 0.0, 50.0], "tokens": 55306, "mult": [5.931, 5.6, 6.266], "vs_rl": [-0.3, -3.28, 2.52]},
        {"id": "base-seq3", "key": "base|seq3", "name": "base + cue, sequential vote, at most 3 (mean of 24 orders)", "family": "vote", "n": 3, "reward": "no", "chosen": "no", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 178.75, "wrong": 130.75, "abst": 18.5, "acc": [54.5, 49.44, 59.6], "share": [-45.69, -97.69, -21.04], "tokens": 25567, "mult": [2.742, 2.647, 2.831], "vs_rl": [-6.48, -9.32, -3.89]},
        {"id": "base-seq4-restart", "key": "base|seq4_restart", "name": "base + cue, sequential vote, at most 4, restarts (mean of 24 orders)", "family": "vote", "n": 4, "reward": "no", "chosen": "no", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 190.75, "wrong": 136.25, "abst": 1.0, "acc": [58.16, 52.79, 63.44], "share": [-4.31, -32.54, 14.29], "tokens": 46817, "mult": [5.021, 4.644, 5.39], "vs_rl": [-2.82, -5.69, -0.05]},
        {"id": "base-seq4-restart-short", "key": "base|seq4_restart_short", "name": "base + cue, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders)", "family": "vote", "n": 4, "reward": "no", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "day1_3/hard328_base_cue_s4r2-01", "right": 198.5, "wrong": 128.5, "abst": 1.0, "acc": [60.52, 55.03, 66.01], "share": [22.41, -1.61, 47.06], "tokens": 46817, "mult": [5.021, 4.644, 5.39], "vs_rl": [-0.46, -3.43, 2.44]},
        {"id": "rl-single", "key": "rl|single", "name": "RL plain, one sample (mean of 4)", "family": "single", "n": 1, "reward": "yes", "chosen": "no", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 200.0, "wrong": 119.0, "abst": 9.0, "acc": [60.98, 56.17, 65.7], "share": [100.0, 100.0, 100.0], "tokens": 9325, "mult": [1.0, 1.0, 1.0], "vs_rl": [0.0, 0.0, 0.0]},
        {"id": "rl-restart", "key": "rl|restart", "name": "RL plain, one sample, restart after a cap hit (mean of 4)", "family": "single", "n": 1, "reward": "yes", "chosen": "no", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 204.5, "wrong": 121.0, "abst": 2.5, "acc": [62.35, 57.62, 67.0], "share": [110.84, 104.97, 118.18], "tokens": 11027, "mult": [1.183, 1.137, 1.228], "vs_rl": [1.37, 0.61, 2.21]},
        {"id": "rl-vote4", "key": "rl|vote4", "name": "RL plain, vote over 4", "family": "vote", "n": 4, "reward": "yes", "chosen": "no", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 221.0, "wrong": 107.0, "abst": 0.0, "acc": [67.38, 62.2, 72.56], "share": [100.0, 100.0, 100.0], "tokens": 37299, "mult": [4.0, 4.0, 4.0], "vs_rl": [6.4, 4.42, 8.38]},
        {"id": "rl-vote4-restart", "key": "rl|vote4_restart", "name": "RL plain, vote over 4 after restart", "family": "vote", "n": 4, "reward": "yes", "chosen": "no", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 224.0, "wrong": 104.0, "abst": 0.0, "acc": [68.29, 63.11, 73.48], "share": [110.34, 91.67, 140.0], "tokens": 44108, "mult": [4.73, 4.547, 4.91], "vs_rl": [7.32, 5.11, 9.68]},
        {"id": "rl-vote4-short", "key": "rl|vote4_short", "name": "RL plain, vote over 4, ties to the shortest", "family": "vote", "n": 4, "reward": "yes", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 222.0, "wrong": 106.0, "abst": 0.0, "acc": [67.68, 62.5, 72.87], "share": [103.45, 81.82, 131.58], "tokens": 37299, "mult": [4.0, 4.0, 4.0], "vs_rl": [6.71, 4.65, 8.92]},
        {"id": "rl-vote4-restart-short", "key": "rl|vote4_restart_short", "name": "RL plain, vote over 4 after restart, ties to the shortest", "family": "vote", "n": 4, "reward": "yes", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 220.0, "wrong": 108.0, "abst": 0.0, "acc": [67.07, 61.89, 72.26], "share": [96.55, 73.52, 126.09], "tokens": 44108, "mult": [4.73, 4.547, 4.91], "vs_rl": [6.1, 3.96, 8.31]},
        {"id": "rl-seq3", "key": "rl|seq3", "name": "RL plain, sequential vote, at most 3 (mean of 24 orders)", "family": "vote", "n": 3, "reward": "yes", "chosen": "no", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 212.67, "wrong": 115.33, "abst": 0.0, "acc": [64.84, 59.86, 69.67], "share": [71.26, 51.78, 87.65], "tokens": 23575, "mult": [2.528, 2.482, 2.573], "vs_rl": [3.86, 2.85, 4.9]},
        {"id": "rl-seq4-restart", "key": "rl|seq4_restart", "name": "RL plain, sequential vote, at most 4, restarts (mean of 24 orders)", "family": "vote", "n": 4, "reward": "yes", "chosen": "no", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 218.25, "wrong": 109.75, "abst": 0.0, "acc": [66.54, 61.36, 71.57], "share": [90.52, 68.75, 118.0], "tokens": 31620, "mult": [3.391, 3.176, 3.601], "vs_rl": [5.56, 3.73, 7.47]},
        {"id": "rl-seq4-restart-short", "key": "rl|seq4_restart_short", "name": "RL plain, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders)", "family": "vote", "n": 4, "reward": "yes", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 220.5, "wrong": 107.5, "abst": 0.0, "acc": [67.23, 62.04, 72.41], "share": [98.28, 77.03, 126.0], "tokens": 31620, "mult": [3.391, 3.176, 3.601], "vs_rl": [6.25, 4.27, 8.38]},
        {"id": "think-single", "key": "think|single", "name": "Think-SFT + cue, one sample (mean of 4)", "family": "single", "n": 1, "reward": "no", "chosen": "no", "source": "thinkvote/hard328_sft1_cue_s4-01", "right": 209.0, "wrong": 37.5, "abst": 81.5, "acc": [63.72, 58.92, 68.45], "share": [121.69, 102.86, 144.45], "tokens": 10103, "mult": [1.083, 1.06, 1.105], "vs_rl": [2.74, 0.38, 5.18]},
        {"id": "think-vote4", "key": "think|vote4", "name": "Think-SFT + cue, vote over 4", "family": "vote", "n": 4, "reward": "no", "chosen": "no", "source": "thinkvote/hard328_sft1_cue_s4-01", "right": 241.0, "wrong": 57.0, "abst": 30.0, "acc": [73.48, 68.6, 78.35], "share": [168.97, 127.78, 250.0], "tokens": 40410, "mult": [4.334, 4.241, 4.421], "vs_rl": [12.5, 9.3, 15.78]},
        {"id": "think-vote4-short", "key": "think|vote4_short", "name": "Think-SFT + cue, vote over 4, ties to the shortest", "family": "vote", "n": 4, "reward": "no", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "thinkvote/hard328_sft1_cue_s4-01", "right": 239.0, "wrong": 59.0, "abst": 30.0, "acc": [72.87, 67.99, 77.74], "share": [162.07, 121.95, 242.15], "tokens": 40410, "mult": [4.334, 4.241, 4.421], "vs_rl": [11.89, 8.76, 15.02]},
        {"id": "think-vote4-restart-short", "key": "think|vote4_restart_short", "name": "Think-SFT + cue, vote over 4 after restart, ties to the shortest (no restart rows: restart = none)", "family": "vote", "n": 4, "reward": "no", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "thinkvote/hard328_sft1_cue_s4-01", "right": 239.0, "wrong": 59.0, "abst": 30.0, "acc": [72.87, 67.99, 77.74], "share": [162.07, 121.95, 242.15], "tokens": 40410, "mult": [4.334, 4.241, 4.421], "vs_rl": [11.89, 8.76, 15.02]},
        {"id": "think-seq3", "key": "think|seq3", "name": "Think-SFT + cue, sequential vote, at most 3 (mean of 24 orders)", "family": "vote", "n": 3, "reward": "no", "chosen": "no", "source": "thinkvote/hard328_sft1_cue_s4-01", "right": 233.17, "wrong": 54.33, "abst": 40.5, "acc": [71.09, 66.26, 75.91], "share": [141.95, 106.9, 207.87], "tokens": 26114, "mult": [2.8, 2.706, 2.891], "vs_rl": [10.11, 7.14, 13.01]},
        {"id": "think-seq4-restart", "key": "think|seq4_restart", "name": "Think-SFT + cue, sequential vote, at most 4, restarts (mean of 24 orders) (no restart rows: restart = none)", "family": "vote", "n": 4, "reward": "no", "chosen": "no", "source": "thinkvote/hard328_sft1_cue_s4-01", "right": 238.92, "wrong": 59.08, "abst": 30.0, "acc": [72.84, 67.91, 77.64], "share": [161.78, 122.37, 239.22], "tokens": 30837, "mult": [3.307, 3.15, 3.452], "vs_rl": [11.86, 8.71, 14.99]},
        {"id": "think-seq4-restart-short", "key": "think|seq4_restart_short", "name": "Think-SFT + cue, sequential vote, at most 4, restarts, ties to the shortest (mean of 24 orders) (no restart rows: restart = none)", "family": "vote", "n": 4, "reward": "no", "chosen": "no (tie rule written on MATH-500 after reading the problems it fixes: in-sample there, held out here)", "source": "thinkvote/hard328_sft1_cue_s4-01", "right": 239.5, "wrong": 58.5, "abst": 30.0, "acc": [73.02, 67.99, 77.74], "share": [163.79, 124.24, 244.44], "tokens": 30837, "mult": [3.307, 3.15, 3.452], "vs_rl": [12.04, 8.92, 15.17]},
        {"id": "think-capl", "key": "think|capL", "name": "Think-SFT + cue, one sample stopped at 14,028 tokens (tokens matched to one RL sample; mean of 4)", "family": "single", "n": 1, "reward": "no", "chosen": "L set from the 328's token counts, no score read", "source": "thinkvote/hard328_sft1_cue_s4-01", "right": 191.25, "wrong": 16.0, "abst": 120.75, "acc": [58.31, 53.43, 63.11], "share": [78.92, 61.85, 97.87], "tokens": 9325, "mult": [1.0, 0.981, 1.019], "vs_rl": [-2.67, -5.11, -0.23]},
        {"id": "rl-capl", "key": "rl|capL", "name": "RL plain, one sample stopped at the same 14,028 tokens (mean of 4)", "family": "single", "n": 1, "reward": "yes", "chosen": "L set from the 328's token counts, no score read", "source": "day1_3/hard328_rl_plain_s4r2-01", "right": 191.0, "wrong": 66.0, "abst": 71.0, "acc": [58.23, 53.43, 63.03], "share": [78.31, 69.62, 85.78], "tokens": 8970, "mult": [0.962, 0.957, 0.968], "vs_rl": [-2.74, -3.89, -1.75]},
        {"id": "mix-2rl-2think", "key": "mix|2rl+2think", "name": "mixed vote, 2 RL plain + 2 Think-SFT + cue (mean over combinations)", "family": "vote", "n": 4, "reward": "partly", "chosen": "no (every mix is reported, none picked)", "source": "mixvote from the three runs", "right": 228.1, "wrong": 99.49, "abst": 0.42, "acc": [69.54, 64.72, 74.25], "share": [124.47, 103.44, 166.67], "tokens": 38855, "mult": [4.167], "vs_rl": [8.57, 6.75, 10.39]},
        {"id": "mix-2rl-2base", "key": "mix|2rl+2base", "name": "mixed vote, 2 RL plain + 2 base + cue (mean over combinations)", "family": "vote", "n": 4, "reward": "partly", "chosen": "no (every mix is reported, none picked)", "source": "mixvote from the three runs", "right": 207.62, "wrong": 120.04, "abst": 0.33, "acc": [63.3, 58.31, 68.11], "share": [53.88, 37.32, 68.06], "tokens": 37101, "mult": [3.979], "vs_rl": [2.32, 1.15, 3.51]},
        {"id": "mix-2think-2base", "key": "mix|2think+2base", "name": "mixed vote, 2 Think-SFT + cue + 2 base + cue (mean over combinations)", "family": "vote", "n": 4, "reward": "no", "chosen": "no (every mix is reported, none picked)", "source": "mixvote from the three runs", "right": 220.82, "wrong": 90.99, "abst": 16.19, "acc": [67.32, 62.41, 71.99], "share": [99.38, 75.08, 142.57], "tokens": 38656, "mult": [4.145], "vs_rl": [6.35, 4.04, 8.66]},
        {"id": "mix-4rl-4think", "key": "mix|4rl+4think", "name": "mixed vote, 4 RL plain + 4 Think-SFT + cue (mean over combinations)", "family": "vote", "n": 8, "reward": "partly", "chosen": "no (every mix is reported, none picked)", "source": "mixvote from the three runs", "right": 239.0, "wrong": 89.0, "abst": 0.0, "acc": [72.87, 67.84, 77.74], "share": [162.07, 130.88, 230.0], "tokens": 77710, "mult": [8.334], "vs_rl": [11.89, 9.22, 14.56]},
        {"id": "mix-4think-4base", "key": "mix|4think+4base", "name": "mixed vote, 4 Think-SFT + cue + 4 base + cue (mean over combinations)", "family": "vote", "n": 8, "reward": "no", "chosen": "no (every mix is reported, none picked)", "source": "mixvote from the three runs", "right": 238.0, "wrong": 87.0, "abst": 3.0, "acc": [72.56, 67.53, 77.44], "share": [158.62, 120.23, 237.5], "tokens": 77312, "mult": [8.291], "vs_rl": [11.59, 8.69, 14.63]},
        {"id": "relay-rl-rl-25", "key": "relay|rl->rl|25", "name": "relay: RL writes the first 25 %, RL finishes", "family": "single", "n": 1, "reward": "yes", "chosen": "no (arms and cuts filed in SPEC_relay)", "source": "relay/rl_c25-01", "right": 206.0, "wrong": 113.0, "abst": 9.0, "acc": [62.8, 57.32, 67.99], "share": [114.46, 90.06, 141.22], "tokens": 9559, "mult": [1.025, 1.002, 1.049], "vs_rl": [1.83, -1.3, 4.95]},
        {"id": "relay-rl-rl-50", "key": "relay|rl->rl|50", "name": "relay: RL writes the first 50 %, RL finishes", "family": "single", "n": 1, "reward": "yes", "chosen": "no (arms and cuts filed in SPEC_relay)", "source": "relay/rl_c50-01", "right": 193.0, "wrong": 128.0, "abst": 7.0, "acc": [58.84, 53.66, 64.02], "share": [83.13, 61.27, 106.33], "tokens": 9519, "mult": [1.021, 1.0, 1.043], "vs_rl": [-2.13, -5.03, 0.76]},
        {"id": "relay-rl-think-25", "key": "relay|rl->think|25", "name": "relay: RL writes the first 25 %, Think-SFT + cue finishes", "family": "single", "n": 1, "reward": "partly", "chosen": "no (arms and cuts filed in SPEC_relay)", "source": "relay/think_c25-01", "right": 204.0, "wrong": 30.0, "abst": 94.0, "acc": [62.2, 57.01, 67.68], "share": [109.64, 85.48, 137.13], "tokens": 10511, "mult": [1.127, 1.1, 1.156], "vs_rl": [1.22, -1.91, 4.34]},
        {"id": "relay-rl-think-50", "key": "relay|rl->think|50", "name": "relay: RL writes the first 50 %, Think-SFT + cue finishes", "family": "single", "n": 1, "reward": "partly", "chosen": "no (arms and cuts filed in SPEC_relay)", "source": "relay/think_c50-01", "right": 199.0, "wrong": 35.0, "abst": 94.0, "acc": [60.67, 55.49, 66.16], "share": [97.59, 71.7, 126.38], "tokens": 10664, "mult": [1.144, 1.118, 1.169], "vs_rl": [-0.3, -3.58, 3.05]},
        {"id": "relay-think-rl-25", "key": "relay|think->rl|25", "name": "relay: Think-SFT + cue writes the first 25 %, RL finishes", "family": "single", "n": 1, "reward": "partly", "chosen": "no (arms and cuts filed in SPEC_relay)", "source": "relay/rl_c25-01", "right": 207.0, "wrong": 117.0, "abst": 4.0, "acc": [63.11, 57.62, 68.29], "share": [116.87, 92.1, 145.24], "tokens": 8900, "mult": [0.954, 0.929, 0.981], "vs_rl": [2.13, -1.07, 5.26]},
        {"id": "relay-think-rl-50", "key": "relay|think->rl|50", "name": "relay: Think-SFT + cue writes the first 50 %, RL finishes", "family": "single", "n": 1, "reward": "partly", "chosen": "no (arms and cuts filed in SPEC_relay)", "source": "relay/rl_c50-01", "right": 209.0, "wrong": 119.0, "abst": 0.0, "acc": [63.72, 58.23, 68.9], "share": [121.69, 97.14, 150.78], "tokens": 8923, "mult": [0.957, 0.932, 0.984], "vs_rl": [2.74, -0.38, 5.87]},
        {"id": "relay-think-think-25", "key": "relay|think->think|25", "name": "relay: Think-SFT + cue writes the first 25 %, Think-SFT + cue finishes", "family": "single", "n": 1, "reward": "no", "chosen": "no (arms and cuts filed in SPEC_relay)", "source": "relay/think_c25-01", "right": 219.0, "wrong": 38.0, "abst": 71.0, "acc": [66.77, 61.59, 71.95], "share": [145.78, 118.71, 180.0], "tokens": 10029, "mult": [1.076, 1.05, 1.102], "vs_rl": [5.79, 2.52, 9.22]},
        {"id": "relay-think-think-50", "key": "relay|think->think|50", "name": "relay: Think-SFT + cue writes the first 50 %, Think-SFT + cue finishes", "family": "single", "n": 1, "reward": "no", "chosen": "no (arms and cuts filed in SPEC_relay)", "source": "relay/think_c50-01", "right": 211.0, "wrong": 37.0, "abst": 80.0, "acc": [64.33, 58.84, 69.51], "share": [126.51, 96.72, 161.87], "tokens": 10423, "mult": [1.118, 1.086, 1.15], "vs_rl": [3.35, -0.46, 7.16]},
        {"id": "axis-base-plain", "key": "axis|base_plain", "name": "base plain, one sample", "family": "single", "n": 1, "reward": "no", "chosen": "no", "source": "axis/hard328-01/vectors.json [base_plain]", "right": 76.0, "wrong": None, "abst": None, "acc": [23.17, 18.6, 27.74], "share": [-198.8, -273.76, -144.27], "tokens": 4928, "mult": [0.529], "vs_rl": [-37.8, -42.76, -32.85], "cap_hits": 35},
        {"id": "axis-base-cue", "key": "axis|base_cue", "name": "base + cue, one sample, Day-1 #1 draw", "family": "single", "n": 1, "reward": "no", "chosen": "no", "source": "axis/hard328-01/vectors.json [base_cue]", "right": 164.0, "wrong": None, "abst": None, "acc": [50.0, 44.51, 55.49], "share": [13.25, -15.34, 39.54], "tokens": 9344, "mult": [1.002], "vs_rl": [-10.98, -14.71, -7.39], "cap_hits": 77},
        {"id": "axis-rl-plain", "key": "axis|rl_plain", "name": "RL plain, one sample, Day-1 #1 draw", "family": "single", "n": 1, "reward": "yes", "chosen": "no", "source": "axis/hard328-01/vectors.json [rl_plain]", "right": 206.0, "wrong": None, "abst": None, "acc": [62.8, 57.32, 67.99], "share": [114.46, 92.0, 139.9], "tokens": 9315, "mult": [0.999], "vs_rl": [1.83, -1.07, 4.73], "cap_hits": 20},
        {"id": "axis-rl-cue", "key": "axis|rl_cue", "name": "RL + cue, one sample", "family": "single", "n": 1, "reward": "yes", "chosen": "no", "source": "axis/hard328-01/vectors.json [rl_cue]", "right": 205.0, "wrong": None, "abst": None, "acc": [62.5, 57.01, 67.69], "share": [112.05, 90.95, 137.4], "tokens": 9316, "mult": [0.999], "vs_rl": [1.52, -1.22, 4.34], "cap_hits": 25},
        {"id": "axis-theta0.25-cue", "key": "axis|theta0.25_cue", "name": "base + 0.25 (RL - base) + cue, one sample", "family": "single", "n": 1, "reward": "partly", "chosen": "no", "source": "axis/hard328-01/vectors.json [theta0.25_cue]", "right": 182.0, "wrong": None, "abst": None, "acc": [55.49, 50.0, 60.67], "share": [56.63, 30.86, 81.41], "tokens": 9097, "mult": [0.976], "vs_rl": [-5.49, -8.92, -2.29], "cap_hits": 56},
        {"id": "axis-theta0.5-cue", "key": "axis|theta0.5_cue", "name": "base + 0.5 (RL - base) + cue, one sample", "family": "single", "n": 1, "reward": "partly", "chosen": "no", "source": "axis/hard328-01/vectors.json [theta0.5_cue]", "right": 190.0, "wrong": None, "abst": None, "acc": [57.93, 52.44, 63.41], "share": [75.9, 50.78, 101.86], "tokens": 9656, "mult": [1.036], "vs_rl": [-3.05, -6.25, 0.23], "cap_hits": 73},
        {"id": "axis-code-cue", "key": "axis|code_cue", "name": "RL-Zero-Code + cue, one sample", "family": "single", "n": 1, "reward": "yes (code reward)", "chosen": "no", "source": "axis/hard328-01/vectors.json [code_cue]", "right": 187.0, "wrong": None, "abst": None, "acc": [57.01, 51.52, 62.5], "share": [68.67, 44.74, 93.04], "tokens": 7613, "mult": [0.816], "vs_rl": [-3.96, -7.24, -0.84], "cap_hits": 25},
        {"id": "other-sft1-cue", "key": "other|sft1_cue", "name": "Think-SFT + cue, one sample, other workspace (sameraslan)", "family": "single", "n": 1, "reward": "no", "chosen": "no", "source": "git bdba62b:studies/rlneurons/results/wsp1/hard328/sft1_cue-01/per_problem.json", "right": 219.0, "wrong": None, "abst": None, "acc": [66.77, 61.28, 71.95], "share": [145.78, 119.88, 177.71], "tokens": 10123, "mult": [1.086, 1.057, 1.114], "vs_rl": [5.79, 2.67, 8.92], "cap_hits": 89},
        {"id": "other-sft1-plain", "key": "other|sft1_plain", "name": "Think-SFT plain, one sample (sameraslan)", "family": "single", "n": 1, "reward": "no", "chosen": "no", "source": "git bdba62b:studies/rlneurons/results/wsp1/hard328/sft1_plain-01/per_problem.json", "right": 203.0, "wrong": None, "abst": None, "acc": [61.89, 56.71, 67.07], "share": [107.23, 80.0, 137.82], "tokens": 9376, "mult": [1.005, 0.966, 1.045], "vs_rl": [0.91, -2.59, 4.42], "cap_hits": 86},
    ],
}

# The comparisons of the control. family: the rows whose share uses this comparison's gap; most: the largest token
# multiple of one RL sample a row may have to be shown (the token comparison).
VIEWS = [
    {"id": "one", "name": "One sample", "family": "single", "most": None,
     "base": 158.5, "rl": 200.0, "hint": "One answer per problem. 0 % is one Base + cue sample, 100 % one RL sample."},
    {"id": "vote", "name": "Vote over 4 samples", "family": "vote", "most": None,
     "base": 192.0, "rl": 221.0, "hint": "The most common of 4 answers counts. 0 % and 100 % are the votes of Base + cue and RL."},
    {"id": "tokens", "name": "At the tokens of one RL sample", "family": "single", "most": 1.02,
     "base": 158.5, "rl": 200.0, "hint": "Only settings that spend at most 1.02 times the tokens of one RL sample."},
]

# The families, top to bottom: name and a short second line.
GROUPS = [
    ["base", "Base + cue", "untrained weights"],
    ["edit", "Weight edits", "part of RL's change"],
    ["think", "Think-SFT", "imitation, no reward"],
    ["rl", "RL", "reward-trained"],
    ["mix", "Mixed", "hand-offs and votes"],
]

# One row of the picture per slot: its family and the configuration it shows in each comparison (one, vote, tokens).
# A slot that holds a configuration in two comparisons keeps its mark, which travels from one value to the other.
SLOTS = [
    ["base", "base-single", "base-vote4", "base-single"],
    ["base", "base-restart", "base-vote4-restart", None],
    ["base", None, "base-vote4-short", None],
    ["base", None, "base-vote4-restart-short", None],
    ["base", None, "base-seq3", None],
    ["base", None, "base-seq4-restart", None],
    ["base", None, "base-seq4-restart-short", None],
    ["base", "axis-base-cue", None, "axis-base-cue"],
    ["base", "axis-base-plain", None, "axis-base-plain"],
    ["edit", "axis-theta0.25-cue", None, "axis-theta0.25-cue"],
    ["edit", "axis-theta0.5-cue", None, None],
    ["think", "think-single", "think-vote4", None],
    ["think", "think-capl", None, "think-capl"],
    ["think", None, "think-vote4-short", None],
    ["think", None, "think-vote4-restart-short", None],
    ["think", None, "think-seq3", None],
    ["think", None, "think-seq4-restart", None],
    ["think", None, "think-seq4-restart-short", None],
    ["think", "other-sft1-cue", None, None],
    ["think", "other-sft1-plain", None, "other-sft1-plain"],
    ["rl", "rl-single", "rl-vote4", "rl-single"],
    ["rl", "rl-restart", "rl-vote4-restart", None],
    ["rl", "rl-capl", None, "rl-capl"],
    ["rl", None, "rl-vote4-short", None],
    ["rl", None, "rl-vote4-restart-short", None],
    ["rl", None, "rl-seq3", None],
    ["rl", None, "rl-seq4-restart", None],
    ["rl", None, "rl-seq4-restart-short", None],
    ["rl", "axis-rl-plain", None, "axis-rl-plain"],
    ["rl", "axis-rl-cue", None, "axis-rl-cue"],
    ["rl", "axis-code-cue", None, "axis-code-cue"],
    ["mix", "relay-think-think-25", None, None],
    ["mix", "relay-think-think-50", None, None],
    ["mix", None, "mix-2think-2base", None],
    ["mix", None, "mix-4think-4base", None],
    ["mix", "relay-think-rl-25", None, "relay-think-rl-25"],
    ["mix", "relay-think-rl-50", None, "relay-think-rl-50"],
    ["mix", "relay-rl-think-25", None, None],
    ["mix", "relay-rl-think-50", None, None],
    ["mix", "relay-rl-rl-25", None, None],
    ["mix", "relay-rl-rl-50", None, None],
    ["mix", None, "mix-2rl-2think", None],
    ["mix", None, "mix-4rl-4think", None],
    ["mix", None, "mix-2rl-2base", None],
]

# The label of each row in the picture, and one plain sentence for the side column.
_RULE = {
    "single": ("One sample", "answers each problem once; the count is the mean over its 4 stored samples."),
    "restart": ("One sample, with restarts", "answers each problem once, and an answer cut off at 16,384 tokens is sampled "
                "again, up to two more times; the count is the mean over 4 samples."),
    "vote4": ("Vote over 4 samples", "answers 4 times and takes the most common final answer."),
    "vote4-restart": ("Vote over 4, with restarts", "answers 4 times, samples each answer cut off at 16,384 tokens again, "
                      "and takes the most common final answer."),
    "vote4-short": ("Vote over 4, ties to the shortest", "answers 4 times and takes the most common final answer; a tied "
                    "vote goes to the shortest finished sample."),
    "vote4-restart-short": ("Vote over 4, restarts, ties to the shortest", "answers 4 times with restarts and takes the "
                            "most common final answer; a tied vote goes to the shortest finished sample."),
    "seq3": ("Stop when 2 agree, at most 3", "draws one sample at a time and stops when two final answers agree, at most "
             "3; the count is the mean over the 24 orders of its 4 stored samples."),
    "seq4-restart": ("Stop when 2 agree, at most 4, restarts", "draws one sample at a time, with restarts, and stops when "
                     "two final answers agree, at most 4; mean over 24 orders."),
    "seq4-restart-short": ("Stop when 2 agree, restarts, ties to shortest", "draws one sample at a time, with restarts, "
                           "and stops when two agree, at most 4; a tie goes to the shortest finished sample; mean over 24 "
                           "orders."),
}
_WHO = {"base": "Base + cue, the untrained base model with the opening cue,",
        "rl": "RL, the base model after reinforcement learning on math, with no cue,",
        "think": "Think-SFT + cue, the base model fine-tuned to copy worked solutions with no reward,"}
SHORT, DESC = {}, {}
for _m in _WHO:
    for _k, (_s, _d) in _RULE.items():
        SHORT[f"{_m}-{_k}"], DESC[f"{_m}-{_k}"] = _s, f"{_WHO[_m]} {_d}"
SHORT.update({
    "think-capl": "One sample, stopped at 14,028 tokens", "rl-capl": "One sample, stopped at 14,028 tokens",
    "axis-base-cue": "One sample, a separate draw", "axis-base-plain": "Base without the cue, one draw",
    "axis-rl-plain": "One sample, a separate draw", "axis-rl-cue": "RL + cue, one draw",
    "axis-code-cue": "RL on code + cue, one draw",
    "axis-theta0.25-cue": "¼ of RL's weight change, + cue", "axis-theta0.5-cue": "½ of RL's weight change, + cue",
    "other-sft1-cue": "One sample, a separate run", "other-sft1-plain": "Without the cue, a separate run",
    "mix-2think-2base": "Vote: 2 Think-SFT + 2 Base + cue", "mix-4think-4base": "Vote over 8: 4 Think-SFT + 4 Base + cue",
    "mix-2rl-2think": "Vote: 2 RL + 2 Think-SFT", "mix-4rl-4think": "Vote over 8: 4 RL + 4 Think-SFT",
    "mix-2rl-2base": "Vote: 2 RL + 2 Base + cue",
})
DESC.update({
    "think-capl": "Think-SFT + cue answers each problem once and is stopped at 14,028 tokens, the length at which it spends as "
                  "many tokens per problem as one RL sample; the count is the mean over 4 samples.",
    "rl-capl": "RL answers each problem once and is stopped at the same 14,028 tokens as Think-SFT; the count is the mean "
               "over 4 samples.",
    "axis-base-cue": "Base + cue answers each problem once: one separate draw, from the first day's run.",
    "axis-base-plain": "The base model answers each problem once with the plain prompt, no opening cue: one draw.",
    "axis-rl-plain": "RL answers each problem once: one separate draw, from the first day's run.",
    "axis-rl-cue": "RL answers each problem once with the opening cue: one draw.",
    "axis-code-cue": "RL-Zero-Code, the same base model after reinforcement learning on code instead of math, answers once "
                     "with the opening cue: one draw.",
    "axis-theta0.25-cue": "The base weights plus a quarter of RL's weight change (a = 0.25), with the opening cue, answer once: "
                          "one draw.",
    "axis-theta0.5-cue": "The base weights plus half of RL's weight change (a = 0.5), with the opening cue, answer once: one "
                         "draw.",
    "other-sft1-cue": "Think-SFT + cue answers each problem once: one draw from a separate run in another workspace.",
    "other-sft1-plain": "Think-SFT answers each problem once with the plain prompt, no opening cue: one draw from a separate "
                        "run in another workspace.",
    "mix-2think-2base": "A vote over 2 Think-SFT + cue samples and 2 Base + cue samples; the count is the mean over every "
                        "way of choosing them from the stored samples.",
    "mix-4think-4base": "A vote over all 4 Think-SFT + cue samples and all 4 Base + cue samples, 8 in total.",
    "mix-2rl-2think": "A vote over 2 RL samples and 2 Think-SFT + cue samples; mean over every way of choosing them.",
    "mix-4rl-4think": "A vote over all 4 RL samples and all 4 Think-SFT + cue samples, 8 in total.",
    "mix-2rl-2base": "A vote over 2 RL samples and 2 Base + cue samples; mean over every way of choosing them.",
})
_NAME = {"rl": "RL", "think": "Think-SFT"}
for _a in ("rl", "think"):
    for _b in ("rl", "think"):
        for _c in ("25", "50"):
            SHORT[f"relay-{_a}-{_b}-{_c}"] = f"{_NAME[_a]} writes {_c} %, then {_NAME[_b]}"
            DESC[f"relay-{_a}-{_b}-{_c}"] = (f"A hand-off: {_NAME[_a]}{' + cue' if _a == 'think' else ''} writes the first "
                                             f"{_c} % of its answer, then {_NAME[_b]}{' + cue' if _b == 'think' else ''} "
                                             "writes the rest: one sample per problem.")

_ROWS = {r["id"]: r for r in DATA["rows"]}
FILLED = ("base-", "rl-", "think-", "mix-")  # measured on the 4 stored samples per problem; the rest are one draw


def members(v):
    """The ids of the rows shown in comparison v, in the order of the table."""
    return [r["id"] for r in DATA["rows"] if r["family"] == v["family"] and (v["most"] is None or r["mult"][0] <= v["most"])]


def lead(v):
    """The best row with no reward-trained weights, measured on the stored samples, and the best rule on untrained weights."""
    ids = [i for i in members(v) if i.startswith(FILLED)]
    best = max((i for i in ids if _ROWS[i]["reward"] == "no"), key=lambda i: _ROWS[i]["share"][0])
    base = max((i for i in ids if i.startswith("base-")), key=lambda i: _ROWS[i]["share"][0])
    return best, base


for _v in VIEWS:
    _v["lead"], _v["contrast"] = lead(_v)

# The names of the configurations the readout can name, short enough for its line.
LEADNAME = {"think-single": "Think-SFT + cue, one sample", "think-vote4": "Think-SFT + cue, vote over 4 samples",
            "think-capl": "Think-SFT + cue, stopped at 14,028 tokens", "base-single": "Base + cue, one sample",
            "base-restart": "Base + cue, one sample with restarts",
            "base-vote4-restart-short": "Base + cue, vote, restarts, ties to shortest"}
assert set(LEADNAME) == {i for v in VIEWS for i in (v["lead"], v["contrast"])}

_L = {v["id"]: [_ROWS[i] for i in lead(v)] for v in VIEWS}
_pc = lambda x: f"{x:.0f}".replace("-", "−") + " %"
_ci = lambda s: f"95 % interval {_pc(s[1])} to {_pc(s[2])}"
_one, _vote, _tok = _L["one"][0], _L["vote"][0], _L["tokens"][0]
_seed = [r for r in DATA["rows"] if r["id"] in ("other-sft1-cue", "relay-think-think-25", "other-sft1-plain")]

_count = lambda v: None if v is None else f"{v:.0f}" if v == int(v) else f"{v:.1f}"  # "209", "158.5", "191.2"

TITLE = "Gap closed without reward"  # the name on its tile on /findings and in the browser tab
PROBLEM = "How much of RL's gain on hard math can we get without reward?"
LINE = f"With no reward, Think-SFT closes {_pc(_one['share'][0])} of the gap from Base + cue to RL."

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences.
PANELS = [
    ["new", "What is new",
     "Earlier results each measured the gap their own way. Here all 49 configurations on the 328 harder problems are rebuilt "
     "from committed per-problem rows with one definition: 0 % is Base + cue, 100 % is RL.",
     ["DeepSeek-R1 (arXiv 2501.12948, section 4.1) reports that a smaller model trained to copy a stronger model's solutions "
      "beats the same model trained with large-scale RL. We see the same order on a 7B model, on one scale with untrained "
      "rules, weight edits and equal tokens.",
      f"With no training, the best rule closes {_pc(_L['one'][1]['share'][0])} of the gap at one sample and "
      f"{_pc(_L['vote'][1]['share'][0])} under the vote over 4 samples.",
      f"At the tokens of one RL sample, Think-SFT closes {_pc(_tok['share'][0])} ({_ci(_tok['share'])})."]],
    ["why", "Why it matters",
     "The research direction asks for the cheapest route to RL's score that uses no reward. The untrained weights stop near "
     "a fifth of the gap; imitation of worked solutions passes RL.",
     [f"Think-SFT + cue gets {_one['right']:.0f} of 328 right with one sample, RL {_ROWS['rl-single']['right']:.0f} and "
      f"Base + cue {_ROWS['base-single']['right']:.1f}.",
      f"Under the vote over 4 samples: Think-SFT {_vote['right']:.0f}, RL {_ROWS['rl-vote4']['right']:.0f}, Base + cue "
      f"{_ROWS['base-vote4']['right']:.0f}.",
      "Most of Think-SFT's lead at one sample needs more than 14,028 tokens: stopped there, it matches RL stopped at the same "
      "length."]],
    ["how", "How we know",
     "studies/rlneurons/analysis/config_table.py rebuilt every row from committed per-problem rows: 328 problems, T 1.0, "
     "cut off at 16,384 tokens, grader v3. Nothing was chosen on the 328.",
     ["Intervals come from a bootstrap over the 328 problems, 5,000 resamples, the same in every row; a share's interval is "
      "the interval of the ratio.",
      "176 of 176 numbers posted earlier reproduce. Planted rows equal to RL and to Base + cue score 100 % and 0 %.",
      "Without the 6 problems that may be in Think-SFT's training data, or with grader v4, no share moves by more than "
      "3.5 points."]],
    ["limits", "What it does not show",
     f"The vote's gap is 29 problems ({_ROWS['base-vote4']['right']:.0f} against {_ROWS['rl-vote4']['right']:.0f} of 328), so "
     f"every vote share has a wide interval: Think-SFT's {_pc(_vote['share'][0])} runs from {_pc(_vote['share'][1])} to "
     f"{_pc(_vote['share'][2])}.",
     ["Think-SFT is trained on worked solutions written by other models, so it is not free of training. Only the Base + cue "
      "rules use no training at all.",
      f"Hollow marks are one draw per problem from a separate run. Two of them reach {_pc(_seed[1]['share'][0])} at one "
      f"sample, and Think-SFT without the cue reaches {_pc(_seed[2]['share'][0])} at about the tokens of one RL sample. "
      "The large number counts only the 4-sample rows.",
      "Left out for lack of committed per-problem rows: the weight stack and the run with a 32k-token cap (both still running), the "
      "top RL directions and the loop-neuron edit."]],
    ["run", "How to reproduce it",
     f"Run {DATA['command']} at commit {DATA['code_commit']}; it reads only committed rows.",
     ["The run folder " + RUN + " holds table.md, table.json, checks.json and run.json.",
      "The README of studies/rlneurons, section “All configurations on the 328 in one table”, lists every source run."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's picture, reduced.
# A glass slab with the 0 % and 100 % lines, four rows of marks with intervals, and the last (Think-SFT) sliding slowly
# between its one-sample and its vote value.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, w = th / 2, X = s => a * (-.8 + 1.6 * (s + 50) / 300);
  const q = .5 - .5 * Math.cos((Number(t) || 0) * .45);
  const rows = [[0, 0, 0], [20, 13, 29], [100, 100, 100], [122 + 47 * q, 103 + 25 * q, 144 + 106 * q]];
  let out = kit.slab(a, b, th);
  for (const s of [0, 100]) out += kit.line(kit.at(X(s), -b * .74, w), kit.at(X(s), b * .74, w), .6, "plain", .8);
  rows.forEach(([s, lo, hi], i) => {
    const v = -b * .5 + i * b * .34, last = i === 3;
    if (hi > lo) out += kit.line(kit.at(X(lo), v, w), kit.at(X(hi), v, w), last ? .9 : .7, last ? "lit" : "plain", .9);
    const p = kit.at(X(s), v, w);
    out += `<ellipse cx="${p[0].toFixed(2)}" cy="${p[1].toFixed(2)}" rx="${(2.3 * p[2]).toFixed(2)}" ry="${(1.7 * p[2]).toFixed(2)}" fill="${last ? kit.token.blue : kit.token.ink}" opacity="${last ? 1 : .8}"/>`;
  });
  return out;
}"""

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
   with a cast shadow in place of the glow. The light comes from the upper left in both. Blue marks the configuration
   of the large number; a lighter mark uses reward-trained weights; a hollow mark is one draw from a separate run. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
  --gap: .055; --rw: .38;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
    --gap: .075; --rw: .42;
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

/* The picture: one plate holding the readout and the forest of configurations, and the one switch under it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg { width: 100%; max-height: calc(100vh - 170px); display: block; overflow: visible; touch-action: pan-y; user-select: none; -webkit-user-select: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
svg .hit { pointer-events: all; fill: var(--ink); fill-opacity: 0; stroke: none; cursor: pointer; outline: none; }
svg .hit:hover { fill-opacity: .035; }
svg .hit:focus-visible { stroke: var(--blue); stroke-width: 1.5; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.gapband { fill: var(--blue); opacity: var(--gap); }
.ref { stroke: var(--ink); stroke-width: 1.3; opacity: .5; }
.ref.rl { stroke: var(--blue); opacity: .75; }
.grid { stroke: var(--ink); stroke-width: 1; opacity: .07; fill: none; }
.sep { stroke: var(--ink); stroke-width: 1; opacity: .09; }
.tick { fill: var(--mute); font-weight: 500; }
.atitle { fill: var(--mute); font-weight: 560; }
.rlab { font-weight: 640; }
.rlab.rl { fill: var(--blue); }
.past { fill: var(--mute); font-weight: 500; }
.gname { font-weight: 680; font-stretch: 112%; }
.gsub { fill: var(--mute); font-weight: 480; }
.row { fill: var(--ink); font-weight: 480; }
.row.on { font-weight: 640; }
.iv { stroke: var(--ink); stroke-width: 1.7; stroke-linecap: round; opacity: .55; fill: none; }
.pt { fill: var(--ink); stroke: var(--ink); stroke-width: 1.6; }
.pt.hollow { fill: var(--sheet); }
.reward .iv { opacity: calc(var(--rw) * .7); }
.reward .pt { opacity: var(--rw); }
.reward .row { fill: var(--mute); }
.lead .iv { stroke: var(--blue); opacity: .95; stroke-width: 2.4; }
.lead .pt { fill: var(--blue); stroke: var(--blue); }
.lead .row { font-weight: 660; }
.halo { fill: var(--blue); opacity: calc(var(--bloom) * .22); }
.ring { fill: none; stroke: var(--ink); stroke-width: 1.4; }
.sel { fill: none; stroke: var(--blue); stroke-width: 1.8; }
.val { fill: var(--ink); font-weight: 640; }
.lead .val { fill: var(--blue); }
.far { fill: var(--ink); }
.big { fill: var(--ink); font-weight: 640; letter-spacing: -.035em; font-stretch: 100%; }
.l1 { fill: var(--ink); font-weight: 520; }
.l2, .ccap, .cci { fill: var(--mute); font-weight: 500; }
.cnum { fill: var(--ink); font-weight: 600; letter-spacing: -.02em; opacity: .72; font-stretch: 100%; }
.cname { fill: var(--ink); font-weight: 560; }
.vrule { stroke: var(--ink); stroke-width: 1; opacity: .12; }
.klab { fill: var(--mute); font-weight: 520; }
.switch { display: inline-flex; align-self: center; margin-top: 14px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.switch button[aria-pressed="true"]:hover { color: var(--paper); }
.hint { align-self: center; margin: 9px 0 0; font-size: 13px; color: var(--mute); text-align: center; }

/* One drawn entrance, then only the slow sway and what the reader changes */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .frame { animation: fade .7s .5s both; }
.enter .read { animation: fade .7s .7s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; white-space: nowrap; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.dhead h2 span { display: block; color: var(--mute); font-size: 13px; font-weight: 540; font-stretch: 106%; letter-spacing: 0; margin-bottom: 2px; }
.close { font-size: 13px; color: var(--mute); flex: none; }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.share { margin: 18px 0 0; display: flex; align-items: baseline; gap: 10px; }
.share b { flex: none; white-space: nowrap; font-size: 40px; font-weight: 640; letter-spacing: -.03em; line-height: 1; }
.share b.blue { color: var(--blue); }
.share span { color: var(--mute); font-size: 14.5px; line-height: 1.3; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.facts li b { color: var(--ink); font-weight: 620; }
.note { margin: 12px 0 0; font-size: 13.5px; color: var(--mute); max-width: 44ch; }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; display: flex; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
  .switch { order: -1; display: flex; margin: 0 0 14px; }
  .switch button { flex: 1; text-align: center; padding: 10px 4px; font-size: 14px; white-space: normal; line-height: 1.2; }
  .hint { order: -1; margin: 0 0 10px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button, .top a { transition: none; }
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
    <svg id="svg" role="group"></svg>
    <div class="switch" id="switch" role="group" aria-label="Which comparison"></div>
    <p class="hint" id="hint"></p>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <div class="pane" id="pane" aria-live="polite"></div>
  </div>
</div>
<script>
const C = __CONFIG__, $ = id => document.getElementById(id);
const still = matchMedia("(prefers-reduced-motion: reduce)"), narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v)), ease = p => p < .5 ? 4 * p * p * p : 1 - (-2 * p + 2) ** 3 / 2;
const minus = s => s.replace("-", "−");
const pc = v => { const r = Math.round(v); return (r < 0 ? "−" : "") + Math.abs(r) + " %"; };
const num = v => Math.round(v).toLocaleString("en-US");

/* The data: one row per configuration, one slot per row of the picture, three comparisons. */
const N = C.n, ROWS = Object.fromEntries(C.rows.map(r => [r.id, r]));
const VIEWS = C.views, GROUPS = C.groups, GI = Object.fromEntries(GROUPS.map((g, i) => [g[0], i]));
const SLOTS = C.slots.map((s, i) => ({ i, group: s[0], ids: s.slice(1), cur: { x: 0, lo: 0, hi: 0, y: 0, op: 0 }, from: null, to: null, t0: 0, shown: null }));
const DOM = [-55, 255], TICKS = [-50, 0, 50, 100, 150, 200, 250];
const vi = id => Math.max(0, VIEWS.findIndex(v => v.id === id));
const S = { view: 0, pick: null, open: null, g: null, el: {}, last: 0, t: 0, nums: null, groups: GROUPS.map(() => ({ y: 0, op: 0, from: null, to: null, t0: 0 })),
  h: null, rove: 0, txt: {} };
const filled = id => /^(base|rl|think|mix)-/.test(id);
const rewardOf = r => r.reward !== "no";

/* Geometry, in the units of the viewBox. Desktop: the label column at the left, the axis at the right. Phone: each
   label above its row, and the plate grows with the number of rows. */
function geo() {
  return narrow.matches
    ? { w: 480, phone: true, a0: 6, r: 22, deep: 28, blur: 12, cx: 240, D: 1800, X: [34, 446], fs: 17, fsv: 17,
        big: [28, 88, 78], l1: 120, l2: 145, l3: 170, l4: 195, con: [28, 240, 282, 309, 334, 359], vr: null,
        ref: 404, top: 422, pitch: 40, gh: 32, gap: 10, tail: [34, 64, 100, 152] }
    : { w: 1000, phone: false, a0: 14, r: 30, deep: 40, blur: 16, cx: 500, D: 2200, X: [446, 950], fs: 13.5, fsv: 13,
        big: [56, 96, 86], l1: 128, l2: 150, l3: 172, con: [668, 52, 96, 128, 150, 172], vr: 640,
        ref: 206, top: 220, bottom: 664, pmax: 27, gap: 11, gx: 52, lx: 424, tail: [24, 50], h: 748 };
}
const sx = (g, s) => mix(g.X[0], g.X[1], (s - DOM[0]) / (DOM[1] - DOM[0]));

/* The layout of comparison v: the y of every shown slot and group, and the plate's height. */
function layout(v) {
  const g = S.g, rows = SLOTS.filter(s => s.ids[v]), used = [...new Set(rows.map(s => s.group))];
  const ys = {}, gy = {};
  if (g.phone) {
    let y = g.top;
    used.forEach((gid, k) => {
      if (k) y += g.gap;
      gy[gid] = y + 20; y += g.gh;
      rows.filter(s => s.group === gid).forEach(s => { ys[s.i] = y; y += g.pitch; });
    });
    return { ys, gy, bottom: y + 4, h: y + g.tail[3] + 26 };
  }
  const pitch = Math.min(g.pmax, (g.bottom - g.top - g.gap * (used.length - 1)) / rows.length);
  let y = g.top;
  used.forEach((gid, k) => {
    if (k) y += g.gap;
    gy[gid] = y;
    const mine = rows.filter(s => s.group === gid), y0 = y;
    mine.forEach(s => { ys[s.i] = y; y += pitch; });
    y = Math.max(y, y0 + 30);  // room for the family's two-line name
  });
  return { ys, gy, pitch, bottom: g.bottom, h: g.h };
}

const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z, cy) {
  const X = x - g.cx, Y = y - cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, cy + y1 * k];
}
function slab(g, h, z) {
  const x0 = g.a0, y0 = g.a0 - (g.phone ? 0 : 6), x1 = g.w - g.a0, y1 = h - g.a0, r = g.r, p = [], cy = h / 2;
  const corner = (cx, cyy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cyy + r * Math.sin((a0 + 15 * i) * RAD), z, cy)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}

/* The picture, built once per layout. Everything on the plate sits in one group #face; the sway moves the plate in
   perspective and the face with it by a shift and a scale, so names never tilt. */
function build() {
  const g = S.g = geo(), svg = $("svg");
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const T = (id, cls, size, anchor, text) => `<text${id ? ` id="${id}"` : ""} class="${cls}" font-size="${size}"${anchor ? ` text-anchor="${anchor}"` : ""}>${text || ""}</text>`;
  const fs = g.fs;
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" id="glow" fill="url(#atmo)"/><rect class="shade" id="shade" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/><ellipse class="spec" id="shine" fill="url(#spec)"/>` +
    `<g id="face"><g class="read">` +
    T("big", "big", g.big[2]) + T("l1", "l1", g.phone ? 18 : 17) + T("l2", g.phone ? "l1" : "l2", g.phone ? 18 : 14) + T("l3", "l2", g.phone ? 17 : 14) + (g.phone ? T("l4", "l2", 17) : "") +
    (g.vr ? `<line class="vrule" x1="${g.vr}" x2="${g.vr}" y1="34" y2="178"/>` : "") +
    T("ccap", "ccap", g.phone ? 17 : 14, "", "Best rule on untrained weights") + T("cnum", "cnum", g.phone ? 38 : 46) +
    T("cname", "cname", g.phone ? 17 : 14.5) + T("ccount", "cci", g.phone ? 17 : 14) + T("cci", "cci", g.phone ? 17 : 14) + `</g>` +
    `<g class="frame"><rect class="gapband" id="gapband"/><path class="grid" id="grid"/><path class="sep" id="sep"/>` +
    `<line class="ref" id="ref0"/><line class="ref rl" id="ref1"/>` +
    T("rlab0", "rlab", fs, "middle", "0 % Base + cue") + T("rlab1", "rlab rl", fs, "middle", "100 % RL") +
    T("past", "past", fs, "middle", "Past RL →") +
    TICKS.map(v => T("tk" + v, "tick", g.phone ? 17 : 12.5, "middle", minus(v + " %"))).join("") +
    T("atitle", "atitle", g.phone ? 17 : 13, g.phone ? "" : "end", "Share of the gap closed") +
    GROUPS.map((gr, k) => `<g id="g${k}">` + T("gn" + k, "gname", fs, "", esc(gr[1])) + T("gs" + k, "gsub", g.phone ? fs : 12, "", esc(gr[2])) + `</g>`).join("") +
    `<g id="key">` +
    `<circle class="pt" id="k0" r="4.4"/>${T("kt0", "klab", g.phone ? 17 : 12.5, "", "Mean of 4 samples per problem")}` +
    `<circle class="pt hollow" id="k1" r="4.4"/>${T("kt1", "klab", g.phone ? 17 : 12.5, "", "One draw, separate run")}` +
    `<g class="reward"><circle class="pt" id="k2" r="4.4"/></g>${T("kt2", "klab", g.phone ? 17 : 12.5, "", "Reward-trained weights")}</g>` +
    `</g><g class="marks">` +
    SLOTS.map(s => `<g id="s${s.i}" style="display:none"><circle class="halo" id="ha${s.i}" r="11" style="display:none"/>` +
      `<line class="iv" id="iv${s.i}"/><path class="far" id="far${s.i}"/><circle class="ring" id="rg${s.i}" r="8.5" style="display:none"/>` +
      `<circle class="sel" id="se${s.i}" r="9.5" style="display:none"/><circle class="pt" id="pt${s.i}" r="${g.phone ? 5 : 4.6}"/>` +
      T("rw" + s.i, "row", fs, g.phone ? "" : "end") + T("va" + s.i, "val", g.fsv) + `</g>`).join("") +
    `</g><g class="rows" role="group" aria-label="The configurations of this comparison. Arrow keys move between them, Enter opens one.">` +
    SLOTS.map(s => `<rect class="hit" id="h${s.i}" data-slot="${s.i}" tabindex="-1" role="button" style="display:none"/>`).join("") + `</g></g>`;
  S.el = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  S.txt = {};
}
const setText = (id, v) => { if (S.txt[id] !== v) S.el[id].textContent = S.txt[id] = v; };
const at = (el, x, y) => { el.setAttribute("x", f(x)); el.setAttribute("y", f(y)); };

/* A change of comparison: every slot gets a target (its configuration's share and interval, its row, shown or not),
   reached over 750 ms; slots start a few milliseconds apart from top to bottom, so the eye can follow. */
function target(v, now, entrance) {
  const L = layout(v), g = S.g, view = VIEWS[v];
  let n = 0;
  const order = [...SLOTS].sort((a, b) => (L.ys[a.i] ?? 1e4) - (L.ys[b.i] ?? 1e4));
  order.forEach(s => {
    const id = s.ids[v], r = id && ROWS[id], y = id ? L.ys[s.i] : s.cur.y;
    const to = r ? { x: r.share[0], lo: r.share[1], hi: r.share[2], y, op: 1 } : { ...s.cur, op: 0 };
    if (r && !s.cur.op) Object.assign(s.cur, { x: 0, lo: 0, hi: 0, y });  // a new row grows out of the 0 % line
    s.from = { ...s.cur }; s.to = to;
    const fresh = r && !s.from.op;
    s.dur = r ? 750 : 260;
    s.t0 = still.matches ? -1e9 : !r ? now : now + (entrance ? 30 : 13) * n + (entrance ? 650 : fresh ? 220 : 0);
    if (r) n++;
    s.id = id || s.id;
    s.show = !!r;
    if (r) setRow(s, r, view);
  });
  GROUPS.forEach((gr, k) => {
    const G = S.groups[k], y = L.gy[gr[0]];
    G.from = { y: G.y, op: G.op }; G.to = { y: y ?? G.y, op: y == null ? 0 : 1 };
    if (y != null && !G.op) G.from.y = y;
    G.t0 = still.matches ? -1e9 : now + (entrance ? 500 : 0);
  });
  S.hfrom = S.h ?? L.h; S.hto = L.h; S.ht0 = still.matches ? -1e9 : now;
  S.L = L;
  const lr = ROWS[view.lead], cr = ROWS[view.contrast];
  const goal = [lr.share[0], lr.share[1], lr.share[2], cr.share[0]];
  const start = S.nums && !entrance ? S.nums.now : entrance ? [0, 0, 0, 0] : goal;
  S.nums = { from: start, to: goal, now: start, t0: still.matches ? -1e9 : now + (entrance ? 650 : 0) };
  readText(view, lr, cr);
}
/* The words of a row: its label, and the classes for reward, one draw, the large number and the contrast. */
function setRow(s, r, view) {
  const E = S.el, cls = [rewardOf(r) ? "reward" : "", r.id === view.lead ? "lead" : "", r.id === view.contrast ? "contrast" : ""].filter(Boolean).join(" ");
  E["s" + s.i].setAttribute("class", cls);
  E["pt" + s.i].setAttribute("class", "pt" + (filled(r.id) ? "" : " hollow"));
  setText("rw" + s.i, C.short[r.id]);
  E["ha" + s.i].style.display = r.id === view.lead ? "" : "none";
  E["rg" + s.i].style.display = r.id === view.contrast ? "" : "none";
}
function readText(view, lr, cr) {
  const g = S.g;
  const counts = `${lr.s.right} of ${N} right; RL ${C.views_s[view.id][1]}, Base + cue ${C.views_s[view.id][0]}`;
  const ci = `95 % interval ${pc(lr.share[1])} to ${pc(lr.share[2])}`;
  if (g.phone) {
    setText("l1", "of the gap closed by");
    setText("l2", C.short_lead[lr.id]);
    setText("l3", `${counts}, T 1.0`);
    setText("l4", ci);
  } else {
    setText("l1", `of the gap closed by ${C.short_lead[lr.id]}`);
    setText("l2", `${counts} (328 harder problems, T 1.0)`);
    setText("l3", ci);
  }
  setText("ccount", `${cr.s.right} of ${N} right`);
  setText("cname", C.short_lead[cr.id]);
  setText("cci", cr.share[2] > cr.share[1] ? `95 % interval ${pc(cr.share[1])} to ${pc(cr.share[2])}` : "This is the 0 % of the scale.");
}

/* Every frame: the sway, the plate, and whatever is still moving. */
function place(now) {
  const g = S.g, E = S.el, L = S.L;
  const tw = (o, d) => ease(clamp((now - o.t0) / d, 0, 1));
  const h = S.h = mix(S.hfrom, S.hto, ease(clamp((now - S.ht0) / 800, 0, 1)));
  const cy = h / 2;
  if (g.phone) $("svg").setAttribute("viewBox", `0 0 ${g.w} ${f(h)}`);
  else if (!S.vb) { $("svg").setAttribute("viewBox", `0 0 ${g.w} ${g.h}`); S.vb = 1; }
  E.back.setAttribute("d", slab(g, h, -g.deep));
  E.plate.setAttribute("d", slab(g, h, 0));
  const aw = g.w - 2 * g.a0, ah = h - 2 * g.a0;
  E.glow.setAttribute("cx", g.cx); E.glow.setAttribute("cy", f(cy)); E.glow.setAttribute("rx", f(aw * .8)); E.glow.setAttribute("ry", f(Math.min(ah * .9, aw * 1.3)));
  E.shade.setAttribute("x", f(g.a0 + aw * .012)); E.shade.setAttribute("y", f(g.a0 + ah * .03)); E.shade.setAttribute("width", f(aw)); E.shade.setAttribute("height", f(ah)); E.shade.setAttribute("rx", g.r);
  const spx = g.a0 + aw * .3, spy = g.a0 + Math.min(ah * .2, 180);
  E.shine.setAttribute("cx", f(spx)); E.shine.setAttribute("cy", f(spy)); E.shine.setAttribute("rx", f(aw * .26)); E.shine.setAttribute("ry", f(Math.min(ah * .16, 130)));
  // The face follows the plate: the shift and scale of the plate's centre and corners, no shear.
  const c = proj(g, g.cx, cy, 0, cy), r1 = proj(g, g.cx + 100, cy, 0, cy), d1 = proj(g, g.cx, cy + 100, 0, cy);
  const kx = (r1[0] - c[0]) / 100, ky = (d1[1] - c[1]) / 100;
  E.face.setAttribute("transform", `matrix(${kx.toFixed(4)} 0 0 ${ky.toFixed(4)} ${f(c[0] - kx * g.cx)} ${f(c[1] - ky * cy)})`);

  if (S.moving || S.first) frameMarks(now, tw);
  // The large number and the contrast count with the marks.
  const p = tw(S.nums, 800);
  S.nums.now = S.nums.from.map((v, i) => mix(v, S.nums.to[i], p));
  setText("big", pc(S.nums.now[0]));
  setText("cnum", pc(S.nums.now[3]));
}
function frameMarks(now, tw) {
  const g = S.g, E = S.el, L = S.L, bottom = mix(S.boFrom ?? L.bottom, L.bottom, ease(clamp((now - S.ht0) / 800, 0, 1)));
  let moving = false;
  // The frame: readout, the gap band, the reference lines, grid, ticks, key.
  at(E.big, g.big[0] - 3, g.big[1]);
  at(E.l1, g.big[0], g.l1); at(E.l2, g.big[0], g.l2); at(E.l3, g.big[0], g.l3); if (g.phone) at(E.l4, g.big[0], g.l4);
  at(E.ccap, g.con[0], g.con[1]); at(E.cnum, g.con[0] - 2, g.con[2]); at(E.cname, g.con[0], g.con[3]); at(E.ccount, g.con[0], g.con[4]); at(E.cci, g.con[0], g.con[5]);
  const x0 = sx(g, 0), x1 = sx(g, 100), yt = g.ref + 6, yb = bottom + 2;
  E.gapband.setAttribute("x", f(x0)); E.gapband.setAttribute("y", f(yt)); E.gapband.setAttribute("width", f(x1 - x0)); E.gapband.setAttribute("height", f(yb - yt));
  [["ref0", x0], ["ref1", x1]].forEach(([id, x]) => { const e = E[id]; e.setAttribute("x1", f(x)); e.setAttribute("x2", f(x)); e.setAttribute("y1", f(yt - 2)); e.setAttribute("y2", f(yb)); });
  at(E.rlab0, x0, g.ref); at(E.rlab1, x1, g.ref); at(E.past, sx(g, 200), g.ref);
  let grid = "";
  TICKS.forEach(v => { const x = sx(g, v); if (v !== 0 && v !== 100) grid += `M${f(x)} ${f(yt)}V${f(yb)}`; at(E["tk" + v], x, yb + g.tail[0] - 4); });
  E.grid.setAttribute("d", grid);
  if (g.phone) { at(E.atitle, g.X[0], yb + g.tail[1]); }
  else at(E.atitle, g.X[1], yb + g.tail[1]);
  const ky = g.phone ? [yb + g.tail[2], yb + g.tail[2] + 26, yb + g.tail[2] + 52] : [yb + g.tail[1], yb + g.tail[1], yb + g.tail[1]];
  const kx = g.phone ? [g.X[0] + 4, g.X[0] + 4, g.X[0] + 4] : [g.gx + 4, g.gx + 218, g.gx + 384];
  for (let k = 0; k < 3; k++) {
    E["k" + k].setAttribute("cx", f(kx[k])); E["k" + k].setAttribute("cy", f(ky[k] - 4));
    at(E["kt" + k], kx[k] + 11, ky[k]);
  }
  // The family names and the hairlines between families.
  let sep = "";
  GROUPS.forEach((gr, k) => {
    const G = S.groups[k], p = tw(G, 750);
    G.y = mix(G.from.y, G.to.y, p); G.op = mix(G.from.op, G.to.op, p);
    if (p < 1) moving = true;
    E["g" + k].setAttribute("opacity", G.op.toFixed(2));
    E["g" + k].style.display = G.op < .01 ? "none" : "";
    if (g.phone) {
      at(E["gn" + k], g.X[0], G.y);
      const w = S.gw?.[k] ?? (S.gw = S.gw || [], S.gw[k] = E["gn" + k].getComputedTextLength());
      at(E["gs" + k], g.X[0] + w + 8, G.y);
      if (G.op > .01 && k !== firstGroup()) sep += `M${g.X[0]} ${f(G.y - 24)}H${g.X[1]}`;
    } else {
      at(E["gn" + k], g.gx, G.y + L.pitch * .5 + 4.5);
      at(E["gs" + k], g.gx, G.y + L.pitch * .5 + 20);
      if (G.op > .01 && k !== firstGroup()) sep += `M${g.gx} ${f(G.y - g.gap * .5)}H${g.X[1]}`;
    }
  });
  E.sep.setAttribute("d", sep);
  // The rows.
  const view = VIEWS[S.view], half = (L.pitch || g.pitch) / 2;
  SLOTS.forEach(s => {
    if (!s.to) return;
    const p = tw(s, s.dur || 750), c = s.cur;
    for (const k in s.to) c[k] = mix(s.from[k], s.to[k], p);
    if (p < 1) moving = true;
    const grp = E["s" + s.i], hit = E["h" + s.i];
    if (c.op < .01 && !s.show) { grp.style.display = "none"; hit.style.display = "none"; return; }
    grp.style.display = ""; grp.setAttribute("opacity", c.op.toFixed(2));
    const my = g.phone ? c.y + 27 : c.y + half, ly = g.phone ? c.y + 13 : c.y + half + 4.6;
    const lo = clamp(c.lo, DOM[0], DOM[1]), hi = clamp(c.hi, DOM[0], DOM[1]), xp = clamp(c.x, DOM[0], DOM[1]);
    const iv = E["iv" + s.i], xa = sx(g, lo), xb = sx(g, hi), xm = sx(g, xp);
    iv.setAttribute("x1", f(xa)); iv.setAttribute("x2", f(xb)); iv.setAttribute("y1", f(my)); iv.setAttribute("y2", f(my));
    iv.style.display = hi - lo > .5 ? "" : "none";
    // Beyond the axis: a small arrowhead at the edge.
    let far = "";
    if (c.x < DOM[0] - .5) far += `M${f(xm - 8)} ${f(my - 4.5)}L${f(xm - 15)} ${f(my)}L${f(xm - 8)} ${f(my + 4.5)}Z`;
    else if (c.lo < DOM[0] - .5) far += `M${f(xa + 1)} ${f(my - 4)}L${f(xa - 6)} ${f(my)}L${f(xa + 1)} ${f(my + 4)}Z`;
    if (c.hi > DOM[1] + .5) far += `M${f(xb - 1)} ${f(my - 4)}L${f(xb + 6)} ${f(my)}L${f(xb - 1)} ${f(my + 4)}Z`;
    E["far" + s.i].setAttribute("d", far);
    ["pt", "ha", "rg", "se"].forEach(k => { E[k + s.i].setAttribute("cx", f(xm)); E[k + s.i].setAttribute("cy", f(my)); });
    at(E["rw" + s.i], g.phone ? g.X[0] : g.lx, ly);
    // The value beside the mark, for the large number, the contrast, the selection and a mark beyond the axis.
    const r = ROWS[s.id], show = r && s.show && (r.id === view.lead || r.id === view.contrast || (S.pick && S.pick.id === r.id) || c.x < DOM[0]);
    const va = E["va" + s.i];
    va.style.display = show ? "" : "none";
    if (show) {
      setText("va" + s.i, pc(c.x));
      const right = c.x < DOM[0] ? xm + 12 : Math.max(xb, xm + 4) + 10;
      at(va, right, my + 4.4);
    }
    hit.style.display = s.show ? "" : "none";
    if (s.show) {
      const top = g.phone ? c.y - 2 : c.y, hh = g.phone ? g.pitch : L.pitch;
      hit.setAttribute("x", f(g.phone ? g.X[0] - 8 : g.gx + 120)); hit.setAttribute("width", f(g.phone ? g.X[1] - g.X[0] + 16 : g.X[1] + 20 - g.gx - 120));
      hit.setAttribute("y", f(top)); hit.setAttribute("height", f(hh)); hit.setAttribute("rx", 6);
      hit.setAttribute("aria-label", r ? `${C.groupname[s.group]}: ${C.short[r.id]}, ${pc(r.share[0])} of the gap` : "");
    }
  });
  SLOTS.forEach(s => { S.el["se" + s.i].style.display = S.pick && s.show && s.id === S.pick.id ? "" : "none"; S.el["rw" + s.i].setAttribute("class", "row" + (S.pick && s.show && s.id === S.pick.id ? " on" : "")); });
  S.boFrom = bottom;
  S.moving = moving;
  S.first = false;
}
const firstGroup = () => GROUPS.findIndex((gr, k) => S.groups[k].to && S.groups[k].to.op > 0);

function frame(now) {
  requestAnimationFrame(frame);
  if (now - S.last < 30) return;
  S.last = now;
  S.t = now / 1000;
  if (still.matches) aim(0, 0);
  else {
    V.px += (V.tx - V.px) * .08;
    V.py += (V.ty - V.py) * .08;
    aim(2.4 * Math.sin(S.t * .13) + 2.2 * V.px, 1.1 * Math.sin(S.t * .09) - 1.2 * V.py);
  }
  place(now);
}

/* The control and the address. */
function setView(v, push) {
  if (v === S.view && S.L) return;
  const was = S.view;
  S.view = v;
  // A detail that is open follows its slot to the new comparison, or closes.
  if (S.pick) {
    const slot = SLOTS.find(s => s.ids[was] === S.pick.id), id = slot && slot.ids[v];
    S.pick = id ? ROWS[id] : null;
    if (!S.pick && S.open === "row") S.open = null;
  }
  target(v, performance.now(), false);
  S.moving = true;
  controls();
  pane();
  address(push);
}
function controls() {
  [...$("switch").children].forEach((b, i) => b.setAttribute("aria-pressed", String(i === S.view)));
  $("hint").textContent = VIEWS[S.view].hint + " Click a row for its details.";
  const view = VIEWS[S.view], lr = ROWS[view.lead];
  $("svg").setAttribute("aria-label", `Share of the gap from Base + cue to RL closed by each configuration on the 328 harder problems, ${view.name}. ` +
    `${C.short_lead[lr.id]} closes ${pc(lr.share[0])}, 95 % interval ${pc(lr.share[1])} to ${pc(lr.share[2])}.`);
  rovable();
}
function address(push) {
  const parts = [S.view ? VIEWS[S.view].id : "", S.pick ? S.pick.id : "", S.open && S.open !== "row" ? S.open : ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const v = VIEWS.findIndex(w => parts.includes(w.id)), p = C.panels.find(p => parts.includes(p[0]));
  const nv = v < 0 ? 0 : v;
  const r = parts.map(x => ROWS[x]).find(r => r && SLOTS.some(s => s.ids[nv] === r.id));
  S.pick = r || null;
  S.open = r ? "row" : p ? p[0] : null;
  if (first) { S.view = nv; return; }
  if (nv !== S.view) { S.view = nv; target(nv, performance.now(), false); S.moving = true; }
  S.moving = true;
  controls();
  pane();
}

/* The side column: the five panels, or the configuration the reader clicked. */
function rowPane(r) {
  const view = VIEWS[S.view], slot = SLOTS.find(s => s.ids[S.view] === r.id), lead = r.id === view.lead;
  const facts = [];
  facts.push(`<b>${r.s.right} of ${N}</b> right (${r.acc[0]} %, 95 % interval ${r.acc[1]} % to ${r.acc[2]} %)` +
    (r.wrong != null ? `; ${r.s.wrong} wrong and ${r.s.abst} with no answer.` : `. This draw stores only right or not; ${r.cap_hits} answers were cut off at 16,384 tokens.`));
  facts.push(`<b>${num(r.tokens)} tokens</b> per problem, ${r.mult[0].toFixed(2)} times one RL sample` +
    (r.mult.length > 2 ? ` (95 % interval ${r.mult[1].toFixed(2)} to ${r.mult[2].toFixed(2)}).` : "."));
  facts.push(`In this comparison 0 % is Base + cue at ${C.views_s[view.id][0]} of ${N} and 100 % is RL at ${C.views_s[view.id][1]} of ${N}` +
    (view.family === "vote" ? ", a gap of 29 problems." : "."));
  const notes = [C.rewardnote[r.reward]];
  if (/tie rule/.test(r.chosen)) notes.push("The tie rule was written on MATH-500 after reading the problems it fixes; here it is held out.");
  if (/no restart rows/.test(r.name)) notes.push("Think-SFT's run has no restarts, so this rule runs here without them.");
  if (/L set/.test(r.chosen)) notes.push(`The length of ${num(C.cap_L)} tokens was set from the token counts of the 328; no score was read.`);
  if (!filled(r.id)) notes.push("One draw per problem from a separate run, so it is noisier than a mean of 4 samples; the large number does not count it.");
  return `<div class="dhead"><h2><span>${esc(C.groupname[slot.group])}</span>${esc(C.short[r.id])}</h2><button class="close" data-open="">Close</button></div>` +
    `<div class="share"><b class="${lead ? "blue" : ""}">${pc(r.share[0])}</b><span>of the gap closed, ${esc(view.name.toLowerCase())}<br>` +
    (r.share[2] > r.share[1] ? `95 % interval ${pc(r.share[1])} to ${pc(r.share[2])}` : "the end of the scale") + `</span></div>` +
    `<p class="lead">${esc(C.desc[r.id])}</p><ul class="facts">${facts.map(x => `<li>${x}</li>`).join("")}</ul>` +
    `<p class="note">${esc(notes.join(" "))}</p>`;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = S.open === "row" && S.pick ? rowPane(S.pick)
    : p ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ block: "start", behavior: still.matches ? "auto" : "smooth" }); };
function open(key) {
  const was = S.open, mark = S.pick;
  S.open = key || null;
  if (!key) S.pick = null;
  S.moving = true;
  address(true);
  pane();
  const back = was === "row" && mark ? SLOTS.find(s => s.show && s.id === mark.id) : null;
  const to = key ? $("pane").querySelector(".close") : back ? S.el["h" + back.i] : $("pane").querySelector(`[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  if (key) show();
}
function pick(slot) {
  const s = SLOTS[slot];
  if (!s || !s.show) return;
  S.pick = ROWS[s.id]; S.open = "row"; S.moving = true;
  rove(s);
  address(true);
  pane();
  show();
}
/* The rows are one stop in the tab order; the arrow keys move along them from top to bottom. */
const visible = () => SLOTS.filter(s => s.ids[S.view]).sort((a, b) => S.L.ys[a.i] - S.L.ys[b.i]);
function rove(s) {
  SLOTS.forEach(o => S.el["h" + o.i].setAttribute("tabindex", "-1"));
  S.rove = s.i;
  S.el["h" + s.i].setAttribute("tabindex", "0");
}
function rovable() {
  const vis = visible(), keep = vis.find(s => s.i === S.rove) || vis.find(s => S.pick && s.ids[S.view] === S.pick.id) || vis[0];
  rove(keep);
}

$("switch").innerHTML = VIEWS.map((v, i) => `<button data-view="${i}" aria-pressed="false">${esc(v.name)}</button>`).join("");
$("switch").addEventListener("click", e => { const b = e.target.closest("[data-view]"); if (b) setView(Number(b.dataset.view), true); });
document.addEventListener("click", e => { const o = e.target.closest("[data-open]"); if (o) open(o.dataset.open); });
const svg = $("svg");
svg.addEventListener("click", e => { const h = e.target.closest(".hit"); if (h) pick(Number(h.dataset.slot)); });
svg.addEventListener("keydown", e => {
  const h = e.target.closest(".hit");
  if (!h) return;
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(Number(h.dataset.slot)); return; }
  const step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
  if (!step) return;
  e.preventDefault();
  const vis = visible(), k = vis.findIndex(s => s.i === Number(h.dataset.slot)), s = vis[(k + step + vis.length) % vis.length];
  rove(s);
  S.el["h" + s.i].focus();
});
document.addEventListener("keydown", e => { if (e.key === "Escape" && S.open) open(""); });
addEventListener("popstate", () => fromHash(false));
addEventListener("hashchange", () => fromHash(false));
narrow.addEventListener("change", () => { build(); S.gw = null; S.vb = 0; S.h = null; S.boFrom = null; target(S.view, -1e9, false); S.first = true; controls(); });
const stage = $("stage");
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1;
  V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("problem").textContent = C.problem;
$("say").innerHTML = esc(C.line).replace(/(?<![\w-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");
aim(0, 0);
build();
fromHash(true);
/* On load every mark starts on the 0 % line, Base + cue, and travels out to its share; the large number counts with it. */
target(S.view, performance.now(), !location.hash && !still.matches);
S.first = true; S.moving = true;
controls();
pane();
place(performance.now());
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "n": DATA["n"], "cap_L": DATA["cap_L"],
    "views": [{k: v[k] for k in ("id", "name", "family", "base", "rl", "hint", "lead", "contrast")} for v in VIEWS],
    "views_s": {v["id"]: [_count(v["base"]), _count(v["rl"])] for v in VIEWS}, "groups": GROUPS, "groupname": {g[0]: g[1] for g in GROUPS}, "slots": SLOTS, "short": SHORT, "desc": DESC,
    "short_lead": LEADNAME,
    "rewardnote": {"no": "No reward-trained weights.", "yes": "Uses reward-trained weights.",
                   "partly": "Partly uses reward-trained weights.", "yes (code reward)": "Uses weights trained with a reward on code."},
    "rows": [{**{k: r[k] for k in ("id", "name", "reward", "chosen", "right", "wrong", "abst", "share", "tokens", "mult", "cap_hits") if k in r},
              "s": {k: _count(r[k]) for k in ("right", "wrong", "abst")}, "acc": [f"{v:.1f}" for v in r["acc"]]}
             for r in DATA["rows"]]}, ensure_ascii=False))

if __name__ == "__main__":  # DATA against its artifact; run from the repository root
    import re
    run, table = json.load(open(RUN + "run.json")), json.load(open(DATA["artifact"]))
    assert run["commit"].startswith(DATA["code_commit"]) and table["n"] == DATA["n"] and table["cap_L_matched"] == DATA["cap_L"]
    assert len(table["rows"]) == len(DATA["rows"]) == 49
    r2 = lambda v: None if v is None else round(v, 2)
    for r, t in zip(DATA["rows"], table["rows"]):
        tm = t["token_multiple"]
        assert r["id"] == re.sub(r"[^a-z0-9.]+", "-", t["key"].lower()).strip("-") and r["key"] == t["key"], r["id"]
        assert (r["name"], r["family"], r["n"], r["reward"], r["chosen"], r["source"]) == (
            t["name"], t["family"], t["n_samples"], t["reward"], t["chosen_on_328"], t["source"]), r["id"]
        assert (r["right"], r["wrong"], r["abst"], r["tokens"]) == (r2(t["right"]), r2(t["wrong"]), r2(t["abstained"]), round(t["tokens"])), r["id"]
        for k, src in (("acc", t["accuracy"]["percent"]), ("share", t["share"]["percent"]), ("vs_rl", t["minus_rl_single"]["points"])):
            iv = t[{"acc": "accuracy", "share": "share", "vs_rl": "minus_rl_single"}[k]]["interval95"]
            assert r[k] == [r2(src)] + [r2(v) for v in iv], (r["id"], k)
        assert r["mult"] == [round(tm["x"], 3)] + ([round(v, 3) for v in tm["interval95"]] if tm["interval95"] else []), r["id"]
        assert r.get("cap_hits") == t.get("cap_hits"), r["id"]
    # Every row is in a slot, every slot's row is in its comparison, and each comparison shows exactly its rows.
    for k, v in enumerate(VIEWS):
        shown = [s[1 + k] for s in SLOTS if s[1 + k]]
        assert sorted(shown) == sorted(members(v)) and len(shown) == len(set(shown)), v["id"]
        assert all(_ROWS[s[1 + k]]["family"] == v["family"] for s in SLOTS if s[1 + k])
        b = next(r for r in DATA["rows"] if r["id"] == ("base-single" if v["family"] == "single" else "base-vote4"))
        q = next(r for r in DATA["rows"] if r["id"] == ("rl-single" if v["family"] == "single" else "rl-vote4"))
        assert (v["base"], v["rl"]) == (b["right"], q["right"]) and b["share"][0] == 0 and q["share"][0] == 100, v["id"]
    assert {i for s in SLOTS for i in s[1:] if i} == set(_ROWS) and set(SHORT) >= set(_ROWS) and set(DESC) >= set(_ROWS)
    assert all(_ROWS[s[1 + k]] and GROUPS[[g[0] for g in GROUPS].index(s[0])] for s in SLOTS for k in range(3) if s[1 + k])
    # The sentences of the page, against the README section and the board result.
    got = {v["id"]: (v["lead"], round(_ROWS[v["lead"]]["share"][0]), v["contrast"], round(_ROWS[v["contrast"]]["share"][0])) for v in VIEWS}
    assert got == {"one": ("think-single", 122, "base-restart", 20), "vote": ("think-vote4", 169, "base-vote4-restart-short", 24),
                   "tokens": ("think-capl", 79, "base-single", 0)}, got
    assert [round(x) for x in _ROWS["think-vote4"]["share"][1:]] == [128, 250] and [round(x) for x in _ROWS["think-single"]["share"][1:]] == [103, 144]
    assert [round(x) for x in _ROWS["think-capl"]["share"][1:]] == [62, 98]
    assert _ROWS["rl-vote4"]["right"] - _ROWS["base-vote4"]["right"] == 29
    assert (round(_seed[1]["share"][0]), round(_seed[0]["share"][0]), round(_seed[2]["share"][0])) == (146, 146, 107)
    move = max(abs(t[a]["share"]["percent"] - t["share"]["percent"]) for t in table["rows"] for a in ("clean322", "v4") if isinstance(t.get(a), dict) and "share" in t[a])
    assert move <= 3.5, move
    checks = json.load(open(RUN + "checks.json"))
    assert checks["passed"] == len(checks["posted_numbers"]) == 176 and not checks["failed"]
    assert [p["got_percent"] for p in checks["planted"][:2]] == [100.0, 0.0]
    print("DATA matches", DATA["artifact"], "(table.json, run.json, checks.json)")
