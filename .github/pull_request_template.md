<!--
Thanks for contributing. CONTRIBUTING.md has the detail; this is the short
checklist. Delete anything that doesn't apply to your change.
-->

## What this changes

<!-- One or two sentences. If it fixes an issue, link it. -->

## Type

- [ ] New detection in `scan.py`
- [ ] Fixes a false positive
- [ ] Jurisdiction section (`references/jurisdictions.md`)
- [ ] Reference or template content
- [ ] Skill workflow (`SKILL.md`)
- [ ] Docs, tooling or CI

## Checklist

- [ ] `scan.py` still imports **only** the standard library
- [ ] `python3 launch-compliance/scripts/scan.py examples/demo-project` exits 0
- [ ] `python3 launch-compliance/scripts/scan.py examples/demo-library` reports
      nothing but `docs.security-missing`
- [ ] `python3 launch-compliance/scripts/scan.py . --quiet` exits 0

### If you added a detection

- [ ] Something in `examples/demo-project` triggers it
- [ ] Its id is in the expected list in `.github/workflows/self-scan.yml`
- [ ] It has an entry in `FINDING_BASIS` (`absence` / `pattern` / `inference`)
- [ ] Launch-readiness findings use `self.web_gap(...)`, not `self.add_finding(...)`
- [ ] `examples/sample-scan.md` regenerated, with its header re-added
- [ ] Severity is honest — not everything is blocking

### If you changed the frontmatter `description`

- [ ] Still under 1024 characters, and contains no unescaped `: `
- [ ] Ran `evals/triggering.md` — scores before/after:

### If you wrote legal content

- [ ] Volatile figures are marked "verify before quoting", or omitted
- [ ] Any jurisdiction status line (`Detailed` / `Structural`) is honest
- [ ] Plain language — legalese is a defect here, not caution

## Anything you're unsure about

<!-- Genuinely useful. Uncertainty stated plainly beats a confident guess. -->
