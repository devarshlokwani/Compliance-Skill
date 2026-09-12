# demo-stale-docs (fixture)

The third failure mode. `demo-project` is the app with no documents at all;
`demo-library` is the clean project that should produce near-silence. This one
*has* a privacy policy — and it is wrong.

It was generated from a template two years ago and never revisited. Since then
the project added OpenAI, Sentry, PostHog and Resend. The policy names none of
them, still names Google Analytics which was removed, and still contains
`[COMPANY NAME]`. The terms have no date at all.

This is the case the skill treats as worse than having no policy: a missing
policy is a gap, a published and inaccurate one is a written misstatement of
your practices in a form anyone can check.

Not a real product. Do not use this code, and especially do not use these
documents.
