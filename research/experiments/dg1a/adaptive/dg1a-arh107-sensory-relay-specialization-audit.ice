TITLE: DG-1A-AR-H107 — Developmental Sensory Relay Specialization / Information Condensation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE REVERSIBLE SENSORY-RELAY RESULT + RELAY-DENSITY / SPATIAL-ALIASING TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh106-collective-observable-audit.ice

PURPOSE
H106 lets:
every cell
compute:
its own local collective observable.

That duplicates:
neighbor sensing
and
feature computation
across:
nearby cells.

H107 asks:

CAN A SUBSET OF CELLS
TEMPORARILY SPECIALIZE
AS:
SENSORY RELAYS

that:
condense local relational evidence
into:
a cheap context message
for nearby tissue?

BOUNDARY
This is synthetic.

It does not:
- freeze relay roles;
- freeze relay radius;
- prove actual cells should communicate discrete context labels;
- establish hardware costs;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TISSUE
20 x 20.

Four spatial quadrants.

Context pattern:

upper-left:
mode 0.

upper-right:
mode 1.

lower-left:
mode 1.

lower-right:
mode 0.

Thus:
the organism simultaneously contains:
multiple local contexts.

ACTIVE DEMAND
Only:
one half of the tissue

needs:
the context-dependent computation
in a given phase.

Phase 1:
upper half.

Phase 2:
lower half.

Demand therefore:
moves spatially.

LOCAL EVIDENCE
Same H106 one-hop covariance-like signal.

A relay averages:
its own local evidence
plus:
immediate-neighbor evidence

before:
emitting
one low-dimensional local context message.

RELAY DEVELOPMENT
The adaptive relay pattern uses:
a local coverage / lateral-inhibition abstraction.

A demanded cell becomes:
relay

if:
no nearby active relay
already covers:
its local neighborhood.

This yields:
distributed relay spacing

without:
a global target relay count.

The selected role is:
phase-specific
and
reversible.

COMPARATORS

CELL-AUTONOMOUS

every demanded cell
computes:
its own local collective observable.

FIXED RELAY GRID

25 relays
remain active
across:
the whole tissue

whether:
their region is demanded
or not.

DEMAND-DRIVEN ADAPTIVE RELAYS

relay roles appear only:
where:
active context-dependent work
requires:
the signal.

PRIMARY CONFIRMATION
500 matched synthetic episodes
across:
both demand phases.

CELL-AUTONOMOUS

mean context accuracy:
85.49%.

synthetic sensing/computation cost:
200.

active local computations:
200.

FIXED RELAY GRID

accuracy:
85.35%.

cost:
135.

relays:
25.

PRIMARY FIXED-RELAY RESULT
A sparse fixed relay grid
saves:
duplicate sensing cost

but:
does not improve:
local context fidelity
in the four-region geometry.

Some client cells:
reuse:
relay summaries
from:
the wrong side of:
a local context boundary.

DEMAND-DRIVEN ADAPTIVE RELAYS

accuracy:
91.64%.

cost:
167.32.

mean active relays:
31.46.

PRIMARY RELAY POSITIVE
Local relay specialization improves:

perception accuracy

and

resource cost

relative to:
every cell independently computing
the full collective observable.

Compared with:
cell-autonomous sensing:

cost falls:
approximately 16.3%.

accuracy rises:
approximately 6.1 percentage points.

The accuracy gain comes from:
local evidence condensation.

RELAY-DENSITY SWEEP
Adaptive local coverage radius.

RADIUS 1

mean relays:
75.54.

cost:
387.72.

accuracy:
92.66%.

RADIUS 2

relays:
31.46.

cost:
167.28.

accuracy:
91.82%.

RADIUS 3

relays:
19.34.

cost:
106.69.

accuracy:
90.67%.

RADIUS 4

relays:
12.74.

cost:
73.71.

accuracy:
89.40%.

PRIMARY DENSITY TRADEOFF
More relays:

reduce:
spatial aliasing

but:
increase:
computation / communication cost.

Fewer relays:

compress:
the sensorium

but:
a single relay message
covers:
larger heterogeneous regions.

Thus:

SENSORY COMPRESSION
HAS
A SPATIAL NYQUIST-LIKE LIMIT.

The relay density must remain:
high enough
for:
the scale of context variation.

RELAY FAILURE STRESS
Primary radius-2 adaptive pattern.

40%
of active relays
are removed.

WITHOUT RE-SPECIALIZATION

accuracy:
approximately 90.95%.

remaining relays:
18.89.

cost:
104.43.

The tissue retains:
substantial perception

because:
other local relays still provide:
nearby context evidence.

LOCAL RE-SPECIALIZATION
Uncovered demanded cells
can:
re-enter the relay role
using:
the same local coverage rule.

accuracy:
approximately 92.08%.

relays:
32.10.

cost:
170.50.

PRIMARY REPAIR RESULT
Relay loss can be:
locally repaired

without:
global sensor-network reconstruction.

The replacement pattern is:
not identical
to:
the old pattern.

It only restores:
local information coverage.

ROLE REVERSIBILITY
When:
context-dependent demand
moves
from:
upper half

to:
lower half,

the relay population
can be:
recomputed locally
around:
the new demand field.

The scientific point is:

SENSOR-RELAY ROLE
need not be:
a permanent cell type.

It can be:
a reversible phenotype
created by:
local information demand.

RELATION TO H69-H71
H69:
resource niches can create:
division of computational labor.

H71:
unmet work can control:
role population.

H107:
unmet information demand
can create:
division of perceptual labor.

The same developmental rule family
can potentially generate:

processors

relays

repair cells

or
sensors

from:
local functional demand.

RELATION TO H106
H106:
local collective observables
preserve:
regional truth.

H107:
those observables
can be:
computed once locally
and
reused
by:
nearby cells.

But:
condensation must remain:
local enough
to avoid:
averaging distinct contexts.

RELATION TO H62-H66
Once:
a relay computes:
a local context summary,

it can potentially use:
the adaptive signaling substrates
developed in:
H62-H66

to communicate:
that summary.

H107 does not yet:
integrate those mechanisms.

OUTSIDE-STATUS-QUO IMPLICATION
The sensorium can become:
a developmental tissue role.

Instead of:
every computational unit
receiving:
the same fixed observation vector,

some cells can temporarily become:

LOCAL OBSERVATION ORGANS

whose output:
other nearby computation reuses.

This is:
a software architecture.

GENERAL PRINCIPLE
COMPUTE:
LOCAL SUFFICIENT STATISTICS

ONCE
WHERE POSSIBLE.

REUSE THEM:
NEARBY.

But:

DO NOT CONDENSE
SO AGGRESSIVELY
THAT:
DISTINCT LOCAL CONTEXTS
ALIAS
INTO
ONE MESSAGE.

DECISION
AR-H107 is POSITIVE WITH A RELAY-DENSITY / SPATIAL-ALIASING TRADEOFF.

Supported synthetically:

- reversible local sensory relays can reduce duplicated sensing work;
- relay-local evidence aggregation can improve context accuracy;
- fixed relay placement can misalign with moving/heterogeneous information demand;
- adaptive relay density trades cost against spatial resolution;
- sparse relays create context aliasing;
- relay loss can be locally repaired by reversible role re-specialization.

Not demonstrated:

- online relay birth/death dynamics;
- relay trust;
- adversarial relay messages;
- multi-scale sensory hierarchy;
- learned relay radius;
- integration with real Yggdrasil communication.

NEXT HIGH-VALUE MOVE
AR-H108 — MULTI-SCALE PERCEPTUAL HIERARCHY / ADAPTIVE INFORMATION SCALE

H106-H107 establish:
local context sensing
and:
local relay condensation.

Question:

when should:
a local context summary
be allowed to:
propagate upward
into:
a regional
or
organism-level
representation?

Candidate principle:

if:
neighbor relay summaries
agree
and
context remains:
spatially homogeneous,

condense:
to a larger-scale summary.

If:
relay disagreement / boundary evidence rises,

stop:
upward aggregation
and
preserve:
local representations.

Compare:

A.
always local;

B.
always global;

C.
fixed multi-scale pyramid;

D.
agreement-gated scale growth;

E.
mixed local contexts;

F.
global context transition.

Desired:

PERCEPTUAL SCALE
itself becomes:
adaptive developmental state.

The organism should:
compress aggressively
where:
the world is homogeneous

and:
retain fine resolution
where:
causal structure differs.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 20x20
primary_matched_episodes = 500
adaptive_radius2_accuracy = 0.9164
adaptive_radius2_cost = 167.32
