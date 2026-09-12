# Intake — the questions, and what each answer changes

Read this before asking anything. The point is not to collect answers; it is to
collect the answers that **change the output**. A question whose answer doesn't
change a document, a severity, or a recommendation is a question that costs you
the user's patience for nothing.

## Rules for this phase

1. **Infer first, ask second.** The scanner plus the user's original message
   usually answers half of this. Asking someone to confirm they use Stripe when
   `stripe` is in their `package.json` reads as not having looked.
2. **One round if you can.** Batch the questions. A back-and-forth
   interrogation is the single most common reason people abandon a compliance
   pass halfway through.
3. **Ask in their language.** Not "what is your lawful basis for processing" —
   ask "when someone signs up, what do you actually do with their email?"
4. **Show your inference and let them correct it.** "It looks like you store
   name, email, phone and date of birth, and send transcripts to OpenAI — is
   that right, and is there anything not in the code yet?" is faster and more
   accurate than an open question, and it surfaces the things they forgot.
5. **Accept "I don't know."** It's a finding, not a failure. "Nobody knows how
   long we keep deleted accounts" is a real answer that goes in the punchlist.

## The questions that actually change things

### 1. Who are you, legally?

*"Is this a registered company, and where? Or are you operating as an
individual?"*

**Changes:** who the data controller is and who gets named in every document;
whether you can meaningfully limit liability (a sole trader generally cannot
limit it the way an entity can); which country's consumer law is the baseline;
whether an EU/UK representative may be required; the governing-law clause.

If they have no entity and are taking money, say plainly that the liability
sits on them personally. Don't labour it — one sentence — but don't skip it.

### 2. Where are your users?

*"Roughly where are the people using this? Anywhere in the EU or UK? Anyone in
California? Australia?"*

**Changes:** almost everything. This is the highest-value question in the set.

- **Any EU/EEA or UK users** → GDPR/UK GDPR applies to you regardless of where
  you are. Cookie consent before non-essential storage, DSAR process, lawful
  basis for each purpose, transfer mechanism for every non-EU subprocessor.
- **California and other US states** → notice at collection, opt-out rights,
  the "Do Not Sell or Share" question (which catches analytics and ad pixels
  far more often than people expect), and honouring the Global Privacy Control
  signal.
- **Australia** → the Privacy Act and the APPs, with reforms in progress.
- **Nowhere in particular / "just my friends"** → you still need a policy if
  you have an app-store listing or an OAuth consent screen, but severity drops.

"I don't know where my users are" means "assume EU and US" for a public website.

### 3. What do you collect, and what do you do with it?

*"Walk me through what happens when someone signs up and uses the main
feature."*

**Changes:** the entire data inventory, every purpose statement in the privacy
policy, and the retention table.

Specific follow-ups worth the tokens:

- **Do you log request bodies?** People say no and their error tracker says
  yes. `sendDefaultPii`, request-body capture and session replay are the three
  that catch everyone.
- **Does the session replay tool mask inputs?** Unmasked replay captures
  everything typed into a form, including what users paste in.
- **What's in your analytics events?** Custom properties routinely carry email
  addresses and free-text content that nobody intended to send.

### 4. How long do you keep it?

*"If someone deletes their account today, what's actually gone and what's
still there in a month?"*

**Changes:** the retention section (which must contain real numbers), the
deletion mechanism scope, and whether the policy you're about to write is true.

Almost nobody has an answer. The useful output is a decision made now:
a number per category, and a mechanism that enforces it. "Indefinitely, until
the user asks" is a legitimate answer for some data and an indefensible one for
raw logs.

### 5. Who else sees the data?

*"Anything the scan found that you didn't expect? Anyone else with database
access — a contractor, a co-founder, an agency?"*

**Changes:** the subprocessor list; whether you need access controls you don't
have; whether a DPA exists with each provider.

### 6. Are you taking money?

*"Paid now, or paid later? Subscription or one-off?"*

**Changes:** terms of service become blocking rather than advisable; renewal
and cancellation disclosure duties attach; refund policy; consumer withdrawal
rights in the EU/UK; sales tax and VAT exposure (and whether a merchant of
record is absorbing it); PCI scope (usually minimal if the card form is hosted
by the processor, and large the moment card data touches your server).

### 7. Can users put things into it that other users see?

*"Can one user see something another user created — uploads, comments,
profiles, shared links?"*

**Changes:** moderation policy, takedown process, DMCA agent registration,
acceptable-use terms, and whether minors could encounter other users' content.
Also changes the security profile: user-controlled content served from your
origin is a stored-XSS vector.

### 8. Is there an AI feature?

*"What exactly gets sent to the model — just what they type, or their
documents, their history, their database rows?"*

**Changes:** cross-border transfer analysis, subprocessor disclosure, the
training-data question, retention at the provider, and — if the output is
shown as advice, a decision, or a score — whether this is a high-risk use that
needs its own review.

### 9. Who is this for?

*"Any chance under-13s use this? Under-16s? Is it aimed at them?"*

**Changes:** everything, if yes. Children's data has its own regime, its own
penalties, and its own enforcement appetite. A general-audience service that
"might have some teenagers" is a different conversation from one designed for
kids, and the design-code rules in several jurisdictions bite on "likely to be
accessed by children", not on who you intended to serve.

### 10. Has anything already happened?

*"Has anyone complained, sent a takedown, asked for their data, or emailed you
about a vulnerability?"*

**Changes:** the whole posture. An existing complaint, regulator letter or
takedown moves this from "get ready" to "there is a live matter", and it is a
lawyer conversation now, not a template conversation.

## What to produce from this phase

A data inventory table, shown to the user before you draft anything:

| Data | Why collected | Lawful basis | Where stored | Kept for | Who else sees it |
| --- | --- | --- | --- | --- | --- |
| Email | Account identity, transactional email | Contract | Postgres (Neon, EU) | Life of account + 30 days | Resend |
| Meeting transcript | The core feature | Contract | Postgres + S3 | 12 months | OpenAI (inference), Sentry (if an error occurs) |

Two things to watch for as you fill it in:

- **A row with no purpose is a row to delete.** The fastest compliance win
  available is collecting less. If nothing reads `dateOfBirth`, drop the column
  and the entire question disappears.
- **A row whose "who else sees it" surprises them** is the row to talk about.
  That's usually the error tracker or the session-replay tool.
