TITLE: LU-2J EXACT-ARTIFACT EXPOSURE-CONDITIONED INTEGRITY AUDIT CLOSURE
DATE: 2026-09-24
STATUS: CLOSED / EXPOSURE-CONDITIONED METRIC EFFECT SUPPORTED / NO L2 ORGANIZATION COLLAPSE OBSERVED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
5defdaacf15f3e9c5ac72b4cd72518399e2294a3

PARENT LU-2I CLOSURE:
1cfbfd3c3bfad9233bc9493b94f5b6db96f7bc9d

ACCEPTED LU-2I RUN:
36050323979

ACCEPTED LU-2I ARTIFACT:
10829937783

LU-2J AUDIT RUN:
36051112738

LU-2J AUDIT HEAD:
edce8cfa8f8ef71c1b79b2855357031a7ffef5a5

LU-2J EVIDENCE ARTIFACT:
10830881245

EXACT-ARTIFACT IDENTITY

primary1.bin == primary2.bin:
TRUE

bytes:
1016475

SHA256:
ff39cb4013bf988086e7ee1ebf5cf906c697f1b7393a09ac7cce5f10a632e1da

No world was rerun.
No new world was derived.
No learned-U arm executed.
No threshold or dynamic was changed.

DIAGNOSTIC STATUS

EXPOSURE_CONDITIONED_METRIC_ARTIFACT_SUPPORTED:
TRUE

L2_DEVELOPMENTAL_ORGANIZATION_COLLAPSE_SUPPORTED:
FALSE

NO_L2_ORGANIZATION_COLLAPSE_OBSERVED:
TRUE

REQUEST_LEVEL_DEADLINE_GEOMETRY_RESOLVED:
FALSE

NEXT_STEP_L1_FRESH_EXACT_PARENT_VALIDATION_AUTHORIZED_BY_DIAGNOSTIC:
TRUE

EXPOSURE-CONDITIONED REPAIR CHAIN

L1

corruptions reaching egress:
82

detection_given_egress:
1.0000000000

repair_given_detected:
0.9878048780

done_given_repaired:
0.9876543210

done_given_egress:
0.9756097561

L2

corruptions reaching egress:
146

detection_given_egress:
0.9383561644

repair_given_detected:
0.9489051095

done_given_repaired:
0.9538461538

done_given_egress:
0.8493150685

L3

corruptions reaching egress:
92

detection_given_egress:
0.8913043478

repair_given_detected:
0.9146341463

done_given_repaired:
0.9200000000

done_given_egress:
0.7500000000

Thus L2 exposes 54 more corrupted requests to the egress boundary than L3,
while every opportunity-conditioned repair-chain fraction is higher at L2
than at L3.

This explains how a binary world-level repair_integrity gate can produce
worse coverage at L2 even though the conditional integrity process itself is
better than L3.

CORRECTNESS

incorrect DONE:
zero in every L1, L2, and L3 world.

FUNCTIONAL STREAMS

Both C and S produce correct DONE in every accepted world at every load.

DEVELOPMENTAL ORGANIZATION

For each phase the accepted artifact was audited for median C, S, C+S, U,
H, FC, FS, and FC+FS.

Number of phases where median L2 C+S is strictly below both L1 and L3:
0 / 5

Any L2 world losing a functional stream:
FALSE

Therefore the preregistered conservative organization-collapse criterion
does not trigger.

This does not prove organization is identical across loads.
It establishes only that the L2 strict-feasibility trough is not accompanied
by the preregistered collapse signature.

DEADLINE GEOMETRY LIMITATION

The exact accepted LU-2I artifact does not contain per-request:

first VERIFY timestamp;
failed VERIFY timestamp;
REPAIR timestamp;
post-repair VERIFY timestamp;
remaining lifetime at those events.

Therefore individual fair-opportunity deadline geometry cannot be recovered
from this artifact without rerunning the worlds.

Per preregistration, no rerun was performed.

The earlier LU-2H service-envelope audit remains the valid evidence that
deadline pressure and finite-horizon censoring exist at L3.

CAUSAL INTERPRETATION

LU-2I's FALSE ordinary-overload verdict remains unchanged.

Offered load strongly controls admission congestion, but binary strict
repair-integrity coverage is exposure-sensitive because loads differ in how
many corruptions survive long enough to face the integrity chain.

L2 is not worse than L3 when repair is compared conditionally at each
observed opportunity boundary.

The current exact artifact also does not show a medium-load developmental
workforce collapse.

DECISION

Do not modify or reinterpret LU-2I.

Do not tune repair or expiry.

Do not run another L2/L3 calibration merely to recover timestamps.

Proceed to the already-required fresh exact-parent validation of L1 as a
candidate Task-2 environment.

That validation must use ten new worlds and may not reuse LU-2I calibration
worlds.

No learned-U comparison is authorized until fresh exact-parent L1 validation
passes its preregistered baseline criterion.

PLAIN-SPEAK INTERPRETATION

The two-job setting looked worse because it gave damaged jobs more chances
to reach the repair checkpoint.

Three-job worlds killed more work in the queue before those damaged jobs
ever got tested.

When we compare jobs that actually reach each repair step, two jobs per
epoch performs better than three at every step.

The cell population also does not show the medium-load collapse we were
worried about.

So we do not need to redesign the organism around the strange L2 score.

The clean next test is the one already required:
give the hand-written parent ten completely fresh one-job Task-2 worlds and
see whether that environment is reliably feasible before the neural
recruiter is allowed back in.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
