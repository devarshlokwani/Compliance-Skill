# tinyretry (demo fixture)

A deliberately *clean* fixture for `launch-compliance/scripts/scan.py`.

`examples/demo-project` tests that the scanner finds things. This one tests
that it stays quiet: a library with no web surface, no personal data, no
third-party services and no secrets should produce almost nothing.

A scanner that tells a retry decorator it needs Open Graph tags and a cookie
policy is a scanner people switch off, so this fixture is a regression test for
false positives. The only finding it should produce is the missing
`SECURITY.md`, which is legitimate advice for any public repository.

Do not use this code; it is a fixture, not a library.
