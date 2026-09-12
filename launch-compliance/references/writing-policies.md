# Writing the documents — how to fill templates without making them worthless

Read this before touching anything in `assets/`.

The templates are scaffolding. Filled in carelessly they produce the exact
thing this skill exists to prevent: a fluent document that describes a product
nobody built.

## The one rule

**Every sentence must be true of this specific product.**

That's it. Everything below is an application of it.

A privacy policy is a statement of fact about your practices. In the US, an
inaccurate one is a deceptive practice under FTC Section 5 — enforceable at any
size, with no threshold. In the EU it undermines the lawful basis it was
supposed to establish. "Your policy said X and you did Y" is the easiest
enforcement case there is, and a generated policy is unusually good at
producing exactly that gap, because templates describe the median product
rather than this one.

A vague policy is not safer than a specific one. It is less useful to the user,
less protective of you, and construed against you when it's ambiguous.

## Deriving the policy from the code

This table is the core of the phase. Left column is what the scanner and the
intake found; right column is what must therefore appear in the document.

| What's in the code | What the policy must say |
| --- | --- |
| `email` field on a user model | Email is collected; why (account identity, transactional mail); how long it's kept |
| OAuth provider (Google, GitHub…) | You receive profile data from that provider; which fields; that they are a source of data |
| `password` / `passwordHash` | Credentials are stored; that they are hashed (say so — users care) |
| Stripe or any processor | Payments are processed by [named provider]; that you do not store card numbers; that billing records are kept for tax reasons and for how long |
| Analytics SDK | Usage data collected; which provider; whether it uses cookies; how to opt out |
| Session replay | **Session recordings may capture what you type** — this needs its own sentence, not a mention inside "analytics" |
| Error tracker | Diagnostic data including technical details of errors; whether request content can be included |
| LLM API call | Content sent to [named provider] for [specific feature]; whether it trains their models; their retention |
| File upload handler | Files you upload are stored; where; who can access them; what happens on deletion |
| `ipAddress`, `userAgent` | Collected; why (security, abuse prevention); retention |
| Location fields | Location collected; precision; purpose; that it's sensitive |
| Email sending provider | Named as a recipient of your email address |
| Cron job deleting old rows | The retention period it enforces — and now you can state a real number |
| **No deletion route in the code** | **Do not write a deletion clause yet.** Build the route first, or say precisely what the manual process is and how to trigger it |

That last row is the one that matters most. Working backwards from a template's
promises to a product that doesn't keep them is how these documents become
liabilities.

## Filling in the brackets

- **Every bracket gets filled or the section gets cut.** `[COMPANY NAME]` in
  production is common and makes the entire document look unconsidered — which
  in turn suggests nobody read it, which is exactly the inference you don't
  want a regulator drawing.
- **Delete inapplicable sections entirely.** A children's data section in a
  B2B tool, a clause about physical mail, a section on data you don't collect
  — each is a misrepresentation, and each dilutes the parts that matter.
- **Never leave a section in "just in case" you add the feature later.** Add it
  when you add the feature; that's what the review triggers in `COMPLIANCE.md`
  are for.
- **Retention must be a real number** with a mechanism behind it. "As long as
  necessary" alone fails transparency requirements. "For the life of your
  account, then 30 days" is a sentence you can implement and verify.

## Naming names

"We may share your information with third-party service providers" is the
default template phrasing and it is close to useless — it tells the user
nothing and satisfies transparency requirements poorly.

Write instead:

> We use Stripe to process payments, Resend to send email, Sentry to monitor
> errors, and OpenAI to generate meeting summaries. Each of these receives only
> the data needed for that function. The full list, including what each one
> receives and where it processes data, is at [link].

This is more protective, not less. You have disclosed, specifically, and the
list is maintainable in one place rather than restated in three documents.

The word **"may"** deserves particular suspicion. "We may collect your
location" usually means one of: we do, we don't, or nobody checked. Find out
which, and write that.

## Plain language is a legal requirement

GDPR Art. 12 requires concise, transparent, intelligible and easily accessible
information in clear and plain language — and where the audience includes
children, language a child can understand. US state laws increasingly say the
same. This is a substantive requirement, not a style note.

It also happens to be good drafting. Ambiguity is construed against the
drafter, so vague language protects you less than clear language.

Practically:

- Short sentences. Second person: "you", "we".
- Headings people can scan. "Can I delete my data?" beats "Data Subject
  Rights" for a consumer product.
- Define nothing you can avoid defining. If you must use "processing", say what
  it means in the sentence where it appears.
- No "heretofore", no "including but not limited to" as a reflex, no capitalised
  Defined Terms unless the term genuinely carries specific meaning.
- A summary table at the top, with the detail below, is legitimate and helpful.
  Just make sure the summary and the detail agree.

**The counter-rule:** plain language does not mean vague language. "We keep
your stuff safe" is plain and useless. "We store your files encrypted, and only
you and anyone you share a link with can open them" is plain and specific.

## Matching the product's voice

A policy that reads like a different company wrote it signals that nobody read
it. Match the product's register — a playful consumer app can have a readable
policy, and a B2B tool can be formal. What can't change is accuracy.

## The failure modes to check for before shipping a draft

Read the draft against these:

1. **A promise with no mechanism.** Deletion, export, retention, consent
   withdrawal, breach notification. If it's promised, it must exist — see
   Phase 4 of `SKILL.md`.
2. **A named service that isn't used**, or a used service that isn't named.
   Check against the scan output both ways.
3. **A retention period nothing enforces.**
4. **A jurisdiction section for a place with no users**, or — worse — no
   section for a place with plenty.
5. **A rights section listing rights with no way to exercise them.** Every
   right needs an address or a button.
6. **A contact address nobody monitors.** `privacy@` has to reach a human.
7. **An effective date that never changes**, or changes without anyone telling
   users about a material change.
8. **A "we don't sell your data" claim** made without checking whether the ad
   pixel or analytics integration meets the statutory definition of "sale" in
   the relevant states. This one is specific and it catches people.
9. **Copied clauses that reference the wrong entity type** — a sole trader's
   policy that talks about "our group companies", or terms referencing a
   merchant-of-record arrangement that isn't in place.

## Keeping them true

A policy is accurate on the day it's written and decays from then on. The
`COMPLIANCE.md` review triggers exist for exactly this. The changes that most
often falsify a policy without anyone noticing:

- adding an analytics or support tool
- turning on session replay
- adding an AI feature
- switching email or hosting provider
- adding a paid tier
- opening to a new country
- a provider changing their own defaults underneath you

When something material changes, update the document, change the effective
date, and tell users if the change is material. Silent material edits are their
own problem.

## Where the disclaimer goes

Include `assets/disclaimer.md` with any generated document set. Once, clearly,
at the point of handover — not repeated at the top of every file and not
sprinkled through the prose. Hedging every sentence reads as evasion and makes
the useful parts harder to find.
