---
name: launch-compliance
description: Audits a project for the legal, privacy, security and launch-readiness gaps it has already triggered, then drafts the documents and applies the fixes — privacy policy, terms of service, cookie consent, data deletion, subprocessor list, security baseline, sitemap and robots.txt, OG/social preview tags, accessibility defects, and a severity-ranked punchlist. Use this whenever a project is heading to production or the public — deploying, shipping, going live, opening signups, pushing to Vercel/Netlify/Fly/Railway, buying a domain, putting up a landing page or waitlist, submitting to an app store, or announcing on Product Hunt. Trigger it even when the person only mentions deploy mechanics and says nothing about legal or compliance; that is the main case this skill exists for. Also use it for privacy policy, terms, GDPR, CCPA, Australian Privacy Act, cookie banner, data deletion, DPA, "what am I missing before launch", taking payments, user accounts, file uploads, or sending user data to an LLM.
---

# Launch Compliance

Most projects now get built far faster than their owners can absorb the obligations that come with them. Someone ships a working product in a weekend, adds Stripe, adds Google auth, pipes user text into an LLM API, opens signups — and has, without noticing, become a data controller processing personal data across borders, a merchant subject to auto-renewal rules, and a service with a duty to honour deletion requests it has no mechanism to honour.

This skill closes that gap. It finds the obligations that already exist, drafts what can honestly be drafted, and is specific about what cannot.

## The stance that makes this useful

**You are not their lawyer, and pretending otherwise is the failure mode to avoid.** A generated privacy policy that confidently describes data flows the app doesn't have is worse than no policy — it is a written, signed misrepresentation of their practices, and regulators treat "your policy said X and you did Y" as the easiest possible enforcement case.

So the value here is not fluent legalese. It is:

1. **Accuracy** — every document describes what the code actually does, verified against the codebase, not against a template's guesses.
2. **Triage** — separating the 80% they can genuinely self-serve from the 20% that needs a real lawyer, and being unembarrassed about naming the second category.
3. **Making it real** — a deletion clause is a lie unless a deletion path exists. Ship the mechanism alongside the promise.

Include the disclaimer from `assets/disclaimer.md` in every generated document set. Say it once, clearly, and then get on with being useful — don't hedge every sentence.

## Workflow

Work through these in order. Don't skip to drafting documents; the drafting is the easy part and it's worthless without the first two phases.

### Phase 1 — Establish what the app actually does

Never write a policy from the user's description alone. People consistently forget the analytics script they added in week one and the error tracker that captures request bodies.

If you have access to the codebase, run the scanner first:

```bash
python3 scripts/scan.py /path/to/project --out compliance-scan.json --report compliance-scan.md
```

It reports third-party services (which become subprocessors), personal-data fields in schemas and forms, auth and payment integrations, AI/LLM API calls, cookie and storage usage, exposed secrets, which governance files are missing, launch-readiness gaps (sitemap, robots.txt, OG and Twitter tags, favicon, canonical URLs, leftover framework titles, insecure asset URLs, pre-ticked consent boxes), and common accessibility defects.

It needs no dependencies and exits non-zero only on an exposed secret, so it is safe to run as a pre-deploy gate.

**Read the `basis` tag on each finding**, because it tells you how much to trust it and therefore how to present it:

- `absence` — a file or route is not there. Reliable; state it as fact.
- `pattern` — a pattern matched in source. Usually right, but open the evidence lines before repeating the claim.
- `inference` — derived from names, imports or dependencies. Always confirm with the user before it reaches a published document.

An `inference` finding presented as settled fact is exactly the failure this skill exists to avoid. It also detects the project shape (framework, and whether there is a web surface at all) and skips launch-readiness checks for libraries and CLIs, so an empty polish list on a library means those checks didn't apply — not that the project passed them.

If the user has findings they've already decided don't apply, a `.launch-compliance-ignore` file in their repo suppresses them by id — one per line, optionally scoped as `id:path/prefix`. Offer it for genuine non-applicability, never as a way to make a list shorter.

**If legal documents already exist, the scanner reads them.** It reports services in the code that the published policy never names, template brackets like `[COMPANY NAME]` that were shipped unfilled, and documents that are undated or years old. These are `absence` findings and they are reliable — a name is either in the text or it is not. Lead with them when they appear: a policy that is published and wrong is the case this skill exists for, and it is worse than no policy, because a gap is a gap but a published misstatement is checkable.

What the scanner still cannot do is tell you an existing document is *accurate*. It only proves specific things absent from it. So read the documents it flags rather than ticking the box.

Then fill the gaps by asking. Read `references/intake.md` for the question set and, importantly, for what each answer changes. Ask only what you can't already infer; the scanner plus the user's original message usually answers half of it. Keep it to one round of questions if you can — a long interrogation is how people abandon this.

The output of this phase is a **data inventory**: for each category of personal data, what it is, why it's collected, where it's stored, how long it's kept, and who else can see it. Everything downstream derives from this table. Write it down and show it to them — most people have never seen their own data flows laid out and it's often the moment the problem becomes concrete.

### Phase 2 — Triage risk

Now map the inventory to obligations. Read the reference file(s) matching the project:

| If the project… | Read |
| --- | --- |
| collects any personal data at all | `references/privacy-law.md` |
| has users outside the EU/UK, US or Australia | `references/jurisdictions.md` |
| sends user data to an LLM, or ships AI-generated output | `references/ai-features.md` |
| takes money, subscriptions, or runs a marketplace | `references/payments-and-billing.md` |
| hosts user-generated content, or has any social surface | `references/user-content.md` |
| touches kids, health, finance, biometrics, employment, or location | `references/high-risk-categories.md` |
| has a login, a database, or an API (i.e. all of them) | `references/security-baseline.md` |
| is about to be publicly reachable (i.e. all of them) | `references/launch-readiness.md` |
| has reached Phase 4, or promises deletion, export or consent | `references/building-mechanisms.md` |

Sort every finding into four buckets and present them this way:

- **Blocking** — do not open signups until this is fixed. Reserve this for genuine exposure: no lawful basis for data already being collected, secrets in the repo, children's data with no consent mechanism, health or payment data stored insecurely, a jurisdiction where they simply cannot operate as designed.
- **Fix this month** — real obligations with real penalties, but not on fire. Missing DSAR process, no cookie consent in the EU, no breach response plan, no subprocessor list.
- **Know about it** — thresholds they haven't crossed yet but will, and what the trigger is. This is the most under-appreciated output. "You're exempt from X until you hit 100k users; here's what you'll need to do at that point" is far more useful than silence.
- **Polish** — won't get them sued, but the launch looks unfinished without it: no OG image so every share is a grey box, a default `Create Next App` title, no favicon, no sitemap. These are minutes of work each and they're the most visible thing about a launch, so list them rather than dismissing them.

Be honest about which bucket things go in. Inflating everything to blocking gets the whole list ignored; filing a missing privacy policy under polish is negligent.

**Escalate to a lawyer** when the project involves health records, financial services or lending, insurance, legal or medical advice, children under 13, biometric identifiers, employment or credit decisions, regulated substances, or firearms — or when they're raising money, signing enterprise customers with their own paper, entering a market with data localisation rules, or have already received a complaint, takedown, or regulator letter. Say so plainly and early rather than producing documents that create false comfort.

### Phase 3 — Draft the artifacts

Templates live in `assets/`. Read `references/writing-policies.md` before using them — it covers how to fill them without producing the vague boilerplate that provides no legal protection and no user clarity.

Standard output set, and the template each one comes from:

| Write this | From this template |
| --- | --- |
| `legal/privacy-policy.md` | `assets/privacy-policy.md` |
| `legal/terms-of-service.md` | `assets/terms-of-service.md` |
| `legal/cookie-policy.md` — only if there are cookies or trackers beyond strictly necessary | `assets/cookie-policy.md` |
| `legal/subprocessors.md` — the third-party list from Phase 1 | `assets/subprocessors.md` |
| `SECURITY.md` at the repo root — vulnerability disclosure contact and policy | `assets/security-md.md` |
| `COMPLIANCE.md` at the repo root — the Phase 2 checklist with owners, dates and review triggers | `assets/compliance-md.md` |

Every template carries its own filling instructions in HTML comments. Read them, then delete them — they must not survive into a published document.

Rules for filling templates:

- **Delete what doesn't apply.** A clause about a data type they don't collect is a misrepresentation. Never leave a placeholder section "just in case".
- **Every bracket gets filled or the section gets cut.** Shipping `[COMPANY NAME]` into production is common and makes the whole document look unconsidered.
- **Name specifics.** "We may share data with service providers" is weak. "We use Stripe for payments, Resend for email, and Anthropic for the summarisation feature" is what actually satisfies transparency requirements — and it's what you got from the scan.
- **Retention periods must be real numbers**, and there must be a plausible mechanism to enforce them.
- **Match the product's voice.** Plain language is not just nicer, it is explicitly required under GDPR Art. 12 and increasingly by US state laws. Readable policies are also better legal documents because ambiguity gets construed against the drafter.

### Phase 4 — Make the promises true

This is where this skill differs from a document generator, and it's the part not to skip.

Read `references/building-mechanisms.md` before building any of it. Deletion in particular is where almost every implementation is quietly incomplete, because the data has spread further than anyone remembers — and the reference has the full list of places to look, the order to delete in, and how to be honest about backups rather than promising erasure you can't perform.

For each commitment in the drafted documents, check whether the mechanism exists — and if it doesn't, offer to build it:

| The policy says | So the app needs |
| --- | --- |
| users can delete their account and data | an actual deletion endpoint that also clears backups, logs, caches, and third-party copies |
| users can export their data | an export route producing a portable format |
| we retain X for N months | a scheduled job that enforces it |
| we'll notify you of a breach | a written incident runbook with contacts and a clock |
| you can withdraw consent | a preference surface, and code that respects it |
| we don't train on your data | verified against the actual API settings of every AI provider used |

Finish by writing `COMPLIANCE.md` into the repo: the open items, who owns them, and — critically — the **review triggers** that mean they should run this again. Common triggers: adding any new third-party service, opening to a new country, adding a paid tier, crossing a user threshold, adding file uploads, adding an AI feature, taking a first enterprise customer.

## Things that change — verify, don't recall

Privacy and platform law moves faster than any model's training data. Before stating a threshold, deadline, fee, or enforcement status as fact, search for the current position. Assume these specifically have changed:

- Which US states have comprehensive privacy laws in force, and their applicability thresholds
- The status of the FTC negative-option / click-to-cancel rule (it has been through litigation)
- EU AI Act phase-in dates and which obligations are live
- UK, EU, and Australian reform packages in progress
- App Store and Play Store privacy label and data-safety requirements
- Statutory penalty amounts, and DMCA agent registration fees

If you can't verify, say the rule exists and that the specific figure needs checking. A confidently wrong threshold is worse than an acknowledged gap.

**`references/jurisdictions.md` marks each country `Detailed` or `Structural`.** A `Structural` section gives you the shape of the regime and the phrases to search for — use it to tell someone *that* they have an obligation, then look up the detail before stating it. Don't quote specifics out of a `Structural` section.

## Tone with the person you're helping

They are usually a solo builder or a small team, often not a lawyer and sometimes not a professional developer. The goal is a person who understands their own exposure well enough to make decisions, not a person who has been frightened into inaction or lulled into thinking a generated PDF makes them safe.

Lead with what's actually urgent. Don't dump twenty findings of equal weight. If nothing is blocking, say so — "you're in decent shape, three things to fix this month" is a legitimate and welcome result.
