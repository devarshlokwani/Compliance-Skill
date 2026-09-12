# Payments and billing — what taking money makes you

> **Verify before quoting.** The FTC negative-option / click-to-cancel rule has
> been through litigation and its status has changed; state auto-renewal
> statutes differ in their specifics; VAT and sales-tax registration thresholds
> change annually; app-store commission and external-payment rules are actively
> litigated. Check current positions before stating any of them as fact.

## The moment the obligations attach

They attach when you take the first payment, not when you incorporate, hire a
lawyer, or hit a revenue number. Adding Stripe to a side project makes you a
merchant with disclosure duties, refund exposure, tax registration questions
and chargeback liability — the same day.

This is why a missing terms of service goes in **blocking** when a payment
integration is present, and in **fix this month** when it isn't.

## Auto-renewal: the most-enforced thing on this page

Any recurring charge — subscriptions, trials that convert, annual plans — is a
"negative option" and sits under a dense set of overlapping rules: FTC
authority in the US, state auto-renewal statutes (California's being the
most-cited), consumer law in the EU and UK, and Australian Consumer Law.

What they broadly require, and what to check in the actual product:

**Before the charge:**
- Clear and conspicuous disclosure of the renewal terms **adjacent to the
  purchase button**, not in linked terms. Price, frequency, and that it renews
  until cancelled.
- If a free trial converts to paid: when, and at what price, stated up front.
- Affirmative consent to the *recurring* charge specifically — not consent to
  the purchase with recurrence buried in it.

**After the charge:**
- An acknowledgement with the cancellation instructions in it.
- Advance notice before a material change in price or terms. Several regimes
  also require notice before an annual renewal.

**Cancellation:**
- **At least as easy as signing up.** If they subscribed in two clicks online,
  they must be able to cancel in roughly two clicks online. A phone-only or
  email-only cancellation path for an online signup is the single most
  frequently penalised dark pattern in this area.
- No retention flow that obstructs. Offering a discount on the way out is
  fine; requiring the user to click through it repeatedly, or hiding the
  confirm button, is not.

Check the actual cancellation flow in the product, not the promise in the
terms. If the terms say "cancel anytime in settings" and settings has no such
control, that gap is the finding.

## Refunds

There is no universal right to a refund — and there are several specific ones:

- **EU/UK distance selling** gives consumers a 14-day withdrawal right for
  distance contracts. For digital content delivered immediately, you can lose
  that right, but **only if** the consumer gave express consent to immediate
  performance and acknowledged losing the right. That acknowledgement has to
  exist in the checkout flow; a line in the terms is not enough.
- **Australian Consumer Law** provides consumer guarantees that cannot be
  contracted out of. A blanket "no refunds under any circumstances" is not just
  unenforceable there — stating it can itself be a misrepresentation.
- **Card network rules and chargebacks** operate independently of your policy.
  A customer who disputes has a path regardless of what your terms say.

Write a refund policy you will actually honour, state it plainly, and put it
where people see it before paying. An unstated policy defaults to whatever the
customer's jurisdiction, their card network and your payment provider decide
between them.

## PCI scope — usually small, occasionally enormous

If card data never touches your server — hosted checkout, Stripe Elements,
Payment Element, a redirect flow — your PCI burden is minimal (typically a
self-assessment questionnaire, and often your processor handles most of it).

It becomes enormous the moment you:
- accept raw card numbers on your own form and post them to your backend,
- log a request body containing card data (this is the accidental one),
- or store a PAN anywhere, including in an error tracker.

The practical rule: **never let card data enter your application**. If the scan
found `credit_card`, `card_number` or `cvv` as fields in a schema, that is a
conversation to have immediately — it is almost always a mistake rather than a
design decision.

## Tax — the part nobody plans for

Selling digital services across borders creates tax registration obligations
that are unrelated to your size or profitability:

- **EU VAT on digital services** is generally due in the *customer's* country,
  from the first sale for cross-border B2C, with the OSS scheme available to
  file in one place rather than 27.
- **UK VAT** has its own registration threshold for domestic supply and its own
  rules for digital services.
- **US sales tax** is a per-state economic-nexus question, with thresholds that
  vary by state and are periodically revised.
- **Australian GST** has a registration threshold and specific rules for
  imported digital services.

The realistic options for a small team:

1. **Use a merchant of record** — Paddle, Lemon Squeezy, Polar, and similar.
   They become the seller of record and take on the tax registration and
   remittance. This is why they cost more than a payment processor, and for
   most solo products it is the right trade.
2. **Use a payment processor and handle tax yourself** — cheaper per
   transaction, and you own the registrations and filings.

The distinction matters for the documents too: with a merchant of record, the
customer's contract for the sale is with *them*, which changes what your terms
should say. Don't copy terms from a Stripe-based product into a Paddle-based
one without checking this.

## App stores

If the product ships through the App Store or Play Store:

- **Digital goods and subscriptions generally must use the platform's
  in-app purchase**, with the platform's commission — the external-payment
  carve-outs vary by jurisdiction and are actively litigated. Check the current
  rules for the markets you're in.
- **Subscription disclosure requirements** are enforced by review, and rejection
  for this is routine.
- **Privacy labels / data-safety declarations** must match what the app
  actually does, including what your SDKs do. A mismatch is both a review
  failure and, in the US, an FTC-shaped problem.
- **In-app account deletion** is required for apps that let users create an
  account. Your deletion mechanism is now a store-listing requirement, not just
  a privacy one.

## Chargebacks, fraud and the operational floor

- Keep evidence of delivery: timestamps, IPs, what the customer accessed.
- Send a receipt every time, with your trading name on it — an unrecognised
  descriptor on a card statement is a common cause of disputes.
- Make the statement descriptor match the product name people know.
- Expect and plan for card testing on any public payment endpoint. Rate limit,
  and turn on your processor's fraud tooling before launch rather than after
  the first wave.

## Terms of service clauses that specifically matter here

- Subscription mechanics: price, billing period, renewal, what happens on
  failed payment
- Cancellation: how, when it takes effect, what happens to data afterwards
- Refunds: your actual policy, stated plainly
- Price changes: notice period, and the right to cancel before they apply
- Taxes: whether prices are inclusive or exclusive, and who bears them
- Suspension and termination for non-payment or abuse
- Limitation of liability and warranty disclaimers — noting that consumer
  protections in the EU, UK and Australia limit how far these can go, and that
  overreaching clauses can be unenforceable *and* treated as misleading
- Governing law and dispute resolution

## Checklist

- [ ] Terms of service exist and describe the actual billing behaviour
- [ ] Renewal terms disclosed adjacent to the purchase button
- [ ] Trial conversion date and price stated before purchase
- [ ] Cancellation is self-serve and at least as easy as signup — verified in
      the product, not just in the terms
- [ ] Refund policy written, honourable, and visible before payment
- [ ] EU/UK immediate-performance acknowledgement captured at checkout, if
      selling digital content to consumers there
- [ ] No card data touching your servers or logs
- [ ] Tax approach decided: merchant of record, or registrations owned
- [ ] Receipts sent; statement descriptor recognisable
- [ ] Rate limiting and fraud tooling live on payment endpoints
- [ ] Webhook signature verification implemented (an unverified billing
      webhook is an authorisation bypass, not just a bug)
