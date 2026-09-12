<!--
TEMPLATE: cookie policy.

Only produce this if the product sets something beyond strictly necessary
cookies. If the only cookie is a session cookie, a paragraph in the privacy
policy is enough and a separate document is noise.

The hard part is not the document — it is the gate. In the EU/UK, consent is
required BEFORE non-essential storage happens. A banner that fires the tag on
page load and asks afterwards is the specific pattern regulators penalise. If
the code has no consent gate, the finding is the gate, not the policy.

"Cookies" here means cookies, localStorage, sessionStorage, IndexedDB, pixels
and fingerprinting — the ePrivacy rule bites on storing or reading anything on
the user's device, not on cookies specifically.

Delete every one of these HTML comments before publishing.
-->

# Cookie Policy

**Last updated: [DATE]**

This page lists everything [PRODUCT NAME] stores on your device, what each item
is for, and how to change your choices.

## Your choices

<!-- Delete this section if you have no consent mechanism — and then go build one, because if you serve EU/UK users you need it. Do not describe a control that doesn't exist. -->

[You chose your preferences when you first visited. You can change them at any
time at [LINK / "Cookie settings" in the footer].]

Strictly necessary cookies can't be turned off — without them the service
doesn't work. Everything else is off until you turn it on.

## What we store

### Strictly necessary

These keep you signed in and the service working. No consent is required for
these, and turning them off isn't possible.

| Name | Purpose | Expires | Set by |
| --- | --- | --- | --- |
| [session] | [Keeps you signed in] | [30 days] | [us] |
| [csrf_token] | [Protects against cross-site request forgery] | [Session] | [us] |
| [cookie_consent] | [Remembers your choices on this page] | [12 months] | [us] |

### Analytics

<!-- Delete this section if you don't run analytics. If your analytics tool is genuinely cookieless, say so — it's a real advantage and worth stating. -->

These help us understand which features get used. [Off until you accept.]

| Name | Purpose | Expires | Set by |
| --- | --- | --- | --- |
| [ph_*] | [Product analytics: which pages and features are used] | [12 months] | [PostHog] |
| [_ga, _ga_*] | [Visitor and session measurement] | [up to 24 months] | [Google Analytics] |

[[ANALYTICS PROVIDER] is configured to [anonymise IP addresses / not use
cookies / store data in the EU].]

### Session recording

<!--
If session replay is running, it needs its own section. Bundling it under
"analytics" understates it substantially: it can capture what users type.
-->

[[TOOL]] records how people move through the product so we can find confusing
or broken flows. Recordings [mask all text you type / mask password and payment
fields]. [Off until you accept.]

| Name | Purpose | Expires | Set by |
| --- | --- | --- | --- |
| [tool_session] | [Links events into a single recording] | [PERIOD] | [TOOL] |

### Advertising

<!-- Delete unless you run ad pixels. If you do keep it, check whether this counts as a "sale" or "share" under the US state laws you're subject to — it often does, and that triggers an opt-out obligation beyond the cookie banner. -->

[These let us measure whether our ads work. Off until you accept.]

| Name | Purpose | Expires | Set by |
| --- | --- | --- | --- |
| [_fbp] | [Conversion measurement] | [3 months] | [Meta] |

## Other storage

<!-- Most cookie policies omit this and most products use it. localStorage counts. -->

We also use your browser's local storage for:

| Key | Purpose | Cleared when |
| --- | --- | --- |
| [theme] | [Remembers light or dark mode] | [You clear site data] |
| [draft_*] | [Keeps unsaved drafts if your browser closes] | [You submit or discard the draft] |

## Turning things off in your browser

You can block or delete cookies in your browser settings. Blocking strictly
necessary cookies will stop [PRODUCT NAME] working — you won't be able to stay
signed in.

[We honour the Global Privacy Control signal. If your browser sends it, we
treat it as an opt-out of [analytics and advertising storage / sale and
sharing] without you needing to do anything else.]

## Changes

If we add or remove anything that stores data on your device, we'll update this
page and the date at the top. [Adding a new non-essential item means asking for
your consent again.]

Questions: [PRIVACY EMAIL].
