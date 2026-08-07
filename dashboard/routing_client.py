"""
Client for Rohan's EVRange routing API.

WHY THIS IS CACHE FIRST RATHER THAN LIVE FIRST
----------------------------------------------
The API runs on a laptop behind a Cloudflare Tunnel and its author has said he
cannot guarantee uptime. A module that calls it live would be a broken page on
the day an examiner opens the dashboard, while every other module reads local
files and works forever.

So the disk cache is the primary path, not the fallback. Preset routes are
fetched once, committed to the repository under data/evrange_cache/, and served
from disk thereafter. The live call is an optional refresh for input
combinations that were never pre-fetched, and its failure is not an error.

Order of resolution:
    memory cache -> disk cache -> live API -> stub

STUB DATA MUST NEVER REACH THE REPORT
-------------------------------------
Until the host is live there is nothing to call, so a stub keeps the UI
buildable. Every result carries a `source` field, stub results additionally
carry `stub=True`, and `assert_reportable()` raises on anything that is not
live or disk. Call it before any figure that will be quoted.

Configuration, both from the environment, never committed:
    EVRANGE_API_URL   e.g. https://<whatever Rohan sends>
    EVRANGE_API_KEY   the x-api-key value

Citation: EVRange (2026), physics-based EV range model calibrated on the
Jamaican road network, unpublished. Route energy estimates via
/api/routing/calculate.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# Committed to the repo on purpose, so the module works with no network.
# Deliberately not a dotted directory: data/.http_cache/ is gitignored and this
# one must not be.
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "evrange_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

ENDPOINT_PATH = "/api/routing/calculate"

# Rohan's documented limit is 20 requests per minute per IP. Three seconds
# between live calls keeps us under it without needing a token bucket, and the
# cache means we rarely get near it anyway.
MIN_LIVE_INTERVAL_S = 3.0
REQUEST_TIMEOUT_S = 20.0

_last_live_call = 0.0
_rate_lock = threading.Lock()
_memory_cache: dict[str, dict] = {}

# Defaults for the fields a casual user should not have to think about. Kept
# here rather than in the layout so the cache key is stable across UI changes.
DEFAULTS = {
    "passengerCount": 1,
    "cargoKg": 0,
    "tyrePressureMult": 1.0,
    "ambientTempC": 28,
    "drivingMode": "normal",
    "currentSocPct": 80,
    "returnTrip": False,
}

STUB_WARNING = (
    "Stub data. The EVRange host is not configured, so these figures are "
    "synthetic and must not be quoted."
)


class NotReportable(RuntimeError):
    """Raised when stub or unavailable data is used where a real figure is required."""


def _configured() -> tuple[str | None, str | None]:
    url = os.environ.get("EVRANGE_API_URL", "").strip().rstrip("/")
    key = os.environ.get("EVRANGE_API_KEY", "").strip()
    return (url or None), (key or None)


def build_body(ev_spec_id: str, start_coords, end_coords, **overrides) -> dict:
    """
    Assemble a request body. Key order is fixed by canonical_key(), so callers
    need not worry about it, but every field is always present: a body that
    omits an optional field would cache under a different key from an identical
    body that supplies its default.
    """
    body = {
        "evSpecId": ev_spec_id,
        "startCoords": [float(start_coords[0]), float(start_coords[1])],
        "endCoords": [float(end_coords[0]), float(end_coords[1])],
        **DEFAULTS,
    }
    unknown = set(overrides) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"unknown routing parameters: {sorted(unknown)}")
    body.update(overrides)
    return body


def _norm_number(v):
    """
    Numbers are normalised to a fixed-precision string so that 28 and 28.0
    hash identically. Without this the same request cached twice, because a
    slider yielding an int and a default written as a float are the same
    request as far as the API is concerned.

    bool is checked first: in Python bool is a subclass of int, so True would
    otherwise normalise to "1.000000" and collide with the integer 1.
    """
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return f"{float(v):.6f}"
    return v


def canonical_key(body: dict) -> str:
    """Stable cache key: sorted keys, uniform number formatting."""
    norm = {}
    for k, v in body.items():
        if isinstance(v, list):
            norm[k] = [_norm_number(x) for x in v]
        else:
            norm[k] = _norm_number(v)
    blob = json.dumps(norm, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()[:20]


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


# Written into every cache record by _write_disk, and required by _read_disk.
#
# This exists because a cache hit returns source="disk", which assert_reportable
# accepts. Without a provenance marker, anything dropped into the cache
# directory by hand would be trusted as a real measurement. That happened once
# during development, when a test fixture was written straight to the cache and
# then served as if EVRange had returned it. An entry without this marker is
# ignored rather than trusted.
CACHE_ORIGIN = "evrange-live-response-v1"


def _read_disk(key: str) -> dict | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        # A corrupt entry is not worth crashing a dashboard over, and it will
        # be rewritten on the next successful live call.
        return None
    if rec.get("origin") != CACHE_ORIGIN:
        # Hand-written, edited, or from an older format. Not trustworthy as a
        # source of quotable figures, so treat it as absent.
        return None
    return rec.get("response")


def _write_disk(key: str, body: dict, response: dict) -> None:
    rec = {
        "origin": CACHE_ORIGIN,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "request": body,
        "response": response,
    }
    try:
        _cache_path(key).write_text(
            json.dumps(rec, indent=2, sort_keys=True), encoding="utf-8"
        )
    except Exception:
        pass


def _throttle() -> None:
    global _last_live_call
    with _rate_lock:
        wait = MIN_LIVE_INTERVAL_S - (time.monotonic() - _last_live_call)
        if wait > 0:
            time.sleep(wait)
        _last_live_call = time.monotonic()


def _call_live(body: dict) -> tuple[dict | None, str]:
    url, key = _configured()
    if not url or not key:
        return None, "not configured"
    _throttle()
    try:
        r = requests.post(
            url + ENDPOINT_PATH,
            headers={"Content-Type": "application/json", "x-api-key": key},
            json=body,
            timeout=REQUEST_TIMEOUT_S,
        )
    except requests.RequestException as e:
        return None, f"unreachable: {type(e).__name__}"
    if r.status_code == 429:
        return None, "rate limited"
    if r.status_code in (401, 403):
        return None, f"rejected: HTTP {r.status_code}, check EVRANGE_API_KEY"
    if r.status_code >= 400:
        return None, f"HTTP {r.status_code}"
    try:
        return r.json(), "ok"
    except ValueError:
        return None, "response was not JSON"


def _stub(body: dict) -> dict:
    """
    Synthetic response in the documented shape, so the layout and callbacks can
    be built and tested before the host exists.

    The numbers are deliberately crude. A straight line between the endpoints
    and a flat consumption figure, with no terrain model at all. They are the
    right order of magnitude so charts render sensibly, and wrong enough that
    nobody would mistake them for a result.
    """
    (lon1, lat1), (lon2, lat2) = body["startCoords"], body["endCoords"]
    # Rough planar approximation, adequate for a placeholder at this latitude.
    dx = (lon2 - lon1) * 111.32 * 0.951
    dy = (lat2 - lat1) * 110.57
    straight_km = (dx * dx + dy * dy) ** 0.5
    distance_km = round(straight_km * 1.35, 1)          # crude road factor
    if body.get("returnTrip"):
        distance_km = round(distance_km * 2, 1)
    avg_whkm = 150.0
    usable_kwh = 60.0
    soc_needed = round(distance_km * avg_whkm / 1000.0 / usable_kwh * 100.0, 1)
    return {
        "evModel": "STUB, not a real vehicle",
        "batteryUsableKwh": usable_kwh,
        "currentSocPct": body["currentSocPct"],
        "stub": True,
        "routes": [{
            "distanceKm": distance_km,
            "durationMin": round(distance_km / 40.0 * 60.0),
            "avgWhkm": avg_whkm,
            "socNeededPct": soc_needed,
            "socAfterTripPct": round(body["currentSocPct"] - soc_needed, 1),
            "chargeNeeded": soc_needed > body["currentSocPct"],
            "chargeWarning": STUB_WARNING,
            "hasTolls": False,
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon1, lat1], [lon2, lat2]],
            },
        }],
    }


def calculate_route(ev_spec_id: str, start_coords, end_coords,
                    *, allow_live: bool = True, **overrides) -> dict:
    """
    Resolve one route. Never raises on network trouble.

    Returns the API response with two fields added:
        source  one of "memory", "disk", "live", "stub"
        note    human readable explanation when the live call was not used

    Check `source` before quoting anything, or call assert_reportable().
    """
    body = build_body(ev_spec_id, start_coords, end_coords, **overrides)
    key = canonical_key(body)

    if key in _memory_cache:
        return {**_memory_cache[key], "source": "memory", "note": ""}

    disk = _read_disk(key)
    if disk is not None:
        _memory_cache[key] = disk
        return {**disk, "source": "disk", "note": ""}

    if allow_live:
        live, why = _call_live(body)
        if live is not None:
            _memory_cache[key] = live
            _write_disk(key, body, live)
            return {**live, "source": "live", "note": ""}
    else:
        why = "live call not permitted by caller"

    return {**_stub(body), "source": "stub", "note": why}


def assert_reportable(result: dict) -> dict:
    """
    Guard for any figure that will appear in the report or be quoted.
    Passes through live and disk results, raises on anything else.
    """
    if result.get("source") in ("live", "disk", "memory") and not result.get("stub"):
        return result
    raise NotReportable(
        f"routing result has source={result.get('source')!r}: {result.get('note') or STUB_WARNING}"
    )


def cache_status() -> dict:
    """Small summary for the UI and for scripts that populate the cache."""
    url, key = _configured()
    entries = sorted(CACHE_DIR.glob("*.json"))
    return {
        "configured": bool(url and key),
        "url_set": bool(url),
        "key_set": bool(key),
        "cached_routes": len(entries),
        "cache_dir": str(CACHE_DIR),
    }
