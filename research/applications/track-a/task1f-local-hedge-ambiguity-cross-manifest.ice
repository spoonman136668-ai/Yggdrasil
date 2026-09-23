TITLE: TASK-1F — Local Hedge Ambiguity Cross-Manifest Differential
DATE: 2026-09-22
STATUS: PREREGISTERED / NOT EXECUTED
TRACK: DG-1 / TASK-1
PARENT: TASK-1E T1EF1 PRIMARY CLOSURE
PARENT CLOSURE: 532862b59937e53b37e39c5c0f25fbf259ea704e
STATE DIAGNOSIS: f7850403306be7244d7f2cbf48883c8ff8ebf240

QUESTION

Does the frozen V0 H state fail spatial task redeployment
because it interprets population-wide coexistence of C and S demand
as local ambiguity?

Can H formation / release use only local C/S evidence
while every other V0 and Task-1 mechanism remains unchanged?

MOTIVATION

Task-1E removed the dominant request-handoff artifact.

REQUEST_BOUND improved:

Phase-4 final-16:
34.375% -> 78.125%.

Legacy completion:
6.98% -> 97.67%.

Anchor recovery:
not attained -> 0 epochs.

But Task-1E remained formally unqualified.

The exact post-closure replay then localized
the remaining deficit to the relocated S region.

Final-16 relocated S-ingress neighborhood:

mean H:
4.375 of 5 cells.

mean S:
0.5.

mean U:
0.125.

Local evidence at that same ingress:

L_S3:
1.0.

L_C3:
0.0.

L_S12:
0.345.

L_C12:
0.0025.

Thus the local task signal is strongly and correctly S-sided.

Yet the inherited normalized population pools remain:

P_C:
approximately 0.936.

P_S:
approximately 0.988.

The inherited H release and H formation rules
use the globally mixed support values.

Observed final-16 H-release probability
near relocated S ingress:

approximately 3.37% per H cell / epoch.

No new Phase-4 S request completes.

This suggests that H currently represents:

GLOBAL COEXISTENCE

rather than:

LOCAL AMBIGUITY.

Task-1F tests exactly that distinction.

FROZEN PARENTS

Developmental Substrate V0:
92654adf407310a01e368e2c53934beae749482c

Task-1 T1F1:
22b6ab5a036732cc9efbda077069e971c34a337e

Task-1B T1BF1:
83af31c2a95adeba47700f7c34d159d7739549c9

Task-1E T1EF1:
04872029aeb773b3e98ccb71537c18ff965487e1

Task-1E closure:
532862b59937e53b37e39c5c0f25fbf259ea704e

NO OTHER CHANGE

Preserve exactly:

D2;

G5_FULL OFF;

B update;

rho = 3/4;

radius-12 evidence;

radius-3 recruitment evidence;

ECHO_PHASE;

Hill law;

committed-cell defection;

refractory semantics;

C/S recruitment support law;

support-margin field;

fixed 64-cell ring;

R_TASK = 2;

neutral sensing;

request-bound anchor handoff;

oldest-request-first local deferred matching;

one operation per cell per epoch;

one operation per request per epoch;

six-edge route;

route direction;

32-epoch expiry;

verification;

repair;

5% corruption;

distributed lesion;

five 32-epoch phases;

+16 anchor shift;

two arrivals per epoch;

truth-table interpreter.

PRIMARY ARMS

Exactly two dynamic arms per replicate.

GLOBAL_HEDGE

Exact Task-1E REQUEST_BOUND parent.

No change.

LOCAL_HEDGE

Exact GLOBAL_HEDGE
except the evidence source used
by the H transition family.

SINGLE SEMANTIC FACTOR

The H state is defined as
local ambiguity.

Both directions of the H transition family
must use the same local ambiguity source.

No other equation changes.

PARENT H RELEASE

The frozen parent computes:

sup_C
=
W_POOL * P_C
+
W_LOCAL * L_C3(i)

sup_S
=
W_POOL * P_S
+
W_LOCAL * L_S3(i)

then:

lambda_release_parent
=
ETA
*
[1 - min(sup_C, sup_S)]
*
[1 - local_H_density].

LOCAL_HEDGE RELEASE

Replace only the ambiguity inputs:

hedge_C(i) = L_C3(i)

hedge_S(i) = L_S3(i)

lambda_release_local
=
ETA
*
[1 - min(hedge_C, hedge_S)]
*
[1 - local_H_density].

No gain.

No threshold.

No smoothing.

No phase input.

No task-stream special case.

PARENT H FORMATION

For an eligible U cell,
the frozen parent uses:

lambda_H_parent
=
ETA
*
sup_C
*
sup_S
*
[1 + local_H_density].

LOCAL_HEDGE FORMATION

Replace only the H ambiguity inputs:

lambda_H_local
=
ETA
*
L_C3(i)
*
L_S3(i)
*
[1 + local_H_density].

C/S recruitment remains exactly parent:

lambda_C unchanged.

lambda_S unchanged.

Therefore Task-1F does NOT
remove the global pool
from C/S support.

It changes only whether
the H state treats remote opposite-side demand
as local ambiguity.

RNG DISCIPLINE

Preserve the exact parent RNG:

same state-independent base;

same epoch/cell identities;

same H-release salt;

same U recruitment salt;

same task randomness.

LOCAL_HEDGE changes transition probabilities
only through the preregistered H lambda values.

No new random stream.

MECHANISM TELEMETRY

For each replicate and arm report:

H cells evaluated;

mean parent-equivalent H-release probability;

mean active H-release probability;

H -> U transitions;

eligible U cells;

mean parent-equivalent lambda_H;

mean active lambda_H;

U -> H transitions;

U -> C transitions;

U -> S transitions.

For Phase 4 additionally report:

same quantities globally;

same quantities
within R_TASK of the relocated C ingress;

same quantities
within R_TASK of the relocated S ingress;

final-16 C/S/H/U composition
near each relocated ingress;

new Phase-4 correct DONE by stream.

CROSS-MANIFEST DESIGN

Task-1F uses exactly:

5 fresh primary manifests.

They are derived only after T1FF1 exists.

For replicate k in {1,2,3,4,5}:

derive a deterministic replicate key
from:

T1FF1;
literal TASK1F-REPLICATE;
k.

From that key derive:

four fresh balanced,
nonconstant,
non-affine truth tables;

fresh task seed;

320 arrivals;

corruption schedule;

lesion offset;

absolute anchor rotation.

Every replicate preserves
the same frozen task geometry and phase contract.

All five manifests
must be bound before
any Task-1F primary arm executes.

No replicate may be replaced.

No additional replicate
may be added after results.

POST-FREEZE DISCIPLINE

Implement and mechanically validate.

Freeze exact implementation as T1FF1.

Only after T1FF1:

derive all five primary manifests.

Commit one five-manifest binding
before primary execution.

Run two complete
five-replicate primary sweeps.

The complete serialized sweep outputs
must be byte-identical
before scientific interpretation.

MECHANICAL GATE

Before T1FF1 prove:

1. GLOBAL_HEDGE exact behavioral parity
   with Task-1E REQUEST_BOUND
   on the mechanical manifest.

2. LOCAL_HEDGE differs from GLOBAL_HEDGE
   only through H release / H formation lambdas.

3. C/S B update exact parent parity.

4. committed-cell defection exact parent law.

5. lambda_C exact parent law.

6. lambda_S exact parent law.

7. ECHO_PHASE exact parent law.

8. request-bound handoff exact parent semantics.

9. neutral sensing exact parent semantics.

10. scheduler exact parent semantics.

11. task lifecycle exact parent semantics.

12. no new RNG namespace.

13. no global majority input.

14. no phase identifier enters H semantics.

15. H release uses only L_C3 / L_S3
    plus local H density.

16. H formation uses only L_C3 / L_S3
    plus local H density.

17. one-operation cell/request invariants pass.

18. all inherited integrity probes pass.

19. two complete mechanical sweeps
    are byte-identical.

PRIMARY INFORMATION GAIN

For each replicate k,
define:

gain_k
=
LOCAL_HEDGE Phase-4 final-16 correct-completion rate
-
GLOBAL_HEDGE Phase-4 final-16 correct-completion rate.

Define final16 backlog reduction
against GLOBAL_HEDGE
for the same replicate.

TASK1F_LOCAL_HEDGE_INFORMATION_GAIN = TRUE iff all are true:

1. mechanism active
   in all five replicates;

2. Phase-0 LOCAL_HEDGE completion
   >=95% of GLOBAL_HEDGE
   in every replicate;

3. gain_k > 0
   in at least 4 of 5 replicates;

4. median gain_k
   >=10 percentage points;

5. final-16 total backlog
   is lower under LOCAL_HEDGE
   in at least 4 of 5 replicates;

6. median final-16 backlog reduction
   >=15%;

7. LOCAL_HEDGE new Phase-4 S correct completions
   exceed GLOBAL_HEDGE
   in at least 4 of 5 replicates;

8. incorrect DONE = 0
   in every LOCAL_HEDGE replicate;

9. operations per correct completion
   <=125% of paired GLOBAL_HEDGE
   in every replicate;

10. all integrity probes pass.

PRIMARY QUALIFICATION

TASK1F_QUALIFIED = TRUE iff
TASK1F_LOCAL_HEDGE_INFORMATION_GAIN = TRUE
and all are true:

1. median LOCAL_HEDGE
   Phase-4 final-16 correct completion
   >=85%;

2. at least 4 of 5 LOCAL_HEDGE replicates
   achieve Phase-4 final-16
   >=85%;

3. anchor-rotation recovery
   <=8 epochs
   in at least 4 of 5 replicates;

4. demand-reversal recovery
   <=8 epochs
   in all five replicates;

5. lesion recovery
   <=8 epochs
   or paired lesion-backlog nonregression
   in all five replicates;

6. repair detection
   >=95%
   in every replicate
   where corrupted work reaches egress;

7. repair success
   >=90%
   in every replicate
   where a corrupted request is detected;

8. no replicate has
   worse than 5 percentage-point
   Phase-0 completion regression
   versus its paired GLOBAL_HEDGE.

FAILURE ATTRIBUTION

If LOCAL_HEDGE releases H locally
but Phase-4 throughput does not improve:

H trapping is real
but not the dominant remaining bottleneck.

If S completion improves
but C or earlier phases regress:

global pool participation in H
was providing a broader stabilizing function
that local ambiguity alone loses.

If one or two manifests improve strongly
but cross-manifest criteria fail:

the mechanism is location / history sensitive
and is not robust enough for V0 promotion.

If information gain is robust
but the 85% qualification bar remains unmet:

local H semantics are useful,
but another independent spatial-service seam remains.

If TASK1F qualifies:

promote local-ambiguity H semantics
as a candidate V0.1 substrate change
only after a separate frozen confirmation.

Do not silently rewrite V0
inside Task-1F.

NO POST-RESULT TUNING

Do not change:

H radius;

local evidence radius;

release coefficient;

formation coefficient;

pool weights outside H;

C/S recruitment;

thresholds;

number of manifests;

manifest selection;

task load;

anchor displacement;

expiry;

scheduler;

handoff;

D family;

G5;

or qualification
after primary results.

PLAIN-SPEAK QUESTION

The organism has C work
and S work at the same time.

That does not mean
every neighborhood is confused.

A cell beside a pile of S jobs
should not stay undecided
just because C jobs exist
on the other side of the organism.

Task-1F asks:

WHAT IF "I AM UNCERTAIN"
MEANS

"MY LOCAL NEIGHBORHOOD
HAS CONFLICTING EVIDENCE"

instead of

"THE WHOLE ORGANISM
HAS MORE THAN ONE KIND OF WORK"?

Nothing else changes.

And because one lucky location
would not be enough evidence,
we test the rule on five fresh worlds.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
