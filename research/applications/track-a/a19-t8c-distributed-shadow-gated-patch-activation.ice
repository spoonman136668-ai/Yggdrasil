TITLE: YGGDRASIL A19 / T8C — Distributed Shadow-Gated Patch Activation Calibration
DATE: 2026-09-21
STATUS: PREREGISTERED CALIBRATION EXPERIMENT / NON-ACCEPTING / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8C / APPLICATION-A
PARENT: A18 Local Turnover Geometry and Horizon Attribution
BRANCH: dg1a-ar

PURPOSE

A18 established that A17's learned bounded patches were structurally correct,
but learning a correct developmental target
and immediately using that target as a birth-control prior
are not equivalent operations.

A18 found:

0 / 11 A17 losses were repaired by extending the score to all 16 epochs;

4 / 11 losing evaluations had material replacement-geometry sensitivity;

4 / 11 had material inherited-state / partial-turnover sensitivity;

11 / 11 contained local birth-prior objective mismatch.

Therefore A19 separates:

PATCH LEARNING

from

PATCH ACTIVATION.

A learned patch may exist durably
without automatically gaining authority over newborn-cell specialization.

A19 asks whether bounded counterfactual shadow evaluation
performed by independent healthy evaluator lineages
can predict when a learned patch should be activated
and when the currently active prior should remain in control.

A19 is a calibration experiment.

It does NOT reopen A17 acceptance.
It does NOT select a final activation gate post hoc.
It compares three preregistered activation rules
on the same frozen held-out worlds.

RESEARCH CONTEXT

The architecture follows the general safe-policy-improvement principle
that a proposed update should be evaluated against a trusted baseline
before adoption.

Recent external work also motivates:

restricted / local policy updates;
baseline non-inferiority;
predictive evaluation before takeover;
and fallback to an existing policy when confidence is insufficient.

A19 does not import an RL implementation.

It tests an analogous developmental-control rule
inside Yggdrasil's synthetic cellular architecture.

FROZEN SCIENTIFIC INPUT

Original A17 scientific seed F17:

3ec24f8242285688a537f5e7dd6e9a231a645597.

Corrected A17 executable freeze F17A:

c33df49a8b171c1f6cd8e64820dd3bca0e2f4492.

A17 primary manifest SHA-256:

8284e3f1e47a17f234eb02f2b427cddaee16999e0df795d38f1b0b457cf8e43f.

A17 corrected primary result SHA-256:

ee53b151295a5d31ba1e54e4cd8d4deae0aff604ff3b66406fb87b748a08306d.

A18 closure:

80d4801a636ef527ae35dd424a9bb11f7fd70d57.

The exact 48 A17 patch-evaluation worlds
and exact A17 pre-evaluation candidate cell states
are reused unchanged.

No A19 decision may inspect or derive from the A17 held-out evaluation demands.

A19 FREEZE

Let the exact A19 implementation freeze commit be:

F19.

Only after F19 exists may A19 derive
its new shadow-activation evidence.

SHADOW EVIDENCE

After a patch has already satisfied
all A17-FIXA learning / provenance / ancestry rules,
but before held-out activation evaluation,
collect exactly:

4

additional provenance-qualified shadow observations.

These observations are NOT used to learn the patch target.

They exist only to evaluate whether activation is locally justified.

For scenario s and patch k,
derive two symmetric zero-mean pairs around the already-learned target
using only:

F19;
scenario;
patch;
pair index;

under tag:

YGG-A19-SHADOW-OBS.

Thus the four-observation exact mean remains the learned patch target.

No held-out A17 evaluation demand is visible.

SHADOW PROVENANCE

Every shadow observation requires:

two distinct observation roots.

Roots are post-F19 derived under:

YGG-A19-SHADOW-ATTEST.

Same-root fanout does not qualify.

Four unique qualified observations are required.

No duplicate-copy evidence weighting.

INDEPENDENT SHADOW EVALUATORS

Two distinct healthy evaluator lineages:

SHADOW_EVALUATOR_A_ROOT = 1 << 48.

SHADOW_EVALUATOR_B_ROOT = 1 << 49.

They are distinct from:

A17 learner roots;
A14 observation roots.

Each evaluator independently reconstructs:

the exact four shadow observations;
the exact current pre-evaluation cell state;
the learned target prior;
the stale-previous active prior;
all 495 four-cell replacement sets.

Each evaluator enumerates the 495 sets
in a separately derived deterministic order.

Order may differ between evaluators.

Final geometry statistics must agree exactly.

No single evaluator can authorize activation.

SHADOW GEOMETRY REPLAY

For every four-cell replacement set:

C(12,4) = 495,

use the exact A17 pre-evaluation cell state.

Order the four chosen cell IDs
by a deterministic F19-bound shadow replacement-order hash
that is independent of candidate / stale policy.

Fork the same state into:

candidate shadow;

stale-baseline shadow.

Candidate shadow:

recreate the four cells using the learned patch target
as birth-role prior.

Stale shadow:

recreate the same four cells,
in the same order,
using the previous active developmental prior.

Then score the same four shadow observations
with the inherited migration rule.

For each geometry g:

delta(g) =
candidate shadow service
-
stale shadow service.

The evaluator summary contains:

minimum delta;
maximum delta;
mean delta;
median delta;
fraction delta >= 0;
fraction delta > 0;
complete deterministic delta histogram.

No held-out evaluation information is used.

PREREGISTERED ACTIVATION ARMS

G0 — ALWAYS PATCH

Reference only.

Equivalent to A17 automatic activation.

G1 — WORST-CASE-SAFE

Activate iff:

minimum geometry delta >= 0

AND

mean geometry delta > 0.

Otherwise:

patch remains learned but dormant;
stale-previous prior retains birth-control authority.

G2 — SUPERMAJORITY

Activate iff:

fraction of geometries with delta >= 0
>= 0.75

AND

mean geometry delta > 0.

Otherwise remain dormant.

G3 — POSITIVE-MEAN

Activate iff:

mean geometry delta > 0.

Otherwise remain dormant.

G4 — ALWAYS STALE

Reference only.

No gate arm may be modified after F19 shadow evidence is derived.

No arm may use held-out outcome signs.

HELD-OUT EVALUATION

After each gate decision,
evaluate on the exact corresponding frozen A17 16-epoch held-out sequence
with exact A17 replacement episodes:

0 and 8

and exact canonical A17 replacement targets.

For each patch evaluation:

if gate activates:
use the learned target prior.

if gate holds:
use the stale-previous prior.

The exact A17 pre-evaluation state is used.

A19 deliberately evaluates each patch decision independently
from the frozen A17 pre-evaluation state.

A19 does NOT yet test cascading sequential gate decisions.

That is reserved for a later experiment
if one activation rule is scientifically justified.

CALIBRATION METRICS

For each G1 / G2 / G3 arm report:

activation count;

dormant count;

held-out harmful activations:
activated and candidate < stale;

held-out beneficial activations:
activated and candidate > stale;

held-out neutral activations:
activated and candidate == stale;

missed beneficial opportunities:
dormant while candidate > stale;

avoided harmful activations:
dormant while candidate < stale;

first-four aggregate service;

full-16 aggregate service;

aggregate delta versus always-stale;

aggregate delta versus always-patch;

activation precision for strictly beneficial outcomes;

activation recall for strictly beneficial outcomes.

Report the complete 48-decision table.

A19 has no pass / fail winner.

No arm becomes canonical
because it has the highest observed score.

The purpose is calibration:

how much coverage must be sacrificed
to reduce harmful activation.

CONFIDENCE CALIBRATION

For every patch,
record:

shadow fraction delta >= 0;

shadow mean delta;

shadow minimum delta;

held-out candidate-minus-stale first-four delta;

held-out full-16 delta.

Measure whether stronger shadow confidence
corresponds to lower held-out harm.

Report calibration by fixed preregistered bins:

[0.00,0.25);
[0.25,0.50);
[0.50,0.75);
[0.75,1.00);
1.00 exactly.

Do not choose new bins after results.

DEDICATED PROBES

P1 — SAME-ROOT SHADOW FANOUT

Required:

shadow observation not qualified.

P2 — FEWER THAN FOUR SHADOW OBSERVATIONS

Required:

no activation decision;
ABSTAIN / INSUFFICIENT_SHADOW_EVIDENCE.

P3 — EVALUATOR ROOT COLLISION

If evaluator A root == evaluator B root:

required reject.

P4 — EVALUATOR DISAGREEMENT

If evaluator summary differs:

required reject;
no activation.

P5 — HELD-OUT LEAKAGE

A gate input containing any held-out A17 demand identity:

required invalid experiment / fail closed.

P6 — WORST-CASE-SAFE ZERO-MEAN

If min >= 0 but mean == 0:

G1 must remain dormant.

P7 — SUPERMAJORITY BELOW 0.75

If non-inferior fraction < 0.75:

G2 must remain dormant.

P8 — POSITIVE-MEAN NONPOSITIVE

If mean <= 0:

G3 must remain dormant.

P9 — DORMANT PATCH PRESERVATION

Holding activation must NOT delete
or mutate the learned patch record.

P10 — ACTIVE PRIOR PRESERVATION

A dormant patch must leave
the stale-previous birth-control prior active.

NEGATIVE / LIMIT CONTROLS

N1 — ALWAYS ACTIVATE

Expected to reproduce A17 harmful activations.

N2 — USE HELD-OUT DEMANDS IN SHADOW

Invalid leakage.
Expected artificially optimistic calibration.

N3 — SINGLE EVALUATOR AUTHORITY

Unsafe evaluator-corruption shortcut.

N4 — AUTO-DELETE DORMANT PATCH

Unsafe learned-memory loss.

N5 — ACTIVATE ON MEAN ALONE

Represented by G3.
Expected greater coverage
with potentially weaker protection than G1 / G2.

N6 — SHADOW MODEL MISMATCH

Boundary.

A19 uses exact inherited transition / migration rules.
Real model error is not solved here.

N7 — CASCADING ACTIVATION DECISIONS

Boundary.

A19 evaluates each decision from the frozen A17 pre-evaluation state.
Sequential interaction between gate decisions remains untested.

INTERPRETATION RULE

A19 should identify a safety / coverage frontier,
not a post-hoc winner.

If G1 blocks nearly everything,
that is evidence that worst-case geometry robustness is too conservative.

If G3 activates harmful patches,
that is evidence that mean shadow benefit alone is insufficient.

If G2 retains materially more beneficial activations than G1
while avoiding substantially more harmful activation than G3,
that is evidence that distributed supermajority confidence
deserves a separate sequential preregistered test.

That later choice must be made in a new experiment,
not by rewriting A19.

PLAIN-SPEAK PREREGISTERED QUESTION

A17 let a learned patch immediately take control.

A18 showed that was too simple.

A patch can be correct
and still be the wrong thing to activate right now.

A19 gives Yggdrasil a rehearsal room.

It learns the patch exactly as before.

Then two independent healthy evaluator groups
replay the new patch and the old policy
against four new observations
across every possible set of four cells that might be replaced.

The patch is allowed to exist in memory
even if it does not get control.

We compare three attitudes:

very cautious;
three-quarters consensus;
and average-benefit only.

Then we expose all three decisions
to the same untouched held-out worlds.

We are not picking a winner after the fact.

We are measuring:

how cautious does self-evaluation need to be
before a developmental update is allowed to act?

That moves Yggdrasil from:

LEARN -> ACT

toward:

LEARN
->
PRESERVE
->
SELF-EVALUATE
->
CONSENSUS
->
ACT OR REMAIN DORMANT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A19 DISTRIBUTED SHADOW ACTIVATION CALIBRATION

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL A19 SHADOW OBSERVATION,
SHADOW ATTESTATION,
EVALUATOR GEOMETRY ORDER,
OR ACTIVATION DECISION.

IMPLEMENTATION COMMIT

05ce27bf71d47e54d65599317fad61658bb2aafa.

SOURCE BUNDLE

Loader:

research/applications/track-a/a19_t8c_shadow_activation_calibration_v1.py

Loader Git blob:

708b958c0976dea8976d96f7d0a0bb84aae8c3e5.

Payload:

research/applications/track-a/a19_t8c_shadow_activation_calibration_v1.py.gz

Payload Git blob:

2dbc72e820f815ca0ed8845e617f718bb91890a6.

Decompressed source SHA-256:

d9637729a6b53526efd4a3fb7f90f37efea6185ab5f0f863419a63cff8ad649f.

Decompressed source bytes:

23829.

Deterministic gzip SHA-256:

42665aa79a3c6b12b9f184d2dfbc71134adc6e9e7a8368962796afcc2812cf2e.

Compressed payload bytes:

6733.

LINEAGE VALIDATION

The exact source independently reconstructs and verifies:

A11 manifest:
b0e00f29d36637a1365ab2407678aacf232ac4f4cf05d387f68af975a5b4bedd.

A12 manifest:
502009818ea9d6e57089a91424e7cf399e7c5e95024a9623816e733c58c3f63a.

A14 exact-F14 manifest:
83a0ad4d67d7a3f3625e49c311f5d2a85c73fee40cde96e24937ae79e1e944ae.

Exact A17 replay:
candidate first-four 3978;
stale first-four 3950;
target-policy reference 3978;
candidate >= stale 37 / 48;
migrations avoided 38.

Exact 11 A17 below-stale pairs:

S00/P1;
S00/P2;
S00/P3;
S02/P4;
S04/P1;
S04/P2;
S04/P3;
S10/P2;
S10/P4;
S11/P1;
S11/P4.

MECHANICAL PRECHECK — NON-EVIDENCE

Two complete fake-freeze sweeps using:

MECHANICAL-F19

were byte-identical.

Serialized output SHA-256:

6f0784b0b7f9b896119168fe4c38a77cd8482d555752eb27ae09d743bf205637.

Serialized file SHA-256:

26429edc06c3a2fa40293135cb26c603f5fe22123d69f5558c82a83a0c47bea3.

Both independent evaluator lineages enumerated all:

495

four-cell geometries per patch
and produced identical order-independent summaries.

Mechanical source / gate logic:

PASS.

The fake-freeze calibration values remain NON-SCIENTIFIC.
They were observed only to validate deterministic execution
and may not be used to tune G1 / G2 / G3.

PRIMARY SHADOW STATUS

No real F19-derived shadow evidence exists yet.

No real A19 activation decision exists yet.

No real A19 held-out gated evaluation exists yet.

Let the resulting commit SHA of this freeze record be:

F19.

Only after F19 exists may the harness derive:

- four shadow observations per patch;
- shadow attestations;
- independent evaluator enumeration orders;
- shadow confidence statistics;
- G1 / G2 / G3 activation decisions.

NO POST-FREEZE GATE TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — A19 / T8C DISTRIBUTED SHADOW-GATED PATCH ACTIVATION CALIBRATION

DATE:
2026-09-21.

STATUS:
CLOSED / REPRODUCIBLE CALIBRATION RESULT /
FOUR-OBSERVATION SHADOW CONFIDENCE NOT SUFFICIENT FOR ACTIVATION AUTHORITY /
NO GATE SELECTED /
NON-ACCEPTING /
NON-CANONICAL.

FROZEN HARNESS

Implementation commit:

05ce27bf71d47e54d65599317fad61658bb2aafa.

F19:

b28ee8335d6c3555e42d503d685241cd6a986e73.

Source SHA-256:

d9637729a6b53526efd4a3fb7f90f37efea6185ab5f0f863419a63cff8ad649f.

PRIMARY REPRODUCIBILITY

Two complete real F19-derived A19 sweeps.

Sweep 1 serialized file SHA-256:

9af7551fb882112f07071fb78fe81780e149bfdf4fb7f800067c18e40c7fe6c3.

Sweep 2 serialized file SHA-256:

9af7551fb882112f07071fb78fe81780e149bfdf4fb7f800067c18e40c7fe6c3.

Byte-identical:

TRUE.

Serialized semantic output SHA-256:

cd589be645a91331be28bf48e61778936909264494c36ba8ded0735e1d7cbcd1.

LINEAGE INTEGRITY

A11 / A12 / A14 exact manifest hashes:

MATCH.

A17 exact replay:

3978 candidate first-four;
3950 stale first-four;
3978 target-policy reference;
37 / 48 candidate >= stale;
38 migrations avoided.

Exact 11 A17 harmful first-four activations:

MATCH.

Every shadow evaluator enumerated:

495

four-cell geometries.

Independent evaluator summaries:

EXACT MATCH.

No held-out A17 demand was used by any activation gate.

G1 — WORST-CASE-SAFE

Rule:

minimum shadow geometry delta >= 0
AND
mean shadow geometry delta > 0.

Activated:

11 / 48.

Dormant:

37 / 48.

Held-out first-four:

beneficial activations = 6;
neutral activations = 3;
harmful activations = 2.

Avoided harmful A17 activations:

9 / 11.

Missed beneficial A17 opportunities:

17 / 23.

First-four service:

3958.

Always-stale first-four:

3950.

G1 delta versus always-stale:

+8.

Always-patch A17 first-four:

3978.

G1 delta versus always-patch:

-20.

Full-16 service:

7913.

Always-stale full-16:

7906.

G1 full-16 delta versus always-stale:

+7.

Always-patch full-16:

7929.

G1 full-16 delta versus always-patch:

-16.

Strictly beneficial first-four activation precision:

6 / 11.

Strictly beneficial first-four activation recall:

6 / 23.

Held-out first-four harmful G1 activations:

S00/P3;
S11/P4.

Held-out full-16 harmful G1 activations:

S00/P3;
S11/P2;
S11/P4.

Thus even the strictest preregistered shadow rule
does NOT establish non-degrading activation authority.

CRITICAL G1 FALSE-CONFIDENCE CASES

S00/P3:

shadow fraction candidate >= stale:
1.000;

shadow minimum delta:
+1;

shadow mean delta:
+1.000;

held-out first-four delta:
-1;

held-out full-16 delta:
-1.

S11/P4:

shadow fraction candidate >= stale:
1.000;

shadow minimum delta:
+1;

shadow mean delta:
+1.762;

held-out first-four delta:
-1;

held-out full-16 delta:
-1.

These patches looked favorable
for every one of the 495 shadow replacement geometries
and still underperformed on independent held-out demand.

Therefore:

EXHAUSTIVE GEOMETRY ROBUSTNESS
ON FOUR SHADOW OBSERVATIONS

does not imply:

HELD-OUT ACTIVATION SAFETY.

G2 — SUPERMAJORITY

Rule:

shadow fraction candidate >= stale >= 0.75
AND
mean shadow delta > 0.

Activated:

32 / 48.

Dormant:

16 / 48.

Held-out first-four:

beneficial activations = 17;
neutral activations = 8;
harmful activations = 7.

Avoided harmful A17 activations:

4 / 11.

Missed beneficial opportunities:

6 / 23.

First-four service:

3971.

Delta versus always-stale:

+21.

Delta versus always-patch:

-7.

Full-16 service:

7923.

Full-16 delta versus always-stale:

+17.

Full-16 delta versus always-patch:

-6.

Strictly beneficial first-four precision:

17 / 32.

Strictly beneficial first-four recall:

17 / 23.

First-four harmful G2 activations:

S00/P1;
S00/P2;
S00/P3;
S04/P1;
S10/P2;
S10/P4;
S11/P4.

Full-16 harmful G2 activations:

S00/P1;
S00/P2;
S00/P3;
S01/P4;
S04/P1;
S10/P2;
S10/P4;
S11/P2;
S11/P4.

G3 — POSITIVE-MEAN

Rule:

mean shadow delta > 0.

Observed decisions were exactly identical to G2:

32 / 48 activate.

Therefore on this frozen F19 shadow evidence:

every positive-mean case also had
at least 75% non-inferior geometries.

G3 metrics are therefore exactly equal to G2.

This means the preregistered 0.75 supermajority threshold
added no discrimination on this particular evidence set.

It must not be interpreted as a general equivalence.

CONFIDENCE CALIBRATION

Fixed preregistered bins
using shadow fraction candidate >= stale.

[0.00,0.25):

count = 2;
beneficial held-out = 2;
neutral = 0;
harmful = 0;
mean held-out first-four delta = +1.0.

[0.25,0.50):

count = 3;
beneficial = 1;
neutral = 0;
harmful = 2;
mean held-out delta = 0.0.

[0.50,0.75):

count = 3;
beneficial = 0;
neutral = 2;
harmful = 1;
mean held-out delta = -0.3333.

[0.75,1.00):

count = 26;
beneficial = 13;
neutral = 7;
harmful = 6;
mean held-out delta = +0.6923.

1.00 exactly:

count = 14;
beneficial = 7;
neutral = 5;
harmful = 2;
mean held-out delta = +0.6429.

The confidence signal has useful information,
but it is not calibrated strongly enough
to function as an activation certificate.

In particular:

100% shadow non-inferiority still contains harmful held-out activations.

COMPLETE 48-DECISION TABLE

Legend:

shadow>= =
fraction of 495 shadow geometries where candidate >= stale.

meanΔ =
mean shadow candidate-minus-stale service.

minΔ =
worst shadow geometry delta.

heldout Δ4 =
A17 first-four candidate minus stale.

Δ16 =
complete 16-epoch candidate minus stale.

A =
activate.

H =
hold dormant.

S/P | shadow>= | meanΔ | minΔ | heldout Δ4 | Δ16 | G1 | G2 | G3
S00/P1 | 0.758 | +0.069 | -2 | -1 | -2 | H | A | A
S00/P2 | 0.964 | +0.194 | -1 | -1 | -1 | H | A | A
S00/P3 | 1.000 | +1.000 | +1 | -1 | -1 | A | A | A
S00/P4 | 0.889 | +0.834 | -1 | +1 | +1 | H | A | A
S01/P1 | 0.970 | +1.459 | -2 | +1 | +1 | H | A | A
S01/P2 | 1.000 | +1.935 | +0 | +1 | +1 | A | A | A
S01/P3 | 0.000 | -1.000 | -1 | +1 | +0 | H | H | H
S01/P4 | 0.998 | +1.451 | -1 | +0 | -1 | H | A | A
S02/P1 | 1.000 | +0.010 | +0 | +0 | +0 | A | A | A
S02/P2 | 0.745 | -0.065 | -2 | +0 | +0 | H | H | H
S02/P3 | 0.838 | +0.691 | -4 | +2 | +2 | H | A | A
S02/P4 | 0.992 | +0.000 | -1 | -1 | -2 | H | H | H
S03/P1 | 0.921 | +0.624 | -1 | +1 | +1 | H | A | A
S03/P2 | 1.000 | +1.727 | +0 | +1 | +1 | A | A | A
S03/P3 | 0.962 | +0.885 | -1 | +1 | +1 | H | A | A
S03/P4 | 0.901 | +0.354 | -1 | +0 | +1 | H | A | A
S04/P1 | 0.879 | +0.012 | -1 | -2 | -3 | H | A | A
S04/P2 | 0.424 | -0.576 | -1 | -1 | -2 | H | H | H
S04/P3 | 0.598 | -0.485 | -2 | -1 | -1 | H | H | H
S04/P4 | 0.869 | -0.042 | -1 | +0 | +0 | H | H | H
S05/P1 | 0.299 | -0.533 | -3 | +4 | +3 | H | H | H
S05/P2 | 1.000 | +0.572 | +0 | +2 | +1 | A | A | A
S05/P3 | 0.939 | +0.505 | -1 | +2 | +3 | H | A | A
S05/P4 | 0.964 | +0.776 | -1 | +0 | +0 | H | A | A
S06/P1 | 0.838 | +0.345 | -3 | +3 | +3 | H | A | A
S06/P2 | 0.960 | +0.313 | -3 | +0 | +0 | H | A | A
S06/P3 | 0.978 | +1.812 | -3 | +2 | +2 | H | A | A
S06/P4 | 1.000 | +0.970 | +0 | +3 | +4 | A | A | A
S07/P1 | 0.970 | +0.564 | -1 | +1 | +1 | H | A | A
S07/P2 | 1.000 | +0.000 | +0 | +1 | +1 | H | H | H
S07/P3 | 1.000 | +0.745 | +0 | +0 | +0 | A | A | A
S07/P4 | 0.885 | +0.418 | -2 | +2 | +3 | H | A | A
S08/P1 | 0.770 | -0.206 | -1 | +0 | +0 | H | H | H
S08/P2 | 0.608 | -0.335 | -1 | +0 | +0 | H | H | H
S08/P3 | 0.929 | +0.000 | -1 | +3 | +3 | H | H | H
S08/P4 | 1.000 | +0.743 | +0 | +2 | +2 | A | A | A
S09/P1 | 1.000 | +0.000 | +0 | +0 | +1 | H | H | H
S09/P2 | 0.034 | -1.079 | -3 | +1 | +1 | H | H | H
S09/P3 | 1.000 | +0.000 | +0 | +0 | +0 | H | H | H
S09/P4 | 1.000 | +0.186 | +0 | +1 | +1 | A | A | A
S10/P1 | 0.806 | -0.133 | -3 | +3 | +5 | H | H | H
S10/P2 | 0.998 | +1.533 | -1 | -1 | -2 | H | A | A
S10/P3 | 0.970 | +0.939 | -1 | +0 | +0 | H | A | A
S10/P4 | 0.972 | +0.313 | -1 | -1 | -3 | H | A | A
S11/P1 | 0.448 | -0.549 | -2 | -3 | -3 | H | H | H
S11/P2 | 1.000 | +0.970 | +0 | +0 | -1 | A | A | A
S11/P3 | 0.998 | +1.695 | -1 | +3 | +3 | H | A | A
S11/P4 | 1.000 | +1.762 | +1 | -1 | -1 | A | A | A

TECHNICAL INTERPRETATION

A19 establishes that:

LEARNED PATCH
->
EXHAUSTIVE COUNTERFACTUAL SHADOW REPLAY
->
INDEPENDENT EVALUATOR CONSENSUS

is still not sufficient,
when the shadow evidence contains only four new observations.

The failure is not geometry enumeration.

All 495 geometries were evaluated.

The failure is not evaluator disagreement.

Both evaluator lineages agreed exactly.

The failure is not patch learning.

A17 targets are already exact.

The remaining uncertainty is:

FUTURE DEMAND REALIZATION
AND
TRAJECTORY-SPECIFIC STATE EVOLUTION.

A four-observation shadow sample
can be unanimously favorable across all replacement geometries
and still fail to represent the next independent demand sequence.

Therefore healthy-cell consensus can be authoritative
only over the evidence it actually has.

Consensus does not manufacture information.

A19 also shows a real safety / coverage tradeoff:

G1:
much safer,
but misses most beneficial activations.

G2 / G3:
retain much more benefit,
but allow more harmful activations.

No preregistered arm provides enough evidence
to become an autonomous activation authority.

PLAIN-SPEAK INTERPRETATION

We gave Yggdrasil the rehearsal room.

It worked in one sense:

the shadow tests did help.

The strict rule caught 9 of the 11 bad A17 activations.

But it also blocked 17 good patches.

Worse,
two patches looked good under literally every shadow replacement geometry
and still lost when they met a fresh demand sequence.

That teaches us something important.

The evaluator cells were not wrong about the four observations they saw.

They simply had too little evidence
about what was going to happen next.

Even perfect consensus cannot fix that.

If every healthy cell has seen the same small,
unrepresentative slice of the future,
they can all confidently agree
and still make the wrong activation decision.

So Yggdrasil now needs another layer:

not just

SELF-EVALUATION,

but

UNCERTAINTY ABOUT SELF-EVALUATION.

The next experiment should not simply increase the consensus threshold.

A19 already shows that 100% geometry consensus can fail.

The stronger next question is whether activation can be:

PROVISIONAL,
LOW-EXPOSURE,
OBSERVATION-GATHERING,
AND REVERSIBLE.

Instead of deciding:

"activate the whole patch or do nothing"

from four shadow observations,
Yggdrasil could expose only a bounded minority of newborn cells
to the new patch,
watch real post-activation service,
and either:

expand activation;

hold;

or roll the canary cells back.

That would turn uncertainty into controlled evidence
rather than pretending the shadow model has certainty it does not possess.

A19 selects no gate.

A17 remains closed mixed / negative.

A18 remains explanatory.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
