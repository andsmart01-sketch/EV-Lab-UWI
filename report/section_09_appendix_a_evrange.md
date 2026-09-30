# Appendix A: The EVRange Energy Model

---

The Route Cost Map (Section 5.8) takes its energy figures from EVRange, an unpublished model built by a colleague from the field runs this study also drew on. Because the model cannot be inspected by a reader, its author's own description is reproduced here in full, as supplied for this report on 7 August 2026 (R. Brown, personal communication, August 7, 2026). Nothing in it has been edited. The interpretation in Section 5.8 is this study's.

## A.1 Model Description, as Supplied

> Energy consumption is computed per micro-segment (approximately 500m spacing on long steps, full waypoint resolution on steps under 3km) using a physics-based model. Each segment calculates aerodynamic drag power (½ρCdAv³), rolling resistance (Crr × m × g × v), gravitational climb power (mg sin θ × v), and regenerative braking recovery from both gravity on descent and kinetic energy at stops. HVAC load is modelled as a function of ambient temperature, ramping from 0W at 22°C to full cooling capacity at 38°C. An idle fraction derived from step speed (0.35 at <20 km/h, down to 0.02 at highway speed) captures stop-start overhead. A piecewise terrain correction function, calibrated from measured BYD Yuan Plus runs on Jamaican roads (T1 highway, Red Hills, Spur Tree Hill), scales the physics output to match observed consumption. At near-flat gradients the correction additionally interpolates between a low-speed urban anchor (0.70, calibrated from Kingston urban runs) and a highway anchor (1.09, calibrated from T4 at 83 km/h). The inputs ambientTempC directly scales HVAC load; drivingMode applies a multiplier of 0.93 (eco), 1.00 (normal), or 1.10 (sport) to final Wh/km; cargoKg and passengerCount enter the mass term in all force calculations; tyrePressureMult scales rolling resistance coefficient.

On toll detection, from the same correspondence:

> It currently detects the T1 (Portmore) and T2 (May Pen) Highway 2000 corridors by bounding box. It returns a boolean, not a toll amount.

The author asked that requests be limited to 20 per minute per IP address, and that the model be cited as: EVRange (2026), physics-based EV range model calibrated on Jamaican road network, unpublished. Route energy estimates via /api/routing/calculate.

## A.2 Interface

The dashboard calls one endpoint, `POST /api/routing/calculate`, from the server side, with the access key held in an environment variable. The request and response fields, as documented by the author, are:

| Request field | Meaning | Dashboard control |
|---|---|---|
| `evSpecId` | Vehicle identifier from `/api/ev-models` | Vehicle selector |
| `startCoords`, `endCoords` | Longitude, latitude | Corridor preset or custom entry |
| `passengerCount` | Occupants, enters the mass term | Conditions, passengers |
| `cargoKg` | Load, enters the mass term | Conditions, cargo |
| `tyrePressureMult` | Scales rolling resistance | Held at 1.0 |
| `ambientTempC` | Scales cooling load | Conditions, temperature |
| `drivingMode` | eco, normal or sport multiplier | Conditions, driving mode |
| `currentSocPct` | Battery state of charge at departure | Battery slider |
| `returnTrip` | Out and back | Return trip checkbox |

| Response field | Meaning | Where it appears |
|---|---|---|
| `evModel`, `batteryUsableKwh` | Vehicle as modelled | Basis panel |
| `distanceKm`, `durationMin` | Routed distance and time | Distance card |
| `avgWhkm` | Mean consumption over the route | Electric cost card and basis |
| `socNeededPct`, `socAfterTripPct` | Battery used and remaining | Battery card |
| `chargeNeeded`, `chargeWarning` | Whether the trip fits in the charge available | Battery card and warning strip |
| `hasTolls` | Toll corridor touched, geometric detection | Toll line in the basis panel |
| `geometry` | Route as a GeoJSON LineString | Map |

## A.3 Corridors Supplied by the Author

Three measured corridors with usable start and end pairs were supplied on 7 August 2026 and are loaded as presets. Coordinates are longitude then latitude, as the model expects.

| Run | Corridor | Start | End |
|---|---|---|---|
| T4 | Portmore to UWI Mona, T1 highway | [-76.9876, 17.9488] | [-76.7467, 17.9958] |
| T7 and T8 | Spur Tree Hill, descent and ascent | [-77.5085, 18.0447] | [-77.4237, 17.9882] |
| Red Hills | Kingston to Red Hills | [-76.8072, 18.0089] | [-76.8334, 18.0812] |

The author holds further runs with coordinates and measured consumption, which had not been received at the time of writing.
