"""
diagnose_petrojam.py — work out WHY petrojam.com is refusing this machine.

This reads the error. It does not try to get around it.

Every request below sends the same honest EVLabUWI User-Agent that the real
updater sends. Nothing here pretends to be a browser, rotates an address, or
retries in the hope of slipping through. The point is to tell three
possibilities apart, because they have completely different remedies:

  1. The whole site refuses this client
       -> an edge filter is rejecting non-browser clients generally.
          Remedy: ask Petrojam for access or for the data directly.

  2. Only some paths refuse it
       -> a specific rule. Remedy: ask, quoting the exact path.

  3. It works here but not on a schedule
       -> the block is rate-based or address-based, likely from earlier
          development loops. Remedy: ask, and explain the cadence.

Run:
    python scripts/diagnose_petrojam.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import polite_fetch

TARGETS = [
    ("https://www.petrojam.com/robots.txt", "robots.txt"),
    ("https://www.petrojam.com/", "home page"),
    ("https://www.petrojam.com/price/", "price listing (what we need)"),
    ("https://www.petrojam.com/sitemap_index.xml", "sitemap"),
]

# Header names that identify the product doing the blocking. Knowing which one
# it is tells Petrojam's IT staff exactly which control to look at.
WAF_HEADERS = [
    "cf-ray", "cf-cache-status", "server", "x-sucuri-id", "x-sucuri-cache",
    "x-powered-by", "x-cache", "x-akamai-transformed", "retry-after",
]


def main() -> None:
    print("Petrojam access diagnosis")
    print(f"User-Agent sent: {polite_fetch.USER_AGENT}")
    print()
    print("Nothing here disguises the client. If the site refuses an honest")
    print("request, that is the finding, not a problem to be worked around.")
    print()

    session = polite_fetch._get_session()
    results = []

    for url, label in TARGETS:
        try:
            r = session.get(url, timeout=15, allow_redirects=True)
        except Exception as e:
            print(f"  {label:30} ERROR {type(e).__name__}: {e}")
            results.append((label, None))
            continue

        results.append((label, r.status_code))
        print(f"  {label:30} HTTP {r.status_code}  ({len(r.content):,} bytes)")

        seen = {h: r.headers[h] for h in WAF_HEADERS if h in r.headers}
        for h, v in seen.items():
            print(f"      {h}: {v}")

        if r.status_code >= 400:
            snippet = " ".join(r.text.split())[:180]
            if snippet:
                print(f"      body: {snippet}")
        print()

    codes = [c for _, c in results if c is not None]
    blocked = [lbl for lbl, c in results if c in (401, 403, 429)]
    ok = [lbl for lbl, c in results if c and c < 400]

    print("-" * 62)
    if not codes:
        print("VERDICT: no responses at all. Check your internet connection")
        print("         before drawing any conclusion about Petrojam.")
    elif len(blocked) == len(results):
        print("VERDICT: the whole site refuses this client.")
        print()
        print("This is an edge filter rejecting requests that do not look like")
        print("a browser. It is not a robots.txt rule: Petrojam's robots.txt")
        print("says 'User-agent: * / Disallow:', which permits everything.")
        print()
        print("Automated collection is not available on these terms. The way")
        print("to change that is to ask Petrojam, not to disguise the client.")
        print("See the note printed below.")
    elif blocked:
        print(f"VERDICT: mixed. Refused: {blocked}. Allowed: {ok}.")
        print("A specific rule covers some paths. Quote the exact refused path")
        print("when you contact them.")
    else:
        print("VERDICT: everything responded. The earlier 403 was probably")
        print("         temporary or rate-based. Re-run the updater.")

    print()
    print("=" * 62)
    print("WHO TO ASK")
    print("=" * 62)
    print("""
Petrojam is a state-owned public body, and the prices are already published.
Asking is a normal request, not a favour, and you have two routes:

1. Press / general enquiry:  pr@petrojam.com   (876) 923-8611-5
   Short email. Say who you are, that this is a UWI Mona physics research
   project supervised by Dr Louis-Ray Harris, that you need the weekly
   reference price series, and ask whether they publish a machine-readable
   feed or can send the series periodically. Mention you are requesting ONE
   page once a week and that you would rather be given access than work
   around a filter.

2. Access to Information Act request:
   https://www.petrojam.com/contact-us/request-under-ati-act/
   Slower and more formal, but it is a statutory route to data held by a
   public body, and it produces a citable response for your report.

Route 1 first. Route 2 if it goes unanswered.

Either way this is worth doing for the report regardless of the outcome. A
documented request to the data holder is a stronger methods section than a
scraper, and if they decline, that refusal is itself a finding about the
accessibility of Jamaican energy data.
""")


if __name__ == "__main__":
    main()
