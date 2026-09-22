TITLE: YGGDRASIL A37 / T8U — Lineage-Persistent Uncertainty Memory
DATE: 2026-09-21
STATUS: PREREGISTERED LINEAGE-MEMORY EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8U / APPLICATION-A
PARENT: A36 Spatially Cooperative Protected Hedge Niches
BRANCH: dg1a-ar

PURPOSE

A36 proved that uncertainty can form larger,
longer-lived spatial H niches.

But those niches barely changed
the persistent FAMILY-5 oscillatory attractor.

The strongest interpretation is:

spatial coherence alone is insufficient.

A protected uncertainty state may need to persist
through developmental succession,
not merely through adjacency.

A37 therefore tests:

LINEAGE-PERSISTENT UNCERTAINTY MEMORY.

The experiment does NOT:

increase H entry gain globally;

increase H neighborhood radius;

extend all H lifetimes;

or add a centralized uncertainty score.

Instead,
fixed developmental turnover events replace cells.

The question is whether a successor should receive
bounded information that its lineage recently occupied H.

FROZEN PARENT

A36 closure:

fc1e79598729a1cb755759ab5e668c58ab23c0ec.

A36 primary result:

D2_NICHE:

oscillation:
13.54%.

paired FAMILY-5 oscillators broken:
2 / 34.

D3_NICHE:

oscillation:
13.28%.

paired FAMILY-5 oscillators broken:
0 / 30.

Spatial H coherence increased strongly,
but target oscillators remained.

PARENT MECHANISM CARRIED FORWARD

A37 uses the full A36 NICHE mechanism for both:

D2;
D3.

Frozen parent constants:

population:
48 cells.

epochs:
48.

initial states:
12 C;
12 S;
24 U.

pool decay:
3/4.

local cross-inhibition:
R = 12;
n = 3;
K = 1/2.

recruitment radius:
3.

ETA:
1/2.

pool normalization:
160.

A34 C/S suppression:
K_SUPP = 1/2;
N_SUPP = 3.

pool/local weights:
3/4;
1/4.

A35 base H entry:
ETA * SUP_C * SUP_S.

A35 base H release:
ETA * (1 - min(SUP_C,SUP_S)).

A36 H neighborhood radius:
3.

A36 H entry reinforcement:
1 + H_local.

A36 H release protection:
1 - H_local.

Refractory durations:

D2;
D3.

A37 FREEZE

Let the exact A37 implementation freeze commit be:

F37.

No real A37 world,
turnover,
lineage inheritance event,
or scientific outcome
may be derived before F37 exists.

WORLD SHAPE

384 fresh post-F37 trials:

48 contexts
x
8 replicas.

48 cells.

48 epochs.

Environmental families remain structurally identical to A36:

0 stable C advantage;
1 stable S advantage;
2 spatial contradiction;
3 reversal C -> S;
4 reversal S -> C;
5 transient / oscillatory uncertainty.

DEVELOPMENTAL TURNOVER

A37 adds fixed cell replacement events at epochs:

8;
12;
16;
20;
24;
28;
32;
36;
40;
44.

Exactly:

6

ring positions are replaced at every turnover.

For each trial,
derive one F37-bound permutation
of the 48 ring positions.

Partition it into eight groups of six.

Turnover groups are used in order:

G0 at epoch 8;
G1 at 12;
G2 at 16;
G3 at 20;
G4 at 24;
G5 at 28;
G6 at 32;
G7 at 36;
G0 at 40;
G1 at 44.

Thus every position is replaced once
by epoch 36,
with two groups experiencing a second replacement.

The exact permutation is bound
in the post-F37 world manifest.

SUCCESSOR IDENTITY

A replacement creates a new generation
at the same ring position.

Generation number increments by one.

Future stochastic draws include:

position;
generation;
epoch;
decision namespace.

All arms receive
the identical turnover schedule
and generation identities.

MATCHED STATE CONTINUITY

To isolate uncertainty-lineage memory:

for parent states:

C;
S;
U;
FC;
FS

the successor inherits:

the same operational state;

and the same remaining refractory timer
for FC / FS.

Thus turnover itself does not erase
ordinary operational state.

Only H lineage handling differs by arm.

H HISTORY TRACKING

Every position has a generation-local boolean:

H_BEQUEST.

At the start of a new generation:

H_BEQUEST = false.

If that generation enters H
at least once:

H_BEQUEST = true

for the remainder of that generation.

The bequest is external lineage state.

It does NOT alter
the current generation's behavior.

It matters only at successor creation.

Therefore A37 does not reward a cell
for its own previous H state.

It tests information crossing
the parent -> successor boundary.

ARMS

For both D2 and D3:

STATIC

Exact A36 NICHE behavior.

No turnover is applied.

This is the no-succession reference.

RESET

Turnover occurs.

If parent state is H:

successor starts U.

No H lineage information is inherited.

Any parent H_BEQUEST is discarded.

This tests developmental forgetting.

DIRECT

Turnover occurs.

If parent state is H:

successor starts H.

If parent is not currently H:

successor receives no H information.

H_BEQUEST is ignored.

This tests direct phenotype continuity
without historical lineage memory.

PRIME

Turnover occurs.

Every successor starts
with the parent's operational state rule
except:

parent H -> successor U.

The successor may receive
one lineage-memory bit:

M_H = parent H_BEQUEST.

Thus a lineage that entered H
at any time during its generation
can prime its successor
even if the parent is no longer H
at replacement.

LINEAGE PRIME EFFECT

M_H affects only a successor
while it is in U.

For M_H = 1:

lambda_H
=
A36 lambda_H
*
2.

For M_H = 0:

lambda_H
=
A36 lambda_H.

No other transition changes.

M_H does NOT:

change C hazard;

change S hazard;

change H release;

change local inhibition;

change pulse emission;

or alter refractory timing.

ONE-GENERATION EXPIRY

M_H is valid only
for the current successor generation.

At that successor's next turnover:

the mark does NOT automatically persist.

The next successor receives M_H = 1
only if the current generation itself
entered H and therefore set:

H_BEQUEST = true.

Thus uncertainty lineage memory is:

inherited;
bounded;
and self-refreshing only through renewed H experience.

This prevents permanent lineage lock.

NO DIRECT H IN PRIME

PRIME does NOT copy H phenotype directly.

Parent H:

successor begins U;

M_H = 1.

The successor must still enter H
through its own stochastic hazard.

This distinguishes:

historical lineage priming

from:

direct phenotype copying.

PRIMARY ARMS

D2_STATIC.
D2_RESET.
D2_DIRECT.
D2_PRIME.

D3_STATIC.
D3_RESET.
D3_DIRECT.
D3_PRIME.

Exactly eight arms.

PRIMARY LINEAGE METRICS

Report:

turnover count;

replacement count;

H parent replacement count;

H_BEQUEST parent replacement count;

direct H successor count;

primed successor count;

primed successor U -> H count;

unprimed successor U -> H count;

per-eligible-cell H-entry rate
for primed successors;

same for unprimed successors;

prime effect ratio.

LINEAGE CHAIN METRICS

For each ring position,
track consecutive generations
whose parent passed H_BEQUEST.

Report:

mean nonzero chain length;

median;

maximum;

chains >= 2 generations;

chains >= 3 generations.

Also report:

fraction of lineages
ever carrying M_H.

These metrics are measurement only.

They do not affect transitions.

POST-TURNOVER RECONSTITUTION

For turnover events
whose parent carried H_BEQUEST,
report:

time from replacement
to successor's first H entry.

For DIRECT:

if successor begins H,
latency = 0.

For RESET / PRIME:

measure actual later H entry.

If no H entry before next turnover
or trial end:

NEVER.

This quantifies whether lineage memory
reconstitutes uncertainty
without direct phenotype copying.

FAMILY-5 RETEST

For RESET / DIRECT / PRIME
against the matched STATIC duration reference report:

STATIC FAMILY-5 oscillators;

broken oscillators;

new oscillators;

remaining oscillators.

Also report
the same comparisons:

PRIME versus RESET;

PRIME versus DIRECT.

PRIMARY POPULATION METRICS

For every arm report:

aggregate service;

beneficial / neutral / harmful;

harm rate;

oscillatory fraction;

contradiction no-majority fraction;

false C dominance;

false S dominance;

reversal acquisition;

directional coordination;

H occupancy;

contradiction H cluster prevalence;

niche lifetime.

PRIMARY QUALIFICATION

D2_PRIME or D3_PRIME
is LINEAGE-MEMORY-QUALIFIED iff all are true:

1. oscillatory fraction <= 0.05;

2. oscillatory fraction < matched RESET;

3. at least 50%
   of matched RESET FAMILY-5 oscillators
   are broken;

4. contradiction no-majority fraction >= 0.90;

5. prime effect ratio >= 1.5;

6. at least 50% of primed successor generations
   eventually re-enter H;

7. false C dominance <= 0.05
   among S-favoring worlds;

8. false S dominance <= 0.05
   among C-favoring worlds;

9. reversal acquisition >= 0.80;

10. aggregate service
    >= 90%
    of matched RESET;

11. all integrity probes pass.

A37_LINEAGE_MEMORY_INFORMATION_GAIN

TRUE iff at least one PRIME arm:

reduces oscillation versus RESET;

breaks at least 25%
of RESET FAMILY-5 oscillators;

outperforms DIRECT
on at least one of:

oscillation;
FAMILY-5 oscillator breaking;
contradiction no-majority;

has prime effect ratio >= 1.5;

retains reversal acquisition >= 0.80;

and retains >= 90% RESET service.

This is descriptive only.

No production lineage-memory mechanism
is selected.

MECHANISM ATTRIBUTION

If DIRECT helps but PRIME does not:

current phenotype continuity matters,
not historical lineage memory.

If PRIME helps but DIRECT does not:

history of uncertainty matters
even after the parent has left H.

If both help:

developmental continuity broadly matters.

If RESET degrades but STATIC / DIRECT / PRIME are similar:

turnover erases useful uncertainty,
but inherited history adds little beyond state continuity.

If all turnover arms remain equivalent:

lineage is not the missing dimension.

INTEGRITY PROBES

P1:
384 trials.

P2:
48 contexts x 8 replicas.

P3:
48 cells.

P4:
48 epochs.

P5:
initial C/S/U = 12/12/24.

P6:
A36 pulse ecology unchanged.

P7:
pool decay = 3/4.

P8:
A30 inhibition R/n/K = 12/3/1/2.

P9:
A33 recruitment radius = 3.

P10:
ETA = 1/2.

P11:
pool normalization = 160.

P12:
A34 suppression K/n = 1/2 / 3.

P13:
pool/local weights = 75/25.

P14:
A36 H radius = 3.

P15:
A36 entry / release niche modifiers unchanged.

P16:
D2 refractory = 2.

P17:
D3 refractory = 3.

P18:
turnover epochs exactly:
8/12/16/20/24/28/32/36/40/44.

P19:
six replacements per turnover.

P20:
each trial uses one F37-bound 48-position permutation.

P21:
all arms use same trial turnover schedule.

P22:
C/S/U state continuity exact across turnover.

P23:
FC/FS state and timer continuity exact.

P24:
RESET parent H -> successor U.

P25:
DIRECT parent H -> successor H.

P26:
PRIME parent H -> successor U.

P27:
H_BEQUEST set only by actual H entry
within parent generation.

P28:
M_H inherited only from parent H_BEQUEST.

P29:
M_H multiplier exactly 2
on H entry hazard only.

P30:
M_H expires at next turnover
unless refreshed by successor H entry.

P31:
M_H does not affect H release.

P32:
no future environment enters lineage state.

P33:
no centralized confidence scalar exists.

P34:
two complete primary sweeps byte-identical.

NEGATIVE / LIMIT CONTROLS

N1:
STATIC no-turnover reference.

N2:
RESET developmental forgetting.

N3:
DIRECT phenotype-copy control.

N4:
post-result prime multiplier tuning invalid.

N5:
post-result turnover frequency tuning invalid.

N6:
post-result turnover-size tuning invalid.

N7:
changing A36 niche mechanics invalid.

INTERPRETATION

A37 is not asking:

"should H last longer?"

It asks:

"should evidence that a lineage repeatedly needed H
change how its successor behaves?"

The parent can be gone.

The successor can begin unresolved.

But the successor may inherit one bounded fact:

"my lineage recently encountered
enough contradiction to hedge."

If that changes the persistent oscillator family,
uncertainty has acquired developmental memory.

If it does not,
then neither isolated H,
spatial H cooperation,
nor one-generation lineage priming
is sufficient.

PLAIN-SPEAK QUESTION

A36 let uncertain cells
form neighborhoods.

But when a cell is replaced,
the new cell has no idea
what its predecessor went through.

A37 tests a small inheritance mechanism.

A cell that had to hedge
can leave one bit for its successor:

"our lineage recently found this situation unresolved."

The successor is NOT forced to stay uncertain.

It starts unresolved
and must make its own decision.

But for one generation,
it is easier for that lineage
to return to the protected H state
if contradiction continues.

If the successor never needs H,
the inherited mark dies out.

So the question is:

CAN UNCERTAINTY BECOME MORE STABLE
WHEN EXPERIENCE SURVIVES
FROM PARENT TO SUCCESSOR?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
