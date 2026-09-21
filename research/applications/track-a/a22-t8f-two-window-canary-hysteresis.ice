TITLE: YGGDRASIL A22 / T8F — Two-Window Canary Hysteresis
DATE: 2026-09-21
STATUS: PREREGISTERED CONFIRMATORY HYSTERESIS EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8F / APPLICATION-A
PARENT: A21 Out-of-Sample Canary Activation Replication
BRANCH: dg1a-ar

PURPOSE

A21 falsified:

one positive 8-epoch canary window
is sufficient for safe expansion authority.

Positive evidence frequently reversed
in the next independent window.

A16 previously demonstrated that sustained drift
can be separated from transient noise
through hysteretic evidence.

A22 combines those findings.

A learned patch must now demonstrate:

positive real consequence
across TWO consecutive independent canary windows

before it may earn full candidate birth authority.

A third untouched window
tests that earned authority prospectively.

FROZEN INPUT

A21 closure:

8a8108c29213c1953ddad69b7c74ca629e0fb8f2.

A20 source lineage and exact A17 patch contexts remain unchanged.

48 fixed patch contexts:

12 scenarios x 4 patches.

For each context:

candidate prior = learned A17 patch target;
stale prior = previous A17 learned target;
starting cell state = exact A17 pre-evaluation candidate state.

A22 FREEZE

Let the exact implementation freeze commit be:

F22.

No real A22 trajectory may be derived before F22.

POST-FREEZE TRAJECTORIES

After F22,
derive exactly:

8 fresh replicas per patch context.

Total:

384 trajectories.

Each trajectory contains:

24 evaluation epochs
=
12 symmetric zero-mean demand pairs
around the candidate target.

Derivation tag:

YGG-A22-EVAL|F22|scenario|patch|replica|pair.

Replacement episodes:

epoch 0;
epoch 8;
epoch 16.

Each replacement set contains exactly four unique cell IDs.

Derivation tag:

YGG-A22-REPLACE|F22|scenario|patch|replica|epoch|cell_id.

Bind the complete 384-trajectory manifest SHA
before primary execution.

CANARY ARMS

C1:
1 / 4 candidate-controlled newborns.

C2:
2 / 4.

C3:
3 / 4.

The remainder use stale-prior authority.

Canonical replacement tuple order is used.

STALE TWIN

Every trial begins with:

canary state
and
all-stale twin

byte-identical.

The stale twin uses stale prior
at epochs 0,
8,
and 16.

Both receive the exact same demand sequence.

WINDOW 1 — EPOCHS 0-7

At epoch 0,
canary uses the arm exposure fraction.

Run epochs 0-7.

Compute:

D1 =
canary service[0:8]
-
stale twin service[0:8].

If D1 > 0:

patch remains provisional;
continue canary into Window 2.

If D1 <= 0:

the patch does NOT qualify for full authority;
restore stale twin at epoch 8;
remain stale-controlled for the rest of this trial.

The learned patch remains preserved.

WINDOW 2 — EPOCHS 8-15

Only D1-positive trials remain under canary exposure.

At epoch 8:

repeat the SAME canary exposure fraction.

Run epochs 8-15.

Compute:

D2 =
canary service[8:16]
-
stale twin service[8:16].

If:

D1 > 0
AND
D2 > 0

then:

EARNED_EXPANSION.

Otherwise:

NO_EXPANSION;
restore exact stale twin state at epoch 16.

No magnitude threshold.
No averaging D1 and D2.
Both signs must be independently positive.

WINDOW 3 — EPOCHS 16-23

This window is invisible
until after the earned-expansion decision.

EARNED_EXPANSION:

continue canary trajectory;
all four epoch-16 newborns use candidate prior.

NO_EXPANSION:

restore exact stale twin at epoch 16;
all four epoch-16 newborns use stale prior.

Run epochs 16-23.

Window 3 is the prospective confirmation window.

REFERENCE ARMS

R0:
all-stale for all three replacement episodes.

R1:
all-candidate for all three replacement episodes.

ONE-HIT REFERENCE

For diagnosis only,
also compute what the frozen A21 one-hit rule
would have done on Window 1:

D1 > 0 -> expand at epoch 8.

This is not an A22 candidate controller.
It exists only to quantify whether two-hit hysteresis
reduces false positive authority.

PRIMARY CONFIRMATORY SIGNAL PER ARM

An arm is HYSTERESIS-QUALIFIED iff all are true:

EARNED_EXPANSION count >= 48
AND
actual Window-3 harmful expansion rate <= 0.05
AND
R1 Window-3 harmful labels among EARNED_EXPANSION trials <= 0.05
AND
actual harmful expansion rate
is no greater than half
the unconditional R1 Window-3 harm rate
when that unconditional rate is nonzero
AND
all restart / leakage / exposure / restore probes pass.

Coverage floor:

48 / 384.

Harm ceiling:

5%.

These are frozen before F22.

MINIMUM-EXPOSURE SELECTION

If multiple arms qualify,
select the lowest exposure:

C1
then C2
then C3.

If none qualify:

NONE.

No highest-service post-hoc selection.

SECONDARY METRICS

For each arm report:

D1-positive count;

D1-positive but D2-nonpositive count;

EARNED_EXPANSION count;

Window-1 canary regret;

Window-2 canary regret
for D1-positive trials;

Window-3 delta versus stale twins;

complete 24-epoch service delta versus R0;

complete service delta versus R1;

actual beneficial / neutral / harmful earned expansions;

R1 beneficial / neutral / harmful Window-3 labels
among earned expansions;

one-hit reference expansion count and harm rate;

harm reduction from one-hit to two-hit;

distribution across scenarios,
patches,
and replicas.

INTEGRITY PROBES

P1:
A17 replay exact.

P2:
384 unique post-F22 trajectories.

P3:
24 demands per trajectory;
exact mean equals candidate target.

P4:
replacement episodes exactly 0 / 8 / 16;
four unique IDs each.

P5:
no future Window-3 demand reaches D1 or D2 decision code.

P6:
D1 must be independently positive.

P7:
D2 must be independently positive.

P8:
D1 <= 0 restores stale twin at epoch 8.

P9:
D2 <= 0 restores stale twin at epoch 16.

P10:
earned expansion uses 4 / 4 candidate births at epoch 16
without retroactively rewriting existing cells.

P11:
C1 / C2 / C3 provisional exposure limits exact
at epochs 0 and 8.

P12:
learned patch is never deleted.

P13:
two complete primary sweeps byte-identical.

P14:
no C-v3;
no duplicate context;
major history [v1,v2];
slot count 3.

LIMITS

A22 still tests fixed patch semantics.

It does not yet test:

new patch paths;
sequential interaction between different learned patches;
model mismatch;
adversarial provenance;
canonical DG-1R-05.

PLAIN-SPEAK QUESTION

A21 taught us that one good live trial can be a fluke.

A22 asks the patch to prove itself twice.

It gets a small amount of authority.

If it wins the first real window,
we do NOT promote it yet.

We keep it small
and make it win again
on another independent stretch.

Only two consecutive wins
earn full authority.

Then we reveal a third fresh stretch
and see whether that trust was deserved.

This is the software-cell equivalent of saying:

one good day is interesting;
two independent good days may be evidence;
the third day tells us whether our confidence was justified.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
