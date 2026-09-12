# High-risk categories — where a generated document is not good enough

This file exists to draw one line clearly: **some products cannot be made safe
with a template, and the responsible thing is to say so early.**

Naming this is not a cop-out. A person who is told "this part needs a lawyer,
here is specifically why, here is what to ask them" is better served than one
handed a polished document that creates false comfort about an exposure they
didn't know they had.

## How to deliver this

Plainly, once, early, and without drama. Something like:

> Most of this you can handle yourself and I've drafted it. One part I can't:
> you're storing [X], which falls under [regime]. That carries [specific
> consequence]. Here's what to ask a lawyer, and it should be a short
> conversation.

Then continue with everything else. Do not let the escalation stall the rest of
the work, and do not frighten someone out of shipping a product that is
basically fine apart from one field.

## The categories

### Children (under 13, and under 16 in several places)

**Why it's different.** Its own regime, its own penalties, and an unusually
active enforcement appetite. In the US, COPPA requires verifiable parental
consent before collecting personal data from under-13s, with specific rules on
what "verifiable" means. In the EU and UK, design codes apply based on whether
a service is *likely to be accessed by* children, not on whether you aimed at
them — so "we didn't target kids" is not the defence people assume.

**Triggers:** an age field suggesting minors; subject matter that appeals to
children; a school or education customer; any social feature with no age gate.

**What changes:** parental consent mechanics, default-private settings, no
behavioural advertising, data minimisation held to a higher standard, profiling
restrictions, and often a children's privacy notice in language a child can
read.

**Escalate if:** the service is aimed at children at all, or a general-audience
service has a plausible under-13 population and any social or advertising
surface.

### Health data

**Why it's different.** Special-category data under GDPR Art. 9 (needs an
Art. 9 condition, not just a lawful basis) and sensitive under Australian and
most US state regimes.

**The most common misunderstanding:** HIPAA does *not* apply to most health
apps. It applies to covered entities — providers, plans, clearinghouses — and
their business associates. A direct-to-consumer symptom tracker is usually
neither. This is not good news: it means the data is intensely sensitive,
several state and non-US regimes cover it, the FTC's Health Breach Notification
Rule can apply to consumer health apps, and the HIPAA framework people assume
is protecting them isn't in play.

**Triggers:** fields like `diagnosis`, `symptom`, `medication`, `patient`; a
fitness or mental-health feature; anything inferring a health condition — and
inference counts, so a period tracker or a mood log is health data.

**Escalate if:** you store anything that reveals a health condition, you
integrate with a provider or an insurer, or an AI feature produces anything
that reads as medical advice.

### Financial services, lending, insurance

**Why it's different.** Licensing regimes. This is the category where the issue
may not be *how* you operate but *whether you are permitted to at all* without
authorisation.

**Triggers:** lending, credit decisions, brokering, money transmission, holding
customer funds, insurance distribution, investment advice, crypto custody or
exchange.

**What changes:** licensing or registration, capital and conduct requirements,
GLBA-style privacy rules in the US, anti-money-laundering and KYC obligations,
and — for anything that scores or decides — the automated-decision rules under
GDPR Art. 22 and the EU AI Act's high-risk tier.

**Escalate:** always, and before launch, not after. Unauthorised activity in
this space is not a documentation problem.

### Biometric identifiers

**Why it's different.** Special-category data in the EU; a specific statutory
regime in several US states, of which Illinois BIPA is the significant one
because it carries a **private right of action** and statutory damages
calculated per violation. That combination has produced very large settlements
from companies that did not think of themselves as biometric businesses.

**Triggers — broader than people expect:** face detection or matching
(including "is there a face in this photo"), fingerprint or face unlock,
**voiceprints** (so: speech-to-text and voice authentication), gait, iris, and
some behavioural biometrics.

**What changes:** written notice and written consent *before* collection, a
published retention and destruction schedule, and prohibitions on selling or
profiting from the data.

**Escalate if:** you process faces or voices at all, in any state with a
biometric statute. The speech-to-text case catches AI products constantly.

### Employment and hiring decisions

**Why it's different.** Automated decision-making rules, anti-discrimination
law, and a growing set of jurisdiction-specific AI-in-hiring rules — some
requiring independent bias audits and candidate notification before use.

**Triggers:** CV screening, ranking or scoring candidates, interview analysis,
productivity monitoring, scheduling systems that affect pay.

**What changes:** bias auditing, candidate notice, human review of adverse
decisions, explainability, and — under the EU AI Act — likely classification as
a high-risk system.

**Escalate:** if the product influences who gets hired, promoted, disciplined
or fired. Including if a human "makes the final call" on a ranked list.

### Precise location

**Why it's different.** Sensitive data under several US state laws, and the
subject of specific enforcement over location-data brokerage. Continuous
location history reveals home, workplace, religious attendance, health visits
and relationships.

**Triggers:** `latitude`/`longitude` fields, background location, geofencing,
any location history rather than a single current position.

**What changes:** explicit consent, strict purpose limitation, short retention,
and a very high bar before sharing with anyone. Never sell it.

### Government identifiers and immigration status

Social Security numbers, passport and national ID numbers, driving licences,
tax identifiers. Breach notification obligations are strictest for these, and
the downstream harm to the individual is identity theft.

**The right first question is whether you need it at all.** Most products
collecting a national ID number could verify what they actually need some other
way. If the answer is yes — KYC, age verification, right-to-work — use a
specialist provider and avoid storing the number yourself.

### Sexual orientation, religion, ethnicity, political opinion, union membership

Special-category data under GDPR Art. 9 and sensitive elsewhere. Also: often
**inferred** rather than collected. A dating app's matching preferences, a
community feature's group memberships, a content recommender's inferred
interests can all constitute this data without a field ever being named for it.

### Criminal records, and safety-critical contexts

Background checks, offender data, and anything where being wrong causes
physical harm — medical device adjacency, vehicle control, safety alerting.
Different failure mode from the rest of this list: the exposure is negligence
and product liability, not just privacy.

## What to hand the user when you escalate

Not "go see a lawyer". Give them:

1. **The specific trigger.** "You store voice recordings, and speech is a
   biometric identifier under Illinois BIPA."
2. **The specific consequence.** "BIPA has a private right of action with
   per-violation statutory damages — it's the one plaintiffs' firms actually
   file on."
3. **The questions to ask.** "Do we need written consent before recording?
   What does our retention schedule have to say, and where do we publish it?
   Does our current signup flow satisfy the notice requirement?"
4. **What they can do meanwhile.** Usually: stop collecting it, collect less of
   it, or gate the feature by region until the answer is in.

That last one matters. There is nearly always an interim step that reduces
exposure while they wait for advice, and offering it is the difference between
useful and alarming.
