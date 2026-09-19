TITLE: DG-1A-AR-S9 — Online Control Trust / Retirement Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE STABILITY-PLASTICITY CONTROL-TRUST AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
SERIES_NOTE: SUPPLEMENTAL AR-S SERIES — CANONICAL R4 AR-U NUMBERING PRESERVED
BRANCH: dg1a-ar
PARENT: dg1a-ars8-control-selection-provenance-causal-voi-audit.ice

PURPOSE
S8 established that causal resource credit needs a reference that is simultaneously:
- disturbance-coupled;
- action-decoupled;
- fresh;
- provenance-safe.

S9 asks:

What happens when the local causal topology itself changes?

Can a previously valid control be:
- distrusted;
- retired;
- replaced;

without semantic control labels or permanent source authority?

BOUNDARY
This is synthetic.

It does not:
- prove current Yggdrasil control topology changes in this exact way;
- freeze a control-trust decay constant;
- define a production causal graph;
- authorize permanent reference IDs;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CONTROL SET
Same five unlabeled control candidates as S8.

PRE-SHIFT

R0:
strong disturbance match,
high action contamination.

R1:
balanced reference,
low contamination.

R2:
action-decoupled,
but weak disturbance coupling.

R3:
relay copy of R1.

R4:
stale action-decoupled reference.

The correct pre-shift control is:
R1.

TOPOLOGY CHANGE
At event:
25000

the local causal structure changes.

R1 and its relay copy R3 become strongly action-contaminated:

contamination:
0.08
->
0.65.

At the same time,
R2 matures / relocates into a better disturbance position:

disturbance coupling:
0.45
->
0.70.

R2 remains action-decoupled.

Thus the correct control changes from:

R1
->
R2.

No semantic topology-change label is provided.

OBSERVABLE CALIBRATION
Each stream contains:

70% no-action disturbance-fit observations;

30% randomized signed microprobe observations.

No-action observations update:
disturbance prediction / residual error.

Tagged microprobes update:
action-exposure estimate.

CONTROL SCORE
Because S9 is a high-risk online trust test,
the synthetic selector uses:

score
=
disturbance_RMSE
*
(
1
+
2 * abs(action_exposure)
)

The stronger action-exposure penalty is exploratory.

It is not frozen.

SELECTOR MEMORY COMPARATORS

A.
CUMULATIVE HISTORY

All calibration evidence receives permanent equal weight.

B.
SLOW RECENCY EMA

alpha:
0.004.

C.
MEDIUM EMA

alpha:
0.01.

D.
FAST EMA

alpha:
0.03.

QUESTION
How much history should control trust retain?

Too much:
obsolete causal relationships persist.

Too little:
control identity becomes noisy and unstable.

PRIMARY CONFIRMATION
6 matched seeds.

50000 events per seed.

Shift:
25000.

PRE-SHIFT WINDOW:
events 15000..24999.

EARLY POST-SHIFT:
first 5000 events after shift.

LATE POST-SHIFT:
last 10000 events.

PRIMARY RESULTS

CUMULATIVE HISTORY

correct R1 selection pre-shift:
1.0000

correct R2 early post-shift:
0.0000

correct R2 late:
0.5683

between-seed SD late:
0.3787

Interpretation:
cumulative evidence is extremely stable before the topology change,
but old control authority dominates long after it becomes invalid.

SLOW RECENCY EMA
alpha = 0.004

R1 pre:
0.8993
SD:
0.0601

R2 early:
0.9381
SD:
0.0335

R2 late:
0.9866
SD:
0.0197

This is the best stability/plasticity working point in the tested set.

MEDIUM EMA
alpha = 0.01

R1 pre:
0.7651

R2 early:
0.9129

R2 late:
0.9219

The selector adapts rapidly,
but pre-shift control identity is less stable.

FAST EMA
alpha = 0.03

R1 pre:
0.6091

R2 early:
0.7212

R2 late:
0.7370

Fast forgetting produces substantial control oscillation.

PRIMARY POSITIVE
A modest recency-weighted trust memory can:

retain useful causal-control identity during stable conditions

and

rapidly retire that identity when local causal topology changes.

PRIMARY NEGATIVE
Neither extreme is acceptable.

PERMANENT CUMULATIVE TRUST
causes causal-control hangover.

VERY FAST TRUST
causes noisy control switching.

Thus control trust has the same:

STABILITY
vs
PLASTICITY

tradeoff already observed in:
- fast role adaptation;
- inheritance;
- stale-prior suppression;
- context provenance.

RETIREMENT LATENCY
A separate block audit requires:

R2 selected in >=80% of a 500-event block
for
3 consecutive blocks.

6 matched seeds.

CUMULATIVE HISTORY
stable retirement / promotion latency:

13500
21000
15000
18000
22000
20500

events after topology change.

Median:
19250.

SLOW EMA alpha 0.004

all 6 seeds:
500 events.

Median:
500.

MEDIUM EMA alpha 0.01

1500
500
500
2500
500
500

Median:
500.

FAST EMA alpha 0.03

stable threshold reached in only:
4 / 6

within the tested horizon.

Recovered latencies:

3000
19500
13500
10000

Median among recovered:
11750.

Interpretation:

fast raw reactivity is not equivalent to stable adaptation.

The fast estimator sees the topology change,
but keeps changing its mind.

CONTROL RETIREMENT PRINCIPLE
Control authority should not be permanent.

A causal reference needs reversible trust.

When evidence says:

THIS SOURCE NOW LIES INSIDE MY ACTION FOOTPRINT

or

THIS SOURCE NO LONGER TRACKS THE DISTURBANCE

its causal authority should decay.

This does not require deleting the source.

It requires reducing:
CONTROL EXPRESSION TRUST.

RELATION TO H6
H6 separated:

stored inherited prior

from

whether that prior should currently control phenotype.

S9 suggests the same abstraction for causal controls:

SOURCE EXISTS

is separate from

SOURCE IS CURRENTLY TRUSTED AS A CONTROL.

This is a recurring architecture pattern.

RELATION TO S8 PROVENANCE
Provenance identifies:
where evidence came from.

Trust determines:
whether that provenance is currently causally useful.

Do not collapse:
IDENTITY
and
VALIDITY.

RELATION TO STALE EVIDENCE
A formerly excellent control can become wrong without becoming:
missing
or
noisy.

Its problem may be:
causal topology changed.

Therefore:

FRESH DATA
CAN STILL COME FROM
A STALE CAUSAL RELATIONSHIP.

Freshness and causal validity are separate state variables.

CURRENT CONTROL-TRUST STATE
A local causal-control subsystem now plausibly needs:

SOURCE / PROVENANCE SKETCH

+

DISTURBANCE-FIT HISTORY

+

ACTION-EXPOSURE HISTORY

+

RECENCY

+

CONTROL-TRUST MAGNITUDE

+

RETIREMENT / PROMOTION HYSTERESIS.

The last item is motivated by the fast-EMA oscillation.

ARCHITECTURAL CONSEQUENCE
Preferred qualitative control lifecycle:

NEW SOURCE

->
UNCERTAIN CONTROL STATUS

->
CALIBRATION

->
TRUSTED CONTROL

->
SURPRISE / ACTION-EXPOSURE RISE

->
RAPID TRUST SUPPRESSION

->
PERSISTENT INVALIDITY

->
RETIREMENT.

A retired control may later become valid again.

Therefore retirement should normally mean:

NO CURRENT CAUSAL AUTHORITY

not:

DESTROY SOURCE FOREVER.

DECISION
AR-S9 is POSITIVE.

Supported synthetically:

- causal-control validity can change over time;
- cumulative trust can preserve obsolete control authority for very long periods;
- recency-weighted trust can rapidly promote a newly valid control;
- excessive forgetting causes unstable control identity;
- control trust therefore needs its own stability/plasticity timescale;
- control identity and current validity should be represented separately.

Not demonstrated:

- real Yggdrasil online control retirement;
- optimal forgetting rate;
- optimal hysteresis;
- spatially overlapping causal-control sets;
- control revival after topology reversion;
- control selection under simultaneous source birth/death and budget pressure.

NEXT SCIENTIFIC MOVE
The resource-credit lane has now reached a coherent local architecture:

S4:
evidence is a finite resource.

S5:
evidence should be allocated by value,
not uncertainty alone.

S6:
local value can be learned,
but learned resource economics become stale and confounded.

S7:
resource credit needs causal disturbance control.

S8:
control selection needs disturbance fit + action decoupling + provenance.

S9:
control trust must itself be reversible and recency-sensitive.

A useful next cross-lane experiment is:

AR-H8 — STRUCTURAL GROWTH / PRUNING UNDER A HARD PERMANENT MEMORY BUDGET

Question:

Can the organism decide when one additional slow representational degree of freedom is worth its permanent resource cost?

This directly connects:

H7
bounded inherited manifold capacity

with

S4-S9
adaptive resource economics and causal value-of-information.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_matched_seeds = 6
stream_events_per_seed = 50000
topology_shift_event = 25000
retirement_block_size = 500
