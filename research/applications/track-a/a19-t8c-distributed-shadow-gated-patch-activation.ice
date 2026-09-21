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
