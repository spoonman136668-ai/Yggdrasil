TITLE: DG-1A-AR-H18 — Provenance-Diverse Context Fingerprint Confidence Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SOURCE-DIVERSITY RESULT + HARD GLOBAL-COMMON-MODE CONTEXT NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh17-context-conditioned-delayed-credit-audit.ice

PURPOSE
H17 showed that delayed structural credit improves substantially when it retains a compact nomination-time context fingerprint.

H17's current limit is context identifiability.

H18 asks:

Can several partially independent local context cues produce a more reliable context fingerprint,
and can provenance prevent relay copies from creating false confidence?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil has these context sources;
- freeze a context-family representation;
- establish permanent sensor IDs;
- solve all-source common-mode context corruption;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BASE DELAYED-CREDIT TASK
Same A -> B -> A trust task as H17.

1500 opportunities.

Context transitions:
500
and
1000.

Delayed structural confirmation:

base delay 80
+
uniform jitter +/-60.

Context-dependent useful nomination mechanism:

in A:
H0 0.90
H1 0.20.

in B:
H0 0.10
H1 0.85.

Context-conditioned trust still learns from:
the stored nomination-time fingerprint.

CONTEXT SOURCE FAMILIES
Primary toy uses three independent source families:

F0
F1
F2.

Per-family context observation noise SD:

0.80.

F0 also has:

6 relay copies.

Relay noise SD:
0.05.

Thus raw message count is:

8 cues total:

6 copies of F0
+
F1
+
F2.

PRIMARY FAMILY-SPECIFIC CORRUPTION
F0 independently flips the apparent context on:

15%

of opportunities.

F1 and F2 remain unaffected except for ordinary measurement noise.

This creates a discriminating provenance test.

POLICIES

SINGLE SOURCE
Use F0 alone.

RAW RELAY AVERAGE
Average all 8 received cue messages.

This treats six relays of F0 as six independent context votes.

PROVENANCE-AWARE FAMILY AVERAGE
Collapse F0 relays into one family estimate.

Then average:

F0
F1
F2

with equal family authority.

PROVENANCE + AGREEMENT CONFIDENCE
Use family-level average,
but estimate context confidence from independent-family sign agreement.

If confidence is below:
0.60

fall back to context-independent global trust
and do not train the context-conditioned map from that low-confidence fingerprint.

FOUR-INDEPENDENT-SOURCE CONTROL
Separate diagnostic using four independent context sources.

This is an upper comparison for source diversity,
not the same message topology as the relay case.

PRIMARY CONFIRMATION
100 matched delayed-credit streams per policy.

PRIMARY RESULTS

SINGLE F0

late A1 correct nomination selection:
0.9470

early B:
0.1949

late B:
0.9443

early returning A:
0.1051

late A2:
0.8775

wrong context-fingerprint sign:
22.37%.

total regret:
300.73.

RAW RELAY AVERAGE

A1:
0.9470

B early:
0.2675

B late:
0.9368

A2 early:
0.2687

A2 late:
0.8900

wrong fingerprint:
16.35%.

regret:
255.65.

INTERPRETATION
Averaging relay copies reduces ordinary noise somewhat,
but still gives the corrupted F0 family six times the voting weight of either independent source.

Copies do not create equivalent independent context evidence.

PROVENANCE-AWARE FAMILY AVERAGE

A1:
0.9471

B early:
0.4274

B late:
0.9422

A2 early:
0.7751

A2 late:
0.9271

wrong fingerprint:
4.77%.

regret:
157.40.

PRIMARY POSITIVE
Collapsing relay copies to source-family authority reduces context-sign error from:

16.35%

to:

4.77%

and substantially improves context-conditioned delayed credit.

Thus:

COPIES ARE NOT REDUNDANCY

also applies to:
CONTEXT FINGERPRINTS USED FOR CREDIT ROUTING.

PROVENANCE + AGREEMENT CONFIDENCE

A1:
0.9464

B early:
0.5675

B late:
0.9481

A2 early:
0.6882

A2 late:
0.9450

wrong fingerprint:
4.78%.

low-confidence fallback invoked:
37.75%

of opportunities.

regret:
139.88.

CONFIDENCE POSITIVE
Independent-family disagreement is useful evidence that the context fingerprint should not receive full routing authority.

The confidence gate improves total regret relative to provenance-only averaging.

CONFIDENCE NEGATIVE
Fallback to global trust is not universally free.

A-return early accuracy falls from:

0.7751

with provenance-only conditioning

to:

0.6882

with the tested confidence fallback.

Reason:
global trust can itself carry context-transition hangover.

Therefore:

LOW CONTEXT CONFIDENCE
does not automatically imply
GLOBAL TRUST IS CORRECT.

The safe fallback policy remains a separate design problem.

FOUR INDEPENDENT SOURCES
Diagnostic control.

A1:
0.9487

B early:
0.5863

B late:
0.9463

A2 early:
0.9246

A2 late:
0.9482

wrong fingerprint:
0.62%.

regret:
112.12.

This shows the value of genuinely independent context evidence.

It should not be read as a requirement for exactly four sources.

PRIMARY SOURCE-DIVERSITY RULE
Context-fingerprint confidence should depend on:

EFFECTIVE INDEPENDENT SOURCE FAMILIES

not:

RAW MESSAGE COUNT.

This repeats the same architecture principle already observed in:
- context consensus;
- causal controls;
- structural-growth evidence.

GLOBAL COMMON-MODE STRESS
Family-specific provenance cannot solve a context failure shared by all source families.

A separate stress removes F0-specific corruption
and instead flips the apparent context coherently across every source family.

30 matched streams per final stress point.

GLOBAL FLIP PROBABILITY = 0.10

PROVENANCE FAMILY AVERAGE:

wrong context:
11.31%.

B early correct nomination:
0.2776

A-return early:
0.2802

regret:
252.21.

PROVENANCE + CONFIDENCE:

wrong context:
11.31%.

B early:
0.2600

A-return early:
0.4596

regret:
230.56.

FOUR INDEPENDENT SOURCE CONTROL:

wrong context:
10.81%.

B early:
0.2918

A-return early:
0.3471

regret:
244.07.

GLOBAL FLIP = 0.20

PROVENANCE:

wrong:
21.06%.

A-return early:
0.0873

regret:
306.53.

PROVENANCE + CONFIDENCE:

wrong:
21.01%.

A-return:
0.0880

regret:
305.84.

FOUR INDEPENDENT:

wrong:
20.57%.

A-return:
0.0922

regret:
305.57.

GLOBAL FLIP = 0.30

PROVENANCE:

wrong:
30.52%.

A-return:
0.0647

regret:
328.41.

PROVENANCE + CONFIDENCE:

wrong:
30.46%.

A-return:
0.0656

regret:
330.99.

FOUR INDEPENDENT:

wrong:
30.36%.

A-return:
0.0607

regret:
320.13.

HARD NEGATIVE
When every context source shares the same coherent context error:

SOURCE DIVERSITY DOES NOT CREATE INDEPENDENCE.

All families can agree
and all families can be wrong.

Family-level disagreement confidence is especially limited here,
because the corrupt sources agree with one another.

Thus:

CONSENSUS CANNOT MANUFACTURE CONTEXT IDENTIFIABILITY.

RELATION TO H10 / H11
H10:
cross-family structural evidence rejects family-specific shared noise
but fails on global common-mode artifacts.

H11:
temporal separation can reject faster global artifacts,
but fails when artifact and signal share timescale.

H18 reaches the analogous point for delayed-credit context:

provenance diversity rejects family-local corruption,
but globally coherent context error remains under-identified.

CURRENT CONTEXT-FINGERPRINT OBJECT
A context fingerprint used for delayed credit should conceptually contain:

SOURCE / FAMILY PROVENANCE

+

EFFECTIVE INDEPENDENT SOURCE COUNT

+

FAMILY-LEVEL CUE ESTIMATES

+

INTER-SOURCE AGREEMENT

+

CONTEXT CONFIDENCE

+

FRESHNESS / AGE.

Raw repeated messages should not increase context authority by themselves.

GENERAL PRINCIPLE
Yggdrasil should preserve the distinction:

MORE OBSERVATIONS

vs

MORE INDEPENDENT INFORMATION.

This distinction now affects:
- context state;
- causal control;
- structural memory;
- delayed credit routing.

DECISION
AR-H18 is POSITIVE for provenance-diverse context aggregation,
with a HARD NEGATIVE for global common-mode context corruption.

Supported synthetically:

- relay copies can overweight one corrupted context source;
- family-level provenance sharply improves context fingerprint accuracy;
- family disagreement provides useful context-confidence information;
- independent source diversity improves delayed-credit routing;
- globally coherent context corruption defeats source-family provenance and ordinary agreement confidence.

Not demonstrated:

- real Yggdrasil context-source families;
- real compact provenance sketch for context credit;
- optimal context-confidence fallback;
- global common-mode context detection;
- distributed fingerprint fusion under cell birth/death.

NEXT CLEAN QUESTION
AR-H19 — TEMPORAL CONTINUITY / CHANGE-POINT CONFIDENCE FOR CONTEXT FINGERPRINTS

Question:

Can short-lived globally coherent context flips be rejected using temporal continuity
without suppressing a genuine context transition?

Compare:

A.
instantaneous provenance-aware context fingerprint;

B.
slow temporal smoothing;

C.
change-point / persistence gate;

D.
brief global artifact;

E.
real sustained context change;

F.
persistent common-mode false context.

Desired:

brief coherent artifact
->
lower context confidence / hold routing.

real persistent transition
->
adapt after bounded evidence.

persistent false context with the same temporal statistics as a real transition
->
remain an explicit identifiability limit
rather than silently treated as truth.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_streams = 100
context_source_families = 3
f0_relay_copies = 6
primary_family_context_noise_sd = 0.80
primary_family0_flip_probability = 0.15
global_common_mode_stress_streams = 30
confirmation_delay_base = 80
confirmation_delay_jitter = 60
