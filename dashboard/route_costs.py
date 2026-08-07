"""
Cost and emissions layer for the Route Cost Map.

DIVISION OF LABOUR
------------------
EVRange supplies distance, duration and energy (Wh/km). It does not supply
cost, and cannot, because cost depends on Jamaican prices this project
collected: Petrojam pump prices, JPS tariffs, and the Evergo and Charge n Go
charging rates.

So this module takes energy in and puts money out. Everything here is our data
and our arithmetic. Nothing in this file comes from the API.

Every function takes its rates as arguments rather than importing them from
app.py. That keeps this testable on its own and avoids a circular import.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RouteCost:
    """One vehicle over one route. Money in J$, emissions in kg CO2."""
    distance_km: float
    energy_kwh: float = 0.0
    litres: float = 0.0
    energy_cost: float = 0.0
    toll_cost: float = 0.0
    co2_kg: float = 0.0
    basis: list[str] = field(default_factory=list)

    @property
    def total_cost(self) -> float:
        return self.energy_cost + self.toll_cost

    @property
    def cost_per_km(self) -> float:
        return self.total_cost / self.distance_km if self.distance_km else 0.0


def ev_route_cost(distance_km: float, avg_whkm: float, rate_jmd_per_kwh: float,
                  *, grid_intensity_kg_per_kwh: float = 0.0,
                  toll_jmd: float = 0.0, toll_basis: str = "",
                  rate_label: str = "") -> RouteCost:
    """
    Cost of driving one route electrically.

    avg_whkm comes from EVRange. rate_jmd_per_kwh is ours: J$96/kWh flat for
    Evergo, or the JPS Charge n Go rate for the time of day, or a home tariff.

    Charging losses are NOT applied here. EVRange reports energy at the wheels
    over the route, whereas a charging tariff bills energy into the vehicle,
    and the gap between them is charger and pack efficiency of roughly 10 to 15
    per cent. Applying a loss factor without measuring it would be inventing a
    number, so this understates the true charging cost slightly and says so.
    """
    energy_kwh = distance_km * avg_whkm / 1000.0
    cost = energy_kwh * rate_jmd_per_kwh
    basis = [
        f"{distance_km:,.1f} km at {avg_whkm:,.1f} Wh/km gives "
        f"{energy_kwh:,.2f} kWh, energy at the wheels, from EVRange.",
        f"Charged at J${rate_jmd_per_kwh:,.2f}/kWh{f' ({rate_label})' if rate_label else ''}.",
        "Excludes charging and pack losses, roughly 10 to 15 per cent, which "
        "this project has not measured. The electric figure is therefore a "
        "lower bound.",
    ]
    if toll_basis:
        basis.append(toll_basis)
    return RouteCost(
        distance_km=distance_km,
        energy_kwh=energy_kwh,
        energy_cost=cost,
        toll_cost=toll_jmd,
        co2_kg=energy_kwh * grid_intensity_kg_per_kwh,
        basis=basis,
    )


def ice_route_cost(distance_km: float, consumption_l_per_100km: float,
                   pump_price_jmd_per_litre: float,
                   *, co2_kg_per_litre: float = 0.0,
                   toll_jmd: float = 0.0, toll_basis: str = "",
                   price_label: str = "") -> RouteCost:
    """
    Cost of driving the same route on petrol, for comparison.

    consumption_l_per_100km comes from data/vehicles.py. Note the standing
    caveat on those figures: the urban uplift was measured on a single vehicle
    and applied to three, which is on the outstanding work list.
    """
    litres = distance_km * consumption_l_per_100km / 100.0
    cost = litres * pump_price_jmd_per_litre
    basis = [
        f"{distance_km:,.1f} km at {consumption_l_per_100km:,.1f} L/100km "
        f"gives {litres:,.2f} litres.",
        f"Fuel at J${pump_price_jmd_per_litre:,.2f}/litre"
        f"{f' ({price_label})' if price_label else ''}.",
    ]
    if toll_basis:
        basis.append(toll_basis)
    return RouteCost(
        distance_km=distance_km,
        litres=litres,
        energy_cost=cost,
        toll_cost=toll_jmd,
        co2_kg=litres * co2_kg_per_litre,
        basis=basis,
    )


def compare(ev: RouteCost, ice: RouteCost) -> dict:
    """
    Head to head over one route. Positive saving means the EV is cheaper.

    Percentages are guarded against a zero ICE cost, which happens when a
    price has not been entered yet rather than because petrol is free.
    """
    saving = ice.total_cost - ev.total_cost
    co2_saving = ice.co2_kg - ev.co2_kg
    return {
        "ev_total": ev.total_cost,
        "ice_total": ice.total_cost,
        "saving_jmd": saving,
        "saving_pct": (saving / ice.total_cost * 100.0) if ice.total_cost else None,
        "ev_per_km": ev.cost_per_km,
        "ice_per_km": ice.cost_per_km,
        "co2_saving_kg": co2_saving,
        "co2_saving_pct": (co2_saving / ice.co2_kg * 100.0) if ice.co2_kg else None,
        "cheaper": "ev" if saving > 0 else ("ice" if saving < 0 else "tie"),
    }
