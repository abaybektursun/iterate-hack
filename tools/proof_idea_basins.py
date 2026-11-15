"""Idea basins: the 515 items on the team board fall into 12 basins of ideas, by a judge model's reading.

A proof page: a reading of the team's own method (how diverse the ideas of its agents are), served at
/proof/idea-basins and reached from its tile on /proof, which ICON draws (made like a finding page,
.claude/skills/finding-page/SKILL.md; the looks are those of tools/architecture.py, .claude/skills/site-ui/SKILL.md).
The picture is one glass slab seen from slightly above, with a faint relief of ridge lines on it, and every board
item is a dot. The reader switches between three conditions (address /proof/idea-basins#<condition>, arrow keys):
the items in the order they were posted; the items gathered into the judge's basins, each deeper the more items it
holds; and the idea tree, one row per basin with a line from each item to the earlier items it builds on. Study:
studies/basins (results/swarm/main-04/run.json, branch ali/basins).
"""
import json

TITLE = "Idea basins"  # the name on its tile on /proof and in the browser tab
PROBLEM = "How diverse are the ideas our agents found?"
LINE = "515 board items fall into 12 idea basins."

# Every number is copied from the artifacts named here. None is typed from memory.
RESULTS = "studies/basins/results/swarm/"  # branch ali/basins
DATA = {
    "artifact": RESULTS + "main-04/summary.json",  # the items and their basins (the judge's groups)
    "commit": "79f1f7d",  # main-04
    "layout_commit": "79f1f7d",  # analysis/swarm_nested_layout.py and themes-02, branch ali/basins
    "snapshot": "15 November 2026, 19:42 UTC",  # main-04/run.json "snapshot"
    "judge": "gpt-6.1-sol",  # run.json "judge", metrics.json "judge"
    "items": 515, "clusters": 12,  # n_board_items, n_basins
    "largest": 81, "largest_share": 16, "effective": 10.9,  # basins[].board_items, largest_basin_share 0.157, effective_basins 10.87
    "heldout": 73, "shuffled": 51,  # tste_heldout_acc 0.728, tste_shuffled_id_null 0.508, as rounded percentages
    "ari_orders": 0.80, "ari_kmeans": 0.13,  # partition_ari_order0_vs_order1, partition_ari_vs_kmeans
    # Where things lie on the slab, with no board text: printed by
    #   python3 -m studies.basins.analysis.swarm_nested_layout studies/basins/results/swarm/main-04 studies/basins/results/swarm/themes-02 0.009
    # of which the page keeps the clusters and the items. x runs 0 to 1 and y 0 to wh. items are in the order they
    # were posted: c is the item's cluster, k its place among that cluster's items and p the places, in that order, of
    # the earlier items it builds on (the idea tree of main-04). "name" is the judge's short name
    # of the cluster (themes-02/metrics.json "short") and "full" its name in main-04.
    "layout": {
        "wh": 0.84, "s": 0.009,
        "clusters": [
            {"name": "Team tools", "full": "Research coordination and execution tools", "n": 63, "x": 0.3744, "y": 0.1648, "r": 0.0795},
            {"name": "Board design", "full": "Site design and research communication", "n": 72, "x": 0.1821, "y": 0.2387, "r": 0.0845},
            {"name": "Weight edits", "full": "Weight editing and self training", "n": 81, "x": 0.7641, "y": 0.4909, "r": 0.0891},
            {"name": "Neuron edits", "full": "Neuron interventions and loop mechanisms", "n": 24, "x": 0.7024, "y": 0.6646, "r": 0.0522},
            {"name": "Workspace steering", "full": "Jacobian lens readout and steering", "n": 25, "x": 0.8493, "y": 0.6544, "r": 0.0531},
            {"name": "Prompt cues", "full": "Prompt cues and context interventions", "n": 48, "x": 0.5163, "y": 0.5517, "r": 0.0705},
            {"name": "Sampling settings", "full": "Sampling distributions and temperature schedules", "n": 21, "x": 0.4657, "y": 0.7054, "r": 0.0493},
            {"name": "Sample selection", "full": "Voting restarts and token allocation", "n": 31, "x": 0.3543, "y": 0.6054, "r": 0.0582},
            {"name": "Theory tests", "full": "Theory generation and forecast testing", "n": 37, "x": 0.7358, "y": 0.2455, "r": 0.0628},
            {"name": "Scoring audits", "full": "Grading leakage and evaluation integrity", "n": 29, "x": 0.6062, "y": 0.1479, "r": 0.0566},
            {"name": "Error analysis", "full": "Failure analysis and correctness prediction", "n": 55, "x": 0.5713, "y": 0.3178, "r": 0.0748},
            {"name": "GPU prices", "full": "GPU rental price forecasting", "n": 29, "x": 0.3585, "y": 0.3956, "r": 0.0566},
        ],
        "items": [
            {"kind": "idea", "c": 6, "k": 0, "p": []}, {"kind": "idea", "c": 6, "k": 1, "p": []},
            {"kind": "idea", "c": 7, "k": 0, "p": []}, {"kind": "idea", "c": 2, "k": 0, "p": []},
            {"kind": "result", "c": 5, "k": 0, "p": []}, {"kind": "result", "c": 6, "k": 2, "p": []},
            {"kind": "result", "c": 6, "k": 3, "p": [4, 5]}, {"kind": "result", "c": 7, "k": 1, "p": [2]},
            {"kind": "result", "c": 6, "k": 4, "p": []}, {"kind": "knowledge", "c": 9, "k": 0, "p": [0]},
            {"kind": "knowledge", "c": 9, "k": 1, "p": []}, {"kind": "knowledge", "c": 5, "k": 1, "p": []},
            {"kind": "idea", "c": 9, "k": 2, "p": [10]}, {"kind": "idea", "c": 6, "k": 5, "p": [0]},
            {"kind": "idea", "c": 5, "k": 2, "p": [11]}, {"kind": "knowledge", "c": 0, "k": 0, "p": []},
            {"kind": "knowledge", "c": 0, "k": 1, "p": []}, {"kind": "knowledge", "c": 0, "k": 2, "p": [0, 1, 16]},
            {"kind": "result", "c": 0, "k": 3, "p": []}, {"kind": "work", "c": 0, "k": 4, "p": []},
            {"kind": "result", "c": 0, "k": 5, "p": [19]}, {"kind": "work", "c": 6, "k": 6, "p": [0, 17]},
            {"kind": "knowledge", "c": 5, "k": 3, "p": [6]}, {"kind": "knowledge", "c": 6, "k": 7, "p": [2]},
            {"kind": "work", "c": 1, "k": 0, "p": []}, {"kind": "work", "c": 7, "k": 2, "p": [2, 17]},
            {"kind": "work", "c": 6, "k": 8, "p": [1]}, {"kind": "idea", "c": 7, "k": 3, "p": [2]},
            {"kind": "idea", "c": 7, "k": 4, "p": [2, 7]}, {"kind": "idea", "c": 10, "k": 0, "p": [4, 5]},
            {"kind": "idea", "c": 2, "k": 1, "p": [3, 6]}, {"kind": "idea", "c": 0, "k": 6, "p": []},
            {"kind": "idea", "c": 10, "k": 1, "p": [6]}, {"kind": "work", "c": 0, "k": 7, "p": [31]},
            {"kind": "work", "c": 1, "k": 1, "p": [24]}, {"kind": "result", "c": 10, "k": 2, "p": [4, 5, 22, 23, 27, 28, 29, 30]},
            {"kind": "work", "c": 6, "k": 9, "p": [0, 21]}, {"kind": "work", "c": 1, "k": 2, "p": [24]},
            {"kind": "work", "c": 0, "k": 8, "p": [23]}, {"kind": "work", "c": 10, "k": 3, "p": [29]},
            {"kind": "work", "c": 7, "k": 5, "p": [25, 27, 28]}, {"kind": "work", "c": 2, "k": 2, "p": [3]},
            {"kind": "work", "c": 4, "k": 0, "p": [6]}, {"kind": "work", "c": 3, "k": 0, "p": [6]},
            {"kind": "work", "c": 0, "k": 9, "p": [19]}, {"kind": "result", "c": 0, "k": 10, "p": [44]},
            {"kind": "knowledge", "c": 3, "k": 1, "p": [43]}, {"kind": "knowledge", "c": 3, "k": 2, "p": [43]},
            {"kind": "knowledge", "c": 4, "k": 1, "p": [42]}, {"kind": "result", "c": 0, "k": 11, "p": [31, 33]},
            {"kind": "knowledge", "c": 0, "k": 12, "p": [38]}, {"kind": "result", "c": 0, "k": 13, "p": [38, 50]},
            {"kind": "knowledge", "c": 2, "k": 3, "p": [3, 41]}, {"kind": "knowledge", "c": 2, "k": 4, "p": [41]},
            {"kind": "idea", "c": 2, "k": 5, "p": [3, 53]}, {"kind": "idea", "c": 2, "k": 6, "p": [35, 52]},
            {"kind": "result", "c": 2, "k": 7, "p": [3, 41, 52, 53, 54, 55]}, {"kind": "idea", "c": 4, "k": 2, "p": [29, 35, 48]},
            {"kind": "idea", "c": 4, "k": 3, "p": [57]}, {"kind": "idea", "c": 4, "k": 4, "p": [57]},
            {"kind": "result", "c": 4, "k": 5, "p": [42, 48, 57, 58, 59]}, {"kind": "result", "c": 1, "k": 3, "p": [37]},
            {"kind": "result", "c": 6, "k": 10, "p": [0, 21]}, {"kind": "result", "c": 6, "k": 11, "p": [1, 26]},
            {"kind": "work", "c": 1, "k": 4, "p": []}, {"kind": "result", "c": 10, "k": 4, "p": [29, 39]},
            {"kind": "result", "c": 1, "k": 5, "p": [64]}, {"kind": "work", "c": 0, "k": 14, "p": []},
            {"kind": "knowledge", "c": 0, "k": 15, "p": [67]}, {"kind": "work", "c": 0, "k": 16, "p": [64]},
            {"kind": "work", "c": 0, "k": 17, "p": [45]}, {"kind": "work", "c": 11, "k": 0, "p": []},
            {"kind": "result", "c": 6, "k": 12, "p": [36, 62]}, {"kind": "result", "c": 11, "k": 1, "p": [71]},
            {"kind": "work", "c": 1, "k": 6, "p": [24]}, {"kind": "work", "c": 7, "k": 6, "p": [2, 25, 27, 28, 40, 62]},
            {"kind": "result", "c": 6, "k": 13, "p": [36, 72]}, {"kind": "work", "c": 11, "k": 2, "p": [73]},
            {"kind": "result", "c": 0, "k": 18, "p": [33, 49]}, {"kind": "work", "c": 4, "k": 6, "p": [57]},
            {"kind": "result", "c": 11, "k": 3, "p": [73, 77]}, {"kind": "knowledge", "c": 11, "k": 4, "p": [73]},
            {"kind": "idea", "c": 11, "k": 5, "p": [77, 80]}, {"kind": "work", "c": 2, "k": 8, "p": [3, 30]},
            {"kind": "result", "c": 11, "k": 6, "p": [80]}, {"kind": "result", "c": 10, "k": 5, "p": [28, 62]},
            {"kind": "work", "c": 0, "k": 19, "p": [19]}, {"kind": "idea", "c": 11, "k": 7, "p": [80, 82]},
            {"kind": "idea", "c": 11, "k": 8, "p": [77, 80]}, {"kind": "idea", "c": 11, "k": 9, "p": [77]},
            {"kind": "idea", "c": 11, "k": 10, "p": [77]}, {"kind": "idea", "c": 11, "k": 11, "p": [81]},
            {"kind": "work", "c": 2, "k": 9, "p": [54, 83]}, {"kind": "result", "c": 3, "k": 3, "p": [43, 47]},
            {"kind": "result", "c": 1, "k": 7, "p": [74]}, {"kind": "skill", "c": 1, "k": 8, "p": [74]},
            {"kind": "work", "c": 5, "k": 4, "p": [30, 83]}, {"kind": "idea", "c": 0, "k": 20, "p": [31]},
            {"kind": "work", "c": 10, "k": 6, "p": [32]}, {"kind": "result", "c": 11, "k": 12, "p": [87, 88]},
            {"kind": "result", "c": 11, "k": 13, "p": [82]}, {"kind": "result", "c": 0, "k": 21, "p": [86]},
            {"kind": "result", "c": 0, "k": 22, "p": [62, 70]}, {"kind": "work", "c": 0, "k": 23, "p": []},
            {"kind": "result", "c": 2, "k": 10, "p": [83]}, {"kind": "result", "c": 11, "k": 14, "p": [87, 99]},
            {"kind": "knowledge", "c": 2, "k": 11, "p": [52, 56, 83, 103]}, {"kind": "result", "c": 3, "k": 4, "p": [43, 93]},
            {"kind": "knowledge", "c": 3, "k": 5, "p": [43, 93, 103]}, {"kind": "knowledge", "c": 3, "k": 6, "p": [43, 63, 103]},
            {"kind": "knowledge", "c": 3, "k": 7, "p": [43, 103]}, {"kind": "knowledge", "c": 3, "k": 8, "p": [47, 83, 93, 103]},
            {"kind": "knowledge", "c": 2, "k": 12, "p": [83, 92, 93, 103]}, {"kind": "result", "c": 2, "k": 13, "p": [3, 54, 92]},
            {"kind": "knowledge", "c": 2, "k": 14, "p": [52, 56, 103]}, {"kind": "idea", "c": 2, "k": 15, "p": [3, 83, 92, 111]},
            {"kind": "knowledge", "c": 4, "k": 7, "p": [48, 60, 103]}, {"kind": "knowledge", "c": 4, "k": 8, "p": [55, 79, 103, 116]},
            {"kind": "knowledge", "c": 3, "k": 9, "p": [103]}, {"kind": "knowledge", "c": 3, "k": 10, "p": [103, 118]},
            {"kind": "knowledge", "c": 3, "k": 11, "p": [103, 119]}, {"kind": "knowledge", "c": 3, "k": 12, "p": [47, 93, 103, 111]},
            {"kind": "knowledge", "c": 5, "k": 5, "p": [7, 103]}, {"kind": "knowledge", "c": 10, "k": 7, "p": [4, 5, 103]},
            {"kind": "knowledge", "c": 3, "k": 13, "p": [103]}, {"kind": "knowledge", "c": 9, "k": 3, "p": [8, 103]},
            {"kind": "knowledge", "c": 5, "k": 6, "p": [9, 11, 103]}, {"kind": "knowledge", "c": 9, "k": 4, "p": [10, 65, 103]},
            {"kind": "knowledge", "c": 4, "k": 9, "p": [58, 60, 79, 103]}, {"kind": "knowledge", "c": 4, "k": 10, "p": [48, 103]},
            {"kind": "knowledge", "c": 2, "k": 16, "p": [47, 83, 103, 111]}, {"kind": "knowledge", "c": 0, "k": 24, "p": [14, 54, 103]},
            {"kind": "idea", "c": 2, "k": 17, "p": [83, 92, 96, 111]}, {"kind": "result", "c": 3, "k": 14, "p": [43, 46, 107]},
            {"kind": "result", "c": 4, "k": 11, "p": [79]}, {"kind": "result", "c": 4, "k": 12, "p": [58, 79]},
            {"kind": "result", "c": 4, "k": 13, "p": [79, 134]}, {"kind": "idea", "c": 4, "k": 14, "p": [59, 136]},
            {"kind": "knowledge", "c": 5, "k": 7, "p": [96]}, {"kind": "knowledge", "c": 11, "k": 15, "p": [77]},
            {"kind": "result", "c": 7, "k": 7, "p": [25, 27, 28, 40]}, {"kind": "result", "c": 7, "k": 8, "p": [62, 75]},
            {"kind": "idea", "c": 7, "k": 9, "p": [40, 75, 140]}, {"kind": "knowledge", "c": 0, "k": 25, "p": [103, 118]},
            {"kind": "result", "c": 0, "k": 26, "p": [103, 143]}, {"kind": "result", "c": 11, "k": 16, "p": [88, 90, 105]},
            {"kind": "result", "c": 2, "k": 18, "p": [83]}, {"kind": "result", "c": 11, "k": 17, "p": [90, 105]},
            {"kind": "result", "c": 2, "k": 19, "p": [3, 30, 83]}, {"kind": "result", "c": 2, "k": 20, "p": [146, 148]},
            {"kind": "work", "c": 4, "k": 15, "p": [79, 116, 129]}, {"kind": "work", "c": 6, "k": 14, "p": [1, 49]},
            {"kind": "work", "c": 8, "k": 0, "p": []}, {"kind": "work", "c": 2, "k": 21, "p": [62, 148]},
            {"kind": "result", "c": 8, "k": 1, "p": [152]}, {"kind": "result", "c": 10, "k": 8, "p": [98]},
            {"kind": "idea", "c": 5, "k": 8, "p": [113, 148]}, {"kind": "work", "c": 5, "k": 9, "p": [156]},
            {"kind": "work", "c": 5, "k": 10, "p": [4, 49]}, {"kind": "work", "c": 8, "k": 2, "p": [152]},
            {"kind": "idea", "c": 2, "k": 22, "p": [30, 148]}, {"kind": "idea", "c": 8, "k": 3, "p": [153, 159]},
            {"kind": "result", "c": 8, "k": 4, "p": [159, 161]}, {"kind": "work", "c": 2, "k": 23, "p": [160]},
            {"kind": "knowledge", "c": 4, "k": 16, "p": [129, 150]}, {"kind": "result", "c": 11, "k": 18, "p": [82, 105]},
            {"kind": "result", "c": 11, "k": 19, "p": [77, 165]}, {"kind": "result", "c": 11, "k": 20, "p": [89]},
            {"kind": "result", "c": 6, "k": 15, "p": [151]}, {"kind": "result", "c": 3, "k": 15, "p": [43, 107, 133]},
            {"kind": "work", "c": 0, "k": 27, "p": [45]}, {"kind": "result", "c": 7, "k": 10, "p": [2, 25]},
            {"kind": "knowledge", "c": 0, "k": 28, "p": []}, {"kind": "work", "c": 8, "k": 5, "p": [162]},
            {"kind": "result", "c": 2, "k": 24, "p": [92, 113, 115]}, {"kind": "result", "c": 4, "k": 17, "p": [150]},
            {"kind": "result", "c": 4, "k": 18, "p": [150]}, {"kind": "result", "c": 5, "k": 11, "p": [158]},
            {"kind": "work", "c": 7, "k": 11, "p": [142, 171]}, {"kind": "work", "c": 1, "k": 9, "p": [34, 64]},
            {"kind": "work", "c": 1, "k": 10, "p": [64, 179]}, {"kind": "result", "c": 1, "k": 11, "p": [4, 148, 171, 179, 180]},
            {"kind": "result", "c": 7, "k": 12, "p": [141, 178]}, {"kind": "work", "c": 0, "k": 29, "p": [41, 43]},
            {"kind": "result", "c": 2, "k": 25, "p": [148, 153]}, {"kind": "result", "c": 2, "k": 26, "p": [184]},
            {"kind": "knowledge", "c": 0, "k": 30, "p": [52, 131, 177, 183]}, {"kind": "work", "c": 0, "k": 31, "p": [186]},
            {"kind": "result", "c": 8, "k": 6, "p": [161, 173, 184]}, {"kind": "work", "c": 2, "k": 27, "p": [56, 171]},
            {"kind": "work", "c": 9, "k": 5, "p": [4, 7, 62, 148, 171, 182]}, {"kind": "result", "c": 2, "k": 28, "p": [148, 160, 163]},
            {"kind": "idea", "c": 2, "k": 29, "p": [107, 113, 163, 174, 187]}, {"kind": "result", "c": 9, "k": 6, "p": [148, 182, 190]},
            {"kind": "result", "c": 2, "k": 30, "p": [92, 174]}, {"kind": "result", "c": 4, "k": 19, "p": [150, 175]},
            {"kind": "work", "c": 8, "k": 7, "p": [188]}, {"kind": "work", "c": 9, "k": 7, "p": [22, 171]},
            {"kind": "result", "c": 9, "k": 8, "p": [4, 171, 197]}, {"kind": "knowledge", "c": 9, "k": 9, "p": [173, 196]},
            {"kind": "idea", "c": 2, "k": 31, "p": [156, 171, 182, 191, 194]}, {"kind": "idea", "c": 10, "k": 9, "p": [135, 140, 160, 191, 200]},
            {"kind": "result", "c": 1, "k": 12, "p": [179]}, {"kind": "result", "c": 2, "k": 32, "p": [163, 191, 201]},
            {"kind": "result", "c": 3, "k": 16, "p": [43, 63]}, {"kind": "result", "c": 5, "k": 12, "p": [156, 157]},
            {"kind": "result", "c": 1, "k": 13, "p": [180, 181]}, {"kind": "work", "c": 2, "k": 33, "p": [192]},
            {"kind": "idea", "c": 10, "k": 10, "p": [35, 171]}, {"kind": "work", "c": 10, "k": 11, "p": [208]},
            {"kind": "result", "c": 2, "k": 34, "p": [92, 194]}, {"kind": "idea", "c": 10, "k": 12, "p": [208, 210]},
            {"kind": "idea", "c": 5, "k": 13, "p": [122, 208]}, {"kind": "work", "c": 5, "k": 14, "p": [212]},
            {"kind": "work", "c": 10, "k": 13, "p": [211]}, {"kind": "work", "c": 7, "k": 13, "p": [2, 141, 171]},
            {"kind": "result", "c": 9, "k": 10, "p": [12]}, {"kind": "result", "c": 10, "k": 14, "p": [209]},
            {"kind": "knowledge", "c": 7, "k": 14, "p": [63, 124, 171]}, {"kind": "idea", "c": 9, "k": 11, "p": [12, 217]},
            {"kind": "work", "c": 9, "k": 12, "p": [219]}, {"kind": "work", "c": 11, "k": 21, "p": [166]},
            {"kind": "result", "c": 2, "k": 35, "p": [192, 207]}, {"kind": "result", "c": 4, "k": 20, "p": [134, 150]},
            {"kind": "result", "c": 4, "k": 21, "p": [150, 223]}, {"kind": "result", "c": 8, "k": 8, "p": [196]},
            {"kind": "work", "c": 1, "k": 14, "p": [31, 78]}, {"kind": "work", "c": 8, "k": 9, "p": [196, 225]},
            {"kind": "result", "c": 11, "k": 22, "p": [221]}, {"kind": "result", "c": 9, "k": 13, "p": [220]},
            {"kind": "work", "c": 1, "k": 15, "p": []}, {"kind": "result", "c": 1, "k": 16, "p": [226]},
            {"kind": "result", "c": 10, "k": 15, "p": [211, 214]}, {"kind": "work", "c": 1, "k": 17, "p": [74, 95, 230]},
            {"kind": "work", "c": 4, "k": 22, "p": [137]}, {"kind": "work", "c": 5, "k": 15, "p": [205]},
            {"kind": "result", "c": 11, "k": 23, "p": [165, 221, 228]}, {"kind": "idea", "c": 10, "k": 16, "p": [232]},
            {"kind": "work", "c": 10, "k": 17, "p": [227, 237]}, {"kind": "idea", "c": 10, "k": 18, "p": [217, 234]},
            {"kind": "work", "c": 10, "k": 19, "p": [234, 239]}, {"kind": "result", "c": 0, "k": 32, "p": [170]},
            {"kind": "work", "c": 0, "k": 33, "p": []}, {"kind": "work", "c": 1, "k": 18, "p": [31, 231]},
            {"kind": "work", "c": 10, "k": 20, "p": [201]}, {"kind": "idea", "c": 6, "k": 16, "p": [168, 218]},
            {"kind": "work", "c": 6, "k": 17, "p": [245]}, {"kind": "result", "c": 0, "k": 34, "p": [31, 78, 205]},
            {"kind": "work", "c": 5, "k": 16, "p": [194]}, {"kind": "result", "c": 10, "k": 21, "p": [234, 240]},
            {"kind": "result", "c": 11, "k": 24, "p": [221]}, {"kind": "result", "c": 4, "k": 23, "p": [234]},
            {"kind": "result", "c": 1, "k": 19, "p": [243]}, {"kind": "result", "c": 0, "k": 35, "p": [242]},
            {"kind": "result", "c": 10, "k": 22, "p": [238]}, {"kind": "work", "c": 1, "k": 20, "p": [217, 249]},
            {"kind": "idea", "c": 10, "k": 23, "p": [232, 254]}, {"kind": "work", "c": 10, "k": 24, "p": [256]},
            {"kind": "idea", "c": 0, "k": 36, "p": []}, {"kind": "result", "c": 11, "k": 25, "p": [221]},
            {"kind": "result", "c": 11, "k": 26, "p": [221, 236]}, {"kind": "skill", "c": 0, "k": 37, "p": [253]},
            {"kind": "result", "c": 1, "k": 21, "p": [255]}, {"kind": "result", "c": 5, "k": 17, "p": [96]},
            {"kind": "result", "c": 1, "k": 22, "p": [230]}, {"kind": "work", "c": 1, "k": 23, "p": [74]},
            {"kind": "result", "c": 1, "k": 24, "p": [233]}, {"kind": "result", "c": 5, "k": 18, "p": [157, 205]},
            {"kind": "work", "c": 1, "k": 25, "p": [170, 241]}, {"kind": "work", "c": 5, "k": 19, "p": [28, 85]},
            {"kind": "work", "c": 0, "k": 38, "p": [44]}, {"kind": "knowledge", "c": 0, "k": 39, "p": [234]},
            {"kind": "result", "c": 10, "k": 25, "p": [201, 244]}, {"kind": "result", "c": 10, "k": 26, "p": [256, 257]},
            {"kind": "work", "c": 10, "k": 27, "p": [191, 209, 249]}, {"kind": "work", "c": 1, "k": 26, "p": [179]},
            {"kind": "result", "c": 0, "k": 40, "p": [270]}, {"kind": "work", "c": 1, "k": 27, "p": [74]},
            {"kind": "result", "c": 5, "k": 20, "p": [28, 126, 269]}, {"kind": "work", "c": 2, "k": 36, "p": [52, 210]},
            {"kind": "work", "c": 2, "k": 37, "p": [189, 200]}, {"kind": "idea", "c": 10, "k": 28, "p": [232, 273]},
            {"kind": "work", "c": 10, "k": 29, "p": [248, 281]}, {"kind": "idea", "c": 9, "k": 14, "p": [9]},
            {"kind": "idea", "c": 7, "k": 15, "p": [171, 182]}, {"kind": "work", "c": 9, "k": 15, "p": [283]},
            {"kind": "work", "c": 7, "k": 16, "p": [215, 284]}, {"kind": "result", "c": 1, "k": 28, "p": [277]},
            {"kind": "work", "c": 0, "k": 41, "p": [270]}, {"kind": "result", "c": 3, "k": 17, "p": [204]},
            {"kind": "work", "c": 1, "k": 29, "p": [4, 7, 171, 182, 263]}, {"kind": "result", "c": 10, "k": 30, "p": [191, 249, 274]},
            {"kind": "work", "c": 10, "k": 31, "p": [274, 280, 291]}, {"kind": "work", "c": 1, "k": 30, "p": [74]},
            {"kind": "result", "c": 1, "k": 31, "p": [293]}, {"kind": "result", "c": 7, "k": 17, "p": [215, 286]},
            {"kind": "result", "c": 5, "k": 21, "p": [248]}, {"kind": "work", "c": 0, "k": 42, "p": [270, 276]},
            {"kind": "work", "c": 0, "k": 43, "p": [172]}, {"kind": "result", "c": 10, "k": 32, "p": [282, 296]},
            {"kind": "result", "c": 2, "k": 38, "p": [189]}, {"kind": "idea", "c": 7, "k": 18, "p": [296, 299]},
            {"kind": "work", "c": 7, "k": 19, "p": [298, 301]}, {"kind": "result", "c": 2, "k": 39, "p": [300]},
            {"kind": "work", "c": 9, "k": 16, "p": [12]}, {"kind": "result", "c": 0, "k": 44, "p": [297]},
            {"kind": "result", "c": 2, "k": 40, "p": [207, 210]}, {"kind": "work", "c": 1, "k": 32, "p": [31, 78]},
            {"kind": "result", "c": 0, "k": 45, "p": [265]}, {"kind": "result", "c": 3, "k": 18, "p": [204, 289]},
            {"kind": "result", "c": 1, "k": 33, "p": [4, 7, 171, 182, 263, 290]}, {"kind": "result", "c": 2, "k": 41, "p": [279]},
            {"kind": "result", "c": 0, "k": 46, "p": [298]}, {"kind": "work", "c": 0, "k": 47, "p": [297]},
            {"kind": "result", "c": 9, "k": 17, "p": [12, 304]}, {"kind": "result", "c": 5, "k": 22, "p": [11, 227]},
            {"kind": "knowledge", "c": 8, "k": 10, "p": [65, 191, 227]}, {"kind": "knowledge", "c": 8, "k": 11, "p": [227]},
            {"kind": "idea", "c": 3, "k": 19, "p": [227]}, {"kind": "result", "c": 8, "k": 12, "p": [227, 315]},
            {"kind": "work", "c": 8, "k": 13, "p": [319]}, {"kind": "idea", "c": 5, "k": 23, "p": [227, 315]},
            {"kind": "result", "c": 0, "k": 48, "p": [290]}, {"kind": "work", "c": 1, "k": 34, "p": [224, 310]},
            {"kind": "result", "c": 5, "k": 24, "p": [213]}, {"kind": "result", "c": 1, "k": 35, "p": [323]},
            {"kind": "result", "c": 5, "k": 25, "p": [296]}, {"kind": "result", "c": 4, "k": 24, "p": [137, 234]},
            {"kind": "result", "c": 3, "k": 20, "p": [204, 309]}, {"kind": "work", "c": 8, "k": 14, "p": [227, 320]},
            {"kind": "work", "c": 1, "k": 36, "p": [74]}, {"kind": "result", "c": 3, "k": 21, "p": [278, 328]},
            {"kind": "result", "c": 2, "k": 42, "p": [207, 222]}, {"kind": "result", "c": 0, "k": 49, "p": [313]},
            {"kind": "work", "c": 0, "k": 50, "p": [297, 333]}, {"kind": "result", "c": 0, "k": 51, "p": [265]},
            {"kind": "result", "c": 1, "k": 37, "p": [275]}, {"kind": "result", "c": 1, "k": 38, "p": [330]},
            {"kind": "result", "c": 2, "k": 43, "p": [279, 311]}, {"kind": "idea", "c": 5, "k": 26, "p": [302, 324, 326]},
            {"kind": "work", "c": 5, "k": 27, "p": [339]}, {"kind": "work", "c": 2, "k": 44, "p": [200]},
            {"kind": "result", "c": 10, "k": 33, "p": [217, 329]}, {"kind": "idea", "c": 2, "k": 45, "p": [210, 329]},
            {"kind": "idea", "c": 5, "k": 28, "p": [4, 329]}, {"kind": "knowledge", "c": 8, "k": 15, "p": [329, 344]},
            {"kind": "result", "c": 10, "k": 34, "p": [329]}, {"kind": "result", "c": 8, "k": 16, "p": [329, 343, 344]},
            {"kind": "result", "c": 9, "k": 18, "p": [326]}, {"kind": "work", "c": 2, "k": 46, "p": [281, 299, 302]},
            {"kind": "result", "c": 1, "k": 39, "p": [265]}, {"kind": "idea", "c": 0, "k": 52, "p": [75, 182]},
            {"kind": "idea", "c": 0, "k": 53, "p": [163]}, {"kind": "result", "c": 2, "k": 47, "p": [280]},
            {"kind": "work", "c": 7, "k": 20, "p": [278, 326]}, {"kind": "result", "c": 6, "k": 18, "p": [245, 246]},
            {"kind": "work", "c": 1, "k": 40, "p": [233, 291, 315, 327]}, {"kind": "knowledge", "c": 5, "k": 29, "p": [200, 321]},
            {"kind": "knowledge", "c": 9, "k": 19, "p": [355]}, {"kind": "work", "c": 8, "k": 17, "p": [320, 329]},
            {"kind": "result", "c": 2, "k": 48, "p": [207, 306]}, {"kind": "work", "c": 2, "k": 49, "p": [192, 360]},
            {"kind": "idea", "c": 5, "k": 30, "p": [4, 344]}, {"kind": "work", "c": 5, "k": 31, "p": [362]},
            {"kind": "result", "c": 7, "k": 21, "p": [182, 215]}, {"kind": "result", "c": 9, "k": 20, "p": [283, 285]},
            {"kind": "result", "c": 2, "k": 50, "p": [360, 361]}, {"kind": "knowledge", "c": 7, "k": 22, "p": [142, 364]},
            {"kind": "work", "c": 5, "k": 32, "p": [315, 321]}, {"kind": "work", "c": 7, "k": 23, "p": [215, 302]},
            {"kind": "result", "c": 6, "k": 19, "p": [291, 292]}, {"kind": "result", "c": 7, "k": 24, "p": [302, 369]},
            {"kind": "result", "c": 7, "k": 25, "p": [301, 302, 348, 349]}, {"kind": "work", "c": 9, "k": 21, "p": [348, 372]},
            {"kind": "result", "c": 10, "k": 35, "p": [274, 292, 370]}, {"kind": "idea", "c": 0, "k": 54, "p": [19]},
            {"kind": "work", "c": 10, "k": 36, "p": [272, 374]}, {"kind": "work", "c": 0, "k": 55, "p": [17]},
            {"kind": "result", "c": 10, "k": 37, "p": [376]}, {"kind": "knowledge", "c": 10, "k": 38, "p": [272, 370, 374, 378]},
            {"kind": "result", "c": 5, "k": 33, "p": [339, 340]}, {"kind": "idea", "c": 9, "k": 22, "p": [348, 372]},
            {"kind": "work", "c": 9, "k": 23, "p": [381]}, {"kind": "idea", "c": 10, "k": 39, "p": [372]},
            {"kind": "work", "c": 10, "k": 40, "p": [383]}, {"kind": "result", "c": 10, "k": 41, "p": [384]},
            {"kind": "result", "c": 0, "k": 56, "p": [377]}, {"kind": "idea", "c": 10, "k": 42, "p": [385]},
            {"kind": "work", "c": 10, "k": 43, "p": [387]}, {"kind": "result", "c": 9, "k": 24, "p": [348, 372, 373, 382]},
            {"kind": "result", "c": 5, "k": 34, "p": [362, 363]}, {"kind": "result", "c": 5, "k": 35, "p": [390]},
            {"kind": "result", "c": 10, "k": 44, "p": [387, 388]}, {"kind": "work", "c": 10, "k": 45, "p": [383, 385]},
            {"kind": "result", "c": 10, "k": 46, "p": [385, 393]}, {"kind": "idea", "c": 9, "k": 25, "p": []},
            {"kind": "work", "c": 9, "k": 26, "p": [349, 354, 395]}, {"kind": "result", "c": 3, "k": 22, "p": [309, 328]},
            {"kind": "result", "c": 9, "k": 27, "p": [326, 354, 396]}, {"kind": "work", "c": 10, "k": 47, "p": [387, 392]},
            {"kind": "result", "c": 10, "k": 48, "p": [392, 399]}, {"kind": "idea", "c": 2, "k": 51, "p": [343, 359]},
            {"kind": "result", "c": 10, "k": 49, "p": [342, 359]}, {"kind": "knowledge", "c": 8, "k": 18, "p": [321, 359]},
            {"kind": "result", "c": 8, "k": 19, "p": [320, 359, 401]}, {"kind": "work", "c": 8, "k": 20, "p": [320]},
            {"kind": "result", "c": 2, "k": 52, "p": [360, 361, 366]}, {"kind": "work", "c": 2, "k": 53, "p": [192, 406]},
            {"kind": "result", "c": 2, "k": 54, "p": [349]}, {"kind": "work", "c": 2, "k": 55, "p": [281, 408]},
            {"kind": "result", "c": 8, "k": 21, "p": [405]}, {"kind": "work", "c": 8, "k": 22, "p": [405]},
            {"kind": "idea", "c": 6, "k": 20, "p": [278, 334]}, {"kind": "knowledge", "c": 8, "k": 23, "p": [411]},
            {"kind": "result", "c": 8, "k": 24, "p": [401, 411]}, {"kind": "result", "c": 7, "k": 26, "p": [354]},
            {"kind": "work", "c": 7, "k": 27, "p": [171, 402]}, {"kind": "result", "c": 9, "k": 28, "p": [381, 382]},
            {"kind": "result", "c": 8, "k": 25, "p": [334, 354, 368, 382, 407, 409, 416, 417]}, {"kind": "idea", "c": 7, "k": 28, "p": [372, 415, 417]},
            {"kind": "work", "c": 7, "k": 29, "p": [419]}, {"kind": "work", "c": 0, "k": 57, "p": []},
            {"kind": "result", "c": 2, "k": 56, "p": [406, 407]}, {"kind": "work", "c": 5, "k": 36, "p": [4, 263]},
            {"kind": "work", "c": 2, "k": 57, "p": [407, 417]}, {"kind": "work", "c": 2, "k": 58, "p": [192, 406]},
            {"kind": "result", "c": 8, "k": 26, "p": [401, 418, 422]}, {"kind": "work", "c": 11, "k": 27, "p": [166]},
            {"kind": "result", "c": 0, "k": 58, "p": [297, 334, 412]}, {"kind": "result", "c": 0, "k": 59, "p": [199, 406, 408, 415, 417, 421, 422]},
            {"kind": "work", "c": 1, "k": 41, "p": []}, {"kind": "result", "c": 5, "k": 37, "p": [423]},
            {"kind": "result", "c": 11, "k": 28, "p": [228, 427]}, {"kind": "work", "c": 2, "k": 59, "p": [406, 422, 424, 429]},
            {"kind": "work", "c": 8, "k": 27, "p": [320]}, {"kind": "idea", "c": 10, "k": 50, "p": [295, 412, 415]},
            {"kind": "work", "c": 10, "k": 51, "p": [435]}, {"kind": "result", "c": 5, "k": 38, "p": [315, 321, 368]},
            {"kind": "result", "c": 3, "k": 23, "p": [43, 107, 397]}, {"kind": "work", "c": 1, "k": 42, "p": []},
            {"kind": "result", "c": 2, "k": 60, "p": [406, 424, 425, 433]}, {"kind": "result", "c": 1, "k": 43, "p": [439]},
            {"kind": "work", "c": 1, "k": 44, "p": [265]}, {"kind": "work", "c": 1, "k": 45, "p": [308]},
            {"kind": "result", "c": 1, "k": 46, "p": [442]}, {"kind": "result", "c": 1, "k": 47, "p": [443]},
            {"kind": "result", "c": 2, "k": 61, "p": [406, 425]}, {"kind": "work", "c": 2, "k": 62, "p": [192, 263, 406]},
            {"kind": "result", "c": 7, "k": 30, "p": [354, 415]}, {"kind": "work", "c": 5, "k": 39, "p": [415]},
            {"kind": "work", "c": 0, "k": 60, "p": [420, 429, 433]}, {"kind": "work", "c": 1, "k": 48, "p": [24]},
            {"kind": "result", "c": 1, "k": 49, "p": [430]}, {"kind": "result", "c": 10, "k": 52, "p": [272, 378, 436]},
            {"kind": "work", "c": 5, "k": 40, "p": [437, 450]}, {"kind": "result", "c": 1, "k": 50, "p": [451]},
            {"kind": "idea", "c": 2, "k": 63, "p": [210, 401]}, {"kind": "work", "c": 2, "k": 64, "p": [456]},
            {"kind": "result", "c": 2, "k": 65, "p": [406, 447]}, {"kind": "result", "c": 8, "k": 28, "p": [458]},
            {"kind": "result", "c": 8, "k": 29, "p": [450]}, {"kind": "knowledge", "c": 2, "k": 66, "p": [222, 437]},
            {"kind": "work", "c": 2, "k": 67, "p": [192, 406]}, {"kind": "knowledge", "c": 8, "k": 30, "p": [434]},
            {"kind": "result", "c": 8, "k": 31, "p": [434, 463]}, {"kind": "idea", "c": 8, "k": 32, "p": [464]},
            {"kind": "work", "c": 5, "k": 41, "p": [465]}, {"kind": "work", "c": 5, "k": 42, "p": [465]},
            {"kind": "work", "c": 2, "k": 68, "p": [465]}, {"kind": "work", "c": 8, "k": 33, "p": [320, 464]},
            {"kind": "result", "c": 5, "k": 43, "p": [437, 454]}, {"kind": "result", "c": 2, "k": 69, "p": [401, 456, 457]},
            {"kind": "result", "c": 2, "k": 70, "p": [406, 462]}, {"kind": "work", "c": 2, "k": 71, "p": [192, 472]},
            {"kind": "result", "c": 5, "k": 44, "p": [465, 466]}, {"kind": "result", "c": 5, "k": 45, "p": [450, 470]},
            {"kind": "work", "c": 1, "k": 51, "p": [444, 445]}, {"kind": "knowledge", "c": 10, "k": 53, "p": [272]},
            {"kind": "work", "c": 2, "k": 72, "p": [472]}, {"kind": "work", "c": 2, "k": 73, "p": [469, 472]},
            {"kind": "work", "c": 2, "k": 74, "p": [469]}, {"kind": "result", "c": 2, "k": 75, "p": [422, 424]},
            {"kind": "result", "c": 1, "k": 52, "p": [182, 247, 307]}, {"kind": "result", "c": 8, "k": 34, "p": [458, 469]},
            {"kind": "knowledge", "c": 8, "k": 35, "p": [422, 428, 458, 472, 474, 483]}, {"kind": "result", "c": 2, "k": 76, "p": [472, 473]},
            {"kind": "work", "c": 1, "k": 53, "p": [350, 482]}, {"kind": "result", "c": 5, "k": 46, "p": [465, 467]},
            {"kind": "work", "c": 5, "k": 47, "p": [263, 372]}, {"kind": "result", "c": 1, "k": 54, "p": [455]},
            {"kind": "work", "c": 2, "k": 77, "p": [132, 192, 408]}, {"kind": "work", "c": 2, "k": 78, "p": [192, 332]},
            {"kind": "work", "c": 1, "k": 55, "p": [356, 409]}, {"kind": "work", "c": 8, "k": 36, "p": [320, 483]},
            {"kind": "work", "c": 1, "k": 56, "p": [489]}, {"kind": "result", "c": 1, "k": 57, "p": [247, 307]},
            {"kind": "work", "c": 1, "k": 58, "p": [441]}, {"kind": "result", "c": 10, "k": 54, "p": [272, 450, 477]},
            {"kind": "result", "c": 1, "k": 59, "p": [476]}, {"kind": "work", "c": 1, "k": 60, "p": []},
            {"kind": "knowledge", "c": 0, "k": 61, "p": [442]}, {"kind": "knowledge", "c": 0, "k": 62, "p": [443]},
            {"kind": "work", "c": 1, "k": 61, "p": [482, 486, 495]}, {"kind": "result", "c": 2, "k": 79, "p": [332, 491]},
            {"kind": "result", "c": 2, "k": 80, "p": [472, 478, 485]}, {"kind": "result", "c": 1, "k": 62, "p": [450]},
            {"kind": "result", "c": 1, "k": 63, "p": [494]}, {"kind": "work", "c": 1, "k": 64, "p": [498]},
            {"kind": "result", "c": 1, "k": 65, "p": [499]}, {"kind": "work", "c": 1, "k": 66, "p": [486]},
            {"kind": "result", "c": 1, "k": 67, "p": [502]}, {"kind": "result", "c": 1, "k": 68, "p": [496]},
            {"kind": "work", "c": 1, "k": 69, "p": [510]}, {"kind": "work", "c": 1, "k": 70, "p": [494, 506]},
            {"kind": "work", "c": 1, "k": 71, "p": [511]},
        ],
    },
}
_ITEMS = DATA["layout"]["items"]
_LINKS = [(p, i) for i, n in enumerate(_ITEMS) for p in n["p"]]
# The idea tree: counted from the links above, and checked against main-04/summary.json "tree" (n_links,
# cross_basin_links, roots); depth, written and found are its max_depth, explicit_links and explicit_found_by_judge.
DATA["tree"] = {
    "links": len(_LINKS), "cross": sum(_ITEMS[a]["c"] != _ITEMS[b]["c"] for a, b in _LINKS),
    "merge": sum(len(n["p"]) > 1 for n in _ITEMS), "roots": sum(not n["p"] for n in _ITEMS),
    "depth": 34, "written": 382, "found": 269,
}
assert (DATA["tree"]["links"], DATA["tree"]["cross"], DATA["tree"]["roots"]) == (914, 269, 29), DATA["tree"]

# What the reader switches between. The first is shown on load: start from the problem, not from the answer.
DATA["states"] = [
    {"key": "items", "name": f"{DATA['items']} items", "unit": "items on the team board",
     "note": "Each dot is an item on the team board, in the order it was posted: an idea, a piece of work, a note or a result."},
    {"key": "basins", "name": f"{DATA['clusters']} basins", "unit": "idea basins",
     "note": "A judge model compared the methods of the items. Items with the same method fall into one basin, and a basin is deeper the more items it holds."},
    {"key": "tree", "name": "Idea tree", "unit": "items that build on two or more earlier items",
     "problem": "Do ideas from different basins come together?",
     "line": f"{DATA['tree']['cross']} of {DATA['tree']['links']} links between items join two different basins.",
     "note": "Each row is a basin, and its items run from left to right in the order they were posted. A line joins an item to an earlier item it builds on. A blue line crosses from one basin to another."},
]

# Depth, opened by a click: key, name, one sentence, then at most three more. Full plain sentences, no bold lead-ins.
PANELS = [
    ["new", "What is new",
     "Idea basins are published for the runs of single models. Here they are read from a live team board.",
     ["Idea basins come from Fork-and-Flush (arXiv 2610.07447): a basin is a group of attempts that share a broad method.",
      "Bespoke Labs mapped the basins of the models on its AutoResearchExam benchmark (\"How models explore ideas\", 10 November 2026): 58 % of runs never reach the basin of their task's best solution.",
      f"The {DATA['items']} items of three people's agents fall into {DATA['clusters']} basins. The fullest holds {DATA['largest']} items ({DATA['largest_share']} %), so no single idea took over the board."]],
    ["why", "Why it matters",
     "The number of items says how busy a team of agents was. The number of basins says how diverse its ideas were.",
     [f"Weighted by size, the {DATA['clusters']} basins count as {DATA['effective']} equally full ones.",
      f"Ideas also converge: {DATA['tree']['merge']} of {DATA['items']} items build on two or more earlier items, and the longest chain has {DATA['tree']['depth']} links."]],
    ["how", "How we know",
     f"A judge model ({DATA['judge']}) was asked, for three items at a time, which two use the closer method. The basins come from its answers.",
     [f"A map fitted to the answers predicts {DATA['heldout']} % of answers it was not fitted on. With the items shuffled it predicts {DATA['shuffled']} %.",
      "Two exact copies of one board item were planted. The judge put both in the basin of the original, in both orders of the board.",
      f"The judge grouped the board twice, in two orders of the items. The two groupings agree with an adjusted Rand index of {DATA['ari_orders']}."]],
    ["limits", "What it does not show",
     "The number of basins depends on how finely the judge groups. It is one judge model's count, on one snapshot of the board.",
     ["Only membership is measured: where a dot lies inside its basin carries no meaning, and a basin says nothing about whether its ideas work.",
      f"Of the {DATA['tree']['links']} links, {DATA['tree']['written']} are item ids that an item names in its own text. The judge found {DATA['tree']['found']} of those by reading the items, and proposed the rest."]],
    ["run", "How to reproduce it",
     "The commands are in the run.json beside each artifact: export the board, run the judge, then swarm_analyze writes the numbers.",
     ["The basins are in " + DATA["artifact"] + " on branch ali/basins, commit " + DATA["commit"] + ".",
      "The places of the dots and the links come from analysis/swarm_nested_layout.py of that study, commit " + DATA["layout_commit"] + ".",
      "The snapshot is the board of " + DATA["snapshot"] + "."]],
]

# The icon of this page's tile on /proof: a glass slab with three basins, the nearest lit.
ICON = r"""(kit, t, tilt) => {
  const a = 44, b = 38, th = 5, top = th / 2;
  const ring = (u, v, r, w, tone, n = 14) => { let s = ""; for (let i = 0; i < n; i++) { const p = i / n * 6.2832, q = (i + 1) / n * 6.2832;
    s += kit.line(kit.at(u + r * Math.cos(p), v + r * Math.sin(p), top - w), kit.at(u + r * Math.cos(q), v + r * Math.sin(q), top - w), tone === "lit" ? 1.1 : .7, tone, tone === "lit" ? 1 : .8); } return s; };
  return kit.slab(a, b, th) + ring(-14, -6, 9, 0, "plain") + ring(8, 6, 11 + .5 * Math.sin(t * .6), 0, "lit") + ring(31, -22, 6, 0, "plain", 10);
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
/* The tokens and the light of architecture.py. Dark is the hero: one lit glass slab in a dark room. Light is the same
   slab as white porcelain on a cool grey table, with a cast shadow in place of the glow. The light comes from the
   upper left in both. --wash is how strongly a basin takes the accent. */
:root {
  color-scheme: light dark;
  --paper: #eceef0; --sheet: #fbfcfc; --ink: #101820; --mute: #56636d; --faint: #606c76; --rule: #d3d9de;
  --blue: #1f43d6; --red: #cf2338;
  --glass-hi: #ffffff; --glass: #f9fafb; --glass-lo: #dfe4e8;
  --rim-a: rgba(16, 24, 32, .28); --rim-b: rgba(16, 24, 32, .58); --rim-c: rgba(16, 24, 32, .9);
  --glow: 0; --shadow: 1; --spec: 0; --bloom: .4; --core: var(--blue); --wash: .05;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #080c11; --sheet: #111922; --ink: #e9eff3; --mute: #93a1ad; --faint: #788590; --rule: #1c2630;
    --blue: #8fb1ff; --red: #ff6b7c;
    --glass-hi: #34485e; --glass: #152029; --glass-lo: #090e14;
    --rim-a: rgba(255, 255, 255, .92); --rim-b: rgba(255, 255, 255, .1); --rim-c: rgba(143, 177, 255, .45);
    --glow: 1; --shadow: 0; --spec: 1; --bloom: 1; --core: #f6f9ff; --wash: .07;
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

/* The picture, and the one control that changes it */
.stage { min-height: 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 8px 40px 0 0; }
svg#svg { width: 100%; max-height: 69vh; display: block; overflow: visible; }
svg text { font-family: inherit; fill: var(--ink); font-stretch: 106%; }
.atmo, .shade, .spec, .bloom { pointer-events: none; }
.atmo { opacity: var(--glow); }
.shade { opacity: var(--shadow); }
.spec { opacity: var(--spec); }
.bloom { opacity: var(--bloom); }
.body { fill: var(--glass-lo); stroke: var(--rim-b); stroke-width: 1; stroke-linejoin: round; }
.face { fill: url(#body) var(--sheet); }
.rim { fill: none; stroke: url(#rim) var(--ink); stroke-width: 1.7; stroke-linejoin: round; }
.ring { fill: var(--blue); fill-opacity: var(--wash); stroke: url(#fade-n) var(--ink); stroke-linejoin: round; }
.lane, .lk { fill: none; stroke: var(--ink); stroke-linecap: round; }
.lk.x { stroke: var(--blue); }
.lname { text-anchor: end; font-weight: 560; paint-order: stroke fill; stroke: var(--glass); stroke-width: 4px; stroke-linejoin: round; }
.land { fill: none; stroke: url(#fade-n) var(--ink); stroke-linejoin: round; }
.solid, .small { fill: var(--ink); }
.hollow { fill: var(--glass); stroke: var(--ink); }
.cname { text-anchor: middle; paint-order: stroke fill; stroke: var(--glass); stroke-linejoin: round; }
.cname { font-weight: 560; stroke-width: 5px; }
.cname tspan { fill: var(--mute); font-weight: 420; }
.halo { fill: var(--blue); }
.core { fill: var(--core); }
.cap { fill: var(--mute); font-weight: 500; text-anchor: middle; }
.value { font-weight: 330; letter-spacing: -.03em; text-anchor: middle; font-stretch: 100%; }
.switch { display: inline-flex; align-self: center; margin-top: 14px; border: 1px solid var(--faint); border-radius: 999px; padding: 3px; }
.switch button { padding: 8px 18px; border-radius: 999px; font-weight: 600; font-size: 15px; white-space: nowrap; transition: background .15s ease, color .15s ease; }
.switch button:hover { color: var(--blue); }
.switch button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.note { align-self: center; margin: 12px 0 0; color: var(--mute); font-size: 15px; text-align: center; max-width: 62ch; min-height: 3em; }
.key { align-self: center; display: flex; flex-wrap: wrap; justify-content: center; gap: 4px 22px; margin-top: 8px; font-size: 13px; color: var(--mute); }
.key[hidden], .key span[hidden] { display: none; }
.key span { display: inline-flex; align-items: center; gap: 7px; }
.key svg { width: 12px; height: 12px; overflow: visible; }

/* One drawn entrance */
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade { from { opacity: 0; } }
.enter .draw { stroke-dasharray: 1; animation: draw 1.1s cubic-bezier(.6, 0, .2, 1) both; }
.enter .atmo, .enter .shade, .enter .spec, .enter .face, .enter .body { animation: fade 1.3s .15s both; }
.enter #dots, .enter .scale { animation: fade .7s .7s both; }

/* The words */
.side {
  min-width: 0; min-height: 0; overflow-y: auto; scrollbar-width: none;
  padding: clamp(20px, 7vh, 96px) 0 0 40px; border-left: 1px solid var(--rule);
}
.credit { margin: 22px 0 0; font-size: 13px; color: var(--faint); max-width: 40ch; }
.credit a { color: var(--mute); text-decoration: underline; text-underline-offset: 2px; }
.credit a:hover { color: var(--blue); }
.problem { margin: 0; color: var(--mute); font-size: clamp(16px, 1.25vw, 20px); line-height: 1.3; max-width: 26ch; }
.say { margin: 14px 0 0; font-size: clamp(25px, 2.15vw, 40px); line-height: 1.14; font-weight: 300; font-stretch: 102%; letter-spacing: -.016em; max-width: 17ch; }
.say b { font-weight: 620; }
.pane { margin-top: clamp(22px, 4vh, 44px); }
.more { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--rule); }
.more button { display: flex; width: 100%; justify-content: space-between; align-items: baseline; padding: 12px 0; border-bottom: 1px solid var(--rule); font-size: 17px; font-weight: 520; transition: color .15s ease; }
.more button span { color: var(--faint); font-size: 20px; line-height: 1; }
.more button:hover { color: var(--blue); }
.dhead { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--ink); }
.dhead h2 { margin: 0; font-size: 17px; font-weight: 660; font-stretch: 114%; letter-spacing: .008em; }
.close { font-size: 13px; color: var(--mute); padding: 12px 0 12px 16px; margin: -12px 0; }
.close:hover { color: var(--ink); }
.lead { margin: 18px 0 0; font-size: clamp(17px, 1.3vw, 21px); line-height: 1.36; font-weight: 380; max-width: 30ch; }
.facts { list-style: none; margin: 18px 0 0; padding: 0; font-size: 14.5px; color: var(--mute); max-width: 40ch; overflow-wrap: anywhere; }
.facts li { padding: 8px 0; border-top: 1px solid var(--rule); }
.names { display: none; }
@media (max-width: 900px) {
  /* On a phone the order is: the problem, the finding, the picture, the depth. */
  .page { display: flex; flex-direction: column; height: auto; min-height: 0; padding: 16px 16px 40px; }
  .top { gap: 13px; padding-bottom: 12px; flex-wrap: wrap; }
  .name { font-stretch: 112%; margin-right: 0; }
  .side { display: contents; }
  .problem { order: 1; margin-top: 20px; max-width: none; }
  .credit { order: 6; }
  .say { order: 2; max-width: 22ch; }
  .stage { order: 3; margin-top: 22px; padding: 0; }
  .pane { order: 5; margin-top: 14px; }
  /* The plate carries only the counts; the names of the basins stand under the picture, in the same order. */
  .names:not([hidden]) { order: 4; display: grid; grid-template-columns: 1fr 1fr; column-gap: 20px; list-style: none; margin: 14px 0 0; padding: 0; font-size: 13px; border-top: 1px solid var(--rule); }
  .names li { display: flex; justify-content: space-between; gap: 8px; padding: 7px 0; border-bottom: 1px solid var(--rule); }
  .names span { color: var(--mute); }
  svg#svg { max-height: none; }
  .switch { display: grid; grid-template-columns: 1fr 1fr 1fr; align-self: stretch; border-radius: 24px; }
  .switch button { text-align: center; padding: 12px 4px; font-size: 14px; }
  .note { min-height: 6em; font-size: 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .enter * { animation: none !important; }
  .switch button, .more button { transition: none; }
}
</style>
</head>
<body>
<div class="page">
  <header class="top">
    <h1 class="name">Invariant</h1>
    <a href="/">Board</a>
    <a href="/architecture">Design</a>
    <a href="/proof" aria-current="page">Proof</a>
    <a href="/findings">Findings</a>
  </header>
  <div class="stage" id="stage">
    <svg id="svg" role="img"></svg>
    <div class="switch" id="switch" role="group" aria-label="Condition"></div>
    <p class="note" id="note" aria-live="polite"></p>
    <div class="key" aria-label="Key">
      <span><svg viewBox="0 0 12 12"><circle class="solid" cx="6" cy="6" r="4.6"/></svg>Result</span>
      <span><svg viewBox="0 0 12 12"><circle class="hollow" cx="6" cy="6" r="4" stroke-width="1.5"/></svg>Work</span>
      <span><svg viewBox="0 0 12 12"><circle class="small" cx="6" cy="6" r="2.4"/></svg>Idea or note</span>
      <span id="key-link" hidden><svg viewBox="0 0 12 12"><path class="lk x" d="M0 10C5 10 7 2 12 2" stroke-width="1.5"/></svg>Builds on another basin</span>
    </div>
  </div>
  <div class="side">
    <p class="problem" id="problem"></p>
    <p class="say" id="say"></p>
    <ul class="names" id="names" aria-label="The basins and their items" hidden></ul>
    <div class="pane" id="pane" aria-live="polite"></div>
    <p class="credit">After Bespoke Labs: <a href="https://bespokelabs.ai/blog/how-models-explore-ideas">How models explore ideas</a> and <a href="https://benchmarks.bespokelabs.ai/autoresearchexam/">AutoResearchExam</a>.</p>
  </div>
</div>
<script>
const C = __CONFIG__, D = C.data, L = D.layout, $ = id => document.getElementById(id);
const S = { state: 0, open: null, g: null, el: null, out: null, cur: null, from: null, goal: null, t0: 0, dur: 900, t: 0, shown: -1, dots: [], pulse: -1, pulseAt: 0, turn: 0 };
const still = matchMedia("(prefers-reduced-motion: reduce)");
const narrow = matchMedia("(max-width: 900px)");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const f = n => n.toFixed(1), h = n => n.toFixed(2), mix = (a, b, q) => a + (b - a) * q, clamp = v => Math.max(0, Math.min(1, v));
const ease = p => p < .5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2;

/* The data. Items are in the order they were posted. */
const N = L.items.length, COLS = 34, ROWS = Math.ceil(N / COLS);
const MOST = Math.max(...L.clusters.map(c => c.n));  // items in the fullest basin
const NEWEST = L.items.map((n, i) => i).slice(-40);  // what the replay loops over
/* The idea tree: a link from an item to each earlier item it builds on, and one row per basin, the basins in the
   order of their first item. */
const LINKS = L.items.flatMap((n, i) => n.p.map(p => [p, i]));
const FIRST = L.clusters.map((c, i) => L.items.findIndex(n => n.c === i));
const LANE = FIRST.map(a => FIRST.filter(b => b < a).length);

/* What each condition looks like: g, the dots have gathered into their basins (2.6 s, the first posted first);
   t, the basins are laid out as the rows of the idea tree (0.9 s). */
const LOOK = { "items": { g: 0, t: 0 }, "basins": { g: 1, t: 0 }, "tree": { g: 1, t: 1 } };

const SOFT = .32, RIM = SOFT * Math.exp(-.7);  // how far the ground around a basin slopes toward it, and how low its rim then lies

/* Geometry: the slab lives in a small 3D space around one centre (x right, y down, z toward the viewer), as in
   architecture.py. It lies back by TILT degrees, so it is seen from slightly above. u runs to its right, v toward the
   viewer and w out of its top face. The count lies flat on the screen under it. */
const RAD = Math.PI / 180, TILT = 58, PC = Math.cos(TILT * RAD), PS = Math.sin(TILT * RAD);
function geo() {
  return narrow.matches
    ? { w: 720, h: 760, cx: 360, cy: 250, a: 296, th: 20, r: 24, D: 1900, yaw: -4, lw: 1.5, fs: 17, count: 27, wide: 86, ay: 706, num: 120, fl: 27, dot: 1.4, deep: 32, gx: 48, gy: 24, lab: 196, lane: 46 }
    : { w: 1000, h: 752, cx: 500, cy: 258, a: 440, th: 22, r: 32, D: 2500, yaw: -6, lw: 1.05, fs: 14.5, wide: 104, ay: 700, num: 84, fl: 17, dot: 1.22, deep: 42, gx: 76, gy: 30, lab: 204, lane: 62 };
}
const V = { c1: 1, s1: 0, c2: 1, s2: 0, px: 0, py: 0, tx: 0, ty: 0 };  // the view: a slow sway, plus a few degrees toward the pointer
function aim(yaw, pitch) { V.c1 = Math.cos(yaw * RAD); V.s1 = Math.sin(yaw * RAD); V.c2 = Math.cos(pitch * RAD); V.s2 = Math.sin(pitch * RAD); }
const world = (u, v, w) => [u, v * PC - w * PS, v * PS + w * PC];
function proj(g, p) {  // to the screen: [x, y, scale, depth]
  const x = p[0] * V.c1 + p[2] * V.s1, z1 = p[2] * V.c1 - p[0] * V.s1;
  const y = p[1] * V.c2 - z1 * V.s2, z = z1 * V.c2 + p[1] * V.s2, k = g.D / (g.D - z);
  return [g.cx + x * k, g.cy + y * k, k, z];
}
function outline(g) {  // the rounded outline of the slab in its own plane, clockwise from the far right corner
  const pts = [], n = 6;
  [[1, -1, -90], [1, 1, 0], [-1, 1, 90], [-1, -1, 180]].forEach(([su, sv, a0]) => {
    for (let i = 0; i <= n; i++) {
      const a = (a0 + 90 * i / n) * RAD;
      pts.push([su * (g.a - g.r) + g.r * Math.cos(a), sv * (g.b - g.r) + g.r * Math.sin(a)]);
    }
  });
  return pts;
}
function hull(p) {  // the silhouette of a convex body is the convex hull of its projected points
  p = [...p].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const turn = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const half = list => {
    const out = [];
    for (const q of list) { while (out.length > 1 && turn(out[out.length - 2], out[out.length - 1], q) <= 0) out.pop(); out.push(q); }
    out.pop();
    return out;
  };
  return [...half(p), ...half(p.reverse())];
}
const disc = (p, r) => `M${f(p[0] - r)} ${f(p[1])}a${f(r)} ${f(r)} 0 1 0 ${f(2 * r)} 0a${f(r)} ${f(r)} 0 1 0 ${f(-2 * r)} 0Z`;

/* The picture is built once per layout; place() then sets everything that depends on the view and on the condition.
   Back to front: the light around the slab, its body, its top face, the relief, the rims of the basins, the dots,
   the item that the replay shows, the rim, the names, and the count. */
function build() {
  const g = S.g = geo(), svg = $("svg");
  g.b = g.a * .92; g.unit = 2 * g.a / .88;  // one unit of the layout on the slab
  const stop = (at, color, alpha) => `<stop offset="${at}" style="stop-color:${color}${alpha == null ? "" : ";stop-opacity:" + alpha}"/>`;
  const U = x => (x - .5) * g.unit, Vv = y => (y - L.wh / 2) * g.unit;
  // A basin is a bowl in the slab, deepest at its centre, and the ground around it slopes gently toward it.
  const bowl = (c, s, most, k) => ({ u: U(c.x), v: Vv(c.y), R: c.r * g.unit, d: g.deep * k * Math.sqrt(c.n / most), s: s * g.unit });
  const depth = (rings, u, v) => {
    let z = 0, soft = 0;
    for (const r of rings) { const q = ((u - r.u) ** 2 + (v - r.v) ** 2) / (r.R * r.R); if (q < 1) z = Math.min(z, -r.d * (1 - q)); soft -= SOFT * r.d * Math.exp(-.7 * q); }
    return z + soft;
  };
  const inBowl = (rings, b, k) => { const r = b.s * Math.sqrt(k + .5), a = k * 2.39996323, u = b.u + r * Math.cos(a), v = b.v + r * Math.sin(a); return [u, v, depth(rings, u, v)]; };
  S.rings = L.clusters.map(c => bowl(c, L.s, MOST, 1));
  S.tl = -g.a + g.lab;  // the tree: where its rows begin, right of the names, and how far back or forward each row lies
  S.lv = LANE.map(k => (k - (LANE.length - 1) / 2) * g.lane);
  // Each board dot has two places: in the list of the board, row by row in the order of posting, and in its basin,
  // where the dots are packed outward from the centre in the same order.
  S.dots = L.items.map((n, i) => {
    const [u1, v1, w1] = inBowl(S.rings, S.rings[n.c], n.k);
    return { kind: n.kind, i, u1, v1, w1, ut: S.tl + (g.a - g.r - S.tl) * i / (N - 1), vt: S.lv[n.c],
      u0: (i % COLS - (COLS - 1) / 2) * g.unit * .0245, v0: (Math.floor(i / COLS) - (ROWS - 1) / 2) * g.unit * .046 };
  });
  // The relief: lines across the slab, from the back to the front, that dip where a basin lies.
  const eu = g.a - g.r * .6, ev = g.b - g.r * .6;
  S.land = Array.from({ length: g.gy }, (_, j) => {
    const v = -ev + 2 * ev * j / (g.gy - 1), us = Array.from({ length: g.gx }, (_, i) => -eu + 2 * eu * i / (g.gx - 1));
    return { v, us, zb: us.map(u => depth(S.rings, u, v)) };
  });
  svg.setAttribute("viewBox", `0 0 ${g.w} ${g.h}`);
  svg.innerHTML = "<defs>" +
    `<radialGradient id="body" cx=".3" cy=".16" r="1.05">${stop(0, "var(--glass-hi)")}${stop(.5, "var(--glass)")}${stop(1, "var(--glass-lo)")}</radialGradient>` +
    `<linearGradient id="rim" x1=".06" y1="0" x2=".94" y2="1">${stop(0, "var(--rim-a)")}${stop(.56, "var(--rim-b)")}${stop(1, "var(--rim-c)")}</linearGradient>` +
    `<radialGradient id="atmo">${stop(.42, "var(--blue)", .24)}${stop(.7, "var(--blue)", .07)}${stop(1, "var(--blue)", 0)}</radialGradient>` +
    `<radialGradient id="shade">${stop(.55, "var(--ink)", .2)}${stop(1, "var(--ink)", 0)}</radialGradient>` +
    `<radialGradient id="spec">${stop(0, "#fff", .2)}${stop(1, "#fff", 0)}</radialGradient>` +
    `<linearGradient id="fade-n" gradientUnits="userSpaceOnUse">${stop(0, "var(--ink)", .38)}${stop(1, "var(--ink)", .95)}</linearGradient></defs>` +
    `<g class="atmo"><ellipse id="glow" cx="${g.cx}" cy="${f(g.cy + g.b * .08)}" rx="${f(g.a * 1.7)}" ry="${f(g.b * PC * 2.1)}" fill="url(#atmo)"/></g>` +
    `<g class="shade"><ellipse cx="${f(g.cx + g.a * .07)}" cy="${f(g.cy + g.b * PC * .22 + g.th)}" rx="${f(g.a * 1.3)}" ry="${f(g.b * PC * 1.36)}" fill="url(#shade)"/></g>` +
    `<path class="body" id="side"/><path class="face" id="face"/>` +
    `<g class="spec"><ellipse id="shine" rx="${f(g.a * .5)}" ry="${f(g.b * PC * .4)}" fill="url(#spec)"/></g>` +
    `<path class="land" id="land" stroke-width="${h(g.lw * .95)}" opacity="0"/>` +
    `<path class="lane" id="lanes" stroke-width="${h(g.lw * .8)}" opacity="0"/>` +
    `<path class="ring" id="ring" stroke-width="${h(g.lw)}" opacity="0"/>` +
    `<path class="lk" id="lk" stroke-width="${h(g.lw * .75)}" opacity="0"/><path class="lk x" id="lkx" stroke-width="${h(g.lw * .95)}" opacity="0"/>` +
    `<g id="dots"><path class="small" id="small"/><path class="hollow" id="hollow" stroke-width="${h(g.lw * 1.4)}"/><path class="solid" id="solid"/></g>` +
    `<g class="bloom"><circle class="halo" id="ph" r="${f(12 * g.dot)}" opacity="0"/></g><circle class="core" id="pc" r="${f(4.4 * g.dot)}" opacity="0"/>` +
    `<path class="rim draw" id="rim" pathLength="1"/>` +
    L.clusters.map((c, i) => g.count  // on a phone only the count stands on the plate, and the names are listed under the picture
      ? `<text class="cname" id="cn-${i}" font-size="${g.count}" opacity="0">${c.n}</text>`
      : `<text class="cname" id="cn-${i}" font-size="${g.fs}" font-stretch="${g.wide}%" opacity="0">${esc(c.name)}<tspan dx="6">${c.n}</tspan></text>`).join("") +
    L.clusters.map((c, i) => `<text class="lname" id="ln-${i}" font-size="${f(g.fs * (narrow.matches ? .8 : .9))}" font-stretch="${g.wide}%" opacity="0">${esc(c.name)}</text>`).join("") +
    `<g class="scale"><text class="value" id="value" x="${g.cx}" y="${f(g.ay - g.num * .2)}" font-size="${g.num}"></text>` +
    `<text class="cap" id="cap" x="${g.cx}" y="${f(g.ay + g.fl * .7)}" font-size="${g.fl}"></text></g>`;
  S.el = {};
  ["glow", "side", "face", "shine", "land", "lanes", "lk", "lkx", "ring", "dots", "small", "hollow", "solid", "ph", "pc", "rim", "fade-n", "value", "cap"].forEach(id => { S.el[id] = $(id); });
  S.el.cn = L.clusters.map((c, i) => $("cn-" + i));
  S.el.ln = L.clusters.map((c, i) => $("ln-" + i));
  S.out = outline(g);
  S.shown = -1;
}

function place(t) {
  const g = S.g, c = S.cur, E = S.el, top = g.th / 2;
  if (!E || !c) return;
  const at = (u, v, w) => proj(g, world(u, v, w)), set = (el, o) => { for (const k in o) el.setAttribute(k, o[k]); };
  const path = p => "M" + p.map(q => f(q[0]) + " " + f(q[1])).join("L") + "Z";
  const circle = (u, v, r, w) => { const pts = []; for (let i = 0; i < 36; i++) { const a = i / 36 * 2 * Math.PI; pts.push(at(u + r * Math.cos(a), v + r * Math.sin(a), w)); } return path(pts); };

  // The slab: its top face, and the silhouette of its whole body, of which the face covers all but the near edge.
  const up = S.out.map(([u, v]) => at(u, v, top)), down = S.out.map(([u, v]) => at(u, v, -top));
  const face = path(up);
  set(E.face, { d: face }); set(E.rim, { d: face }); set(E.side, { d: path(hull([...up, ...down])) });
  const shine = at(-g.a * .36, -g.b * .34, top);
  set(E.shine, { cx: f(shine[0]), cy: f(shine[1]) });
  const far = at(0, -g.b, top), near = at(0, g.b, top);  // lines are faint at the back and full in front
  set(E["fade-n"], { x1: f(far[0]), y1: f(far[1]), x2: f(near[0]), y2: f(near[1]) });
  E.glow.setAttribute("opacity", h(.45 + .4 * c.g));

  // The relief, kept faint: it is flat while the dots lie in the list and dips as they gather into their basins.
  // For the tree the slab lies flat again and the basins become rows.
  const here = ease(clamp(c.g * 2 - 1));  // the basins come once most dots have arrived
  const tt = ease(c.t), flat = 1 - tt, board = here * flat;
  let land = "";
  for (const row of S.land) for (let i = 0; i < row.us.length; i++) {
    const p = at(row.us[i], row.v, top + here * flat * row.zb[i]);
    land += (i ? "L" : "M") + f(p[0]) + " " + f(p[1]);
  }
  set(E.land, { d: land, opacity: h((.24 + .3 * here) * (1 - .75 * tt)) });
  set(E.ring, { d: S.rings.map(r => circle(r.u, r.v, r.R, top - RIM * r.d * here)).join(""), opacity: h(board) });
  if (tt > .005) set(E.lanes, { d: S.lv.map(v => { const a = at(S.tl - 8, v, top), b = at(g.a - g.r + 8, v, top); return `M${f(a[0])} ${f(a[1])}L${f(b[0])} ${f(b[1])}`; }).join("") });
  E.lanes.setAttribute("opacity", h(.4 * tt));

  // The board's dots: each moves from its place in the list to its place in its basin, the first posted first, in a
  // low arc.
  {
    let small = "", hollow = "", solid = "";
    S.dots.forEach(o => {
      const q = ease(clamp((c.g - .45 * o.i / N) / .55));
      o.u = mix(mix(o.u0, o.u1, q), o.ut, tt); o.v = mix(mix(o.v0, o.v1, q), o.vt, tt);
      const p = at(o.u, o.v, top + o.w1 * q * flat + 46 * Math.sin(Math.PI * q) + 34 * Math.sin(Math.PI * tt));
      o.x = p[0]; o.y = p[1];
      if (o.kind === "result") solid += disc(p, 3.5 * g.dot * p[2]); else if (o.kind === "work") hollow += disc(p, 2.9 * g.dot * p[2]); else small += disc(p, 1.9 * g.dot * p[2]);
    });
    set(E.small, { d: small }); set(E.hollow, { d: hollow }); set(E.solid, { d: solid });
  }
  // The links of the tree, drawn between the dots where they are now: an arc inside a row, an S between two rows.
  const on = ease(clamp(c.t * 2 - 1));
  if (on > .005) {
    let same = "", cross = "";
    const pt = (u, v) => { const p = at(u, v, top); return f(p[0]) + " " + f(p[1]); };
    for (const [a, b] of LINKS) {
      const p = S.dots[a], n = S.dots[b], du = n.u - p.u;
      if (L.items[a].c === L.items[b].c) same += `M${pt(p.u, p.v)}Q${pt((p.u + n.u) / 2, p.v - Math.min(g.lane * .8, 12 + Math.abs(du) * .3))} ${pt(n.u, n.v)}`;
      else cross += `M${pt(p.u, p.v)}C${pt(p.u + du * .5, p.v)} ${pt(n.u - du * .5, n.v)} ${pt(n.u, n.v)}`;
    }
    set(E.lk, { d: same }); set(E.lkx, { d: cross });
  }
  E.lk.setAttribute("opacity", h(.26 * on)); E.lkx.setAttribute("opacity", h(.5 * on));

  // The replay: one real item of the newest 40 at a time lights up where it lies.
  if (S.pulse >= 0) {
    const o = S.dots[NEWEST[S.pulse]], age = t - S.pulseAt, a = clamp(age / .35) * clamp((2.1 - age) / .6);
    set(E.pc, { cx: f(o.x), cy: f(o.y), opacity: h(a) }); set(E.ph, { cx: f(o.x), cy: f(o.y), opacity: h(.3 * a) });
  } else { E.pc.setAttribute("opacity", 0); E.ph.setAttribute("opacity", 0); }

  // The names stand upright, each in front of its basin.
  S.rings.forEach((r, i) => { const p = at(r.u, r.v + r.R, top); set(E.cn[i], { x: f(p[0]), y: f(p[1] + (g.count || g.fs) * 1.12), opacity: h(board) }); });
  S.lv.forEach((v, i) => { const p = at(S.tl - 18, v, top); set(E.ln[i], { x: f(p[0]), y: f(p[1] + g.fs * .3), opacity: h(tt) }); });

  // Under the slab: the count of what the picture shows now (items, basins, items of the tree that build on two or more).
  const level = c.t > .5 ? 2 : c.g > .5 ? 1 : 0;
  if (level !== S.shown) { S.shown = level; E.value.textContent = [D.items, D.clusters, D.tree.merge][level]; E.cap.textContent = D.states[level].unit; }
}

/* Motion that is always on: the view sways by a few degrees and leans toward the mouse, and at rest one real item
   after another lights up. With reduced motion the page shows one still frame and a condition changes at once. */
function frame(now) {
  const t = S.t = now / 1000;
  V.px += (V.tx - V.px) * .06;
  V.py += (V.ty - V.py) * .06;
  aim(S.g.yaw + 6 * Math.sin(t * .13) + 5 * V.px, 2.5 * Math.sin(t * .09) - 2.5 * V.py);
  if (S.from) {
    const p = Math.min(1, (now - S.t0) / S.dur), e = ease(Math.min(1, (now - S.t0) / 900));
    for (const k in S.goal) S.cur[k] = mix(S.from[k], S.goal[k], k === "g" ? p : e);
    if (p >= 1) { S.from = null; S.pulseAt = t - 1.5; S.pulse = -1; }
  } else if (t - S.pulseAt > 2.5) { S.pulseAt = t; S.pulse = S.turn = (S.turn + 1) % NEWEST.length; }
  place(t);
  requestAnimationFrame(frame);
}

const bold = s => esc(s).replace(/(?<![\w.-])(\d+(?:[.,]\d+)*(?: ?%)?)/g, "<b>$1</b>");  // the numbers of a line

/* The condition and the open panel are one value in the address: #<condition>, #<panel> or #<condition>/<panel>. */
function choose(i, instant) {
  const st = D.states[i];
  S.state = i; S.pulse = -1;
  S.goal = { ...LOOK[st.key] };
  if (instant || still.matches || !S.cur) { S.cur = { ...S.goal }; S.from = null; }
  else { S.from = { ...S.cur }; S.t0 = performance.now(); S.dur = S.goal.g !== S.cur.g ? 2600 : 900; }
  $("svg").setAttribute("aria-label", `Dots on a glass slab, shown as ${st.name}: ${st.note}`);
  $("note").textContent = st.note;
  $("problem").textContent = st.problem || C.problem;
  $("say").innerHTML = bold(st.line || C.line);
  $("key-link").hidden = st.key !== "tree";
  $("names").hidden = st.key !== "basins";
  $("switch").querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-pressed", k === i));
  place(S.t);
}
function pane() {
  const p = C.panels.find(p => p[0] === S.open);
  $("pane").innerHTML = p
    ? `<div class="dhead"><h2>${esc(p[1])}</h2><button class="close" data-open="">Close</button></div><p class="lead">${esc(p[2])}</p>` +
      `<ul class="facts">${p[3].map(x => `<li>${esc(x)}</li>`).join("")}</ul>`
    : `<ul class="more">${C.panels.map(p => `<li><button data-open="${p[0]}">${esc(p[1])}<span aria-hidden="true">›</span></button></li>`).join("")}</ul>`;
}
function address(push) {
  const parts = [S.state ? D.states[S.state].key : "", S.open || ""].filter(Boolean);
  const url = parts.length ? "#" + parts.join("/") : location.pathname;
  push ? history.pushState(null, "", url) : history.replaceState(null, "", url);
}
function fromHash(first) {
  const parts = decodeURIComponent(location.hash.slice(1)).split("/");
  const i = Math.max(0, D.states.findIndex(s => parts.includes(s.key))), p = C.panels.find(p => parts.includes(p[0]));
  if (first === true || i !== S.state) choose(i, first === true);
  S.open = p ? p[0] : null;
  pane();
}
function open(key) {  // a panel opens in the side column; the keyboard focus follows it there and back
  const was = S.open;
  S.open = key || null;
  address(true);
  pane();
  const to = $("pane").querySelector(key ? ".close" : `[data-open="${was}"]`);
  if (to) to.focus({ preventScroll: true });
}

document.addEventListener("click", e => {
  const s = e.target.closest("[data-state]"), o = e.target.closest("[data-open]");
  if (s) { choose(Number(s.dataset.state)); address(false); }
  if (o) open(o.dataset.open);
});
document.addEventListener("keydown", e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "Escape" && S.open) open("");
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
    const inside = document.activeElement && document.activeElement.closest("#switch");
    choose((S.state + (e.key === "ArrowRight" ? 1 : D.states.length - 1)) % D.states.length);
    address(false);
    if (inside) $("switch").children[S.state].focus();
  }
});
addEventListener("hashchange", fromHash);
addEventListener("popstate", fromHash);
narrow.addEventListener("change", () => { build(); place(S.t); });
const stage = $("stage");  // the view leans a few degrees toward a mouse, and settles back
stage.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse" || still.matches) return;
  const b = stage.getBoundingClientRect();
  V.tx = 2 * (e.clientX - b.left) / b.width - 1;
  V.ty = 2 * (e.clientY - b.top) / b.height - 1;
});
stage.addEventListener("pointerleave", () => { V.tx = V.ty = 0; });

$("names").innerHTML = L.clusters.map(c => `<li>${esc(c.name)}<span>${c.n}</span></li>`).join("");
$("switch").innerHTML = D.states.map((s, i) => `<button data-state="${i}" aria-pressed="false">${esc(s.name)}</button>`).join("");
build();
aim(S.g.yaw, 0);  // the still frame
fromHash(true);
if (!still.matches) {
  $("svg").classList.add("enter");
  setTimeout(() => $("svg").classList.remove("enter"), 2200);
  requestAnimationFrame(frame);
}
</script>
</body>
</html>
""".replace("__TITLE__", TITLE).replace("__CONFIG__", json.dumps({"problem": PROBLEM, "line": LINE, "data": DATA, "panels": PANELS}))
