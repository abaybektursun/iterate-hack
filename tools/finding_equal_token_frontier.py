"""No rule that spends more samples on the base model reaches one sample of its RL version on MATH-500, up to 4.2 times the tokens.

The page of one finding, served at /finding/equal-token-frontier (view.py serves every tools/finding_<slug>.py) and
reached from its tile on /findings, which ICON draws. The picture is one lit plate holding a scatter: right answers on
MATH-500 against generated tokens per problem, one mark per rule and model (24 rules for the base model with the cue, the
same 24 for the RL model), and the score of one RL sample as a level line. The reader's one control is a token budget, a
line across the chart dragged along the x axis (or the arrow keys on it): rules that fit the budget light up, the best
base rule within it is ringed, the large number is its distance to one RL sample with its interval, and the strip under
the chart lights the problems that rule answers right. Clicking a mark names the rule and shows one real problem in the
side column. Address: /finding/equal-token-frontier#<budget>/<model>-<rule>/<panel>. The rules are in
.claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py (.claude/skills/site-ui/SKILL.md).
Study: studies/rlneurons, README section "Token frontier"; board result-40ed3b.

    python3 tools/finding_equal_token_frontier.py    checks DATA against the artifacts it was copied from
"""
import json

import finding_vote_over_four as _vote  # the vote over k of 12 samples, quoted once in "What it does not show"

RUN = "studies/rlneurons/results/frontier/math500-01/"

# Every number is copied from the artifacts named here. None is typed from memory. The deployed site ships only
# tools/*.py, so the copy is a literal; run this file to compare it with the artifacts.
# rules: one row per model and rule of frontier.json (configuration, right_24, tokens_per_problem_24, ran_out), with
# readout.json's base_minus_rl_single (gap: points, interval; multiple: token_multiple) and rl_minus_base (rl_lead) for
# the base rules. grid: per_problem.json per_problem.<model>.<rule>.s, problem i as the letter "a" + 24 * s: in how many
# of the 24 draw orders the rule answers problem i right.
DATA = {
    "artifact": RUN + "readout.json",
    "commit": "c269f7a",  # run.json of the frontier run: the commit of analysis/frontier.py
    "source_commit": "c36f562",  # run.json source_commits: the commit of both sampling jobs
    "jobs": {"base": "abaybektursun-1114-153825-208b", "rl": "abaybektursun-1114-183640-e828"},  # run.json source_jobs
    "models": {"base": "allenai/Olmo-3-1025-7B", "rl": "allenai/Olmo-3.1-7B-RL-Zero-Math"},  # day1_3 run.json model_repo
    "n": 500,
    "rl_single": {"right": 460.0, "tokens": 4686.79},  # readout.json rl_single_24
    "rules": [
    {"model": "base", "rule": "single", "config": "one sample", "right": 410.5, "tokens": 4008.3875, "ran_out": 0, "gap": [-9.9, -11.6, -8.3], "multiple": 0.86, "rl_lead": [9.9, 8.3, 11.6],
     "grid": "ysyysyyyyasgyyssysaymmsyysayysyysysyyyygyyyayssyssgssyyyyyyymyysgyyyyysgyyyyyyyygsyyyyyysymyyymyasyygayagyyyymayyysmyyyssysyyygymyyyyyyyssmyyssyysyyyysyyyaysyyyyyyysyayayayyyyysssysyyymyyyygsyyysysysyyyyyamyyyyayyyayymymsymyssssgyyygysyysyaaymyysyysyyyysyyyyyyyyyyaysyyyyysssyyyyayyyygyayyyyyyysayyyyyaygyyayayysysyyymyyyyyyaysgyyysmmssyyysayyyyyyyyayygyysyysgyyyyysyyyayysyyyysysygsyygyyysysassymyssamsgyyyyysyssyyyyyysssayyayyyysymsyyyssyyysygsyyyyyyyysyyymyayyyyygyyyssmmymyysyygsysssyyymgyymyymyy"},
    {"model": "base", "rule": "restart", "config": "one sample, sampled again after a cap hit (up to 2 times)", "right": 418.0, "tokens": 4924.2475, "ran_out": 0, "gap": [-8.4, -10.1, -6.8], "multiple": 1.05, "rl_lead": [9.0, 7.4, 10.7],
     "grid": "ysyysyyyygsgyyssysaymmsyysgyysyysysyyyygyyyayssyssgssyyyyyyysyysmyyyyysgyyyyyyyygsyyyyyyyymyyymyasyyggyagyyyysayyysmyyysyysyyysymyyyyyyyssmyyssyysyyyysyyyayyyyyyyyysyayaymyyyyysssysyyymyyyyssyyyyysysyyyyyasyyyyayyyayymymsymyssssgyyygysyysyaaymyysyysyyyysyyyyyyyyyyaysyyyyysssyyyyayyyygyayyyyyyysmyyyyygymyyayayyyysyyymyyyyyyaysgyyysmmsyyyysayyyyyyyyayymyysyysgyyyyyyyyyayysyyyysysygsyygyyysysassymyssamsgyyyyysyssyyyyyysssayymyyyysyysyyyssyyysygsyyyyyyyysyyymyayyyyygyyyssmmymyysyygsysssyyymgyymyysyy"},
    {"model": "base", "rule": "R8000", "config": "one sample, abandoned at 8,000 tokens and drawn again", "right": 424.0, "tokens": 6410.027333333333, "ran_out": 37, "gap": [-7.2, -9.0, -5.4], "multiple": 1.37, "rl_lead": [8.033333333333337, 6.3, 9.9],
     "grid": "ysyysyyyyasmyyqmysayqysyysayysyyyysyyyygyyyayssyssgssyyyyyyyyyysyyyyyysyyyyyyyyyasyyyyyysymyyymyasyyaayayyyyyyayyysmyyysyysyyyyyqyyyyyyyyyqyysyyyyyyyyyyyyaysyyyyyyyqyayayayyyyysysysyyymyyyyysyyyyysysyyyyyayyyyyayyyayyqymyyyyqsysiyyygysyysyaaymyysyysyyyysyyyyyyyyyyaysyyyyyssqyyyyayyyyayayyyyyyysayyyyyayyyyayayyyysyyyyyyyyyyaysgyyysmysyyyymayyyyyyyyayygyyyyysgyyyyyyyyyayyqyyyyyysyasyygyyysyyasyyayssamsgyyyyysyyyyyyyyyysyayyayyyysyyyyyyssyyysygsyyyyyyyyqyyyyyayyyyyayyyysmyymyyyyygsysssyyyagyymyymyy"},
    {"model": "base", "rule": "R12000", "config": "one sample, abandoned at 12,000 tokens and drawn again", "right": 423.9166666666667, "tokens": 5715.072666666667, "ran_out": 13, "gap": [-7.216666666666662, -9.0, -5.5], "multiple": 1.22, "rl_lead": [8.45, 6.7, 10.2],
     "grid": "ysyysyyyyasgyyssysayqysyysayysyyqysyyyygyyyayssyssgssyyyyyyyyyysmyyyyysgyyyyyyyygsyyyyyyyymyyyyyasyymayamyyyyyayyysmyyymyysyyyyymyyyyyyyqsmyysyyyyyyyysyyyayyyyyyyyysyayayayyyyysysysyyyqyyyyysyyyyysysyyyyyaqyyyyayyyayymyysymyssqsiyyygysyysyaaymyysyysyyyysyyyyyyyyyyaysyyyyysssyyyyayyyyiyayyyyyyysayyyyyayyyyayayyyysyyyyyyyyyyaysayyysyysyyyyqayyyyyyyyayygyyyyysgyyyyyyyyyayysyyyyyysyisyygyyysysassymyssaysgyyyyysyssyyyyyyssyayyayyyysyysyyyssyyysygyyyyyyyyysyyyqyayyyyygyyyysmyyqyyyyygsysssyyymgyyyyyqyy"},
    {"model": "base", "rule": "vote2", "config": "vote over 2", "right": 418.8333333333333, "tokens": 8016.775, "ran_out": 0, "gap": [-8.233333333333338, -9.9, -6.7], "multiple": 1.71, "rl_lead": [8.45, 6.9, 10.1],
     "grid": "ysyysyyyyasgyyssysaymqyyysayysyysysyyyygyyyayssyssgssyyyyyyyqyyskyyyyysgyyyyyyyygyyyyyyyyyqyyymyayyykayagyyyyuayyyymyyysyyyyyymymyyyyyyyssmyyysyyyyyyysyyyaysyyyyyyyyyayayayyyyysssysyyyqyyyyksyyyyysysyyyyyaqyyyyayyyayymymsymyssssgyyygysyyyyaaymyysyysyyyysyyyyyyyyyyaysyyyyysssyyyyayyyyiyayyyyyyysayyyyyayiyyayayysysyyyuyyyyyyaysgyyysmqysyyyyayyyyyyyyayykyysyyygyyyyyyyyyayysyyyysysyisyygyyysysassymysyaqsgyyyyysyssyyyyyysssayyayyyyyymsyyyssyyysyisyyyyyyyysyyymyayyyyygyyyssmmyqyysyymsysssyyymgyyqyyqyy"},
    {"model": "base", "rule": "vote3", "config": "vote over 3", "right": 442.1666666666667, "tokens": 12025.1625, "ran_out": 0, "gap": [-3.566666666666663, -5.1, -2.0], "multiple": 2.57, "rl_lead": [5.65, 4.0, 7.4],
     "grid": "yyyyyyyyyaygyyyyyyaymsyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyysyyymyyyyyygyyyyyyyyeyyyyyyyyysyyymyayyymayagyyyyyayyyyqyyyyyyyyyysyqyyyyyyyyyqyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyysyyyymyyyyyyyyyyyyyyasyyyyayyyayyqymyyqyyyyygyyyeyyyyyyaayqyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyiyayyyyyyyyayyyyyayiyyayayyyyyyyyyyyyyyyayygyyyyqsyyyyyyayyyyyyyyayymyyyyyygyyyyyyyyyayyyyyyyyyyygyyyeyyyyyyayyymyyyasyeyyyyyyyyyyyyyyyyyyayyayyyyyyqyyyyyyyyyyyiyyyyyyyyyyyyyqyayyyyygyyyyyqqysyyyyysyyyyyyyyqgyysyysyy"},
    {"model": "base", "rule": "vote4", "config": "vote over 4", "right": 448.25, "tokens": 16033.55, "ran_out": 0, "gap": [-2.35, -4.0, -0.7], "multiple": 3.42, "rl_lead": [5.216666666666662, 3.4, 7.2],
     "grid": "yyyyyyyyyaygyyyyyyaymyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyymyyyyyygyyyyyyyyayyyyyyyyyyyyymyayyymayagyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyyyyyyymyyyyyyyyyyyyyyayyyyyayyyayyyymyyyyyyyygyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyiyayyyyyyyyayyyyyayiyyayayyyyyyyyyyyyyyyayygyyyyyyyyyyyyayyyyyyyyayymyyyyyygyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyymyyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyyiyyyyyyyyyyyyyyyayyyyygyyyyyyyyyyyyyyyyyyyyyyyygyyyyyyyy"},
    {"model": "base", "rule": "vote2_short", "config": "vote over 2, ties to the shortest finished sample", "right": 428.6666666666667, "tokens": 8016.775, "ran_out": 0, "gap": [-6.266666666666662, -8.0, -4.5], "multiple": 1.71, "rl_lead": [7.866666666666663, 6.0, 9.7],
     "grid": "yyyyyyyyyaumyyqmyyayuuyyyyayymyyuyyyyyyiyyyayyqyuuimyyyyyyyyuyymmyyyyyqmyyyyyyyyiyyyyyyyyyuyyyuyayyyiayamyyyyuayyyyeyyymyyyyyymyqyyyyyyyuyqyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyymyyymyyymyyyymyyyyyyuymyyyyyaqyyyyayyyayymymyyuyqquumyyymymyyyyaayqyyyyyyyyyymyyyyyyyyyyayuyyyyyqumyyyyayyyyeyayyyyyyyyayyyyyaymyyayayyyyyyyyuyyyyyyayyiyyyquuyyyyyyayyyyyyyyayymyyuyyymyyyyyyyyyayymyyyyyymyiqyyeyyyyyyaqyyeyuyaqyeyyyyyqyyyyyyyyyyuyayyayyyyyyuuyyyymyyyuyiuyyyyyyyyuyyyuyayyyyyayyyuyiuyqyyyyymqyuyyyyyeeyyuyymyy"},
    {"model": "base", "rule": "vote3_short", "config": "vote over 3, ties to the shortest finished sample", "right": 446.5, "tokens": 12025.1625, "ran_out": 0, "gap": [-2.7, -4.3, -1.1], "multiple": 2.57, "rl_lead": [5.233333333333338, 3.5, 7.1],
     "grid": "yyyyyyyyyaysyyyyyyaymyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyysyyyyyysyyyyyyyyayyyyyyyyyyyyymyayyygayasyyyyyayyyymyyyyyyyyyysysyyyyyyyyysyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyymyyyysyyyyyyyyyyyyyyasyyyyayyyayymymyyyyyyyysyyymyyyyyyaaysyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyayayyyyyyyyayyyyyaysyyayayyyyyyyyyyyyyyyayygyyyyyyyyyyyyayyyyyyyyayysyyyyyysyyyyyyyyyayyyyyyyyyyygyyyayyyyyyayyymyyyasyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyygyyyyyyyyyyyyyyyayyyyyayyyyymyysyyyyysyyyyyyyymayyyyymyy"},
    {"model": "base", "rule": "vote4_short", "config": "vote over 4, ties to the shortest finished sample", "right": 453.0, "tokens": 16033.55, "ran_out": 0, "gap": [-1.4, -3.2, 0.4], "multiple": 3.42, "rl_lead": [4.4, 2.4, 6.4],
     "grid": "yyyyyyyyyayyyyyyyyayyyyyyyayyyyyyyyyyyyayyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyaayayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyayyyayyyyyyyyyyyyyyyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyayayyyyyyyyayyyyyayyyyayayyyyyyyyyyyyyyyayyayyyyyyyyyyyyayyyyyyyyayyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyyayyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyayyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyy"},
    {"model": "base", "rule": "vote4_restart", "config": "vote over 4 after restart", "right": 452.0833333333333, "tokens": 19696.99, "ran_out": 0, "gap": [-1.583333333333337, -3.2, 0.1], "multiple": 4.2, "rl_lead": [4.8, 3.1, 6.6],
     "grid": "yyyyyyyyyiygyyyyyyaymyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyyyyyyyyygyyyyyyyyayyyyyyyyyyyyymyayyyigyaiyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyayyyyyayyyayyyymyyyyyyyygyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyygyayyyyyyyyyyyyyygyyyyayayyyyyyyymyyyyyyayygyyyyyyyyyyyyayyyyyyyyayyyyyyyyygyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyymyyyamyayyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyiyyyyyyyyyyyyyyyayyyyygyyyyyymyyyyyyyyyyyyyyyyygyyyyyyyy"},
    {"model": "base", "rule": "vote4_restart_short", "config": "vote over 4 after restart, ties to the shortest", "right": 454.0, "tokens": 19696.99, "ran_out": 0, "gap": [-1.2, -3.0, 0.6], "multiple": 4.2, "rl_lead": [4.2, 2.4, 6.0],
     "grid": "yyyyyyyyyayyyyyyyyayyyyyyyayyyyyyyyyyyyayyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyaayayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayyyyyayyyayyyyyyyyyyyyyyyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyayayyyyyyyyyyyyyyayyyyayayyyyyyyyyyyyyyyayyayyyyyyyyyyyyayyyyyyyyayyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyyayyyaayayyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyayyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyy"},
    {"model": "base", "rule": "seq3", "config": "sequential vote: stop when two agree, at most 3 samples", "right": 442.1666666666667, "tokens": 9977.744666666666, "ran_out": 0, "gap": [-3.566666666666663, -5.1, -2.0], "multiple": 2.13, "rl_lead": [5.65, 4.0, 7.4],
     "grid": "yyyyyyyyyaygyyyyyyaymsyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyysyyymyyyyyygyyyyyyyyeyyyyyyyyysyyymyayyymayagyyyyyayyyyqyyyyyyyyyysyqyyyyyyyyyqyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyysyyyymyyyyyyyyyyyyyyasyyyyayyyayyqymyyqyyyyygyyyeyyyyyyaayqyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyiyayyyyyyyyayyyyyayiyyayayyyyyyyyyyyyyyyayygyyyyqsyyyyyyayyyyyyyyayymyyyyyygyyyyyyyyyayyyyyyyyyyygyyyeyyyyyyayyymyyyasyeyyyyyyyyyyyyyyyyyyayyayyyyyyqyyyyyyyyyyyiyyyyyyyyyyyyyqyayyyyygyyyyyqqysyyyyysyyyyyyyyqgyysyysyy"},
    {"model": "base", "rule": "seq4", "config": "sequential vote: stop when two agree, at most 4 samples", "right": 448.25, "tokens": 11256.234166666665, "ran_out": 0, "gap": [-2.35, -4.0, -0.7], "multiple": 2.4, "rl_lead": [5.216666666666662, 3.4, 7.2],
     "grid": "yyyyyyyyyaygyyyyyyaymyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyymyyyyyygyyyyyyyyayyyyyyyyyyyyymyayyymayagyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyyyyyyymyyyyyyyyyyyyyyayyyyyayyyayyyymyyyyyyyygyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyiyayyyyyyyyayyyyyayiyyayayyyyyyyyyyyyyyyayygyyyyyyyyyyyyayyyyyyyyayymyyyyyygyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyymyyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyyiyyyyyyyyyyyyyyyayyyyygyyyyyyyyyyyyyyyyyyyyyyyygyyyyyyyy"},
    {"model": "base", "rule": "seq4_short", "config": "sequential vote, at most 4, ties to the shortest finished sample", "right": 452.0, "tokens": 11256.234166666665, "ran_out": 0, "gap": [-1.6, -3.3, 0.2], "multiple": 2.4, "rl_lead": [4.5, 2.6, 6.5],
     "grid": "yyyyyyyyyayyyyyyyyaymyyyyyayyyyyyyyyyyyayyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyymyayyyaayayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyayyyayyyymyyyyyyyyyyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyayayyyyyyyyayyyyyayyyyayayyyyyyyyyyyyyyyayyayyyyyyyyyyyyayyyyyyyyayyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyymyyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyayyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyy"},
    {"model": "base", "rule": "seq_2then4", "config": "draw 2; if they differ draw 2 more; vote", "right": 448.25, "tokens": 11938.714333333333, "ran_out": 0, "gap": [-2.35, -4.0, -0.7], "multiple": 2.55, "rl_lead": [5.216666666666662, 3.4, 7.2],
     "grid": "yyyyyyyyyaygyyyyyyaymyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyymyyyyyygyyyyyyyyayyyyyyyyyyyyymyayyymayagyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyyyyyyymyyyyyyyyyyyyyyayyyyyayyyayyyymyyyyyyyygyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyiyayyyyyyyyayyyyyayiyyayayyyyyyyyyyyyyyyayygyyyyyyyyyyyyayyyyyyyyayymyyyyyygyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyymyyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyyiyyyyyyyyyyyyyyyayyyyygyyyyyyyyyyyyyyyyyyyyyyyygyyyyyyyy"},
    {"model": "base", "rule": "seq_2then4_short", "config": "draw 2; if they differ draw 2 more; vote, ties to the shortest", "right": 452.6666666666667, "tokens": 11938.714333333333, "ran_out": 0, "gap": [-1.4666666666666628, -3.2, 0.3], "multiple": 2.55, "rl_lead": [4.433333333333326, 2.5, 6.4],
     "grid": "yyyyyyyyyayyyyyyyyayuyyyyyayyyyyyyyyyyyayyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyuyayyyaayayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyayyyayyyyuyyyyyyyyyyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyayayyyyyyyyayyyyyayyyyayayyyyyyyyyyyyyyyayyayyyyyyyyyyyyayyyyyyyyayyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyyeyyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyayyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyy"},
    {"model": "base", "rule": "seq4_restart", "config": "sequential vote, at most 4, each sample restarted after a cap hit", "right": 452.0833333333333, "tokens": 14192.8195, "ran_out": 0, "gap": [-1.583333333333337, -3.2, 0.1], "multiple": 3.03, "rl_lead": [4.8, 3.1, 6.6],
     "grid": "yyyyyyyyyiygyyyyyyaymyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyyyyyyyyygyyyyyyyyayyyyyyyyyyyyymyayyyigyaiyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyayyyyyayyyayyyymyyyyyyyygyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyygyayyyyyyyyyyyyyygyyyyayayyyyyyyymyyyyyyayygyyyyyyyyyyyyayyyyyyyyayyyyyyyyygyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyymyyyamyayyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyiyyyyyyyyyyyyyyyayyyyygyyyyyymyyyyyyyyyyyyyyyyygyyyyyyyy"},
    {"model": "base", "rule": "seq4_restart_short", "config": "sequential vote, at most 4, restarts, ties to the shortest", "right": 453.0, "tokens": 14192.8195, "ran_out": 0, "gap": [-1.4, -3.1, 0.3], "multiple": 3.03, "rl_lead": [4.4, 2.7, 6.2],
     "grid": "yyyyyyyyyayyyyyyyyaymyyyyyayyyyyyyyyyyyayyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyymyayyyaayayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyayyyyyayyyayyyymyyyyyyyyyyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyayayyyyyyyyyyyyyyayyyyayayyyyyyyymyyyyyyayyayyyyyyyyyyyyayyyyyyyyayyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyymyyyamyayyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyayyyyyymyyyyyyyyyyyyyyyyyayyyyyyyy"},
    {"model": "base", "rule": "seq4_stop1000", "config": "sequential vote, at most 4; a finished answer of at most 1,000 tokens is accepted at once", "right": 441.6666666666667, "tokens": 10874.015, "ran_out": 0, "gap": [-3.666666666666663, -5.5, -1.9], "multiple": 2.32, "rl_lead": [6.466666666666662, 4.5, 8.5],
     "grid": "yyyyyyyyyaygyyyyyyayqyyyyyayyqyyyyyyyyyayyyayyyyssayyyyyyyyyyyyymyyyyyqgyyyyyyyyayyyyyyyyyqyyymyayyymayagyyyyyayyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyymyyymyyyyyyyymyyyyyyyymyyyyyayyyyyayyyayyyymyyyyyyysgyyyaymyyyyaayyyyyyyyyyyysyyyyyyyyyyayqyyyyyyyyyyyyayyyyiyayyyyyyyyayyyyyayiyyayayyyysyyyyyyyyyyayygyyyyyyyyyyyyayyyyyyyyayymyyyyyygyyyyyyyyyayymyyyyyyyyayyyayyyyyyaoyymyyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyyiyyyyyyyyyyyyyyyayyyyygyyyyymyyyyyyyyyyyyyyyyyygyyyyyyyy"},
    {"model": "base", "rule": "seq4_stop2000", "config": "sequential vote, at most 4; a finished answer of at most 2,000 tokens is accepted at once", "right": 439.5, "tokens": 10384.203833333335, "ran_out": 0, "gap": [-4.1, -5.8, -2.4], "multiple": 2.22, "rl_lead": [6.9166666666666625, 5.0, 8.9],
     "grid": "yyyyyyyyyaygyyyyyyayuyyyyyayysyyyyyyyyymyyyaysyyssamyyyyyyyyyyyymyyyyysgyyyyyyyyayyyyyyyyyqyyymyayyymayagyyyyyayyyymyyyyyyyyyyyyqyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyymyyyoyyyyyyyymyyyyyysyoyyyyyayyyyyayyyayyyymyyyyyoysgyyyaymyyyyaayyyyyyyyyyyysyyyyyyyyyyaysyyyyyqqyyyyyayyyyiyayyyyyyyyayyyyyayiyyayayyyysyyyyyyyyyyayygyyyyyyyyyyyyayyyyyyyyayymyyyyyygyyyyyyyyyayymyyyyyymyayyyiyyyyyyasyymyyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyqyyysyiyyyyyyyyyyyyyyyayyyyygyyyysmyyyyyyyyyyyyyyyyyygyyyyyyyy"},
    {"model": "base", "rule": "seq4_L8000", "config": "sequential vote, at most 4, samples abandoned at 8,000 tokens", "right": 444.5833333333333, "tokens": 10441.353666666666, "ran_out": 76, "gap": [-3.083333333333337, -4.8, -1.4], "multiple": 2.23, "rl_lead": [4.483333333333338, 2.8, 6.3],
     "grid": "yyyyyyyyyaymyyysyyayyyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyysyyyyymyayyyaayayyyyyyayyyyyyyysyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaysyyyyyyyyyayayayyyyyyyyyyyyypyyyyyyyyyyyyyyyyyyyayyyyyayyyayyyymyyyyyyyyiyyyayyyyyyaaypyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyayayyyyyyyyayyyyyayyyyayayyyyyyyyyyyyyyyayygyyyymyyyyyyyayyyyyyyyayygyyyyyygyyyyyyyyyayyyyyyyyyyygyyyayyyyyyayyyayyyamyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyygsyyyyyyyyyyyyyyayyyyyayyyyyyyypyyyyygyyyyyyyyagyymyypyy"},
    {"model": "base", "rule": "seq4_L12000", "config": "sequential vote, at most 4, samples abandoned at 12,000 tokens", "right": 450.0416666666667, "tokens": 11001.995666666666, "ran_out": 36, "gap": [-1.991666666666663, -3.7, -0.3], "multiple": 2.35, "rl_lead": [4.5416666666666625, 2.8, 6.4],
     "grid": "yyyyyyyyyaygyyyyyyayyyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyymyyyyyygyyyyyyyyayyyyyyyyyyyyyyyayyymayamyyyyyayyyyyyyysyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyayyyayyyyyyyyyyyyyiyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyiyayyyyyyyyayyyyyayyyyayayyyyyyyyyyyyyyyayyayyyyyyyyyyyyayyyyyyyyayygyyyyyygyyyyyyyyyayyyyyyyyyyyjyyyayyyyyyayyymyyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyygyyyyyyyyyyyyyyyayyyyygyyyyyyyyyyyyyygyyyyyyyyygyyyyyyyy"},
    {"model": "base", "rule": "par4_m2", "config": "4 in parallel, all stop when two finished answers agree", "right": 448.25, "tokens": 13402.18, "ran_out": 0, "gap": [-2.35, -4.1, -0.7], "multiple": 2.86, "rl_lead": [5.116666666666663, 3.2, 7.1],
     "grid": "yyyyyyyyyaygyyyyyyayyyyyyyayyyyyyyyyyyygyyyayyyyyyayyyyyyyyyyyyymyyyyyygyyyyyyyyayyyyyyyyyyyyyyyayyymayagyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayayyyyyyyyyyyyyyyyyymyyyyyyyyyyyyyyayyyyyayyyayyyyayyyyyyyygyyyayyyyyyaayyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyayyyyiyayyyyyyyyayyyyyayiyyayayyyyyyyyyyyyyyyayygyyyyyyyyyyyyayyyyyyyyayymyyyyyygyyyyyyyyyayyyyyyyyyyyayyyayyyyyyayyyayyyayyayyyyyyyyyyyyyyyyyyayyayyyyyyyyyyyyyyyyyyiyyyyyyyyyyyyyyyayyyyygyyyyyyyyyyyyyyyyyyyyyyyygyyyyyyyy"},
    {"model": "rl", "rule": "single", "config": "one sample", "right": 460.0, "tokens": 4686.79, "ran_out": 0,
     "grid": "yyyyyyyyygymyyyyyymyyyyysymyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyysysyyyyyyyyyyymyayyymmyayyyyyygyyyyyyyysyyyyyygysyyyyyyysyyyyyyyyyysyyysyyaysyyyyyyyyygyayyyyyyyysyyyyyysyyyysyyyyyyyyyyyyyyayyyyysyysmyymymsysyyyyysyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyysyysyyyyyygyayyyyyyyymyyyyysysyymyasyyyyyyyyyyyyyyayyyyyyyysyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayysyyyyyyyysyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayymyyyyyymyyyysyyyyyyayyyyyyyyyyyyyyyayyyyysyyyyyymyyyysyyysyyssyyyyyyymyyyyy"},
    {"model": "rl", "rule": "restart", "config": "one sample, sampled again after a cap hit (up to 2 times)", "right": 463.0, "tokens": 4965.9475, "ran_out": 0,
     "grid": "yyyyyyyyygymyyyyyymyyyyysysyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyysyyyyyyyyyyymygyyymsyayyyyyygyyyyyyyysyyyyyymysyyyyyyyyyyyyyyyyyysyyyyyyaysyyyyyyyyygyayyyyyyyysyyyyyysyyyysyyyyyyyyyyyyyyayyyyysyysmyymymsysyyyyysyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyysyysyyyyyygyayyyyyyyysyyyyysysyymyasyyyyyyyyyyyyyyayyyyyyyysyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayysyyyyyyyysyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyysyyyysyyyyyyayyyyyyyyyyyyyyyayyyyysyyyyyymyyyysyyysyyssyyyyyyysyyyyy"},
    {"model": "rl", "rule": "R8000", "config": "one sample, abandoned at 8,000 tokens and drawn again", "right": 464.1666666666667, "tokens": 7681.68, "ran_out": 50,
     "grid": "yyyyyyyyygyayyyyyymyyyyysymyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyysyyyyyyyyyyyyymyayyymmyayyyyyygyyyyyyyysyyyyyyyyyyyyyyyysyyyyyyyyyyqyyyyyyaymyyyyyyyyygyayyyyyyyyyyyyyyymyyyysyyyyyyyyyyyyyyayyyyyyyyymyymymsysyyyyysyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyysyyyyyyyyayyyyyyyymyyyyyyyyyymyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyayyayyyyyyyyyyyyyyyyayyyyyyyyyyysyyyyyyyyyygyyyyyyyayyiyyyyyyyyyyyyyyyyyyayymyyyyyyyyyyysyyyyyyayyyyyyyyyyyyyyyayyyyyqyyyyyyyyyyysyyysyyysyyyyyyymyyyyy"},
    {"model": "rl", "rule": "R12000", "config": "one sample, abandoned at 12,000 tokens and drawn again", "right": 466.1666666666667, "tokens": 6224.895666666667, "ran_out": 12,
     "grid": "yyyyyyyyygymyyyyyyiyyyyysyyyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyymyayyyymyayyyyyygyyyyyyyyqyyyyyyyysyyyyyyyyyyyyyyyyyysyyyyyyaysyyyyyyyyyayayyyyyyyysyyyyyysyyyyyyyyyyyyyyyyyyyayyyyyyyyymyyyymsyyyyyyysyyyyyyyyyyaayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyysyysyyyyyygyayyyyyyyyyyyyyysyqyyqyasyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyiyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayymyyyyyyyyyyysyyyyyyayyyyyyyyyyyyyyyayyyyysyyyyyyyyyyysyyysyysmyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "vote2", "config": "vote over 2", "right": 461.0833333333333, "tokens": 9373.58, "ran_out": 0,
     "grid": "yyyyyyyyygymyyyyyymyyyyysymyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyysyyyyyyyyyyymyayyymmyayyyyyyiyyyyyyyysyyyyyygysyyyyyyysyyyyyyyyyysyyyyyyaysyyyyyyyyygyayyyyyyyysyyyyyysyyyysyyyyyyyyyyyyyyayyyyysyysmyymymsysyyyyysyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyysyysyyyyyygyayyyyyyyyqyyyyysysyymyasyyyyyyyyyyyyyyayyyyyyyysyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayysyyyyyyyysyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayymyyyyyyqyyyysyyyyyyayyyyyyyyyyyyyyyayyyyysyyyyyymyyyysyyysyyssyyyyyyyqyyyyy"},
    {"model": "rl", "rule": "vote3", "config": "vote over 3", "right": 470.4166666666667, "tokens": 14060.37, "ran_out": 0,
     "grid": "yyyyyyyyyeyqyyyyyyqyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyqyayyyqqyayyyyyyiyyyyyyyyyyyyyyyeyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyeyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyqyyqyqyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyysyyyyyyyyyyqyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyqyyyyyysyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyqyyyyyyyyyyyyyyyyyyyysyyyyy"},
    {"model": "rl", "rule": "vote4", "config": "vote over 4", "right": 474.3333333333333, "tokens": 18747.16, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyiyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "vote2_short", "config": "vote over 2, ties to the shortest finished sample", "right": 468.0, "tokens": 9373.58, "ran_out": 0,
     "grid": "yyyyyyyyyiymyyyyyyiyyyyymyuyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyymyayyyuqyayyyyyymyyyyyyyyqyyyyyymyyyyyyyyyyyyyyyyyyyyqyyyyyyayqyyyyyyyyyeyayyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyayyyyyyyyyqyyqyuyyyyyyyyyyyyyyyyyyyaayeyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyqyyyyyymyayyyyyyyyuyyyyyyyuyyuyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyiyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyayymyyyyyyyyyyyyyyyyyyayyqyyyyyyuyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyymyyyyyyuyyyyqyyyyyyyqyyyyyyyuyyyyy"},
    {"model": "rl", "rule": "vote3_short", "config": "vote over 3, ties to the shortest finished sample", "right": 472.6666666666667, "tokens": 14060.37, "ran_out": 0,
     "grid": "yyyyyyyyygymyyyyyymyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyymyayyyyuyayyyyyysyyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyysyysyyyyyyyyyyyyyyyyyyyyyaayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyayymyyyyyyyyyyyyyyyyyyayyuyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "vote4_short", "config": "vote over 4, ties to the shortest finished sample", "right": 475.0, "tokens": 18747.16, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyayyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "vote4_restart", "config": "vote over 4 after restart", "right": 476.0833333333333, "tokens": 19863.79, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyygyyyyyyayyyyyyiyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "vote4_restart_short", "config": "vote over 4 after restart, ties to the shortest", "right": 475.0, "tokens": 19863.79, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyayyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq3", "config": "sequential vote: stop when two agree, at most 3 samples", "right": 470.4166666666667, "tokens": 10495.383666666667, "ran_out": 0,
     "grid": "yyyyyyyyyeyqyyyyyyqyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyqyayyyqqyayyyyyyiyyyyyyyyyyyyyyyeyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyeyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyqyyqyqyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyysyyyyyyyyyyqyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyqyyyyyysyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyqyyyyyyyyyyyyyyyyyyyysyyyyy"},
    {"model": "rl", "rule": "seq4", "config": "sequential vote: stop when two agree, at most 4 samples", "right": 474.3333333333333, "tokens": 11079.546666666665, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyiyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq4_short", "config": "sequential vote, at most 4, ties to the shortest finished sample", "right": 474.5, "tokens": 11079.546666666665, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq_2then4", "config": "draw 2; if they differ draw 2 more; vote", "right": 474.3333333333333, "tokens": 11617.187333333333, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyiyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq_2then4_short", "config": "draw 2; if they differ draw 2 more; vote, ties to the shortest", "right": 474.8333333333333, "tokens": 11617.187333333333, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyyuyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyeyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyayyuyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq4_restart", "config": "sequential vote, at most 4, each sample restarted after a cap hit", "right": 476.0833333333333, "tokens": 11770.929, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyygyyyyyyayyyyyyiyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq4_restart_short", "config": "sequential vote, at most 4, restarts, ties to the shortest", "right": 475.0, "tokens": 11770.929, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyayyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq4_stop1000", "config": "sequential vote, at most 4; a finished answer of at most 1,000 tokens is accepted at once", "right": 474.0, "tokens": 11018.1085, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyiyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyqyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq4_stop2000", "config": "sequential vote, at most 4; a finished answer of at most 2,000 tokens is accepted at once", "right": 474.0833333333333, "tokens": 10620.402166666667, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyiyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyysyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyymyyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "seq4_L8000", "config": "sequential vote, at most 4, samples abandoned at 8,000 tokens", "right": 467.0, "tokens": 11646.833333333334, "ran_out": 67,
     "grid": "yyyyyyyyygyayyyyyymyyyyyyymyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyysyyyyyyyyyyyyymyayyymmyayyyyyygyyyyyyyysyyyyyyyyyyyyyyyysyyyyyyyyyyyyyyyyyaysyyyyyyyyygyayyyyyyyyyyyyyyysyyyysyyyyyyyyyyyyyyayyyyyyyyyyyymymyysyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyymyyyyyyyyyymyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyayyayyyyyyyyyyyyyyyyayyyyyyyyyyysyyyyyyyyyygyyyyyyyayyayyyyyyyyyyyyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyysyyyyyyysyyyyyyymyyyyy"},
    {"model": "rl", "rule": "seq4_L12000", "config": "sequential vote, at most 4, samples abandoned at 12,000 tokens", "right": 472.75, "tokens": 11426.751166666667, "ran_out": 26,
     "grid": "yyyyyyyyygypyyyyyymyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyypyayyyymyayyyyyygyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyayyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayymyyyyyyyyyyyyyyyyyyayymyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyysyyyyyyyyyyyyy"},
    {"model": "rl", "rule": "par4_m2", "config": "4 in parallel, all stop when two finished answers agree", "right": 473.8333333333333, "tokens": 16552.826, "ran_out": 0,
     "grid": "yyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyayyyyyyiyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyaaygyyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyayayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyayyayyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyygyyyyyyyayyayyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyayyyyyyyyyyyyyyyayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"},
    ],
    # examples.json: base.stops_at_2_wrong and rl.stops_at_2_wrong. samples: [extracted_v3, n_new, score_v3] of the four
    # stored samples; tails: [sample, the end of text_last_2000]. question: the problem sentence of the prompt.
    "examples": {
        "base": {"problem": 20, "question": "Evaluate $(1+2i)6-3i$.", "gold": "6+9i", "samples": [["117 + 41i", 2762, 0], ["117 + 41i", 12838, 0], ["6 + 9i", 413, 1], ["6 + 9i", 1873, 1]], "tails": [[0, "Subtracting \\(3i\\) from this result:\n\n\\[\n(117 + 44i) - 3i = 117 + (44 - 3)i = 117 + 41i\n\\]\n\nThe value of \\((1 + 2i)^6 - 3i\\) is \\(\\boxed{117 + 41i}\\)."], [2, "Multiply (1 + 2i) by 6: 6*1 is 6, 6*2i is 12i. Then subtract 3i, which is 6 + 12i - 3i. 12i - 3i is 9i. So the final result is 6 + 9i. Yep, that's correct.\n\n**Answer:** 6 + 9i"]]},
        "rl": {"problem": 369, "question": "What is the number of square centimeters in the area of this trapezoid?", "gold": "21", "figure": True, "samples": [["189", 10015, 0], ["189", 10382, 0], ["189", 11123, 0], ["189", 12576, 0]], "tails": [[0, "Finally, divide by 2:\n   \\[\n   \\frac{378}{2} = 189\n   \\]\n\nThus, the area of the trapezoid is \\(\\boxed{189}\\)."]]},
    },
    # The 5-fold choice per budget (readout.json models.<model>.selection, held_out_right_24) for the budgets of 12,500 and up.
    "held_out": {"base": [452.0, 450.3333333333333, 450.5, 450.0], "rl": [474.3333333333333, 474.3333333333333, 474.3333333333333, 474.3333333333333]},
}

# A short plain name for each rule, for the picture; the full description is the rule's config.
NAMES = {
    "single": "One sample",
    "restart": "One sample, redrawn if cut off at 16,384 tokens",
    "R8000": "One sample, redrawn if longer than 8,000 tokens",
    "R12000": "One sample, redrawn if longer than 12,000 tokens",
    "vote2": "Vote over 2", "vote3": "Vote over 3", "vote4": "Vote over 4",
    "vote2_short": "Vote over 2, ties to the shortest",
    "vote3_short": "Vote over 3, ties to the shortest",
    "vote4_short": "Vote over 4, ties to the shortest",
    "vote4_restart": "Vote over 4, cut-off samples redrawn",
    "vote4_restart_short": "Vote over 4, cut-off samples redrawn, ties to the shortest",
    "seq3": "Stop when two agree, at most 3",
    "seq4": "Stop when two agree, at most 4",
    "seq4_short": "Stop when two agree, at most 4, ties to the shortest",
    "seq_2then4": "Draw 2, then 2 more if they differ",
    "seq_2then4_short": "Draw 2, then 2 more if they differ, ties to the shortest",
    "seq4_restart": "Stop when two agree, at most 4, with redraws",
    "seq4_restart_short": "Stop when two agree, with redraws, ties to the shortest",
    "seq4_stop1000": "Stop when two agree, or at an answer under 1,000 tokens",
    "seq4_stop2000": "Stop when two agree, or at an answer under 2,000 tokens",
    "seq4_L8000": "Stop when two agree, samples cut at 8,000 tokens",
    "seq4_L12000": "Stop when two agree, samples cut at 12,000 tokens",
    "par4_m2": "4 in parallel, stop when two agree",
}

_R = {(r["model"], r["rule"]): r for r in DATA["rules"]}
_base = [r for r in DATA["rules"] if r["model"] == "base"]
_best = max(_base, key=lambda r: (r["right"], -r["tokens"]))  # the best base rule at any budget
_plain = max((r for r in _base if not r["rule"].endswith("_short")), key=lambda r: (r["right"], -r["tokens"]))
_lead = min((r for r in _base), key=lambda r: r["rl_lead"][0])  # the smallest lead of RL under the same rule
_rl1 = DATA["rl_single"]
_rlmax = max((r for r in DATA["rules"] if r["model"] == "rl"), key=lambda r: r["right"])
_k = lambda v: f"{round(v):,}"
_p = lambda v: f"{v:+.1f}".replace("-", "\u2212")
_ci = lambda c: f"(95 % interval {c[1]:.1f} to {c[2]:.1f})".replace("-", "\u2212")
_seq = _R[("base", "seq4")], _R[("base", "vote4")], _R[("rl", "seq4")], _R[("rl", "vote4")]
_save = lambda a, b: round(100 * (1 - a["tokens"] / b["tokens"]))  # per cent of the tokens the sequential vote saves

TITLE = "More samples against RL"  # the name on its tile on /findings and in the browser tab
PROBLEM = ("Can drawing more samples from the base model with the opening cue match one sample of the model trained by "
           "reinforcement learning (RL)?")
LINE = (f"On MATH-500, the best rule for drawing several samples of the base model and picking one answer uses "
        f"{_best['multiple']:.1f} times the tokens of one RL sample and still scores {abs(_best['gap'][0]):.1f} percentage "
        "points lower.")

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
# Not from our runs: Aggarwal et al., Adaptive-Consistency (arXiv 2305.11860), abstract: up to 7.9 times fewer samples at
# under 0.1 % average accuracy drop; Li et al., Early-Stopping Self-Consistency (arXiv 2401.10480); Yue et al. (arXiv
# 2504.13837), Figure 1: the base model's pass@256 exceeds its RL version's.
PANELS = [
    ["new", "What is new",
     "New here is the base model against RL, the same model after reward training, at equal tokens. Stopping a vote once "
     "samples agree is published: Adaptive-Consistency (arXiv 2305.11860) reports up to 7.9 times fewer samples at under "
     "0.1 % accuracy drop.",
     [f"In these samples, stopping the vote once two samples agree gives the score of a vote over 4 with {_save(_seq[0], _seq[1])} % fewer tokens for the base "
      f"and {_save(_seq[2], _seq[3])} % fewer for RL.",
      "Yue et al. (arXiv 2504.13837, Figure 1) report that RL training lowers pass@256, the share of problems solved by at least "
      "one of 256 samples checked against the answer key. Every rule here picks its answer without the key.",
      f"Under each of the 24 rules the RL model stays ahead of the base model using the same rule; the smallest lead is {_lead['rl_lead'][0]:.1f} points "
      f"{_ci(_lead['rl_lead'])}."]],
    ["why", "Why it matters",
     "The team's research goal is the cheapest way, with no reward training, to reach RL's score at equal tokens. On "
     "MATH-500, drawing more samples is not that way.",
     [f"One RL sample costs {_k(_rl1['tokens'])} tokens per problem. The best base rule spends {_k(_best['tokens'])} and is "
      f"still {abs(_best['gap'][0]):.1f} points below.",
      f"Above 12,500 tokens per problem the base model gains nothing: when the best rule at each budget is chosen on four "
      f"fifths of the problems and scored on the remaining fifth, it stays at {min(DATA['held_out']['base']):.1f} to {max(DATA['held_out']['base']):.1f} of 500.",
      f"The same rules lift RL too, from {_rl1['right']:.1f} to {_rlmax['right']:.1f} of 500, so extra samples do not "
      "close the gap."]],
    ["how", "How we know",
     "Before scoring any, we wrote into a plan 24 rules for drawing samples and picking one answer (single samples with "
     "redraws, votes, and votes that stop early). We then applied them to four stored samples per problem from each "
     "model: MATH-500, 500 problems, temperature 1.0, scored by the grader (version 3).",
     ["A rule sees only each sample's length, whether it was cut off at 16,384 tokens, and its extracted answer. Code that "
      "reads the score or the answer key raises an error.",
      "Tokens count every token of every sample a rule draws. Scores and tokens are means over all 24 orders (4 × 3 × 2 × 1) in which the "
      "four samples can be drawn.",
      "Intervals come from a paired bootstrap over problems, 5,000 resamples."]],
    ["limits", "What it does not show",
     "The best base rules break vote ties toward the shortest finished sample, a tie rule written after reading the "
     "problems it fixes, so they are optimistic. They are drawn as rings.",
     [f"Without that tie rule, the best base rule is {abs(_plain['gap'][0]):.1f} points below one RL sample "
      f"{_ci(_plain['gap'])}, at {_plain['multiple']:.1f} times its tokens.",
      "For the best base rules the interval includes 0, so a tie with one RL sample is not excluded. A tie with RL given "
      "the same rule is excluded.",
      f"Every rule here draws from 4 stored samples per problem. With 12 samples, a vote over 6 samples of Base + cue "
      f"reaches RL's one-sample range, {_vote.K[6][1]} of 500, at {_vote.times(_vote.K[6][7]):.1f} times the tokens "
      "([Vote over 6 samples](/finding/vote-over-four)). The 328 harder problems are not on this chart yet. Rules that cut long samples ran out of stored samples on some "
      "problems, so their results are approximate."]],
    ["run", "How to reproduce it",
     "studies/rlneurons/analysis/frontier.py replays the rules on the stored rows; the command is in studies/rlneurons/README.md, "
     "section Token frontier.",
     [f"The samples come from jobs {DATA['jobs']['base']} (Base + cue) and {DATA['jobs']['rl']} (RL) at commit "
      f"{DATA['source_commit']}; the frontier ran at commit {DATA['commit']}.",
      "The picture's numbers are in " + RUN + " (frontier.json, readout.json, per_problem.json, examples.json)."]],
]

# The icon of this finding's tile on /findings (tools/findings.py says how it is called): the page's own picture,
# reduced. A glass slab with a lit level line near the back (one RL sample) and a staircase of dots that rises toward it
# and flattens just below. A faint budget line sweeps slowly across, and the dots behind it are lit.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, w = th / 2;
  const pts = [[-.78, .62], [-.6, .36], [-.42, .22], [-.18, -.06], [.06, -.2], [.32, -.27], [.58, -.3], [.78, -.32]];
  const sweep = -.9 + 1.8 * (.5 - .5 * Math.cos((Number(t) || 0) * .35));
  let out = kit.slab(a, b, th);
  out += kit.line(kit.at(-a * .86, -b * .5, w), kit.at(a * .86, -b * .5, w), 1.1, "lit");
  out += kit.line(kit.at(a * sweep, -b * .72, w), kit.at(a * sweep, b * .76, w), .6, "plain", .7);
  for (const [u, v] of pts) {
    const p = kit.at(a * u, b * v, w), on = u <= sweep;
    out += `<ellipse cx="${p[0].toFixed(2)}" cy="${p[1].toFixed(2)}" rx="${(2.3 * p[2]).toFixed(2)}" ry="${(1.6 * p[2]).toFixed(2)}" fill="${kit.token.ink}" opacity="${on ? .9 : .28}"/>`;
  }
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
   with a cast shadow in place of the glow. The light comes from the upper left in both. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #c41e34;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1;
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
  gap: 0; min-height: max(100vh, 620px); max-width: 1840px; margin: 0 auto; padding: 20px 40px 28px;
}
.top { grid-column: 1 / -1; display: flex; align-items: center; gap: 26px; font-size: 13px; padding-bottom: 16px; border-bottom: 1px solid var(--rule); }
.name { font-weight: 740; font-stretch: 122%; font-size: 15px; letter-spacing: .02em; margin: 0 6px 0 0; }
.top a { color: var(--mute); text-decoration: none; white-space: nowrap; transition: color .15s ease; }
.top a:hover { color: var(--ink); }
.top a[aria-current] { color: var(--ink); font-weight: 600; }

/* The picture: one plate holding the chart, the readout and the strip of problems */
/* The words can be taller than the window: then the page scrolls as a whole, and the picture, which keeps the
   height of the window under the header, stays in view. */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; position: sticky; top: 0; align-self: start; height: calc(max(100vh, 620px) - 87.5px); }
svg { width: 100%; max-height: calc(100vh - 120px); display: block; overflow: visible; touch-action: pan-y; user-select: none; -webkit-user-select: none; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
svg * { pointer-events: none; }
svg .hit { pointer-events: all; fill: transparent; stroke: none; cursor: pointer; outline: none; }
svg .hit:focus-visible { stroke: var(--blue); stroke-width: 2; }
svg .grab { pointer-events: all; fill: transparent; cursor: ew-resize; }
.atmo { opacity: var(--glow); }
.shade { fill: var(--ink); opacity: calc(var(--shadow) * .17); }
.spec { opacity: var(--spec); }
.back { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; }
.plate { fill: url(#body) var(--sheet); stroke: url(#rim) var(--ink); stroke-width: 1.7; }
.grid { stroke: var(--ink); stroke-width: 1; opacity: .08; fill: none; }
.axis { stroke: var(--ink); stroke-width: 1.2; opacity: .45; fill: none; }
.tick { fill: var(--mute); font-weight: 500; }
.atitle { fill: var(--mute); font-weight: 560; }
.spent { fill: var(--blue); opacity: calc(.035 + var(--glow) * .03); }
.stair { fill: none; stroke-linejoin: round; stroke-linecap: round; }
.stair.b0 { stroke: var(--ink); stroke-width: 1.2; opacity: .16; }
.stair.b1 { stroke: var(--ink); stroke-width: 2.2; opacity: .75; }
.stair.r0 { stroke: var(--blue); stroke-width: 1.2; opacity: .2; }
.stair.r1 { stroke: var(--blue); stroke-width: 1.8; opacity: .5; }
.level { stroke: var(--blue); stroke-width: 1.6; stroke-dasharray: 5 6; fill: none; }
.lvl { fill: var(--blue); font-weight: 620; }
.mk.base { fill: var(--ink); }
.mk.rl { fill: var(--blue); }
.mk.ring { fill: var(--sheet); stroke-width: 2.2; }
.mk.base.ring { stroke: var(--ink); }
.mk.rl.ring { stroke: var(--blue); }
.halo { fill: var(--blue); opacity: calc(var(--bloom) * .2); }
.focus { fill: none; stroke: var(--ink); stroke-width: 1.6; }
.focus.rl { stroke: var(--blue); }
.bar { stroke: var(--ink); stroke-width: 1.6; opacity: .55; fill: none; stroke-linecap: round; }
.budget { stroke: var(--ink); stroke-width: 1.2; opacity: .55; }
.knob { fill: var(--ink); }
.knob-ring { fill: none; stroke: var(--ink); stroke-width: 1.2; opacity: .35; }
.knob-ring.on { stroke: var(--blue); stroke-width: 2.4; opacity: 1; }
.blab { fill: var(--ink); font-weight: 640; }
.bhint { fill: var(--mute); font-weight: 500; }
.big { fill: var(--ink); font-weight: 660; letter-spacing: -.035em; font-stretch: 100%; }
.unit { fill: var(--ink); font-weight: 480; }
.ci, .cap, .score { fill: var(--mute); font-weight: 500; }
.rname { fill: var(--ink); font-weight: 640; }
.cell { fill: none; stroke: var(--ink); stroke-linecap: round; }
.exring { fill: none; stroke: var(--blue); stroke-width: 1.6; }
.slab-t { fill: var(--mute); font-weight: 520; }
.klab { fill: var(--mute); font-weight: 520; }
.sr { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }

/* One drawn entrance, then only the slow sway and what the reader moves */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .back { animation: fade 1.3s .15s both; }
.enter .chart { animation: fade .7s .6s both; }
.enter .marks, .enter .read, .enter .strip, .enter .key { animation: fade .7s .85s both; }

/* The words */
.side {
  min-width: 0;
  padding: clamp(10px, 7vh - 38px, 58px) 0 0 40px; border-left: 1px solid var(--rule);
}
a.back { display: inline-block; font-size: 13px; color: var(--mute); padding: 10px 0; margin: -10px 0 6px; }
a.back:hover { color: var(--ink); }
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
.close { font-size: 13px; color: var(--mute); flex: none; }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; overflow-wrap: anywhere; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.ex { margin: 26px 0 0; font-size: 14px; font-weight: 660; font-stretch: 114%; color: var(--ink); padding-bottom: 8px; border-bottom: 1px solid var(--ink); }
.q { margin: 12px 0 0; font-size: 16px; line-height: 1.4; max-width: 36ch; }
.q span { color: var(--mute); }
.q .qt { color: var(--ink); }
.q b { color: var(--ink); font-weight: 600; }
.samples { list-style: none; margin: 12px 0 0; padding: 0; font-size: 14px; max-width: 40ch; }
.samples li { display: grid; grid-template-columns: 1fr auto 4.2em; gap: 12px; padding: 5px 0; border-top: 1px solid var(--rule); color: var(--mute); }
.samples li b { color: var(--ink); font-weight: 600; }
.samples li .ok { color: var(--blue); font-weight: 600; }
.verdict { margin: 12px 0 0; font-size: 14.5px; max-width: 40ch; }
.tail { margin: 12px 0 0; padding: 0 0 0 12px; border-left: 2px solid var(--rule); font-size: 13px; line-height: 1.45; color: var(--mute); white-space: pre-wrap; overflow-wrap: anywhere; max-width: 44ch; }
.tail span { display: block; color: var(--ink); font-weight: 600; margin-bottom: 2px; white-space: normal; }
.tail .tt { display: inline; color: var(--mute); font-weight: 400; white-space: pre-wrap; }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  a.back { order: 0; align-self: flex-start; margin-top: 14px; }
  .problem { order: 1; margin-top: 0; max-width: none; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; position: relative; height: auto; align-self: stretch; display: block; }
  .pane { order: 4; margin-top: 22px; }
  svg { max-height: none; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .more button, .top a { transition: none; }
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
    <input class="sr" id="budget" type="range" step="100" aria-label="Token budget per problem">
    <svg id="svg" role="group"></svg>
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
const RAD = Math.PI / 180, f = n => n.toFixed(1), mix = (a, b, q) => a + (b - a) * q;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v)), ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;
const num = v => Math.round(v).toLocaleString("en-US"), one = v => v.toFixed(1);
const sgn = v => (v > 0.04 ? "+" : v < -0.04 ? "\u2212" : "") + Math.abs(v).toFixed(1);

/* The data: one mark per model and rule. g is the rule's score on each problem, as a share of the 24 draw orders. */
const N = D.n, RL1 = D.rl_single;
const R = D.rules.map((r, i) => ({ ...r, i, key: r.model + "-" + r.rule, short: r.rule.endsWith("_short"), name: C.names[r.rule],
  g: [...r.grid].map(c => (c.charCodeAt(0) - 97) / 24), v: 0, tgt: 0, at: 0 }));
const BASE = R.filter(r => r.model === "base"), RLS = R.filter(r => r.model === "rl");
const ONE = RLS.find(r => r.rule === "single");
/* The strip's order: easiest first, by the mean score of all 48 rows on each problem. PLACE[i] is problem i's place. */
const EASY = Array.from({ length: N }, (_, i) => i).map(i => [i, R.reduce((a, r) => a + r.g[i], 0)]).sort((a, b) => b[1] - a[1] || a[0] - b[0]);
const PLACE = new Array(N); EASY.forEach(([i], p) => { PLACE[i] = p; });
const same = r => R.find(o => o.rule === r.rule && o.model !== r.model);
const B0 = 20000, SWEEP0 = 4700, BMIN = 4100, BMAX = 20000, XD = [3000, 20500], YD = [400, 480];
const best = (list, b) => list.reduce((o, r) => r.tokens <= b && (!o || r.right > o.right || (r.right === o.right && r.tokens < o.tokens)) ? r : o, null);
const S = { budget: B0, shown: B0, pick: null, open: null, focus: null, last: 0, t: 0, drag: false, g: null, el: {},
  nums: null, ring: null, strip: null, cells: new Array(N).fill(0), seen: false, sweep: null, rove: 0 };

/* Geometry: the plate faces the viewer, in a small 3D space around its centre (x right, y down, z toward the viewer).
   X, Y: the chart's left/right and top/bottom; rx, ry: the readout's left edge and its line baselines; wrap: characters
   per line of a rule name; sx, sy, sp, cols: the strip of problems; ky: the key; fs: label size. */
function geo() {
  return narrow.matches
    ? { w: 480, h: 1030, cx: 240, cy: 515, D: 2000, a: [6, 8, 474, 1022], r: 22, deep: 30, blur: 12,
        X: [82, 452], Y: [374, 660], fs: 17, fb: 84, rx: 34, ry: { big: 104, unit: 138, ci: 186, cap: 222, name: 246, lh: 23 }, wrap: 40,
        tick: 688, atitle: 714, ytitle: 348, sx: 36, sy: 786, sp: 8.3, rows: 10, slab: 762, cell: [2.2, 4.4], ky: [930, 962, 994], kx: [[36, 0], [36, 1], [36, 2]],
        mark: 7.2, hit: 17, near: 150 }
    : { w: 1000, h: 640, cx: 500, cy: 320, D: 2200, a: [20, 14, 980, 626], r: 30, deep: 40, blur: 16,
        X: [100, 672], Y: [74, 420], fs: 15, fb: 104, rx: 712, ry: { big: 186, unit: 218, ci: 264, cap: 306, name: 329, lh: 21 }, wrap: 27,
        tick: 444, atitle: 466, ytitle: 50, sx: 62, sy: 514, sp: 8.85, rows: 5, slab: 494, cell: [1.9, 3.9], ky: [598], kx: [[62, 0], [392, 0], [656, 0]],
        mark: 6.4, hit: 15, near: 66 };
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
function proj(g, x, y, z) {
  const X = x - g.cx, Y = y - g.cy, x1 = X * V.c1 + z * V.s1, z1 = z * V.c1 - X * V.s1;
  const y1 = Y * V.c2 - z1 * V.s2, k = g.D / (g.D - (z1 * V.c2 + Y * V.s2));
  return [g.cx + x1 * k, g.cy + y1 * k];
}
const px = (g, tok) => mix(g.X[0], g.X[1], (tok - XD[0]) / (XD[1] - XD[0]));
const py = (g, right) => mix(g.Y[1], g.Y[0], (right - YD[0]) / (YD[1] - YD[0]));
function slab(g, z) {
  const [x0, y0, x1, y1] = g.a, r = g.r, p = [];
  const corner = (cx, cy, a0) => { for (let i = 0; i <= 6; i++) p.push(proj(g, cx + r * Math.cos((a0 + 15 * i) * RAD), cy + r * Math.sin((a0 + 15 * i) * RAD), z)); };
  corner(x1 - r, y0 + r, -90); corner(x1 - r, y1 - r, 0); corner(x0 + r, y1 - r, 90); corner(x0 + r, y0 + r, 180);
  return "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
}
const line = (g, pts, z) => "M" + pts.map(([x, y]) => { const q = proj(g, x, y, z); return f(q[0]) + " " + f(q[1]); }).join("L");
function wrap(s, n) {  // a rule name in lines of at most n characters
  const out = [""];
  s.split(" ").forEach(w => { const l = out[out.length - 1]; if (l && (l + " " + w).length > n) out.push(w); else out[out.length - 1] = l ? l + " " + w : w; });
  return out;
}
/* The staircase of the best rule so far, from the cheapest rule up to tokens b, in chart coordinates. */
function stair(g, list, b) {
  const pts = [];
  let top = null;
  [...list].sort((p, q) => p.tokens - q.tokens).forEach(r => {
    if (r.tokens > b || (top && r.right <= top.right)) return;
    if (top) pts.push([px(g, r.tokens), py(g, top.right)]);
    pts.push([px(g, r.tokens), py(g, r.right)]);
    top = r;
  });
  if (top) pts.push([px(g, Math.min(b, XD[1])), py(g, top.right)]);
  return pts;
}

/* The picture, built once per layout; place() sets everything that depends on the view, the budget and the focus. */
function build() {
  const g = S.g = geo(), svg = $("svg"), [ax0, ay0, ax1, ay1] = g.a, aw = ax1 - ax0, ah = ay1 - ay0;
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const T = (id, cls, size, anchor, text) => `<text id="${id}" class="${cls}" font-size="${size}"${anchor ? ` text-anchor="${anchor}"` : ""}>${text || ""}</text>`;
  const yt = [410, 420, 430, 440, 450, 460, 470, 480], xt = [5000, 10000, 15000, 20000];
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".22" r=".95">${stop(0, "var(--glass-hi)")}${stop(.46, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1=".04" x2=".94" y2=".96">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.5, "var(--blue)", .2)}${stop(.72, "var(--blue)", .06)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<filter id="soft" x="-20%" y="-20%" width="140%" height="150%"><feGaussianBlur stdDeviation="${g.blur}"/></filter></defs>` +
    `<ellipse class="atmo" cx="${g.cx}" cy="${g.cy}" rx="${f(aw * .8)}" ry="${f(ah * .9)}" fill="url(#atmo)"/>` +
    `<rect class="shade" x="${f(ax0 + aw * .012)}" y="${f(ay0 + ah * .04)}" width="${aw}" height="${ah}" rx="${g.r}" filter="url(#soft)"/>` +
    `<path class="back" id="back"/><path class="plate draw" id="plate" pathLength="1"/>` +
    `<ellipse class="spec" cx="${f(ax0 + aw * .3)}" cy="${f(ay0 + ah * .26)}" rx="${f(aw * .28)}" ry="${f(ah * .2)}" transform="rotate(-16 ${f(ax0 + aw * .3)} ${f(ay0 + ah * .26)})" fill="url(#spec)"/>` +
    `<g class="chart"><path class="spent" id="spent"/><path class="grid" id="grid"/><path class="axis" id="axis"/>` +
    yt.map(v => T("yt" + v, "tick", g.fs, "end", v)).join("") + xt.map(v => T("xt" + v, "tick", g.fs, "middle", v.toLocaleString("en-US"))).join("") +
    T("ytitle", "atitle", g.fs, "", "MATH-500, temperature 1.0: right answers out of " + N) + T("xtitle", "atitle", g.fs, "end", "Tokens per problem") +
    `<path class="stair b0" id="sb0"/><path class="stair r0" id="sr0"/><path class="stair r1" id="sr1"/><path class="stair b1" id="sb1"/>` +
    `<path class="level" id="level"/>` + T("lvl", "lvl", g.fs, "", narrow.matches ? "One RL sample" : `One RL sample: ${one(RL1.right)} of ${N}`) + `</g>` +
    `<g class="marks"><line class="budget" id="budget-line"/><path class="bar" id="bar"/><circle class="halo" id="halo"/>` +
    R.map(r => `<circle class="mk ${r.model}${r.short ? " ring" : ""}" id="m${r.i}"/>`).join("") +
    `<circle class="focus" id="focus"/>` +
    `<circle class="knob-ring" id="knob-ring" r="${g.mark * 2.3}"/><circle class="knob" id="knob" r="${g.mark * 1.1}"/>` +
    T("blab", "blab", g.fs, "middle") + T("bhint", "bhint", g.fs) + `</g>` +
    `<g class="read">` + T("big", "big", g.fb) + T("unit", "unit", g.fs + 1, "", "points versus one RL sample") + T("unit2", "ci", g.fs) + T("ci", "ci", g.fs) +
    T("cap", "cap", g.fs) + [0, 1, 2].map(k => T("nm" + k, "rname", g.fs + 1)).join("") + T("score", "score", g.fs) + `</g>` +
    `<g class="strip">` + T("slab", "slab-t", g.fs, "", narrow.matches ? "The 500 problems, easiest first" : "The 500 problems, easiest first, lit where the ringed rule is right") +
    `<path class="level" id="stick"/>` + T("stlab", "lvl", g.fs, "end", `One RL sample: ${one(RL1.right)} of ${N}`) +
    Array.from({ length: 13 }, (_, k) => `<path class="cell" id="c${k}" stroke-width="${k ? g.cell[1] : g.cell[0]}" opacity="${k ? (.3 + .55 * k / 12).toFixed(2) : .28}"/>`).join("") +
    `<circle class="exring" id="exring" r="${g.sp * .9}"/></g>` +
    `<g class="key"><circle class="mk base" id="kd0" r="${g.mark * .8}"/>${T("kt0", "klab", g.fs, "", "Base + cue, no training: one dot per rule")}` +
    `<circle class="mk rl" id="kd1" r="${g.mark * .8}"/>${T("kt1", "klab", g.fs, "", "RL (reward training), same rules")}` +
    `<circle class="mk base ring" id="kd2" r="${g.mark * .72}"/>${T("kt2", "klab", g.fs, "", "Tie rule chosen after its misses")}</g>` +
    `<rect class="grab" id="grab"/><g class="rules" role="group" aria-label="The 48 rules. Arrow keys move between them, Enter opens one.">` +
    R.map(r => `<circle class="hit" id="h${r.i}" data-rule="${r.key}" tabindex="${r.i === S.rove ? 0 : -1}" role="button" aria-label="${esc((r.model === "base" ? "Base + cue: " : "RL: ") + r.name)}" r="${g.hit}"/>`).join("") + "</g>";
  S.el = {};
  svg.querySelectorAll("[id]").forEach(e => { S.el[e.id] = e; });
  S.shownText = {};
}

/* The rule the readout, the ring and the strip follow: the one the reader clicked, or the best base rule in budget. */
const focusOf = b => S.pick || best(BASE, b);
function readout(r) {  // the numbers of the readout for rule r, which count from one rule to the next
  if (r.model === "base") return [r.gap[0], r.gap[1], r.gap[2], r.right, r.tokens];
  const d = (r.right - RL1.right) / 5;
  return [d, d, d, r.right, r.tokens];
}
function refocus(now) {
  const r = focusOf(S.shown);
  if (r === S.focus) return;
  const was = S.focus;
  S.focus = r;
  if (!r) return;
  const from = S.nums ? S.nums.now : readout(r), to = readout(r);
  S.nums = { from, to, now: from, t0: now };
  const at = was ? (S.ring ? S.ring.now : [was.tokens, was.right]) : [r.tokens, r.right];
  S.ring = { from: at, to: [r.tokens, r.right], now: at, t0: now };
  S.strip = { from: S.cells.slice(), to: r.g, t0: now };
  if (still.matches || !was) { S.nums.t0 = S.ring.t0 = S.strip.t0 = -1e9; }
}

function place(now) {
  const g = S.g, E = S.el, z0 = 0;
  const at = (el, q) => { el.setAttribute("x", f(q[0])); el.setAttribute("y", f(q[1])); };
  const ctr = (el, q) => { el.setAttribute("cx", f(q[0])); el.setAttribute("cy", f(q[1])); };
  const text = (id, v) => { if (S.shownText[id] !== v) E[id].textContent = S.shownText[id] = v; };
  const P = (x, y, z) => proj(g, x, y, z || 0);
  E.back.setAttribute("d", slab(g, -g.deep));
  E.plate.setAttribute("d", slab(g, 0));
  const [X0, X1] = g.X, [Y0, Y1] = g.Y, b = S.shown, bx = px(g, b);

  // The chart: the spent region left of the budget, the grid, the axes and their labels.
  E.spent.setAttribute("d", line(g, [[X0, Y0], [bx, Y0], [bx, Y1], [X0, Y1]], z0) + "Z");
  let grid = "";
  [410, 420, 430, 440, 450, 460, 470, 480].forEach(v => { grid += line(g, [[X0, py(g, v)], [X1, py(g, v)]], z0); at(E["yt" + v], P(X0 - 12, py(g, v) + g.fs * .35)); });
  E.grid.setAttribute("d", grid);
  E.axis.setAttribute("d", line(g, [[X0, Y0 - 8], [X0, Y1], [X1, Y1]], z0));
  [5000, 10000, 15000, 20000].forEach(v => { at(E["xt" + v], P(px(g, v), g.tick)); E["xt" + v].setAttribute("opacity", Math.abs(px(g, v) - bx) < g.near ? 0 : 1); });
  at(E.ytitle, P(X0 - 2, g.ytitle - (narrow.matches ? 0 : 0)));
  at(E.xtitle, P(X1, g.atitle));

  // The frontier of each model up to the budget, faint beyond it; one RL sample as a level line.
  E.sb0.setAttribute("d", line(g, stair(g, BASE, XD[1]), 2));
  E.sb1.setAttribute("d", line(g, stair(g, BASE, b), 3));
  E.sr0.setAttribute("d", line(g, stair(g, RLS, XD[1]), 2));
  E.sr1.setAttribute("d", line(g, stair(g, RLS, b), 3));
  E.level.setAttribute("d", line(g, [[X0, py(g, RL1.right)], [X1, py(g, RL1.right)]], 4));
  // Where no mark is: on a wide plate under the line left of the base marks near 450, on a phone above it at the right.
  E.lvl.setAttribute("text-anchor", narrow.matches ? "end" : "start");
  at(E.lvl, narrow.matches ? P(px(g, 19300), py(g, RL1.right) - 7, 4) : P(px(g, 6000), py(g, RL1.right) + g.fs + 3, 4));

  // The marks: a rule within the budget is lit; one that leaves or enters it changes over about half a second.
  const k = still.matches ? 1 : 1 - Math.exp(-(now - (S.lastPlace || now)) / 110);
  S.lastPlace = now;
  R.forEach(r => {
    if (now >= r.at) r.v += (r.tgt - r.v) * k;
    const q = P(px(g, r.tokens), py(g, r.right), 6 + 6 * r.v), e = E["m" + r.i];
    ctr(e, q);
    e.setAttribute("r", f(g.mark * (r === ONE ? 1.3 : 1) * (.78 + .22 * r.v)));
    e.setAttribute("opacity", (.2 + .8 * r.v).toFixed(2));
    ctr(E["h" + r.i], q);
  });
  const q1 = P(px(g, ONE.tokens), py(g, ONE.right), 12);
  ctr(E.halo, q1);
  E.halo.setAttribute("r", f(g.mark * 2.6 * (still.matches ? 1 : 1 + .08 * Math.sin(S.t * .7))));

  // The budget: a line across the chart and a knob on the x axis.
  const bt = P(bx, Y0 - 6, 8), bb = P(bx, Y1, 8);
  E["budget-line"].setAttribute("x1", f(bt[0])); E["budget-line"].setAttribute("y1", f(bt[1]));
  E["budget-line"].setAttribute("x2", f(bb[0])); E["budget-line"].setAttribute("y2", f(bb[1]));
  ctr(E.knob, bb); ctr(E["knob-ring"], bb);
  E["knob-ring"].setAttribute("r", f(g.mark * (2.3 + (S.seen || still.matches ? 0 : .35 * Math.sin(S.t * 2.2)))));
  text("blab", `${num(b)} tokens`);
  at(E.blab, P(clamp(bx, X0 + 20, X1 - (narrow.matches ? 54 : 30)), g.tick, 8));
  const right = bx > (X0 + X1) / 2;  // the hint sits on the side of the line that has room
  text("bhint", right ? "Drag left to spend fewer tokens" : "Drag right to spend more tokens");
  E.bhint.setAttribute("text-anchor", right ? "end" : "start");
  at(E.bhint, P(bx + (right ? -18 : 18), Y1 - 12, 8));
  E.bhint.setAttribute("opacity", S.seen || S.sweep ? 0 : .9);

  // The focus: a ring that travels to the rule, the interval of its distance to one RL sample, and the readout.
  const r = S.focus, tw = (o, d) => { if (!o) return; const p = ease(clamp((now - o.t0) / d, 0, 1)); o.now = o.from.map((v, i) => mix(v, o.to[i], p)); };
  tw(S.ring, 650); tw(S.nums, 650);
  ["focus", "bar", "big", "unit", "unit2", "ci", "cap", "score", "nm0", "nm1", "nm2"].forEach(id => E[id].style.display = r ? "" : "none");
  if (r) {
    const [rt, rr] = S.ring.now, fq = P(px(g, rt), py(g, rr), 13);
    ctr(E.focus, fq);
    E.focus.setAttribute("r", f(g.mark * 2));
    E.focus.setAttribute("class", "focus" + (r.model === "rl" ? " rl" : ""));
    const [d, lo, hi, right, tok] = S.nums.now;
    if (r.model === "base") {
      const xb = px(g, rt), y1 = py(g, RL1.right + 5 * lo), y2 = py(g, RL1.right + 5 * hi), c = 5;
      E.bar.setAttribute("d", line(g, [[xb, y1], [xb, y2]], 10) + line(g, [[xb - c, y1], [xb + c, y1]], 10) + line(g, [[xb - c, y2], [xb + c, y2]], 10));
      E.bar.style.display = "";
    } else E.bar.style.display = "none";
    text("big", sgn(d));
    text("unit2", r.model === "base" ? `95 % interval ${sgn(lo)} to ${sgn(hi)}` : "An RL rule: no interval computed");
    text("ci", r.model === "base" && lo < 0 && hi > 0 ? "The interval includes 0." : "");
    text("cap", S.pick ? (r.model === "base" ? "Selected Base + cue rule" : "Selected RL rule") : "Best Base + cue rule within budget");
    const nm = wrap(r.name, g.wrap);
    [0, 1, 2].forEach(k => text("nm" + k, nm[k] || ""));
    text("score", `${one(right)} of ${N} at ${num(tok)} tokens`);
    const Y = g.ry;
    at(E.big, P(g.rx - 4, Y.big, 4)); at(E.unit, P(g.rx, Y.unit, 4)); at(E.unit2, P(g.rx, Y.unit + Y.lh, 4)); at(E.ci, P(g.rx, Y.ci, 4)); at(E.cap, P(g.rx, Y.cap, 4));
    [0, 1, 2].forEach(k => at(E["nm" + k], P(g.rx, Y.name + k * Y.lh, 4)));
    at(E.score, P(g.rx, Y.name + nm.length * Y.lh + 4, 4));
  }

  // The strip: one dot per problem, in the order of the benchmark, lit as often as the focus rule answers it right.
  // A change runs as a wave from left to right.
  const paths = Array.from({ length: 13 }, () => "");
  const st = S.strip;
  const cols = N / g.rows, cell = i => { const p = PLACE[i], row = p % g.rows; return [(p - row) / g.rows, row]; };
  for (let i = 0; i < N; i++) {
    const [col, row] = cell(i);
    let v = S.cells[i];
    if (st) { const p = ease(clamp((now - st.t0 - col * (350 / cols) - row * 10) / 420, 0, 1)); v = mix(st.from[i], st.to[i], p); }
    S.cells[i] = v;
    const q = P(g.sx + col * g.sp, g.sy + row * g.sp, 3);
    paths[Math.round(v * 12)] += "M" + f(q[0]) + " " + f(q[1]) + "h0";
  }
  paths.forEach((d, k) => E["c" + k].setAttribute("d", d));
  at(E.slab, P(g.sx - 2, g.slab, 3));
  const tx = g.sx + (RL1.right / g.rows - .5) * g.sp, ty = g.sy + g.rows * g.sp;  // where one RL sample's count of lit dots would end
  E.stick.setAttribute("d", line(g, [[tx, g.sy - g.sp], [tx, ty]], 4));
  at(E.stlab, narrow.matches ? P(tx + 4, ty + g.fs + 6, 4) : P(tx + 4, g.slab, 4));
  const ex = S.open === "rule" && S.pick ? C.examples[S.pick.model].problem : null;
  E.exring.style.display = ex == null ? "none" : "";
  if (ex != null) { const [col, row] = cell(ex); ctr(E.exring, P(g.sx + col * g.sp, g.sy + row * g.sp, 4)); }

  // The key under the strip.
  for (let k = 0; k < g.kx.length; k++) {
    const [kx, row] = g.kx[k], q = P(kx, g.ky[row], 3);
    ctr(E["kd" + k], q);
    at(E["kt" + k], [q[0] + g.fs * .8, q[1] + g.fs * .35]);
  }
  const ga = P(X0 - 20, Y0 - 30), gb = P(X1 + 10, Y1 + 30);
  E.grab.setAttribute("x", f(ga[0])); E.grab.setAttribute("y", f(ga[1]));
  E.grab.setAttribute("width", f(gb[0] - ga[0])); E.grab.setAttribute("height", f(gb[1] - ga[1]));
}

/* Motion that is always on: the plate sways by a few degrees and leans toward the mouse. The budget the picture shows
   follows the one the reader set within about a quarter of a second, so a jump sweeps across the chart. */
function frame(now) {
  requestAnimationFrame(frame);
  if (now - S.last < 30) return;
  S.last = now;
  S.t = now / 1000;
  if (still.matches) { S.shown = S.budget; aim(0, 0); }
  else {
    V.px += (V.tx - V.px) * .1;
    V.py += (V.ty - V.py) * .1;
    aim(3 * Math.sin(S.t * .13) + 3 * V.px, 1.4 * Math.sin(S.t * .09) - 1.5 * V.py);
    const k = 1 - Math.exp(-30 / 120), sw = S.sweep;
    if (sw) {  // the entrance: the budget rises once from 4,700 tokens to the full budget
      const p = clamp((now - sw.t0) / sw.d, 0, 1);
      S.shown = mix(SWEEP0, S.budget, ease(p));
      if (p >= 1) S.sweep = null;
    } else S.shown = Math.abs(S.budget - S.shown) < 5 ? S.budget : S.shown + (S.budget - S.shown) * k;
  }
  light(now);
  refocus(now);
  place(now);
}
/* Which marks are lit: the rules that fit the budget shown. A mark that changes waits a few milliseconds per mark
   already changing, so a jump lights them one after another. */
function light(now) {
  let n = 0;
  R.forEach(r => {
    const t = r.tokens <= S.shown || r === S.pick ? 1 : 0;
    if (t !== r.tgt) { r.tgt = t; r.at = still.matches ? 0 : now + 18 * n++; }
  });
}

function setBudget(b, push) {
  S.budget = clamp(Math.round(b / 100) * 100, BMIN, BMAX);
  S.pick = null; S.sweep = null;
  if (S.open === "rule") S.open = null;
  const inp = $("budget");
  inp.value = S.budget;
  inp.setAttribute("aria-valuetext", `${num(S.budget)} tokens per problem`);
  label();
  pane();
  address(push);
}
function label() {
  const r = focusOf(S.budget);
  $("svg").setAttribute("aria-label", `Right answers on MATH-500 against tokens per problem for 24 rules on the base model and the RL model. ` +
    `Budget ${num(S.budget)} tokens per problem.` + (r ? ` ${r.name}: ${one(r.right)} of ${N} at ${num(r.tokens)} tokens.` : ""));
}

/* The side column: the five panels, or the rule the reader clicked with one real problem. */
function rulePane(r) {
  const o = same(r), ex = C.examples[r.model], k = Math.round(r.g[ex.problem] * 24), mult = r.tokens / RL1.tokens;
  const facts = [`${one(r.right)} of ${N} right, the mean over the 24 orders of drawing the four samples, at ${num(r.tokens)} tokens per problem, ` +
    `${mult.toFixed(2)} times one RL sample.`];
  if (r.model === "base") facts.push(`${sgn(r.gap[0])} points versus one RL sample, 95 % interval ${sgn(r.gap[1])} to ${sgn(r.gap[2])}. ` +
    `RL with the same rule has ${one(o.right)} of ${N}, ${sgn(r.rl_lead[0])} points ahead (95 % interval ${sgn(r.rl_lead[1])} to ${sgn(r.rl_lead[2])}).`);
  else facts.push(r === ONE ? "This is the baseline: one sample of the RL model, the mean of its four samples." :
    `${sgn((r.right - RL1.right) / 5)} points versus one RL sample. Base + cue with the same rule has ${one(o.right)} of ${N}.`);
  if (r.short) facts.push("Ties go to the shortest finished sample. This tie rule was written after reading the problems it fixes, so the score is optimistic.");
  if (r.ran_out) facts.push(`On ${r.ran_out} problems the four stored samples ran out before the rule finished, so this row is approximate.`);
  const who = r.model === "base" ? "Base + cue" : "RL", tails = ex.tails.map(([i, t]) =>
    `<p class="tail"><span>End of sample ${i + 1}</span><span class="tt" data-math>${esc(t)}</span></p>`).join("");
  return `<div class="dhead"><h2>${esc(r.name)}</h2><button class="close" data-open="">Close</button></div>` +
    `<p class="lead">${who}, T 1.0: ${esc(r.config)}.</p><ul class="facts">${facts.map(x => `<li>${esc(x)}</li>`).join("")}</ul>` +
    `<h3 class="ex">One problem: MATH-500, problem ${ex.problem}, ringed in the strip</h3>` +
    `<p class="q"><span class="qt" data-math>${esc(ex.question)}</span>${ex.figure ? " <span>(with a figure given as code)</span>" : ""} <span>The answer key says <b data-math>${esc(ex.gold)}</b>.</span></p>` +
    `<ol class="samples">${ex.samples.map((s, i) => `<li><b data-math>${esc(s[0])}</b><span>${num(s[1])} tokens</span>` +
      `<span class="${s[2] ? "ok" : ""}">${s[2] ? "right" : "wrong"}</span></li>`).join("")}</ol>` +
    `<p class="verdict">${who} samples, in the order drawn. This rule answers the problem right in ${k} of the 24 draw orders.</p>` + tails;
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = S.open === "rule" && S.pick ? rulePane(S.pick)
    : p ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x).replace(/\[([^\]]+)\]\((\/finding\/[a-z-]+)\)/g, '<a href="$2">$1</a>')}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
/* The state is one value in the address: #<budget>, then <model>-<rule> or a panel, each optional. */
function address(push) {
  const parts = [S.budget !== B0 ? String(S.budget) : "", S.pick ? S.pick.key : "", S.open && S.open !== "rule" ? S.open : ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash() {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const b = parts.find(p => /^\d+$/.test(p)), r = R.find(r => parts.includes(r.key)), p = C.panels.find(p => parts.includes(p[0]));
  S.budget = clamp(b ? Math.round(Number(b) / 100) * 100 : B0, BMIN, BMAX);
  $("budget").value = S.budget;
  S.pick = r || null;
  S.open = r ? "rule" : p ? p[0] : null;
  if (r) rove(r);
  if (r || b) S.seen = true;
  label();
  pane();
}
const show = () => { if (narrow.matches) $("pane").scrollIntoView({ block: "start", behavior: still.matches ? "auto" : "smooth" }); };
function open(key) {
  const was = S.open, mark = S.pick;
  S.open = key || null;
  if (!key) S.pick = null;
  address(true);
  pane();
  const to = key ? $("pane").querySelector(".close") : was === "rule" && mark ? S.el["h" + mark.i] : $("pane").querySelector(`[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
  if (key) show();
}
function pick(key) {
  const r = R.find(r => r.key === key);
  if (!r) return;
  S.pick = r; S.open = "rule"; S.seen = true;
  rove(r);
  address(true);
  pane();
  show();
}
/* The 48 rule marks are one stop in the tab order; the arrow keys move along them in order of tokens. */
const ORDER = [...R].sort((p, q) => p.tokens - q.tokens || p.right - q.right);
function rove(r) {
  S.el["h" + S.rove].setAttribute("tabindex", "-1");
  S.rove = r.i;
  S.el["h" + r.i].setAttribute("tabindex", "0");
}

document.addEventListener("click", e => {
  const o = e.target.closest("[data-open]");
  if (o) open(o.dataset.open);
});
const svg = $("svg");
svg.addEventListener("click", e => { const h = e.target.closest(".hit"); if (h) pick(h.dataset.rule); });
svg.addEventListener("keydown", e => {
  const h = e.target.closest(".hit");
  if (!h) return;
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(h.dataset.rule); return; }
  const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
  if (!step) return;
  e.preventDefault();
  const r = ORDER[(ORDER.findIndex(o => o.key === h.dataset.rule) + step + R.length) % R.length];
  rove(r);
  S.el["h" + r.i].focus();
});
function fromPointer(e) {  // the budget under the pointer, read off the x axis as the reader sees it
  const g = S.g, m = svg.getScreenCTM().inverse(), pt = new DOMPoint(e.clientX, e.clientY).matrixTransform(m);
  const a = proj(g, g.X[0], g.Y[1], 0), b = proj(g, g.X[1], g.Y[1], 0);
  return mix(XD[0], XD[1], (pt.x - a[0]) / (b[0] - a[0]));
}
svg.addEventListener("pointerdown", e => {
  if (e.target.id !== "grab") return;
  S.drag = true; S.seen = true;
  svg.setPointerCapture(e.pointerId);
  setBudget(fromPointer(e), false);
});
svg.addEventListener("pointermove", e => { if (S.drag) setBudget(fromPointer(e), false); });
const end = () => { S.drag = false; };
svg.addEventListener("pointerup", end);
svg.addEventListener("pointercancel", end);
const inp = $("budget");
inp.min = BMIN; inp.max = BMAX;
inp.addEventListener("input", () => { S.seen = true; setBudget(Number(inp.value), false); });
inp.addEventListener("focus", () => S.el["knob-ring"].classList.add("on"));
inp.addEventListener("blur", () => S.el["knob-ring"].classList.remove("on"));
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) open("");
  if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && document.activeElement !== inp && !e.target.closest("input, textarea, .hit")) {
    S.seen = true;
    setBudget(S.budget + (e.key === "ArrowRight" ? 500 : -500), false);
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); place(performance.now()); });
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
S.rove = best(BASE, B0).i;
build();
fromHash();
S.shown = S.budget;
/* With no state in the address, the budget rises once from 4,700 tokens to the full budget after the plate appears. */
if (!location.hash && !still.matches) { S.shown = SWEEP0; S.sweep = { t0: performance.now() + 1300, d: 2600 }; }
R.forEach(r => { r.v = r.tgt = r.tokens <= S.shown ? 1 : 0; });
refocus(0);
place(0);
if (!still.matches) {
  svg.classList.add("enter");
  setTimeout(() => svg.classList.remove("enter"), 2200);
}
requestAnimationFrame(frame);
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({
    "problem": PROBLEM, "line": LINE, "panels": PANELS, "names": NAMES, "examples": DATA["examples"],
    "data": {"n": DATA["n"], "rl_single": DATA["rl_single"],
             "rules": [{k: r[k] for k in ("model", "rule", "config", "right", "tokens", "ran_out", "gap", "rl_lead", "grid") if k in r} for r in DATA["rules"]]}}))

if __name__ == "__main__":  # DATA against its artifacts; run from the repository root
    load = lambda path: json.load(open(path))
    run, readout, table = load(RUN + "run.json"), load(DATA["artifact"]), load(RUN + "frontier.json")
    per, ex = load(RUN + "per_problem.json")["per_problem"], load(RUN + "examples.json")
    assert run["commit"].startswith(DATA["commit"]) and DATA["jobs"] == run["source_jobs"]
    assert all(c.startswith(DATA["source_commit"]) for c in run["source_commits"].values())
    for m, folder in (("base", "math500_base_cue-01"), ("rl", "math500_rl-01")):
        assert load(f"studies/rlneurons/results/day1_3/{folder}/run.json")["config"]["model_repo"] == DATA["models"][m], m
    assert DATA["rl_single"] == {"right": readout["rl_single_24"]["right"], "tokens": readout["rl_single_24"]["tokens_per_problem"]}
    rows = [x for x in table["rows"] if x["model"] in ("base", "rl")]
    assert len(rows) == len(DATA["rules"]) == 48 and set(NAMES) == {r["rule"] for r in DATA["rules"]}
    for r in DATA["rules"]:
        m, k = r["model"], r["rule"]
        row = next(x for x in rows if x["model"] == m and x["rule"] == k)
        assert (r["config"], r["right"], r["tokens"], r["ran_out"]) == (row["configuration"], row["right_24"], row["tokens_per_problem_24"], row["ran_out"]), (m, k)
        assert r["grid"] == "".join(chr(97 + round(s * 24)) for s in per[m][k]["s"]) and len(r["grid"]) == DATA["n"], (m, k)
        assert abs(sum((ord(c) - 97) / 24 for c in r["grid"]) - r["right"]) < 1e-6, (m, k)
        if m == "base":
            b, q = readout["base_minus_rl_single"][k], readout["rl_minus_base"][k]
            assert r["gap"] == [b["points"], round(b["interval95"][0], 1), round(b["interval95"][1], 1)], k
            assert r["multiple"] == round(b["token_multiple"], 2), k
            assert r["rl_lead"] == [q["points"], round(q["interval95"][0], 1), round(q["interval95"][1], 1)], k
    for m in ("base", "rl"):
        e, src = DATA["examples"][m], ex[m]["stops_at_2_wrong"]
        assert (e["problem"], e["gold"]) == (src["problem_index"], src["gold"]) and e["question"] in src["prompt"], m
        assert e["samples"] == [[s["extracted_v3"], s["n_new"], s["score_v3"]] for s in src["samples"]], m
        assert all(src["samples"][i]["text_last_2000"].endswith(t) for i, t in e["tails"]), m
        sel = readout["models"][m]["selection"]
        assert DATA["held_out"][m] == [s["held_out_right_24"] for s in sel if s["budget"] >= 12500], m
    # The sentences of the page, against the table of README section "Token frontier".
    assert (_best["rule"], _best["right"], round(_best["tokens"]), _best["gap"], _best["multiple"]) == ("vote4_restart_short", 454.0, 19697, [-1.2, -3.0, 0.6], 4.2)
    assert (_plain["rule"], [round(v, 1) for v in _plain["gap"]], _plain["multiple"]) == ("seq4_restart", [-1.6, -3.2, 0.1], 3.03)
    assert round(_rlmax["right"], 1) == 476.1
    assert (_lead["rule"], _lead["rl_lead"]) == ("vote4_restart_short", [4.2, 2.4, 6.0])
    assert (_save(_seq[0], _seq[1]), _save(_seq[2], _seq[3])) == (30, 41), (_save(_seq[0], _seq[1]), _save(_seq[2], _seq[3]))
    print("DATA matches", RUN, "(run.json, readout.json, frontier.json, per_problem.json, examples.json)")
