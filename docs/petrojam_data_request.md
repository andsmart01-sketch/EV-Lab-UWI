# Data access request to Petrojam

Send to: pr@petrojam.com
Copy: Dr Louis-Ray Harris (supervisor), so the request is on the record as departmental

Fill in the three bracketed items before sending. Keep it short. The person
reading it is in communications, not IT, and will forward it if it is clear.

---

**Subject:** Request for weekly ex-refinery price data, UWI Mona research project

Good day,

My name is Andrew Smart. I am a physics undergraduate at UWI Mona, working on
a research project supervised by Dr Louis-Ray Harris that compares the running
costs and emissions of electric vehicles against petrol and diesel vehicles in
Jamaica. Petrojam's weekly ex-refinery prices are the fuel cost basis for the
whole analysis, and I have been using the published series from
https://www.petrojam.com/price/ with attribution to Petrojam.

I am writing about two things.

First, I would like to ask how best to obtain the weekly series on an ongoing
basis. At the moment I copy the figures from the price page by hand each week.
That works but it is error prone, and I would rather rely on something you are
happy for me to use. If you publish a spreadsheet, a CSV, or any machine
readable feed, I would be grateful for a pointer to it. If not, would you be
willing to have the weekly figures sent to a mailing list, or for me to be
given access to retrieve the price page once a week?

Second, I should flag something in case it is not intended. Requests to
www.petrojam.com from a plain, clearly identified research client are being
refused with HTTP 403 by what appears to be an AWS load balancer. This affects
every path I tried, including /robots.txt itself. Your robots.txt, when I can
read it, says "User-agent: * / Disallow:", which permits automated access, so
the 403 looks like a separate filter rather than a deliberate policy. I have
not attempted to work around it, and I am not asking anyone to weaken a
security control. I am asking whether retrieving one page once a week is
something you can accommodate, and if so, how you would like me to do it.

For scale, the project needs a single page request once per week, on Thursday
evenings after publication. It is a student research project and the dashboard
is not a commercial product.

If a formal request under the Access to Information Act is the more
appropriate route, please say so and I will submit one.

Happy to answer any questions, or to share the project with you if that is
useful.

With thanks,

Andrew Smart
Department of Physics, The University of the West Indies, Mona
[your preferred contact email]
[your phone number, optional]
Supervisor: Dr Louis-Ray Harris, [his UWI email]

---

## Notes for you, not for the email

**Why mention the 403 at all.** It is concrete and actionable. Their IT can
check an ALB rule in minutes. Saying "your site blocks me" without evidence
gets ignored; naming AWS ELB, the 403, and the robots.txt contradiction gets
forwarded to someone who can act.

**Why say you did not work around it.** Because you did not, and because it
tells them you are asking rather than announcing. That matters for whether
they say yes.

**What to do with the reply.** Save it. Whatever they say, it goes in the
report. A documented request to the data holder is a stronger methods section
than a scraper, and a refusal or a non reply is itself a finding about the
accessibility of Jamaican energy data. Section 8 already covers data
availability limits and this belongs there.

**If they do not reply within two weeks**, submit the ATI request at
https://www.petrojam.com/contact-us/request-under-ati-act/ . Petrojam is a
public body and the Access to Information Act covers it. The statutory route
is slower but it produces a citable, dated response.
