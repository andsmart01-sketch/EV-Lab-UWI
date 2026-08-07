# Follow-up to Rohan

Reply to his answers of 7 August 2026. Short, because the last one was long.
Five asks, all small. Can be sent as written.

---

Thanks, that's everything I needed. Starting on my side now so it's ready when
the server is.

Five quick things.

**1. Send the Excel.** You mentioned you have all the other trips with
coordinates and usage. That sheet is the most useful thing you've offered,
because the measured consumption is the only way I can check the API's output
against what we actually recorded. Three coordinate pairs is enough to start
building, but I want the measured numbers before I put anything in the report.
Whatever state it's in is fine, I can clean it up.

**2. Is the terrain correction Yuan Plus only?** Reading your description, the
physics is generic but the piecewise terrain correction and the 0.70 urban and
1.09 highway anchors are all calibrated from Yuan Plus runs. For Kingston
corridors that urban anchor is doing most of the work, since it's pulling the
raw physics down by about thirty per cent. So I want to be clear on what happens
when the vehicle is not a Yuan Plus. Does the Leaf have its own calibration, or
does it inherit the Yuan Plus correction with only the mass and drag terms
changing?

Not a criticism. I have the same problem in my own data, where I applied a
consumption factor measured on one car to three, and it's on my list to fix. I
just need to describe it accurately in the methods.

**3. Let's restrict the module to the Yuan Plus and the Leaf.** Rather than you
sourcing specs for my other vehicles, I'd rather ship two vehicles that are
genuinely calibrated than eleven that are partly guessed. My dataset only has
battery capacity anyway. I don't hold kerb weight, drag coefficient, frontal
area or regen efficiency for any of them, so anything you added would be your
sourcing rather than mine, and I can't cite it properly in a report with my name
on it. Two honest vehicles is the better answer.

If the Leaf turns out to be uncalibrated per point 2, I'll ship one.

**4. What exactly is batteryUsableKwh?** My dataset holds nominal pack capacity,
which is usually a few per cent above usable. I want to be sure I'm not mixing
the two when I write up. Just tell me whether yours is manufacturer usable
capacity or something you derived.

**5. Heads up on how I'm calling it.** Given the laptop and tunnel setup, I'm
building it cache first rather than live first. I'll pre-fetch each preset route
and vehicle at default conditions once, commit that cache to my repo, and serve
from disk by default. The live call becomes an optional refresh that fills in
the adjustable controls when the server happens to be up.

That means my steady-state load on you is close to zero, and the module still
works on an examiner's machine with no network at all. It does mean one burst of
requests when I first populate the cache. I'll keep it under your 20 a minute,
but tell me if you'd rather I did it at a particular time.

Also taking your point on the tolls, I'll source the TransJamaican rates for T1
and T2 myself and note in the methods that your detection is geometric rather
than from a live toll feed.

Citation noted, I'll use EVRange (2026) as you wrote it and put your model
description in an appendix, since it's unpublished and an examiner won't be able
to inspect the code.

Andrew
