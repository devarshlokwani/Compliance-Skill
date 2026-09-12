<!--
TEMPLATE: COMPLIANCE.md — the working document that stays in the repo.

This is the output of Phase 2 and the entry point for the next run. It is the
only document in the set written for the team rather than for users, so it can
be blunt.

Two things make it worth keeping rather than a one-off report:
  * owners and dates on open items
  * review triggers — the changes that mean the documents have gone stale

Fill in real names. "TBD" as an owner means nobody owns it.

Delete every one of these HTML comments before publishing.
-->

# Compliance status

**Last reviewed: [DATE]** · **Next review: [DATE or "on trigger"]**
**Owner: [NAME]**

What this records: what we decided, what's outstanding, and what should make us
look at this again. Not legal advice; see [DISCLAIMER LINK].

## Where we stand

[ONE PARAGRAPH, HONEST. e.g. "We collect email, name and uploaded transcripts
from users in the UK, EU and US. We take subscription payments through Stripe
and send transcript content to OpenAI for summarisation. Documents are
published and accurate as of [DATE]. Deletion is self-serve; backups clear on a
30-day rotation. Nothing is currently blocking."]

## Blocking

<!-- Do not open signups until these are done. If this section is empty, say so explicitly — an empty blocking list is a real and welcome result. -->

| # | Item | Owner | Due | Status |
| --- | --- | --- | --- | --- |
| 1 | [Rotate the Stripe key that was committed in [COMMIT]] | [NAME] | [DATE] | [Done / In progress] |
| 2 | [Publish privacy policy] | [NAME] | [DATE] | [ ] |

## Fix this month

| # | Item | Owner | Due | Status |
| --- | --- | --- | --- | --- |
| 1 | [Build account deletion endpoint — must clear S3, Sentry and PostHog too] | [NAME] | [DATE] | [ ] |
| 2 | [Cookie consent gate before PostHog loads] | [NAME] | [DATE] | [ ] |
| 3 | [Publish subprocessor list and link it from the privacy policy] | [NAME] | [DATE] | [ ] |
| 4 | [Write the incident runbook] | [NAME] | [DATE] | [ ] |

## Know about it

<!-- Thresholds not yet crossed, and what changes when they are. This is the most useful section six months from now. -->

| Thing | Where we are now | What happens at the trigger |
| --- | --- | --- |
| [US state privacy law thresholds] | [Below all of them] | [Crossing a state's threshold brings notice, opt-out and DSAR duties — re-check the current thresholds, they move] |
| [EU representative] | [Not required at our size/profile] | [Reassess if EU users become a substantial share] |
| [SOC 2] | [Not started] | [First enterprise customer will ask; 3-6 months of lead time] |
| [DPA requests] | [None yet] | [First business customer will send their own paper — budget legal review time] |
| [DMCA agent] | [Not registered] | [Register if we open up public sharing of uploads] |

## Polish

| # | Item | Owner | Status |
| --- | --- | --- | --- |
| 1 | [OG image and tags] | [NAME] | [ ] |
| 2 | [Real page title — still "Create Next App"] | [NAME] | [ ] |
| 3 | [Favicon] | [NAME] | [ ] |
| 4 | [Sitemap + robots.txt (current one is staging's `Disallow: /`)] | [NAME] | [ ] |

## Decisions we've made

<!-- Record the reasoning, not just the outcome. In six months nobody remembers why, and the "why" is what you need when someone asks whether it's still right. -->

| Date | Decision | Why |
| --- | --- | --- |
| [DATE] | [Retain raw transcripts for 12 months] | [Users asked for history; 12 months balances that against storage and exposure] |
| [DATE] | [No EU data residency for now] | [Provider's EU region costs more; revisit at first enterprise customer] |
| [DATE] | [Legitimate interests for security logging, consent for analytics] | [Analytics isn't strictly necessary, so the cookie rule applies regardless of basis] |

## Needs a lawyer

<!-- Be specific about the trigger and the question. "Talk to a lawyer at some point" gets ignored. -->

| Trigger | The question to ask | Status |
| --- | --- | --- |
| [We store voice recordings] | [Does Illinois BIPA apply to us, and what notice and written consent do we need before recording?] | [Not started] |
| [We're raising] | [Will our data practices survive diligence?] | [Not started] |

## Review triggers

**Run the compliance pass again when any of these happen.** This is the part
that keeps the documents from quietly becoming false.

- [ ] We add any new third-party service — including an internal tool that
      receives user data
- [ ] We add or change an AI feature, or a provider changes their training or
      retention defaults
- [ ] We open to a new country
- [ ] We add a paid tier, or change how billing works
- [ ] We add file uploads, or let users share content with each other
- [ ] We cross [10k / 100k] users
- [ ] We sign our first enterprise customer, or receive our first DPA
- [ ] We start collecting a new category of personal data
- [ ] Someone asks for their data, asks for deletion, or complains
- [ ] We have a security incident of any size
- [ ] [12 months pass since the last review]

## Evidence and references

- Last scan: [PATH TO compliance-scan.md] ([DATE])
- Data inventory: [LINK]
- Published documents: [LINKS]
- DPAs on file: [WHERE THEY'RE STORED]
- Incident runbook: [LINK]
