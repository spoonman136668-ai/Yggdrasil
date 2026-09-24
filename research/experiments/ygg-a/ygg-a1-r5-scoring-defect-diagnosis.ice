TITLE: YGG-A1 R5 Mechanical Gate Failure Diagnosis
DATE: 2026-09-24
STATUS: INFRASTRUCTURE / SCORING DEFECT CONFIRMED
LANE: YGG-A
PREREGISTRATION: 44e5db473c0a0aa4c6065b77aa2d83cedecfc1eb
RUN: 36073385879
HEAD: bdfa8de18e5cd5621e508021dcf67af3b1d5a228
ARTIFACT_ID: 10839058192
ARTIFACT_SHA256: 91f29693bdb26a8438cbb85b6ecbb609af6c3c3f39b66f058dc6cccc21e285ff

OBSERVED
fork_join_fixture_BC=true
fork_join_fixture_CB=true
join_blocks_D=true
D_after_both_siblings=true
fork_dependencies_exact=true
repair_reverify_fixture=true
duplicate_byte_identical=true
no_model_rng=true

FAILED SCORED PROBES
zero_incorrect_done=false
maturity_pass=false

WORLD DIAGNOSTICS
correct_done=122
incorrect_done=25
backlog=13
maturity_reached_egress=7
maturity_failed_rows=2

ROOT CAUSE
The YGG-A1 execution path computes the preregistered fork/join target with its local expected() function:
A -> {B,C} -> D.

However run_world bound g.expected_pair to the inherited LU-2T compatibility scorer, which recomputes the old sequential target:
A -> B -> C -> D.

The inherited t.maturity_summary likewise validates repaired values with the old sequential expected_quad function.

Therefore valid fork/join outputs can be classified as incorrect DONE, and valid fork/join repair states can fail maturity validation. The fork/join mechanics themselves passed all direct frozen fixtures.

AUTHORIZED REPAIR
Bind world scoring and maturity validation to the already-preregistered YGG-A1 fork/join expected() function.
Do not change topology, scheduler, load, corruption schedule, repair sequence, thresholds, seed, N, T, D, R_TASK, expiry, route edges, or qualification rules.

CLASSIFICATION
R5 is invalid as a scientific outcome because its scorer evaluates a different topology than the experiment under test.
