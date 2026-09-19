TITLE: DG-1A-AR-H41 — Functional Regeneration Canary for Global Common-Mode Template Failure
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE FUNCTIONAL-PROMOTION RESULT + CAUSAL-CONTROL REQUIREMENT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh40-canary-provenance-correlated-validation-audit.ice

PURPOSE
H40 established that provenance-diverse observational canaries can reject single-family corruption,
but all observational canaries fail when they share the same global common-mode bias as the update stream.

H41 asks:

WHEN UPDATE EVIDENCE AND EVERY OBSERVATIONAL CANARY AGREE ON THE SAME TEMPLATE CHANGE,
CAN A SMALL FUNCTIONAL REGENERATION CHALLENGE DETERMINE WHETHER THAT CHANGE ACTUALLY IMPROVES REGENERATED FUNCTION?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil has a target-free functional regeneration signal;
- freeze a challenge threshold;
- freeze a challenge budget;
- establish final causal-control machinery;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FOCUSED SHARED-TEMPLATE STATE
Latent family coefficient dimensions:
3.

Current live family center:
[0,0,0].

Candidate shared-template center:
[0.8,0,0].

The candidate is assumed to have already passed:
- update-stream evidence;
- observational fit;
- temporal persistence;
- all observational canary families.

This deliberately recreates H40's hard global-common-mode failure.

TWO HIDDEN WORLDS

GLOBAL COMMON-MODE POISON

True family center remains:
[0,0,0].

But:
- update stream;
- observational canaries;

are all biased toward:
[0.8,0,0].

LEGITIMATE FAMILY DRIFT

True family center has actually moved to:
[0.8,0,0].

Update stream and observational canaries report the same candidate.

Thus observational evidence is intentionally identical.

Only regenerated functional consequence differs.

REGENERATION CHALLENGE
For each challenge trial:

1.
sample one lineage coefficient from the actual current family;

2.
regenerate/evaluate once using:
LIVE TEMPLATE;

3.
regenerate/evaluate the matched lineage using:
CANDIDATE TEMPLATE;

4.
observe local paired functional-loss difference.

Positive challenge benefit means:
candidate performs better than live.

Primary lineage variation SD:
0.55.

Primary consequence observation noise SD:
0.25.

The challenge receives no:
- poison label;
- semantic family-change label;
- true family center.

SEQUENTIAL DECISION
Maximum challenge pairs:
32.

Minimum before decision:
4.

At each step,
compute the running paired benefit estimate.

Exploratory confidence threshold:
approximately 2.33 standard errors.

ACCEPT candidate if:
benefit is confidently positive.

REJECT candidate if:
benefit is confidently negative.

Otherwise:
continue until the cap.

If unresolved at 32:
HOLD / DO NOT PROMOTE YET.

These constants are synthetic discriminating values only.

PRIMARY FUNCTIONAL CONFIRMATION
20,000 fresh challenge episodes per condition.

GLOBAL COMMON-MODE POISON

false candidate ACCEPT:
approximately 0.30%.

correct REJECT:
approximately 96.96%.

HOLD:
approximately 2.74%.

mean challenge pairs:
10.60.

median:
8.

LEGITIMATE FAMILY DRIFT

correct ACCEPT:
approximately 97.17%.

incorrect REJECT:
approximately 0.31%.

HOLD:
approximately 2.52%.

mean challenge pairs:
10.52.

median:
8.

PRIMARY POSITIVE
The poisoned candidate and legitimate drift candidate are observationally indistinguishable by construction.

Functional regeneration consequence separates them.

Thus:

OBSERVATIONAL CONSENSUS
CAN NOMINATE A TEMPLATE VERSION,

but

FUNCTIONAL CONSEQUENCE
CAN PROVIDE THE FINAL PROMOTION SIGNAL
WHEN OBSERVATIONAL SOURCES SHARE A FAILURE MODE.

This closes H40's specific passive-observation identifiability failure in the tested synthetic geometry.

WEAK / PARTIAL DRIFT REGION
Intermediate true family centers create ambiguous functional evidence.

True center:
0.2 along the candidate axis.

ACCEPT:
approximately 5%.

REJECT:
approximately 62%.

HOLD:
approximately 33%.

True center:
0.4.

ACCEPT:
approximately 18%.

REJECT:
approximately 18%.

HOLD:
approximately 64%.

True center:
0.6.

ACCEPT:
approximately 62%.

REJECT:
approximately 5%.

HOLD:
approximately 33%.

INTERPRETATION
When live and candidate templates have similar functional value,
the bounded validator often remains unresolved.

This is appropriate.

A high-leverage shared template should be allowed to remain:

CANDIDATE / UNPROMOTED

when functional evidence is weak.

FUNCTIONAL VALIDATION IS NOT AUTOMATICALLY CAUSAL
A second stress contaminates the regeneration challenge itself.

Suppose passive environmental improvement occurs while candidate regeneration is being evaluated.

The raw observed benefit becomes:

true candidate benefit
+
passive waiting improvement.

This passive term is NOT caused by the candidate template.

RAW CHALLENGE UNDER POSITIVE PASSIVE BIAS
Poison world remains truly centered at 0.

PASSIVE BIAS = 0.20

false ACCEPT:
0.77%.

REJECT:
79.59%.

HOLD:
19.64%.

PASSIVE BIAS = 0.40

false ACCEPT:
3.69%.

REJECT:
43.03%.

HOLD:
53.28%.

PASSIVE BIAS = 0.60

false ACCEPT:
9.75%.

REJECT:
14.65%.

HOLD:
75.60%.

PASSIVE BIAS = 0.80

false ACCEPT:
29.82%.

REJECT:
5.30%.

HOLD:
64.88%.

PRIMARY FUNCTIONAL-CONFOUNDING NEGATIVE
A sufficiently large passive improvement can make a poisoned template look functionally useful.

Therefore:

FUNCTION IMPROVED AFTER CANDIDATE REGENERATION

does not automatically imply:

THE CANDIDATE TEMPLATE CAUSED THE IMPROVEMENT.

H41 does not bypass the causal-control problem.

MATCHED WAITING / DISTURBANCE CONTROL
Add one matched action-decoupled control measurement of the passive environmental change.

Adjusted benefit:

candidate-vs-live functional difference
-
matched waiting/disturbance change.

Control observation noise SD:
0.10.

POISON WORLD
Across tested passive biases:

0
0.20
0.40
0.60
0.80

false candidate acceptance remains approximately:

0.25% to 0.38%.

correct rejection remains approximately:

96.7% to 97.0%.

mean challenge pairs remain near:

10.5 to 10.7.

LEGITIMATE DRIFT
Apply equivalent negative passive bias,
which can make a truly useful candidate appear less useful.

WITHOUT matched control:

bias -0.40:
correct ACCEPT falls to approximately 42.86%.

bias -0.80:
correct ACCEPT falls to approximately 5.25%.

WITH matched control:

across:
0
-0.20
-0.40
-0.60
-0.80

correct candidate ACCEPT remains approximately:

96.5% to 96.8%.

incorrect rejection remains around:
0.25% to 0.44%.

PRIMARY CAUSAL-CONTROL POSITIVE
Functional regeneration validation becomes robust to the tested passive waiting bias when the challenge uses:

ACTION-DECOUPLED MATCHED DISTURBANCE CONTROL.

This directly reuses the S7-S9 causal-control architecture.

No separate causal system is required.

CURRENT SHARED-TEMPLATE PROMOTION HIERARCHY
LINEAGE / FAMILY UPDATE

->
CURRENT-FIT SCREEN

->
SHADOW CANDIDATE VERSION

->
PROVENANCE-DIVERSE OBSERVATIONAL CANARIES

->
if observational evidence is sufficient and independent:
PROMOTION CONFIDENCE.

If all observational sources may share a common-mode failure:

BOUNDED FUNCTIONAL REGENERATION CHALLENGE

+

MATCHED WAITING / DISTURBANCE CONTROL

+

REPEATED CONSEQUENCE CONFIDENCE

->

PROMOTE
or
REJECT
or
HOLD.

GENERAL PRINCIPLE
The evidence hierarchy is now:

OBSERVATION
can propose.

INDEPENDENT OBSERVATION
can strengthen confidence.

PERSISTENCE
can reject transient artifacts.

FUNCTIONAL CAUSAL CONSEQUENCE
can break observational equivalence.

But even functional consequence itself requires:
causal control.

This hierarchy has now appeared repeatedly in:
- action credit;
- resource credit;
- structural growth;
- context authority;
- shared generative-template promotion.

RELATION TO H12
H12 validated candidate permanent structural dimensions through functional microprobes.

H41 applies the same principle one level higher:

a candidate SHARED GENERATIVE TEMPLATE VERSION
must earn functional consequence before receiving family-wide authority
when observational validation is under-identified.

RELATION TO H20
H20 used functional challenge to distinguish:
real context transition
from
persistent false context.

H41 uses functional challenge to distinguish:
real family-template evolution
from
globally agreed poisoned template.

This suggests a reusable Yggdrasil motif:

OBSERVATIONAL CHANGE PROPOSAL
->
BOUNDED FUNCTIONAL CHALLENGE
->
CAUSAL AUTHORITY.

IMPORTANT LIMITATION
H41 still assumes:
- safe temporary regeneration/challenge is possible;
- paired challenge samples are meaningful;
- a valid matched disturbance control exists;
- challenge cost is acceptable.

The next problem is therefore not:
whether functional validation can work.

It is:
WHEN ITS COST AND RISK JUSTIFY USING IT.

DECISION
AR-H41 is POSITIVE WITH A CAUSAL-CONTROL REQUIREMENT.

Supported synthetically:

- functional regeneration challenge can distinguish legitimate family drift from globally common-mode poisoned observational evidence;
- the strong cases resolve with roughly 8 median paired trials;
- weak/partial drift produces an appropriate hold region;
- passive environmental improvement can confound functional promotion credit;
- matched action-decoupled waiting control restores robust discrimination in the tested bias range.

Not demonstrated:

- real target-free regenerative consequence;
- safe real regeneration challenge;
- optimal challenge budget;
- optimal confidence threshold;
- real matched waiting control;
- distributed execution across lineage fragments.

NEXT CLEAN QUESTION
AR-H42 — VALUE-GATED FUNCTIONAL TEMPLATE VALIDATION

Question:

A functional regeneration challenge is expensive and may temporarily perturb a lineage.

Can the organism decide:

WHEN IS IT WORTH CHALLENGING A TEMPLATE VERSION?

Use:
- observational promotion confidence;
- number/effective diversity of canaries;
- template leverage / number of dependent retired lineages;
- expected functional divergence;
- challenge cost;
- urgency of recurrence;
- uncertainty that all observational sources share one failure mode.

Compare:

A.
always functional-challenge every candidate version;

B.
never challenge if observational canaries agree;

C.
value-gated challenge;

D.
high-leverage vs low-leverage shared templates;

E.
rare global-common-mode poison.

Desired:

cheap/low-impact candidate
->
avoid unnecessary challenge.

high-leverage ambiguous candidate
->
buy functional validation.

strong safe evidence
->
promote without spending maximal challenge budget.

This should reuse S4-S9/H21-H22 evidence-economy logic
rather than create another scheduler.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_functional_episodes_per_condition = 20000
max_challenge_pairs = 32
primary_confidence_z = 2.33
primary_lineage_sd = 0.55
primary_consequence_noise_sd = 0.25
matched_control_noise_sd = 0.10
