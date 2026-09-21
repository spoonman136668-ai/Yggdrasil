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


PRE-RUN IMPLEMENTATION FREEZE 01 — A22 TWO-WINDOW CANARY HYSTERESIS

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL A22 TRAJECTORY.

IMPLEMENTATION COMMIT

8085aea24e78a954f133e4460bd25449a750064c.

SOURCE BUNDLE

Loader:

research/applications/track-a/a22_t8f_two_window_canary_hysteresis_v1.py

Loader Git blob:

5c8ed0ab2deb3ceae5d3795deb224975a6765440.

Payload:

research/applications/track-a/a22_t8f_two_window_canary_hysteresis_v1.py.gz

Payload Git blob:

95fa001a1cb80ac9842d716146244a24a562e4e2.

Decompressed source SHA-256:

7305db14a246c20522e3977e12e61ac06a64786f0b966bf0f288b5e5985da073.

Decompressed source bytes:

10576.

Deterministic gzip SHA-256:

0e91184955407713260dee8cfda1b1a0e27eef514250cba28a31ade03e59d5c4.

Compressed payload bytes:

3839.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake freeze:

MECHANICAL-F22-NONPRIMARY.

Two complete sweeps:

BYTE-IDENTICAL.

Serialized file SHA-256:

6ce7114971e14d3bdb17d531effcc4cc8c16cdbf793017fb759a50faaf6163ef.

Serialized semantic output SHA-256:

b56159f82cb2229536a213a37a9b7c5892e9a2861cc76e81b3eb90d50c8f49dc.

All P1-P14 probes:

PASS.

Fake-world unconditional R1 Window-3 harm rate:

0.15364583333333334.

Mechanical earned expansions:

C1 = 2.
C2 = 8.
C3 = 19.

No arm met the preregistered 48-expansion coverage floor.

No arm qualified.

This is NON-SCIENTIFIC mechanical evidence only.

REAL A22 STATUS

No real post-F22 trajectory has been derived.

No real A22 manifest exists.

No real D1,
D2,
earned expansion,
or Window-3 outcome has been observed.

Let the resulting commit SHA be:

F22.

After F22 exists:

1. derive exactly 384 fresh 24-epoch trajectories;
2. bind the complete manifest SHA;
3. only then execute two complete primary sweeps;
4. require byte-identical output;
5. apply the frozen C1 -> C2 -> C3 minimum-exposure selection rule.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A22 TWO-WINDOW CANARY HYSTERESIS

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A22 D1 / D2 / WINDOW-3 OUTCOME.

F22:

89299d7480dc39a093888798ac9789d550e8e913.

TRAJECTORY COUNT:

384.

STRUCTURE:

48 fixed A17 patch contexts
x
8 fresh F22-derived replicas.

EPOCHS PER TRAJECTORY:

24.

REPLACEMENT EPISODES:

0;
8;
16.

COMPLETE MANIFEST SHA-256:

b413e65063149a141e54e6eb906766807b9a94c7d3a407309b3e0ce1d46756bf.

Serialized manifest-wrapper SHA-256:

99808975634e6677b2855ac60f73ca7de6b1723d1b28290b9a1a4203c5be8a1a.

The complete manifest binds all:

- scenario identities;
- patch identities;
- replica identities;
- candidate priors;
- stale priors;
- 24 fresh demands;
- epoch-0 replacement sets;
- epoch-8 replacement sets;
- epoch-16 replacement sets.

Each 24-demand sequence has exact mean equal to its candidate target.

No primary A22 outcome has been observed.

The next permitted operation is:

two complete deterministic A22 primary sweeps.

NO REDRAW.
NO THRESHOLD CHANGE.
NO EXPOSURE CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A22 / T8F TWO-WINDOW CANARY HYSTERESIS

DATE:
2026-09-21.

STATUS:
CLOSED / SAFETY IMPROVED /
COVERAGE INSUFFICIENT /
NO ARM QUALIFIED /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

8085aea24e78a954f133e4460bd25449a750064c.

F22:

89299d7480dc39a093888798ac9789d550e8e913.

Source SHA-256:

7305db14a246c20522e3977e12e61ac06a64786f0b966bf0f288b5e5985da073.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

fe77f5aebabab76b81e2045ae641d43499513437.

384-trajectory manifest SHA-256:

b413e65063149a141e54e6eb906766807b9a94c7d3a407309b3e0ce1d46756bf.

Manifest-wrapper SHA-256:

99808975634e6677b2855ac60f73ca7de6b1723d1b28290b9a1a4203c5be8a1a.

PRIMARY REPRODUCIBILITY

Two complete primary sweeps were byte-identical.

Serialized result-file SHA-256:

56b39f4f1be0ad32eba27722705a76fd009a2921264e3511464124a4f73e1487.

Serialized semantic output SHA-256:

3f606fc1ef1dd5b42a56955156d12370f8a57ddf58a815796458ae10d2b4bc93.

All P1-P14 probes:

PASS.

FRESH R1 WINDOW-3 BASELINE

Unconditional all-candidate Window-3 harmful:

52 / 384.

Unconditional harm rate:

0.1354166667.

C1 — 25% STATIC CANARY

Window-1 positive:

10.

Window-1 positive but Window-2 nonpositive:

8.

EARNED_EXPANSION:

2.

Actual Window-3 outcomes after earned expansion:

beneficial = 0;
neutral = 2;
harmful = 0.

Actual harm rate:

0.0.

R1 Window-3 labels among earned expansions:

beneficial = 0;
neutral = 2;
harmful = 0.

R1-label harm rate:

0.0.

One-hit reference expansions:

10.

One-hit reference harm rate:

0.20.

Two-hit harm reduction:

20 percentage points
to zero observed harm.

Coverage floor:

2 / 48 required minimum.

FAIL.

C1 HYSTERESIS-QUALIFIED:

FALSE.

C2 — 50% STATIC CANARY

Window-1 positive:

36.

Window-1 positive but Window-2 nonpositive:

28.

EARNED_EXPANSION:

8.

Actual Window-3 outcomes:

beneficial = 1;
neutral = 7;
harmful = 0.

Actual harm rate:

0.0.

R1 Window-3 labels:

beneficial = 1;
neutral = 7;
harmful = 0.

R1-label harm rate:

0.0.

One-hit reference expansions:

36.

One-hit harm rate:

0.1666666667.

Two-hit harm reduction:

16.67 percentage points
to zero observed harm.

Coverage:

8 / 48 required minimum.

FAIL.

C2 HYSTERESIS-QUALIFIED:

FALSE.

C3 — 75% STATIC CANARY

Window-1 positive:

89.

Window-1 positive but Window-2 nonpositive:

73.

EARNED_EXPANSION:

16.

Actual Window-3 outcomes:

beneficial = 6;
neutral = 9;
harmful = 1.

Actual harm rate:

0.0625.

R1 Window-3 labels:

beneficial = 6;
neutral = 9;
harmful = 1.

R1-label harm rate:

0.0625.

One-hit reference expansions:

89.

One-hit harm rate:

0.1573033708.

Two-hit harm reduction:

9.48 percentage points.

Harm ceiling:

6.25%
versus
required <= 5%.

FAIL.

Coverage:

16 / 48 required minimum.

FAIL.

C3 HYSTERESIS-QUALIFIED:

FALSE.

PRIMARY RESULT

Selected arm:

NONE.

A22_TWO_WINDOW_CANARY_HYSTERESIS_SUCCESS:

FALSE.

TECHNICAL INTERPRETATION

A22 confirms that temporal persistence
contains real safety information.

Compared with the same fresh-world one-hit reference,
requiring two consecutive positive canary windows
substantially reduced false-positive expansion.

But the static canary fraction
does not produce enough decisive evidence.

Most first-window positive cases
failed to remain positive
through Window 2.

Observed retention:

C1:
2 / 10.

C2:
8 / 36.

C3:
16 / 89.

Thus a second independent live window
filters transient positives aggressively.

That is useful.

But it also leaves the controller
without enough qualified expansions
to satisfy the preregistered usefulness / coverage floor.

The architecture has therefore reached a new tradeoff:

ONE WINDOW:
too noisy.

TWO STATIC WINDOWS:
much safer,
but too indecisive.

The next problem is not:

"how do we lower the safety threshold?"

The next problem is:

"how do we gather more informative evidence
without prematurely granting full authority?"

PLAIN-SPEAK INTERPRETATION

Making the patch prove itself twice helped a lot.

With one good trial,
we were fooled fairly often.

With two good trials in a row,
the bad expansions almost disappeared.

That is exactly what we hoped hysteresis would do.

But almost everything got stuck waiting.

A patch would win once,
then the next small trial would tie or lose,
so it never earned full control.

The safest arms ended up approving only:

2 patches;
8 patches;
and 16 patches

out of 384 fresh futures.

That is too little useful authority
for the system we ultimately want.

So we should NOT respond by weakening the rule.

That would throw away the safety lesson.

Instead,
Yggdrasil needs a better way to accumulate evidence.

Right now it treats each window almost like:

win;
win again;
or start over.

A more mature organism should be able to say:

"I have some evidence for this patch.
Not enough to trust it yet.
Keep the patch dormant or partially active.
Add future independent evidence to the same confidence record."

That points toward a persistent:

PATCH CONFIDENCE LEDGER

rather than a simple consecutive-win switch.

Evidence should accumulate across real experiences,
decay or reverse when contradicted,
and grant authority only when confidence becomes strong enough.

That is the next research direction.

A17:
mixed / negative.

A18:
diagnostic.

A19:
shadow confidence insufficient.

A20:
real-canary discovery.

A21:
one-hit replication failed.

A22:
two-hit hysteresis safer but insufficiently decisive.

No sequential autonomous activation controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
