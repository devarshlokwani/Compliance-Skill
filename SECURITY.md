# Security Policy

## Reporting a vulnerability

Open a [private security advisory](https://github.com/devarshlokwani/Compliance-Skill/security/advisories/new)
on this repository, or email the address on the maintainer's GitHub profile.

Please include what you found, how to reproduce it, and what an attacker could
do with it. You'll get an acknowledgement within **5 days**.

## What's in scope

`launch-compliance/scripts/scan.py` is the only executable code here. It reads
files and writes two report files. The things worth reporting:

- **Path traversal or writes outside the intended output paths** — the scanner
  should only ever write to `--out` and `--report`.
- **A crafted repository that makes the scanner hang or exhaust memory.** It
  runs in CI on untrusted branches, so catastrophic regex backtracking on a
  hostile input file counts as a vulnerability, not a performance bug.
- **Secret leakage into report output.** Detected credentials are masked before
  they reach the report; a path that emits one in full is a real issue, because
  reports get uploaded as CI artifacts.
- **Anything that causes the scanner to execute code it has read.** It never
  should — it does no imports, no `eval`, and runs nothing it finds.

## What's out of scope

- **Missed detections and false positives.** These are correctness bugs, and
  they matter, but they go in a normal issue — please use the
  [detection template](.github/ISSUE_TEMPLATE/detection.md).
- The deliberately broken fixture in `examples/demo-project`. It contains
  placeholder credentials and defective code on purpose.
- The content of the reference files or document templates. Corrections are
  very welcome as ordinary issues or pull requests.

## Good-faith research

We won't pursue legal action against anyone researching in good faith under
this policy. Please don't test against other people's repositories without
their permission.
