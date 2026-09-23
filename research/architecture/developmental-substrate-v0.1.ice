TITLE: YGGDRASIL — DEVELOPMENTAL SUBSTRATE V0.1
DATE: 2026-09-23
STATUS: FROZEN / LOCAL_HEDGE PROMOTED AFTER INDEPENDENT CONFIRMATION
TRACK: DG-1 / POST-TASK-1 ARCHITECTURE

PURPOSE

Promote exactly one experimentally replicated change
from Developmental Substrate V0:

H-state ambiguity semantics.

Developmental Substrate V0 remains the historical baseline.

V0.1 changes no other cell state,
parameter,
topology rule,
task scheduler,
repair rule,
or optional mechanism.

PARENT

Developmental Substrate V0:
92654adf407310a01e368e2c53934beae749482c.

V0 architecture record:
research/architecture/developmental-substrate-v0.ice.

PROMOTION EVIDENCE

Task-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063.

Task-1F closure:
fda86a2fee99fb948524b53b0eb0652011d655f6.

Task-1F established:

LOCAL_HEDGE information gain = TRUE;

positive Phase-4 gain in 5/5 fresh manifests;

median Phase-4 gain = +31.25 percentage points;

backlog reduction in 5/5;

new relocated S completion gain in 5/5;

Phase-0 preserved;

safety preserved;

cost bounded.

Task-1F remained formally unqualified
because one correctly repaired request
expired before mandatory re-verification.

That historical result remains unchanged.

Task-1G closure:
b11eb856b1348d8d08cc99497ac59f7a15e7ceaa.

Task-1G showed:

repair-critical EDF active in 5/5;

repair-service information gain = FALSE;

the remaining repair miss is not caused
by ordinary post-detection local proposal ordering.

Task-1G remains negative.

Service-envelope audit:
e6ea693894ab12a6d542d50e297e97abf801124c.

The audit established:

73 / 73 repair paths
that were both mathematically recoverable
under the frozen expiry
and observable through the fixed horizon
completed correctly.

The remaining misses were explained by
deadline impossibility
or finite-horizon censoring.

Task-1H T1HF1:
2b57ce116fa9a92a5da55399fbdea3737f9aafe8.

Task-1H closure:
1b848079ae0d54dd9e7b01c8d004a93b16aeb62d.

Task-1H independently confirmed LOCAL_HEDGE
on five newly derived manifests.

TASK1H_LOCAL_HEDGE_CONFIRMED:
TRUE.

TASK1H_LOCAL_HEDGE_STRONG_CONFIRMATION:
TRUE.

Task-1H observed:

positive Phase-4 gain:
5/5;

median Phase-4 gain:
+21.875 percentage points;

final-window backlog lower:
5/5;

median backlog reduction:
18.307692%;

new relocated S completion gain:
4/5;

Phase-0 completion:
100% under both paired arms in all five;

incorrect DONE:
0 in all five LOCAL_HEDGE arms;

anchor-rotation recovery:
0, 0, 1, 0, 0 epochs;

operation cost:
no increase relative to GLOBAL_HEDGE in any replicate.

PROMOTED CHANGE

V0.1 changes only H formation and H release
from global-coexistence-weighted ambiguity
to local neighborhood ambiguity.

All C/S commitment,
defection,
recruitment,
B accumulation,
ECHO_PHASE,
refractory,
and topology semantics
remain inherited exactly from V0.

LOCAL H RELEASE

For H cell i,
use the inherited radius-3 local evidence:

L_C3(i);
L_S3(i).

The active release hazard is:

lambda_release_local(i)
=
ETA
*
[1 - min(L_C3(i), L_S3(i))]
*
[1 - local_H_density(i, HEDGE_R)].

Release probability remains:

1 - exp(-max(0, lambda_release_local)).

Interpretation:

H persists when the cell's own neighborhood
contains meaningful evidence for both sides.

H releases as local ambiguity disappears.

Global C/S workload coexistence
does not by itself keep a locally unambiguous cell
in H.

LOCAL H FORMATION

For recruitable U cell i,
preserve the exact inherited C and S recruitment hazards.

Replace only the H formation hazard with:

lambda_H_local(i)
=
ETA
*
L_C3(i)
*
L_S3(i)
*
[
1 + local_H_density_snapshot(i, HEDGE_R)
].

The H-density snapshot remains
the inherited pre-entry local H snapshot
used by Task-1F.

Interpretation:

a U cell enters H
when its own local neighborhood
simultaneously supports C and S.

Global coexistence elsewhere in the organism
does not create H locally.

UNCHANGED V0 CONTRACT

Retain exactly:

C / S / U / H / FC / FS state family;

rho = 3/4;

signed local B accumulation;

local evidence radius = 12;

Hill n = 3;

Hill K = 1/2;

cooperative / recruitment radius = 3;

ETA = 1/2;

D2 and D3 frozen refractory families;

A45 one-epoch ECHO_PHASE;

side-specific Q trace;

fixed bounded local topology;

anti-oracle constraints;

deterministic/stateless randomness discipline;

external global scoring only;

no hidden full-world controller.

ECHO_PHASE

Unchanged from V0:

Q_eff = max(Q_raw, Q_echo);

trace stores Q_raw only;

one epoch only;

side-specific;

resets when commitment is lost;

cannot cross side;

new commitments echo-free;

no recursive memory;

no phase oracle.

OPTIONAL RECOVERY

G5_FULL remains:

VALIDATED OPTIONAL / DEFAULT OFF.

V0.1 does not promote G5_FULL to default.

It may be used only under
a separately preregistered experiment/task contract
with the frozen implementation unchanged.

EXCLUDED MECHANISMS

Still excluded from the default substrate:

A49 challenge push-pull;

A51 challenge-field TTL memory;

A52 fixed TAU3 response delay;

A53 current-evidence-vetoed phase memory;

Task-1G repair EDF.

Task-1G EDF is a task-service scheduling treatment,
not a developmental primitive,
and it produced no repair-service information gain.

TASK-SPECIFIC MECHANISMS NOT PROMOTED

The following remain Task-1 interface/benchmark mechanics,
not V0.1 cellular substrate primitives:

R_TASK task-service radius;

request pipeline;

request expiry;

task anchors;

task scheduler;

truth-table interpreter;

VERIFY / REPAIR packet lifecycle.

The Task-1 service-envelope result
must not be baked into cell dynamics.

DEFERRED MECHANISMS

Still deferred:

learned NCA updater;

richer communication protocol;

dynamic topology;

long-term role DNA;

Byzantine-cell machinery;

resource economy;

open-ended replication;

neural-module payloads;

LoRA / micro-expert cells.

PROMOTION LOGIC

This promotion does NOT reinterpret Task-1F as qualified.

It does NOT reinterpret Task-1G as positive.

It does NOT relax repair thresholds.

It does NOT change Task-1 expiry.

It does NOT select only favorable Task-1H worlds.

The promotion is based on:

one five-world causal information-gain experiment;

one independent five-world strong confirmation;

and a separate service-envelope diagnosis
that localized the orthogonal repair misses.

Thus LOCAL_HEDGE has replicated causal support
independent of threshold editing.

SUBSTRATE STATUS

DEVELOPMENTAL SUBSTRATE V0:
HISTORICAL FROZEN BASELINE.

DEVELOPMENTAL SUBSTRATE V0.1:
CURRENT HAND-DESIGNED SUBSTRATE.

A45 ECHO_PHASE:
CORE.

LOCAL_HEDGE:
CORE DEFAULT H SEMANTICS.

G5_FULL:
VALIDATED OPTIONAL / DEFAULT OFF.

A49 PUSH_PULL:
EXCLUDED.

A51 TTL:
EXCLUDED.

A52 TAU3_FIXED:
EXCLUDED.

A53 TAU3_VETO:
EXCLUDED.

TASK-1G REPAIR EDF:
NOT PROMOTED.

NEXT RESEARCH BOUNDARY

V0.1 is now sufficiently frozen
for the next developmental question.

Do not continue Task-1 scheduler tuning
to make the benchmark prettier.

The next experiment should test
a genuinely new capability boundary
or begin the preregistered transition
toward the learned per-cell updater.

Any learned-updater experiment must treat
V0.1 as the behavioral teacher / reference substrate
unless separately justified.

It must preserve hard invariants
for locality,
anti-oracle behavior,
bounded communication,
determinism/evidence discipline,
and functional regeneration measurement.

PLAIN-SPEAK SUMMARY

We changed one thing in the organism.

Before,
a cell could become uncertain
because the organism as a whole
was doing two kinds of work.

Now,
a cell becomes uncertain
because its own neighborhood
really contains conflicting evidence.

We tested that once across five worlds.

Then we froze a new experiment
and tested it again across five more worlds.

It repeated.

So this is no longer
an experimental trick.

It is now part of
the default hand-designed organism.

Everything else stays where it was.

V0 remains the historical baseline.

V0.1 is the new frozen starting point.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
