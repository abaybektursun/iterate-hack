"""Inputs of the audit of the transcribed fresh2026 statements (specs/SPEC_freshaudit.md): fetches the official HMMT
solutions PDFs again, checks their sha256, renders every page to a PNG and to its text layer, and writes the batches that
the blind second transcribers get (PDF pages and problem numbers only, no statement of the data file). No model.

    python3 -m studies.rlneurons.prep.freshaudit_prep --out runs/freshaudit

Needs curl, pdftoppm and pdftotext. The PDFs are untrusted data and are not committed: each goes into its own directory
under <out>/pdf/, nothing is run from there. Writes <out>/sources.json (url, sha256, pages), <out>/pages/<source>/p-NN.png
and tNN.txt, <out>/batches/<batch>.json. Fail loud.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
import re
import subprocess

STUDY = pathlib.Path(__file__).resolve().parents[1]
FRESH = STUDY / "data" / "fresh"
URL = "https://hmmt-archive.s3.amazonaws.com/tournaments/2026/{}/solutions.pdf"
# the five transcribed sources (sha256 in data/fresh/transcribed_v1/sources.json) and the three control PDFs: the official
# files of the HMMT February 2026 individual rounds, whose problems the data file has from MathArena/hmmt_feb_2026
PATHS = {"hmmt_feb2026_guts": "feb/guts", "hmmt_nov2026_gen": "nov/gen", "hmmt_nov2026_thm": "nov/thm", "hmmt_nov2026_team": "nov/team",
         "hmmt_nov2026_guts": "nov/guts", "hmmt_feb2026_algnt": "feb/algnt", "hmmt_feb2026_comb": "feb/comb", "hmmt_feb2026_geo": "feb/geo"}
CONTROL_ROUNDS = ("hmmt_feb2026_algnt", "hmmt_feb2026_comb", "hmmt_feb2026_geo")       # MathArena index 1-10, 11-20, 21-30
N_CONTROL, SEED, BATCH, DPI = 15, 0, 7, 110


def control_ids(data: list) -> list:
    """15 of the kept hmmt_feb2026 problems of the individual rounds (MathArena index 1 to 30), drawn with a fixed seed."""
    ids = sorted(int(x["source_id"]) for x in data if x["source"] == "hmmt_feb2026" and int(x["source_id"]) <= 30)
    return sorted(random.Random(SEED).sample(ids, N_CONTROL))


def wanted(data: list) -> dict:
    """{pdf source: [(unique_id of the data file, problem number in the PDF)]}"""
    out = {s: [(x["unique_id"], int(x["source_id"])) for x in data if x["source"] == s] for s in PATHS if s not in CONTROL_ROUNDS}
    for i in control_ids(data):
        out.setdefault(CONTROL_ROUNDS[(i - 1) // 10], []).append((f"hmmt_feb2026/{i}", (i - 1) % 10 + 1))
    return out


def fetch(src: str, out: pathlib.Path) -> dict:
    d = out / "pdf" / src
    d.mkdir(parents=True, exist_ok=False)
    url, pdf = URL.format(PATHS[src]), d / "solutions.pdf"
    subprocess.run(["curl", "-sS", "-f", "-L", "-o", str(pdf), url], check=True)
    pages = out / "pages" / src
    pages.mkdir(parents=True)
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", str(pdf), str(pages / "p")], check=True)
    n = len(list(pages.glob("p-*.png")))
    for p in range(1, n + 1):
        subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), str(pdf), str(pages / f"t{p:02d}.txt")], check=True)
    return {"url": url, "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pages": n}


def page_of(src: str, numbers: list, out: pathlib.Path, n_pages: int) -> dict:
    """The page on which each problem starts: the first page, not before the previous problem's, with a line `N.` at the margin."""
    texts = {p: (out / "pages" / src / f"t{p:02d}.txt").read_text() for p in range(1, n_pages + 1)}
    found, start = {}, 1
    for num in range(1, max(numbers) + 1):
        hit = [p for p in range(start, n_pages + 1) if re.search(rf"^ {{0,3}}{num}\. ", texts[p], re.M)]
        assert hit, (src, num, "problem number not found in the text layer")
        found[num], start = hit[0], hit[0]
    return {num: found[num] for num in numbers}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = pathlib.Path(ap.parse_args().out)
    data = json.loads((FRESH / "fresh2026_v1.json").read_text())
    recorded = json.loads((FRESH / "transcribed_v1" / "sources.json").read_text())
    sources, want = {}, wanted(data)
    (out / "batches").mkdir(parents=True, exist_ok=False)
    for src in PATHS:
        s = sources[src] = fetch(src, out)
        if src in recorded:
            assert s["url"] == recorded[src]["url"] and s["sha256"] == recorded[src]["sha256"], (src, "the PDF is not the file the prep step transcribed")
        s["same_file_as_transcribed_v1"] = src in recorded or None
        pages = page_of(src, [n for _, n in want[src]], out, s["pages"])
        for b in range(0, len(want[src]), BATCH):
            part = want[src][b:b + BATCH]
            first, last = pages[part[0][1]], min(pages[part[-1][1]] + 1, s["pages"])
            (out / "batches" / f"{src}_{b // BATCH + 1}.json").write_text(json.dumps(
                {"source": src, "numbers": [n for _, n in part], "start_page": {n: pages[n] for _, n in part},
                 "pages": list(range(first, last + 1)), "dir": str((out / "pages" / src).resolve())}, indent=1) + "\n")
    (out / "sources.json").write_text(json.dumps(sources, indent=1) + "\n")
    (out / "wanted.json").write_text(json.dumps(want, indent=1) + "\n")
    print(json.dumps(sources, indent=1), "\nbatches:", len(list((out / "batches").glob("*.json"))))


if __name__ == "__main__":
    main()
