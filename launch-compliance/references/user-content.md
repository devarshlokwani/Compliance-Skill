# User-generated content — what accepting uploads commits you to

> **Verify before quoting.** DMCA agent registration fees and renewal periods,
> EU Digital Services Act thresholds and which obligations apply at which size,
> and online-safety regimes in the UK and Australia all change. Confirm current
> positions before stating specifics.

## The trigger is smaller than people think

You have user-generated content the moment **one user can cause something to be
shown to another user**. That includes:

- uploads, obviously
- comments, reviews, profiles, display names, bios
- public share links to private documents
- avatars
- anything an AI feature generates from one user's input and displays to
  another

A "private" document with a shareable link is publishable content. If the
scanner found an upload handler, this file applies.

## Intermediary protection, and how you lose it

Most jurisdictions offer some protection for hosts who didn't create the
content and act when notified. The shape differs, but the shared condition is
that you have to **have a process and use it**:

- **US** — Section 230 for most content-based claims; the DMCA safe harbour for
  copyright specifically. The DMCA safe harbour requires you to **designate an
  agent with the Copyright Office** (there is a fee and a renewal period —
  check current), publish the agent's contact details on your site, implement
  notice-and-takedown, and adopt and reasonably implement a repeat-infringer
  termination policy. Miss the registration and you simply don't have the
  safe harbour, no matter how responsive you are.
- **EU** — the Digital Services Act sets baseline obligations for hosting
  services: a notice-and-action mechanism, statements of reasons when you
  remove content, a point of contact, and transparency requirements that scale
  with size. The heaviest obligations attach to very large platforms, but the
  baseline applies broadly.
- **UK** — the Online Safety Act imposes duties around illegal content and, for
  services likely to be accessed by children, children's safety duties. Scope
  and phase-in are worth checking; the risk-assessment duties are real even for
  small services in some categories.
- **Australia** — the Online Safety Act and the eSafety Commissioner's removal
  powers, including for cyber-abuse and image-based abuse, with statutory
  response windows.

Common thread: a published contact point, a process that works, and a record
that you followed it.

## What to build

**A takedown path.** An email address or form that a rights holder or an
affected person can use without creating an account. Published where it can be
found — a `/legal` page and your terms, not buried. Route it somewhere a human
reads.

**A record.** For each report: what was reported, when, what you decided, when
you acted, and what you told the reporter and the uploader. This is both a
DSA-style requirement and the thing that protects you if a dispute escalates.

**A repeat-infringer policy.** Written, and actually applied. "Reasonably
implemented" has been litigated and means more than having the sentence.

**Counter-notice handling**, if you operate under the DMCA — the uploader can
dispute, and the statute sets out what happens next.

## Moderation

You don't need a trust-and-safety team to launch. You do need a decision made
in advance, because the first bad upload arrives sooner than anyone expects.

Minimum viable:

- **Acceptable use terms** that say what is not allowed, specifically enough to
  act on: illegal content, sexual content involving minors, harassment,
  impersonation, malware, spam, IP infringement.
- **A report button**, or at least a documented address.
- **The ability to remove content and suspend an account**, and a stated right
  to do so in the terms. Removing content without that right stated is its own
  problem.
- **A scanning decision for the worst case.** Any service accepting image
  uploads should think about CSAM detection before launch, not after. There are
  free and low-cost hash-matching services; know what you'd do, and know your
  reporting obligations.

## Content you now host — the other obligations

**Copyright.** You don't own what users upload, and your terms need a licence
grant broad enough to actually run the service — store it, display it, make
thumbnails, back it up, and show it to whoever the user shared it with. Keep
the grant limited to operating the service. A grant that reads as "we can use
your content for anything forever" is a recurring source of public backlash and
is often broader than you need.

**Personal data in content.** Content uploaded by one user may be personal data
about a *third party* who never used your service — a face in a photo, a name
in a document, a voice in a recording. Your deletion mechanism should be able
to act on it, and your privacy policy should acknowledge that you process it.

**Metadata.** Photos carry GPS coordinates, device identifiers and timestamps
in EXIF. Documents carry author names and revision history. If you display or
redistribute uploads, **strip metadata on ingest** unless the feature depends
on it. Users do not expect their home address to travel with a photo.

**Malware and content-type confusion.** Validate content types server-side
rather than trusting the extension or the client-supplied MIME type. Serve
user-uploaded files from a **separate origin** (a different domain, not just a
different path) so a malicious upload can't execute in your site's security
context. Set `Content-Disposition: attachment` where the file isn't meant to be
rendered.

**Storage that is accidentally public.** Misconfigured buckets remain one of
the most common sources of breaches. If uploads are private, verify that a
signed URL is required, that signed URLs expire, and that object keys aren't
guessable.

## Minors

If under-18s can reach user content, the risk profile changes — contact
between adults and minors, exposure to harmful content, and design-code
obligations in several jurisdictions that apply based on whether children are
*likely* to access the service rather than whether you targeted them.

See `high-risk-categories.md`. If children are a plausible audience and the
service has any social surface, this is a lawyer conversation.

## Terms clauses specific to UGC

- Licence grant from user to you, scoped to operating the service
- Representation that the user has the rights to what they upload
- Acceptable use, specific enough to enforce
- Your right to remove content and suspend accounts, with or without notice
- Takedown and counter-notice process, with the contact point
- Repeat infringer policy
- What happens to content when an account is deleted or terminated
- Disclaimer that you don't endorse or verify user content

## Checklist

- [ ] Takedown contact published and monitored
- [ ] DMCA agent registered, if operating in the US and relying on the safe
      harbour
- [ ] Notice-and-action process written down, with a record kept per report
- [ ] Repeat-infringer policy written and applied
- [ ] Acceptable use terms specific enough to act on
- [ ] Removal and suspension capability built, and the right to use it stated
- [ ] EXIF and document metadata stripped on upload
- [ ] Content types validated server-side
- [ ] User files served from a separate origin
- [ ] Private uploads verified genuinely private (signed, expiring, unguessable)
- [ ] Licence grant in terms is broad enough to operate and no broader
- [ ] A plan for the worst-case upload, decided before launch
