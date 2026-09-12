# AI features — what shipping a model call actually commits you to

> **Verify before quoting.** EU AI Act phase-in dates, which obligations are
> live, provider training and retention defaults, and app-store AI disclosure
> rules all move. Check the provider's current documentation rather than
> recalling it — the defaults have changed more than once, and they differ
> between consumer, API and enterprise tiers of the same product.

## The thing people miss

Adding an LLM call feels like adding a library. It isn't. It is:

- a **new subprocessor** who receives user content,
- a **cross-border transfer**, almost always to the US,
- a **new retention location** you don't control,
- a **new disclosure obligation**, and
- potentially a **new category of liability** for what the output says.

None of that is exotic. All of it is invisible in the diff.

## Map the data flow before anything else

The question is not "do you use AI". It is **what exactly leaves the building**:

| What gets sent | Why it matters |
| --- | --- |
| Only what the user typed into a prompt box | Most defensible; still a transfer and still needs disclosure |
| The user's stored documents or transcripts | Much larger exposure; user may not realise the feature reads their whole account |
| Rows from your database, injected as context | Includes data about *other* users if your retrieval is not scoped per-user |
| System prompts containing internal data | Leaks through jailbreaks; treat as public |
| Uploaded files, images, audio | Audio and face images carry biometric implications in several jurisdictions |

The retrieval-scoping point deserves a real check. A vector store that isn't
partitioned by user is a data breach waiting for one prompt: "summarise
everything you know". Confirm the filter is applied at query time, server-side,
not in the prompt.

## The training question

Get this right, in writing, per provider. The answer differs by tier:

- API and enterprise tiers generally **do not** train on customer content by
  default; consumer chat products often **do** unless opted out.
- Some providers offer zero-retention or reduced-retention modes on request.
- "Abuse monitoring" retention is separate from training, usually shorter, and
  usually not opt-outable on standard tiers.

Two failure modes to check for:

1. **The policy says "we don't train on your data" and the provider's default
   says otherwise.** This is a false statement of fact in a published document.
2. **The user believes the account-level setting applies to the API key.** It
   often doesn't. Check the setting that applies to the key actually in use.

Write the answer down in the subprocessor list with a date, because it changes.

## Disclosure that actually satisfies transparency

"This product uses AI" is not a disclosure. What people need to know:

- **Which provider**, named. It goes in the subprocessor list.
- **What is sent** — "the text of the meeting you upload", not "your data".
- **Whether it is used for training**, plainly.
- **How long the provider keeps it**, if you know. If you don't, that is a
  question to ask them, not a detail to omit.
- **That output can be wrong**, where the user might rely on it.

For EU users this is also a lawful-basis question. If the AI feature is the
core service the user signed up for, contract works. If you are sending
existing user data through a model for a *new* purpose they didn't sign up for
— enrichment, classification, training — that is a separate purpose needing its
own basis, and consent is usually the honest answer.

## EU AI Act — the short version for a small product

A risk-tiered regime, phasing in over several years. **Check which obligations
are live before stating dates.** The structure:

- **Prohibited practices** — social scoring, certain biometric categorisation,
  emotion inference in workplaces and schools, manipulative techniques
  exploiting vulnerability. If a product does one of these, it is not a
  compliance-document problem, it is a don't-build-it problem.
- **High-risk systems** — including AI used in employment and worker
  management, education access, credit scoring, essential services eligibility,
  and biometric identification. Heavy obligations: risk management, data
  governance, logging, human oversight, conformity assessment. A small team
  should not be improvising here; this is the escalate-to-a-lawyer line.
- **Transparency obligations** — users must be told when they are interacting
  with an AI system, synthetic media must be marked as machine-generated, and
  deepfakes disclosed. This is the tier most indie products land in, and it is
  cheap to comply with.
- **General-purpose model obligations** — fall mainly on the model provider,
  not on you as an API consumer. But if you fine-tune and distribute a model,
  check where you sit.

Most weekend projects are in the transparency tier. Say so, and say clearly
which use cases would move them up a tier: anything screening job applicants,
scoring creditworthiness, or making decisions about access to services.

## Liability for what the model says

The exposure isn't hypothetical, and it doesn't depend on novel law. Ordinary
consumer-protection and negligence principles apply to what your product tells
users, regardless of what generated it. Established points:

- **You are responsible for your product's output**, including a chatbot's.
  "The model said it, not us" has been tested and has not worked well.
- **Advice-shaped output in a regulated domain** — medical, legal, financial,
  tax, immigration — is where this gets serious. See
  `high-risk-categories.md`. A disclaimer helps; it does not immunise, and it
  does nothing at all if the product is designed to be relied on.
- **Defamation and IP** in generated output are live risks where outputs are
  published or shared.

Practical mitigations that are worth the effort:

- Scope the feature. A summariser is a smaller problem than an adviser.
- Show provenance where you can — quote the source passage.
- Make the "check this" affordance real: don't bury it in terms, put it next to
  the output.
- Don't auto-publish generated content to a public surface without a human in
  the loop.

## Prompt injection is a security issue, not a prompt issue

If your model call includes untrusted content — a web page, an uploaded
document, another user's text — assume an attacker controls part of the prompt.
Consequences worth checking:

- **Tool access.** If the model can call functions that read or write data,
  injected instructions can drive them. Scope tool permissions to the current
  user and validate arguments server-side; never let the model choose which
  user's records to touch.
- **Data exfiltration via rendered output.** Markdown images and links in model
  output can smuggle data to an attacker's server when rendered. Sanitise, or
  don't render raw HTML/markdown from model output.
- **System prompt leakage.** Assume it leaks. Don't put secrets or other
  users' data in it.

Treat model output as untrusted input to the rest of your system — because
that's exactly what it is.

## Cost and abuse — the operational part

Not a legal issue, but it lands on the same launch day:

- **Rate limit per user and globally.** An unauthenticated endpoint that
  proxies a paid model API is a bill waiting to happen.
- **Cap token spend.** Both per request and per user per day.
- **Never put the provider key in client code.** The scanner checks for this;
  a key in a `NEXT_PUBLIC_` variable is public.

## Checklist

- [ ] Every model provider named in the privacy policy and subprocessor list
- [ ] What gets sent described in concrete terms, not "your data"
- [ ] Training setting verified **in the provider's console for the key in
      use**, and recorded with a date
- [ ] Provider retention window known and consistent with your policy
- [ ] Transfer mechanism in place (usually the provider's DPA and SCCs)
- [ ] Retrieval scoped per-user, enforced server-side
- [ ] AI interaction disclosed to the user where they might not realise
- [ ] Generated output marked where it could be mistaken for human or factual
- [ ] Tool calls scoped to the current user's own data
- [ ] Rate limits and spend caps in place
- [ ] Confirmed this is not a high-risk use case under the AI Act — and if it
      might be, escalated rather than templated
