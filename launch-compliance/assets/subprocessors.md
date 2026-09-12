<!--
TEMPLATE: subprocessor list.

Fill this from the scanner's "Third-party services" table, confirmed with the
user. It is the single most reusable document in the set: the privacy policy
links to it, enterprise customers ask for it, and it is the thing you update
rather than re-editing three documents every time you add a tool.

Two columns people get wrong:
  * "Where it processes" — check the provider's actual region setting for THIS
    account, not their marketing page. Many offer EU hosting and default to US.
  * "Trains on your data" — verify in the console for the API key in use. The
    default differs between consumer and API tiers and it changes.

Record the date you checked. That's what makes this document trustworthy later.

Delete every one of these HTML comments before publishing.
-->

# Subprocessors

**Last updated: [DATE]**

[PRODUCT NAME] uses the services below to operate. Each one processes personal
data on our behalf, only for the purpose listed, and under a data processing
agreement with us.

We review this list whenever we add or change a service. [To be notified of
changes, subscribe at [LINK] / email [PRIVACY EMAIL].]

## Infrastructure

| Provider | What it does for us | Data it receives | Where it processes | DPA |
| --- | --- | --- | --- | --- |
| [Vercel] | [Application hosting] | [Request metadata, IP addresses] | [US / EU] | [Link] |
| [Neon] | [Database hosting] | [Everything stored in the product] | [EU (Frankfurt)] | [Link] |
| [Cloudflare R2] | [File storage] | [Files you upload] | [Auto (EU)] | [Link] |

## Product features

| Provider | What it does for us | Data it receives | Where it processes | DPA |
| --- | --- | --- | --- | --- |
| [Stripe] | [Payments and subscriptions] | [Name, email, billing address, card details] | [US, EU] | [Link] |
| [Resend] | [Transactional email] | [Email address, email content] | [US] | [Link] |
| [OpenAI] | [Generating summaries] | [The content you submit for summarisation] | [US] | [Link] |

<!-- For every AI provider, add this line. Verify it before writing it. -->

[[AI PROVIDER] does not use our API content to train its models. It retains
content for up to [PERIOD] for abuse monitoring. Verified [DATE].]

## Analytics and monitoring

| Provider | What it does for us | Data it receives | Where it processes | DPA |
| --- | --- | --- | --- | --- |
| [PostHog] | [Product analytics] | [IP address, device data, feature usage events] | [EU] | [Link] |
| [Sentry] | [Error monitoring] | [Error details, request URLs, user ID] | [US / EU] | [Link] |

<!-- If your error tracker can capture request bodies, say what you've done about it. Most people have not checked. -->

[[ERROR TRACKER] is configured to scrub request bodies and headers before they
leave our servers.]

## Support and internal tools

<!-- Delete if you have none. But check: a shared inbox, a CRM, a Slack workspace receiving webhook notifications with user emails in them, and a spreadsheet of signups are all subprocessors. -->

| Provider | What it does for us | Data it receives | Where it processes | DPA |
| --- | --- | --- | --- | --- |
| [Google Workspace] | [Email and documents] | [Anything in support correspondence] | [US / EU] | [Link] |
| [Slack] | [Internal notifications] | [New-signup notifications containing email addresses] | [US] | [Link] |

## International transfers

Where a provider above processes data outside [THE EEA / THE UK / AUSTRALIA],
we rely on [STANDARD CONTRACTUAL CLAUSES / the provider's adequacy
certification / YOUR ACTUAL MECHANISM], as set out in each provider's data
processing agreement.

## Changes

We'll update this page when we add, remove or change a provider.
[We give [30] days notice before a new subprocessor starts processing customer
data, and enterprise customers can object during that period.]

<!--
That notice commitment is worth making only if you'll actually do it. Business
customers ask for it, but it's a real operational obligation — an unkept
promise here surfaces at exactly the wrong moment, during a security review.
-->

Questions: [PRIVACY EMAIL].
