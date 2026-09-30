# Note to Rohan, 16 September 2026: first results from the live server

Context: hostname and key arrived on 16 September, the cache populated in
four minutes with no failures, and the first comparison against the recorded
runs shows the model returning roughly half the measured energy, no response
to gradient, and toll flags on routes that touch no toll road. This replaces
the earlier chase note. Register informal, like the earlier notes. Can be
sent as written. The numbers come straight from
`scripts/fetch_evrange_cache.py` output on 16 September.

The cache is populated locally but deliberately NOT committed until he
answers, because the dashboard would show these figures under a green
"Figures from EVRange" banner. Refetch with `--force` once he has fixed
whatever it is.

---

Hey Rohan, thanks for the key, it works. I pulled `/api/ev-models`, mapped
the Yuan Plus and the 40 kWh Leaf, and fetched all 76 route and vehicle
combinations in four minutes at 3 second spacing, no errors, no 429s. So the
plumbing between us is fine.

The numbers are not, and I want to show you exactly what I'm seeing before
either of us assumes anything.

**1. Energy comes out at about half of what the car recorded.** Over the
sixteen Kingston runs I measured in the Yuan Plus, your model gives 6.65 kWh
across 94.1 km, which is 71 Wh/km. The car's own trip display gave 14.1 kWh
across 81 km, 173 Wh/km, and my uncertainty band on that is 151 to 204. So
you're outside the band by a factor of two, and that's not a distance-basis
issue, because your routed distances are longer than mine, not shorter. Even
the T4 highway run comes out at 95.7 Wh/km, and the example in your own docs
for that kind of run was 142.3. Is the server running the calibrated build?
Or is there an efficiency factor (drivetrain, battery-to-wheel) that's
applied in one place and not the other?

**2. Gradient doesn't seem to be doing anything.** The cleanest case is Red
Hills Road between Mackville and Fi-wi Mary, which I drove in both
directions: the car recorded 3.2 kWh going up and minus 1.3 kWh coming down.
Your model gives 0.37 kWh up and 0.38 kWh down. Same story on Old Hope Road
(car 0.7 vs 2.0 kWh by direction, model 0.52 vs 0.50). And the Spur Tree
round trip comes out at 1.6 kWh for 33 km up and down the hill. That reads to
me like the elevation lookup is returning flat everywhere on the deployed
server, which would also explain point 1: if every gradient is near zero,
everything falls to the 0.70 urban anchor. Worth checking whether the DEM or
elevation service is actually reachable from where it's running.

**3. `hasTolls` is true on 10 of my 19 routes,** and only one of them, T4,
touches a toll road. The others are Kingston to Red Hills, Half Way Tree to
Three Miles, the Red Hills Road runs, and Spanish Town Road between Three
Miles and Duhaney Park. So the T1 bounding box is covering a good part of
west Kingston. I've stopped treating the flag as evidence of a toll on my
side, but it would be better fixed at source. If you can return the corridor
id rather than a boolean, I can cost each plaza properly.

Two smaller things to confirm rather than fix:

- For `returnTrip: true`, `distanceKm` and `avgWhkm` are per direction and
  `socNeededPct` is for the round trip. I've coded to that; just tell me if
  it's not what you intended.
- Your Yuan Plus is listed at 55.4 kWh usable. The car ATL priced for me is
  the Standard Range with a 49.92 kWh nominal pack, and usable can't exceed
  nominal, so I think yours is the 60.48 kWh Extended Range. Which is it? It
  changes the battery percentage figures, not the cost.

Still on the list from before: your spreadsheet of runs with coordinates and
consumption, and whether the Leaf has its own calibration or inherits the
Yuan Plus correction.

I'm holding the cache locally and not committing it until you've had a look,
because as things stand my dashboard would put these figures on screen under
a "from EVRange" banner and I can't stand behind them yet. Once you've
changed something on the server I can refetch the lot in four minutes. Happy
to send you the 76 request bodies if you want to reproduce it your end.

Andrew
