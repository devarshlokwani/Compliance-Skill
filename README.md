# launch-compliance

A Claude Skill that fires when you're about to deploy something public, and
audits it for the legal, privacy, security and launch-readiness gaps you didn't
know to ask about.

It scans the codebase, triages what it finds by severity, drafts the missing
documents from your app's actual data flows, and builds the mechanisms those
documents promise.

---

## The problem

People ship working products in a weekend now. The obligations arrive silently.

- Add Stripe, and you're a merchant with auto-renewal disclosure duties.
- Add Google auth, and you're processing personal data.
- Pipe user text to an LLM, and you've made a cross-border transfer to a
  subprocessor you've named nowhere.

None of that shows up in a diff. All of it is real the day you open signups.

## What it does

**Phase 1 — Establish what the app actually does.** Runs a scanner over the
source: third-party services, personal-data fields in schemas and forms, auth
and payment integrations, LLM calls, cookie and storage use, exposed secrets,
missing governance files, launch-readiness gaps and accessibility defects.
Confirms the result with you, because people forget the analytics script they
added in week one. Output is a data inventory.

**Phase 2 — Triage.** Maps the inventory to obligations and sorts everything
into four honest buckets: blocking, fix this month, know about it, polish. Names
what needs a real lawyer rather than papering over it.

**Phase 3 — Draft.** Privacy policy, terms, cookie policy, subprocessor list,
`SECURITY.md`, `COMPLIANCE.md` — written from what the code does, with real
retention numbers and specific service names.

**Phase 4 — Make the promises true.** A deletion clause is a lie unless a
deletion path exists. This phase checks each commitment against the code and
offers to build what's missing.

## Design principles

These are load-bearing. If you're contributing, keep them.

- **Accuracy over fluency.** A policy that confidently describes data flows the
  app doesn't have is worse than no policy. It's a written misrepresentation,
  and "your policy said X and you did Y" is the easiest enforcement case there
  is.
- **Not your lawyer, and explicit about it.** The skill names what needs
  specialist review — health, children, biometrics, lending, insurance,
  employment decisions — rather than producing documents that create false
  comfort. Disclaimer stated once, clearly, then it gets on with being useful.
- **Absence is reliable; presence is not.** The scanner can tell you a privacy
  policy is missing. It cannot tell you an existing one is accurate. The report
  never implies otherwise.
- **Honest severity.** Inflating everything to blocking gets the whole list
  ignored. Filing a missing privacy policy under polish is negligent.
- **Verify, don't recall.** Privacy law moves faster than training data.
  Thresholds, deadlines, fees and enforcement status get looked up, not
  asserted. A confidently wrong threshold is worse than an acknowledged gap.
- **Plain language.** Required under GDPR Art. 12 and increasingly by US state
  laws. Legalese is a compliance defect, not a safety measure.

## Install

### Claude Code

```bash
git clone https://github.com/devarshlokwani/Compliance-Skill.git
cp -r Compliance-Skill/launch-compliance ~/.claude/skills/
```

Use `.claude/skills/` inside a project instead of `~/.claude/skills/` if you
want it scoped to that project rather than to you.

### Claude.ai and the desktop app

Zip the `launch-compliance/` directory — the folder itself, not its contents —
and upload it under **Settings → Capabilities → Skills**.

```bash
cd Compliance-Skill
zip -r launch-compliance.zip launch-compliance
```

The nesting is deliberate: the skill lives in a subdirectory so it can be
zipped and installed standalone, separate from this distribution wrapper.

## Use

You mostly don't invoke it. It triggers on deploy-shaped intent:

> "I'm pushing this to Vercel tonight"
> "what am I missing before launch?"
> "about to open signups"
> "just bought the domain"

Triggering on deploy mechanics alone — with no mention of legal or compliance —
is the main case it exists for.

You can also run the scanner directly, with no Claude involved:

```bash
python3 launch-compliance/scripts/scan.py /path/to/project
python3 launch-compliance/scripts/scan.py . --out scan.json --report scan.md --quiet
```

No dependencies, standard library only. It exits non-zero only on an exposed
secret, which makes it safe to drop in as a pre-deploy gate — see
[examples/github-workflow.yml](examples/github-workflow.yml).

Three things about the scanner worth knowing:

**It tags every finding with how it got there** — `absence` (a file isn't
there, so the claim is reliable), `pattern` (something matched in your source,
read the evidence), or `inference` (derived from names and imports, confirm it).
That's the "absence is reliable, presence is not" principle made machine-
readable, so a guess never arrives looking like a fact.

**It works out what kind of project it's looking at** before deciding what to
check. A Python library doesn't get told it needs Open Graph tags — the
launch-readiness checks only run when there's a web surface. A scanner that
cries wolf is a scanner people switch off.

**Findings you've decided don't apply can be suppressed** with a
`.launch-compliance-ignore` file — one finding id per line, optionally scoped
as `id:path/prefix`. This repo [uses one](.launch-compliance-ignore) for its own
deliberately-broken fixture.

## What's in here

```
README.md, LICENSE, CONTRIBUTING.md, DISCLAIMER.md, SECURITY.md
.launch-compliance-ignore   worked example of the suppression file
evals/triggering.md         manual harness for the trigger description
examples/
  demo-project/        deliberately incomplete Next.js app — tests detection
  demo-library/        clean Python package — tests for false positives
  sample-scan.md       what a real report looks like
  github-workflow.yml  drop-in CI gate
launch-compliance/     ← the skill; this is what you install
  SKILL.md             the four-phase workflow
  references/          10 files, loaded on demand
  assets/              7 annotated document templates
  scripts/scan.py      the scanner, stdlib only
```

See [examples/sample-scan.md](examples/sample-scan.md) for the output of a real
run against the demo project.

Two fixtures rather than one, because a scanner has two ways to fail:
`demo-project` proves the checks fire, and `demo-library` proves they stay
quiet when they don't apply. CI enforces both.

## Scope, honestly

**Covered in depth:** EU/UK GDPR, US federal and state privacy structure,
Australian Privacy Act and the APPs, payments and auto-renewal, AI features,
user content, security baseline, launch readiness.

**Covered structurally:** Canada, Brazil, India, Japan, South Korea, China,
Switzerland, Singapore, New Zealand, South Africa, Nigeria and others, in
[references/jurisdictions.md](launch-compliance/references/jurisdictions.md).
Every section there carries a status line — `Detailed` or `Structural` — saying
how much weight to put on it, and most are `Structural`: the shape of the
regime is right, the specifics need looking up. That's an honest label rather
than a disclaimer, and the skill is told not to quote specifics out of a
`Structural` section. Upgrading one is the highest-value contribution anyone
can make; see [CONTRIBUTING.md](CONTRIBUTING.md).

**Deliberately shallow:** accessibility. The scanner checks four defects that
can be detected reliably from static source — missing alt text, removed focus
indicators, `<div onClick>` as a button, placeholder-as-label. It does not check
contrast, heading order or keyboard traps. The report says so.

**Not covered:** anything requiring a rendered page, anything configured in a
provider's dashboard rather than in code, and the accuracy of documents that
already exist.

## Not legal advice

This produces a well-informed starting point, not legal advice, and using it
doesn't create a lawyer-client relationship with anyone. See
[DISCLAIMER.md](DISCLAIMER.md). Nothing in this repository has been reviewed by
a lawyer.

## Licence

MIT with the [Commons Clause](https://commonsclause.com/). See
[LICENSE](LICENSE) for the text. In plain language:

**You can:**

- Use it, on anything — including the commercial product you're about to launch
- Install it in your own Claude, at work or at home
- Fork it, modify it, and publish your fork
- Use it inside your company, for your company's own products

**You can't:**

- Sell the skill itself, or charge for access to it
- Host it as a paid service
- Charge people specifically for running it on their behalf

**Documents it generates are 100% yours.** The privacy policy, terms, scan
report or `COMPLIANCE.md` you produce with this carry no licence, need no
attribution, and are yours to publish and profit from however you like. The
licence covers the skill; it does not follow the output.

The short version: build a business with it, don't build a business *out of*
it.

> **Note:** the Commons Clause makes this not open source under the OSI
> definition, because it restricts a field of use. That's deliberate. If your
> employer's policy only permits OSI-approved licences, this won't clear it —
> [open an issue](https://github.com/devarshlokwani/Compliance-Skill/issues)
> and we can talk about it.
