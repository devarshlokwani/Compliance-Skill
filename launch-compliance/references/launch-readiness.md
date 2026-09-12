# Launch readiness — the visible half

Everything else in this skill is about obligations. This file is about the
things that are simply *missing*, cost minutes each, and are the most visible
part of a launch.

They belong here for a practical reason: the moment someone is about to deploy
is the only moment they will fix them. The person who just shipped is not going
to come back next week to add an OG image, and every link they post between now
and then renders as a grey box.

Severity for almost all of this is **polish** — it won't get anyone sued. Two
exceptions are called out below where a launch-readiness defect is also a legal
one.

## Social previews — the highest-value ten minutes

**Open Graph tags.** Without them, every link shared to Slack, iMessage,
LinkedIn, Discord, WhatsApp or X renders as a bare URL in a grey box. This is
the single most common launch-day defect and the most visible.

```html
<meta property="og:title" content="..." />
<meta property="og:description" content="..." />
<meta property="og:image" content="https://example.com/og.png" />
<meta property="og:url" content="https://example.com" />
<meta property="og:type" content="website" />
```

- The image must be an **absolute URL**. Relative paths silently fail — this is
  the single most common mistake.
- 1200×630 is the safe size.
- Keep it under ~1MB; some crawlers give up on large images.
- Text in the image should be readable at thumbnail size.

**Twitter/X card tags.** Clients fall back to Open Graph, but without
`twitter:card` you get the small card rather than the large one:

```html
<meta name="twitter:card" content="summary_large_image" />
```

**Test before you post**, not after. Every platform caches aggressively and
some are difficult to bust — a wrong image on launch day can persist for
longer than the launch.

In Next.js App Router this is the `openGraph` and `twitter` keys of the
`metadata` export, plus `metadataBase` so relative image paths resolve to
absolute URLs.

## Title, description, canonical

**Title.** A leftover `Create Next App` shows in tabs, bookmarks, search
results and every link preview. Set a real one, and a template so child pages
inherit a consistent suffix.

**Meta description.** 140–160 characters. Without it, search engines synthesise
one from page text, usually badly. This is the one line most people read before
deciding whether to click.

**Canonical URL.** If the site answers on more than one hostname — apex and
`www`, a preview deployment domain, http and https — search engines treat each
as a separate site and split ranking between them. Set `metadataBase` and a
canonical, and pick one hostname to redirect the others to.

## robots.txt and sitemap

**robots.txt.** Without it, crawlers index anything reachable, including staging
routes and any API endpoint that returns HTML.

```
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: https://example.com/sitemap.xml
```

**The blanket `Disallow: /` case is worth its own note.** It is correct for
staging and a silent disaster in production: the site is not indexed at all, and
nothing raises an error to tell anyone. It happens when a staging robots.txt is
copied forward. The scanner reports this as **know about it** rather than
polish, because unlike a missing file it is actively doing damage and nobody
will notice for weeks.

Also: robots.txt is not an access control. Disallowing `/admin` tells everyone
where `/admin` is. Use authentication for anything that matters.

**Sitemap.** Crawlers find linked pages anyway; a sitemap speeds up discovery
of new ones and — more usefully — unlocks the coverage reporting in Search
Console that makes indexing problems visible in the first place.

## Icons and manifest

**Favicon.** Without one, the browser shows a blank document icon in tabs and
bookmarks. Include an `apple-touch-icon` at 180×180 for iOS home screens.

**Web manifest.** Needed for install-to-home-screen and for Android share
targets and splash screens. Name, short_name, icons, theme_color, display.

## The two that are more than polish

**Insecure `http://` assets.** Browsers block mixed active content outright and
downgrade or warn on passive content. On launch day these either fail silently
or put a security warning in front of users. This is **fix this month** — it is
a transport-security issue, not a cosmetic one.

**Pre-ticked consent boxes.** A checkbox for marketing or terms that is checked
by default is not valid consent under GDPR — the recitals name pre-ticked boxes
specifically — and it is enforced often because it is visible from outside the
product. Bundling marketing consent with accepting the terms fails the same
test. This is **fix this month**, and it belongs to `privacy-law.md` as much as
to this file.

## Accessibility

**This section is deliberately shallow, and the skill says so.** The scanner
checks four defects that can be detected reliably from static source. It does
**not** check colour contrast, heading order, keyboard traps, focus order, ARIA
correctness, motion sensitivity, or anything requiring a rendered page. A clean
scan here means four specific defects are absent. It does not mean the product
is accessible.

Why it's in scope at all: accessibility is increasingly a legal question, not
only a quality one. In the US, web accessibility claims under the ADA are a
large and active category of litigation. In the EU, the European Accessibility
Act brings consumer-facing digital services into scope with real obligations.

The four checks:

**1. Images without `alt`.** Screen readers announce the filename instead.
WCAG 1.1.1 Level A, and the most frequently cited failure in US complaints.
Decorative images get `alt=""` so assistive technology skips them — an empty
alt is a decision, a missing alt is an omission.

**2. Focus indicator removed.** `outline: none` in a stylesheet with no
`:focus-visible` replacement. Keyboard users then cannot see where they are,
which makes forms unusable without a mouse. WCAG 2.4.7. The fix is to replace
the ring, not to delete it:

```css
:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }
```

**3. `<div onClick>` as a button.** Not focusable, not announced as
interactive, doesn't respond to Enter or Space. WCAG 2.1.1 and 4.1.2. Use a
real `<button type="button">`; if the markup truly can't change, add
`role="button"`, `tabIndex={0}` and a key handler.

**4. Placeholder as the only label.** The placeholder disappears as soon as
someone types, so anyone interrupted mid-form loses the only indication of what
the field was for — and screen readers may not announce it at all. WCAG 3.3.2.
Use a `<label>`, visually hidden if the design demands it.

If the user wants to go further, point them at an automated checker (axe,
Lighthouse) and, more valuably, at keyboard-only testing: unplug the mouse and
try to complete the main flow. That single exercise finds more than any
static scan.

## Operational things that aren't legal but ruin launches

Worth a line each in the punchlist:

- **A 404 page** that isn't the framework default.
- **An error page** that doesn't leak a stack trace in production.
- **Analytics actually firing** — verify, don't assume.
- **Email deliverability**: SPF, DKIM and DMARC on the sending domain, or your
  signup confirmations land in spam on the busiest day you'll ever have.
- **A status or contact route.** When something breaks, people need somewhere
  to go that isn't a social media reply.
- **Uptime monitoring**, even the free tier of anything.
- **A rollback plan.** Know how to revert before you need to.

## Checklist

- [ ] Open Graph title, description, image (absolute URL), url
- [ ] `twitter:card` set to `summary_large_image`
- [ ] Preview tested on at least one platform before posting
- [ ] Real page title, with a template for child pages
- [ ] Meta description written
- [ ] Canonical URL set; one hostname chosen and the others redirected
- [ ] robots.txt present, and **not** a copied-forward `Disallow: /`
- [ ] Sitemap generated and referenced from robots.txt
- [ ] Favicon and apple-touch-icon
- [ ] Web manifest
- [ ] No `http://` asset references
- [ ] No pre-ticked consent boxes
- [ ] Images have alt text
- [ ] Focus indicators visible
- [ ] Interactive elements are real buttons and links
- [ ] Inputs have labels
- [ ] Custom 404 and a production error page that leaks nothing
- [ ] SPF, DKIM, DMARC configured
- [ ] Uptime monitoring and a rollback plan
