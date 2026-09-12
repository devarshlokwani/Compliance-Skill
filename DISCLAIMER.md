# Disclaimer

**This project does not provide legal advice.**

`launch-compliance` is a tool that reads source code and produces a
well-informed starting point: a list of obligations a project has probably
triggered, and draft documents derived from what the code actually does. That
is useful. It is not the same as advice from a lawyer who knows your business,
your jurisdiction and your risk appetite, and it does not create a
lawyer-client relationship with anyone.

## Specifically

- **No warranty of accuracy or completeness.** The scanner finds signals in
  source code. It misses anything configured in a provider's dashboard, anything
  outside the repository, and anything its patterns don't cover.

- **Absence is reliable; presence is not.** The tool can tell you a privacy
  policy is missing. It cannot tell you an existing one is accurate, that a
  consent banner actually blocks the tag it sits in front of, or that a deletion
  endpoint deletes everything it should.

- **Law changes; this repository lags.** Thresholds, deadlines, fees and
  enforcement positions move. The reference files flag the volatile ones and
  tell Claude to verify rather than recall, but a stale figure can still reach
  you. Check anything you are going to rely on.

- **Generated documents are drafts.** They are statements of fact about your
  practices, and you are the one making them. An inaccurate privacy policy is
  worse than no privacy policy — in the US it is a deceptive practice
  regardless of company size. Read what you publish.

- **Some categories cannot be handled by a tool.** Health data, children's
  data, biometrics, lending, insurance, employment decisions and similar
  categories carry obligations no template discharges. The skill is designed to
  name these and stop, rather than produce something reassuring.

- **Nothing here has been reviewed by a lawyer.** Not the templates, not the
  reference material, not the severity assignments.

## Use it for what it's good for

Understanding your own exposure well enough to make decisions, and arriving at
a lawyer's office with a specific, accurate draft rather than a blank page —
which makes that a much shorter and cheaper conversation.

If you are taking money, holding sensitive data, raising investment, or signing
a customer with their own contract, have a lawyer read what you publish.

---

Provided "as is", without warranty of any kind. See [LICENSE](LICENSE).

Documents you generate with this are yours: no licence attaches to them and no
attribution is required. The warranty disclaimer above still matters, though —
publishing a generated document is your decision and your statement of fact.
