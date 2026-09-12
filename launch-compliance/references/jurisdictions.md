# Jurisdictions — the atlas

`privacy-law.md` covers the EU/UK, the US and Australia in depth, because those
are where most of this skill's users and their users are. This file is
everything else.

## How to read this file

**Every section carries a status line.** That is deliberate, and it is the most
important thing on the page:

- **`Detailed`** — the section covers the mechanics well enough to act on,
  subject to the usual verification of numbers.
- **`Structural`** — the shape of the regime is right: who is in scope, what
  kind of obligations exist, what the regulator is called. Specific
  requirements, thresholds and deadlines need looking up before you state them.

Treat a `Structural` section as a map, not a manual. Use it to tell someone
*that* they have an obligation and *what to search for*, never to tell them the
detail. A confidently wrong specific is worse than an acknowledged gap — and
this file is the place in the skill where that failure is easiest to make,
because it reads as authoritative whatever its status line says.

**Nothing here has been reviewed by a lawyer.** Upgrading a section from
`Structural` to `Detailed` is the single most valuable contribution anyone can
make to this project. See `CONTRIBUTING.md`.

## Quick reference

| Where | Regime | Extraterritorial? | The thing people miss |
| --- | --- | --- | --- |
| Canada | PIPEDA + provincial | Yes, via real and substantial connection | Quebec's Law 25 is much stricter than federal, and CASL is stricter than almost anyone's anti-spam rules |
| Brazil | LGPD | Yes | More lawful bases than GDPR, and a DPO requirement that catches small teams |
| India | DPDP Act | Yes | Children are under **18**, with verifiable parental consent and a ban on tracking them |
| Japan | APPI | Yes | Cross-border transfer needs consent *with specific information about the destination* |
| South Korea | PIPA | Yes | Consent must be granular per purpose, and separately for sensitive data |
| China | PIPL | Yes | Separate consent for transfers, plus localisation and a local representative |
| Switzerland | revFADP | Yes | Penalties fall on *individuals*, not the company |
| Singapore | PDPA | Yes | Mandatory DPO, and the Do Not Call registry |
| New Zealand | Privacy Act 2020 | Yes | IPP 12 makes you accountable for overseas recipients |
| South Africa | POPIA | Yes | Information Officer must be registered |
| Nigeria | NDPA | Yes | Registration if you are a controller "of major importance" |

---

## Canada

**Status: Structural.** The federal/provincial split and Quebec's divergence
are right; specifics need checking, and federal reform has been in and out of
Parliament for years.

**In scope:** PIPEDA applies to organisations collecting, using or disclosing
personal information in the course of **commercial activity**. It reaches
foreign organisations with a real and substantial connection to Canada.
Alberta, British Columbia and Quebec have their own private-sector laws deemed
substantially similar, which displace PIPEDA for intra-provincial activity.

**Regulator:** the Office of the Privacy Commissioner of Canada (OPC),
alongside provincial commissioners.

**What differs from GDPR:** PIPEDA is built around **consent** and ten fair
information principles rather than a menu of lawful bases. Consent must be
meaningful — the OPC's guidance on what that requires is unusually practical
and worth reading directly. There is an accountability principle that requires
a designated individual responsible for compliance.

**Quebec's Law 25 is the one to watch.** It phased in over several years and is
materially stricter than the federal baseline:

- a designated Privacy Officer, named publicly (by default, the most senior
  person in the organisation)
- privacy impact assessments for projects involving personal information
- mandatory confidentiality-by-default settings
- transparency about automated decision-making, with a right to be informed
- a data portability right
- breach reporting, with a register of incidents
- meaningful penalties, including a private right of action

It applies to organisations doing business in Quebec regardless of where they
sit. A product with Montreal users is in scope.

**Breach:** under PIPEDA, report to the OPC and notify individuals where there
is a **real risk of significant harm**, and keep records of *all* breaches —
including ones you decide not to report — for a set period. The record-keeping
obligation is the one people miss.

**CASL — Canada's anti-spam law — deserves its own warning.** It is stricter
than the US CAN-SPAM and than most of Europe: it requires consent (express or
narrowly-defined implied) before sending commercial electronic messages,
prescribes identification and unsubscribe requirements, and carries very large
maximum penalties. "We bought a list" is not a strategy that survives contact
with CASL.

**What to search for:** "OPC meaningful consent guidelines", "Quebec Law 25
obligations", "CASL express consent requirements", and the current status of
federal reform.

---

## Brazil

**Status: Structural.** GDPR-shaped, so the instincts transfer; ANPD's
enforcement posture and the sanction specifics need checking.

**In scope:** the LGPD applies to processing carried out in Brazil, processing
aimed at offering goods or services to people in Brazil, or processing of data
collected in Brazil — the familiar extraterritorial pattern.

**Regulator:** the Autoridade Nacional de Proteção de Dados (ANPD).

**What differs from GDPR:** the structure is close enough that a GDPR-compliant
product is most of the way there, with some real differences:

- **Ten legal bases**, not six. The extras include credit protection and the
  regular exercise of rights in legal proceedings, and there is a separate list
  for sensitive data.
- **A data protection officer (*encarregado*) is required** more broadly than
  GDPR's narrow DPO triggers. For a small team this usually means naming
  someone and publishing the contact, not hiring.
- Data subject rights track GDPR's closely, with the addition of a right to
  information about public and private entities with which data has been shared.

**Breach:** notify the ANPD and affected data subjects within a reasonable
period where there is risk or relevant damage. The definition of "reasonable"
has been the subject of ANPD guidance — check it rather than assuming 72 hours.

**Sanctions:** administrative fines calculated on Brazilian revenue with a
per-infraction cap, plus publicising the violation, blocking and deletion of
data. **Verify the current figures.**

**What to search for:** "ANPD sanções LGPD", "LGPD encarregado obrigatório",
"ANPD incidente de segurança prazo".

---

## India

**Status: Structural, and unusually volatile.** The Digital Personal Data
Protection Act was passed in 2023 and its implementing rules and commencement
have been staged. **Check what is actually in force before advising anything.**

**In scope:** processing of digital personal data within India, and processing
outside India where it relates to offering goods or services to people in
India.

**Terminology to expect:** Data Principal (the individual), Data Fiduciary (the
controller), Data Processor, and Consent Manager — a registered intermediary
through which people can give and withdraw consent, which has no direct
equivalent elsewhere.

**What differs, and matters:**

- **Consent-and-notice centric**, with a defined set of "legitimate uses"
  operating as the alternative to consent rather than a broad
  legitimate-interests balancing test.
- **Notice must be itemised**, and available in English plus the scheduled
  Indian languages.
- **Children are under 18** — a much higher bar than COPPA's 13 or the GDPR's
  13-to-16 range. Processing children's data requires **verifiable parental
  consent**, and **behavioural advertising and tracking directed at children
  are prohibited**. For a general-audience consumer product with Indian users,
  this is the provision most likely to cause a redesign.
- **Significant Data Fiduciary** designation brings extra duties — a DPO based
  in India, independent audits, and data protection impact assessments.
- Penalties are set per-breach-type with high ceilings, and are levied by the
  Data Protection Board.

**What to search for:** "DPDP Rules notified", "DPDP Act commencement",
"Significant Data Fiduciary criteria", "DPDP verifiable parental consent".

---

## Japan

**Status: Structural.** The transfer rules and the "personally related
information" concept are the substantive points; details need checking.

**In scope:** the Act on the Protection of Personal Information (APPI) applies
to businesses handling personal information, including foreign businesses
handling the personal information of people in Japan in connection with
supplying goods or services.

**Regulator:** the Personal Information Protection Commission (PPC).

**What differs:**

- **Purpose specification is strict.** You state the purpose of use, and using
  data beyond it generally needs fresh consent.
- **Third-party provision requires consent** by default, with an opt-out
  mechanism available for some cases subject to notification to the PPC.
- **Cross-border transfers** need one of: consent that is informed by **specific
  information about the destination country's regime and the recipient's
  protections**, a recipient who meets Japanese standards under a contract or
  binding rules, or transfer to a country designated as adequate. That
  information-rich consent requirement is stricter than it first looks, and
  a generic "we may transfer your data overseas" line does not meet it.
- **"Personally related information"** covers identifiers such as cookie data
  that are not personal in your hands but become personal when combined by the
  recipient. Providing it to a third party who can re-identify triggers consent
  obligations — this catches adtech and analytics arrangements specifically.
- **Breach reporting to the PPC is mandatory**, with a preliminary and a final
  report, plus notification to affected individuals.

Japan and the EU have a mutual adequacy arrangement, which simplifies flows in
both directions.

**What to search for:** "APPI cross-border transfer consent requirements",
"personally related information APPI", "PPC breach report deadline".

---

## South Korea

**Status: Structural.** PIPA is among the strictest regimes globally and has an
active enforcement record against foreign companies; treat this section as a
prompt to get local advice rather than as guidance.

**In scope:** the Personal Information Protection Act applies broadly, with
extraterritorial reach to processing affecting people in Korea.

**Regulator:** the Personal Information Protection Commission (PIPC), which has
issued substantial fines to global technology companies.

**What differs, and it differs a lot:**

- **Consent is granular and itemised.** Separate consent per purpose, separate
  consent for sensitive information and for unique identifiers, separate
  consent for marketing, and separate consent for third-party provision. A
  single "I agree to the privacy policy" checkbox does not work here.
- **Cross-border transfers** require their own consent (or another specified
  ground), with disclosure of the recipient, the country, the purpose and the
  retention period.
- **Unique identifiers**, particularly the resident registration number, are
  subject to heavy restrictions — collection is prohibited absent a specific
  legal basis.
- **Destruction obligations** when the retention period ends or the purpose is
  achieved are explicit and enforced.
- Penalties can be calculated on turnover, and there are criminal provisions.

If a product is deliberately targeting Korea, this is a local-counsel
conversation, not a template conversation.

**What to search for:** "PIPA separate consent requirements", "PIPC
cross-border transfer", "PIPA destruction obligation".

---

## China

**Status: Structural.** PIPL differs enough from everything else here that a
product genuinely entering China needs specialist advice, not a reference file.

**In scope:** PIPL applies to processing within China, and to processing
outside China aimed at providing products or services to individuals in China
or analysing their behaviour.

**What differs materially:**

- **Separate consent** is required for several categories, including sensitive
  personal information, cross-border transfers, and provision to third parties
  — "separate" meaning a distinct, specific act, not part of a bundled
  agreement.
- **Cross-border transfer** requires one of a security assessment by the
  regulator, a certification, or the standard contractual clauses in the
  Chinese form, with thresholds determining which applies.
- **Data localisation** applies to critical information infrastructure
  operators and to processors above volume thresholds.
- **Offshore processors must establish a local entity or designate a
  representative** in China and file their details.

**What to search for:** "PIPL cross-border transfer thresholds", "China SCCs
filing", "PIPL separate consent".

---

## Switzerland

**Status: Structural.** Close to GDPR in shape; the penalty model is the
notable difference.

The revised Federal Act on Data Protection (revFADP) took effect in September
2023 and aligns substantially with GDPR: transparency, records of processing
(with a small-organisation exemption), data protection impact assessments,
privacy by design and default, and breach notification to the Federal Data
Protection and Information Commissioner (FDPIC) as soon as possible.

**The difference worth knowing:** penalties are criminal fines levied on
**responsible individuals** rather than administrative fines on the company,
with a ceiling in the hundreds of thousands of Swiss francs. It changes who
in an organisation cares about compliance.

Switzerland benefits from and grants adequacy arrangements; check current
status for flows in each direction.

---

## Singapore

**Status: Structural.**

The Personal Data Protection Act (PDPA) covers consent, purpose limitation and
notification, with an accountability framework layered on by amendment.

Points that catch people:

- **A Data Protection Officer must be appointed and their business contact
  published.** This applies regardless of size.
- **Mandatory breach notification** to the PDPC and affected individuals where
  a breach results in significant harm or is of significant scale. **The
  numeric threshold for "significant scale" should be verified.**
- **The Do Not Call registry** governs marketing calls and texts to Singapore
  numbers and is separate from the consent rules for data.

---

## New Zealand

**Status: Structural.**

The Privacy Act 2020 works through Information Privacy Principles rather than
lawful bases. Two things matter most:

- **Notifiable privacy breaches** must be reported to the Privacy Commissioner
  and affected individuals where serious harm is likely.
- **IPP 12** restricts disclosure to overseas recipients: you must believe on
  reasonable grounds that the recipient is subject to comparable safeguards.
  In practice this is the same exercise as the Australian APP 8 analysis, and
  the same subprocessor list answers both.

---

## South Africa

**Status: Structural.**

POPIA sets eight conditions for lawful processing, supervised by the
Information Regulator.

The distinctive operational requirement is the **Information Officer**: every
responsible party has one by default (the head of the organisation), they must
be **registered with the Regulator**, and they carry defined duties. Failing to
register is a common and easily avoided gap.

Cross-border transfer rules broadly follow the adequacy-or-safeguards pattern.

---

## Nigeria

**Status: Structural.**

The Nigeria Data Protection Act 2023 established the Nigeria Data Protection
Commission and replaced the earlier regulation.

The notable requirement is **registration of "data controllers and processors
of major importance"** — determined by sector and by the volume of data
subjects handled — plus the appointment of a data protection officer for those
entities. **Check the current threshold and registration process.**

---

## Others worth naming

Each of these has a comprehensive regime that follows the
consent/rights/transfer pattern closely enough that a GDPR-shaped product is
most of the way there, and different enough that you should say so rather than
assume:

- **Thailand** — PDPA, with consent requirements and a data protection
  committee; heavily GDPR-influenced.
- **Indonesia** — the Personal Data Protection Law, phased in with a
  transition period; check what is in force.
- **Vietnam** — Decree 13 on personal data protection, with notable
  registration and impact-assessment filing requirements.
- **Saudi Arabia** — the Personal Data Protection Law, administered by SDAIA,
  with registration and transfer rules.
- **UAE** — a federal law plus separate regimes in the DIFC and ADGM free
  zones, which are closer to GDPR than the federal law is. Which applies
  depends on where the entity sits.
- **Israel** — the Privacy Protection Law with significant amendments
  increasing enforcement powers; holds EU adequacy, which has been subject to
  periodic review.
- **Turkey** — KVKK, GDPR-influenced, with its own registration (VERBIS) and
  transfer mechanics.

## Adding a jurisdiction

If you know one of these properly, a full section is the most valuable thing
you can contribute. Follow the structure of the Canada or Japan sections:

1. **In scope** — who it catches, and on what basis
2. **Regulator** — the name people should search for
3. **What differs** — from GDPR, since that is the reader's mental model.
   Don't restate what is the same.
4. **The thing people miss** — the provision that catches products out
5. **Breach** — who to tell, how fast
6. **What to search for** — the exact phrases that find current guidance
7. **A status line** — and be honest in it

Change the status line to `Detailed` only if you have worked with the regime
and checked the current text. Leaving it as `Structural` is not a failure; it
is the honest default, and it tells the reader exactly how much weight to put
on what they just read.
