# Building the mechanisms — making the promises true

This is Phase 4, and it is the part that separates this from a document
generator.

Every commitment in a policy is a claim about a capability. "You can delete
your account" is false unless something deletes the account. Writing the
sentence without building the thing does not just leave you exposed — it
actively creates the exposure, because now there is a published statement that
can be shown to be untrue.

The rule: **do not write the clause until the mechanism exists, or write the
clause that describes what actually happens.**

## Deletion — the hard one

Deletion is where almost every implementation is quietly incomplete, because
the data has spread further than anyone remembers.

### Step 1: find every copy

Work from the scanner's service table. For a typical stack, one user's data
lives in:

| Where | What | How it gets missed |
| --- | --- | --- |
| Primary database | The obvious rows | Related rows with no cascade, or soft-deleted rows that stay forever |
| Object storage | Uploads, avatars, exports | Orphaned keys nobody has a pointer to |
| Search / vector index | Indexed content and embeddings | Indexes are rebuilt from the DB, so a deleted row leaves a stale doc |
| Cache / queue | Sessions, rate-limit keys, jobs | A queued job re-creates the row after deletion |
| Analytics | Events keyed to a user ID | Treated as "anonymous" when it isn't |
| Error tracker | User context on past events | Nobody thinks of Sentry as user data storage |
| Email provider | Contact record, send history | Marketing lists in particular |
| Payment provider | Customer object, invoices | Genuinely must be retained — see below |
| Support tooling | Conversation history | Often a different team's tool |
| Logs | Request logs with IP and user ID | The big one; usually has no deletion path |
| Backups | Everything, frozen | The honest problem — see below |

### Step 2: delete, in the right order

Order matters: revoke access first so nothing re-creates what you just
removed.

```
1. Revoke sessions and API tokens        → user cannot act mid-deletion
2. Cancel scheduled jobs for that user   → nothing re-creates rows
3. Delete third-party copies             → these can fail; do them before
                                           losing the IDs you need
4. Delete object storage
5. Delete database rows
6. Record that the deletion happened     → keep the audit entry, not the data
```

Step 3 before step 5 is the part people get wrong. If you delete the user row
first, you have lost the Stripe customer ID and the PostHog distinct ID, and
those copies are now unreachable.

### Per-provider notes

These change. Check current API docs rather than trusting this table — but
the *shape* of the problem is stable.

- **Stripe** — you generally must **not** delete everything. Invoices and
  transaction records are retained for tax and anti-money-laundering reasons,
  typically ~7 years. Delete or anonymise the customer object's contact
  details where the provider allows; keep the financial record and say so in
  the policy. This is a legitimate retention exception, and stating it plainly
  is the right answer.
- **Analytics (PostHog, Mixpanel, Amplitude)** — have per-person delete APIs.
  Queue it: deletion is often asynchronous and can take days.
- **Sentry / error trackers** — user context attaches to past events. There is
  usually a data-scrubbing or user-deletion endpoint. The better fix is not
  sending PII in the first place.
- **Email (Resend, SendGrid, Loops, Mailchimp)** — delete the contact *and*
  suppress-list handling needs thought: a suppression list is itself personal
  data, but removing someone from it can cause you to email them again. Keeping
  a hashed suppression entry is the usual compromise; say so.
- **Object storage** — delete by prefix, and confirm versioning is off or
  versions are purged too. Versioned buckets keep "deleted" objects.
- **Vector stores / search indexes** — delete by metadata filter. If you only
  rebuild the index from the database on a schedule, the data is still
  retrievable until the next rebuild; either delete directly or state the lag.

### The backup problem, honestly

You cannot surgically delete one user from an encrypted nightly snapshot, and
almost nobody does. Regulators broadly accept that backups are handled on their
normal rotation, provided you:

1. do not restore a backup to re-create deleted data,
2. re-apply outstanding deletions if you ever do restore, and
3. **say this in the policy** rather than implying instant total erasure.

Good wording: *"Your data is removed from our live systems immediately. Copies
in encrypted backups are overwritten within 30 days as those backups rotate."*

Bad wording: *"We permanently delete all your data immediately."* — because it
is not true, and it is checkable.

### What you are allowed to keep

Deletion rights are not absolute. You can usually keep:

- financial and tax records for the statutory period
- what you need to defend a legal claim
- a minimal suppression record proving someone asked to be forgotten
- aggregated or genuinely anonymised data — *genuinely* meaning it cannot be
  re-identified, which a hashed email is not

Name each exception in the policy, with its period. A specific exception reads
as competence; silence reads as an omission.

### Verify it

Write a test that creates a user, populates every surface, deletes, then
asserts each surface is empty. Without it, deletion rots the first time someone
adds a table.

## Export

Much easier, and often the same query shaped differently.

- Return everything you hold **about the person**, not just what they typed.
  That includes derived data and usage records.
- Structured and machine-readable: JSON or CSV. A PDF is not portable.
- Generate asynchronously and deliver by signed, expiring link — exports are
  large, and an export endpoint is a lovely target for scraping.
- Rate limit it, and require re-authentication.
- **The export link itself is a data breach waiting to happen** if it never
  expires or is guessable.

## Retention that actually runs

A retention period in a policy with no job behind it is the easiest promise to
break, because nothing fails when it isn't kept.

```
daily:
  delete request logs older than 90 days
  delete soft-deleted accounts older than 30 days
  delete abandoned signups older than 14 days
  delete expired sessions and password-reset tokens
  delete orphaned uploads with no owning row
```

Two things to get right:

- **Log it.** Record how many rows each run deleted. A cleanup job that has
  silently failed for six months looks exactly like one that works.
- **Match the numbers in the policy.** If the job says 90 days and the policy
  says 12 months, one of them is wrong — and it is usually the policy, written
  by someone who never saw the cron file.

## A consent gate that actually blocks

This is the mechanism most often built wrong, and the failure is invisible
from the outside unless you look at the network tab.

**The rule:** in the EU and UK, consent is required *before* anything
non-essential is stored on or read from the device. Not before it is
*processed* — before it is **stored or read**. So the tag must not load until
consent exists.

The common broken pattern:

```
<Script src="https://analytics.example/tag.js" />   ← loads on page load
<CookieBanner />                                     ← asks afterwards
```

That is the specific thing regulators keep penalising. The banner is not the
compliance mechanism; the *blocking* is.

What correct looks like:

- Non-essential scripts are not rendered at all until consent state is
  "granted" — conditional rendering, not CSS or a flag the script reads later.
- Consent state is stored in a strictly-necessary cookie, readable server-side
  so the first render is already correct.
- **Refusing is exactly as easy as accepting.** Same number of clicks, same
  visual prominence. "Accept all" as a button next to "Manage preferences" as
  a text link is the pattern that gets cited.
- No pre-ticked anything.
- Withdrawing is reachable later — a persistent footer link.
- Record what was consented to and when, including the version of the text
  shown.

If a provider offers a consent-mode integration, understand what it does: some
still send a cookieless ping before consent. Whether that is acceptable
depends on the regime, so check rather than assume the integration makes it
fine.

Also worth knowing: analytics that genuinely sets no cookies and reads nothing
from the device may fall outside the consent requirement entirely. Switching
tools is sometimes cheaper than building the gate.

## DSAR intake

A right with no route is not a right.

- **A monitored address.** `privacy@` that reaches a human. Publish it in the
  policy and mean it.
- **Identity verification** proportionate to the request — enough that you are
  not handing someone's data to an impersonator, not so much that you collect
  a passport scan to answer an email.
- **A clock.** Log the date received. One month under GDPR, 45 days under
  several US state laws, 30 days in Australia; extensions exist and usually
  must be communicated.
- **A log**: who asked, what for, what you did, when. This is what you show if
  it is ever disputed.
- A template reply for each request type saves the panic.

## The breach runbook

Write it before you need it. Neither the GDPR 72-hour clock nor Australia's
assessment window is achievable if the first hour goes on working out who to
call. One page, in the repo:

1. **Who leads** — a name, not a role nobody holds.
2. **Contain** — rotate keys, revoke sessions, disable the endpoint.
3. **Assess** — what data, whose, how many, what harm is likely.
4. **The clock** — when did we become aware? That timestamp starts everything.
5. **Notify** — which regulator, which users, payment provider, insurer,
   enterprise customers with contractual windows.
6. **Holding statement** — drafted in advance.
7. **Record every decision and its time.** Regulators ask for the timeline and
   reconstructing it afterwards is miserable.

## Before you call Phase 4 done

- [ ] Deletion covers every row in the "find every copy" table
- [ ] Deletion order revokes access before removing data
- [ ] Retention exceptions named in the policy, each with a period
- [ ] Backup wording is honest about rotation
- [ ] A test asserts deletion actually empties every surface
- [ ] Export returns everything, expires, and is rate limited
- [ ] Retention jobs exist, log their results, and match the policy's numbers
- [ ] Non-essential tags do not load before consent
- [ ] Refusing consent is as easy as accepting
- [ ] A monitored privacy address, with a log and a clock
- [ ] Breach runbook written, with names

The test for the whole phase: **take each promise in the drafted documents and
point at the code that keeps it.** Anything you cannot point at is either work
to do or a sentence to change.
