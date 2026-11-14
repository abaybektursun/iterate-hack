# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=5", "modal>=1.4"]
# ///
"""Download a paper or post, then add specific findings from it to the team's past.dev memory.

  uv run tools/paper.py fetch 2401.12345                                 arXiv: PDF, title and date
  uv run tools/paper.py fetch <url> --title "<title>" --date YYYY-MM-DD   any other PDF or web page
  uv run tools/paper.py add <paper-id> --where "Table 3, p. 7" --quote "<exact words>" "<finding>"

fetch writes papers/<paper-id>.txt, with [page N] markers, and papers/<paper-id>.json.
Read the whole .txt, appendix included, before adding findings.
add checks that the quote appears in the text, sends the finding to past.dev as one data point dated
at the paper's date, and waits until past.dev has processed it.
"""
import argparse
import hashlib
import html
import io
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import events

PAPERS = Path(__file__).resolve().parent.parent / "papers"
MIN_QUOTE_CHARS = 30


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "iterate-invariant"})) as r:
        return r.read(), r.headers.get_content_type()


def pdf_text(data):
    from pypdf import PdfReader

    pages = PdfReader(io.BytesIO(data)).pages
    return "".join(f"\n\n[page {n}]\n{page.extract_text()}" for n, page in enumerate(pages, 1))


def html_text(data):
    text = re.sub(r"(?is)<(script|style).*?</\1>", "", data.decode("utf-8", "replace"))
    text = re.sub(r"(?i)<(br|/p|/div|/h\d|/li|/tr)[^>]*>", "\n", text)
    return html.unescape(re.sub(r"<[^>]+>", "", text))


def normalized(text):
    return re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKC", text).lower())


def fetch(args):
    if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", args.source):
        atom = ET.fromstring(get(f"https://export.arxiv.org/api/query?id_list={args.source}")[0])
        entry = atom.find("{http://www.w3.org/2005/Atom}entry")
        title = " ".join(entry.findtext("{http://www.w3.org/2005/Atom}title").split())
        date = entry.findtext("{http://www.w3.org/2005/Atom}published")[:10]
        paper_id, url = f"arxiv-{args.source}", f"https://arxiv.org/abs/{args.source}"
        text = pdf_text(get(f"https://arxiv.org/pdf/{args.source}")[0])
    else:
        assert args.title and args.date, "a URL needs --title and --date"
        title, date, url = args.title, args.date, args.source
        paper_id = "web-" + hashlib.sha256(url.encode()).hexdigest()[:10]
        data, kind = get(url)
        text = pdf_text(data) if kind == "application/pdf" else html_text(data)

    PAPERS.mkdir(exist_ok=True)
    (PAPERS / f"{paper_id}.txt").write_text(text)
    (PAPERS / f"{paper_id}.json").write_text(json.dumps({"title": title, "date": date, "url": url}))
    print(f"{paper_id}: {title} ({date}), {text.count('[page ')} pages, {len(text.splitlines())} lines")
    print(f"read all of papers/{paper_id}.txt, appendix included, before adding findings")


def add(args):
    from past import call

    meta = json.loads((PAPERS / f"{args.paper_id}.json").read_text())
    quote = normalized(args.quote)
    assert len(quote) >= MIN_QUOTE_CHARS, f"quote too short: give at least {MIN_QUOTE_CHARS} letters and digits"
    assert quote in normalized((PAPERS / f"{args.paper_id}.txt").read_text()), "quote not found in the paper text"

    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout
    who = email.strip().split("@")[0]
    receipt = call("POST", "ingest", {
        "id": f"{args.paper_id}:{hashlib.sha256((args.where + args.finding).encode()).hexdigest()[:10]}",
        "label": f"{meta['title']}, {args.where}",
        "content": f"{meta['title']} ({meta['date']}, {meta['url']})\n{args.where}: {args.finding}\nQuote: \"{args.quote}\"",
        "timestamp": f"{meta['date']}T00:00:00Z",
        "metadata": {"paper": args.paper_id, "where": args.where, "who": who},
    })
    while receipt["status"] != "completed":
        time.sleep(3)
        receipt = call("GET", f"ingest/{receipt['ingestionId']}")
        assert receipt["status"] != "failed", receipt["failure"]
    print("added")


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
commands = parser.add_subparsers(required=True)
p = commands.add_parser("fetch")
p.add_argument("source", help="arXiv id or URL")
p.add_argument("--title")
p.add_argument("--date", help="YYYY-MM-DD")
p.set_defaults(run=fetch)
p = commands.add_parser("add")
p.add_argument("paper_id")
p.add_argument("--where", required=True, help='section, table or page, e.g. "Appendix C, Table 9"')
p.add_argument("--quote", required=True, help="exact words from the paper that support the finding")
p.add_argument("finding", help="one specific result: setup, numbers, and what it means for us")
p.set_defaults(run=add)
args = parser.parse_args()
email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout
events.log("paper", sys.argv[1:], email.strip().split("@")[0])
args.run(args)
