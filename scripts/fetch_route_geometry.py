"""
Fetch road geometry for the measured Kingston runs, once, and cache it.

WHY THIS EXISTS
---------------
The map was drawing straight lines between endpoints because that is all the
stub provides. EVRange returns real geometry, but its host is not up yet and
will not be reliable when it is, so the map would fall back to straight lines
whenever it was down.

Road geometry does not change. So it is fetched once from OSRM, written to
data/route_geometry.json, and committed. After that the module draws real
routes with no network access at all, on any machine, forever.

WHAT THIS DOES NOT DO
---------------------
It does not supply any number used in a cost or emissions figure. Energy comes
from EVRange, distance from the odometer readings in dashboard/routes.py.

OSRM's road distance IS recorded, but only as an independent cross-check
against the recorded distances. It is a different kind of measurement, derived
from the road network rather than from the vehicle, and it assumes the driver
took the route OSRM would choose. Where the two disagree that is worth knowing,
not worth silently averaging.

USAGE
    python scripts/fetch_route_geometry.py           fetch anything missing
    python scripts/fetch_route_geometry.py --force   refetch everything

Uses the public OSRM demo server, which asks for light use. This makes at most
sixteen requests, once, with a pause between them, and never runs again unless
a route is added.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dashboard"))
import routes as route_data  # noqa: E402

OSRM = "https://router.project-osrm.org/route/v1/driving"
OUT = Path(__file__).resolve().parent.parent / "data" / "route_geometry.json"
PAUSE_S = 1.5
TIMEOUT_S = 30

ATTRIBUTION = (
    "Road geometry from the OSRM public demo server, project-osrm.org, "
    "routing over OpenStreetMap data. OpenStreetMap contributors, ODbL."
)


def fetch_one(start, end):
    """start and end are [lon, lat]. OSRM wants lon,lat in the path."""
    url = (f"{OSRM}/{start[0]},{start[1]};{end[0]},{end[1]}"
           f"?overview=full&geometries=geojson")
    r = requests.get(url, timeout=TIMEOUT_S,
                     headers={"User-Agent": "UWI-Mona-EV-Lab/1.0 research"})
    r.raise_for_status()
    data = r.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise RuntimeError(f"OSRM returned {data.get('code')!r}")
    route = data["routes"][0]
    return {
        "geometry": route["geometry"],
        "osrm_distance_km": round(route["distance"] / 1000.0, 3),
        "osrm_duration_min": round(route["duration"] / 60.0, 1),
        "points": len(route["geometry"]["coordinates"]),
    }


def main(force: bool = False) -> int:
    cache = {}
    if OUT.exists() and not force:
        cache = json.loads(OUT.read_text(encoding="utf-8")).get("routes", {})

    runs = route_data._runs_with_coords()
    if not runs:
        print("No runs have coordinates yet. Fill in PLACES in "
              "dashboard/routes.py first.")
        return 1

    print(f"{len(runs)} runs with coordinates, {len(cache)} already cached\n")
    fetched = failed = 0
    for r in runs:
        key = r["key"]
        if key in cache and not force:
            continue
        try:
            got = fetch_one(r["start"], r["end"])
        except Exception as e:
            print(f"  FAILED  {key:<8} {r['label'][:44]}  {type(e).__name__}: {e}")
            failed += 1
            continue
        cache[key] = {**got, "label": r["label"],
                      "recorded_km": r["measured_km"]}
        fetched += 1
        ratio = got["osrm_distance_km"] / r["measured_km"] if r["measured_km"] else 0
        flag = "  <-- differs by more than 25%" if not 0.75 <= ratio <= 1.25 else ""
        print(f"  ok      {key:<8} {r['label'][:40]:<40} "
              f"recorded {r['measured_km']:>4.1f}  osrm {got['osrm_distance_km']:>5.2f}"
              f"  ratio {ratio:>4.2f}  {got['points']:>4} pts{flag}")
        time.sleep(PAUSE_S)

    OUT.write_text(json.dumps(
        {"attribution": ATTRIBUTION,
         "note": ("Geometry only. Distances here are an independent "
                  "cross-check and are NOT used in any cost or emissions "
                  "figure."),
         "routes": cache}, indent=2, sort_keys=True), encoding="utf-8")
    print(f"\n{fetched} fetched, {failed} failed, {len(cache)} cached total")
    print(f"written to {OUT}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main(force="--force" in sys.argv))
