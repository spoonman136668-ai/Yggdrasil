TITLE: YGGDRASIL A25 / T8I — Temporal Low-Pass Persistence Calibration
DATE: 2026-09-21
STATUS: PREREGISTERED TEMPORAL-AVERAGING EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8I / APPLICATION-A
PARENT: A24 Distributed Quorum-Qualified Patch Activation
BRANCH: dg1a-ar

PURPOSE

A24 showed that distributed quorum materially reduces harmful activation,
but broad local agreement can still fail prospectively.

The remaining failure is temporal:

cells may broadly agree that a patch helps NOW
without knowing whether the effect will persist.

A25 isolates temporal averaging / persistence detection.

It does NOT add:

quorum as authority;
above-noise confidence thresholds;
negative-feedback correction;
positive-feedback commitment;
bet-hedging;
adaptive threshold tuning.

Quorum remains measured as a secondary diagnostic only.

FROZEN PARENT

A24 closure:

decfdbb7b3e8bbc887cf1ab69ead2248d128b910.

A24 result:

global one-hit actual harm rate = 16.67%.

7-of-12 local quorum actual harm rate = 6.67%.

Quorum coverage = 15 / 384.

A24 showed that broad present-tense agreement
does not guarantee future persistence.

A25 FREEZE

Let the exact A25 implementation freeze commit be:

F25.

No real A25 trajectory,
temporal-filter state,
or future outcome
may be derived before F25 exists.

FRESH TRAJECTORIES

After F25,
derive exactly:

384

fresh trajectories:

48 fixed A17 patch contexts
x
8 F25-derived replicas.

Each trajectory contains:

32 fresh demand epochs.

Evidence windows:

W1 = 0-7;
W2 = 8-15;
W3 = 16-23.

Untouched confirmation:

W4 = 24-31.

Replacement episodes:

0;
8;
16;
24.

Every 32-demand sequence has exact mean
equal to the candidate target prior.

All demand / replacement namespaces:

YGG-A25-*.

FIXED PROVISIONAL EXPOSURE

Use only:

C3 = 3 of 4 candidate-controlled newborns

for each evidence-phase replacement episode:

0;
8;
16.

The fourth newborn remains stale-controlled.

Matched stale twin:

all four births stale-controlled.

No full candidate expansion occurs before W4.

Reason:

A25 isolates temporal evidence processing.
Exposure is fixed.

PER-EPOCH INPUT SIGNAL

For each evidence epoch t in 0..23:

X_t =
canary service at epoch t
-
matched stale-twin service at epoch t.

X_t is an integer.

The same X_t sequence
feeds all temporal-filter arms.

No arm may use W4 information.

REFERENCE

L0 — LATEST-WINDOW SNAPSHOT

Compute:

B3 =
sum X_t for t in W3.

Expand iff:

B3 > 0.

This asks whether only the most recent 8-epoch block is positive.

LOW-PASS ARMS

Use exact rational arithmetic.

For all arms:

S_-1 = 0.

At each evidence epoch t:

S_t =
(1 - alpha) * S_(t-1)
+
alpha * X_t.

LP_FAST:

alpha = 1/2.

LP_MEDIUM:

alpha = 1/4.

LP_SLOW:

alpha = 1/8.

At end of W3:

expand iff S_23 > 0.

No magnitude threshold above zero is used.

This deliberately isolates temporal averaging
from the later threshold / ultrasensitivity experiment.

COHERENT PERSISTENCE DETECTOR

PERSIST:

direct branch:

B3 > 0.

delayed branch:

LP_SLOW S_23 > 0.

Expand iff BOTH are true.

Thus:

recent evidence must be positive

AND

the slower integrated state must also be positive.

This is the software analogue
of a coherent persistence detector:

a short pulse may activate the direct branch
but can decay before the delayed branch supports commitment.

W4 AUTHORITY

For each gate independently:

EXPAND:

continue that gate's provisional canary trajectory;
all four epoch-24 newborns use candidate target prior.

NO EXPANSION:

restore the exact stale-twin state at epoch 24;
all four epoch-24 newborns use stale prior.

Then execute untouched W4.

The learned patch remains preserved in both cases.

REFERENCE LABELS

R0:

all stale.

R1:

all candidate.

For each trial report
R1-minus-R0 W4 sign:

beneficial;
neutral;
harmful.

PRIMARY METRICS

For:

L0;
LP_FAST;
LP_MEDIUM;
LP_SLOW;
PERSIST

report:

expansion count;

actual W4:
beneficial;
neutral;
harmful;

actual harm rate;

R1 W4 label among expansions:
beneficial;
neutral;
harmful;

R1-label harm rate;

W1-W3 provisional aggregate delta;

W4 aggregate delta versus stale;

complete 32-epoch service delta versus R0;

complete service delta versus R1.

TEMPORAL-SPECIFIC METRICS

Report:

final filter-state distribution;

fraction of trials where
LP_FAST / LP_MEDIUM / LP_SLOW disagree;

trials where latest W3 is positive
but LP_SLOW is nonpositive;

trials where LP_SLOW is positive
but latest W3 is nonpositive;

harm / benefit rates for each disagreement class;

sign-change count in per-window sums:

B1;
B2;
B3.

QUORUM SECONDARY DIAGNOSTIC

Using the exact A24 cell-level marginal definition,
compute a 7-of-12 quorum separately for:

W1;
W2;
W3.

Quorum does NOT control A25 authority.

Report whether temporal filters behave differently when:

0 of 3 windows have quorum;
1 of 3;
2 of 3;
3 of 3.

This preserves quorum as an uncertainty signal
without combining mechanisms prematurely.

PRIMARY QUALIFICATION

A temporal gate is TEMPORAL-QUALIFIED iff:

expansion count >= 48

AND

actual W4 harmful expansion rate <= 0.05

AND

R1 W4 harmful-label rate
among expansions <= 0.05

AND

actual harm rate
is no greater than half
the unconditional R1 W4 harm rate
when that unconditional rate is nonzero

AND

all integrity probes pass.

Coverage floor:

48 / 384.

Harm ceiling:

5%.

A25 does not choose a production winner.

If more than one arm qualifies,
all qualifying arms are reported.

Any later combination or selection
requires a new preregistered experiment.

A25_TEMPORAL_INFORMATION_GAIN

TRUE iff at least one temporal arm:

has lower actual harm rate than L0

AND

rejects at least one harmful L0 expansion

AND

retains at least 50% of L0 beneficial expansions.

This is descriptive only.

INTEGRITY PROBES

P1:
exact A17 replay unchanged.

P2:
384 unique post-F25 trajectories.

P3:
32 demands per trajectory;
exact mean equals candidate target.

P4:
replacement episodes exactly 0 / 8 / 16 / 24;
four unique IDs each.

P5:
W4 future leakage impossible.

P6:
all arms consume identical X_t sequence.

P7:
LP_FAST exact alpha = 1/2.

P8:
LP_MEDIUM exact alpha = 1/4.

P9:
LP_SLOW exact alpha = 1/8.

P10:
rational arithmetic exact;
no floating-point gate decision.

P11:
L0 uses W3 sum only.

P12:
PERSIST requires:
B3 > 0 AND LP_SLOW > 0.

P13:
no above-zero noise threshold
is introduced.

P14:
non-expansion restores exact stale twin.

P15:
learned patch remains preserved.

P16:
quorum is diagnostic only
and cannot affect any gate decision.

P17:
restart equivalence at W3/W4 boundary.

P18:
two complete primary sweeps byte-identical.

P19:
no C-v3;
no duplicate context;
major history [v1,v2];
slot count 3.

NEGATIVE / LIMIT CONTROLS

N1 — ONE LATE POSITIVE EPOCH

Expected to influence LP_FAST more strongly
than LP_SLOW.

N2 — EARLY POSITIVE PULSE FOLLOWED BY NEUTRAL / NEGATIVE SIGNAL

Expected to wash out more strongly
under finite-memory filters.

N3 — FUTURE W4 IN FILTER

Invalid leakage.

N4 — TUNE ALPHA AFTER RESULT

Invalid post-result tuning.

N5 — ADD POSITIVE THRESHOLD ABOVE ZERO

Reserved for threshold / ultrasensitivity experiment.

N6 — USE QUORUM TO VETO OR AUTHORIZE

Not permitted in A25.

N7 — FEEDBACK / BISTABILITY / BET-HEDGING

Not tested in A25.

INTERPRETATION

If slower temporal filters
lower harm while retaining useful coverage,
persistence carries predictive information.

If PERSIST improves over both
latest-window and low-pass-only gates,
a direct-plus-delayed feed-forward motif
earns separate follow-up.

If all temporal filters remain unsafe,
temporal averaging alone is insufficient.

If filters become safe only by collapsing coverage,
the mechanism adds conservatism
but not enough usable predictive information.

PLAIN-SPEAK QUESTION

A24 asked:

"do enough different cells agree?"

That helped,
but one broad consensus still failed later.

A25 asks a different question:

"does the evidence LAST?"

Every epoch adds a tiny push
toward or away from the new patch.

A fast filter reacts quickly
and forgets quickly.

A medium filter averages longer.

A slow filter remembers longer
and should ignore short spikes better.

We also test a persistence detector
that requires both:

the recent window looks good

and

the slow accumulated signal still looks good.

Nothing is allowed to look at the final untouched future.

So A25 asks:

CAN YGGDRASIL DISTINGUISH
A SUSTAINED USEFUL SIGNAL
FROM A TEMPORARY GOOD STRETCH?

Quorum remains visible in the measurements,
but it does not get a vote in this experiment.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A25 TEMPORAL LOW-PASS PERSISTENCE CALIBRATION

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F25-DERIVED TRAJECTORY,
TEMPORAL FILTER STATE,
OR W4 OUTCOME.

IMPLEMENTATION COMMIT

2e332c746259df64525978373cc582a11cab366f.

SOURCE BUNDLE

Loader:

research/applications/track-a/a25_t8i_temporal_lowpass_persistence_v1.py

Loader Git blob:

f44c5076c990715c93060520f9e96abcbb034971.

Payload:

research/applications/track-a/a25_t8i_temporal_lowpass_persistence_v1.py.gz

Payload Git blob:

b4c0e06111e14a516f11aa8d85f8108a318b7dcf.

Decompressed source SHA-256:

b95d723ffdfd70db388d007b99b88b5e78078fab627af71fcd2b34044f1b9e3b.

Decompressed source bytes:

12810.

Deterministic gzip SHA-256:

e64fefd2eefe676c1d821f32718e79ffc4beb909a23d5e328268833a219f6bff.

Compressed payload bytes:

4734.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake freeze:

MECHANICAL-F25-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized result-file SHA-256:

f775212ffae563a06d9f0da0a1aaa8939907553e5e346f0808235193e1880a13.

Serialized semantic output SHA-256:

cc1dfa76a787f6f3bde6a7ae7507e453c67f1972c491cd1855711d8619d1e41a.

All P1-P19 integrity probes:

PASS.

Exact A17 replay:

3978 candidate first-four;
3950 stale first-four;
37 / 48 candidate >= stale;
exact 11 below-stale pairs reproduced.

Mechanical unconditional R1 W4 harm rate:

0.15625.

Mechanical expansion / harm:

L0:
93 expansions;
10 harmful;
harm rate 0.1075268817.

LP_FAST:
156 expansions;
20 harmful;
harm rate 0.1282051282.

LP_MEDIUM:
158 expansions;
20 harmful;
harm rate 0.1265822785.

LP_SLOW:
157 expansions;
20 harmful;
harm rate 0.1273885350.

PERSIST:
91 expansions;
10 harmful;
harm rate 0.1098901099.

No temporal arm qualified.

A25_TEMPORAL_INFORMATION_GAIN:

FALSE

in the fake world.

This is NON-SCIENTIFIC mechanical evidence only.

It demonstrates that temporal filtering
does not trivially satisfy the preregistered criteria.

REAL A25 STATUS

No real F25 trajectory has been derived.

No real temporal filter state has been observed.

No real A25 manifest exists.

No real W4 outcome has been observed.

Let the resulting commit SHA be:

F25.

After F25 exists:

1. derive exactly 384 fresh 32-epoch trajectories from F25;
2. bind the complete manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. report all temporal arms without post-result selection.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A25 TEMPORAL LOW-PASS PERSISTENCE CALIBRATION

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A25 TEMPORAL FILTER DECISION
OR W4 OUTCOME.

F25:

f71b2b6bfec7cb9e0c0c265993ebb33f2f2d9187.

FROZEN SOURCE SHA-256:

b95d723ffdfd70db388d007b99b88b5e78078fab627af71fcd2b34044f1b9e3b.

TRAJECTORY COUNT:

384.

STRUCTURE:

48 fixed A17 patch contexts
x
8 fresh F25-derived replicas.

EPOCHS PER TRAJECTORY:

32.

EVIDENCE WINDOWS:

W1 = 0-7;
W2 = 8-15;
W3 = 16-23.

UNTOUCHED CONFIRMATION:

W4 = 24-31.

REPLACEMENT EPISODES:

0 / 8 / 16 / 24.

COMPLETE MANIFEST SHA-256:

1cd2a35733746d54d3c700d092128a42492b55d42ec36a0ea4b0f18c38449baf.

Serialized manifest-wrapper SHA-256:

f05be1f717ac6bea198514e12e8c06c176b2d24dd9a7f05dda64b46553468cf8.

Serialized manifest-wrapper bytes:

202918.

Every 32-demand sequence has exact mean equal to its candidate target.

Every replacement set contains exactly four unique cell IDs.

All trajectory namespaces are:

YGG-A25-*.

PRIMARY STATUS AT MANIFEST BIND

Real filter states observed:

0.

Real L0 / LP_FAST / LP_MEDIUM / LP_SLOW / PERSIST decisions observed:

0.

Real W4 outcomes observed:

0.

The next permitted operation is:

two complete deterministic A25 primary sweeps
over this exact manifest.

NO TRAJECTORY REDRAW.
NO ALPHA CHANGE.
NO THRESHOLD CHANGE.
NO PERSISTENCE-RULE CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
