"""Search the web and read pages with Exa's HTTP API (https://docs.exa.ai). Uses your own EXA_API_KEY.

Usage:
  python3 tools/exa.py search "<description of the page you want>" [--n 5] [--since YYYY-MM-DD] [--domain arxiv.org]
  python3 tools/exa.py fetch <url> [<url> ...]

search prints each result's title, URL, date and highlights. fetch prints the full text of each page.
"""
import argparse
import json
import os
import subprocess
import urllib.request


def api_key():
    """The key from this process's environment, or from the shell profile when the agent started before it was set."""
    key = os.environ.get("EXA_API_KEY") or subprocess.run(
        [os.environ["SHELL"], "-ic", 'printf %s "$EXA_API_KEY"'], capture_output=True, text=True).stdout
    if not key:
        raise SystemExit("EXA_API_KEY is not set in this shell or in your shell profile: see README section 8.")
    return key


def call(endpoint, body):
    request = urllib.request.Request(
        f"https://api.exa.ai/{endpoint}", json.dumps(body).encode(),
        {"x-api-key": api_key(), "content-type": "application/json", "user-agent": "exa.py"})
    return json.load(urllib.request.urlopen(request))


parser = argparse.ArgumentParser()
commands = parser.add_subparsers(dest="command", required=True)
search = commands.add_parser("search")
search.add_argument("query")
search.add_argument("--n", type=int, default=5, help="number of results")
search.add_argument("--since", help="only pages published on or after this date, YYYY-MM-DD")
search.add_argument("--domain", action="append", help="only this domain; repeat for several")
fetch = commands.add_parser("fetch")
fetch.add_argument("urls", nargs="+")
args = parser.parse_args()

if args.command == "search":
    body = {"query": args.query, "numResults": args.n, "contents": {"highlights": True}}
    if args.since:
        body["startPublishedDate"] = args.since
    if args.domain:
        body["includeDomains"] = args.domain
    page = call("search", body)
    for result in page["results"]:
        print(f"{result.get('publishedDate', '')[:10] or 'no date   '}  {result['title']}\n  {result['url']}")
        for highlight in result["highlights"]:
            print("  | " + " ".join(highlight.split()))
        print()
else:
    page = call("contents", {"urls": args.urls, "text": True})
    for result in page["results"]:
        print(f"# {result['title']}\n{result['url']}\n\n{result['text']}\n")
print(f"[{len(page['results'])} results, {page['costDollars']['total']} USD]")
