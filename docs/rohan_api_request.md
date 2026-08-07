# API access request to Rohan

Reply to Rohan's routing API message of 7 August 2026.

Context: Rohan collected consumption data on the same field runs as this
project, including long distance routes to Manchester and back. His routing
API returns distance, duration, energy use and battery state for a given EV
and route. It fills the gap that killed the Route Cost Map, which was that no
mapping source was agreed and no corridor distances were ever measured.

This asks for the six things needed before the module can be built. Nothing is
bracketed; it can be sent as written. Register is informal because his message
was.

---

Hey Rohan, thanks for this, it fills the one gap I had.

I want to build it into the dashboard properly as a module rather than a
separate page, so there are a few things I need from you before I can start.

Quick context on why some of this looks different from what you described. My
dashboard is Plotly Dash, so it is Python running on a server rather than a
static page with JavaScript in it. That means I will not be doing the fetch in
the browser. I will call your endpoint from Python server side and keep the key
in an environment variable so it never reaches the page source. Same request
and response shapes you sent, just made from a different place. It is less work
on my end, not more, so no problem there.

What I need from you:

**1. The real hostname.** Your message has https://your-api-domain.com in it,
including on its own line at the bottom. I think that is the placeholder from
your docs template. It does not resolve, so there is nothing for me to point at
yet.

**2. An API key.** The header line reads `x-api-key: <the key you give them>`,
so I think that documentation was written from your side of the fence rather
than mine.

**3. The output of /api/ev-models**, or just a list of models with their
evSpecIds. I need to check your list against the 21 vehicles in my dataset and
build a mapping between them. The ones that matter most are the BYD Yuan Plus
2024, the used Nissan Leaf and the Nissan Tiida, because those drive my taxi
tool and my calculator. If any of them are not in your list, say so and I will
work out what to do about it.

**4. A short description of what the model does to produce avgWhkm.** Not
because I doubt it. I know it is built on the runs we did together. It is that
I have to write it up in the methods section of my report and I would rather
quote you than guess. Enough to answer: does it interpolate between the runs we
measured, fit a curve, or compute it from drag and rolling resistance? And what
it does with ambientTempC, drivingMode, cargoKg and tyrePressureMult, since
those are all inputs and I will be exposing them as controls on the page.

**5. Rate limits, or whatever you would prefer.** Dash callbacks fire on every
input change, so if I am not careful a slider drag sends you thirty requests in
five seconds. I am going to cache responses locally either way, but tell me what
you want and I will build to it.

**6. Whether the server will still be up through submission**, and roughly how
long after. My other seven modules read local files and work forever. This one
stops working the day your server goes off, and if that happens while an
examiner has the page open it just breaks. If uptime is uncertain I would rather
cache a fixed set of routes to disk and ship those as a fallback, which is easy
if I know now rather than later.

**On routes.** I want to use the corridors we actually drove rather than a free
text search box. Partly because it is reproducible, but mainly because it means
I can check your output against what we measured in the car. Can you send me
start and end coordinates for the runs you did, including the Manchester ones?
I will load them as presets. If a route did not have a clean start and end
point, give me your best pair and I will note it.

**On the map.** I am going to use Plotly's map component rather than Mapbox GL
JS directly, because it drops into Dash without a separate JavaScript layer. It
still draws your geometry.coordinates as a LineString, and I can point it at
Mapbox tiles if their basemap looks better for Jamaica than OpenStreetMap. So
your suggestion stands, it just goes through Plotly.

**On what I am adding.** Your API gives distance, duration and energy. It does
not give cost, so that part is mine. I will take your avgWhkm and multiply it
by the charging rates I collected, Evergo at a flat J$96/kWh and JPS Charge n Go
on time of day pricing, then compare it against the same route in a Probox at
measured Petrojam pump prices. So the module is your routing layer joined to my
cost layer. Tell me how you want to be cited and I will put it in the report and
on the page itself.

Also, your response has hasTolls in it, which I had not thought about. Highway
2000 tolls are a real operating cost my taxi module ignores completely at the
moment, so that is useful on its own.

On your offer to make the changes, thanks, but I will do the Dash side since it
is my codebase and my supervisor has to be able to follow it. The repo is
current if you want to look at how the other modules are put together. I will
shout if I get stuck on the request side.

Send those six things over and I will start.

Andrew
