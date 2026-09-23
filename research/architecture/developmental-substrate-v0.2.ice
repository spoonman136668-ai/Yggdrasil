TITLE: YGGDRASIL — DEVELOPMENTAL SUBSTRATE V0.2
DATE: 2026-09-23
STATUS: FROZEN / GLOBAL RECRUITMENT POOL REMOVED AFTER INDEPENDENT CONFIRMATION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Advance the current hand-designed developmental substrate
from V0.1 to V0.2
by removing exactly one replicated unnecessary nonlocal dependency:

the organism-wide C/S recruitment-pool contribution
used in U-cell C/S recruitment.

No local replacement pool is added.

No other V0.1 mechanism changes.

PARENT

Developmental Substrate V0.1:

4d3887fba0478bc1ef3bc4bea44f8e08582f5803.

V0.1 architecture record:

research/architecture/developmental-substrate-v0.1.ice.

V0.1 remains the historical parent.

PROMOTION EVIDENCE

LU-0 strict-local identifiability closure:

074513c64a64318053fcbfcabdc9207202849063.

LU-0 established constructively
that the historical V0.1 global recruitment pool
can make two cells with byte-identical complete radius-12 local signatures
have different exact U-cell transition distributions.

Thus the pool is a genuine nonlocal dependency.

LU-0B closure:

c974b4def2973e72feec8b6be078c9255a0070d0.

LU-0B established
that the global recruitment-pool dependency
is active on ordinary fresh Task-1 trajectories.

LU-0C LU0CF1:

872509a6da0935e791f458eca42d0d8741c9e200.

LU-0C closure:

2356cdb49171a1144c3f56a28ba9d29a47f42796.

LU-0C observed:

LU0C_NO_POOL_SIMPLIFICATION_VIABLE = TRUE;

LU0C_LOCAL_POOL_PRESERVES_V01 = FALSE;

LU0C_LOCAL_POOL_ADDS_VALUE_OVER_NO_POOL = FALSE.

The five-world LU-0C NO_POOL arm passed
the full preregistered preservation envelope.

The first literal radius-12 recurrent local-pool replacement
did not pass its own preservation gate
and added no preregistered value over deletion.

LU-0D LU0DF1:

f23888e37fce4b19a65403dafe27f8a8848b8600.

LU-0D closure:

f77fa375e484859628081f67c54c734cf7eb41d5.

LU-0D independently confirmed NO_POOL
on five newly derived worlds.

LU0D_NO_POOL_CONFIRMED = TRUE.

All sixteen frozen confirmation checks passed.

LU-0D median NO_POOL Phase-4 completion:
125.0%.

LU-0D median paired Phase-4 delta
NO_POOL minus GLOBAL_POOL_PARENT:
+6.25 percentage points.

LU-0D Phase-0 preservation:
5 / 5.

LU-0D anchor recovery <=8:
5 / 5.

LU-0D demand-reversal recovery <=8:
5 / 5.

LU-0D lesion criterion:
5 / 5.

LU-0D incorrect DONE:
0 / 5 worlds.

LU-0D operation-cost bound:
5 / 5.

PROMOTED CHANGE

V0.2 changes only
the U-cell C/S recruitment-pool contribution.

Historical V0.1 recruitment uses
organism-wide pool terms:

pc_i;

ps_i.

V0.2 sets:

pc_i = 0;

ps_i = 0

for U-cell C/S recruitment.

No local recurrent pool replaces them.

NO_POOL U-CELL SUPPORT TERMS

Preserve the inherited constants:

W_POOL = 3/4;

W_LOCAL = 1/4;

K_SUPP = 1/2;

N_SUPP = 3;

ETA = 1/2.

With:

pc_i = 0;

ps_i = 0;

the inherited support terms reduce exactly to:

sup_C(i)
=
W_LOCAL * L_C3(i);

sup_S(i)
=
W_LOCAL * L_S3(i);

opp_C(i)
=
W_LOCAL * L_S3(i);

opp_S(i)
=
W_LOCAL * L_C3(i).

Preserve the exact inherited:

support_margin_field;

g_C;

g_S;

lambda_C;

lambda_S;

and state-transition sampling semantics.

The numerical weights are not renormalized.

W_LOCAL remains 1/4.

Do not silently rescale local support
to compensate for deletion of the pool.

LOCALITY EFFECT

The removed pc/ps term was
the known organism-wide information dependency
identified by LU-0 and LU-0B.

V0.2 introduces no replacement global statistic
and no recurrent local proxy.

Therefore this specific
organism-wide recruitment-pool channel
is absent from V0.2.

This does not by itself prove
that every V0.2 transition is strictly local.

Strict-local learned-updater readiness
must still be audited explicitly
before training.

UNCHANGED V0.1 CONTRACT

Retain exactly:

C / S / U / H / FC / FS state family;

rho = 3/4
where still used by inherited substrate mechanisms;

signed local B accumulation;

local evidence radius = 12;

Hill n = 3;

Hill K = 1/2;

cooperative / recruitment radius = 3;

ETA = 1/2;

D2 and D3 frozen refractory families;

A45 one-epoch ECHO_PHASE;

LOCAL_HEDGE default H semantics;

side-specific Q trace;

fixed bounded local topology;

anti-oracle constraints;

deterministic/stateless randomness discipline;

external global scoring only;

no hidden full-world controller.

LOCAL_HEDGE

Unchanged from V0.1.

For H cell i:

lambda_release_local(i)
=
ETA
*
[1 - min(L_C3(i), L_S3(i))]
*
[1 - local_H_density(i, HEDGE_R)].

Release probability remains:

1 - exp(-max(0, lambda_release_local)).

For recruitable U cell i:

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

Global C/S workload coexistence
does not enter H formation or H release.

ECHO_PHASE

Unchanged from V0 / V0.1:

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

V0.2 does not promote it.

EXCLUDED / NOT PROMOTED

Still excluded from the default substrate:

A49 challenge push-pull;

A51 challenge-field TTL memory;

A52 fixed TAU3 response delay;

A53 current-evidence-vetoed phase memory;

Task-1G repair EDF;

LU-0C LOCAL_POOL_R12.

LOCAL_POOL_R12 is not retained
because it failed its frozen preservation gate
and did not add value over simple deletion.

TASK-SPECIFIC MECHANISMS

Remain benchmark/interface mechanics,
not V0.2 developmental primitives:

R_TASK;

request pipeline;

request expiry;

task anchors;

task scheduler;

truth-table interpreter;

VERIFY / REPAIR packet lifecycle.

HISTORICAL RESULT BOUNDARY

Do not rewrite prior results.

V0:
historical frozen baseline.

V0.1:
historical LOCAL_HEDGE parent.

LU-0:
strict-local identifiability false
under the audited V0.1 signature.

LU-0B:
global-pool prevalence positive.

LU-0C:
NO_POOL viable;
LOCAL_POOL_R12 not preserved;
LOCAL_POOL_R12 no value over deletion.

LU-0D:
NO_POOL independently confirmed.

V0.2 does not claim
that LU-0 would have had a different result
under a substrate that did not yet exist.

It creates the new substrate
that must now be audited independently.

CURRENT SUBSTRATE STATUS

Developmental Substrate V0:
HISTORICAL.

Developmental Substrate V0.1:
HISTORICAL PARENT.

Developmental Substrate V0.2:
CURRENT HAND-DESIGNED SUBSTRATE.

A45 ECHO_PHASE:
CORE.

LOCAL_HEDGE:
CORE DEFAULT H SEMANTICS.

GLOBAL C/S RECRUITMENT POOL:
REMOVED.

LOCAL_POOL_R12:
NOT PROMOTED.

G5_FULL:
VALIDATED OPTIONAL / DEFAULT OFF.

NEXT RESEARCH BOUNDARY

Before training the first learned per-cell updater,
audit V0.2 for remaining information channels
that violate the intended student observation boundary.

The audit must answer:

given the complete proposed local student input,
is the exact V0.2 transition distribution identifiable?

Do not assume that deleting pc/ps
automatically proves full local identifiability.

If V0.2 is strictly locally identifiable
under a practical frozen input representation,
then proceed to the first teacher-imitation experiment
with V0.2 as the behavioral teacher/reference.

The first learned updater should remain:

shared across cells;

small;

feed-forward;

bounded to local cell/neighborhood state;

without task ids;

without future information;

without global score;

without centralized planning.

Training success must not authorize deployment.

Functional-regeneration and held-out perturbation tests
remain required after imitation.

PLAIN-SPEAK SUMMARY

We removed a wire.

The old organism gave every recruitable cell
a little piece of organism-wide information:

how much C-type and S-type recruitment pressure
existed across the whole system.

That was a problem
for a future genuinely local learned cell.

We first proved the wire was real.

Then we tried replacing it
with a local memory.

The local memory did not earn its complexity.

Then we tried simply unplugging the wire.

That worked across five worlds.

We froze a completely new experiment
and tried the unplugged version
across five more worlds.

It worked again.

So V0.2 removes the wire
and adds nothing in its place.

Everything else stays the same.

The next question is now much cleaner:

does any other hidden nonlocal information
still remain
before we train the first learned cell?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
