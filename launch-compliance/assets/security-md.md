<!--
TEMPLATE: SECURITY.md — vulnerability disclosure policy.

Write this to the repository root as SECURITY.md (GitHub surfaces it in the
Security tab and in the "report a vulnerability" flow). Optionally also publish
/.well-known/security.txt on the website.

The point of this file is that a researcher who finds something has an obvious
place to send it. Without one, their options are an unmonitored support address
or a public post.

Only commit to a response time you will meet. A missed 24-hour promise is worse
than an honest 5-day one.

Delete every one of these HTML comments before publishing.
-->

# Security Policy

## Reporting a vulnerability

Email **[SECURITY EMAIL]**. [Or use GitHub's private vulnerability reporting on
this repository.]

Please include:

- what you found, and where
- steps to reproduce it
- what an attacker could do with it
- anything you'd like credited [and how you'd like to be named]

You'll get an acknowledgement within **[2 business days]** and an assessment
within **[7 business days]**. We'll keep you updated while we work on a fix,
and tell you when it ships.

[If you'd like to encrypt your report, our PGP key is at [LINK].]

## What we ask

- Give us reasonable time to fix the issue before disclosing it publicly.
  [We suggest 90 days, and we'll work with you if you need something different.]
- Don't access, modify or delete data that isn't yours. If you accidentally
  access someone else's data, stop and tell us.
- Don't run attacks that degrade the service for other people — no denial of
  service, no spam, no brute forcing against production.
- Use test accounts you create yourself.

## What we commit to

- We won't pursue legal action against you for research done in good faith
  under this policy.
- We'll respond within the times above.
- We'll credit you when we fix it, if you'd like to be credited.
- [We don't currently run a paid bug bounty. / Rewards are at our discretion:
  [DETAILS].]

## In scope

- [example.com and its subdomains]
- [The API at api.example.com]
- [This repository]

## Out of scope

<!-- Being specific saves everyone time. These are the reports every project receives and nobody wants. -->

- Findings from automated scanners without a demonstrated impact
- Missing security headers with no exploitable consequence
- Rate limiting on non-sensitive endpoints
- Social engineering of our staff or users
- Physical attacks
- Reports about third-party services we use — please report those to the
  provider directly
- [Self-XSS, clickjacking on pages with no sensitive action, missing SPF/DMARC
  on non-sending domains]

## Supported versions

<!-- Delete this section if the product is a hosted service with a single live version, which is the common case. -->

| Version | Supported |
| --- | --- |
| [1.x] | [Yes] |
| [< 1.0] | [No] |

---

[LEGAL ENTITY NAME] — last updated [DATE]
