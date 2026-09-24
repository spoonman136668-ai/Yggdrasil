TITLE: LU-2J EXACT-ARTIFACT EXPOSURE-CONDITIONED INTEGRITY AUDIT CLOSURE
DATE: 2026-09-24
STATUS: CLOSED / EXPOSURE-CONDITIONED METRIC ARTIFACT SUPPORTED / NO L2 ORGANIZATION COLLAPSE OBSERVED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
5defdaacf15f3e9c5ac72b4cd72518399e2294a3

PARENT LU-2I CLOSURE:
1cfbfd3c3bfad9233bc9493b94f5b6db96f7bc9d

ACCEPTED LU-2I RUN:
36050323979

ACCEPTED ARTIFACT:
10829937783

AUDIT EXECUTION:
36051112738

AUDIT HEAD:
edce8cfa8f8ef71c1b79b2855357031a7ffef5a5

ARTIFACT IDENTITY

primary1.bin == primary2.bin:
TRUE

bytes each:
1016475

SHA256:
ff39cb4013bf988086e7ee1ebf5cf906c697f1b7393a09ac7cce5f10a632e1da

No world rerun occurred.
No new world was derived.
No learned-U arm executed.
No threshold, expiry, load, repair, verification, or developmental dynamic changed.

SCIENTIFIC STATUS

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

EXPOSURE-CONDITIONED INTEGRITY

L1:
corruptions reaching egress 82
verification detected 82
repaired 81
correct DONE after repair 80

detection_given_egress:
1.0

repair_given_detected:
0.9878048780

done_given_repaired:
0.9876543210

done_given_egress:
0.9756097561

L2:
corruptions reaching egress 146
verification detected 137
repaired 130
correct DONE after repair 124

detection_given_egress:
0.9383561644

repair_given_detected:
0.9489051095

done_given_repaired:
0.9538461538

done_given_egress:
0.8493150685

L3:
corruptions reaching egress 92
verification detected 82
repaired 75
correct DONE after repair 69

detection_given_egress:
0.8913043478

repair_given_detected:
0.9146341463

done_given_repaired:
0.92

done_given_egress:
0.75

Thus every preregistered opportunity-conditioned repair fraction is better
at L2 than L3, while L2 exposes substantially more corrupted requests to
the integrity checkpoint.

ZERO INCORRECT DONE

L1:
TRUE

L2:
TRUE

L3:
TRUE

FUNCTIONAL STREAMS

Both C and S produced correct DONE in every accepted world at every load.

DEVELOPMENTAL ORGANIZATION

The preregistered collapse criterion did not fire.

L2 phases in which median C+S was strictly below both L1 and L3:
none.

No L2 world lost either functional stream.

This does not prove organization is identical across loads.
It does establish that the specific hypothesized medium-load organization
collapse needed to explain the binary feasibility trough is not observed.

DEADLINE GEOMETRY

The accepted LU-2I artifact contains aggregate repair counters and phase-state
summaries but no request-level first-verify / repair / reverify timestamp
fields.

Therefore:

REQUEST_LEVEL_DEADLINE_GEOMETRY_RESOLVED = FALSE

No rerun was performed to manufacture those timestamps.

INTERPRETATION

The nonmonotonic world-level repair-integrity score is explained by unequal
opportunity exposure strongly enough for experiment-selection purposes.

L2 is not worse than L3 when like-for-like repair opportunities are compared.
It is better at detection, repair completion, reverify completion, and
end-to-end repaired DONE among corruptions that reach egress.

L2 looks worse under the binary world gate because many more damaged jobs
survive long enough to be tested.

At L3, heavier queueing and expiry censor many damaged requests before they
reach the integrity checkpoint.

This preserves the LU-2I FALSE verdict and does not retroactively change any
accepted result.

DECISION

Proceed to a fresh exact-parent validation of the L1 Task-2 environment on
ten new worlds.

Do not reuse LU-2I calibration worlds.
Do not introduce learned U.
Do not tune L1 using learned-U behavior.
Do not change the inherited 32-epoch expiry or Task-2 computation.

PLAIN-SPEAK INTERPRETATION

The weird medium-load dip was a scoring/exposure effect, not evidence that the
organism reorganized badly at two jobs per epoch.

At two jobs, more damaged work survives long enough to face the repair test.
At three jobs, more of it dies earlier in the queue.

When we compare only jobs that actually reach the repair checkpoint, two jobs
per epoch is consistently healthier than three.

And the medium-load organism still keeps both functional streams and does not
show the preregistered workforce-collapse signature.

So the clean next step is to validate the one-job-per-epoch Task-2 environment
on a completely fresh exact-parent world set before learned U is allowed back
into the experiment.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
