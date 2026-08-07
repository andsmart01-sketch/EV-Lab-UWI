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

# ── Named but not yet measured ───────────────────────────────────
# From report Section 8.3. These were identified as route-taxi corridors of
# interest and never surveyed. Endpoints are unknown, NOT approximated.
PENDING_ROUTES = {
    "hwt-papine":        "Half Way Tree to Papine",
    "hwt-three-miles":   "Half Way Tree to Three Miles",
    "downtown-crossroads": "Downtown to Crossroads",
    "manor-park":        "Manor Park corridor",
    "backgate-spanish-town": "Backgate to Spanish Town",
}


def selectable_routes() -> list[dict]:
    """Routes fit to offer in the UI. Only measured ones qualify."""
    return [{"value": k, "label": v["label"]} for k, v in MEASURED_ROUTES.items()]


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
