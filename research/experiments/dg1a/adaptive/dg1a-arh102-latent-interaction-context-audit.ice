TITLE: DG-1A-AR-H102 — Latent Interaction Context / Residual-Driven Context-Split Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE LATENT-CONTEXT SPLIT RESULT + OBSERVABILITY / OVERFIT LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh101-causal-module-interface-audit.ice

PURPOSE
H101 stores:
one interaction model
for:
one module interface.

H102 asks a harder question:

WHAT IF
THE SAME INTERFACE
HAS:
TWO DIFFERENT CAUSAL BEHAVIORS

depending on:
an unlabelled latent mode?

The danger is:
averaging the two modes
into:
one noisy edge model.

QUESTION
Can:
systematic residual structure

cause:
a new context split

rather than:
merely increasing:
variance?

BOUNDARY
This is synthetic.

It does not:
- infer arbitrary latent variables;
- freeze one scalar cue;
- freeze one decision stump;
- prove the discovered partition is semantically correct;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

INTERFACE
Same conceptual X:Y interface.

LATENT MODE Z
Two unlabelled states.

Z = 0:

joint success:
0.88.

Z = 1:

joint success:
0.35.

Modes occur:
approximately 50/50.

The learner does NOT receive:
Z.

UNLABELLED LOCAL CUE
One scalar local observation:

C.

Under:
Z=0

C ~ Normal(-mu, 1).

Under:
Z=1

C ~ Normal(+mu, 1).

Primary:
mu = 0.8.

Thus:
the cue is:
informative
but:
noisy.

It is not:
a semantic context ID.

DATA
240 training interface observations.

240 independent validation observations.

MODEL A — SINGLE INTERFACE
One success probability
for:
all observations.

MODEL B — RESIDUAL-DRIVEN CONTEXT SPLIT
Search:
candidate thresholds
over:
the unlabelled cue.

For each threshold:

estimate:
one Bernoulli interface model
on each side.

Choose:
the threshold
with greatest:
training log-loss improvement.

PROMOTION
The split is accepted only if:

training improvement
>
0.015

AND

independent validation improvement
>
0.015.

Thus:
context birth
requires:
out-of-sample evidence.

PRIMARY MONTE CARLO
3,000 matched latent-interface trials.

3,000 homogeneous controls.

LATENT MODE
mu = 0.8.

split promoted:
87.37%.

single-interface held-out cross entropy:
0.66856.

validated split:
0.62636.

mean held-out improvement:
0.04220.

latent-mode classification accuracy
from:
the discovered threshold:

approximately 76.32%.

PRIMARY LATENT-CONTEXT POSITIVE
The system can discover:

THIS INTERFACE
DOES NOT HAVE
ONE STABLE CONSEQUENCE MODEL.

A simple cue-conditioned split
recovers:
substantial predictive structure

without:
being told
the latent mode label.

The discovered partition is:
imperfect

but:
functionally useful.

CUE-STRENGTH SWEEP

mu = 0.4

promotion:
28.13%.

held-out improvement:
0.00702.

context classification:
63.20%.

mu = 0.6

promotion:
67.33%.

improvement:
0.02307.

classification:
69.94%.

mu = 0.8

promotion:
87.37%.

improvement:
0.04220.

classification:
76.32%.

mu = 1.0

promotion:
95.77%.

improvement:
0.06299.

classification:
81.99%.

PRIMARY OBSERVABILITY RESULT
Latent structure becomes:
more discoverable

as:
some observable local variable
carries:
more information about:
the hidden mode.

This is expected
and
important.

NO-CUE STRESS
Set:

mu = 0.

The two causal modes still exist.

But:
the cue distribution
is identical
in both.

split promoted:
0.033%.

mean held-out improvement:
approximately zero.

context classification:
approximately 52.6%.

PRIMARY IDENTIFIABILITY LIMIT
If:
no observed variable
contains information
about:
the latent mode,

the tested learner cannot:
recover that hidden context.

This is not:
an algorithmic tuning failure.

It is:
an information limit.

HIDDEN CAUSE
CANNOT BE INFERRED
FROM
NO EVIDENCE.

HOMOGENEOUS INTERFACE CONTROL
No latent mode.

Single true interface success:
approximately 0.615.

Validation-gated false context promotion:
0.033%.

Thus:
independent validation strongly prevents:
ordinary stochastic residuals
from:
becoming:
new context state.

TRAINING-ONLY SPLIT NEGATIVE
If:
the best training split
is promoted
without:
independent validation,

homogeneous-noise false split rate:
approximately 5.1%.

PRIMARY OVERFIT NEGATIVE
Residual clustering
is itself:
a powerful overfitting mechanism.

If every:
random error pattern

can create:
new context,

the internal state space:
explodes.

Thus:

LATENT CONTEXT BIRTH
NEEDS
THE SAME:
SHADOW / VALIDATION DISCIPLINE
AS:
HYPOTHESIS BIRTH.

SINGLE-MODE AVERAGING FAILURE
The unsplit interface learns:
approximately the mode average.

That model is:
not completely wrong.

It is:
systematically under-specific.

It can never express:

HIGH-CONFIDENCE COMPATIBLE

and

HIGH-CONFIDENCE INCOMPATIBLE

at the same time.

This matters when:
the decision should differ
by:
context.

RELATION TO H7
H7:
model-fit confidence
should fall
when:
current evidence lies off:
the inherited representational manifold.

H102:
persistent structured misfit
can justify:
EXPANDING
the context representation itself.

RELATION TO H83
H83:
functional equivalence
is:
context-bounded.

H102:
sometimes:
the context boundary
is not supplied.

It must be:
inferred
from:
residual structure.

RELATION TO H98
H98:
persistent model residual
can create:
a new hypothesis.

H102:
persistent interface residual
can create:
a new context dimension / partition.

Thus:
open-world learning can expand:

MODEL SET

and

CONTEXT REPRESENTATION.

GENERAL PRINCIPLE
DO NOT AUTOMATICALLY LABEL:

SYSTEMATIC MULTIMODAL ERROR

as:

NOISE.

But:

DO NOT AUTOMATICALLY LABEL:

NOISE

as:

NEW CONTEXT.

Require:
repeatable,
out-of-sample
predictive improvement.

DECISION
AR-H102 is POSITIVE WITH OBSERVABILITY AND OVERFIT LIMITS.

Supported synthetically:

- one interface can contain multiple context-dependent causal modes;
- averaging those modes loses useful structure;
- residual-driven cue splitting can recover a useful latent-context partition;
- split quality tracks cue informativeness;
- independent validation sharply suppresses false latent-context birth;
- training-only residual splitting overfits ordinary noise;
- an unobservable latent mode cannot be recovered by the tested mechanism.

Not demonstrated:

- multi-dimensional latent contexts;
- nonlinear context boundaries;
- context birth in continuous causal graphs;
- active discovery of missing cues;
- context inheritance across cells;
- dynamic context merge / retirement.

NEXT HIGH-VALUE MOVE
AR-H103 — ACTIVE LATENT-CONTEXT DISCOVERY / SEEKING VARIABLES THAT EXPLAIN RESIDUALS

H102 assumes:
a useful cue C
is already being observed.

Question:

if an interface remains:
multimodal

but:
current observations do not explain it,

can the organism choose:
WHICH additional local measurement
or perturbation
is worth sampling?

Candidate setup:

several candidate internal variables.

Only one:
contains information about:
the hidden interface mode.

Others:
correlate weakly,
are expensive,
or
are noise.

Compare:

A.
observe everything continuously;

B.
random extra sensing;

C.
residual-information-gain sensing;

D.
cost-aware sensing;

E.
temporarily informative cue that later stops working.

Desired:

UNEXPLAINED CAUSAL RESIDUAL
->
TARGETED SENSORY RECRUITMENT

rather than:
permanent observation of:
every possible variable.

This would make:
the organism's effective sensorium
itself:
developmental and evidence-driven.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
train_observations = 240
validation_observations = 240
primary_cue_mu = 0.8
primary_split_promotion = 0.8737
homogeneous_false_split = 0.00033
