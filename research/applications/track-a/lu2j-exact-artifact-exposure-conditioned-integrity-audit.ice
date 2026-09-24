TITLE: LU-2J — EXACT-ARTIFACT EXPOSURE-CONDITIONED INTEGRITY AUDIT
DATE: 2026-09-24
STATUS: PREREGISTERED / OBSERVATION-ONLY / NO RERUN
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PARENT LU-2I CLOSURE:
1cfbfd3c3bfad9233bc9493b94f5b6db96f7bc9d

LU2IF1:
326f89f940818a6abb0fcbc999595b844936dc53

ACCEPTED LU-2I RUN:
36050323979

ACCEPTED ARTIFACT:
10829937783

ACCEPTED DUPLICATE SWEEP

bytes each:
1016475

SHA256:
ff39cb4013bf988086e7ee1ebf5cf906c697f1b7393a09ac7cce5f10a632e1da

QUESTION

Is the apparent L2 repair-feasibility trough in LU-2I primarily an
all-or-nothing metric / opportunity-exposure effect, or does the exact
accepted artifact show a genuine nonmonotonic developmental organization
failure at medium load?

BOUNDARY

Open the exact accepted LU-2I duplicate only.

Do not rerun a world.
Do not derive a new world.
Do not alter a manifest.
Do not execute learned U.
Do not change a threshold.
Do not change expiry, load, repair, verification, or developmental dynamics.

FAIL-CLOSED ARTIFACT IDENTITY

Require:

primary1.bin == primary2.bin

bytes:
1016475

SHA256:
ff39cb4013bf988086e7ee1ebf5cf906c697f1b7393a09ac7cce5f10a632e1da

Otherwise stop without interpretation.

EXPOSURE-CONDITIONED COUNTS

For each load L1, L2, L3 sum across the ten accepted rows:

scheduled corruptions;
corruption applied;
corruptions reaching egress;
verification detected;
repaired;
correct DONE after repair.

Derive the following opportunity-conditioned fractions:

detection_given_egress
=
verification_detected / corruptions_reaching_egress

repair_given_detected
=
repaired / verification_detected

done_given_repaired
=
correct_DONE_after_repair / repaired

done_given_egress
=
correct_DONE_after_repair / corruptions_reaching_egress

Also report each fraction per world.

EXPOSURE-CONDITIONED METRIC ARTIFACT

Define:

EXPOSURE_CONDITIONED_METRIC_ARTIFACT_SUPPORTED = TRUE iff:

1. L2 corruptions reaching egress > L3 corruptions reaching egress;
2. L2 detection_given_egress >= L3 detection_given_egress;
3. L2 repair_given_detected >= L3 repair_given_detected;
4. L2 done_given_repaired >= L3 done_given_repaired;
5. L2 done_given_egress >= L3 done_given_egress;
6. L2 and L3 both have zero incorrect DONE.

This does NOT retroactively change LU-2I's FALSE verdict.
It only diagnoses why binary world-level repair_integrity coverage can be
nonmonotonic even when service quality improves as load falls.

DEVELOPMENTAL ORGANIZATION AUDIT

Use only the phase_state_mean fields already stored in the accepted artifact.

For each load and phase report median:

C;
S;
C+S;
U;
H;
FC;
FS;
FC+FS.

Also report whether both C and S streams produced correct DONE in every
accepted world.

Define a conservative organization-collapse flag:

L2_DEVELOPMENTAL_ORGANIZATION_COLLAPSE_SUPPORTED = TRUE iff either:

A. any L2 world loses one functional stream entirely;

or

B. in at least two of five phases, median L2 C+S is strictly lower than
both paired-load medians L1 and L3.

This is intentionally a collapse test, not a claim that all subtler
organization differences are absent.

If neither A nor B holds, report:

NO_L2_ORGANIZATION_COLLAPSE_OBSERVED = TRUE.

Do not claim that this proves organization is identical across loads.

DEADLINE-GEOMETRY LIMITATION

The accepted LU-2I artifact contains aggregate repair counters and
phase-state summaries, but not request-level first-verify / repair /
reverify timestamps.

Therefore this audit may not invent remaining-lifetime values.

Report:

REQUEST_LEVEL_DEADLINE_GEOMETRY_RESOLVED = FALSE

unless those timestamps are actually present in the accepted artifact.

Do not rerun the worlds merely to obtain them.

DECISION

If:

EXPOSURE_CONDITIONED_METRIC_ARTIFACT_SUPPORTED = TRUE

and

L2_DEVELOPMENTAL_ORGANIZATION_COLLAPSE_SUPPORTED = FALSE,

then the immediate L2 trough is adequately explained as an exposure-sensitive
binary integrity metric effect for purposes of choosing the next experiment.

That does not establish that load has no developmental effects.

NEXT STEP RULE

LU-2I already identified L1 as the only load meeting the preregistered
candidate criterion (>=8/10 strict baseline worlds and both streams active).

If LU-2J supports the exposure explanation and finds no L2 organization
collapse, proceed to the already-required fresh exact-parent validation
of the L1 Task-2 environment on ten new worlds.

Do not reuse LU-2I calibration worlds.

Do not introduce learned U in that validation.

If LU-2J instead supports a genuine L2 organization collapse, diagnose that
mechanism before validating L1 for learned transfer.

PLAIN-SPEAK QUESTION

At two jobs per epoch, more damaged jobs survive long enough to reach the
repair checkpoint than at three jobs per epoch.

That gives the two-job worlds more chances to fail an all-or-nothing rule
that says one incomplete repair fails the whole world.

This audit asks whether the actual repair chain is nevertheless better at
two jobs than at three once we compare like-for-like opportunities.

It also checks whether the medium-load organism truly loses functional cell
organization.

We use the exact accepted data.
We do not run the experiment again.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
