TITLE: YGGDRASIL A23 / T8G — Persistent Patch Confidence Ledger
DATE: 2026-09-21
STATUS: PREREGISTERED SEQUENTIAL EVIDENCE-ACCUMULATION EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8G / APPLICATION-A
PARENT: A22 Two-Window Canary Hysteresis
BRANCH: dg1a-ar

PURPOSE

A21 showed that one positive real canary window is too noisy.

A22 showed that requiring two consecutive positive windows
substantially improves safety,
but discards too much partial evidence
and leaves too few expansions.

A23 therefore replaces the consecutive-win switch
with a persistent confidence ledger.

The ledger does not forget a positive window
just because the next window is neutral.

It also does not ignore contradiction.

Every independent real window
adds signed evidence to the same immutable record.

The scientific question is:

CAN A PATCH ACCUMULATE ENOUGH REAL EVIDENCE
TO EARN AUTHORITY
WITHOUT REQUIRING CONSECUTIVE WINS
AND WITHOUT REINTRODUCING THE A21 HARM RATE?

A23 is not permitted to weaken A22 safety limits.

FROZEN PARENT EVIDENCE

A20:
real-canary discovery positive in known A17 worlds.

A21:
fresh one-window replication failed.

A22:
two-window hysteresis reduced harm sharply
but failed the 48 / 384 coverage floor.

A22 closure:

42726774fc258e2f23e1ee5f00342205ab58607f.

A23 FREEZE

Let the exact A23 implementation freeze commit be:

F23.

No real post-F23 trajectory may be derived
before F23 exists.

FRESH TRAJECTORIES

After F23,
derive exactly:

384

fresh trajectories:

48 fixed A17 patch contexts
x
8 post-F23 replicas.

Each trajectory contains:

40 demand epochs.

Replacement episodes:

0;
8;
16;
24;
32.

Windows:

W1 = epochs 0-7;
W2 = 8-15;
W3 = 16-23;
W4 = 24-31;
W5 = 32-39.

W1-W4 are provisional evidence windows.

W5 is untouched confirmation.

Every 40-demand sequence has exact mean
equal to the candidate target prior.

All demand and replacement namespaces are:

YGG-A23-*

and distinct from A17-A22.

CANARY ARMS

C1:
1 of 4 newborns candidate-controlled
during W1-W4.

C2:
2 of 4.

C3:
3 of 4.

The remaining newborns use stale-previous authority.

The same canary fraction is used
at each provisional replacement episode:

0;
8;
16;
24.

No full candidate expansion occurs
before W5.

STALE TWIN

Every provisional trajectory has
an exact stale-control twin
from the same pre-window state.

Candidate canary and stale twin receive
the same demand sequence.

The twin provides:

counterfactual evidence;
rollback authority;
matched service comparison.

CONFIDENCE LEDGER

Initial confidence:

0.

After each provisional window Wi,
compute:

delta_i =
canary cumulative service in Wi
-
matched stale-twin service in Wi.

Evidence contribution:

delta_i > 0:
+1.

delta_i == 0:
0.

delta_i < 0:
-1.

Ledger score after window i:

L_i =
sum of all contributions from W1..Wi.

No clipping.

With four provisional windows:

L_i is bounded naturally in [-4,+4].

A23 intentionally uses only the sign,
not the magnitude,
because A21 showed that larger positive margins
were not reliably safe.

IMMUTABLE LEDGER RECORD

Every evidence record contains:

scenario;
patch;
replica;
canary arm;
window index;
canary service;
stale-twin service;
delta;
signed contribution;
prior ledger digest;
post-update score;
window evidence digest.

Each ledger record is digest-chained.

Historical evidence is immutable.

A neutral or contradictory window
does not erase prior evidence.

EARNED AUTHORITY RULE

At the end of W4:

if L_4 >= +2:

EARNED_EXPANSION.

Otherwise:

NO_EXPANSION.

No earlier full expansion is permitted.

No score below +2 deletes the learned patch.

The patch remains:

LEARNED / DORMANT / PROVISIONAL.

A23 therefore tests:

two NET positive windows
across four independent opportunities,

not:

two consecutive positive windows.

WHY +2

A22 required two positive windows in a row.

A23 preserves the same net evidentiary requirement
but removes the adjacency requirement.

Thus A23 changes evidence memory,
not the nominal amount of positive evidence required.

W5 CONFIRMATION

At epoch 32:

EARNED_EXPANSION:
all four newborns use candidate target prior.

NO_EXPANSION:
all four newborns use stale-previous prior.

Then execute W5 untouched.

No W5 demand identity
may reach the ledger or decision function.

REFERENCE RULES

R0:
always stale in W5.

R1:
all-candidate in W5.

R2:
A21-style one-hit reference:
W1 positive.

R3:
A22-style two-hit consecutive reference:
W1 positive AND W2 positive.

R4:
A23 ledger:
L4 >= +2.

R2 and R3 are diagnostic references only.

PRIMARY QUALIFICATION PER ARM

An arm is LEDGER-QUALIFIED iff all are true:

EARNED_EXPANSION count >= 48

AND

actual W5 harmful expansion rate <= 0.05

AND

R1 W5 harmful labels
among EARNED_EXPANSION trajectories <= 0.05

AND

actual harmful expansion rate
is no greater than half
the unconditional R1 W5 harm rate
when that rate is nonzero

AND

all integrity probes pass.

Coverage floor:

48 / 384.

Harm ceiling:

5%.

These are inherited unchanged from A22.

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

W1 positive count;
W2 positive count;
W3 positive count;
W4 positive count;

score distribution L4 = -4..+4;

EARNED_EXPANSION count;

provisional W1-W4 aggregate service delta
versus stale twins;

W5 service delta versus stale;

complete 40-epoch service delta versus R0;

complete service delta versus R1;

actual beneficial / neutral / harmful W5 expansions;

R1 beneficial / neutral / harmful W5 labels
among earned expansions;

one-hit reference count and harm rate;

two-hit consecutive reference count and harm rate;

persistent-ledger count and harm rate;

coverage recovered by ledger
relative to A22-style two-hit;

harm difference
relative to one-hit and two-hit;

time distribution of positive / neutral / negative evidence.

EVIDENCE-PATTERN DIAGNOSTICS

Report separately:

++00;
+0+0;
+-+-;
++--;
+--+;
0++;
and all other observed sign patterns.

The purpose is to identify
whether nonconsecutive positive evidence
is genuinely useful
or merely re-admits transient false positives.

No sign pattern may be excluded post hoc.

INTEGRITY PROBES

P1:
exact A17 replay remains unchanged.

P2:
384 unique F23-derived trajectories.

P3:
40 demands per trajectory;
exact mean equals candidate target.

P4:
replacement episodes exactly 0/8/16/24/32;
four unique IDs each.

P5:
W5 future leakage impossible.

P6:
ledger contribution mapping exactly:
positive +1;
zero 0;
negative -1.

P7:
ledger score equals exact sum of immutable records.

P8:
prior ledger digest chain exact.

P9:
contradictory evidence subtracts one
and does not delete prior records.

P10:
neutral evidence changes neither score
nor historical evidence.

P11:
no full candidate authority before W5.

P12:
C1/C2/C3 exposure limits exact
through all provisional windows.

P13:
NO_EXPANSION leaves learned patch preserved.

P14:
two complete primary sweeps byte-identical.

P15:
no C-v3;
no duplicate context;
major history [v1,v2];
slot count 3.

NEGATIVE / LIMIT CONTROLS

N1 — RESET LEDGER AFTER NONPOSITIVE WINDOW

Expected to reproduce the information loss
of consecutive-win hysteresis.

N2 — IGNORE NEGATIVE WINDOWS

Unsafe confidence ratchet.

N3 — WEIGHT POSITIVE MARGIN BY MAGNITUDE

Not authorized in A23.
A21 showed margin magnitude alone
did not establish safety.

N4 — INSPECT W5 BEFORE DECISION

Invalid future leakage.

N5 — DELETE PATCH BELOW THRESHOLD

Invalid learned-memory destruction.

N6 — FULL ACTIVATE BEFORE SCORE +2

Outside A23 authority boundary.

N7 — CORRELATED / NONSTATIONARY WINDOWS

Boundary.

A23 derives independent deterministic window namespaces,
but real-world dependence remains a later research problem.

INTERPRETATION

A23 tests whether the problem in A22
was evidence forgetting.

If A23 materially raises coverage
while retaining the A22 safety improvement,
that supports a persistent confidence representation.

If coverage rises
but harm returns toward A21 levels,
nonconsecutive positive windows are not interchangeable evidence
and the ledger requires stronger temporal weighting.

If coverage remains too low,
the problem is not merely consecutive-win reset;
the canary observation process itself
does not provide enough information.

PLAIN-SPEAK QUESTION

A22 made Yggdrasil prove itself twice.

That made it safer,
but almost every patch got stuck waiting.

The problem is that A22 effectively forgot partial evidence.

If a patch did well,
then had a neutral or bad stretch,
its earlier success stopped helping.

A23 gives each learned patch a small confidence notebook.

Every real trial writes one permanent line:

worked: +1;
tie: 0;
hurt: -1.

Nothing gets erased.

Contradictory evidence counts against confidence.

Neutral evidence does not fake confidence.

After four small real trials,
a patch needs at least two more wins than losses
to earn full authority for a completely untouched fifth window.

So A23 asks:

CAN YGGDRASIL REMEMBER EVIDENCE
WITHOUT BECOMING GULLIBLE?

That is closer to real confidence calibration
than a simple win-twice switch.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-IMPLEMENTATION CLARIFICATION 01 — W5 NO-EXPANSION STATE

DATE:
2026-09-21.

STATUS:
LOCKED BEFORE A23 IMPLEMENTATION FREEZE
AND BEFORE ANY REAL F23-DERIVED TRAJECTORY.

At the epoch-32 boundary:

EARNED_EXPANSION:

continue the provisional canary trajectory;
apply 4 / 4 candidate-controlled newborn births.

NO_EXPANSION:

discard the provisional canary trajectory at the W5 boundary;
restore the exact matched stale-twin state;
apply 4 / 4 stale-controlled newborn births.

Reason:

NO_EXPANSION must mean no residual unearned candidate authority
enters the untouched confirmation window.

This clarification changes no ledger threshold,
no window,
no exposure arm,
no demand generation,
and no qualification criterion.

No A23 outcome has been observed.



PRE-RUN IMPLEMENTATION FREEZE 01 — A23 PERSISTENT PATCH CONFIDENCE LEDGER

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL F23-DERIVED TRAJECTORY
OR REAL A23 LEDGER OUTCOME.

IMPLEMENTATION COMMIT

266cd2111713b271c084172d7b666fa38aecdb3d.

SOURCE BUNDLE

Loader:

research/applications/track-a/a23_t8g_persistent_patch_confidence_ledger_v1.py

Loader Git blob:

918654e8ad050addac1e25e185459a5406042488.

Payload:

research/applications/track-a/a23_t8g_persistent_patch_confidence_ledger_v1.py.gz

Payload Git blob:

567da43bb219803d1ecf6774da1ac47151857bdb.

Decompressed source SHA-256:

05a9c9bf631282189160ebf7c2ad088b6212318440b561d7a4f613a2714763e0.

Decompressed source bytes:

13290.

Deterministic gzip SHA-256:

26a81c5c527ea21b836bc6f3d4ba9e33c7f68e50bc4f4b1c8c87aa5c5f2366b5.

Compressed payload bytes:

4574.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake freeze:

MECHANICAL-F23-NONPRIMARY.

Two complete sweeps were byte-identical.

Serialized result-file SHA-256:

4abbc2e61c74c965bf1355e3e3f4cd34bc9703dffbf6cdba1c8b07b31ac7f204.

Serialized semantic output SHA-256:

462bd5413b6144d2741f0bbb8ee82495bd2775d0156159fcf770c63d4f462fce.

All P1-P15 integrity probes:

PASS.

Exact A17 replay:

3978 candidate first-four;
3950 stale first-four;
37 / 48 candidate >= stale;
exact 11 below-stale pairs reproduced.

384 unique fake trajectories:

PASS.

40-epoch exact target means:

PASS.

Replacement episodes:

0 / 8 / 16 / 24 / 32.

Digest-chained confidence ledger:

PASS.

Restart equivalence:

PASS.

No W5 leakage:

PASS.

Mechanical science result:

no arm qualified.

C1:
earned expansions = 13;
actual harm rate = 0.4615384615.

C2:
earned expansions = 29;
actual harm rate = 0.2758620690.

C3:
earned expansions = 50;
actual harm rate = 0.22.

These values are NON-SCIENTIFIC.
They demonstrate that the +2 ledger rule does not trivially satisfy
the preregistered safety / coverage criteria.

REAL A23 STATUS

No real F23 trajectory has been derived.

No real A23 manifest exists.

No real ledger score,
earned expansion,
or W5 outcome
has been observed.

Let the resulting commit SHA be:

F23.

After F23 exists:

1. derive exactly 384 fresh 40-epoch trajectories from F23;
2. bind the complete manifest SHA;
3. only then execute two complete deterministic primary sweeps;
4. require byte-identical output;
5. apply the frozen C1 -> C2 -> C3 minimum-exposure selection hierarchy.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A23 PERSISTENT PATCH CONFIDENCE LEDGER

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A23 LEDGER UPDATE
OR W5 OUTCOME.

F23:

e73591a5d9671aba5c7edb9ebf378478c2957a79.

FROZEN SOURCE SHA-256:

05a9c9bf631282189160ebf7c2ad088b6212318440b561d7a4f613a2714763e0.

TRAJECTORY COUNT:

384.

STRUCTURE:

48 fixed A17 patch contexts
x
8 fresh F23-derived replicas.

EPOCHS PER TRAJECTORY:

40.

PROVISIONAL WINDOWS:

W1 = 0-7;
W2 = 8-15;
W3 = 16-23;
W4 = 24-31.

UNTOUCHED CONFIRMATION:

W5 = 32-39.

REPLACEMENT EPISODES:

0 / 8 / 16 / 24 / 32.

COMPLETE MANIFEST SHA-256:

c720f03dcd6d509c13570b9f6b72936692c7733483a1761d778fd4b122e18580.

Serialized manifest-wrapper SHA-256:

b7bb48953dd8689a097331d69590780248973321bed301c30b9e213fa3e1293e.

Serialized manifest-wrapper bytes:

239571.

Every 40-demand sequence has exact mean equal to its candidate target.

Every replacement episode contains exactly four unique cell IDs.

All trajectory namespaces are:

YGG-A23-*

and are distinct from A17-A22.

PRIMARY STATUS AT MANIFEST BIND

A23 ledger records observed:

0.

A23 earned expansions observed:

0.

A23 W5 outcomes observed:

0.

A23 selected arm:

NONE / NOT YET EVALUATED.

The next permitted operation is:

two complete deterministic A23 primary sweeps
over this exact manifest.

NO TRAJECTORY REDRAW.
NO THRESHOLD CHANGE.
NO SCORE-MAPPING CHANGE.
NO EXPOSURE CHANGE.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A23 / T8G PERSISTENT PATCH CONFIDENCE LEDGER

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE NEGATIVE RESULT /
PERSISTENT SIGN-LEDGER RECOVERS SOME COVERAGE
BUT FAILS SAFETY /
NO ARM QUALIFIED /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

266cd2111713b271c084172d7b666fa38aecdb3d.

F23:

e73591a5d9671aba5c7edb9ebf378478c2957a79.

Source SHA-256:

05a9c9bf631282189160ebf7c2ad088b6212318440b561d7a4f613a2714763e0.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

1919e140cfc6717dcb51640ffb3c88024197c7d0.

384-trajectory manifest SHA-256:

c720f03dcd6d509c13570b9f6b72936692c7733483a1761d778fd4b122e18580.

Manifest-wrapper SHA-256:

b7bb48953dd8689a097331d69590780248973321bed301c30b9e213fa3e1293e.

PRIMARY REPRODUCIBILITY

Two complete primary sweeps were byte-identical.

Serialized result-file SHA-256:

6bddfb7adf60b66e76c0e4e8bb7a1225c6cc30c895cf0ed34b9591682d256706.

Serialized semantic output SHA-256:

75dcaa50c6e704fb546b74c852b095102eef747378301f9386adb10b5a782416.

All P1-P15 probes:

PASS.

A17 replay remained exact.

FRESH R1 W5 BASELINE

Unconditional all-candidate W5 harmful trajectories:

64 / 384.

Unconditional harm rate:

0.1666666667.

C1 — 25% PROVISIONAL EXPOSURE

Earned expansions:

12.

Actual W5 outcomes:

beneficial = 3;
neutral = 5;
harmful = 4.

Actual harm rate:

0.3333333333.

R1 W5 labels among earned expansions:

beneficial = 1;
neutral = 9;
harmful = 2.

R1-label harm rate:

0.1666666667.

Provisional W1-W4 aggregate delta versus stale twins:

+23.

W5 aggregate delta:

0.

Complete service delta versus R0:

+23.

Complete service delta versus R1:

-784.

Coverage floor:

FAIL.

Harm ceiling:

FAIL.

C1 LEDGER-QUALIFIED:

FALSE.

C2 — 50% PROVISIONAL EXPOSURE

Earned expansions:

23.

Actual W5 outcomes:

beneficial = 7;
neutral = 9;
harmful = 7.

Actual harm rate:

0.3043478261.

R1 labels:

beneficial = 6;
neutral = 10;
harmful = 7.

R1-label harm rate:

0.3043478261.

Provisional aggregate delta:

-39.

W5 aggregate delta:

+2.

Complete delta versus R0:

-37.

Complete delta versus R1:

-844.

Coverage floor:

FAIL.

Harm ceiling:

FAIL.

C2 LEDGER-QUALIFIED:

FALSE.

C3 — 75% PROVISIONAL EXPOSURE

Earned expansions:

45.

Actual W5 outcomes:

beneficial = 12;
neutral = 22;
harmful = 11.

Actual harm rate:

0.2444444444.

R1 labels:

beneficial = 11;
neutral = 24;
harmful = 10.

R1-label harm rate:

0.2222222222.

Provisional aggregate delta:

-12.

W5 aggregate delta:

+2.

Complete delta versus R0:

-10.

Complete delta versus R1:

-817.

Coverage:

45 / 48 minimum.

FAIL.

Harm ceiling:

FAIL.

C3 LEDGER-QUALIFIED:

FALSE.

PRIMARY RESULT

Selected arm:

NONE.

A23_PERSISTENT_PATCH_CONFIDENCE_LEDGER_SUCCESS:

FALSE.

COMPARISON WITH A22

A22 C3:

earned expansions = 16;
actual harm rate = 0.0625.

A23 C3:

earned expansions = 45;
actual harm rate = 0.2444444444.

Thus persistent nonconsecutive sign accumulation
recovered substantial coverage
but reintroduced a large false-positive activation rate.

The A22 coverage problem
was therefore not merely caused by forgetting old positive evidence.

EVIDENCE-PATTERN DIAGNOSTIC

No simple sign-pattern repair is supported.

Observed harmful earned expansions included patterns such as:

++++;
++00;
00++;
+00+;
0+0+;
+++0;
+-++.

For C3:

last window positive:
28 earned;
7 harmful;
harm rate 0.25.

last window neutral:
15 earned;
3 harmful;
harm rate 0.20.

last window negative:
2 earned;
1 harmful;
harm rate 0.50.

C3 with no negative provisional window:

38 earned;
9 harmful;
harm rate 0.2368421053.

Therefore:

recent positivity;
absence of negative windows;
or multiple positive windows

does not by itself establish safe W5 authority.

Even:

++++

contained a harmful W5 outcome.

TECHNICAL INTERPRETATION

A23 falsifies the hypothesis:

A22 WAS TOO INDECISIVE
BECAUSE IT FORGOT NONCONSECUTIVE POSITIVE EVIDENCE.

Keeping all signed evidence
does increase authority coverage.

But equal-weight sign accumulation
treats evidence as more interchangeable than it really is.

A positive window carries no explicit representation of:

effect magnitude uncertainty;
within-window variability;
state dependence;
trajectory dependence;
or how surprising the observed advantage was
under a no-benefit baseline.

A21 had already shown that raw positive margin
was not enough.

A23 now shows that repeated positive signs
are also not enough.

The missing object is therefore not merely:

MEMORY OF EVIDENCE.

It is:

CALIBRATED UNCERTAINTY ABOUT EVIDENCE.

A confidence ledger should not store only:

WIN / TIE / LOSS.

It must represent
how much statistical / causal support
each observation contributes
and how uncertain that support remains.

PLAIN-SPEAK INTERPRETATION

A23 gave every patch a notebook.

Good trial:
+1.

Tie:
0.

Bad trial:
-1.

The notebook remembered everything.

That solved one A22 problem:

more patches eventually accumulated enough evidence
to be considered for full authority.

But it made the organism too trusting again.

For the largest canary arm,
A22 approved only 16 cases
and was much safer.

A23 approved 45.

But 11 of those 45 expansions hurt in the untouched fifth window.

So simply remembering old wins
is not enough.

The biggest lesson is:

A WIN IS NOT A STANDARD UNIT OF EVIDENCE.

One positive window may be strong evidence.

Another positive window may be mostly noise.

Counting them both as +1
throws away the exact thing Yggdrasil now needs to understand:

HOW CERTAIN AM I
THAT THIS OBSERVED IMPROVEMENT IS REAL AND PERSISTENT?

That points to the next experiment.

Do not invent another pattern rule.

Do not just raise +2 to +3.

Do not only require the most recent window to be positive.

Instead,
give the ledger an uncertainty-aware evidence quantity.

The next experiment should accumulate
paired canary-versus-stale evidence
with an explicit lower confidence bound
or anytime-valid evidence process.

Authority should be earned only when
the evidence says not merely:

"we have seen more wins than losses,"

but:

"the accumulated evidence is strong enough
that a non-beneficial patch is becoming implausible."

A17:
mixed / negative.

A18:
diagnostic.

A19:
shadow confidence insufficient.

A20:
known-world real-canary discovery.

A21:
one-hit out-of-sample replication failed.

A22:
two-hit hysteresis safer but too indecisive.

A23:
persistent sign ledger increases coverage
but fails safety.

No sequential autonomous activation controller is authorized.

DG-1R-05 remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
