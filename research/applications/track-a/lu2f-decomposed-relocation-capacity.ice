TITLE: LU-2F — DECOMPOSED RELOCATION-CAPACITY TEST FOR BOUNDED U AUTHORITY
DATE: 2026-09-23
STATUS: PREREGISTERED / NO LU-2F WORLD EXECUTED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Prospectively test 25-percent learned U authority
under a relocation-capacity measurement contract
that separates:

new Phase-4 service;

from

legacy carry-in clearance.

This experiment does not rescore LU-2E.

LU-2E remains failed under its frozen final-window contract.

MOTIVATION

LU-2E replicate 3 showed:

paired raw final-window gap:
FAIL;

but

new Phase-4 correct DONE:
identical;

final backlog:
identical;

final-16 backlog area:
lower under U_A25;

total correct DONE:
higher under U_A25.

The post-closure timing audit showed
that raw final-window completion rate
is influenced by carry-in backlog volume.

LU-2F tests a new prospective measurement question
on fresh worlds.

PARENTS

LU2DF1:
f6f82f9d6e13818d9bad7ffc19c59fda1a077aa5

LU2EF1:
377fdc6e3b65fe843f77296cf1bbdc82736813a1

LU-2E closure:
64835405e06039396e4b73cc2dbf5e54dab09961

LU-2E timing audit:
60e731a50eb67fd646cc708a99c2e4ed5f10360e

ARMS

Exactly:

U_A0

and

U_A25.

Mechanism semantics are identical to LU-2E.

H:
exact V0.2 teacher.

U_A0:
exact V0.2 teacher recruitment.

U_A25:
0.75 teacher U distribution
+
0.25 frozen learned U distribution.

C/S:
exact V0.2 teacher.

Hard lifecycle:
exact V0.2.

No mechanism change.

FRESH WORLDS

Exactly 10.

Derive only after LU2FF1 exists.

Namespace:

LU2F-DECOMP-RELOC|LU2FF1|replicate

for replicate 1..10.

No prior LU-2 world reuse.

No rejection sampling.

No replacement world.

No result-dependent selection.

Bind all ten manifests
before any scientific arm executes.

PRIMARY EXECUTION

Run all ten paired worlds twice.

Require complete canonical sweep byte identity
before evaluation opens.

DECOMPOSED RELOCATION METRICS

For each arm/world report:

legacy_unfinished_at_128;

legacy_correct_done;

legacy_expired;

legacy_completion_fraction;

new4_arrivals;

new4_correct_done;

new4 C correct_done;

new4 S correct_done;

final-16 total backlog area;

final backlog;

Phase-4 total correct DONE;

raw Phase-4 final-window completion rate.

The old raw final-window rate remains descriptive telemetry.

It is not deleted or hidden.

NEW-PHASE SERVICE GATE

For every world:

U_A25 new4_correct_done
>=
0.90 * U_A0 new4_correct_done.

Across 10 worlds:

median new4 completion ratio
>=0.95.

If U_A0 new4_correct_done is zero,
require U_A25 new4_correct_done >= U_A0
and exclude that world from ratio median.

STREAM NON-COLLAPSE

For each stream C and S,
if U_A0 completes at least 4 new Phase-4 requests
for that stream,
require U_A25 to complete
at least 75 percent of the U_A0 count.

This is a non-collapse guard,
not an optimization target.

LEGACY CLEARANCE GATE

For every world:

U_A25 legacy_completion_fraction
>=0.95

and

U_A25 legacy_completion_fraction
>=
U_A0 legacy_completion_fraction - 0.05.

Legacy expired under U_A25:
0
unless U_A0 also has legacy expiry,
in which case U_A25 may not exceed U_A0 legacy expiry count.

BACKLOG / EFFICIENCY GATES

For every world:

U_A25 final-16 backlog area
<=125% U_A0;

U_A25 final backlog
<=125% U_A0;

phases-1-4 completion-area ratio
>=0.90;

operations per correct completion
<=125% U_A0.

Across worlds:

median phases-1-4 completion-area ratio
>=0.95.

RECOVERY / SAFETY GATES

For every world:

anchor-rotation recovery <=8 epochs;

demand-reversal recovery <=8 epochs;

inherited lesion criterion:
PASS;

incorrect DONE:
0;

matching invariants:
PASS.

CAUSAL GATE

U_A25 must:

evaluate U at least once;

have nonzero teacher-vs-active U TV;

and produce at least one realized U transition difference
across the ten-world suite.

OVERALL STATUS

LU2F_DECOMPOSED_RELOCATION_CAPACITY_PRESERVED = TRUE iff:

duplicate execution identity passes;

causal gate passes;

new-phase service gate passes;

stream non-collapse passes;

legacy clearance gate passes;

backlog / efficiency gates pass;

recovery / safety gates pass.

RAW FINAL-WINDOW TELEMETRY

Still report the old LU-2A/LU-2E
paired raw final-window gap.

Do not use it as the LU-2F decision criterion.

Do not claim LU-2E would have passed.

INTERPRETATION

IF TRUE

Evidence supports that
25-percent learned U authority
preserves decomposed relocation capacity
when new work and inherited work
are measured separately.

This would justify a later experiment
combining bounded U authority
with the already-learnable H-release head.

It still would not constitute
automatic substrate promotion.

IF FALSE

Close bounded learned-U promotion
for this model family under Task-1.

Do not tune alpha.

NO POST-RESULT TUNING

Do not change:

alpha;

world count;

namespace;

weights;

task law;

new-work ratio thresholds;

legacy thresholds;

stream guard;

backlog thresholds;

recovery thresholds;

or interpretation rules
after execution begins.

PLAIN-SPEAK QUESTION

The old final-window score mixed together:

jobs created in the final phase;

and old jobs carried in from earlier phases.

That made it possible for an organism
with more unfinished old work
to score a higher final-window throughput number.

LU-2F does not erase that old score.

Instead it asks a cleaner new question
on completely fresh worlds:

does the 25-percent neural recruiter
keep up with new work,
finish the old work it inherited,
control backlog,
and preserve recovery and safety?

If yes,
we have evidence that its real relocation capacity
is preserved even when its developmental history differs.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
