TITLE: DG-1A-AR-H106 — Collective Observable / Distributed Sensor Morphogenesis Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE LOCAL-COLLECTIVE-PERCEPTION RESULT + GLOBAL-AVERAGING FAILURE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh105-temporal-observable-morphogenesis-audit.ice

PURPOSE
H105 shows:
hidden context can live in:
temporal relation.

H106 asks the spatial analogue:

WHAT IF
NO CELL'S OWN SCALAR STATE
CONTAINS
THE RELEVANT CONTEXT,

but:
the relationship among neighbors does?

Can:
perception become:
a local tissue computation

without:
one global observer?

BOUNDARY
This is synthetic.

It does not:
- freeze covariance as the final spatial observable;
- freeze one-hop neighborhoods;
- prove the toy field is a realistic neural tissue;
- establish hardware communication costs;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL FIELD
16 x 16 synthetic tissue.

Each cell carries:
one scalar local value.

The marginal distribution
of:
an individual cell

is approximately:
standardized
under both hidden modes.

Thus:
cell-autonomous value alone
is:
uninformative.

HIDDEN MODES

MODE 0 — LOCALLY COHERENT

neighboring values tend to:
share sign / local structure.

MODE 1 — LOCALLY ANTI-COHERENT

the same underlying smooth field
is modulated by:
alternating spatial sign.

Individual cell marginals remain:
approximately unchanged.

The discriminating information is:
NEIGHBOR RELATION.

CANDIDATE OBSERVABLES

CELL AUTONOMOUS

own scalar value.

ONE-HOP COLLECTIVE

own value
times:
mean of:
four nearest neighbors.

TWO-HOP COLLECTIVE

weighted relation to:
one-hop
and
two-hop neighbors.

GLOBAL CENTRAL READOUT

whole-tissue mean:
nearest-neighbor covariance.

PRIMARY HOMOGENEOUS-TISSUE TEST
Each episode has:
one hidden mode
across:
the full tissue.

250 matched train/test populations
for Brier-gain confirmation.

CELL SELF

mean held-out Brier improvement:
approximately -0.00006.

ONE-HOP

+0.09628.

TWO-HOP

+0.08771.

GLOBAL

+0.24832.

CLASSIFICATION DIAGNOSTIC
150 matched evaluations.

CELL SELF:
52.79%.

ONE-HOP:
85.43%.

TWO-HOP:
79.97%.

GLOBAL:
100%.

PRIMARY COLLECTIVE-PERCEPTION POSITIVE
A cell can infer:
a context absent from:
its own local scalar

by:
recruiting:
neighbor relation.

Spatial context can therefore become:
an emergent local observable.

WHY GLOBAL LOOKS PERFECT
When:
the entire organism
shares:
one spatial mode,

a global average
uses:
hundreds of correlations.

It suppresses:
local noise

and:
classifies the global mode
nearly perfectly.

This is:
a legitimate advantage
in:
a globally homogeneous world.

But:
it creates:
a hidden assumption:

THE WHOLE TISSUE
HAS
ONE CONTEXT.

HETEROGENEOUS-TISSUE STRESS
The left half of the tissue
uses:
coherent mode.

The right half:
anti-coherent mode.

No single:
organism-wide context
is correct.

250 matched predictive tests.

Brier improvement:

CELL SELF:
-0.00004.

ONE-HOP:
+0.09433.

TWO-HOP:
+0.08551.

GLOBAL:
-0.00003.

CLASSIFICATION

CELL:
50.21%.

ONE-HOP:
85.96%.

TWO-HOP:
78.88%.

GLOBAL:
49.97%.

PRIMARY GLOBAL-AVERAGING FAILURE
The centralized readout is:
correct
only when:
one context
describes:
the whole tissue.

When:
different regions occupy:
different causal modes,

the global summary:
averages them together

and loses:
both local truths.

Thus:

MORE GLOBAL INFORMATION
CAN PRODUCE
LESS LOCAL TRUTH.

LOCAL OBSERVABLE
retains:
spatial heterogeneity.

COMMUNICATION-COST DIAGNOSTIC
Synthetic information-cost prices:

ONE-HOP:
0.01.

TWO-HOP:
0.025.

GLOBAL:
0.20
per local decision-equivalent.

HOMOGENEOUS net Brier-value:

ONE-HOP:
~0.0863.

TWO-HOP:
~0.0627.

GLOBAL:
~0.0483.

Even in:
the globally homogeneous case,

the global readout's:
extra certainty

can be:
worse after:
communication cost.

In:
the heterogeneous case,

the global policy is:
both costly
and
uninformative.

This is:
a diagnostic cost model,
not:
hardware benchmarking.

BOUNDARY EFFECT
Local sensors near:
the boundary between modes

receive:
mixed neighbor evidence.

Thus:
their confidence falls.

This is:
desirable.

The boundary is:
actually ambiguous
at:
the tested neighborhood scale.

A local confidence signal can:
represent:
that ambiguity

instead of:
forcing:
one global label.

CURRENT COLLECTIVE SENSOR OBJECT
A local developmental sensor may carry:

OWN STATE

+

NEIGHBOR SUMMARY

+

SPATIAL SCALE

+

INFORMATION VALUE

+

COMMUNICATION COST

+

LOCAL CONTEXT CONFIDENCE.

The useful measurement
belongs to:
the tissue relation,

not:
one cell
in isolation.

RELATION TO H59
H59:
local demand fields
allow:
distributed coordination.

H106:
local relational observables
allow:
distributed perception.

Both avoid:
requiring:
one central global state.

RELATION TO H103-H105
H103:
recruit:
which raw variable
to observe.

H104:
construct:
relations among variables.

H105:
construct:
relations across time.

H106:
construct:
relations across space.

Thus:
the developmental sensorium
now spans:

VARIABLE

ALGEBRA

TIME

SPACE.

OUTSIDE-STATUS-QUO IMPLICATION
Perception need not reside in:
a dedicated global encoder.

Some context may exist only as:
a local tissue statistic.

The organism can:
literally grow:
the measurement
where:
the relation exists.

This is a computational mechanism,
not:
biological tissue implementation.

GENERAL PRINCIPLE
IF:
CONTEXT IS LOCAL,

DO NOT DESTROY IT
BY:
AGGREGATING
THE WHOLE ORGANISM
TOO EARLY.

Use:
local sufficient statistics

and propagate:
only what:
higher scales actually need.

DECISION
AR-H106 is POSITIVE WITH A GLOBAL-AVERAGING FAILURE.

Supported synthetically:

- individual cells can be blind to context encoded in neighbor relations;
- a one-hop collective observable recovers substantial context information;
- global aggregation can be extremely accurate when context is truly global;
- the same global summary collapses under simultaneous spatially different modes;
- local collective sensing preserves heterogeneous regional context;
- communication cost can favor local observables even when global aggregation is more statistically precise.

Not demonstrated:

- asynchronous neighborhoods;
- topology changes;
- learned neighborhood shape;
- sensor-relay specialization;
- multi-scale local context;
- real distributed feature transport.

NEXT HIGH-VALUE MOVE
AR-H107 — INFORMATION CONDENSATION / DEVELOPMENTAL SENSORY RELAY SPECIALIZATION

H106 lets:
every cell
compute:
its own neighborhood statistic.

That may still be:
wasteful.

Question:

can a subset of cells become:
temporary SENSORY RELAYS

that condense:
local relational evidence

into:
a cheap context message
for nearby tissue?

Compare:

A.
every cell computes:
full neighborhood observable;

B.
fixed relay grid;

C.
demand-driven reversible relay specialization;

D.
relay failure;

E.
spatially changing context;

F.
too sparse relays
causing:
aliasing / blind zones.

Desired:

LOCAL EVIDENCE
->
LOW-DIMENSIONAL CONTEXT SUMMARY

->
NEARBY REUSE.

But:
relay roles should remain:
reversible

and:
multiple local contexts
must not be:
collapsed into one global message.

This would connect:
the developmental sensorium
to:
H69-H71 emergent division of labor.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 16x16
homogeneous_onehop_accuracy = 0.8543
heterogeneous_onehop_accuracy = 0.8596
heterogeneous_global_accuracy = 0.4997
