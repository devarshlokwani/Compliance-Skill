# Contributing

Thanks for considering it. This document says what's most useful, what the
constraints are, and what will get a change sent back.

## The highest-value contributions, in order

### 1. Jurisdictions outside the US, EU and Australia

This is the biggest gap and the one most worth filling.

`references/privacy-law.md` covers the EU/UK, the US and Australia properly.
Everywhere else lives in `references/jurisdictions.md`, where each section
carries a status line: `Detailed` means it is good enough to act on,
`Structural` means the shape of the regime is right but the specifics need
looking up. Most are `Structural`.

**Upgrading a section from `Structural` to `Detailed` is the single most
valuable contribution to this project.** Change the status line only if you
have worked with the regime and checked the current text — leaving it as
`Structural` is not a failure, it is the honest default, and it tells the
reader exactly how much weight to put on what they just read.

What a good section looks like — follow the Canada or Japan sections as the
model:

- **The trigger**: who is in scope, and on what basis (residence of users?
  presence of the business? revenue thresholds?)
- **What it actually requires** that differs from GDPR, rather than restating
  the parts that are the same
- **The bits that catch people out** — the Australian section calls out APP 8
  and APP 11.2 because those are the ones people miss
- **Breach notification**: who to tell, how fast
- **Marked clearly where a figure is volatile.** Every threshold and deadline
  needs the "verify before quoting" treatment

Write from the actual regime, not from a summary of it. If you're not confident
about a detail, leave it out and say it needs checking — that's the house style
and it's better than a plausible-sounding error.

### 2. Detections in `scan.py`

New services, new personal-data field patterns, new launch-readiness or
accessibility checks, support for frameworks other than the Next.js-shaped
default.

Use the [detection issue template](.github/ISSUE_TEMPLATE/detection.md) if
you'd rather report than implement.

### 3. Reducing false positives

A scanner that cries wolf gets ignored, and ignored findings are worse than no
findings. If a check fires on correct code, that's a bug worth fixing — open an
issue with the snippet.

`examples/demo-library` is the standing guard against this: a clean Python
package that must produce nothing but `docs.security-missing`. If you can
construct a realistic project shape that gets spurious findings, adding it as a
third fixture is a genuinely useful contribution on its own.

### 4. Accessibility depth

The four current checks are deliberately shallow. Heading order, ARIA misuse,
and form-association checks are all plausible additions that can be done from
static source. Contrast ratios and keyboard traps mostly can't — if you have a
way, it needs to survive the no-dependencies rule.

## Constraints that aren't negotiable

**`scan.py` is standard library only.** No dependencies, ever. It runs as a CI
gate and in environments with no install step. A change that adds an import
from outside the standard library will be sent back, however good the feature.

**`scan.py` exits non-zero only on an exposed secret.** The shipped CI workflow
depends on this. `--fail-on` exists for people who want stricter behaviour;
don't change the default.

**Exactly one `SKILL.md`, at `launch-compliance/SKILL.md`.** Extra ones anywhere
in the tree break skill upload. Supporting documents go in `references/` under
their own names.

**The frontmatter `description` must stay under 1024 characters**, and it's
unquoted YAML — an unescaped `: ` inside it breaks parsing. It currently sits
at about 1006 characters, so there is very little headroom: if you add a
trigger phrase, remove one.

**Don't flatten the directory structure.** The repository root is the
distribution wrapper; the skill itself is the `launch-compliance/` subdirectory
so that folder can be zipped and installed standalone. `README.md`,
`.github/workflows/self-scan.yml` and `.github/ISSUE_TEMPLATE/detection.md` all
reference `launch-compliance/scripts/scan.py` by path.

## Design principles

These are load-bearing. If a change conflicts with one, raise it in the issue
rather than quietly overriding it — sometimes the principle is wrong, but that
should be a decision rather than a side effect.

- **Accuracy over fluency.** Every generated document must describe what the
  code actually does. A policy that confidently describes data flows the app
  doesn't have is a written misrepresentation.
- **Not their lawyer, and explicit about it.** Name what needs specialist
  review instead of producing documents that create false comfort.
- **Absence is reliable; presence is not.** The scanner can prove a file is
  missing. It cannot prove an existing policy is accurate. Report language must
  never imply otherwise.
- **Honest severity.** Four buckets, used honestly. Inflating everything to
  blocking gets the whole list ignored.
- **Verify, don't recall.** Thresholds, deadlines, fees and enforcement status
  get looked up, not asserted.
- **Plain language.** Legalese is a compliance defect, not a safety measure.

## Working on it

### Tests

There is no test framework — the fixtures are the tests, and CI asserts against
them. There are two, because a scanner has two ways to fail: it can miss
something, or it can cry wolf.

```bash
# Detection: a deliberately broken Next.js app. Must exit 0 -- it contains no
# exposed secrets -- and must produce the full set of expected findings.
python3 launch-compliance/scripts/scan.py examples/demo-project

# False positives: a clean Python library with no web surface. Must produce
# NOTHING except docs.security-missing.
python3 launch-compliance/scripts/scan.py examples/demo-library

# Self-scan. Must exit 0.
python3 launch-compliance/scripts/scan.py . --quiet

# Full output while developing.
python3 launch-compliance/scripts/scan.py <path> --out scan.json --report scan.md --quiet
```

CI enforces both fixtures: the expected-findings list for `demo-project`, and
the near-silence of `demo-library`.

If you add a check, **add something to `examples/demo-project` that triggers
it** and **add its id to the expected list** in
`.github/workflows/self-scan.yml` — otherwise there is no way to tell it still
works six months from now.

If your check fires on `examples/demo-library`, it is a false positive. Fix the
check rather than adding it to the allowed set.

**Gate anything launch-readiness-shaped on `self.shape.web`** by calling
`self.web_gap(...)` instead of `self.add_finding(...)`. Telling a CLI tool it
has no favicon is how a scanner trains people to ignore it.

**Set a `basis`** for any new finding id in `FINDING_BASIS` — `absence`,
`pattern` or `inference`. It defaults to `absence`, which is the strongest
claim, so a finding based on inference that you forget to tag will overstate
itself.

### Regenerating the committed sample

After any change to `scan.py` that alters output, regenerate
`examples/sample-scan.md`:

```bash
python3 launch-compliance/scripts/scan.py examples/demo-project \
  --report examples/sample-scan.md --quiet
```

Then re-add the HTML comment header at the top of the file (the scanner doesn't
write it). The scanner echoes the project path exactly as you typed it, so
running it with the relative path above keeps the committed sample
machine-independent — don't run it with an absolute path.

### Validating the skill

If you have the skill-creator tooling available:

```bash
python3 <skill-creator>/scripts/quick_validate.py launch-compliance
```

### Trigger evals

The frontmatter `description` is the entire triggering mechanism and nothing
tests it automatically. `evals/triggering.md` is the manual harness: 35 prompts
across must-trigger, must-not-trigger and judgement cases.

**Run it after any change to the description**, and record the before/after
scores in the PR. Because the field is near its character ceiling, adding a
trigger phrase means removing one — and adding keywords makes homonym misfires
(`launch a subprocess`, `shipping a function`) more likely, so re-run those
cases specifically.

## Style

- Plain language in everything, including the references. The skill tells
  Claude that legalese is a defect; the repository should hold itself to it.
- Explain *why* a rule exists, not just what it is. "Pre-ticked boxes aren't
  valid consent" is less useful than the same statement with the reason it's
  enforced so often.
- Prefer specifics over hedges. If something is genuinely uncertain, say what's
  uncertain and what would resolve it.
- No emoji in the skill files.

## What will get sent back

- Anything adding a dependency to `scan.py`
- A second `SKILL.md`
- A legal claim stated with a confidence the source doesn't support
- A detection with no fixture in `examples/demo-project`
- Severity inflation — everything is not blocking
- Generated-document templates that add clauses for things the scanner can't
  confirm

## Legal

Nothing in this repository has been reviewed by a lawyer, and contributions
don't change that. If you are a lawyer and want to review something, that would
be genuinely valuable — open an issue and say which part.

Contributions are accepted under the project's licence — MIT with the Commons
Clause. By opening a pull request you agree your contribution is licensed on
those terms.

Practically, that means anyone may use and fork your contribution, including
inside a commercial product, but nobody may sell the skill itself. Documents
generated using it stay the property of whoever generated them, with no
attribution required — see the additional permission in `LICENSE`.
