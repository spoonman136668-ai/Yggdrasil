TITLE: DG-1A-AR-C4 — Dynamic Sensor Lineage / Independence Maturation Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX PROVENANCE-LIFECYCLE AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arc3-provenance-compression-audit.ice

PURPOSE
Test how provenance should behave when sensor function is dynamic.

Question:
When a sensing cell:
- divides;
- dies;
- is replaced;
- or another cell adopts sensing function,

when should the new physical cell count as a NEW independent source of evidence?

BOUNDARY
This is synthetic.

It does not:
- prescribe literal cell lineage IDs;
- reserve sensor roles;
- modify or execute STAB-18-R1;
- establish a biological sensing mechanism.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX
ANALYTIC where explicitly stated.

CORE DISTINCTION
PHYSICAL CELL IDENTITY
is not the same as
CAUSAL EVIDENCE INDEPENDENCE.

Two different cells may share:
- the same transduction path;
- the same local environmental disturbance;
- the same inherited latent state;
- the same failure mode.

Therefore:
new cell
!=
new independent sensor.

PART A — DAUGHTER-SENSOR QUORUM

Binary true context.

Per-sensor wrong probability:
p = 0.10

Two daughter sensors originate from one prior sensor lineage.

Their errors follow a common-mode mixture:

with probability q:
both share the same correct/wrong event.

with probability 1-q:
their errors are independent.

If both daughters are given DISTINCT provenance signatures immediately,
two matching daughter reports satisfy the two-source quorum.

ANALYTIC WRONG-QUORUM PROBABILITY

P(wrong quorum)
=
q * p
+
(1-q) * p^2

RESULTS

q = 0.00
1.00%

q = 0.25
3.25%

q = 0.50
5.50%

q = 0.75
7.75%

q = 0.90
9.10%

q = 1.00
10.00%

PRIMARY NEGATIVE
Physical duplication can manufacture apparent redundancy while preserving the original common-mode failure.

This exactly violates the standing rule:

COPIES ARE NOT REDUNDANCY.

INHERITED PROVENANCE CONTROL
If both daughters inherit the SAME source-epoch provenance signature:

daughter/daughter agreement alone:
cannot satisfy two-source quorum.

Wrong two-source quorum from the lineage alone:
0%.

This is fail-safe,
but may undercount evidence after daughters genuinely become independent.

Therefore:
permanent shared lineage provenance is also not sufficient.

PART B — INDEPENDENCE MATURATION

Hypothesis:
a newly created sensor branch should retain inherited provenance until its sensing residuals become sufficiently decorrelated from the parent/source family.

Synthetic analog residual model:

daughter A residual:
unit Gaussian.

daughter B residual:
correlated Gaussian with true correlation rho.

Observation windows:
8
16
32
64 samples.

Simple exploratory independence test:

declare new source independence if:

absolute sample correlation < 0.5.

This is an exploratory discriminating test,
not a frozen Yggdrasil threshold.

TRIALS
50,000 windows per condition.

DECLARED-INDEPENDENT RATE

true rho = 0.90

W=8:
1.04%

W=16:
0.028%

W=32:
approximately 0%

W=64:
approximately 0%

true rho = 0.70

W=8:
18.41%

W=16:
10.49%

W=32:
3.65%

W=64:
0.56%

true rho = 0.60

W=8:
31.97%

W=16:
27.25%

W=32:
19.71%

W=64:
11.96%

true rho = 0.50

W=8:
45.38%

W=16:
46.83%

W=32:
48.38%

W=64:
48.91%

true rho = 0.40

W=8:
57.42%

W=16:
65.91%

W=32:
73.89%

W=64:
83.00%

true rho = 0.20

W=8:
73.98%

W=16:
88.88%

W=32:
96.76%

W=64:
99.65%

PRIMARY POSITIVE
A short local residual-history test can strongly distinguish:
highly common-mode
from
weakly correlated

sensor branches.

At W=16:

rho=0.90:
false independence ~0.03%

rho=0.20:
independence recognized ~88.9%.

This suggests a practical concept:

INDEPENDENCE MUST MATURE.

NEW SENSOR-LINEAGE STATE MACHINE

NEW / ROLE-SWITCHED SENSOR
inherits source-family provenance.

During maturation:
- collect local sensing residual history;
- compare against source-family residual;
- remain one provenance family while evidence is strongly correlated.

If decorrelation evidence becomes strong enough:
mint a new per-epoch source signature.

If confidence is insufficient:
remain conservatively grouped.

This makes uncertainty fail toward:
UNDERCOUNTING

rather than:
FALSE INDEPENDENCE.

SENSOR DEATH
If one physical sensor dies:
its old source signature may remain in relayed evidence for the current epoch,
but no new evidence should be generated from the dead source.

A replacement sensor should not automatically reuse the dead source's identity forever.

It enters:
maturation.

ROLE SWITCHING
If an unrelated cell begins sensing:

physical unrelatedness alone is insufficient.

If it uses the same environmental transduction path and common local disturbance,
its failures may still be strongly correlated.

Therefore role adoption should also enter:
independence maturation.

CELL DIVISION
Daughters should initially share:
source-family provenance.

Do not mint independent signatures merely because:
cell count increased.

COMPONENT RECONNECTION
When previously separated components reconnect:

epoch-ordered provenance sets can merge idempotently.

If the same source lineage propagated into both components:
matching signatures deduplicate.

If separately matured independent sources exist:
their distinct signatures can satisfy quorum.

This is a favorable property of epoch-local stable provenance.

IMPORTANT LIMITATION
Sample correlation is only a synthetic proxy for causal independence.

Low observed correlation does not prove:
independent failure mechanisms.

Two sensors can have:
low ordinary covariance
but
share rare catastrophic failure.

Therefore a real system should prefer:
multiple forms of independence evidence.

Candidates:
- residual covariance;
- response to controlled microperturbations;
- spatially different transduction pathways;
- lineage separation;
- error disagreement under historical disturbances.

Do not use one correlation threshold as a universal independence certificate.

CROSS-DOMAIN CONNECTION
This result links:

ROLE INHERITANCE
with
SENSOR PROVENANCE.

A daughter can inherit:
- state;
- sensitivity;
- function;
- provenance family.

But:
INDEPENDENCE
should not be inherited or minted blindly.

It is an evidence property that can change over time.

MICRO-GENOME IMPLICATION
Future heritable micro-genome variables may include:
- sensing sensitivity;
- role responsiveness;

but source provenance should remain:
ephemeral / evidence-scoped

rather than:
a permanent genetic identity.

This prevents:
lineage identity
from being mistaken for
causal evidence independence.

DECISION
Carry forward:

SOURCE FAMILY
+
INDEPENDENCE MATURATION
+
PER-EPOCH EPHEMERAL SIGNATURE.

Reject:

new physical cell
->
automatic new independent provenance.

NEXT
AR-H1 — HERITABLE MICRO-GENOME TIMESCALE AUDIT

The provenance result makes the inheritance question sharper:

which adaptive parameters should daughters inherit,
how much mutation is safe,
and when does heritable specialization improve adaptation versus freeze common-mode failure into a lineage?

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX_AND_ANALYTIC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
correlation_trials_per_condition = 50000
