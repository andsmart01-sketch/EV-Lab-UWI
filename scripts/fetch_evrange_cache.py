"""
Populate the EVRange disk cache, once, so the Route Cost Map works offline.

WHY THIS EXISTS
---------------
Rohan's server runs on a laptop behind a Cloudflare Tunnel and he has said he
cannot guarantee it stays up. The dashboard is therefore cache first: it reads
data/evrange_cache/ before it ever tries the network, and the live call is only
a refresh for input combinations nobody pre-fetched. But the cache is empty
until something fills it, and until then every route shows placeholder data
with a red banner. This script fills it.

Run it once when the server is up, commit data/evrange_cache/, and the module
works on an examiner's machine with no network and no key.

WHAT IT FETCHES
---------------
Every selectable route (Rohan's three corridors plus the sixteen measured
Kingston runs), for every vehicle with a real evSpecId, at the default
conditions the page opens with, one way and return. That is the set a reader
sees without touching a control. Anything they change after that (passengers,
cargo, temperature, mode, battery level) goes to the live API if it is up and
to the placeholder if it is not, and the page says which.

The request bodies are built by the same routing_client.build_body() the
dashboard uses, so the cache keys match exactly. Do not write cache entries by
any other route: routing_client ignores entries without its provenance marker.

USAGE
    set EVRANGE_API_KEY=...              (Windows)     export ... (Linux/macOS)

    The hostname defaults to Rohan's permanent tunnel, see DEFAULT_API_URL in
    routing_client.py. Set EVRANGE_API_URL only if that ever changes.

    python scripts/fetch_evrange_cache.py --list-models
        GET /api/ev-models, print it, save it to data/evrange_models.json.
        Paste the ids for the Yuan Plus and the Leaf into EV_SPEC_IDS in
        dashboard/module_route.py, then:

    python scripts/fetch_evrange_cache.py --dry-run
        List what would be fetched, without calling anything.

    python scripts/fetch_evrange_cache.py
        Fetch everything not already cached. Paced to Rohan's 20 per minute.

    python scripts/fetch_evrange_cache.py --force
        Refetch everything, for example after Rohan changes the model.

    python scripts/fetch_evrange_cache.py --print-bodies > bodies.json
        Write the full request set as JSON, for Rohan to run on his own
        machine if the server never goes up. Works before the ids are known;
        vehicles without an id get a placeholder he can substitute.

Exit code 0 when nothing failed, 1 when it could not start, 2 when some
routes failed (those are listed, and re-running fetches only the gaps).
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "dashboard"))

import routes as route_data                       # noqa: E402
import routing_client as rc                       # noqa: E402
from module_route import EV_SPEC_IDS              # noqa: E402

MODELS_OUT = ROOT / "data" / "evrange_models.json"


def _configured_or_exit() -> None:
    st = rc.cache_status()
    if st["configured"]:
        print(f"EVRange at {st['url']}")
        return
    missing = [n for n, ok in (("EVRANGE_API_URL", st["url_set"]),
                               ("EVRANGE_API_KEY", st["key_set"])) if not ok]
    print("Not configured. Set " + " and ".join(missing) + " in the "
          "environment first (never in a file that is committed).")
    raise SystemExit(1)


def list_models() -> int:
    """Fetch /api/ev-models, save the raw response, and hint at the two ids."""
    _configured_or_exit()
    data, why = rc.fetch_ev_models()
    if data is None:
        print(f"/api/ev-models failed: {why}")
        return 1
    MODELS_OUT.write_text(json.dumps(
        {"fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "endpoint": rc.MODELS_PATH,
         "response": data}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(data, indent=2))
    print(f"\nSaved to {MODELS_OUT}")

    # The response shape was not documented, so this is a text search rather
    # than a parse. It is a hint for a human, not a mapping.
    blob = json.dumps(data).lower()
    for name in ("yuan", "leaf"):
        print(f"  '{name}' {'appears' if name in blob else 'does NOT appear'} "
              f"in the response")
    print("\nPaste the ids into EV_SPEC_IDS in dashboard/module_route.py, "
          "then run this script again without --list-models.")
    return 0


def plan(placeholders: bool = False) -> list[dict]:
    """
    Every (route, vehicle, return_trip) at default conditions.

    With placeholders=True, vehicles that have no evSpecId yet are included
    under a stand-in id, for --print-bodies only. Never fetch with those.
    """
    vehicles = {k: (v or (f"<evSpecId for {k}>" if placeholders else None))
                for k, v in EV_SPEC_IDS.items()}
    vehicles = {k: v for k, v in vehicles.items() if v}
    jobs = []
    for opt in route_data.selectable_routes():
        r = route_data.resolve_route(opt["value"])
        for vkey, spec in vehicles.items():
            for rt in (False, True):
                body = rc.build_body(spec, r["start"], r["end"], returnTrip=rt)
                jobs.append({"route": opt["value"], "label": opt["label"],
                             "vehicle": vkey, "spec": spec, "return": rt,
                             "body": body, "key": rc.canonical_key(body),
                             "measured_km": r.get("measured_km"),
                             "measured_kwh": r.get("measured_kwh")})
    return jobs


def main(argv: list[str]) -> int:
    if "--list-models" in argv:
        return list_models()
    if "--print-bodies" in argv:
        jobs = plan(placeholders=True)
        print(json.dumps([{"route": j["route"], "vehicle": j["vehicle"],
                           "body": j["body"]} for j in jobs], indent=2))
        print(f"{len(jobs)} request bodies", file=sys.stderr)
        return 0
    dry = "--dry-run" in argv
    force = "--force" in argv

    vehicles = {k: v for k, v in EV_SPEC_IDS.items() if v}
    if not vehicles:
        print("EV_SPEC_IDS in dashboard/module_route.py has no ids yet. Run "
              "with --list-models first and paste them in.")
        return 1
    if not dry:
        _configured_or_exit()

    jobs = plan()
    todo = [j for j in jobs if force or rc._read_disk(j["key"]) is None]
    print(f"{len(jobs)} route/vehicle/direction combinations, "
          f"{len(jobs) - len(todo)} already cached, {len(todo)} to fetch")
    est = len(todo) * rc.MIN_LIVE_INTERVAL_S
    print(f"At {rc.MIN_LIVE_INTERVAL_S:.0f} s spacing that is about "
          f"{est / 60:.0f} minutes.\n")
    if dry:
        for j in todo:
            print(f"  {j['route']:<18} {j['vehicle']:<18} "
                  f"{'return' if j['return'] else 'one way'}")
        return 0

    print(f"{'route':<18} {'vehicle':<18} {'dir':<7} {'km':>6} {'Wh/km':>6} "
          f"{'SoC%':>5} {'tolls':>5}  vs measured")
    fetched = failed = 0
    for j in todo:
        res = rc.calculate_route(j["spec"], j["body"]["startCoords"],
                                 j["body"]["endCoords"], returnTrip=j["return"])
        if res["source"] != "live":
            print(f"  FAILED  {j['route']:<18} {j['vehicle']:<18} "
                  f"{'return' if j['return'] else 'one way'}  {res.get('note')}")
            failed += 1
            if res.get("note") == "rate limited":
                time.sleep(60)
            continue
        fetched += 1
        leg = res["routes"][0]
        cmp_ = ""
        if j["measured_km"] and not j["return"]:
            # The point of the whole exercise: the model against the car.
            api_km = leg["distanceKm"]
            meas_whkm = (j["measured_kwh"] * 1000.0 / j["measured_km"]
                         if j["measured_km"] else float("nan"))
            cmp_ = (f"recorded {j['measured_km']:.1f} km, "
                    f"{meas_whkm:.0f} Wh/km; distance ratio "
                    f"{api_km / j['measured_km']:.2f}")
        print(f"  {j['route']:<18} {j['vehicle']:<18} "
              f"{'return' if j['return'] else 'one way':<7} "
              f"{leg['distanceKm']:>6.1f} {leg['avgWhkm']:>6.1f} "
              f"{leg['socNeededPct']:>5.1f} {str(leg.get('hasTolls')):>5}  {cmp_}")

    st = rc.cache_status()
    print(f"\n{fetched} fetched, {failed} failed, "
          f"{st['cached_routes']} entries in {st['cache_dir']}")
    if fetched:
        print("Commit data/evrange_cache/ so a clean clone serves these "
              "from disk.")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
