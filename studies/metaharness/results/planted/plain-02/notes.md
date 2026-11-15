Windows 2 and 3 and review 3 of this run were run twice. The second review rewrote the README's launch block to three
lines, one of them `git commit studies/gapmap/cells/<batch>.json && git push`. The worker ran that line as a launch
line, it exited non-zero ("nothing to commit"), and windows 2 and 3 ran no job; review 3 then reviewed an empty window.
That was the worker's error. The worker now skips `git` lines of the block. The arena was put back to the end of
review 2 (work branch at commit 73e149f, the 11 board rows and 10 events written afterwards removed), and window 2,
review 3 and window 3 were run again. This folder holds the second run only.
