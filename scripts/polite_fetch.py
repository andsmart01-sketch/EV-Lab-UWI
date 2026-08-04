"""
polite_fetch.py — a well-behaved HTTP layer for the EV Lab scrapers.

WHY THIS EXISTS
---------------
The dashboard needs two external figures on a weekly cadence:

  * Petrojam reference fuel prices (published Wednesdays)
  * USD/JMD exchange rate

That is two requests per week. Two. At that volume no rate limiter on earth
will block you, and if you are being blocked the cause is almost certainly
development loops — re-running a debug script twenty times in an afternoon —
not the scheduled job.

So the fix is not to disguise the requests. The fix is to make far fewer of
them and to identify yourself honestly when you do. That is what this module
does, and it is strictly more robust than evasion, because a cached response
cannot be rate limited at all.

WHAT IT PROVIDES
----------------
1. Conditional GET. Stores ETag / Last-Modified and sends If-None-Match /
   If-Modified-Since. A 304 costs the server almost nothing and costs you no
   parsing at all.
2. An on-disk response cache with a minimum age. Repeated calls inside the
   cache window never touch the network.
3. A "we already have this week's data" short-circuit, so the weekly job is a
   no-op when run twice.
4. Exponential backoff with jitter, honouring Retry-After, with a hard attempt
   cap so a failing endpoint is never hammered.
5. robots.txt checking.
6. An honest User-Agent naming the project and a contact address, so that if
   this ever does cause a problem the operator can email instead of blocking.

Requires: requests (already a project dependency).
"""

from __future__ import annotations

import hashlib
import json
import random
import time
import urllib.robotparser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

# ── Identify the PROJECT, not a person ────────────────────────────
#
# The contact point should outlive whoever is currently running the code.
# It is sent in the User-Agent header on every request, so it ends up in the
# server logs of every site this touches. Do not put a personal address here:
# it will still be in third-party logs long after the project ends, and the
# person who has to answer a query about this scraper in two years may not be
# the person who wrote it.
#
# Use, in order of preference:
#   1. A departmental or lab address  (e.g. physics@uwimona.edu.jm)
#   2. A role address created for the project  (e.g. evlab@uwimona.edu.jm)
#   3. The supervising academic's institutional address, with their agreement
#
# Set it via the environment so the address is not committed to the repo:
#     set EVLAB_CONTACT=evlab@uwimona.edu.jm        (Windows)
#     export EVLAB_CONTACT=evlab@uwimona.edu.jm     (macOS/Linux)
#
# An operator who can contact you will email before blocking you. An operator
# facing an anonymous scraper has only one lever. That is why this exists.

import os

CONTACT = os.environ.get("EVLAB_CONTACT", "").strip()
PROJECT_URL = "https://github.com/andsmart01-sketch/EV-Lab-UWI"

if not CONTACT:
    # Deliberately not a real address. The scraper still works, but it says
    # plainly that it is unattributed, which is honest rather than evasive.
    CONTACT = "contact-not-configured; see EVLAB_CONTACT"

USER_AGENT = (
    f"EVLabUWI/1.0 (UWI Mona Physics research project; "
    f"+{PROJECT_URL}; {CONTACT}) python-requests"
)


def warn_if_unattributed() -> None:
    """Call at the start of any scraping run so the omission is visible."""
    if "not-configured" in CONTACT:
        print("  NOTE: EVLAB_CONTACT is not set, so requests carry no contact "
              "address. Set it to a departmental or project address before "
              "running this regularly.")

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / ".http_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Minimum time between live requests to the same URL, regardless of caller.
DEFAULT_MIN_AGE = timedelta(hours=12)

# Backoff schedule. Five attempts over roughly two minutes, then give up
# and let the caller fall back to cached data.
MAX_ATTEMPTS = 5
BASE_DELAY_S = 2.0
MAX_DELAY_S = 60.0

_session: requests.Session | None = None


def _get_session() -> requests.Session:
    """One session for the whole process: connection reuse, consistent headers."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-JM,en;q=0.9",
        })
    return _session


def _cache_paths(url: str) -> tuple[Path, Path]:
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    return CACHE_DIR / f"{key}.body", CACHE_DIR / f"{key}.meta.json"


def _load_meta(meta_path: Path) -> dict:
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text())
        except Exception:
            pass
    return {}


def robots_allows(url: str) -> tuple[bool, str]:
    """
    Check robots.txt before fetching. Returns (allowed, reason).

    DO NOT use urllib.robotparser's own .read(). It fetches robots.txt with
    urllib's default "Python-urllib/3.x" User-Agent, which many WordPress
    front ends and WAFs answer with 403. RobotFileParser then interprets that
    403 as "disallow everything", so the site appears to forbid crawling when
    its robots.txt in fact permits it. That happened here on 2026-07-31:
    petrojam.com/robots.txt contains

        User-agent: *
        Disallow:

    which is the standard way of saying nothing is disallowed, yet the check
    reported the page as blocked.

    So we fetch robots.txt ourselves, with our own honest User-Agent, and hand
    the text to .parse(). Sending the UA that will actually make the request is
    both more correct and more transparent, since it is the UA the rules are
    being evaluated against.

    A robots.txt we cannot read at all returns True with a reason saying so.
    That is the conventional permissive default. An explicit Disallow returns
    False and MUST stop the caller, including any browser fallback.
    """
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    try:
        resp = _get_session().get(robots_url, timeout=10)
    except requests.RequestException as e:
        return True, f"robots.txt unreachable ({type(e).__name__}); proceeding"

    if resp.status_code in (401, 403):
        # IMPORTANT: this is NOT a robots directive. A 403 on robots.txt means
        # the site's edge filter refused our client before robots.txt was ever
        # consulted. Petrojam's actual robots.txt, read on 2026-07-31, is
        # "User-agent: * / Disallow:", which permits everything.
        #
        # We stop anyway, but for a different and more serious reason: a server
        # that answers 403 to an honestly identified client is telling us it
        # does not want this client. The way to change that answer is to ask
        # the operator, not to change how the client describes itself.
        return False, (f"the site refused our client with HTTP "
                       f"{resp.status_code} (this is an edge/WAF block, not a "
                       f"robots.txt rule)")
    if resp.status_code >= 400:
        return True, f"no robots.txt (HTTP {resp.status_code}); proceeding"

    rp = urllib.robotparser.RobotFileParser()
    rp.parse(resp.text.splitlines())
    if rp.can_fetch(USER_AGENT, url):
        return True, "robots.txt permits this path"
    return False, "robots.txt disallows this path"


def fetch(url: str, *, min_age: timedelta = DEFAULT_MIN_AGE,
          force: bool = False, timeout: int = 20) -> tuple[str | None, str]:
    """
    Fetch a URL politely.

    Returns (body, source) where source is one of:
        "cache-fresh"  cached copy was newer than min_age; no request made
        "cache-304"    server confirmed nothing changed; no body transferred
        "network"      a full response was downloaded
        "cache-stale"  request failed; returning the last good copy
        "failed"       no response and nothing cached

    The caller should treat "failed" as a soft error and keep whatever data it
    already has, rather than writing an empty value.
    """
    body_path, meta_path = _cache_paths(url)
    meta = _load_meta(meta_path)

    # 1. Fresh cache: do not touch the network at all.
    if not force and body_path.exists() and meta.get("fetched_at"):
        age = datetime.now(timezone.utc) - datetime.fromisoformat(meta["fetched_at"])
        if age < min_age:
            return body_path.read_text(encoding="utf-8", errors="replace"), "cache-fresh"

    allowed, reason = robots_allows(url)
    if not allowed:
        print(f"  robots.txt disallows {url} ({reason}). Not fetching.")
        # Return a DISTINCT source value. Callers must be able to tell a robots
        # refusal apart from an ordinary failure, because falling back to a
        # browser after a robots refusal would be evasion.
        if body_path.exists():
            return body_path.read_text(encoding="utf-8", errors="replace"), "robots-blocked-cached"
        return None, "robots-blocked"

    # 2. Conditional request: ask only for what changed.
    headers = {}
    if meta.get("etag"):
        headers["If-None-Match"] = meta["etag"]
    if meta.get("last_modified"):
        headers["If-Modified-Since"] = meta["last_modified"]

    session = _get_session()
    delay = BASE_DELAY_S

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = session.get(url, headers=headers, timeout=timeout)

            if resp.status_code == 304:
                meta["fetched_at"] = datetime.now(timezone.utc).isoformat()
                meta_path.write_text(json.dumps(meta, indent=2))
                return body_path.read_text(encoding="utf-8", errors="replace"), "cache-304"

            # Back off on rate limiting and server errors, and obey Retry-After.
            if resp.status_code in (429, 500, 502, 503, 504):
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait = min(float(retry_after), MAX_DELAY_S)
                    except ValueError:
                        wait = delay
                else:
                    wait = delay
                if attempt == MAX_ATTEMPTS:
                    break
                # Jitter prevents synchronised retries if this ever runs on a
                # schedule alongside anything else.
                wait += random.uniform(0, wait * 0.3)
                print(f"  HTTP {resp.status_code}; waiting {wait:.1f}s "
                      f"(attempt {attempt}/{MAX_ATTEMPTS})")
                time.sleep(wait)
                delay = min(delay * 2, MAX_DELAY_S)
                continue

            resp.raise_for_status()

            body_path.write_text(resp.text, encoding="utf-8")
            meta_path.write_text(json.dumps({
                "url": url,
                "etag": resp.headers.get("ETag"),
                "last_modified": resp.headers.get("Last-Modified"),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "status": resp.status_code,
            }, indent=2))
            return resp.text, "network"

        except requests.RequestException as e:
            if attempt == MAX_ATTEMPTS:
                print(f"  Request failed after {MAX_ATTEMPTS} attempts: {e}")
                break
            wait = delay + random.uniform(0, delay * 0.3)
            print(f"  {type(e).__name__}; waiting {wait:.1f}s "
                  f"(attempt {attempt}/{MAX_ATTEMPTS})")
            time.sleep(wait)
            delay = min(delay * 2, MAX_DELAY_S)

    if body_path.exists():
        print("  Falling back to last good cached copy.")
        return body_path.read_text(encoding="utf-8", errors="replace"), "cache-stale"
    return None, "failed"


# ── The single most effective change ──────────────────────────────

def latest_price_date(path: Path):
    """
    Most recent date in the price series, or None.

    Handles BOTH the .xlsx (which the dashboard actually reads) and the
    derived .csv, and both date formats present in the file: ISO strings
    like 2026-07-29 and long form like "June 11, 2026".
    """
    if not path.exists():
        return None
    try:
        import pandas as pd
        if path.suffix.lower() in (".xlsx", ".xlsm"):
            df = pd.read_excel(path, sheet_name=0)
        else:
            df = pd.read_csv(path)
        date_col = next((c for c in df.columns if str(c).strip().lower() == "date"), None)
        if date_col is None:
            return None
        parsed = pd.to_datetime(df[date_col], format="mixed", errors="coerce").dropna()
        return parsed.max().date() if len(parsed) else None
    except Exception:
        return None


def already_have_current_week(path: Path, publish_weekday: int = 3) -> bool:
    """
    True if the local price series already contains a row dated on or after the
    most recent publication day. Petrojam publishes on THURSDAYS
    (weekday 3, Monday = 0). This was verified against the series itself:
    581 of 602 rows were Thursdays, and every row from April to June 2026 was.
    An earlier version assumed Wednesday, which would have triggered a
    needless scrape every Wednesday and missed the real release every Thursday.

    Point this at the SAME file the dashboard reads, which is the .xlsx in
    data/raw. Pointing it at the derived .csv gives a false negative whenever
    the csv has not been regenerated, which causes an unnecessary scrape.

    Call this BEFORE launching a browser. If it returns True, the correct
    number of network requests this run is zero. This one guard eliminates
    almost all avoidable traffic, because the common failure mode is a job or a
    developer rerunning something that had already succeeded.
    """
    latest = latest_price_date(path)
    if latest is None:
        return False
    today = datetime.now()
    days_since = (today.weekday() - publish_weekday) % 7
    last_publish = (today - timedelta(days=days_since)).date()
    return latest >= last_publish


if __name__ == "__main__":
    # Demonstration: two consecutive calls, only the first touches the network.
    for i in (1, 2):
        body, source = fetch("https://open.er-api.com/v6/latest/USD",
                             min_age=timedelta(hours=12))
        print(f"call {i}: source={source}, bytes={len(body) if body else 0}")
