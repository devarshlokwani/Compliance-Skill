# Security baseline — the floor for anything with a login

This is not a security audit and it is not a pentest. It is the set of things
that, if missing, will either cause an incident or turn a small one into a
notifiable breach. Scope it to what a small team can actually do before launch.

Security belongs in a compliance skill for a specific reason: **most privacy
obligations are discharged by security controls.** GDPR Art. 32 and Australia's
APP 11 both require "appropriate" measures, and a breach is what converts a
paperwork gap into a notification, a regulator conversation, and an email to
every user.

## Secrets

**The blocking one.** A committed credential is treated as compromised the
moment it lands: it is in the reflog, in every clone, and on public repositories
it is found by scanning bots within minutes.

- Rotate at the provider **first**. Removing the line does not invalidate the
  key — this is the step people skip.
- Then move it to an environment variable and confirm `.env` is gitignored.
- Then purge history if the repo is or will be public. Note that a force-push
  does not remove the object from forks or from GitHub's cached views; rotation
  is what actually fixes it.
- `NEXT_PUBLIC_*`, `VITE_*`, `REACT_APP_*` and equivalents are **shipped to the
  browser**. A service key in one of those is public. This is the most common
  way a Supabase service-role key leaks.

Turn on the platform's secret scanning and push protection. It is free and it
catches the next one.

## Authentication

- **Don't roll your own** unless you have a specific reason. The hosted and
  library options are good now.
- **Password storage**: a slow, salted hash designed for the purpose — bcrypt,
  scrypt, Argon2. Never SHA-256, never MD5, never anything unsalted.
- **Session cookies**: `HttpOnly`, `Secure`, `SameSite=Lax` or `Strict`. A
  token readable from JavaScript is a token an XSS steals.
- **Rate limit authentication endpoints** — login, signup, password reset, OTP
  verification. Credential stuffing is automated and constant.
- **Password reset tokens**: single-use, short-lived, and invalidating existing
  sessions on use.
- **Email enumeration**: the same response whether or not the account exists,
  on both login and reset. Often decided against for UX, which is a legitimate
  trade — just make it a decision rather than an accident.
- **Offer MFA** if the account holds anything worth stealing.

## Authorisation — where the real bugs are

Authentication answers "who are you". Authorisation answers "may you touch
this". **Broken object-level authorisation is the most common serious
vulnerability in small applications**, and it is invisible in the UI because
the UI never shows you the button.

Concretely: every handler that takes an ID from the request must check that the
ID belongs to the caller. Not in the frontend. In the handler.

```
// Wrong: fetches whatever ID was asked for
const note = await db.note.findUnique({ where: { id: params.id } })

// Right: ownership is part of the query
const note = await db.note.findFirst({ where: { id: params.id, userId: session.user.id } })
```

Check the same thing for: file downloads and signed URLs, admin routes,
webhooks, background jobs, and anything with a sequential or guessable ID. If
the app uses row-level security, verify it is actually enabled on each table
rather than assumed.

## Transport and headers

- HTTPS everywhere, HTTP redirected, HSTS set.
- No mixed content — the scanner flags `http://` asset references because
  browsers block or downgrade them.
- A Content-Security-Policy. Even a loose one that forbids inline script is
  meaningfully better than none, and it is the main structural defence against
  XSS.
- `X-Content-Type-Options: nosniff`, a sensible `Referrer-Policy`, and
  `X-Frame-Options`/`frame-ancestors` if the app shouldn't be embedded.
- CORS: name the origins. `Access-Control-Allow-Origin: *` combined with
  credentials is a data-exfiltration path.

## Input and output

- **SQL injection**: parameterised queries or an ORM. The risk returns the
  moment someone writes a raw query with template interpolation.
- **XSS**: frameworks escape by default; the danger is `dangerouslySetInnerHTML`,
  `v-html`, and rendering markdown or model output as raw HTML. Sanitise on
  render, not only on store.
- **SSRF**: if the app fetches a user-supplied URL — link previews, webhooks,
  avatar imports — validate the destination and block internal ranges and cloud
  metadata endpoints.
- **File uploads**: validate content type server-side, cap size, generate your
  own filenames, and serve from a separate origin.
- **Webhooks**: verify the signature. An unverified billing webhook is an
  authorisation bypass — anyone who knows the URL can grant themselves a
  subscription.

## Logging — the privacy-shaped security problem

Logs are where personal data accumulates without anyone deciding it should.

- Don't log request bodies wholesale. Error trackers do this by default in some
  configurations (`sendDefaultPii` and friends) — check the setting rather than
  assuming.
- Never log passwords, tokens, cookies, card data or full API keys, including
  in failure paths, which are the ones nobody reviews.
- Session-replay tools capture form input unless masking is on. Verify it is.
- Set a retention period on logs and enforce it. "We keep logs forever" is both
  a retention breach and a bigger blast radius when something goes wrong.
- Your deletion mechanism has to reach logs too, or the deletion claim is false.

## Dependencies and infrastructure

- Enable automated dependency alerts and actually act on them.
- Lockfiles committed; builds reproducible.
- Database not publicly reachable; if it must be, restrict by IP and require
  TLS.
- Admin interfaces behind authentication, and preferably not on the public
  internet at all.
- Backups that exist, and that have been **restored at least once**. An
  untested backup is a belief, not a control.
- Backups encrypted, with a retention period — and remember they are in scope
  for deletion requests, which is the hardest part of any deletion promise to
  keep honest. Say what you actually do: most teams delete from backups on the
  normal backup rotation rather than surgically, and saying that plainly is
  both honest and generally acceptable.

## Vulnerability disclosure

Publish a `SECURITY.md` (and optionally `/.well-known/security.txt`) with:

- an address that reaches a human
- what is in scope
- the response time you commit to
- whether you permit good-faith testing, and a promise not to pursue legal
  action against researchers who follow the policy

Without this, a researcher's options are an unmonitored support address or a
public post. The file costs ten minutes.

## Incident response

Write this **before** you need it. Under GDPR you have 72 hours from awareness
to notify the supervisory authority; Australia's NDB scheme sets an assessment
window and then notification. Neither is achievable if the first hour is spent
working out who to call.

A one-page runbook, in the repo:

1. **Who leads.** A name. Not a role that nobody holds.
2. **How to contain.** Rotate keys, revoke sessions, disable the endpoint.
3. **How to assess.** What data, whose, how many, what harm is likely.
4. **The clock.** When did we become aware? That timestamp starts everything.
5. **Who to notify.** Regulator (which one), affected users, payment provider,
   insurer, enterprise customers with contractual notification windows.
6. **What to say.** A holding statement drafted in advance.
7. **What to record.** Every decision and its time — regulators ask for the
   timeline, and reconstructing it afterwards is miserable.

## Checklist

- [ ] No credentials in the repository; the ones that were there are rotated
- [ ] Secret scanning and push protection enabled
- [ ] No service keys in client-exposed environment variables
- [ ] Passwords hashed with a purpose-built algorithm
- [ ] Session cookies HttpOnly, Secure, SameSite
- [ ] Rate limiting on auth endpoints and anything expensive
- [ ] Every handler checks ownership of the object it touches
- [ ] HTTPS, HSTS, CSP, nosniff, referrer policy
- [ ] CORS restricted to named origins
- [ ] Webhook signatures verified
- [ ] Logs free of personal data and credentials; retention set
- [ ] Session replay masking confirmed
- [ ] Dependency alerts on
- [ ] Database not publicly reachable
- [ ] Backups exist, are encrypted, and have been restored once
- [ ] SECURITY.md published
- [ ] Incident runbook written, with names and a clock
