In the last hour, the accuracy batch posted a misleading result, and I fixed the step that let it happen.

**What went wrong.** The 4 accuracy cells ran correctly in about 3 minutes, but result-d8d83f has two flaws:
1. **Unlabelled interval levels.** The subject split uses a 90% interval, which was set by hand in `cells/accuracy.json` as SPEC requirement 3 allows. The other three splits use 95%. The post lists all of them together without saying which is which, so anyone comparing intervals across splits would read them wrong.
2. **No verdict on the prediction.** SPEC has a rule for when a group counts as different from the overall gap, and a prediction with a stated refutation. The post doesn't apply either. Applied to the committed numbers (overall gap 0.106), the prediction comes out half right:
   - **Confirmed:** the cued base's longest-answer quartile has the largest gap, 0.256 [0.157, 0.355]. That interval excludes 0.106.
   - **Refuted:** "flat across subjects" fails on algebra, 0.0565 [0.018, 0.097] at 90%.

**The improvement.** A new script, `studies/gapmap/analysis/summarize.py <batch>-NN`, reads a finished batch's committed cell files and prints the text to post on the board. Each split line states its own interval level, and any group whose interval excludes the overall point is marked with `*`. It only formats numbers the jobs already produced, so SPEC requirement 1 (nothing computed on a laptop) still holds. I ran it on `accuracy-01` and the output matches the result files.

I also:
- updated `studies/gapmap/README.md` so the run steps close a work item with this script's output, and recorded the accuracy verdict under Numbers;
- committed and pushed it to `dana/gapmap` (43dde96);
- commented a correction on result-d8d83f so teammates see the interval levels and the verdict.

Two smaller problems I left alone:
- **Hand edits can be lost.** Running `make_cells.py` again overwrites the hand-set subject settings. Putting per-batch overrides in `queue.json` would prevent that.
- **Launches are serial.** The subject cell ran alone for a minute before the other three started. Launching all four at once would save that minute per batch.