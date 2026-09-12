# Trigger evals

The `description` in `SKILL.md` frontmatter is the whole triggering mechanism.
It is ~1006 characters carrying the entire decision, and nothing tests it
automatically.

This file is the manual harness. Run it after any change to the description —
it's the highest-risk field in the project, because a skill that doesn't fire
is worth exactly nothing regardless of how good the rest of it is.

## How to run it

In a fresh session with the skill installed, paste a prompt from the tables
below and record whether the skill fired. Don't reuse a session: prior context
contaminates the result badly, and a skill that only fires on the second ask is
a skill that doesn't fire.

Score honestly. The failure that matters most is the **silent miss** — someone
about to deploy who never finds out this exists.

## Must trigger

The core case. Deploy-shaped intent, **no mention of legal, privacy or
compliance**. If these don't fire, the skill has failed at its main job.

| # | Prompt | Notes |
| --- | --- | --- |
| 1 | `I'm pushing this to Vercel tonight` | The canonical case |
| 2 | `how do I deploy this to Railway?` | Pure deploy mechanics |
| 3 | `just bought the domain, how do I point it at this?` | DNS question, launch intent |
| 4 | `about to open signups` | No deploy verb at all |
| 5 | `what am I missing before launch?` | Explicitly invites the audit |
| 6 | `going live tomorrow` | Minimal |
| 7 | `submitting to the App Store this week` | Store review path |
| 8 | `posting this on Product Hunt on Tuesday` | Announcement, not deploy |
| 9 | `can you help me set up a waitlist page?` | Pre-launch surface |
| 10 | `I want to add Stripe to this` | Obligation attaches on integration |
| 11 | `hooked up Google sign-in, what's next?` | Now processing personal data |
| 12 | `I'm sending user messages to Claude for summarisation` | Cross-border transfer |
| 13 | `added file uploads — anything I should know?` | UGC obligations |
| 14 | `finished the MVP, ready to ship` | Vague but unambiguous intent |
| 15 | `setting up the production database` | Production-shaped |

## Must also trigger

Explicit asks. Easier, but worth confirming the obvious route still works.

| # | Prompt |
| --- | --- |
| 16 | `write me a privacy policy` |
| 17 | `do I need a cookie banner?` |
| 18 | `does GDPR apply to me?` |
| 19 | `I need terms of service` |
| 20 | `how do I handle a data deletion request?` |
| 21 | `a customer sent me a DPA to sign` |
| 22 | `is my app compliant with the Australian Privacy Act?` |

## Must NOT trigger

False positives are cheaper than misses but still cost trust — a compliance
audit in the middle of a debugging session is an interruption.

| # | Prompt | Why not |
| --- | --- | --- |
| 23 | `why is this test failing?` | Debugging |
| 24 | `refactor this component` | Ordinary code work |
| 25 | `explain what this regex does` | Explanation |
| 26 | `deploy the docs site for this internal script` | Internal, no users, no data — borderline; a light mention is acceptable, a full audit isn't |
| 27 | `git push isn't working` | "push" is not deploy intent |
| 28 | `how do I launch a subprocess in Python?` | "launch" is a homonym here — a known trap |
| 29 | `what's the terms of the loop variable?` | "terms" homonym |
| 30 | `I'm shipping a new function to this module` | "shipping" in a code sense |

Cases 28–30 are the ones worth rechecking whenever the description changes.
Adding trigger keywords makes homonym misfires more likely, and the
`launch a subprocess` case is the canonical example.

## Judgement cases

No single right answer. Record what happened and whether it felt useful —
these are where the description's wording earns or loses its keep.

| # | Prompt | The question |
| --- | --- | --- |
| 31 | `deploying an internal tool for my team of 4` | Employee data is still personal data. A short version is probably right |
| 32 | `it's just a static landing page` | No data, but launch-readiness still applies |
| 33 | `putting my portfolio site online` | Analytics and a contact form would make it in scope |
| 34 | `building a health tracker for myself` | Not shipping yet, but the high-risk warning is worth surfacing early |
| 35 | `deploying a Discord bot` | Message content is user data |

## Scoring

Record per run:

```
Date:            Model:            Skill version:

Must trigger      __ / 15     ← anything under 14 is a problem
Must also trigger __ / 7      ← should be 7
Must NOT trigger  __ / 8      ← anything under 7 means over-triggering
Judgement         notes
```

**Must-trigger is the number that matters.** A miss there is someone launching
without knowing what they triggered — which is the entire reason this exists.
Over-triggering is an annoyance; under-triggering is a failure.

## After a description change

The description is close to its 1024-character ceiling (currently ~1006), so
adding a trigger phrase means removing one. When you do:

1. Re-run the **Must trigger** table in full.
2. Re-run cases 28–30 specifically, for homonym misfires.
3. Note in the PR which phrases you added and removed, and what the scores
   were before and after.
