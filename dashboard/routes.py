"""
Preset routes and toll data for the Route Cost Map.

WHY PRESETS RATHER THAN A SEARCH BOX
------------------------------------
A free-text location search would let a user generate routes for which no
measured consumption exists, producing numbers nobody can check. The presets
here are the corridors that were actually driven during data collection, so
EVRange output on them can be validated against what was recorded in the car.

Coordinates are [longitude, latitude], matching the EVRange request format.
Note that this is the opposite order from the [lat, lon] convention Plotly and
most mapping libraries use. Convert at the boundary, not in the middle.

A route with coords set to None is one this project has named but not yet
measured. It is listed so the gap is visible rather than silently absent, and
it must not be offered in the UI until real endpoints exist. DO NOT fill these
in by eye from a map: the whole point of the preset list is that every route
in it corresponds to a run with recorded consumption.
"""

from __future__ import annotations

import re

# ── Measured runs ────────────────────────────────────────────────
# Supplied by Rohan, 7 August 2026, from the joint data collection runs.
# The full set with recorded consumption is still to come as a spreadsheet;
# these are the three he confirmed had usable start and end pairs.
MEASURED_ROUTES = {
    "t4-portmore-uwi": {
        "label": "Portmore to UWI Mona (T1 highway)",
        "run_id": "T4",
        "start": [-76.9876, 17.9488],
        "end":   [-76.7467, 17.9958],
        "note": "Highway run. Calibration anchor for the 1.09 highway "
                "correction factor at 83 km/h.",
        "source": "EVRange measured run T4, Rohan, 7 August 2026",
    },
    "t7-spur-tree": {
        "label": "Spur Tree Hill (descent and ascent)",
        "run_id": "T7/T8",
        "start": [-77.5085, 18.0447],
        "end":   [-77.4237, 17.9882],
        "note": "Steep gradient run. Exercises the climb and regenerative "
                "braking terms harder than anything in Kingston.",
        "source": "EVRange measured runs T7 and T8, Rohan, 7 August 2026",
    },
    "red-hills": {
        "label": "Kingston to Red Hills",
        "run_id": "Red Hills",
        "start": [-76.8072, 18.0089],
        "end":   [-76.8334, 18.0812],
        "note": "Mixed urban and gradient. One of the three calibration "
                "routes named in the EVRange terrain correction.",
        "source": "EVRange measured run, Rohan, 7 August 2026",
    },
}

# ── Measured Kingston route-taxi runs ────────────────────────────
#
# Sixteen runs in a BYD Yuan Plus over the corridors named in report Section
# 8.3, recorded by Andrew Smart. Energy read from the vehicle's own end-of-trip
# consumption display, so the resolution is 0.1 kWh.
#
# READ THIS BEFORE USING ANY INDIVIDUAL FIGURE
# --------------------------------------------
# Per-run Wh/km ranges from -271 to +667. That spread is real and mostly
# physical: Kingston rises from the harbour inland, so direction dominates.
# Half Way Tree to Three Miles reads 57 Wh/km downhill and 343 Wh/km on the
# return over the identical 3.5 km. The Red Hills pair regenerates on the
# descent, which is why one figure is negative.
#
# The consequence is that a single run measures one direction of one corridor
# on one day, not the consumption of the vehicle. Only the AGGREGATE below is
# fit to quote, because errors and gradients partly cancel across the set.
#
# Two known problems, both unresolved:
#   - Windward Road is coastal and effectively flat, yet reads 144 Wh/km
#     outbound against 44 Wh/km back. No gradient explains it.
#   - Runs 1 and 5 are the same corridor, Crossroads to South Parade by Slipe
#     Road, recorded as 3.0 km one way and 2.0 km the other. One is wrong.
#
# No coordinates. Endpoints exist only as Google Maps links and place names,
# so these runs cannot yet be drawn on the map or sent to EVRange. Obtaining
# the endpoint coordinates is what would let each run be compared against the
# model directly, which is the whole point of having measured them.
MEASURED_URBAN_RUNS = [
    # (run, origin, via, destination, km, kWh)
    (1,  "Crossroads",       "Slipe Road",      "South Parade",   3.0,  0.3),
    (2,  "Half Way Tree",    "Hagley Park Rd",  "Three Miles",    3.5,  0.2),
    (3,  "Half Way Tree",    "Oxford Rd",       "Crossroads",     2.3,  0.5),
    (4,  "UWI backgate",     "Old Hope Rd",     "Crossroads",     7.0,  0.7),
    (5,  "South Parade",     "Slipe Road",      "Crossroads",     2.0,  1.0),
    (6,  "Crossroads",       "Half Way Tree Rd","Half Way Tree",  3.0,  0.8),
    (7,  "Crossroads",       "Old Hope Rd",     "UWI backgate",   7.0,  2.0),
    (8,  "Half Way Tree",    "Red Hills Rd",    "Mackville",      6.0,  0.8),
    (9,  "Mackville",        "Red Hills Rd",    "Fi-wi Mary",     4.8,  3.2),
    (10, "Fi-wi Mary",       "Red Hills Rd",    "Mackville",      4.8, -1.3),
    (11, "Mackville",        "Red Hills Rd",    "Half Way Tree",  5.3,  1.1),
    (12, "South Parade",     "Windward Rd",     "Harbour View",   9.0,  1.3),
    (13, "Harbour View",     "Windward Rd",     "South Parade",   9.0,  0.4),
    (14, "Three Miles",      "Spanish Town Rd", "Duhaney Park",   5.0,  0.9),
    (15, "Duhaney Park",     "Spanish Town Rd", "Three Miles",    5.0,  1.0),
    (16, "Three Miles",      "Hagley Park Rd",  "Half Way Tree",  3.5,  1.2),
]

MEASURED_RUNS_SOURCE = (
    "Sixteen route-taxi runs in a BYD Yuan Plus over Kingston corridors, "
    "Andrew Smart, 2026. Energy from the vehicle end-of-trip consumption "
    "display, resolution 0.1 kWh."
)

# ── Distance adjustments ─────────────────────────────────────────
#
# MEASURED_URBAN_RUNS above is the record of what was read off the vehicle and
# is never edited. Where a recorded distance is not physically possible against
# the endpoint coordinates, the correction is declared here instead, with its
# reason, so the raw figure and the adjustment stay separately visible.
#
# Both cases are corridors driven in each direction where the two distances
# disagree. The vehicle's distance increment is coarse and the stopping point
# varied between runs, so the true value lies somewhere between the two
# readings. That reasoning holds for run 5 and is ruled out for run 3, where
# the midpoint is still shorter than the straight line.
#
# ON THE UNCERTAINTY MORE BROADLY: five of the seven paired corridors show a
# spread of exactly zero, and two show 26 and 40 per cent. Genuine measurement
# noise would appear on most pairs, so the likeliest explanation is that on the
# five, one reading was recorded for both directions. The uncertainty is
# therefore present throughout and merely invisible outside these two.
DISTANCE_ADJUSTMENTS = {
    3: {"recorded": 2.3, "used": 3.0,
        "reason": ("Straight line between the endpoints is 2.88 km, so 2.3 km "
                   "is impossible and the midpoint of 2.3 and 3.0 is also "
                   "impossible. Geometry forces at least 2.88 km, so the "
                   "3.0 km recorded in the opposite direction is used.")},
    5: {"recorded": 2.0, "used": 2.5,
        "reason": ("Straight line is 2.28 km, so 2.0 km is impossible. The "
                   "same corridor was recorded at 3.0 km in the opposite "
                   "direction, and the midpoint of 2.0 and 3.0 is feasible, "
                   "so 2.5 km is used.")},
}


def distance_for(run_id: int, recorded_km: float) -> float:
    """Adjusted distance where one is declared, otherwise the recorded value."""
    adj = DISTANCE_ADJUSTMENTS.get(run_id)
    return adj["used"] if adj else recorded_km


def urban_aggregate_whkm(include_regen: bool = True) -> dict:
    """
    The one quotable figure from the measured runs.

    Aggregated as total energy over total distance rather than as a mean of
    per-run rates. A mean of rates would weight a 2 km run equally with a 9 km
    one and would be dominated by the short, steep, low-resolution runs.
    """
    runs = MEASURED_URBAN_RUNS if include_regen else [
        r for r in MEASURED_URBAN_RUNS if r[5] > 0]
    km = sum(distance_for(r[0], r[4]) for r in runs)
    kwh = sum(r[5] for r in runs)
    central = kwh * 1000.0 / km
    # Distance uncertainty, taken from the two corridors where the distance was
    # genuinely read in both directions: spreads of 26 and 40 per cent about
    # the mean, so roughly 15 per cent either side. Energy resolution is 0.1
    # kWh, which matters far more on a 2 km run than a 9 km one. Quoted as a
    # band because a single figure would imply a precision the instrument does
    # not have.
    dist_unc = 0.15
    return {
        "wh_per_km": central,
        "wh_per_km_low": kwh * 1000.0 / (km * (1 + dist_unc)),
        "wh_per_km_high": kwh * 1000.0 / (km * (1 - dist_unc)),
        "kwh_per_100km": kwh * 100.0 / km,
        "total_km": km,
        "total_kwh": kwh,
        "runs": len(runs),
        "distance_uncertainty": dist_unc,
        "adjusted_runs": sorted(DISTANCE_ADJUSTMENTS),
        "source": MEASURED_RUNS_SOURCE,
    }


# Convenience: the headline number, all sixteen runs included.
URBAN_AGGREGATE = urban_aggregate_whkm()


# ── Endpoint coordinates ─────────────────────────────────────────
#
# The sixteen measured runs touch only NINE distinct places. Fill these in and
# every run below becomes routable and drawable at once. Until then they are
# measured but not mappable.
#
# HOW TO GET THEM, about five minutes:
#   Open Google Maps, right-click the spot, and the top line of the menu is
#   "17.99581, -76.74670". Click it to copy. Paste both numbers into gmaps()
#   below IN THAT ORDER.
#
# gmaps() exists specifically so the order cannot go wrong. Google shows
# latitude first; EVRange wants longitude first. Passing Google's numbers
# straight into a coordinate list is the single easiest mistake to make here,
# and it fails silently by putting the route in the Indian Ocean rather than
# raising anything. gmaps(lat, lon) does the swap and range-checks that the
# point is actually in Jamaica.
JAMAICA_BOUNDS = {"lat": (17.6, 18.6), "lon": (-78.5, -76.1)}


def gmaps(lat: float, lon: float) -> list[float]:
    """
    Take a Google Maps coordinate pair in its displayed order and return the
    [lon, lat] order EVRange expects.

    Raises rather than warns. A silently transposed coordinate produces a
    plausible-looking route somewhere else entirely, which is exactly the kind
    of confident wrong output this project keeps having to catch.
    """
    lo, hi = JAMAICA_BOUNDS["lat"]
    if not lo <= lat <= hi:
        raise ValueError(
            f"latitude {lat} is outside Jamaica ({lo} to {hi}). "
            f"Did you paste longitude first? gmaps() wants Google's order, "
            f"latitude then longitude.")
    lo, hi = JAMAICA_BOUNDS["lon"]
    if not lo <= lon <= hi:
        raise ValueError(
            f"longitude {lon} is outside Jamaica ({lo} to {hi}). "
            f"Jamaican longitudes are negative.")
    return [float(lon), float(lat)]


_DMS_RE = re.compile(
    r"""(\d+)\s*[°d]\s*(\d+)\s*['′]\s*([\d.]+)\s*["″]?\s*([NSEW])""",
    re.IGNORECASE | re.VERBOSE)


def dms(text: str) -> list[float]:
    """
    Parse the degrees-minutes-seconds string Google Maps shows and return
    [lon, lat] for EVRange.

        dms('''18°00'19.3"N 76°44'30.8"W''')  ->  [-76.741889, 18.005361]

    This exists because converting DMS to decimal by hand is where the first
    round of coordinates went wrong: the latitude came out right and the
    longitude was mistyped, which put a route fifteen kilometres west of where
    it belonged while still producing a valid distance and a plausible cost.

    Copying the string straight out of Google removes the arithmetic. The
    hemisphere letters carry the sign, so W and S cannot be forgotten.
    """
    found = _DMS_RE.findall(text)
    if len(found) != 2:
        raise ValueError(
            f"expected two DMS coordinates with N/S/E/W, found {len(found)} "
            f"in {text!r}. Paste exactly what Google Maps shows, for example "
            "18°00'19.3\"N 76°44'30.8\"W")
    vals = {}
    for deg, mins, secs, hemi in found:
        v = int(deg) + int(mins) / 60.0 + float(secs) / 3600.0
        h = hemi.upper()
        if h in ("S", "W"):
            v = -v
        vals["lat" if h in ("N", "S") else "lon"] = v
    if "lat" not in vals or "lon" not in vals:
        raise ValueError(f"need one N/S and one E/W value, got {text!r}")
    return gmaps(round(vals["lat"], 6), round(vals["lon"], 6))


# Paste coordinates here. Either form works:
#   from decimal, in Google's displayed order:  gmaps(17.9887, -76.7860)
#   straight from Google's DMS readout:        dms('''18°00'19.3"N 76°44'30.8"W''')
# Prefer dms(), since it does the arithmetic for you.
PLACES: dict[str, list[float] | None] = {
    "Crossroads":     gmaps(17.9887, -76.7860),
    "South Parade":   gmaps(17.9695, -76.7936),
    "Half Way Tree":  gmaps(18.0118, -76.7983),
    "Three Miles":    gmaps(17.9984, -76.8248),
    "UWI backgate":   dms("""18°00'19.3"N 76°44'30.8"W"""),
    "Mackville":      gmaps(18.0452, -76.8230),   # TotalEnergies, Mackville Terrace
    "Fi-wi Mary":     gmaps(18.0536, -76.8470),   # Fi-wi Mary gas station, Red Hills Rd
    "Harbour View":   dms("""17°56'57.1"N 76°43'08.6"W"""),   # Harbour View roundabout
    "Duhaney Park":   gmaps(18.0261, -76.8474),   # Duhaney Park
}


def _runs_with_coords() -> list[dict]:
    """
    Measured runs whose endpoints both have coordinates. Returns an empty list
    until PLACES is filled, which is why the picker currently shows only the
    three routes Rohan supplied.
    """
    out = []
    for run, origin, via, dest, km, kwh in MEASURED_URBAN_RUNS:
        a, b = PLACES.get(origin), PLACES.get(dest)
        if a is None or b is None:
            continue
        out.append({
            "key": f"run-{run}",
            "label": f"{origin} to {dest} via {via}",
            "start": a, "end": b,
            "measured_km": km, "measured_kwh": kwh,
            "run_id": run,
        })
    return out


def _haversine_km(a: list[float], b: list[float]) -> float:
    """Great-circle distance between two [lon, lat] points."""
    import math
    R = 6371.0
    lo1, la1 = math.radians(a[0]), math.radians(a[1])
    lo2, la2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))


def check_coordinates() -> list[dict]:
    """
    Sanity-check entered coordinates against the recorded road distances.

    The test that actually bites is ratio < 1: road distance cannot be shorter
    than the straight line between the same two points, so a ratio below 1
    means an endpoint is in the wrong place. Nothing else about the result
    would look wrong. The distance is well formed, the cost is plausible, and
    the map draws a line. This is the only signal available.

    A first attempt at filling PLACES from memory failed six of sixteen runs on
    exactly this test, which is why it exists.

    Returns one entry per problem, empty when everything checks out.
    """
    problems = []
    for r in _runs_with_coords():
        straight = _haversine_km(r["start"], r["end"])
        road = distance_for(r["run_id"], r["measured_km"])
        if straight <= 0:
            problems.append({"run": r["run_id"], "label": r["label"],
                             "severity": "error",
                             "message": "start and end are the same point"})
            continue
        ratio = road / straight
        if ratio < 1.0:
            problems.append({
                "run": r["run_id"], "label": r["label"], "severity": "error",
                "ratio": round(ratio, 2),
                "message": (f"recorded road distance {road} km is shorter than "
                            f"the straight line {straight:.2f} km. Impossible, "
                            f"so one of the two endpoints is wrong.")})
        elif ratio > 2.0:
            problems.append({
                "run": r["run_id"], "label": r["label"], "severity": "warning",
                "ratio": round(ratio, 2),
                "message": (f"road distance {road} km is {ratio:.1f}x the "
                            f"straight line {straight:.2f} km. Possible on a "
                            f"winding route, worth checking the endpoints.")})
    return problems


def coordinate_status() -> dict:
    """How much of the measured set is currently usable."""
    have = [k for k, v in PLACES.items() if v is not None]
    return {
        "places_total": len(PLACES),
        "places_done": len(have),
        "places_missing": [k for k, v in PLACES.items() if v is None],
        "runs_routable": len(_runs_with_coords()),
        "runs_total": len(MEASURED_URBAN_RUNS),
        "problems": check_coordinates(),
    }


if __name__ == "__main__":
    # python dashboard/routes.py  checks whatever is currently in PLACES.
    st = coordinate_status()
    print(f"{st['places_done']} of {st['places_total']} places have coordinates, "
          f"{st['runs_routable']} of {st['runs_total']} runs routable")
    if st["places_missing"]:
        print("missing:", ", ".join(st["places_missing"]))
    probs = st["problems"]
    if not st["runs_routable"]:
        print("\nNothing to check yet. Fill in PLACES using gmaps(lat, lon).")
    elif not probs:
        print("\nAll routable runs pass the distance check.")
    else:
        print(f"\n{len(probs)} problem(s):")
        for p in probs:
            print(f"  [{p['severity']}] run {p['run']}, {p['label']}")
            print(f"      {p['message']}")


def selectable_routes() -> list[dict]:
    """
    Routes fit to offer in the UI: Rohan's three confirmed pairs, plus every
    measured Kingston run whose endpoints have been given coordinates.

    The Kingston runs appear automatically as PLACES is filled in, so adding
    nine coordinate pairs turns on sixteen routes without touching this file.
    """
    opts = [{"value": k, "label": v["label"]} for k, v in MEASURED_ROUTES.items()]
    opts += [{"value": r["key"], "label": r["label"]} for r in _runs_with_coords()]
    return opts


def resolve_route(key: str) -> dict | None:
    """One lookup for both sources, so callers do not need to know which is which."""
    if key in MEASURED_ROUTES:
        return MEASURED_ROUTES[key]
    for r in _runs_with_coords():
        if r["key"] == key:
            return r
    return None


# ── Tolls ────────────────────────────────────────────────────────
# EVRange returns hasTolls as a boolean only, detected geometrically from
# bounding boxes over the T1 (Portmore) and T2 (May Pen) corridors. It does not
# return an amount, so the cost sits here.
#
# VERIFIED: Portmore plaza, Class 1, only. The T1 corridor also has plazas at
# Vineyards, May Pen and Williamsfield whose rates have NOT been checked. Do
# not assume one rate covers a corridor.
TOLL_RATES_JMD = {
    "portmore_class1": {
        "amount": 400.0,
        "class": "Class 1 (motorcycles, cars, light vans)",
        "plaza": "Portmore",
        "corridor": "T1",
        "payment": "cash or card, non T-Tag",
        "effective": "2026-08-01",
        "source": ("TransJamaican Highway 2026 toll rate review, effective "
                   "1 August 2026. https://www.transjamhighways.com/toll_rates/ "
                   "and Jamaica Observer, 24 July 2026."),
        "caveat": ("T-Tag holders pay J$370 until 31 October 2026, then J$390. "
                   "The J$400 figure is the non T-Tag rate and is the "
                   "conservative choice for an operator cost model."),
    },
}

TOLLS_PENDING = (
    "Rates for the Vineyards, May Pen and Williamsfield plazas, and for "
    "vehicle classes above Class 1, are not yet sourced. A route flagged "
    "hasTolls that does not pass Portmore will currently be costed at zero."
)


def toll_cost_jmd(has_tolls: bool, return_trip: bool = False) -> tuple[float, str]:
    """
    Toll cost for a route, with the basis returned alongside so the UI can
    show it rather than presenting a bare number.

    Only the Portmore Class 1 rate is verified, so this deliberately returns a
    known-incomplete figure with an explicit caveat rather than a confident one.
    """
    if not has_tolls:
        return 0.0, "No toll corridor detected on this route."
    r = TOLL_RATES_JMD["portmore_class1"]
    amount = r["amount"] * (2 if return_trip else 1)
    basis = (f"J${r['amount']:,.0f} {r['plaza']} {r['class']}"
             f"{', each way' if return_trip else ''}. {r['caveat']} "
             f"Detection is geometric, from EVRange bounding boxes, not a live "
             f"toll feed. {TOLLS_PENDING}")
    return amount, basis
