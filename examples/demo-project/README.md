# MeetingNotes (demo)

A fake Next.js app used as a fixture for `launch-compliance/scripts/scan.py`.

It is deliberately incomplete in the ways real weekend projects are
incomplete: real integrations wired up, no governance documents, a robots.txt
copied from staging, a handful of accessibility defects, and a pre-ticked
marketing checkbox.

It contains no real credentials. `.env.example` holds placeholders only, which
is why scanning this directory exits 0 — the scanner fails a run only on an
exposed secret.

Do not use any of this code.
