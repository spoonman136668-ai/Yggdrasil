TITLE: DG-1A-AR-S7 — Causally Controlled Learned Value-of-Information Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-WITH-CONTROL-INTEGRITY-LIMIT RESOURCE-CREDIT AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
SERIES_NOTE: SUPPLEMENTAL AR-S SERIES — CANONICAL R4 AR-U NUMBERING PRESERVED
BRANCH: dg1a-ar
PARENT: dg1a-ars6-learned-local-value-of-information-audit.ice

PURPOSE
S6 established that a local learned evidence allocator can recover useful value-of-information behavior from local history.

S6 also exposed a causal failure:

if passive environmental improvement is correlated with the time spent probing,
a naive learner can credit that improvement to the extra evidence itself.

S7 asks:

Can a local evidence allocator distinguish:

THE EXTRA PROBE HELPED

from

THE WORLD IMPROVED WHILE I WAS PROBING?

BOUNDARY
This is synthetic.

It does not:
- prove a real Yggdrasil disturbance reference;
- establish a production control-selection algorithm;
- define biological utility units;
- authorize a central evidence scheduler;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FOCUSED TRANCHE BENCHMARK
S7 isolates the causal question.

Each event begins after four local consequence probes.

The local controller chooses between:

STOP-4

or

EXTEND-8

for event families with enough local time.

The learner is never told:
- maintenance;
- repair;
- true functional stake;
- true observation noise.

It receives only an anonymous local context cluster.

Two latent event families are used in the scored tranche benchmark.

Latent family 0:
stake = 1
noise SD = 0.10

Latent family 1:
stake = 4
noise SD = 0.16

True signal magnitude:
0.08

Probe cost:
0.03 per probe beyond the first.

Anonymous context reports the latent family correctly only:
80%

so context is useful but imperfect.

TRUE CAUSAL VALUE OF EXTENDING
At the parameter-informed expectation level:

family 0:

expected STOP-4 loss:
0.144799

expected EXTEND-8 loss:
0.221826

Thus:
extra probing is harmful after cost.

family 1:

STOP-4:
0.724621

EXTEND-8:
0.524598

Thus:
extra probing is useful.

The correct resource policy must therefore learn:
do not extend every uncertain event.

PASSIVE IMPROVEMENT CONFOUND
When EXTEND-8 is selected,
four additional probe intervals pass.

Synthetic passive environmental improvement is added to the observed outcome:

passive_gain
=
confounding_slope * 4.

This passive gain is not caused by the evidence.

The true evaluation metric removes it.

POLICIES

NAIVE LEARNED VoI
Update action values from raw observed outcome.

MATCHED ACTION-DECOUPLED REFERENCE
A local matched reference experiences the same passive environmental improvement
but receives no probe-caused action benefit.

Adjusted outcome:

target
=
observed_target_outcome
-
matched_reference_change.

SMOOTHED DISTURBANCE BASELINE
Estimate the passive waiting gain by EMA from matched references
and subtract that estimate from probe credit.

CONFIDENCE-WEIGHTED CONTROL
Blend causal correction with the raw learned policy according to:
- reference sample count;
- reference variability.

Low control confidence causes fallback toward the uncorrected learner.

PRIMARY CONFIRMATION
100000 events per seed.

Evaluation:
last 50000.

6 matched seeds.

MAIN CONFOUND SWEEP

NO PASSIVE CONFOUND

NAIVE:
true loss 0.310288
extend rate 0.588847
family-0 extend 0.495743
family-1 extend 0.775405

MATCHED:
0.312119
extend 0.605213
family-0 0.520321
family-1 0.774649

EMA:
0.310107
extend 0.604560

Interpretation:
when no passive confound exists,
causal correction does not create a material advantage.

This is expected.

CONFOUND SLOPE = 0.02 PER EXTRA INTERVAL

NAIVE:
true loss 0.320278
extend rate 0.859623
family-0 extend 0.838140
family-1 extend 0.902369

MATCHED:
true loss 0.312119
extend 0.605213

EMA:
0.310057
extend 0.615693

The naive learner already begins treating almost all events as worth extending.

CONFOUND SLOPE = 0.04

NAIVE:
true loss 0.323979
extend rate 0.945683
family-0 extend 0.943711
family-1 extend 0.949595

MATCHED:
true loss 0.312119
extend 0.605213
family-0 0.520321
family-1 0.774649

EMA:
true loss 0.309802
extend 0.614987
family-0 0.526751
family-1 0.791487

CONFIDENCE-WEIGHTED:
true loss 0.311522
extend 0.640380

PRIMARY POSITIVE
At confound 0.04,
the naive allocator extends:

94.6%

of events.

The matched action-decoupled control remains near:

60.5%.

The smoothed disturbance control remains near:

61.5%.

Most importantly,
the controlled policies retain a large difference between:

family 0,
where extra probing is genuinely costly,

and

family 1,
where extra probing is useful.

The naive policy loses that distinction.

CONFOUND SLOPE = 0.06

NAIVE:
true loss 0.323861
extend rate 0.967540

MATCHED:
0.312119
extend 0.605213

EMA:
0.310166
extend 0.613940

Thus:
the matched causal estimate is essentially invariant to the passive-improvement slope in this benchmark.

RESOURCE WASTE RESULT
The naive learner does not merely become statistically biased.

It spends adaptive resources on decisions where the extra evidence is causally harmful after cost.

Therefore:

OUTCOME IMPROVED AFTER PROBING

does not imply:

PROBING CAUSED THE IMPROVEMENT.

This is the value-of-information version of the earlier causal-credit rule:

PREDICTION / CORRELATION QUALITY
IS NOT
CAUSAL-CONTROL VALIDITY.

CONTROL-CONTAMINATION STRESS
The matched reference is now deliberately allowed to contain some fraction of the target's real probe-caused benefit.

contamination = 0
means action-decoupled.

contamination = 1
means the reference fully inherits the realized causal gain/loss of extra probing.

Primary passive confound:
0.04.

6 matched seeds.

CONTAMINATION = 0

NAIVE:
true loss 0.320896
extend 0.956997

MATCHED:
0.313036
extend 0.626963

EMA:
0.314322
extend 0.652823

CONFIDENCE-WEIGHTED:
0.313750
extend 0.686170

CONTAMINATION = 0.25

MATCHED:
true loss 0.314923
extend 0.716637

EMA:
0.316741
extend 0.703957

CONFIDENCE-WEIGHTED:
0.318875
extend 0.907990

CONTAMINATION = 0.50

MATCHED:
0.317952
extend 0.686127

EMA:
0.317778
extend 0.701650

CONFIDENCE-WEIGHTED:
0.321014
extend 0.941393

CONTAMINATION = 0.75

MATCHED:
0.323364
extend 0.653060

EMA:
0.323133
extend 0.680193

CONTAMINATION = 1.00

MATCHED:
true loss 0.330678
extend 0.512730

EMA:
0.328275
extend 0.644483

CONFIDENCE-WEIGHTED:
0.320293
extend 0.953133

PRIMARY NEGATIVE
Causal correction is only valid when the reference is sufficiently action-decoupled.

A contaminated control subtracts some of the true causal benefit of probing.

At full contamination,
the matched correction becomes worse than the naive allocator on true task loss.

Therefore:

BAD CONTROL
CAN BE WORSE THAN
NO CONTROL.

CONFIDENCE-WEIGHTED FALLBACK
The confidence-weighted controller reacts to unstable / contaminated reference behavior by progressively falling back toward the raw learned allocator.

At full contamination:

true loss:
0.320293

which is close to naive:
0.320896.

But extend rate returns to:
0.953133.

Thus the fallback protects task performance
but gives up most resource savings.

This is an appropriate failure direction:

if the causal baseline is not trustworthy,
do not manufacture false certainty.

REFERENCE-NOISE STRESS
With zero action contamination,
the matched reference remains relatively stable as reference noise SD rises.

At passive confound 0.04:

reference noise 0.01:
matched true loss ~0.3130
extend ~0.611

reference noise 0.03:
~0.3131
extend ~0.612

reference noise 0.06:
~0.3139
extend ~0.605

reference noise 0.10:
~0.3147
extend ~0.614

reference noise 0.15:
~0.3140
extend ~0.611

Thus ordinary measurement noise is much less damaging than systematic action contamination.

That distinction matters.

CONTROL QUALITY HAS TWO AXES

1.
DISTURBANCE COUPLING

Does the reference track the passive change that confounds the target?

2.
ACTION DECOUPLING

Does the reference remain outside the causal footprint of the probe action?

A good control needs both.

This exactly matches the earlier local causal-credit research.

ARCHITECTURAL CONSEQUENCE
The local evidence allocator should not learn probe value directly from:

outcome_after_probe.

It should learn something closer to:

TARGET OUTCOME CHANGE

minus

ACTION-DECOUPLED DISTURBANCE / WAITING CHANGE.

Then update value-of-information only when:
- control freshness is adequate;
- action exposure is low enough;
- control confidence is sufficient.

CURRENT RESOURCE-CREDIT STACK

LOCAL UNCERTAINTY

+

ANONYMOUS CONTEXT

+

CURRENT EVIDENCE

+

PROBE COST

+

DEADLINE

+

LEARNED VALUE HISTORY

+

ACTION-DECOUPLED WAITING / DISTURBANCE REFERENCE

+

CONTROL FRESHNESS

+

CONTROL ACTION-EXPOSURE RISK

->

CAUSAL VALUE OF ONE MORE PROBE.

RELATION TO S1 / S2
S1 established:
disturbance references should be disturbance-coupled and action-decoupled.

S2 established:
baseline choice should adapt to estimated action contamination.

S7 shows that the same requirement is not limited to role-update credit.

It also applies to:

LEARNING WHETHER TO COLLECT MORE EVIDENCE.

Thus causal hygiene belongs one level above the action controller as well.

META-PRINCIPLE
An adaptive system can become causally wrong in two distinct places:

ACTION CREDIT:
did my behavior cause the consequence?

RESOURCE CREDIT:
did collecting more evidence cause the better decision?

Both require valid controls.

DECISION
AR-S7 is POSITIVE WITH A CONTROL-INTEGRITY LIMIT.

Supported synthetically:

- passive improvement can make naive learned VoI severely over-probe;
- matched action-decoupled controls remove most of that bias;
- smoothed disturbance baselines preserve similar benefit;
- ordinary reference noise is tolerable;
- action contamination can invalidate causal correction;
- confidence-weighted fallback can avoid trusting an unstable control,
  but resource efficiency is then lost.

Not demonstrated:

- real Yggdrasil matched controls;
- real waiting baselines;
- real online action-exposure estimation for evidence collection;
- optimal control-confidence representation;
- causal VoI under overlapping spatial causal cones.

NEXT CLEAN QUESTION
AR-S8 — CONTROL-SELECTION / PROVENANCE FOR CAUSAL VoI

Question:

when several possible local references exist,
can the allocator learn which references are:

disturbance-coupled

but

action-decoupled

without receiving a semantic control label?

Test:
- near references with high disturbance match but high action contamination;
- farther references with weaker disturbance match but lower action exposure;
- stale references;
- copied/relayed references that are not independent;
- adaptive reference selection;
- defer when no valid control exists.

Desired:

choose the best causal control only when evidence supports it.

If no trustworthy control exists:

reduce causal-learning confidence

rather than inventing a probe-value estimate.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_events_per_seed = 100000
primary_eval_events = 50000
primary_matched_seeds = 6
control_contamination_seeds = 6
