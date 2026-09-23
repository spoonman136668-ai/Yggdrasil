TITLE: TASK-1 POST-CLOSURE PHASE-4 INGRESS BOOTSTRAP DIAGNOSIS
DATE: 2026-09-22
STATUS: OBSERVATION-ONLY / FROZEN-T1F1 REPLAY
TRACK: DG-1 / TASK-1
PARENT CLOSURE: 9dff320abcf30b3fb063d67beb63fafa87ece669

PURPOSE

Localize the failed Phase-4 anchor-relocation criterion
without changing Task-1 dynamics.

SOURCE / MANIFEST

T1F1:
22b6ab5a036732cc9efbda077069e971c34a337e

source SHA256:
567c37e3e2171bc3cfc15b996c447e87b7ac5cdafb7bc299ba104284ae826e12

primary manifest SHA256:
ef76ca548a1c9754eb2779812d7c14cbe66788821198b5d7c6ebc291360f2d86

The diagnostic replay uses the exact frozen EMERGENT_V0 primary.
Instrumentation observes eligibility immediately before local matching.
It does not alter state transitions, request transitions, matching,
task randomness, corruption, lesion, anchors, or qualification.

PRIMARY FINDING

The Phase-4 throughput failure localizes to SENSE admission,
not downstream processing.

FINAL 16 EPOCHS — PHASE 4

C stream:

mean RAW requests waiting:
12.6875

mean RAW requests with at least one eligible sensing cell:
5.25

mean SENSE matches per epoch:
0.875

mean correctly committed cells within R_TASK of relocated ingress:
5.0

epochs with zero correctly committed ingress cells:
0

S stream:

mean RAW requests waiting:
29.8125

mean RAW requests with at least one eligible sensing cell:
20.125

mean SENSE matches per epoch:
0.3125

mean correctly committed cells within R_TASK of relocated ingress:
1.25

epochs with zero correctly committed ingress cells:
2

DOWNSTREAM AVAILABILITY

Across all Phase-4 epochs, once requests were admitted:

PROCESS requests with an eligible cell:
effectively all observed PROCESS demand.

ROUTE requests with an eligible cell:
effectively all observed ROUTE demand.

VERIFY requests with an eligible cell:
effectively all observed VERIFY demand.

REPAIR requests with an eligible cell:
effectively all observed REPAIR demand.

Therefore the dominant Phase-4 failure is not:

route discontinuity;
verification absence;
repair absence;
or a general inability to change functional operation.

ORGANIZATION CONTEXT

EMERGENT_V0 dominant-operation change after anchor rotation:
100%.

Phase-4 final window still represents at least four operation classes
with at least four active cells.

Thus cells are changing what they do.

The problem is that a relocated ingress may initially sit beside too few
cells already committed to the matching C/S stream.

Under T1F1, SENSE itself requires matching stream commitment.

This creates a bootstrap dependency:

new local demand
must be sensed to enter the task pipeline,

but sensing that demand already requires
the locally correct commitment state.

When the new anchor lands in a region dominated by the opposite or
non-executing state, RAW work accumulates before the demand can be
converted into useful pipeline activity.

CAUSAL HYPOTHESIS

Task-1 currently conflates two functions:

ENVIRONMENTAL TRANSDUCTION
and
STREAM-SPECIFIC TASK COMMITMENT.

A cell must already be committed to stream S
before it can even sense new S work.

That requirement may be unnecessarily position-binding.

The next justified causal experiment should isolate only this interface
dependency.

It should test whether SENSE can be stream-neutral while preserving
stream-matched commitment for PROCESS, ROUTE, VERIFY, and REPAIR.

Do not alter V0.

Do not add dynamic topology.

Do not enlarge R_TASK.

Do not change anchor rotation.

Do not add G5_FULL.

Do not change phase lengths, expiry, or arrival load.

PLAIN-SPEAK INTERPRETATION

The organism can reorganize after work gets into the pipeline.

The problem is getting new work through the front door.

When the S entrance moved, there were often almost no nearby S-committed
cells allowed to pick the work up.

So the jobs piled up outside.

That creates a chicken-and-egg problem:

the new work is supposed to tell the organism
where S demand now exists,

but only cells already committed to S
are allowed to sense that new work.

The next test should break only that circular dependency.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
