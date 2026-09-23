TITLE: TASK-1H — Independent LOCAL_HEDGE Confirmation
DATE: 2026-09-23
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / TASK-1
PARENT: TASK-1F T1FF1-R1
SERVICE-ENVELOPE AUDIT: e6ea693894ab12a6d542d50e297e97abf801124c

PURPOSE

Independently confirm the Task-1F causal result
before changing Developmental Substrate V0.

Task-1H introduces no new mechanism.

It compares the exact frozen:

GLOBAL_HEDGE

versus

LOCAL_HEDGE

semantics from Task-1F
on five new manifests
derived only after Task-1H freeze.

PARENT IDENTITIES

Developmental Substrate V0:
92654adf407310a01e368e2c53934beae749482c.

Task-1F T1FF1-R1:
1b05bc066314138a0eae05c02c31ba8b84f5f063.

Task-1F frozen source SHA256:
a3122a9f4f6da6c138cc12944528f5e2e3ef608e904067ef30da7feab7d640f4.

Task-1F closure:
fda86a2fee99fb948524b53b0eb0652011d655f6.

Task-1G closure:
b11eb856b1348d8d08cc99497ac59f7a15e7ceaa.

Task-1 service-envelope audit:
e6ea693894ab12a6d542d50e297e97abf801124c.

NO DYNAMICS CHANGE

Task-1H must use exact Task-1F arm dynamics.

GLOBAL_HEDGE:
exact frozen Task-1F parent global ambiguity semantics.

LOCAL_HEDGE:
exact frozen Task-1F local ambiguity semantics.

No scheduler change.

No EDF.

No expiry change.

No admission change.

No handoff change.

No repair change.

No verification change.

No task-radius change.

No D-family change.

No G5.

No topology change.

No new RNG namespace inside dynamics.

PRIMARY ARMS

Exactly two:

GLOBAL_HEDGE;
LOCAL_HEDGE.

FRESH MANIFESTS

After the exact Task-1H driver freezes as T1HF1,
derive exactly five primary manifests.

For replicate k in 1..5:

replicate key =
SHA1(
"TASK1H-CONFIRM|" +
T1HF1 +
"|" +
k
).

Task seed =
first 32 hex chars of:

SHA256(
"TASK1H-PRIMARY-SEED|" +
T1HF1 +
"|" +
k
).

Use the frozen Task-1 manifest generators
for:

four balanced nonconstant nonaffine truth tables;

320 arrivals;

5% stateless corruption schedule;

distributed eight-cell lesion;

initial anchors;

+16 Phase-4 anchors.

Bind all five manifests
before any primary arm executes.

No manifest replacement.

No sixth replicate.

DUPLICATE GATE

Run two complete five-replicate sweeps.

They must be byte-identical
before any scientific interpretation.

MECHANICAL GATE

Before T1HF1 prove:

1. GLOBAL_HEDGE exact parity
   with frozen Task-1F GLOBAL_HEDGE
   on the mechanical manifest.

2. LOCAL_HEDGE exact parity
   with frozen Task-1F LOCAL_HEDGE
   on the mechanical manifest.

3. Task-1F LOCAL_HEDGE mechanism telemetry
   remains active.

4. No dynamics code is reimplemented.

5. D2 remains frozen.

6. G5_FULL remains OFF.

7. N = 64.

8. R_TASK = 2.

9. Request-bound handoff remains frozen.

10. Neutral sensing remains frozen.

11. One-op cell/request invariants pass.

12. Primary-format manifests survive
    JSON serialization round-trip.

13. Two complete mechanical sweeps
    are byte-identical.

PRIMARY CONFIRMATION QUESTION

Task-1H does NOT attempt
to retroactively qualify Task-1F.

It asks only:

DOES LOCAL_HEDGE REPLICATE
ITS CAUSAL SPATIAL-ORGANIZATION ADVANTAGE
ON A NEW PREREGISTERED WORLD SET?

For each replicate define:

phase4_gain_k =
LOCAL_HEDGE Phase-4 final-window completion
-
GLOBAL_HEDGE paired value.

backlog_reduction_k =
(
GLOBAL_HEDGE final-16 backlog area
-
LOCAL_HEDGE final-16 backlog area
)
/
GLOBAL_HEDGE final-16 backlog area.

new_S_gain_k =
LOCAL_HEDGE new Phase-4 S correct completions
-
GLOBAL_HEDGE paired value.

TASK1H_LOCAL_HEDGE_CONFIRMED = TRUE iff all are true:

1. LOCAL_HEDGE ambiguity mechanism is active
   in all five replicates;

2. Phase-0 LOCAL_HEDGE completion
   >=95% of GLOBAL_HEDGE
   in every replicate;

3. phase4_gain_k > 0
   in at least 4 of 5 replicates;

4. median phase4_gain
   >=10 percentage points;

5. LOCAL_HEDGE final-16 backlog area
   is lower in at least 4 of 5 replicates;

6. median backlog reduction
   >=15%;

7. new_S_gain_k > 0
   in at least 4 of 5 replicates;

8. incorrect DONE = 0
   in every LOCAL_HEDGE replicate;

9. LOCAL_HEDGE operations per correct completion
   <=125% of GLOBAL_HEDGE
   in every replicate;

10. all integrity probes pass.

STRONG CONFIRMATION

TASK1H_LOCAL_HEDGE_STRONG_CONFIRMATION = TRUE iff
TASK1H_LOCAL_HEDGE_CONFIRMED = TRUE
and all are true:

1. median LOCAL_HEDGE Phase-4 final-window completion >=85%;

2. at least 4 of 5 LOCAL_HEDGE replicates
   have Phase-4 final-window completion >=85%;

3. anchor-rotation recovery <=8 epochs
   in at least 4 of 5 LOCAL_HEDGE replicates;

4. demand-reversal recovery <=8 epochs
   in all five;

5. lesion recovery criterion
   passes in all five.

REPAIR METRICS

Continue to report:

repair detection;

repair success;

age at first VERIFY;

deadline-impossible detections;

horizon-censored repaired requests.

But repair-success threshold
is NOT part of Task-1H LOCAL_HEDGE confirmation.

Reason:

Task-1H is a mechanism replication,
not a redefinition of Task-1 overall qualification.

The frozen service-envelope audit
already established that
Task-1F / Task-1G repair misses
can arise from deadline impossibility
and finite-horizon censoring.

This reporting rule does not alter
Task-1F or Task-1G qualification.

V0.1 DECISION RULE

If TASK1H_LOCAL_HEDGE_STRONG_CONFIRMATION = TRUE:

LOCAL_HEDGE may be promoted
through a separate architecture decision
from experimental candidate
to Developmental Substrate V0.1 default H semantics.

The architecture decision must preserve:

Task-1F remained formally unqualified;

Task-1G remained negative;

promotion is based on
replicated causal information gain
plus service-envelope diagnosis,
not retroactive threshold editing.

If Task-1H fails confirmation:

do not promote LOCAL_HEDGE.

Return to diagnosis
before opening learned-updater training.

NO POST-RESULT TUNING

Do not change:

replicate count;

manifest derivation;

Task-1 programs;

arrival load;

expiry;

horizon;

lesion;

anchors;

H equations;

qualification thresholds;

or parent dynamics
after primary execution begins.

PLAIN-SPEAK QUESTION

We already saw LOCAL_HEDGE work
on five fresh worlds.

Before we bake it into the organism,
we are going to ask it again
on five more worlds
that do not exist yet.

Nothing new is being added.

If the same local-ambiguity rule
again helps the organism
move useful work
after the environment shifts,

then we have a replicated reason
to make it part of V0.1.

If it does not repeat,
we leave V0 alone.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
