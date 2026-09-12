<!--
Generated output, committed so you can see what a real report looks like
without running anything.

Source: examples/demo-project -- a deliberately incomplete Next.js app used as
the scanner's test fixture. It is not a real product, and its findings are real
findings about that fixture.

Regenerate after any change to scan.py that alters output:

    python3 launch-compliance/scripts/scan.py examples/demo-project --report examples/sample-scan.md --quiet

Then re-add this header -- the scanner does not write it. Run it with the
relative path exactly as above: the scanner echoes the path as typed, which is
what keeps this file machine-independent.
-->

# Launch compliance scan: `examples/demo-project`

_Generated 2026-09-12 by launch-compliance scan.py v1.0.0. 14 files scanned. Detected: Next.js - web._

> **What this scan is.** A pass over the source for signals that carry legal,
> privacy, security or launch obligations. It reports what the code shows.
>
> **What it is not.** Legal advice, and not an audit. It can tell you a document
> is *missing* -- that part is reliable. It cannot tell you that an existing
> document is *accurate*, that a consent banner actually blocks the tag it sits
> in front of, or that a deletion endpoint deletes everything it should.
> Anything reported as present still needs a human to read it.


## Summary

| Severity | What it means | Count |
| --- | --- | --- |
| **Blocking** | Do not open signups until this is fixed. | 2 |
| **Fix this month** | A real obligation with real penalties, but not on fire. | 6 |
| **Know about it** | Not triggered yet, or lower probability -- but know the trigger. | 9 |
| **Polish** | Won't get you sued. Will make the launch look unfinished. | 10 |

Each finding is tagged with how it was arrived at:

| Tag | Meaning |
| --- | --- |
| `absence` | we looked and it is not there |
| `pattern` | a pattern matched in your source -- read the evidence |
| `inference` | inferred from names and imports -- confirm before publishing |


## Blocking

_Do not open signups until this is fixed._

### Personal data is collected with no privacy policy

The project handles 10 categories of personal data and no privacy policy was found. A privacy notice is a precondition for lawful processing under GDPR Art. 13-14, required by every US state comprehensive privacy law, required under the Australian Privacy Act's APP 1, and required by both mobile app stores before a listing goes live. It is also the first document any integration partner or business customer asks for.

**Fix.** Draft it from the data inventory rather than from a template's guesses: the actual categories, the actual purposes, the actual retention periods, the actual recipients.

<details><summary>Where this showed up</summary>

```
components/SignupForm.tsx:15  email: form.get("email"),
components/SignupForm.tsx:17  phoneNumber: form.get("phoneNumber"),
prisma/schema.prisma:16  name String?
prisma/schema.prisma:19  dateOfBirth DateTime?
```
</details>

<sub>`docs.privacy-policy-missing` &middot; basis: `absence` &middot; reference: `references/privacy-law.md`</sub>

### Taking money with no terms of service

A payment integration is present and no terms of service were found. Without terms there is no agreed refund policy, no limitation of liability, no chosen governing law and no stated right to suspend an abusive account. If billing recurs, several jurisdictions additionally require specific pre-purchase disclosure and a cancellation path at least as easy as the signup path.

**Fix.** Write terms covering subscription mechanics, renewal and cancellation, refunds, acceptable use, suspension, liability and governing law -- then make the cancellation flow match what they promise.

<details><summary>Where this showed up</summary>

```
package.json:22  "stripe": "^17.5.0",
```
</details>

<sub>`docs.terms-missing-with-payments` &middot; basis: `absence` &middot; reference: `references/payments-and-billing.md`</sub>


## Fix this month

_A real obligation with real penalties, but not on fire._

### User data is sent to an AI provider (OpenAI)

Calls to a hosted model API were found. Whatever context you pass -- user messages, uploaded documents, rows from your database -- leaves your infrastructure and becomes a cross-border transfer to a subprocessor most users have no idea is involved. 'We use AI' is not a disclosure.

**Fix.** Name the provider in the privacy policy and the subprocessor list, say what is sent and why, check in the provider's own settings whether your data trains their models (the default differs between consumer and API tiers), and compare their retention window against what your policy promises.

<details><summary>Where this showed up</summary>

```
package.json:17  "openai": "^4.77.0",
```
</details>

<sub>`ai.provider-disclosure` &middot; basis: `inference` &middot; reference: `references/ai-features.md`</sub>

### Trackers in use with no cookie policy or consent gate

Cookies, client-side storage or analytics tags are in use and no cookie policy was found. In the EU and UK, anything beyond strictly necessary storage needs informed consent *before* it is set: the ePrivacy rule bites on the act of storing or reading, whether or not the data is personal. A banner that fires the tag and then asks is the specific pattern regulators keep fining.

**Fix.** List every cookie and storage key with its purpose and lifetime. If you serve the EU or UK, gate non-essential tags behind consent and make refusing exactly as easy as accepting.

<details><summary>Where this showed up</summary>

```
lib/analytics.ts:12  document.cookie = `mn_visitor=${crypto.randomUUID()}; path=/; max-age=31536000`;
lib/analytics.ts:13  localStorage.setItem("mn_last_seen", new Date().toISOString());
```
</details>

<sub>`docs.cookie-policy-missing` &middot; basis: `inference` &middot; reference: `references/privacy-law.md`</sub>

### No subprocessor list

9 third-party services were detected in the code. Each one that receives personal data is a processor acting on your behalf, and transparency rules require you to disclose the categories of recipients -- naming them is the accepted way to do that. You will also need this list the first time a business customer sends you a DPA to sign.

**Fix.** Publish `legal/subprocessors.md` naming each provider, what it is used for, what data it receives and where it processes. Keep it as a page you update, link it from the privacy policy, and offer notice before you add a new one.

<details><summary>Where this showed up</summary>

```
package.json:22  Stripe -- Payments and subscription billing
package.json:16  NextAuth / Auth.js -- Authentication and session management
package.json:14  Supabase -- Hosted Postgres, auth and file storage
.env.example:5  Google OAuth -- Sign in with Google
package.json:18  PostHog -- Product analytics, session replay, feature flags
package.json:13  Sentry -- Error and performance monitoring
```
</details>

<sub>`docs.subprocessors-missing` &middot; basis: `inference` &middot; reference: `references/privacy-law.md`</sub>

### Assets referenced over http://

One or more assets load over plain http. Browsers block mixed active content outright and downgrade or warn on passive content, so on launch day these either fail silently or put a security warning in front of your users.

**Fix.** Switch every reference to https, or self-host the asset.

<details><summary>Where this showed up</summary>

```
app/page.tsx:18  src="http://cdn.partner-widgets.example.net
```
</details>

<sub>`launch.insecure-assets` &middot; basis: `pattern` &middot; reference: `references/launch-readiness.md`</sub>

### Consent checkbox is pre-ticked

A consent or marketing checkbox is checked by default. Under GDPR consent has to be a freely given, specific, informed and unambiguous affirmative action -- a pre-ticked box is named in the recitals as exactly what does not qualify. It is also one of the most commonly enforced points precisely because it is visible from outside the product.

**Fix.** Default the box to unchecked, keep marketing consent separate from accepting the terms, and record when and how each user consented.

```
// Before -- not valid consent under GDPR, and it bundles two separate things
<input type="checkbox" name="marketingOptIn" defaultChecked />
Send me product updates, and I accept the terms

// After -- unticked, and the two are separated
<input type="checkbox" name="marketingOptIn" />
Send me occasional product updates (optional)

<input type="checkbox" name="acceptedTerms" required />
I accept the <a href="/terms">terms</a> and <a href="/privacy">privacy policy</a>

// Record what they consented to, when, and to which version of the text.
```

<details><summary>Where this showed up</summary>

```
components/SignupForm.tsx:33  <input type="checkbox" name="marketingOptIn" defaultChecked />
```
</details>

<sub>`launch.pre-ticked-consent` &middot; basis: `pattern` &middot; reference: `references/privacy-law.md`</sub>

### No account or data deletion path

Personal data is stored and nothing in the code looks like a deletion route. Deletion on request is a right under GDPR Art. 17, under every US state comprehensive privacy law, and under APP 11.2 in Australia -- and both mobile app stores now require an in-app account deletion path for any app that lets people create an account. A policy that promises deletion with no mechanism behind it is the worst of both worlds: the obligation without the ability to meet it.

**Fix.** Build a deletion endpoint that covers the primary database, uploaded files, backups, logs, caches and third-party copies (analytics, email, support tooling). Decide up front what you must keep for legal reasons, and say exactly that in the policy.

<sub>`mechanism.deletion-missing` &middot; basis: `inference` &middot; reference: `references/privacy-law.md`</sub>


## Know about it

_Not triggered yet, or lower probability -- but know the trigger._

### Clickable div or span used instead of a button

An element with an `onClick` handler is neither a button nor a link and carries no role or tab index. It cannot be reached by keyboard, is not announced as interactive, and does not respond to Enter or Space. WCAG 2.1.1 and 4.1.2.

**Fix.** Use a real `<button type="button">`. If the markup genuinely cannot change, add `role="button"`, `tabIndex={0}` and a key handler for Enter and Space.

```
// Before
<div onClick={handleClick}>See how it works</div>

// After -- keyboard accessible and announced correctly, for free
<button type="button" onClick={handleClick}>See how it works</button>

// If the markup genuinely cannot change:
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleClick(); } }}
>
```

<details><summary>Where this showed up</summary>

```
app/page.tsx:21  <div onClick={() =>
```
</details>

<sub>`a11y.div-as-button` &middot; basis: `pattern` &middot; reference: `references/launch-readiness.md`</sub>

### Focus indicator removed with no replacement

`outline: none` appears in a stylesheet that never defines a `:focus-visible` style. Keyboard users then have no way to see where they are, which makes forms and navigation effectively unusable without a mouse. WCAG 2.4.7.

**Fix.** Replace the default ring rather than deleting it: pair `outline: none` with a `:focus-visible` rule that draws something clearly visible against your background.

```
/* Replace the ring instead of deleting it. :focus-visible only shows it for
   keyboard users, which is the reason people reach for `outline: none`. */
button:focus-visible,
a:focus-visible,
input:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
```

<details><summary>Where this showed up</summary>

```
app/globals.css:17  outline: none
```
</details>

<sub>`a11y.focus-removed` &middot; basis: `pattern` &middot; reference: `references/launch-readiness.md`</sub>

### Images without alt text

One or more image elements have no `alt` attribute, so screen readers announce the file name instead. This is WCAG 1.1.1 Level A -- the single most frequently cited failure in US ADA web accessibility complaints, and in scope for the European Accessibility Act for consumer-facing services.

**Fix.** Add `alt` text describing the image's purpose, or `alt=""` if it is purely decorative so assistive technology skips it.

```
<img src="/hero.png" alt="The dashboard, showing this week's meeting summaries" />

<!-- Decorative only? An empty alt is a decision; a missing one is an omission. -->
<img src="/divider.svg" alt="" />
```

<details><summary>Where this showed up</summary>

```
app/page.tsx:12  <img src="/hero-dashboard.png" width={880} height={420} />
```
</details>

<sub>`a11y.img-missing-alt` &middot; basis: `pattern` &middot; reference: `references/launch-readiness.md`</sub>

### User file uploads are handled

File upload handling was detected. Accepting user content brings its own set of obligations: a notice-and-takedown path (and, in the US, a registered DMCA agent if you want to keep safe-harbour protection), a moderation policy, and metadata hygiene -- photos carry GPS coordinates and device identifiers in EXIF unless you strip them.

**Fix.** Add takedown and acceptable-use terms, strip EXIF on upload, validate content types server-side rather than trusting the extension, and serve user files from a separate origin so a malicious upload cannot execute as your site.

<details><summary>Where this showed up</summary>

```
package.json:23  "uploadthing": "^7.4.0"
```
</details>

<sub>`content.user-uploads` &middot; basis: `inference` &middot; reference: `references/user-content.md`</sub>

### No vulnerability disclosure contact

There is no SECURITY.md or security.txt. When a researcher finds something, the absence of a named contact is what turns a quiet report into a public disclosure, or into an email to a support address that nobody reads for three weeks.

**Fix.** Add `SECURITY.md` with a contact address, what is in scope, the response time you commit to, and whether you permit good-faith testing.

```
# SECURITY.md at the repository root

## Reporting a vulnerability
Email security@example.com. You'll get an acknowledgement within 2 business
days and an assessment within 7.

We won't pursue legal action against good-faith research under this policy.
Please don't access data that isn't yours, and give us time to fix it before
disclosing publicly.
```

<sub>`docs.security-missing` &middot; basis: `absence` &middot; reference: `references/security-baseline.md`</sub>

### robots.txt blocks every crawler

robots.txt has a blanket `Disallow: /` for all user agents. That is correct for a staging site and a silent disaster for a launched one: the site will not be indexed at all, and nothing anywhere raises an error to tell you.

**Fix.** If this is production, drop the blanket rule and disallow only the paths you actually want hidden. If the file was copied from staging, check what else came with it.

<details><summary>Where this showed up</summary>

```
public/robots.txt:1  User-agent: * / Disallow: /
```
</details>

<sub>`launch.robots-blocks-all` &middot; basis: `pattern` &middot; reference: `references/launch-readiness.md`</sub>

### No data export path

No data export route was found. Portability is a right under GDPR Art. 20 and most US state laws, but the practical trigger is usually a support email rather than a regulator -- and hand-writing a database query every time does not scale past the first few.

**Fix.** Add an export route returning the user's records in a structured, machine-readable format such as JSON or CSV.

<sub>`mechanism.export-missing` &middot; basis: `inference` &middot; reference: `references/privacy-law.md`</sub>

### No licence file

The repository has no licence. Under default copyright that means nobody may copy, modify or distribute the code -- including the contributor who wanted to send you a fix.

**Fix.** Add a LICENSE file. MIT for maximum permissiveness, Apache-2.0 if you also want an express patent grant. If the code is deliberately not open, say so explicitly instead of leaving it ambiguous.

<sub>`repo.license-missing` &middot; basis: `absence` &middot; reference: `references/security-baseline.md`</sub>

### Possible high-risk data categories: Date of birth, Location

Field names suggest data that carries obligations beyond the general privacy regime: special-category data under GDPR Art. 9, sector rules such as HIPAA or GLBA, biometric statutes such as Illinois BIPA (which carries a private right of action and per-scan damages), or children's data under COPPA and the age-appropriate design codes. These are the categories where a generated policy is not adequate.

**Fix.** First confirm you actually hold this data -- field names lie in both directions. If you do, this is the part to take to a lawyer; the exposure is wildly out of proportion to the cost of one conversation.

<details><summary>Where this showed up</summary>

```
prisma/schema.prisma:19  dateOfBirth DateTime?
prisma/schema.prisma:55  latitude Float?
```
</details>

<sub>`risk.special-category` &middot; basis: `inference` &middot; reference: `references/high-risk-categories.md`</sub>


## Polish

_Won't get you sued. Will make the launch look unfinished._

### Input labelled only by its placeholder

An input has a placeholder but no associated label or aria-label. The placeholder disappears the moment someone types, so anyone interrupted mid-form loses the only indication of what the field was for, and screen readers may not announce it at all. WCAG 3.3.2.

**Fix.** Add a `<label htmlFor=...>` -- visually hidden if the design needs it -- or an `aria-label`. Keep the placeholder for an example value, not for the field name.

```
// Before -- the label vanishes as soon as they type
<input type="email" placeholder="Work email" />

// After
<label htmlFor="email">Work email</label>
<input id="email" type="email" placeholder="you@company.com" />

/* If the design has no room for a visible label, hide it from sight only --
   never use display:none, which hides it from screen readers too. */
.sr-only {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0 0 0 0); white-space: nowrap; border: 0;
}
```

<details><summary>Where this showed up</summary>

```
components/SignupForm.tsx:27  <input type="email" name="email" placeholder="Work email" required />
components/SignupForm.tsx:28  <input type="password" name="password" placeholder="Password" required />
components/SignupForm.tsx:29  <input type="tel" name="phoneNumber" placeholder="Mobile (optional)" />
```
</details>

<sub>`a11y.placeholder-as-label` &middot; basis: `pattern` &middot; reference: `references/launch-readiness.md`</sub>

### No compliance checklist in the repo

Nothing records what was decided, who owns it, or what should trigger another look. The obligations change when the product changes, and the change that matters is usually small enough that nobody thinks to revisit anything.

**Fix.** Write `COMPLIANCE.md` with the open items, owners, dates and review triggers: a new third-party service, a new country, a paid tier, file uploads, an AI feature, a first enterprise customer.

<sub>`docs.compliance-missing` &middot; basis: `absence`</sub>

### No canonical URLs

No canonical URL is declared. If the site answers on more than one hostname -- apex and www, a preview deployment domain, http and https -- search engines treat each as a separate site and split ranking signals between them.

**Fix.** Set `metadataBase` plus `alternates: { canonical: '/' }` in Next.js metadata, or add `<link rel="canonical">` to the document head.

```
// Next.js metadata
metadataBase: new URL('https://example.com'),
alternates: { canonical: '/' },

<!-- plain HTML -->
<link rel="canonical" href="https://example.com/" />
```

<sub>`launch.canonical-missing` &middot; basis: `absence` &middot; reference: `references/launch-readiness.md`</sub>

### No favicon

No favicon or app icon. Browsers fall back to a blank document icon in tabs, bookmarks and history -- the site looks broken next to every other open tab.

**Fix.** Add `app/icon.png` (Next.js) or `public/favicon.ico`, plus a 180x180 `apple-touch-icon.png` for iOS home screens.

```
# Next.js App Router picks these up by filename -- no markup needed:
app/icon.png              # 512x512 works everywhere
app/apple-icon.png        # 180x180, for iOS home screens

<!-- anything else -->
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
```

<sub>`launch.favicon-missing` &middot; basis: `absence` &middot; reference: `references/launch-readiness.md`</sub>

### Default framework title still in place

The page title is still the scaffold default. It shows in browser tabs, bookmarks, search results and every link preview -- it is the first thing that says nobody finished this.

**Fix.** Set a real `title`, and a `title.template` so child pages inherit a consistent suffix.

<details><summary>Where this showed up</summary>

```
app/layout.tsx:5  title: "Create Next App"
```
</details>

<sub>`launch.framework-title` &middot; basis: `pattern` &middot; reference: `references/launch-readiness.md`</sub>

### No web app manifest

No web app manifest. The site cannot be installed to a home screen, and Android share targets and splash screens fall back to the bare URL.

**Fix.** Add `app/manifest.ts` or `public/site.webmanifest` with name, short_name, icons, theme_color and display.

```
// Next.js app/manifest.ts
import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Product name',
    short_name: 'Product',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#000000',
    icons: [{ src: '/icon-512.png', sizes: '512x512', type: 'image/png' }],
  }
}
```

<sub>`launch.manifest-missing` &middot; basis: `absence` &middot; reference: `references/launch-readiness.md`</sub>

### No meta description

No meta description. Search engines will synthesise one from page text, usually badly, and you lose control of the single line most people read before deciding whether to click.

**Fix.** Add a 140-160 character description to the root metadata and override it per page where it matters.

```
// Next.js metadata -- 140-160 characters
description: 'What it does and who it is for, in one sentence someone would repeat.',

<!-- plain HTML -->
<meta name="description" content="..." />
```

<sub>`launch.meta-description-missing` &middot; basis: `absence` &middot; reference: `references/launch-readiness.md`</sub>

### No Open Graph tags

No Open Graph metadata. Every link shared to Slack, iMessage, LinkedIn, Discord or X renders as a bare grey box with a URL under it. This is the most visible launch-day defect there is and it takes about ten minutes to fix.

**Fix.** Set `openGraph: { title, description, url, images: [...] }` in your root metadata, or add `og:title`, `og:description`, `og:image` and `og:url` meta tags. Use a 1200x630 image and check it with a preview debugger before you post anywhere.

```
// Next.js app/layout.tsx
export const metadata = {
  metadataBase: new URL('https://example.com'),   // makes relative image paths absolute
  openGraph: {
    title: 'Product name',
    description: 'One sentence someone would repeat to a colleague.',
    url: 'https://example.com',
    siteName: 'Product name',
    images: [{ url: '/og.png', width: 1200, height: 630 }],
    type: 'website',
  },
}

<!-- plain HTML equivalent; og:image MUST be an absolute URL -->
<meta property="og:title"       content="Product name" />
<meta property="og:description" content="One sentence." />
<meta property="og:image"       content="https://example.com/og.png" />
<meta property="og:url"         content="https://example.com" />
<meta property="og:type"        content="website" />
```

<sub>`launch.og-tags-missing` &middot; basis: `absence` &middot; reference: `references/launch-readiness.md`</sub>

### No sitemap

Nothing in the project generates a sitemap. Crawlers will still find linked pages, but discovery of new ones is slower and you lose the coverage reporting in Search Console that makes indexing problems visible in the first place.

**Fix.** Add `app/sitemap.ts` (Next.js), a static `public/sitemap.xml`, or your framework's equivalent, and point robots.txt at it.

```
// Next.js app/sitemap.ts
import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: 'https://example.com',          lastModified: new Date(), priority: 1 },
    { url: 'https://example.com/pricing',  lastModified: new Date() },
  ]
}
```

<sub>`launch.sitemap-missing` &middot; basis: `absence` &middot; reference: `references/launch-readiness.md`</sub>

### No Twitter/X card tags

No `twitter:card` metadata. X and several other clients fall back to Open Graph, but without `summary_large_image` you get the small thumbnail card instead of the large one.

**Fix.** Add `twitter: { card: 'summary_large_image', title, description, images }` to your metadata, or the equivalent meta tags.

```
// Next.js metadata
twitter: {
  card: 'summary_large_image',
  title: 'Product name',
  description: 'One sentence.',
  images: ['/og.png'],
}

<!-- plain HTML -->
<meta name="twitter:card" content="summary_large_image" />
```

<sub>`launch.twitter-tags-missing` &middot; basis: `absence` &middot; reference: `references/launch-readiness.md`</sub>


## What the code shows

Confirm every row below with whoever built the feature before it goes into a published document. The scanner sees imports and field names; it cannot see intent, and it cannot see anything configured in a dashboard rather than in the repository.


### Third-party services (candidate subprocessors)

| Service | Category | Used for | Typically receives |
| --- | --- | --- | --- |
| Stripe | payments | Payments and subscription billing | Name, email, billing address, card token, purchase history |
| NextAuth / Auth.js | auth | Authentication and session management | Email, name, avatar, provider account ID |
| Supabase | backend | Hosted Postgres, auth and file storage | Everything stored in the database; auth identifiers; uploaded files |
| Google OAuth | auth | Sign in with Google | Email, name, avatar, Google account ID |
| PostHog | analytics | Product analytics, session replay, feature flags | IP address, device data, events, and anything captured in session replay |
| Sentry | error-tracking | Error and performance monitoring | Stack traces, request URLs, and request bodies/headers if not scrubbed; user ID if set |
| Resend | email | Transactional email delivery | Recipient email address, email content |
| OpenAI | ai | LLM inference | Prompt content -- including any user text, files or context you pass |
| UploadThing | storage | File upload handling and hosting | Uploaded files, uploader identifier |
| Prisma | database | ORM -- its schema is the best source for your data inventory | Local library; no data leaves your infrastructure |


### Personal data found in schemas, forms and types

| Data | Category | First seen |
| --- | --- | --- |
| Usage metadata | behavioural | `prisma/schema.prisma:23` |
| Email address | contact | `components/SignupForm.tsx:15` |
| Phone number | contact | `components/SignupForm.tsx:17` |
| Password / credential | credential | `components/SignupForm.tsx:16` |
| IP address | device | `prisma/schema.prisma:24` |
| User agent | device | `prisma/schema.prisma:25` |
| Date of birth **(high-risk)** | identity | `prisma/schema.prisma:19` |
| Name | identity | `prisma/schema.prisma:16` |
| Profile image | identity | `prisma/schema.prisma:17` |
| Location **(high-risk)** | location | `prisma/schema.prisma:55` |

This is the raw material for a data inventory, not the inventory itself. For each row you still need: why it is collected, the lawful basis, where it is stored, how long it is kept, and who else can see it.


### Cookies and client-side storage

- **document.cookie** -- First-party cookie written in client code `lib/analytics.ts:12`
- **localStorage** -- Persistent client-side storage `lib/analytics.ts:13`


### Mechanisms the documents will have to promise

| Mechanism | Signal in the code |
| --- | --- |
| Account / data deletion | nothing found |
| Data export | nothing found |
| Consent gate | nothing found |
| Retention / cleanup job | nothing found |


## Next

1. Confirm the inventory above with whoever built each feature. Scanners miss anything configured in a dashboard rather than in code.
2. Work the blocking list first, then the monthly one. Resist the urge to start with the polish items because they are easy.
3. Verify any threshold, deadline or fee before relying on it -- privacy law moves faster than any static reference, this one included.
4. Re-run this when you add a third-party service, open to a new country, add a paid tier, add file uploads, add an AI feature, or sign a first enterprise customer.

