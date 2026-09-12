# Privacy law — what applies, and what it actually requires

> **Verify before quoting.** Every threshold, deadline, fee and enforcement
> status in this file is the kind of thing that changes between the writing and
> the reading. Structural rules (there is a right to deletion; consent must be
> affirmative) are stable. Numbers are not. Search for the current position
> before you state one as fact, and if you can't verify, say the rule exists
> and the figure needs checking. A confidently wrong threshold is worse than an
> acknowledged gap.

## The shape of the problem

Privacy law is not one regime you either fall under or don't. It is a set of
overlapping regimes, each triggered by a different thing:

- **Where your users are** (GDPR, UK GDPR, US state laws, Australian Privacy Act)
- **What kind of data** (health, biometric, children's, financial — see
  `high-risk-categories.md`)
- **What you do with it** (selling, sharing for ads, automated decisions,
  training a model)
- **How big you are** (several US state laws have volume or revenue thresholds;
  the EU has almost none)

The practical consequence for a small team: you are probably in scope for more
than you think, and the work required is mostly the same work regardless of
which regime is driving it. Write one good policy, build one deletion path, keep
one subprocessor list, and you satisfy most of several regimes at once.

## EU / EEA — GDPR

Applies if you offer goods or services to people in the EU, or monitor their
behaviour there. Your own location is irrelevant. There is no small-business
exemption from the core obligations.

**Lawful basis.** Every purpose needs one, decided before you process, and
recorded. In practice, for a typical SaaS:

| Purpose | Usual basis | Note |
| --- | --- | --- |
| Creating and running the account | Contract | The service they asked for |
| Billing, tax records | Legal obligation / contract | Retention here is set by tax law, not by you |
| Security, fraud prevention, abuse | Legitimate interests | Document the balancing test, briefly |
| Product analytics | Consent (EU) or LI (contested) | The cookie rule bites first regardless |
| Marketing email | Consent | Soft opt-in for existing customers in some states |
| Training a model on user content | Consent, realistically | Do not try to squeeze this into LI |

Consent, where you rely on it, has to be freely given, specific, informed and
unambiguous — an affirmative action. **A pre-ticked box is not consent**, and it
is one of the most enforced points because it is visible from outside the
product. Bundling marketing consent with accepting the terms fails the "freely
given" test. Withdrawing must be as easy as giving.

**Transparency (Art. 12–14).** Plain language, concise, accessible, free.
Legalese is a defect here, not caution. You must say who you are, what you
collect, why, on what basis, who receives it, whether it leaves the EU and
under what safeguard, how long you keep it, and what rights people have.

**Rights.** Access, rectification, erasure, restriction, portability, objection,
and not to be subject to solely automated decisions with legal or similarly
significant effects. Respond within one month, extendable by two for complex
requests. Free, unless the request is manifestly unfounded or excessive.

**Transfers.** Sending personal data outside the EEA needs a mechanism —
adequacy, Standard Contractual Clauses, or a specific derogation. The practical
form this takes for a small team: your US-based providers offer SCCs or an
adequacy-framework certification in their DPA. Accept the DPA, keep a copy, and
name the provider in your subprocessor list. Note that "we use a US LLM API" is
a transfer, and it is the one people most often fail to identify as one.

**Breach notification.** To the supervisory authority within 72 hours of
becoming aware, unless unlikely to result in risk. To affected individuals
without undue delay where the risk is high. You cannot do this in 72 hours
without a written runbook prepared in advance — see `security-baseline.md`.

**DPO and records.** A DPO is required only in specific cases (public
authority, large-scale systematic monitoring, large-scale special-category
data). Records of processing (Art. 30) have a small-organisation carve-out that
is narrower than people assume — it falls away if processing is not occasional,
which covers running a live service. Keep the record; it is a one-page table
and it is the same table as your data inventory.

**ePrivacy / the cookie rule.** Separate from GDPR and often mis-stated.
Consent is required *before* storing or reading anything on a user's device
that is not strictly necessary — cookies, localStorage, pixels, fingerprinting
— whether or not the data is personal. "Strictly necessary" means necessary to
deliver the service the user asked for: a session cookie, a load-balancer
cookie, a consent-state cookie. Analytics is not strictly necessary, however
much you'd like it to be. The pattern regulators keep penalising is the banner
that fires the tag on page load and asks afterwards, and the banner where
"Accept all" is one click and refusing takes three.

## UK

UK GDPR plus the Data Protection Act; substantively close to the EU regime with
its own regulator (the ICO) and its own reform trajectory. If you serve both,
build to the EU standard and you are covered. The ICO publishes unusually
readable small-business guidance — worth linking the user to it directly.

## United States

No single federal privacy law. What you actually have to deal with:

**State comprehensive laws.** A growing group of states, each with its own
applicability thresholds (typically tied to number of residents' records
processed and/or revenue, often with a lower threshold if you sell data). Most
small products fall under the thresholds at launch — which makes this a
textbook "know about it" item: name the threshold, say what changes when they
cross it, and move on. **Which states are in force and at what threshold
changes constantly. Look it up.**

Where they mostly agree: notice at collection, access, deletion, correction,
portability, opt-out of targeted advertising and of "sale"/"sharing", limits on
sensitive data, and honouring an opt-out preference signal (Global Privacy
Control) in several states.

**The "sale" trap.** Several state laws define "sale" and "share" broadly
enough that passing identifiers to advertising or analytics services can count,
with no money changing hands. A hobby project running an ad pixel can be
"selling" data as the statute defines it. If there is an ad pixel, raise it.

**Sector laws that bite regardless of size:** HIPAA (only for covered entities
and business associates — most health apps are neither, which surprises
people), GLBA (financial), FERPA (education), COPPA (under-13), plus state
biometric statutes, of which Illinois BIPA is the one with a private right of
action and the litigation record to match.

**The FTC.** Section 5 unfair-or-deceptive-practices authority applies to
everyone, at any size, with no threshold. This is the one that makes an
inaccurate privacy policy legally dangerous rather than merely embarrassing:
saying you do something you don't do is a deceptive practice. It is also the
basis for the auto-renewal and dark-pattern actions — see
`payments-and-billing.md`.

## Australia

The Privacy Act and the 13 Australian Privacy Principles. Historically there
was a small-business exemption below an annual turnover threshold, but it has
carve-outs (health service providers, trading in personal information, credit
reporting, contracted service providers) and is under active reform pressure.
**Check whether the exemption still exists and still applies before relying on
it** — building to the APPs anyway is the sane default for anything that might
grow, and it is largely the same work as GDPR.

What the APPs require that catches people out:

- **APP 1 — open and transparent management.** A clearly expressed, up-to-date
  privacy policy is a standalone requirement, not just a disclosure vehicle.
  You must have one even where you'd otherwise be lightly regulated.
- **APP 3 — collection.** Collect only what is reasonably necessary for your
  functions. Sensitive information (health, biometrics, race, religion, sexual
  orientation, criminal record, union membership) generally needs consent.
- **APP 5 — notification at collection.** Tell people at the time, including
  who you are, why you're collecting, who you'll disclose to, and whether any
  recipients are overseas — and which countries, if practicable.
- **APP 6 — use and disclosure.** Only for the primary purpose, or a secondary
  purpose the person would reasonably expect and which is related.
- **APP 8 — cross-border disclosure.** Before sending personal information
  overseas you must take reasonable steps to ensure the recipient complies with
  the APPs, and you generally remain accountable for their handling of it.
  Every US-hosted provider in your stack is an APP 8 question.
- **APP 11 — security and destruction.** Protect it, and **destroy or
  de-identify it when you no longer need it**. This is a positive deletion
  obligation independent of any user request, and almost nobody implements it.
- **APP 12 / 13 — access and correction**, generally within 30 days.

**Notifiable Data Breaches scheme.** An eligible data breach — unauthorised
access or disclosure likely to result in serious harm — must be assessed
promptly (there is a statutory assessment window, typically expressed in days)
and notified to the OAIC and to affected individuals. Treat it operationally
the same as the GDPR 72-hour clock: the only way to meet either is a runbook
written before the incident.

**Direct marketing (APP 7)** and the Spam Act overlap: Australian
anti-spam rules require consent, sender identification, and a working
unsubscribe in every commercial message, with per-message penalties. The
unsubscribe link is not optional and must work without requiring a login.

## Everywhere else

Canada, Brazil, India, Japan, South Korea, China, Switzerland, Singapore, New
Zealand, South Africa, Nigeria and others have their own sections in
**`jurisdictions.md`**. Read that file when a product has users outside the
three regimes above.

Each section there carries a status line — `Detailed` or `Structural` — saying
how much weight to put on it. Most are `Structural`: the shape of the regime is
right, the specifics need looking up. That is the honest state of this skill's
coverage, and the file says so rather than reading as though it were
authoritative everywhere.

Four that change the answer most often, and are easy to miss:

- **Canada** — Quebec's Law 25 is materially stricter than the federal
  baseline, and CASL is stricter than almost anyone's anti-spam rules.
- **India** — children are under **18**, with verifiable parental consent and
  a prohibition on tracking them. This one causes redesigns.
- **Japan** — cross-border transfer consent must carry specific information
  about the destination country. A generic "we may transfer overseas" line does
  not satisfy it.
- **South Korea** — consent must be separate and itemised per purpose. A single
  "I agree to the privacy policy" checkbox does not work.

## What "good" looks like for a small product

The whole EU/US/AU overlap collapses into a short list of things to actually
build:

1. **A privacy policy that is true.** Derived from the data inventory. Names
   the actual services. Real retention numbers.
2. **A subprocessor list** you keep updated, linked from the policy.
3. **A deletion path** that covers database, files, backups, logs, caches and
   third-party copies — plus a retention job that deletes on a schedule without
   anyone asking.
4. **An export route** that returns the user's records as JSON or CSV.
5. **A consent gate** for non-essential storage, if you have EU/UK users, that
   blocks the tag until consent and makes refusing as easy as accepting.
6. **A breach runbook** with names, contacts and a clock.
7. **A DSAR inbox** — an address that is monitored, and a note of what you did
   and when, for each request.

Everything else is documentation of these seven things.
