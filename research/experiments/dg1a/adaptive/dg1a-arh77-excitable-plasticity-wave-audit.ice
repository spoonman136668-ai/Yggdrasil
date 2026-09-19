TITLE: DG-1A-AR-H77 — Excitable Plasticity Wave / Self-Terminating Repair Front Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE MISMATCH-GATED WAVE RESULT + PREPARATION-DEPTH TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh76-adaptive-plasticity-radius-audit.ice

PURPOSE
H75-H76 still represent developmental softening as:
a concentration/radius field.

H77 removes:
explicit radius.

QUESTION
Can injury emit:
an event-triggered plasticity wave

whose propagation is decided by:
the tissue itself?

Candidate rule:

relay the wave only if:
- local role/function mismatch is present;
- or the cell directly borders real damaged tissue.

Otherwise:
healthy correctly functioning tissue absorbs the pulse.

The desired result is:
a repair front that stops because
nothing farther away needs changing.

BOUNDARY
This is synthetic.

It does not:
- freeze a production excitable-wave rule;
- establish final refractory semantics;
- prove real Yggdrasil injury signals exist;
- replace all plasticity fields;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

SPATIAL TISSUE
24 x 24 cells.

Local role specialization:
left/right functional pattern.

CURRENT CANALIZATION
A received plasticity pulse suppresses:
current role commitment

temporarily.

It does not rewrite:
slow developmental memory.

WAVE STATE
Injury emits:
a local pulse.

Each cell may accept/relay the next-hop pulse if:

LOCAL FUNCTIONAL MISMATCH

or

DIRECT ADJACENCY TO REAL DAMAGE.

Cells maintain a short:
4-step recent-wave refractory state

to reduce repeated identical propagation.

The refractory state is local to this synthetic event family.

DAMAGE HEARTBEAT
Persistent damaged regions re-emit a low-frequency local pulse approximately every:
6 steps.

This permits the repair front to continue following:
a changing injury boundary.

COMPARATORS

CELL-LOCAL METAPLASTICITY ONLY

vs

MISMATCH-GATED EXCITABLE PLASTICITY WAVE.

SCENARIOS

EXPANDING DAMAGE

MOVING DAMAGE

SPLIT / TWO-SITE DAMAGE

PERSISTENT FALSE SINGLE EMITTER.

PRIMARY CONFIRMATION
20 matched streams for the first complete comparator.

A reduced 12-stream follow-up tested:
one-hop and two-hop ahead-of-mismatch relay variants.

EXPANDING DAMAGE

CELL-LOCAL ONLY

mean expansion-window service:
697.66.

repair-front functional match:
0.8671.

plasticity-softened tissue:
approximately 1.89%.

WAVE

service:
698.82.

frontier match:
0.9102.

softened tissue:
7.45%.

accepted/relayed wave events across the active damage interval:
approximately 1,872.

PRIMARY EXPANDING-DAMAGE POSITIVE
The self-terminating wave improves:
frontier preparedness

without:
an explicit plasticity radius.

It remains more conservative than:
the strongest fixed/coherence-gated H76 field,
which reached approximately:
0.964 frontier match.

Thus:
self-termination trades some anticipatory preparation for:
less arbitrary spread.

MOVING DAMAGE

CELL-LOCAL

service:
715.32.

frontier match:
0.8752.

WAVE

service:
717.22.

frontier match:
0.9238.

softened tissue:
5.16%.

accepted wave events:
approximately 1,217.

PRIMARY MOVING-FRONT POSITIVE
The wave follows:
a moving local injury

without:
recomputing or storing a global repair radius.

SPLIT / TWO-SITE DAMAGE

CELL-LOCAL

service:
716.52.

frontier match:
0.9381.

WAVE

service:
717.83.

frontier match:
0.9712.

softened tissue:
5.45%.

accepted events:
approximately 1,082.

PRIMARY MULTI-FOCUS POSITIVE
Independent local injury sites can generate:
independent plasticity fronts.

There is no need to convert them into:
one global developmental state.

FALSE SINGLE EMITTER

CELL-LOCAL baseline service:
748.80.

WAVE:
748.50.

softened tissue:
0.174%.

accepted wave events:
150.

post-false-alarm service:
748.80.

PRIMARY FALSE-SOURCE RESULT
The false emitter cannot recruit:
healthy distant tissue

because:
neighboring cells detect neither
functional mismatch
nor
real damage adjacency.

Thus:
the pulse dies locally.

This is the core self-termination property.

COMMUNICATION-SPARSITY RESULT
In the expanding-damage toy,
the wave uses:
approximately 1.9k accepted local pulse/relay events

over the active interval.

A continuously refreshed whole-tissue field would update:
hundreds of local states
every step.

This is not a hardware cost theorem,
but it indicates:
event-triggered developmental softening can be sparse.

AHEAD-OF-MISMATCH RELAY STRESS
Follow-up variants allow:
the wave to propagate through cells one or two hops ahead of current mismatch.

12 matched streams.

BASE MISMATCH-GATED WAVE

expanding match:
0.91017.

softened tissue:
7.45%.

accepted events:
~1,864.

ONE-HOP-AHEAD

match:
0.91018.

softened:
7.60%.

events:
~1,920.

TWO-HOP-AHEAD

match:
0.91018.

softened:
7.77%.

events:
~1,984.

PRIMARY PREPARATION-DEPTH NEGATIVE
Forcing the wave ahead of actual mismatch:
adds communication
and
collateral plasticity

without:
materially improving expanding-front accuracy.

Healthy tissue is already acting as:
a useful stopping boundary.

MOVING-DAMAGE DETAIL
Two-hop-ahead propagation raises moving-front match only modestly:

approximately:
0.9238
->
0.9261,

while increasing:
wave events
and
softened tissue.

This is not enough to justify:
aggressive anticipatory propagation
at the tested working point.

CORE ARCHITECTURAL RESULT
H76 asks:

HOW LARGE SHOULD THE PLASTICITY FIELD BE?

H77 offers a different answer:

DO NOT STORE A RADIUS.

LET EACH CELL DECIDE
WHETHER THE FRONT SHOULD CONTINUE.

The propagation boundary emerges from:
local function.

RELATION TO H62
H62 showed:
waves/pulses can encode sparse developmental coordination efficiently.

H77 applies:
event waves
to
metaplasticity.

The signaling mode is now:
event-triggered
and
self-limiting.

RELATION TO H51
H51 established:
mutually consistent control signals still need:
functional consequence.

H77 uses:
local functional mismatch
as the condition that allows:
developmental influence
to propagate.

Thus:
plasticity recruitment is tied to:
local need,
not merely:
signal receipt.

GENERAL PRINCIPLE
A DEVELOPMENTAL SIGNAL
SHOULD NOT
AUTOMATICALLY HAVE
UNBOUNDED RELAY AUTHORITY.

Propagation can be conditioned on:

IS THIS SIGNAL LOCALLY RELEVANT?

Healthy functioning tissue can:
absorb
rather than:
forward.

DECISION
AR-H77 is POSITIVE WITH A PREPARATION-DEPTH TRADEOFF.

Supported synthetically:

- plasticity can propagate as an event wave rather than a maintained radius field;
- local mismatch can self-terminate the front;
- moving and split injuries are tracked;
- persistent false single emitters remain tightly localized;
- no global radius is required;
- aggressively pushing the front ahead of local evidence provides little value in the tested benchmark.

Not demonstrated:

- asynchronous pulse loss;
- provenance-aware multi-source refractory state;
- globally correlated false mismatch;
- actual regenerative cell division;
- interaction with resource vasculature;
- real functional mismatch signal.

NEXT HIGH-VALUE MOVE
AR-H78 — ROLE / TRANSFORMATION INVENTION FROM GENERIC OPERATORS

H70-H77 improve:
role assignment,
role population,
plasticity,
and
repair.

But one central limitation remains:

the useful TRANSFORMATIONS
are still supplied by the experiment.

Question:

Can a tissue discover:
useful computational pathways

from:
a generic operator repertoire

without being told:
which operators form the useful role sequence?

Candidate setup:

all cells begin symmetric.

Each may apply:
one of several generic local transformations.

Only some transformation sequences produce:
functional output.

Intermediate products carry:
provenance.

Successful downstream use sends:
causal eligibility credit
back to upstream transformations.

Required stresses:

- useless operator loops;
- duplicate-role collapse;
- delayed credit;
- topology/resource niche changes;
- false intermediate that looks locally active but never reaches functional output.

Desired:

ROLE CONTENT ITSELF
begins to emerge,

not only:
which cell expresses a predeclared role.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 24x24
primary_matched_streams = 20
followup_matched_streams = 12
