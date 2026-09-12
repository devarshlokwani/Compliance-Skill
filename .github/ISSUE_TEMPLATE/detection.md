---
name: Detection report
about: A check that missed something, fired on correct code, or should exist
title: "[detection] "
labels: detection
---

<!--
For the scanner at launch-compliance/scripts/scan.py.

Before filing: run the scan and paste what actually happened. A snippet plus
the output is worth more than a description of either.
-->

## Type

- [ ] **False negative** — it should have flagged something and didn't
- [ ] **False positive** — it flagged correct code
- [ ] **New detection** — a check that doesn't exist yet
- [ ] **Wrong severity** — it fires correctly but in the wrong bucket

## The code

<!-- The smallest snippet that reproduces it, and the file type. Redact anything real. -->

```

```

## What the scanner did

<!-- Paste the relevant part of the output. If it found nothing, say so. -->

```
$ python3 launch-compliance/scripts/scan.py <path>

```

## What it should have done

<!--
For a false negative or a new detection, the useful details are:

  * What obligation or defect does this signal? Why does it matter to someone
    about to launch?
  * Which bucket: blocking / month / know / polish -- and why that one? Be
    honest; severity inflation gets the whole list ignored.
  * Which reference file should it point at?
  * How would you detect it without false positives? What correct-looking code
    does the pattern need to NOT match?
-->

## Environment

- Framework / language:
- Scanner version (`scan.py --version`):

## Notes

<!--
If you're planning to send a PR: every new check needs something in
examples/demo-project that triggers it, or there's no way to tell it still
works later. See CONTRIBUTING.md.

Standard library only. No dependencies, ever.
-->
