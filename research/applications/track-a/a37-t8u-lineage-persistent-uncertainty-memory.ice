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


PRE-IMPLEMENTATION CLARIFICATION 01 — TURNOVER ORDER AND GENERATION IDENTITY

DATE:
2026-09-21.

STATUS:
BOUND BEFORE IMPLEMENTATION FREEZE
AND BEFORE ANY REAL F37-DERIVED WORLD EXISTS.

TURNOVER ORDER

At turnover epoch t:

replacement occurs first.

The parent state,
parent refractory timer,
parent H_BEQUEST,
and parent lineage generation
are read from the end of epoch t-1.

The successor is created.

Only then does epoch t perform:

sensing;
pulse emission;
pool update;
H release;
local cross-inhibition;
recruitment;
service accounting.

Thus:

epoch 8 turnover
inherits history accumulated through epochs 0-7.

DIRECT H DWELL

If DIRECT replaces a parent currently in H:

the parent H dwell closes at turnover.

The successor begins a new H dwell
at epoch t.

That successor does not automatically set H_BEQUEST.

H_BEQUEST is set only
when the current generation actually enters H
through its own U -> H transition.

PRIME ORDER

If PRIME receives M_H = 1:

the successor begins in U
unless ordinary state continuity applies
to a non-H parent.

The mark can affect
that successor's H hazard
starting in the same turnover epoch's
recruitment phase.

GENERATION-LOCAL STOCHASTIC IDENTITY

Every replacement increments
the position's generation number.

All post-turnover stochastic decisions
include that generation number.

Matched arms use
the exact same turnover schedule
and generation numbers.

Therefore changing H lineage handling
does not silently reuse
the parent's stochastic stream.

No scientific threshold,
turnover frequency,
turnover size,
lineage multiplier,
or qualification rule changes.

No F37 exists yet.


PRE-RUN IMPLEMENTATION FREEZE 01 — A37 LINEAGE-PERSISTENT UNCERTAINTY MEMORY

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F37-DERIVED WORLD,
TURNOVER,
LINEAGE INHERITANCE EVENT,
OR SCIENTIFIC OUTCOME.

IMPLEMENTATION COMMIT

77206606a0fc48d107b190a2e71eeca3935b080c.

SOURCE BUNDLE

Loader:

research/applications/track-a/a37_t8u_lineage_uncertainty_memory_v1.py

Loader Git blob:

6c3dd5cffdeaabaa7a3e946f29dcc8d8e1d9590a.

Encoded payload:

research/applications/track-a/a37_t8u_lineage_uncertainty_memory_v1.py.gz.b64

Encoded payload Git blob:

0e6de0300506e43ccdaff818dde0ed9ba597d8f3.

Decompressed source SHA-256:

3e69f508489181c989c79d1d7c72f83a751fe457e726c520785b126e0a095de6.

Decompressed source bytes:

28732.

Deterministic gzip SHA-256:

b44c96bd5f4f80f481a323dd5b1162bd8d066c68da9a8b2beae6610f0b202d3a.

Compressed payload bytes:

8082.

Base64 payload characters:

10776.

PACKAGING NOTE

A37 stores the deterministic gzip
as base64 UTF-8 text.

The loader:

base64-decodes;
gzip-decompresses;
SHA-256 verifies;
then executes the exact frozen source.

This avoids the binary truncation defect
previously observed in repository gzip handling.

It changes no scientific behavior.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake seed:

MECHANICAL-F37-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized output SHA-256:

5249753143b313ed2116c4fafd5282288479573a4fd2ef59786a88b584622454.

Mechanical world-manifest SHA-256:

a2ff290196d74ac0c1247799add68009501bf805f8639725d63763c2905131ee.

All P1-P34 integrity probes:

PASS.

No PRIME arm mechanically qualified.

No PRIME arm met:

A37_LINEAGE_MEMORY_INFORMATION_GAIN.

MECHANICAL D2 RESET

oscillation:

13.28%.

FAMILY-5 oscillators:

32.

aggregate service:

230582.

reversal acquisition:

95.31%.

MECHANICAL D2 PRIME

oscillation:

13.02%.

FAMILY-5 oscillators:

30.

RESET FAMILY-5 oscillators broken:

2 / 32.

prime effect ratio:

2.8275x.

primed successors:

5291.

primed successor generations re-entering H:

51.79%.

median reconstitution latency:

3 epochs.

contradiction no-majority:

92.17%.

reversal acquisition:

96.88%.

aggregate service:

228890.

Thus inherited lineage memory is:

functional;
bounded;
and behaviorally consequential.

But it mechanically breaks only:

6.25%

of RESET FAMILY-5 oscillators.

MECHANICAL D3 RESET

oscillation:

14.58%.

FAMILY-5 oscillators:

31.

aggregate service:

224557.

MECHANICAL D3 PRIME

oscillation:

13.54%.

FAMILY-5 oscillators:

30.

RESET FAMILY-5 oscillators broken:

2 / 31.

prime effect ratio:

2.9219x.

primed successors:

4737.

primed successor generations re-entering H:

49.31%.

median reconstitution latency:

3 epochs.

contradiction no-majority:

94.81%.

reversal acquisition:

92.97%.

aggregate service:

224117.

DIRECT PHENOTYPE CONTROL

Direct H inheritance
did not mechanically outperform PRIME.

D2 DIRECT oscillation:

15.36%.

D3 DIRECT:

14.06%.

This suggests that
copying the current H phenotype
is not obviously the missing mechanism.

The historical lineage mark
has a distinct measurable effect.

However:

no mechanical arm approached
the frozen 5% oscillation ceiling.

No turnover frequency,
turnover size,
prime multiplier,
H mechanism,
qualification threshold,
or information-gain rule
is changed in response.

This is NON-SCIENTIFIC mechanical evidence only.

REAL A37 STATUS

No real F37-derived world exists.

No real lineage inheritance outcome exists.

No real A37 primary result exists.

Let the resulting commit SHA be:

F37.

After F37 exists:

1. derive exactly 384 fresh worlds from F37;
2. bind the complete world-manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report STATIC / RESET / DIRECT / PRIME
   for both D2 and D3 without post-result selection.

NO POST-RESULT PRIME-MULTIPLIER TUNING.
NO POST-RESULT TURNOVER TUNING.
NO POST-RESULT A36-NICHE CHANGE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A37 LINEAGE-PERSISTENT UNCERTAINTY MEMORY

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A37 ARM EXECUTION,
TURNOVER,
LINEAGE MARK,
OR SCIENTIFIC OUTCOME.

F37:

d7f0ef718c83962dcb2e7fb2c0e57feba4e97bd3.

FROZEN SOURCE SHA-256:

3e69f508489181c989c79d1d7c72f83a751fe457e726c520785b126e0a095de6.

TRIAL COUNT:

384.

STRUCTURE:

48 frozen environmental contexts
x
8 F37-derived replicas.

CELLS:

48.

EPOCHS:

48.

TURNOVER EPOCHS:

8 / 12 / 16 / 20 / 24 / 28 / 32 / 36 / 40 / 44.

REPLACEMENTS PER TURNOVER:

6.

COMPLETE WORLD-MANIFEST SHA-256:

ad15162fd61dcbde7ec76245423985b7281830a9448f6aa68b56329705384e61.

Serialized manifest-wrapper SHA-256:

80edd5f8f2dfefced90b4a5977f88e33fb72d3bab333ab54a5f717e25d259c1c.

Serialized manifest-wrapper bytes:

40016.

Each bound trial identity includes:

context;
replica;
family;
reversal location where applicable;
spatial region where applicable;
the full F37-derived turnover permutation;
full true local-consequence field hash;
full sensed field hash.

PRIMARY STATUS AT MANIFEST BIND

Real STATIC outcome observed:

0.

Real RESET outcome observed:

0.

Real DIRECT outcome observed:

0.

Real PRIME outcome observed:

0.

Real lineage-chain outcome observed:

0.

The next permitted operation is:

two complete deterministic A37 primary sweeps
using F37 as seed.

NO WORLD REDRAW.
NO TURNOVER CHANGE.
NO PRIME-MULTIPLIER CHANGE.
NO A36-NICHE CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A37 / T8U LINEAGE-PERSISTENT UNCERTAINTY MEMORY

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE MIXED-NEGATIVE RESULT /
LINEAGE PRIMING IS REAL AND BOUNDED
BUT DOES NOT BREAK THE PERSISTENT FAMILY-5 OSCILLATORY ATTRACTOR /
NO PRIME ARM QUALIFIED /
NO ARM MET A37_LINEAGE_MEMORY_INFORMATION_GAIN /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

77206606a0fc48d107b190a2e71eeca3935b080c.

F37:

d7f0ef718c83962dcb2e7fb2c0e57feba4e97bd3.

Source SHA-256:

3e69f508489181c989c79d1d7c72f83a751fe457e726c520785b126e0a095de6.

Deterministic gzip SHA-256:

b44c96bd5f4f80f481a323dd5b1162bd8d066c68da9a8b2beae6610f0b202d3a.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

8018ef44d59b9841fa711cb7e43291ad4c68ee33.

World-manifest SHA-256:

ad15162fd61dcbde7ec76245423985b7281830a9448f6aa68b56329705384e61.

Manifest-wrapper SHA-256:

80edd5f8f2dfefced90b4a5977f88e33fb72d3bab333ab54a5f717e25d259c1c.

PRIMARY REPRODUCIBILITY

Two complete F37-derived primary sweeps
were byte-identical.

Serialized primary SHA-256:

53b1eb601ed308027c556859388a2d1989048f957fee538ef9cb78d438a576ec.

All P1-P34 integrity probes:

PASS.

PRIMARY RESULT

A37_ANY_LINEAGE_MEMORY_QUALIFIED:

FALSE.

A37_LINEAGE_MEMORY_INFORMATION_GAIN:

FALSE.

D2 STATIC

oscillation:

53 / 384
=
13.80%.

FAMILY-5 oscillators:

31.

harm:

15.10%.

aggregate service:

229826.

D2 RESET

oscillation:

56 / 384
=
14.58%.

FAMILY-5 oscillators:

33.

harm:

17.45%.

aggregate service:

230874.

H parent replacements:

1563.

H-history bequest replacements:

5162.

Without inheritance,
only:

39.40%

of bequest-successor generations
reconstituted H before the next turnover / trial end.

Median spontaneous reconstitution latency:

5 epochs.

D2 DIRECT

oscillation:

54 / 384
=
14.06%.

FAMILY-5 oscillators:

32.

Direct H successors:

1634.

Direct phenotype continuity therefore recovered
some of the turnover damage,
but did not materially alter the target attractor.

D2 PRIME

oscillation:

54 / 384
=
14.06%.

FAMILY-5 oscillators:

31.

RESET FAMILY-5 oscillators broken:

2 / 33
=
6.06%.

new FAMILY-5 oscillators versus RESET:

0.

aggregate service:

229145.

service retained versus RESET:

99.25%.

contradiction no-majority:

92.15%.

reversal acquisition:

92.19%.

primed successors:

5275.

primed H-entry rate per eligible opportunity:

21.14%.

unprimed H-entry rate:

7.60%.

prime effect ratio:

2.7814x.

primed successor generations actually re-entering H:

52.06%.

median reconstitution latency:

3 epochs.

Thus the inherited mark strongly changes
successor H propensity.

It is not decorative.

But the population oscillator barely changes.

D3 STATIC

oscillation:

57 / 384
=
14.84%.

FAMILY-5 oscillators:

30.

aggregate service:

223992.

D3 RESET

oscillation:

59 / 384
=
15.36%.

FAMILY-5 oscillators:

31.

aggregate service:

224530.

D3 DIRECT

oscillation:

57 / 384
=
14.84%.

FAMILY-5 oscillators:

32.

Direct H successors:

1378.

D3 PRIME

oscillation:

54 / 384
=
14.06%.

FAMILY-5 oscillators:

29.

RESET FAMILY-5 oscillators broken:

3 / 31
=
9.68%.

new FAMILY-5 oscillators versus RESET:

1.

DIRECT FAMILY-5 oscillators:

32.

PRIME broke:

3

of DIRECT's oscillators
with no new DIRECT-relative FAMILY-5 oscillator.

aggregate service:

223492.

service retained versus RESET:

99.54%.

contradiction no-majority:

93.73%.

reversal acquisition:

96.88%.

primed successors:

4799.

primed H-entry rate:

21.09%.

unprimed H-entry rate:

7.32%.

prime effect ratio:

2.8796x.

primed successor generations re-entering H:

50.51%.

median reconstitution latency:

3 epochs.

LINEAGE EFFECT

A37 proves a narrow but real property:

A BOUNDED INHERITED UNCERTAINTY MARK
CAN ALTER SUCCESSOR BEHAVIOR.

The effect is strong at the local lineage level.

Marked successors are approximately:

2.8x

more likely to re-enter H
per eligible opportunity.

Approximately half
actually use that inherited bias.

The mark is not permanent.

It must be refreshed
by the successor's own H experience
to continue into another generation.

Thus the mechanism behaves as preregistered:

bounded;
inherited;
self-refreshing only through renewed evidence.

However:

that local lineage memory
does not materially change
the persistent oscillator family.

TARGET FAILURE

D2 PRIME breaks:

2 / 33

RESET FAMILY-5 oscillators.

D3 PRIME breaks:

3 / 31.

Frozen information-gain target:

at least 25%.

Frozen qualification target:

at least 50%.

Neither is close.

The persistent oscillatory attractor therefore survives:

isolated H;

spatial H niches;

and one-generation lineage priming.

ATTRACTOR QUALITY LIMIT

False dominance remains far above
the frozen 5% limits.

D2 PRIME:

false C dominance:
18.50%.

false S:
13.81%.

D3 PRIME:

false C:
20.23%.

false S:
15.24%.

Thus lineage priming
does not solve final attractor correctness.

TECHNICAL INTERPRETATION

A37 falsifies the hypothesis:

ONE-GENERATION H-LINEAGE PRIMING
IS THE MISSING TEMPORAL PERSISTENCE DIMENSION.

The history is successfully transmitted.

The successor responds to it.

But the target oscillatory environments
still cause the macroscopic population
to repeatedly reorganize.

This means the remaining problem
is unlikely to be simply:

insufficient memory duration.

A36 already created multi-epoch spatial persistence.

A37 now adds cross-generation historical persistence.

Both remain subordinate
to the temporal forcing pattern.

The FAMILY-5 attractor appears to be
a timescale / phase-organization problem.

The next justified analysis is therefore:

WHICH TEMPORAL MODES
REMAIN OSCILLATORY,
AND WHAT RESPONSE TIMESCALE
DO THEY FORCE?

A future mechanism should not blindly
add more H memory.

It should test whether
different subpopulations need
different intrinsic response timescales
so the organism does not place
all cells on the same temporal resonance.

PLAIN-SPEAK INTERPRETATION

The inheritance mechanism worked.

A cell could leave one small message
for its successor:

"our lineage recently had to stay uncertain."

The successor was not forced
to copy the parent.

But it became almost three times
more likely to hedge again
when it encountered the same kind of conflict.

About half of marked successors
actually used that inherited memory.

So Yggdrasil can now pass
a bounded uncertainty tendency
from one generation to the next.

That is useful.

But the stubborn oscillating worlds
mostly did not care.

Only:

2 of 33

were broken under D2,

and:

3 of 31

under D3.

So we have now tried:

individual uncertainty;

spatially cooperative uncertainty;

and inherited uncertainty.

The same temporal family keeps oscillating.

That points somewhere new.

The problem may be
that too many cells operate
on the same response timescale.

If the environment alternates
near that timescale,
the whole population can resonate with it.

The next question should be:

DOES YGGDRASIL NEED
FAST, MEDIUM, AND SLOW RESPONDER SUBPOPULATIONS
SO TEMPORAL NOISE CANNOT DRAG
THE ENTIRE ORGANISM BACK AND FORTH TOGETHER?

No autonomous controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
