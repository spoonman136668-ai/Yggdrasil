TITLE: YGGDRASIL A26 / T8J — Threshold / Ultrasensitivity Calibration
DATE: 2026-09-21
STATUS: PREREGISTERED THRESHOLD-GATING EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8J / APPLICATION-A
PARENT: A25 Temporal Low-Pass Persistence Calibration
BRANCH: dg1a-ar

PURPOSE

A25 showed that temporal persistence contains some useful information,
but simple low-pass memory does not make activation safe.

A25 deliberately treated any evidence above zero as actionable.

A26 isolates the next biological mechanism:

THRESHOLDING / ULTRASENSITIVITY.

The question is:

DOES REQUIRING A SIGNAL TO RISE CLEARLY ABOVE ZERO
SEPARATE USEFUL EVIDENCE FROM TRAJECTORY NOISE?

A26 does NOT add:

new quorum authority;
new temporal-filter authority;
negative feedback;
positive-feedback commitment;
bet-hedging;
adaptive threshold tuning.

FROZEN PARENT

A25 closure:

65536da466318ccafee19240cee8ea57d22888c7.

A25 result:

plain low-pass filters remained unsafe;
a coherent persistence detector rejected two transient late positives correctly;
absolute harm remained far above the 5% ceiling.

A26 FREEZE

Let the exact A26 implementation freeze commit be:

F26.

No real A26 trajectory,
threshold decision,
or W2 outcome
may be derived before F26 exists.

FRESH TRAJECTORIES

After F26,
derive exactly:

384

fresh trajectories:

48 fixed A17 patch contexts
x
8 F26-derived replicas.

Each trajectory contains:

16 fresh demand epochs.

Evidence window:

W1 = epochs 0-7.

Untouched confirmation:

W2 = epochs 8-15.

Replacement episodes:

0;
8.

Every 16-demand sequence has exact mean
equal to the candidate target prior.

All demand / replacement namespaces:

YGG-A26-*.

FIXED PROVISIONAL EXPOSURE

Use only:

C3 = 3 of 4 candidate-controlled newborns

at epoch 0.

The fourth newborn remains stale-controlled.

Matched stale twin:

all four births stale-controlled.

No full candidate expansion occurs before W2.

EVIDENCE SIGNAL

For W1 compute:

B1 =
cumulative canary service
-
cumulative matched stale-twin service.

B1 is an integer.

The same exact B1
feeds every threshold arm.

No W2 information may reach B1 or any gate.

THRESHOLD / ULTRASENSITIVITY ARMS

T1 — MINIMAL POSITIVE REFERENCE

Expand iff:

B1 >= +1.

This is the old rule:

anything positive counts.

T2 — LOW THRESHOLD

Expand iff:

B1 >= +2.

T3 — MEDIUM THRESHOLD

Expand iff:

B1 >= +3.

T4 — HIGH THRESHOLD

Expand iff:

B1 >= +4.

These are frozen before F26.

No threshold may be tuned after observing real outcomes.

ULTRASENSITIVITY OPERATIONALIZATION

A26 uses a hard step response.

Below threshold:

NO EXPANSION.

At or above threshold:

EXPAND.

Thus a one-unit change around the threshold
can switch authority discretely.

A26 intentionally does not use
a graded sigmoid / Hill output.

That would add another mechanism
and is reserved for later work if needed.

W2 AUTHORITY

For each gate independently:

EXPAND:

continue that gate's provisional canary trajectory;
all four epoch-8 newborns use candidate target prior.

NO EXPANSION:

restore the exact matched stale-twin state;
all four epoch-8 newborns use stale prior.

Then execute untouched W2.

The learned patch remains preserved in both cases.

REFERENCE LABELS

R0:

all stale.

R1:

all candidate.

For each trial report
R1-minus-R0 W2 sign:

beneficial;
neutral;
harmful.

PRIMARY METRICS

For T1 / T2 / T3 / T4 report:

expansion count;

actual W2:
beneficial;
neutral;
harmful;

actual harm rate;

R1 W2 label among expansions:
beneficial;
neutral;
harmful;

R1-label harm rate;

W1 provisional aggregate delta;

W2 aggregate delta versus stale;

complete 16-epoch service delta versus R0;

complete service delta versus R1.

THRESHOLD-SPECIFIC METRICS

For T2 / T3 / T4 report relative to T1:

T1 expansions rejected;

harmful T1 expansions rejected;

beneficial T1 expansions rejected;

beneficial T1 expansions retained;

beneficial retention fraction;

signal histogram by exact B1 value;

actual future harm / benefit rate
conditioned on B1 value.

PRIMARY QUALIFICATION

A threshold arm is THRESHOLD-QUALIFIED iff:

expansion count >= 48

AND

actual W2 harmful expansion rate <= 0.05

AND

R1 W2 harmful-label rate
among expansions <= 0.05

AND

actual harm rate
is no greater than half
the unconditional R1 W2 harm rate
when that unconditional rate is nonzero

AND

all integrity probes pass.

Coverage floor:

48 / 384.

Harm ceiling:

5%.

A26 does not select a production winner.

If multiple thresholds qualify,
all are reported.

Any later combination with quorum
or temporal persistence
requires a new preregistered experiment.

A26_THRESHOLD_INFORMATION_GAIN

TRUE iff at least one of T2 / T3 / T4:

has lower actual harm rate than T1

AND

rejects at least one harmful T1 expansion

AND

retains at least 50% of T1 beneficial expansions.

This is descriptive only.

INTEGRITY PROBES

P1:
exact A17 replay unchanged.

P2:
384 unique post-F26 trajectories.

P3:
16 demands per trajectory;
exact mean equals candidate target.

P4:
replacement episodes exactly 0 / 8;
four unique IDs each.

P5:
W2 future leakage impossible.

P6:
all threshold arms consume identical B1.

P7:
T1 exactly B1 >= 1.

P8:
T2 exactly B1 >= 2.

P9:
T3 exactly B1 >= 3.

P10:
T4 exactly B1 >= 4.

P11:
hard step response only;
no graded authority.

P12:
temporal filters cannot affect authority.

P13:
quorum cannot affect authority.

P14:
non-expansion restores exact stale twin.

P15:
learned patch remains preserved.

P16:
restart equivalence at W1/W2 boundary.

P17:
two complete primary sweeps byte-identical.

P18:
no C-v3;
no duplicate context;
major history [v1,v2];
slot count 3.

NEGATIVE / LIMIT CONTROLS

N1 — ANY POSITIVE COUNTS

T1 reference.

N2 — POST-HOC THRESHOLD TUNING

Invalid.

N3 — USE W2 TO ESTIMATE THRESHOLD

Invalid future leakage.

N4 — TEMPORAL PERSISTENCE VETO

Not permitted in A26.

N5 — QUORUM VETO

Not permitted in A26.

N6 — GRADED / PROBABILISTIC AUTHORITY

Not tested in A26.

N7 — FEEDBACK / BISTABILITY / BET-HEDGING

Not tested in A26.

INTERPRETATION

If T2 / T3 / T4 reduce harm
while retaining useful coverage,
a noise-floor threshold carries predictive information.

If harm falls only because coverage collapses,
the threshold adds conservatism
but not enough usable discrimination.

If stronger B1 values remain unpredictive,
magnitude alone does not solve uncertainty.

If one threshold qualifies,
it still requires independent replication
before combination with other mechanisms.

PLAIN-SPEAK QUESTION

Until now,
Yggdrasil has often treated:

+1

as if it meant:

"the patch helped."

A26 asks whether +1 is often just noise.

We test four fixed rules:

anything positive;
at least +2;
at least +3;
at least +4.

The stronger gates behave like
a biological response threshold.

Below the threshold:

the cell does nothing.

Cross the threshold:

the response switches on.

Nothing gets tuned after we see the answer.

So A26 asks:

HOW STRONG DOES THE SIGNAL HAVE TO BE
BEFORE YGGDRASIL SHOULD TREAT IT
AS MORE THAN NOISE?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A26 THRESHOLD / ULTRASENSITIVITY CALIBRATION

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F26-DERIVED TRAJECTORY,
THRESHOLD DECISION,
OR W2 OUTCOME.

IMPLEMENTATION COMMIT

36596d24028f5e8cf816408099977227c50a8e4b.

SOURCE BUNDLE

Loader:

research/applications/track-a/a26_t8j_threshold_ultrasensitivity_v1.py

Loader Git blob:

2682b710b7d0826a5ec1a570cebdb76eb084f519.

Payload:

research/applications/track-a/a26_t8j_threshold_ultrasensitivity_v1.py.gz

Payload Git blob:

eb233b40893a78468b5e56c4345abd1960d98959.

Decompressed source SHA-256:

67522a26a83b457014453634db2deef3ffb539fea4fe78d2ca165883f19372c4.

Decompressed source bytes:

11894.

Deterministic gzip SHA-256:

b865428eef3c79878c83e1828bf1935e807f96987f92e540bd55bb9c59742f84.

Compressed payload bytes:

4094.

PRE-FREEZE DIAGNOSTIC REPAIR

The first mechanical pass found one diagnostic-only defect.

Rejected T1 cases were being classified
using the restored stale trajectory,
which made their counterfactual T1 consequence appear neutral.

The repair changed only the descriptive:

rejected_t1_harmful;
rejected_t1_beneficial

counters.

It did NOT change:

T1 / T2 / T3 / T4 decisions;
threshold values;
trajectory generation;
service evaluation;
restore semantics;
qualification criteria;
or any scientific outcome.

The repair occurred before F26
and before any real F26-derived trajectory existed.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake freeze:

MECHANICAL-F26-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized result-file SHA-256:

8b6b13aeb45488a95b702304ae51588bbc7d65cdf139828065dd2b9ed19609ab.

Serialized semantic output SHA-256:

428fb9ffbb8215a2ac9af4d6fa1010adc574709515a360db36bfc4d64aeee65b.

All P1-P18 integrity probes:

PASS.

Exact A17 replay:

3978 candidate first-four;
3950 stale first-four;
37 / 48 candidate >= stale;
exact 11 below-stale pairs reproduced.

Mechanical threshold behavior:

T1:
66 expansions;
11 harmful;
16.67% harm.

T2:
17 expansions;
1 harmful;
5.88% harm;
10 / 11 harmful T1 expansions rejected;
26.1% beneficial T1 expansions retained.

T3:
5 expansions;
0 harmful;
4.35% beneficial T1 expansions retained.

T4:
3 expansions;
0 harmful;
0% beneficial T1 expansions retained.

No threshold qualified.

A26_THRESHOLD_INFORMATION_GAIN:

FALSE

in the fake world.

This is NON-SCIENTIFIC mechanical evidence only.

It demonstrates that stronger thresholds can reduce harm
by collapsing coverage,
and that the preregistered criteria do not trivially pass.

REAL A26 STATUS

No real F26 trajectory has been derived.

No real threshold decision has been observed.

No real A26 manifest exists.

No real W2 outcome has been observed.

Let the resulting commit SHA be:

F26.

After F26 exists:

1. derive exactly 384 fresh 16-epoch trajectories from F26;
2. bind the complete manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report all threshold arms without post-result selection.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A26 THRESHOLD / ULTRASENSITIVITY CALIBRATION

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A26 THRESHOLD DECISION
OR W2 OUTCOME.

F26:

1a9fb005e8fbdad1bc683ff744c1b84624b8d470.

FROZEN SOURCE SHA-256:

67522a26a83b457014453634db2deef3ffb539fea4fe78d2ca165883f19372c4.

TRAJECTORY COUNT:

384.

STRUCTURE:

48 fixed A17 patch contexts
x
8 fresh F26-derived replicas.

EPOCHS PER TRAJECTORY:

16.

EVIDENCE WINDOW:

W1 = 0-7.

UNTOUCHED CONFIRMATION:

W2 = 8-15.

REPLACEMENT EPISODES:

0 / 8.

COMPLETE MANIFEST SHA-256:

89864ad4a5ee97d186f14e85c7824fb05fcdfe069d2ecdca5bf621bb034f0b76.

Serialized manifest-wrapper SHA-256:

5fd9144bda9e3d583c0e1dc26ab69549ca561253a170469383dedb3792ec7ed3.

Serialized manifest-wrapper bytes:

129390.

Every 16-demand sequence has exact mean equal to its candidate target.

Every replacement set contains exactly four unique cell IDs.

All trajectory namespaces are:

YGG-A26-*.

PRIMARY STATUS AT MANIFEST BIND

Real B1 signals observed:

0.

Real T1 / T2 / T3 / T4 decisions observed:

0.

Real W2 outcomes observed:

0.

The next permitted operation is:

two complete deterministic A26 primary sweeps
over this exact manifest.

NO TRAJECTORY REDRAW.
NO THRESHOLD CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A26 / T8J THRESHOLD / ULTRASENSITIVITY CALIBRATION

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE NEGATIVE RESULT /
SIGNAL-MAGNITUDE THRESHOLDING DID NOT PRODUCE SAFE USEFUL AUTHORITY /
NO THRESHOLD QUALIFIED /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

36596d24028f5e8cf816408099977227c50a8e4b.

F26:

1a9fb005e8fbdad1bc683ff744c1b84624b8d470.

Source SHA-256:

67522a26a83b457014453634db2deef3ffb539fea4fe78d2ca165883f19372c4.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

fc5f78e31170390fd7e281722401156596d4165d.

384-trajectory manifest SHA-256:

89864ad4a5ee97d186f14e85c7824fb05fcdfe069d2ecdca5bf621bb034f0b76.

Manifest-wrapper SHA-256:

5fd9144bda9e3d583c0e1dc26ab69549ca561253a170469383dedb3792ec7ed3.

PRIMARY REPRODUCIBILITY

Two complete F26-derived primary sweeps were byte-identical.

Serialized result-file SHA-256:

6d997b71628d8ac9fae275c0395f72b0d1aa2c3f7ad46237a8f566242efde988.

Serialized semantic output SHA-256:

b386e5ece647cb6c3a5ff62fab67b1bdce53e076e22dd495e9862657a92ba219.

All P1-P18 integrity probes:

PASS.

A17 replay remained exact.

FRESH R1 W2 BASELINE

Unconditional all-candidate W2 harmful:

53 / 384.

Unconditional harm rate:

0.1380208333.

T1 — B1 >= +1

Expansions:

77.

Actual W2 outcomes:

beneficial = 29;
neutral = 36;
harmful = 12.

Actual harm rate:

0.1558441558.

R1-label harm rate:

0.1428571429.

Complete service delta versus R0:

+26.

T1 QUALIFIED:

FALSE.

T2 — B1 >= +2

Expansions:

20.

Actual W2 outcomes:

beneficial = 7;
neutral = 10;
harmful = 3.

Actual harm rate:

0.15.

R1-label harm rate:

0.15.

Complete service delta versus R0:

+4.

Relative to T1:

57 expansions rejected;
9 harmful T1 expansions rejected;
22 beneficial T1 expansions rejected;
beneficial retention = 24.14%.

T2 QUALIFIED:

FALSE.

T3 — B1 >= +3

Expansions:

9.

Actual W2 outcomes:

beneficial = 2;
neutral = 6;
harmful = 1.

Actual harm rate:

0.1111111111.

R1-label harm rate:

0.1111111111.

Complete service delta versus R0:

-2.

Relative to T1:

68 expansions rejected;
11 harmful T1 expansions rejected;
27 beneficial T1 expansions rejected;
beneficial retention = 6.90%.

T3 QUALIFIED:

FALSE.

T4 — B1 >= +4

Expansions:

4.

Actual W2 outcomes:

beneficial = 0;
neutral = 4;
harmful = 0.

Actual harm rate:

0.0.

R1-label harm rate:

0.0.

Complete service delta versus R0:

-4.

Relative to T1:

73 expansions rejected;
12 harmful T1 expansions rejected;
29 beneficial T1 expansions rejected;
beneficial retention = 0%.

T4 QUALIFIED:

FALSE.

PRIMARY RESULT

A26_ANY_THRESHOLD_QUALIFIED:

FALSE.

A26_THRESHOLD_INFORMATION_GAIN:

FALSE.

SIGNAL-STRENGTH DIAGNOSTIC

Observed actual W2 outcomes
conditioned on exact positive B1:

B1 = +1:

57 trials;
22 beneficial;
26 neutral;
9 harmful;
harm rate = 15.79%.

B1 = +2:

11 trials;
5 beneficial;
4 neutral;
2 harmful;
harm rate = 18.18%.

B1 = +3:

5 trials;
2 beneficial;
2 neutral;
1 harmful;
harm rate = 20.00%.

B1 = +4:

2 trials;
0 beneficial;
2 neutral;
0 harmful.

B1 = +5:

1 trial;
0 beneficial;
1 neutral;
0 harmful.

B1 = +6:

1 trial;
0 beneficial;
1 neutral;
0 harmful.

Thus:

STRONGER POSITIVE SIGNAL

did NOT produce a monotonic reduction
in prospective harm.

In fact,
the +2 and +3 groups
had higher observed harm fractions
than the +1 group.

The only zero-harm high-signal cases
were four extremely sparse +4-or-greater trials,
and all four were neutral rather than beneficial.

Therefore A26 does not support
the simple biological analogy:

"raise the response threshold above the noise floor
and the remaining positive signals become reliably useful."

Thresholding did reduce decisions.

It did not create calibrated certainty.

TECHNICAL INTERPRETATION

A26 falsifies the hypothesis
that simple positive effect magnitude
is the missing confidence variable.

The W1 signal B1 is useful as an observation,
but its magnitude does not map monotonically
to future W2 benefit.

A stronger observed advantage can still be:

trajectory-local;
state-dependent;
temporally unstable;
or followed by a different future demand realization.

Hard ultrasensitive gating therefore produces
a familiar safety / usefulness tradeoff:

higher threshold
-> fewer actions.

But the reduction in harm
comes primarily from refusing to act,
not from isolating a reliably beneficial signal class.

At T4,
zero harm was achieved only with:

4 / 384 expansions

and:

0 / 4 beneficial outcomes.

That is not useful confidence calibration.

PLAIN-SPEAK INTERPRETATION

The threshold idea was worth testing.

It gave us a very clean answer.

We asked:

"maybe +1 is noise.
What if Yggdrasil only acts on +2,
+3,
or +4?"

That did not solve it.

A +2 signal was not reliably safer than +1.

A +3 signal was not reliably safer than +2.

Some stronger-looking signals
still went bad in the untouched future.

The +4 rule had no bad expansions,
but only because almost nothing passed it.

Only four cases got through.

None of those four actually helped later.

They were all neutral.

So a high threshold can make Yggdrasil quiet.

That is not the same as making Yggdrasil wise.

This matters because it eliminates another tempting shortcut:

MORE SIGNAL
does not automatically mean
MORE CERTAINTY.

Across A24-A26 we now have three separate useful-but-incomplete signals:

QUORUM:
how broadly is the effect experienced now?

PERSISTENCE:
does the effect survive through time?

MAGNITUDE / THRESHOLD:
how strong is the observed effect?

None by itself predicts the future well enough
for autonomous activation authority.

The next biological mechanism is therefore well motivated:

NEGATIVE FEEDBACK / HOMEOSTATIC CORRECTION.

Instead of trying to perfectly certify a patch
before granting any authority,
the organism can grant bounded authority
while continuously comparing:

expected state
versus
observed state.

If the new authority pushes the organism
away from its operating setpoint,
negative feedback can reduce or withdraw authority
before the damage compounds.

That tests a different proposition:

NOT:

"can I know in advance that this is safe?"

BUT:

"can I detect that I am becoming wrong
quickly enough to correct myself?"

A24 quorum remains a useful measured signal.

A25 persistence remains a useful measured signal.

A26 thresholds / ultrasensitivity alone are insufficient.

No autonomous activation controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
