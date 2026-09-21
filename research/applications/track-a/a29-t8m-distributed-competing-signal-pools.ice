TITLE: YGGDRASIL A29 / T8M — Distributed Competing Signal Pools
DATE: 2026-09-21
STATUS: PREREGISTERED DISTRIBUTED-SIGNAL EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8M / APPLICATION-A
PARENT: A28 Distributed Dynamical Uncertainty Regimes
BRANCH: dg1a-ar

PURPOSE

A28 showed that uncertainty represented as population dynamics
can materially alter developmental outcomes.

Its strongest result was the METASTABLE heterogeneous population:
rotating which newborns explored the candidate policy
substantially outperformed fixed exploration.

A29 tests the next architectural step:

remove block-level central evidence from regime control.

Cells emit local pulses into two shared decaying signal pools:

C:
candidate-support signal.

S:
stale/opposition-support signal.

The population's regime emerges from those pools.

No cumulative confidence scalar exists.

BIOLOGICAL MOTIVATION

A29 is inspired by three documented mechanisms:

1. frequency-modulated quorum signaling:
individual state can be encoded in pulse frequency
and integrated by a shared signal pool;

2. positive feedback:
sustained pooled signaling can reinforce commitment
and filter fast fluctuations;

3. cross-inhibition:
opposing committed populations can suppress one another,
with nonlinear inhibition providing a mechanism
for rejecting small opposing minorities
while permitting large opposition to force retreat.

These are design inspirations only.
A29 is a synthetic software experiment.

FROZEN PARENT

A28 closure:

637b044a7f30964febe40ae5660e085e74f68d17.

A29 FREEZE

Let the exact A29 implementation freeze commit be:

F29.

No real A29 trajectory,
local pulse,
pool state,
regime transition,
or scientific result
may be derived before F29 exists.

EXPERIMENTAL WORLD SHAPE

After F29 derive exactly:

384 fresh trajectories:

48 fixed synthetic developmental contexts
x
8 F29-derived replicas.

Each trajectory contains:

40 epochs.

There are:

12 persistent cell identities.

There are:

10 turnover blocks,
each four epochs.

At block start,
exactly four cell identities are replaced.

All trial generation is deterministic
from F29 and YGG-A29 namespaces.

This A29 mechanism harness preserves
the 48-context x 8-replica lineage shape,
but it is a dedicated signal-pool mechanism test
rather than a claim of exact A17 behavioral replay.

LOCAL TRUE CONSEQUENCE

For each cell and epoch,
the synthetic world supplies a local candidate consequence:

-1;
0;
+1.

A candidate-controlled cell receives that consequence.

A stale-controlled cell receives zero candidate consequence.

Total trajectory service delta versus stale
is the sum of realized local candidate consequences
over candidate-controlled living cells.

LOCAL SENSING

Each cell observes its own local consequence
through deterministic bounded sensor noise:

-1;
0;
+1.

The sensed value is clipped to:

-1;
0;
+1.

If sensed value > 0:

emit one C pulse.

If sensed value < 0:

emit one S pulse.

If sensed value == 0:

remain silent.

Thus cells do not emit:

confidence scores;
probabilities;
global votes.

They emit local pulses.

FREQUENCY CODING

A cell may pulse repeatedly across epochs.

Therefore persistent local support
produces a higher pulse frequency
than intermittent support.

The pool integrates pulse frequency naturally.

No separate per-cell strength number is stored.

POOLS

At every epoch:

C_pool =
3/4 * previous C_pool
+
candidate pulses
+
candidate positive-feedback pulses.

S_pool =
3/4 * previous S_pool
+
stale/opposition pulses
+
stale positive-feedback pulses.

Pool arithmetic is exact rational arithmetic.

Both pools decay continuously.

No hidden cumulative confidence variable exists.

POPULATION GATE

A regime transition out of U
requires at least:

6

distinct active emitters
during the current epoch.

This prevents a small number of cells
from forcing population commitment.

REGIMES

U — UNRESOLVED / HETEROGENEOUS

Birth authority:

2 / 4 candidate;
2 / 4 stale.

The two candidate newborn slots
rotate deterministically using a frozen hash ordering.

All six 2-of-4 subsets are permitted.

U explicitly represents uncertainty
as population heterogeneity.

C — CANDIDATE COMMITTED

Birth authority:

3 / 4 candidate;
1 / 4 stale.

Positive-feedback pulse:

a candidate-controlled cell
whose sensed evidence is nonnegative
adds one additional C pulse.

S — STALE COMMITTED

Birth authority:

0 / 4 candidate;
4 / 4 stale.

Positive-feedback pulse:

a stale-controlled cell
whose sensed evidence is nonpositive
adds one additional S pulse.

The learned candidate patch remains preserved.

It is not deleted in S.

U COMMIT RULE

Let:

COMMIT = 20.

Let:

OPPOSITION_CEILING = 8.

U -> C iff all are true:

active emitters >= 6;

C_pool >= 20;

S_pool <= 8;

C_pool >= 2 * S_pool.

U -> S symmetrically iff:

active emitters >= 6;

S_pool >= 20;

C_pool <= 8;

S_pool >= 2 * C_pool.

If neither condition is met:

remain U.

If both pools are elevated or contradictory:

remain U.

Thus contradictory evidence
does not get averaged into one score.

NONLINEAR CROSS-INHIBITION

Let:

K = 12.

Candidate-committed retreat response:

I_S =
S_pool^2
/
(K^2 + S_pool^2).

Stale-committed retreat response:

I_C =
C_pool^2
/
(K^2 + C_pool^2).

C -> U iff:

I_S >= 1/2

AND

at least 4 cells emitted S pulses
during the current epoch.

S -> U symmetrically using I_C
and at least 4 C-pulse emitters.

Because I reaches 1/2 at pool level K=12,
the retreat signal threshold is lower
than the U commitment threshold of 20.

This implements hysteresis.

No direct:

C -> S

or:

S -> C

transition is allowed.

A committed state must retreat through U.

CONTRADICTORY / BET-HEDGING REGIME

A29 does not create a fourth named controller state.

Instead,
irreducible contradiction is represented within U.

Define a CONTRADICTORY epoch diagnostically when:

C_pool >= 12

AND

S_pool >= 12.

During such epochs:

U remains U;

birth authority stays 2 / 4;

rotating heterogeneity continues.

Thus the population maintains optionality
rather than forcing consensus.

REFERENCE CONTROLLERS

R0:
all stale.

R4:
all candidate.

STATIC_C3:
3 / 4 candidate births at every turnover.

BLOCK_SIGN:
a non-pool three-regime comparator.

BLOCK_SIGN starts U.

It uses four-epoch realized service delta,
not signal pools.

Two consecutive positive blocks:
U -> C.

Two consecutive negative blocks:
U -> S.

C retreats to U
after three consecutive negative blocks.

S retreats to U
after three consecutive positive blocks.

Birth authority:

U = rotating 2 / 4;
C = 3 / 4;
S = 0 / 4.

A29 FULL CONTROLLER

POOL_FULL:

two decaying local-signal pools;
frequency-coded pulses;
population gate;
positive-feedback pulses in committed states;
nonlinear cross-inhibition;
rotating heterogeneous U state.

ABLATIONS

NO_FREQ

Each cell may emit at most
one base C or S pulse per four-epoch block.

Committed feedback pulses remain.

This removes local pulse-frequency coding
while preserving pool architecture.

NO_PF

Base pulses and pool decay remain.

No committed-state positive-feedback pulses are emitted.

NO_HET

Identical to POOL_FULL,
except U always assigns candidate control
to newborn slots 0 and 1.

No rotating heterogeneous subset.

PRIMARY METRICS

For STATIC_C3 / BLOCK_SIGN / POOL_FULL / NO_FREQ / NO_PF / NO_HET report:

aggregate trajectory delta versus R0;

beneficial trajectories;
neutral trajectories;
harmful trajectories;

harmful-trajectory rate;

worst cumulative drawdown;

mean and median trajectory delta.

POOL-SPECIFIC METRICS

For POOL_FULL and ablations report:

epoch occupancy in U / C / S;

transition counts:

U -> C;
U -> S;
C -> U;
S -> U;

mean C_pool;
mean S_pool;
max C_pool;
max S_pool;

distinct active emitter distribution;

contradictory epoch count;

fraction of contradictory epochs remaining U;

commitment count;

retreat count;

recommitment count;

false candidate commitment:

trajectory ends C
while total trajectory delta < 0;

false stale commitment:

trajectory ends S
while R4 total candidate delta > 0.

HETEROGENEITY METRICS

For U-state replacements report:

all 2-of-4 subsets exercised;

candidate-policy living-cell count over time;

trajectory outcomes conditioned on
time spent unresolved.

PRIMARY QUALIFICATION

POOL_FULL is SIGNAL-POOL-QUALIFIED iff:

harmful-trajectory rate <= 0.05

AND

aggregate delta versus R0 >= 0

AND

false candidate commitment rate <= 0.05
among trajectories ending C

AND

at least 50% of R4-beneficial trajectories
remain beneficial under POOL_FULL

AND

worst cumulative drawdown
is no worse than STATIC_C3

AND

all integrity probes pass.

A29_SIGNAL_POOL_INFORMATION_GAIN

TRUE iff POOL_FULL:

has lower harmful-trajectory rate than BLOCK_SIGN

AND

has aggregate delta >= BLOCK_SIGN

AND

has fewer false candidate commitments than BLOCK_SIGN

AND

keeps at least 90% of contradictory epochs in U.

This is descriptive only.

It does not authorize autonomous control.

INTEGRITY PROBES

P1:
exactly 384 real trajectories.

P2:
48 contexts x 8 replicas.

P3:
40 epochs per trajectory.

P4:
12 persistent cell identities.

P5:
exactly four replacements per block.

P6:
base cell pulse is only C / S / silent.

P7:
pool decay is exactly 3/4.

P8:
POOL_FULL U birth authority exactly 2 / 4.

P9:
POOL_FULL C birth authority exactly 3 / 4.

P10:
POOL_FULL S birth authority exactly 0 / 4.

P11:
U commitment threshold exactly 20.

P12:
population gate exactly 6 active emitters.

P13:
nonlinear retreat K exactly 12.

P14:
retreat requires at least 4 opposing emitters.

P15:
no direct C <-> S transition.

P16:
contradictory elevated pools cannot commit from U.

P17:
POOL_FULL uses more than one U 2-of-4 subset mechanically.

P18:
NO_HET uses only fixed slots 0 and 1 in U.

P19:
NO_FREQ emits at most one base pulse
per cell per block.

P20:
NO_PF emits zero positive-feedback pulses.

P21:
no cumulative confidence scalar exists.

P22:
regime changes affect future births only.

P23:
candidate patch remains preserved in S.

P24:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
post-result threshold tuning invalid.

N2:
future consequence cannot enter pool state.

N3:
global trajectory delta cannot be emitted as a cell pulse.

N4:
C_pool - S_pool cannot be stored
as a confidence variable.

N5:
contradictory high pools cannot be forcibly collapsed.

N6:
full 4 / 4 candidate authority not permitted
inside POOL_FULL.

N7:
A29 does not claim biological equivalence.

INTERPRETATION

If POOL_FULL improves on BLOCK_SIGN,
local rate-coded pools add information
beyond centralized block-sign dynamics.

If NO_FREQ degrades,
pulse frequency carries useful information.

If NO_PF degrades,
committed-state positive feedback contributes.

If NO_HET degrades,
uncertainty-as-population-diversity remains essential.

If contradictory epochs remain U
without excessive deadlock,
the architecture can represent disagreement
without collapsing it to one number.

If POOL_FULL remains unsafe,
the signal-pool architecture still requires
additional local mechanisms or better signal semantics.

PLAIN-SPEAK QUESTION

Each cell now gets only three things it can say:

"candidate seems better";

"old state seems better";

or:

"I have nothing useful to say."

It says that by pulsing.

Persistent experience produces more pulses.

Everybody's pulses enter two shared pools.

Yggdrasil does not calculate:

"my confidence is 73%."

Instead,
the population physically ends up in one of three conditions:

uncertain and mixed;

mostly committed to the candidate;

or committed back to the old state.

If both sides are strongly signaling,
the population stays mixed
instead of pretending the disagreement has disappeared.

A29 asks:

CAN THAT SHARED SIGNAL ECOLOGY
MAKE BETTER DECISIONS
THAN A CENTRAL BLOCK-LEVEL RULE?

And:

DO FREQUENCY CODING,
POSITIVE FEEDBACK,
AND HETEROGENEITY
ACTUALLY CONTRIBUTE,
OR ARE THEY JUST BIOLOGICAL DECORATION?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A29 DISTRIBUTED COMPETING SIGNAL POOLS

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F29-DERIVED TRAJECTORY,
LOCAL PULSE,
POOL STATE,
REGIME TRANSITION,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

a64c827ca0ec4f689c4c947abb02d81d9191dd45.

SOURCE BUNDLE

Loader:

research/applications/track-a/a29_t8m_distributed_signal_pools_v1.py

Loader Git blob:

a75928ba13428483193e2cbc4f0b2743628be0a8.

Payload:

research/applications/track-a/a29_t8m_distributed_signal_pools_v1.py.gz

Payload Git blob:

64a7af0b9fd3161132c90337ed33811ba09db55d.

Decompressed source SHA-256:

4736c3b525be005db46dba17122a6e772da0297919fae95bb28546149c3fe94c.

Decompressed source bytes:

12162.

Deterministic gzip SHA-256:

331e5f931b2a5be7aa89ce1b3756a8e5ee566284fcf57a0031dd7bf86a67f2c3.

Compressed payload bytes:

3837.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F29-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized semantic output SHA-256:

f094d774bab369adaa99086f03d7ab4041a9d77d209c31272d80df7e983b492e.

All P1-P24 implementation / integrity probes:

PASS.

MECHANICAL STATIC_C3

aggregate delta versus stale:

+5680.

harmful trajectories:

164 / 384;
42.71%.

worst cumulative drawdown:

-288.

MECHANICAL BLOCK_SIGN

aggregate delta:

+10734.

harmful:

195 / 384;
50.78%.

worst drawdown:

-132.

MECHANICAL POOL_FULL

aggregate delta:

+13940.

beneficial:

198.

neutral:

4.

harmful:

182 / 384;
47.40%.

worst drawdown:

-70.

end regimes:

C = 159;
S = 131;
U = 94.

commits:

693.

retreats:

403.

recommits:

310.

false candidate commitments:

10.

false stale commitments:

13.

contradictory epochs:

1723.

fraction of contradictory epochs remaining U:

0.7661056297.

POOL_FULL SIGNAL_POOL_INFORMATION_GAIN:

FALSE

in this mechanical fake world.

POOL_FULL qualified:

FALSE.

MECHANICAL NO_FREQ

aggregate delta:

+3903.

harmful:

163 / 384;
42.45%.

commits:

0.

The no-frequency arm never crossed commitment conditions.

This demonstrates that repeated local pulsing
materially changes pool dynamics.

MECHANICAL NO_PF

aggregate delta:

+13956.

harmful:

182 / 384;
47.40%.

false candidate commitments:

19

versus POOL_FULL:

10.

Positive feedback altered commitment quality
without making the fake world safe.

MECHANICAL NO_HET

aggregate delta:

+13866.

harmful:

180 / 384;
46.88%.

Only fixed U subset:

slots 0 and 1.

No ablation mechanically demonstrates
a safe controller.

This is NON-SCIENTIFIC mechanical evidence only.

REAL A29 STATUS

No real F29-derived trajectory exists.

No real local pulse has been observed.

No real signal-pool outcome has been observed.

No real A29 manifest exists.

Let the resulting commit SHA be:

F29.

After F29 exists:

1. derive exactly 384 fresh trial identities from F29;
2. bind the complete manifest SHA;
3. only then execute two complete deterministic primary sweeps using F29 as seed;
4. require byte-identical output;
5. report POOL_FULL and every preregistered comparator without post-result tuning.

NO SIGNAL THRESHOLD CHANGE.
NO DECAY CHANGE.
NO POPULATION-GATE CHANGE.
NO INHIBITION CHANGE.
NO HETEROGENEITY CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A29 DISTRIBUTED COMPETING SIGNAL POOLS

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A29 LOCAL PULSE,
POOL UPDATE,
REGIME TRANSITION,
OR SCIENTIFIC OUTCOME.

F29:

d3647d6860626113ba6b3e5b042b47091925d7e1.

FROZEN SOURCE SHA-256:

4736c3b525be005db46dba17122a6e772da0297919fae95bb28546149c3fe94c.

TRIAL COUNT:

384.

STRUCTURE:

48 fixed synthetic developmental contexts
x
8 F29-derived replicas.

EPOCHS PER TRAJECTORY:

40.

CELL IDENTITIES:

12.

COMPLETE TRIAL-MANIFEST SHA-256:

9c04f4611117978bbffb8089c6a5edadef462e2b6d331212507f3506b7bb4f16.

Serialized manifest-wrapper bytes:

40338.

Each trial identity is:

SHA256(
YGG-A29
|
F29
|
context
|
replica
).

PRIMARY STATUS AT MANIFEST BIND

Real local pulses observed:

0.

Real C_pool / S_pool states observed:

0.

Real POOL_FULL transitions observed:

0.

Real comparator outcomes observed:

0.

The next permitted operation is:

two complete deterministic A29 primary sweeps
using F29 as the experimental seed.

NO TRIAL REDRAW.
NO POOL-RULE CHANGE.
NO COMMIT-THRESHOLD CHANGE.
NO RETREAT-RULE CHANGE.
NO ABLATION CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
