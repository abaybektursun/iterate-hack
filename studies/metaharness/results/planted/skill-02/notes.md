Window 2 was started twice. The second review deleted `prep/make_cells.py` and `cells/` (every cell takes its settings
from `queue.json`, no hand edits). The worker's first start of window 2 stopped when it called the deleted script,
before it posted or launched anything. The worker now takes the cells from `queue.json` when the script is gone and
types no setting by hand. Window 2, review 3 and window 3 then ran once. From window 2 on, the `subject` table has the
queue's 95% interval and 4 digits, so it differs from the reference table (which has the hand settings of that
window) in its interval ends and rounding only: `answers exact` is 3 of 4, the point estimates are the same.
