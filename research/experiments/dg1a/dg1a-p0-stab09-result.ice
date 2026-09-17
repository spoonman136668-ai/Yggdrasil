TITLE: DG-1A-P0-STAB-09 — Mature One-Step Background Homeostasis Velocity Control Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
EVIDENCE CLASS: MEASURED SANDBOX

QUESTION
Can canonical P0 preserve meaningful growth and repair while preventing post-viability support expansion if the established continuous background-alpha objective is augmented with a one-step, maturity-gated homeostasis-velocity penalty?

PREREGISTERED CANDIDATE
HOME-1

BASE STATIC OBJECTIVE
StaticMorphologyLoss =
    GlobalVisibleMSE
    + ForegroundVisibleMSE
    + BackgroundAlphaMSE

DYNAMIC ADDITION
A rollout sample is mature when its hard-active cell count is at least the immutable target foreground cardinality.

Canonical radius-6 target foreground cardinality:
113 cells.

For mature samples only:
- evaluate exactly one virtual NCA step;
- restore the main device RNG state after the probe;
- never write the virtual probe into the state pool.

HomeostasisBackgroundVelocityLoss =
    mean(
        ReLU(probe_alpha - result_alpha) / 0.1
        over immutable target-background pixels of mature samples
    )

TrainingMorphologyLoss =
    StaticMorphologyLoss
    + HomeostasisBackgroundVelocityLoss

All objective coefficients remained fixed at 1.0.

PREREGISTRATION
research/experiments/dg1a/dg1a-p0-stab09-spec.ice

IMPLEMENTATION CONFORMANCE NOTE
Before scientific execution, focused testing exposed one implementation mismatch:
the first implementation evaluated the virtual probe on the full batch and masked immature samples only in the loss.

The preregistration required probe execution on mature samples only.

That implementation defect was repaired before scientific execution:
- the mature mask is computed first;
- only mature rollout states are probed;
- batches with no mature samples skip the probe and receive differentiable zero;
- RNG neutrality and pool isolation remain preserved.

No scientific coefficient, threshold, gate, target, envelope, or candidate definition was changed.

Final implementation/test source revision used for execution:
089ea0e6dd3a220ebc2e92e7ef819de24f87d0ef

SOURCE / PROVENANCE
Sandbox execution used a semantic reconstruction of connected GitHub readbacks of the source revision above.

Therefore:
- source_revision_verified_checkout: NO
- sandbox_source_byte_identity: NO
- scientific status: MEASURED SANDBOX, not commit-bound confirmatory acceptance

TEST SURFACE
Complete reconstructed regression after the mature-only repair:

106 non-runner tests: PASS
6 subprocess runner-evidence tests: PASS

TOTAL:
112 passed
0 failed
all bounded groups returned pytest code 0

Python 3.13.5
PyTorch 2.10.0+cpu

STAB-09 focused contracts covered:
- differentiable-zero behavior for immature batches;
- target-derived maturity cardinality;
- exact positive background-alpha velocity formula;
- zero penalty for contraction/no growth;
- exact full HOME-1 objective;
- fail-closed requirement for the dynamic term;
- RNG-state restoration around the virtual probe;
- frozen config;
- normal training telemetry;
- resumable training telemetry;
- proof that the virtual probe is never written into the state pool;
- runner evidence mode/telemetry.

No failing assertion was weakened, skipped, disabled, or modified merely to obtain a pass.

EXECUTION CONTRACT
Exactly one fresh seed-0 HOME-1 candidate completed 200 / 200 iterations.

Run discipline:
- one writer;
- fresh STAB-09 checkpoints;
- deterministic resumable state;
- 10-iteration durable segments;
- no second seed;
- no second candidate;
- no probe-horizon change;
- no maturity-rule change;
- no normalization/coefficient change;
- no gate change.

MEASURED TRAINING RESULT
training iterations:       200 / 200
initial recorded loss:     0.4459555447
minimum recorded loss:     0.2287646085
final recorded loss:       0.2449941188
training elapsed:          276.9511143 s
non-finite state:          NO

Final recorded component telemetry:
- global morphology MSE:               0.0499896780
- foreground morphology MSE:           0.1428604871
- background alpha MSE:                0.0332227163
- homeostasis background velocity:     0.0189204682
- mature samples in final batch:       8 / 8
- composite morphology loss:           0.2449933589
- hidden penalty:                      0.0764214545
- gradient norm:                       0.5745326877

The dynamic term was active at the final training checkpoint; HOME-1 did not fail merely because the mature gate never opened.

MEASURED EVALUATION RESULT
pre-lesion global MSE:     0.0524558015
post-lesion global MSE:    0.0499905869
final recovery global MSE: 0.0772757083

DamageEffect:              -0.0024652146
RelativeDamageEffect:      -0.0469960330

pre-damage active cells:   993 / 1600
post-damage active cells:  511 / 1600
active-cell removal:       0.4853977845
final recovery active:     1393 / 1600

bounded RecoveryFraction:  undefined
stable T50:                NOT ATTAINED / undefined
stable T90:                NOT ATTAINED / undefined
normalized recovery AUC:   undefined

PERSISTENCE / HOMEOSTASIS RESULT
initial persistence error: 0.0493245237
final persistence error:   0.0822274983
maximum MSE degradation:   0.0455008484

initial active cells:      941
final active cells:        1406
maximum active cells:      1490
final active-cell drift:   +465

visible-state drift MSE:   0.0264241919
mean step update magnitude:0.0033816136

This is a direct failure of the new dynamic homeostasis gates.

PREREGISTERED GATE APPLICATION
PASS  pre-damage active cells >= 113
FAIL  pre-damage active cells <= 800
FAIL  DamageEffect > 0
FAIL  RelativeDamageEffect >= 0.10
PASS  ActiveCellRemovalFraction >= 0.10
FAIL  stable T50 attained
FAIL  final RecoveryFraction > 0.4230230485
FAIL  pre-lesion global MSE <= 0.0361635
PASS  final recovery active cells >= 113
FAIL  final recovery active cells <= 800
PASS  persistence final active cells >= 113
FAIL  persistence final active cells <= 800
FAIL  maximum persistence active cells <= 800
FAIL  final persistence active-cell drift <= 0
FAIL  persistence final global MSE <= 0.0361635
PASS  persistence maximum MSE <= 2x initial persistence MSE
PASS  no non-finite state

CANDIDATE WORTH WIDENING: NO

PRIMARY FAILURE MODE
VIABLE BUT OVERGROWN PHENOTYPE WITH LONG-HORIZON HOMEOSTASIS FAILURE AND INVALID LESION.

The lesion removed 482 active cells, approximately 48.54% of the nominal mature phenotype, yet improved global morphology from 0.0524558 to 0.0499906.

Therefore substantial harmful/excess structure remained before lesion and no valid morphology-damage event existed for regeneration inference.

DIRECTIONAL SIGNAL AT THE NOMINAL GROWTH SNAPSHOT
HOME-1 did improve the 96-step growth snapshot relative to the recent static-objective candidates.

Versus STAB-05:
- pre-damage active: 1206 -> 993, approximately 17.66% lower;
- pre-lesion MSE: 0.0701904967 -> 0.0524558015, approximately 25.27% lower.

Versus STAB-07:
- pre-damage active: 1094 -> 993, approximately 9.23% lower;
- pre-lesion MSE: 0.0625592172 -> 0.0524558015, approximately 16.15% lower.

Versus STAB-08:
- pre-damage active: 1440 -> 993, approximately 31.04% lower;
- pre-lesion MSE: 0.1016835570 -> 0.0524558015, approximately 48.41% lower.

This is mechanistically meaningful but not a pass.

LONG-HORIZON CONTRADICTION
The same trained rule that produced the improved nominal 96-step snapshot then expanded aggressively under persistence:

941 -> 1406 active cells
peak: 1490
drift: +465

Final recovery activity also expanded to 1393.

Therefore the one-step positive-background-alpha derivative penalty did not create a bounded long-horizon attractor.

SCIENTIFIC INTERPRETATION
STAB-09 adds a new distinction to the P0 bracket:

1. static endpoint occupancy objectives alone are insufficient;
2. a maturity-gated one-step local derivative penalty can improve the nominal growth snapshot;
3. that local one-step control does not predict or enforce 96-step homeostasis;
4. the system can exhibit low immediate positive-background velocity during training while retaining a longer-horizon expansive attractor;
5. a valid stabilization mechanism must constrain a longer developmental trajectory, not just one local step.

HOME-1 is therefore a useful negative result rather than evidence that dynamic control is irrelevant.

It specifically rejects:
ONE-STEP LOCAL BACKGROUND-ALPHA VELOCITY CONTROL
as sufficient for canonical P0 stabilization under the frozen envelope.

NEGATIVE KNOWLEDGE RETAINED
1. HOME-1 is not worth widening.
2. The mature gate did activate; failure is not attributable to a permanently inactive homeostasis term.
3. RNG-neutral probing and pool isolation are technically viable training mechanisms.
4. The nominal 96-step phenotype improved versus STAB-05/07/08.
5. One-step local velocity regularization is too myopic to control long-horizon persistence.
6. Persistence maximum occupancy and drift telemetry are necessary; final-point-only reporting would understate the failure.
7. The next mechanism should interrogate or train over a longer homeostatic trajectory rather than another one-step coefficient adjustment.

DECISION
- CLOSE STAB-09 as negative.
- DO NOT widen HOME-1 to additional seeds.
- DO NOT tune the maturity rule, probe horizon, velocity normalization, objective coefficients, or gates inside STAB-09.
- Preserve all eight historical training modes for reproducibility.
- Preserve the 113-cell viability floor and 800-cell occupancy ceiling.
- Preserve the strengthened dynamic persistence gates.
- Preserve global visible morphology MSE as the common evaluation metric.
- Do not reopen STAB-01 through STAB-09 with post-result parameter inserts.

NEXT RESEARCH ACTION
Remain inside canonical DG-1A P0.

Open a new preregistered packet, provisionally DG-1A-P0-STAB-10, before further scientific execution.

STAB-10 should discriminate a LONGER-HORIZON homeostasis mechanism rather than another:
- static spatial weighting;
- coefficient sweep;
- threshold/margin sweep;
- halo-radius sweep;
- one-step local velocity coefficient change.

Plausible mechanism classes include:
- bounded multi-step virtual persistence probe;
- short trajectory-integrated excess-support expansion loss;
- explicit persistence curriculum term coupled to target viability.

NO STAB-10 mechanism is selected by this result record.

MACHINE EVIDENCE
evidence/dg1a/p0_stab09_sandbox.json

Full local sandbox evidence SHA-256:
2efa48b1a32ac2604b75034ebce98e1acefa91ff86d5c4427b4bd24bec48a916

SCIENTIFIC BOUNDARY
This remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this result.
