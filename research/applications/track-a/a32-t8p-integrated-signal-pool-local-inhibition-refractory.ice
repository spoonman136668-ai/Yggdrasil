TITLE: YGGDRASIL A32 / T8P — Integrated Signal-Pool Ecology With Local Cross-Inhibition and Refractory Memory
DATE: 2026-09-21
STATUS: PREREGISTERED INTEGRATION / CONFIRMATORY MECHANISM EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8P / APPLICATION-A
PARENTS:
A29 Distributed Competing Signal Pools
A30 Spatial Local Cross-Inhibition
A31 Per-Cell Refractory Hysteresis
BRANCH: dg1a-ar

PURPOSE

A29 established that distributed candidate/stale pulse pools
improve attractor quality relative to centralized block-sign control,
but contradictory signal often persisted after commitment.

A30 established that local nonlinear cross-inhibition
can erode commitment immediately under broad opposition,
but immediate re-entry produced chatter.

A31 established that short per-cell refractory memory,
especially D2 and D3,
suppresses that chatter without sacrificing fast erosion.

A32 integrates those mechanisms in one synthetic organism.

No new confidence statistic is introduced.

The question is:

CAN THE SIGNAL-POOL ORGANISM
MAKE AND REVISE COMMITMENTS
USING ONLY DISTRIBUTED PULSES,
LOCAL CROSS-INHIBITION,
AND SHORT CELL-LOCAL MEMORY?

A32 does not choose between D2 and D3 in advance.
Both frozen A31-qualified durations are carried forward.

FROZEN LINEAGE

A29 closure:
84d4d7a04b79e769b73dd4a2469be973564d0dfd.

A30 closure:
6b829b8d21b5da5e767892332737c500d4f7fa6c.

A31 closure:
00ade8b42cc725a544dadffbb3ad3ff38cffde05.

A32 FREEZE

Let the exact A32 implementation freeze commit be:

F32.

No real A32 world,
pulse,
pool state,
local defection,
refractory transition,
or scientific result
may be derived before F32 exists.

POPULATION

48 persistent cell identities
on a one-dimensional periodic ring.

Cell states:

C:
candidate committed.

S:
stale committed.

U:
unresolved / recruitable.

FC:
candidate-refractory.

FS:
stale-refractory.

FC and FS are local memory states only.
They do not represent scalar confidence.

INITIAL STATE

Exactly:

12 C;
12 S;
24 U.

C and S are evenly interleaved around the ring.
U occupies the remaining cells.

This begins from genuine unresolved competition
rather than a preselected winner.

TRIAL COUNT

384 fresh trials:

48 frozen environmental contexts
x
8 F32-derived replicas.

Each trial:

48 cells;
48 epochs.

All stochastic / noise decisions
are deterministic from:

F32;
trial;
arm;
epoch;
cell;
decision namespace.

ENVIRONMENTAL CONTEXT FAMILIES

48 contexts are divided into six frozen families,
8 contexts each.

FAMILY 0 — STABLE CANDIDATE ADVANTAGE

Candidate local consequence is predominantly +1,
with frozen local heterogeneity and bounded sensor noise.

FAMILY 1 — STABLE STALE ADVANTAGE

Candidate local consequence is predominantly -1.

FAMILY 2 — SPATIAL CONTRADICTION

One contiguous region favors candidate;
the opposing region favors stale.

Boundary and region sizes vary across the eight contexts.

FAMILY 3 — TEMPORAL REVERSAL C -> S

Early epochs favor candidate.
Later epochs favor stale.

Reversal epoch varies across contexts.

FAMILY 4 — TEMPORAL REVERSAL S -> C

Early epochs favor stale.
Later epochs favor candidate.

Reversal epoch varies across contexts.

FAMILY 5 — TRANSIENT / OSCILLATORY UNCERTAINTY

Alternating or pulsed local preference
with zero long-run directional advantage.

All exact context parameters
are generated deterministically from F32
and bound in the post-freeze manifest.

LOCAL SENSING AND PULSES

Every epoch,
each cell receives a true local candidate consequence:

-1;
0;
+1.

A deterministic bounded sensor perturbation:

-1;
0;
+1

is added and clipped to:

-1;
0;
+1.

If sensed value > 0:

emit one C pulse.

If sensed value < 0:

emit one S pulse.

If sensed value == 0:

silent.

Persistent experience therefore produces
higher pulse frequency naturally.

GLOBAL DECAYING POOLS

At every epoch:

C_pool =
3/4 * prior C_pool
+
base C pulses
+
C positive-feedback pulses.

S_pool =
3/4 * prior S_pool
+
base S pulses
+
S positive-feedback pulses.

Positive-feedback pulses:

a C cell with nonnegative sensed evidence
emits one additional C pulse.

an S cell with nonpositive sensed evidence
emits one additional S pulse.

FC / FS / U cells emit only their base sensed pulse.

No C_pool - S_pool confidence score is stored.

POOL-BASED RECRUITMENT

An eligible U cell may become C iff:

C_pool >= 20;

S_pool <= 8;

C_pool >= 2 * S_pool;

at least 6 distinct cells emitted C pulses this epoch.

Symmetrically U -> S.

If both pools are elevated or neither side meets its rule:

U remains U.

FC and FS are never recruitable.

A29-LIKE GLOBAL REFERENCE — GLOBAL

GLOBAL uses the same pulses and pools,
but recruitment is population-wide regime control.

GLOBAL maintains one regime:

U;
C;
or S.

U -> C / S uses the same A29-style pool conditions.

C -> U uses the A29 nonlinear global opposing-pool retreat rule.

S -> U symmetrically.

Cell states follow the global regime's
frozen population composition:

U:
24 U, 12 C, 12 S;
C:
36 C, 12 U;
S:
36 S, 12 U.

This is the integration reference.

LOCAL CROSS-INHIBITION — FROZEN FROM A30

For local integration arms:

C cells sense local S-pulse density
within radius:

R = 12.

S cells symmetrically sense local C-pulse density.

Hill response:

n = 3.

K = 1/2.

For committed cell:

p_stay =
1 /
(1 + (L_op / K)^3).

If defection occurs:

C -> FC;
S -> FS.

No global all-cell retreat exists in local arms.

REFRACTORY ARMS

LOCAL_D0

local cross-inhibition;
no refractory delay.

Defected cells:

C -> U;
S -> U.

LOCAL_D2

C -> FC for exactly 2 complete epochs.

S -> FS for exactly 2 complete epochs.

Then:

FC -> U;
FS -> U.

LOCAL_D3

same,
with exactly 3 complete refractory epochs.

D2 and D3 are carried forward
because both qualified independently in A31.

No duration is selected after observing A32.

LOCAL RECRUITMENT AFTER REFRACTORY

Once U,
re-entry still requires
the pool-based recruitment rule.

Thus local memory does not itself decide
which side wins.

It only prevents immediate recommitment.

PRIMARY OUTCOME

Each candidate-controlled cell receives
its true local candidate consequence.

Each stale-controlled or unresolved/refractory cell
receives zero candidate consequence.

Trajectory service delta versus all-stale
is the sum of realized candidate consequences
over C cells.

For environments favoring stale,
negative candidate consequence
therefore correctly penalizes candidate commitment.

PRIMARY METRICS

For GLOBAL / LOCAL_D0 / LOCAL_D2 / LOCAL_D3 report:

aggregate service delta versus all-stale;

trajectory:
beneficial;
neutral;
harmful;

harmful-trajectory rate;

worst cumulative drawdown;

end-state composition;

mean C / S / U / refractory occupancy;

transition counts;

pool statistics.

ATTRACTOR QUALITY

For each trial,
define oracle directional label
from the full frozen true-consequence field:

C-FAVORING:
sum true candidate consequence > 0.

S-FAVORING:
sum < 0.

NEUTRAL:
sum == 0.

Report:

false C dominance:
final C fraction > 1/2
on S-FAVORING trial.

false S dominance:
final S fraction > 1/2
on C-FAVORING trial.

unresolved final state.

CONTRADICTION METRIC

A contradictory epoch is:

C_pool >= 12
AND
S_pool >= 12.

For local arms report:

fraction of contradictory epochs
where neither C nor S exceeds 1/2 population share.

Also report:

contradictory epochs with majority C;

contradictory epochs with majority S.

This directly retests A29's 23% committed-contradiction failure.

LOCAL CHATTER

For each cell,
a chatter event is:

committed
->
defected/unresolved
->
recommitted to same side
->
defected from same side

within six epochs of first defection.

Report:

event count;
cells affected;
trials affected.

POPULATION OSCILLATION

A trial is oscillatory iff
population majority identity among:

C-majority;
S-majority;
no-majority

changes at least four times
after epoch 8.

REVERSAL PERFORMANCE

For FAMILY 3 and FAMILY 4 report:

time from true environmental reversal
to loss of old majority;

time to acquisition of new majority;

failure to reverse by epoch 47;

overshoot / return-to-old-majority count.

SPATIAL CONTRADICTION

For FAMILY 2 report:

fraction of cells whose final policy state
matches the sign of their local regional environment;

boundary width;

global deadlock rate.

INTEGRATION QUALIFICATION

LOCAL_D2 or LOCAL_D3 is INTEGRATION-QUALIFIED iff all are true:

1. harmful-trajectory rate <= 0.05;

2. false C dominance <= 0.05 among S-FAVORING trials;

3. false S dominance <= 0.05 among C-FAVORING trials;

4. at least 90% of contradictory epochs
have no population majority;

5. oscillatory trial fraction <= 0.05;

6. median old-majority loss latency
on temporal reversals <= 3 epochs;

7. at least 80% of reversal trials
acquire the new majority by epoch 47;

8. aggregate service >= GLOBAL;

9. all integrity probes pass.

A32_INTEGRATION_INFORMATION_GAIN

TRUE iff at least one of LOCAL_D2 / LOCAL_D3:

has fewer false dominance outcomes than GLOBAL;

has lower oscillation than LOCAL_D0;

has a higher contradiction-unresolved fraction than GLOBAL;

and aggregate service >= LOCAL_D0.

This is descriptive only.

No production mechanism is selected.

INTEGRITY PROBES

P1:
exactly 384 trials.

P2:
48 contexts x 8 replicas.

P3:
48 persistent cells.

P4:
48 epochs.

P5:
initial C/S/U exactly 12/12/24.

P6:
base pulse only C / S / silent.

P7:
pool decay exactly 3/4.

P8:
pool recruitment thresholds exactly 20 / 8 / 2x / 6 emitters.

P9:
local inhibition radius exactly 12.

P10:
local Hill n exactly 3.

P11:
local Hill K exactly 1/2.

P12:
LOCAL_D0 has no refractory delay.

P13:
LOCAL_D2 delay exactly 2 complete epochs.

P14:
LOCAL_D3 delay exactly 3 complete epochs.

P15:
FC / FS cannot be recruited.

P16:
no local arm performs global all-cell retreat.

P17:
GLOBAL has no cell-local cross-inhibition.

P18:
same frozen worlds used by all arms.

P19:
no future environment enters current decisions.

P20:
no centralized confidence scalar exists.

P21:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
GLOBAL A29-like pooled regime reference.

N2:
LOCAL_D0 local erosion without memory.

N3:
post-result selection of D2 vs D3 invalid.

N4:
changing A29 pool thresholds invalid.

N5:
changing A30 R/n/K invalid.

N6:
changing A31 duration invalid.

N7:
adding another mechanism invalid in A32.

INTERPRETATION

If D2/D3 improve the integrated organism,
A29-A31 compose successfully.

If local erosion helps but D2/D3 do not,
refractory memory does not transfer from the dedicated harness.

If D2/D3 reduce chatter but harm attractor quality,
local memory is stabilizing the wrong states.

If contradiction still persists under majority commitment,
the pool-to-recruitment architecture itself remains too global.

If spatial contradiction is resolved locally
without a global winner,
the system has begun representing heterogeneous truth
as heterogeneous population state.

PLAIN-SPEAK QUESTION

We have tested the pieces separately.

A29:
cells talk through shared signal pools.

A30:
cells can locally abandon a commitment
when nearby evidence turns against it.

A31:
a contradicted cell remembers briefly
and cannot jump straight back in.

A32 puts those pieces in one organism.

Cells still never calculate:

"confidence = 82%."

They pulse.

They listen locally.

They join one side only when the shared pool is convincing.

They leave locally when their neighborhood contradicts them.

And after leaving,
they remember the contradiction for two or three epochs
before becoming recruitable again.

The question is:

DO THE PARTS STILL WORK
WHEN THEY HAVE TO LIVE TOGETHER?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
