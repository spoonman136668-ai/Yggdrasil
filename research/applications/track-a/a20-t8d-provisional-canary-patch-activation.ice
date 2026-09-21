TITLE: YGGDRASIL A20 / T8D — Provisional Canary Patch Activation
DATE: 2026-09-21
STATUS: PREREGISTERED PROSPECTIVE CANARY EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8D / APPLICATION-A
PARENT: A19 Distributed Shadow-Gated Patch Activation Calibration
BRANCH: dg1a-ar

PURPOSE

A19 showed that four-observation shadow rehearsal,
independent evaluator agreement,
and exhaustive enumeration of all 495 four-cell replacement geometries
still did not establish safe activation authority.

Two patches were unanimously favorable across all shadow geometries
and still underperformed on untouched held-out demand.

Therefore A20 stops trying to infer full activation safety
from rehearsal alone.

A20 tests whether a learned patch can gain authority gradually
through bounded real exposure.

The patch is already learned,
provenance-qualified,
ancestry-qualified,
and preserved exactly as in A17-FIXA.

A20 changes only activation authority.

CORE IDEA

At the first real turnover episode,
do not give all four newborn cells the learned patch.

Expose only:

1 of 4;
2 of 4;
or
3 of 4

newborn cells to candidate birth-control authority.

The remaining newborns use the stale-previous active prior.

Run the first eight genuine held-out epochs.

Maintain a preserved stale-control twin
from the identical pre-turnover state.

At epoch 8,
before the second turnover,
compare cumulative canary service
against the preserved stale twin.

Decision rule:

canary service > stale twin:
EXPAND.

canary service == stale twin:
HOLD.

canary service < stale twin:
REVOKE.

EXPAND:
continue from the canary trajectory
and give all four epoch-8 newborns candidate birth-control authority.

HOLD:
continue from the canary trajectory
and preserve the same canary exposure fraction
for the four epoch-8 newborns.

REVOKE:
discard the canary trajectory at the epoch-8 boundary,
restore the preserved stale twin state,
and give all four epoch-8 newborns stale-prior authority.

The learned patch record is never deleted.

A20 asks whether bounded real exposure
can provide better prospective activation evidence
than A19 shadow confidence.

FROZEN SCIENTIFIC INPUT

Original A17 scientific seed F17:

3ec24f8242285688a537f5e7dd6e9a231a645597.

Corrected executable freeze F17A:

c33df49a8b171c1f6cd8e64820dd3bca0e2f4492.

A17 primary manifest SHA-256:

8284e3f1e47a17f234eb02f2b427cddaee16999e0df795d38f1b0b457cf8e43f.

A17 corrected primary result SHA-256:

ee53b151295a5d31ba1e54e4cd8d4deae0aff604ff3b66406fb87b748a08306d.

A18 closure:

80d4801a636ef527ae35dd424a9bb11f7fd70d57.

A19 closure:

7f5ef08197b82ef3af84b167ea24718a66afd779.

A20 reuses exactly the frozen A17:

12 scenarios;
four patch paths per scenario;
16 held-out evaluation demands per patch;
replacement episodes 0 and 8;
canonical four-cell replacement target sets;
candidate target prior;
stale-previous prior;
sequential pre-evaluation cell state.

No A20 rule may inspect epochs 8-15
before the epoch-8 activation decision.

A20 FREEZE

Let the exact A20 implementation freeze commit be:

F20.

No real A20 canary outcome may be observed before F20 exists.

CANARY ARMS

C1 — ONE-OF-FOUR CANARY

At epoch 0 replacement:

first one canonical replacement birth:
candidate prior.

remaining three:
stale-previous prior.

Maximum unproven newborn exposure:

25%.

C2 — TWO-OF-FOUR CANARY

At epoch 0:

first two canonical replacement births:
candidate prior.

remaining two:
stale-previous prior.

Maximum unproven newborn exposure:

50%.

C3 — THREE-OF-FOUR CANARY

At epoch 0:

first three canonical replacement births:
candidate prior.

remaining one:
stale-previous prior.

Maximum unproven newborn exposure:

75%.

The order of the four canonical replacement cell IDs
is exactly the frozen A17 replacement tuple order.

No arm may reorder replacement IDs post hoc.

MIXED BIRTH CONTROL

For each replacement birth:

remove all four canonical target cells first,
as in A17.

Recreate targets sequentially in canonical tuple order.

If that birth is candidate-controlled:

choose birth role using the learned target prior.

If stale-controlled:

choose birth role using the stale-previous prior.

The chosen newborn joins the live population
before the next replacement birth,
exactly as in inherited A17 replacement semantics.

CANARY / TWIN EXECUTION

For each patch evaluation,
start from the exact frozen A17 pre-evaluation cell state.

Fork:

A — canary trajectory;
B — stale-control twin.

At epoch 0:

A uses C1 / C2 / C3 mixed birth control.

B uses all-stale birth control.

For epochs 0 through 7:

both trajectories receive
the exact same frozen A17 demand sequence.

Both use the exact inherited deterministic migration rule.

Record service every epoch.

No information from trajectory B changes trajectory A before epoch 8.
The twin exists only as a bounded control / rollback authority.

EPOCH-8 DECISION

Compute:

CANARY_EVIDENCE_DELTA
=
cumulative service A[0:8]
-
cumulative service B[0:8].

If > 0:

EXPAND.

If == 0:

HOLD.

If < 0:

REVOKE.

No other statistic may affect the decision.

No A19 shadow score may affect the decision.

No epoch 8-15 demand may affect the decision.

SECOND TURNOVER

EXPAND:

continue trajectory A;
all four canonical epoch-8 replacement births use candidate prior.

HOLD:

continue trajectory A;
use the same C1 / C2 / C3 candidate/stale birth exposure pattern
for epoch-8 replacements.

REVOKE:

replace trajectory A state with the exact preserved stale-control twin state
at the epoch-8 boundary;
all four epoch-8 replacement births use stale prior.

Then execute epochs 8 through 15
using the exact frozen A17 demands and migration rule.

REFERENCE ARMS

R0 — ALWAYS STALE

All epoch-0 and epoch-8 replacement births use stale-previous prior.

R1 — ALWAYS PATCH

Exact A17 candidate behavior:

all epoch-0 and epoch-8 replacement births use learned target prior.

These are references only.

PRIMARY METRICS

For each C1 / C2 / C3 arm report:

EXPAND count;
HOLD count;
REVOKE count;

canary-phase service epochs 0-7;
stale-twin canary-phase service epochs 0-7;
canary-phase regret versus stale twin;

second-half service epochs 8-15;
matched stale-twin second-half service;
second-half delta;

complete 16-epoch service;
delta versus always-stale;
delta versus always-patch;

harmful expansions:
EXPAND and second-half service < stale-twin second-half;

beneficial expansions:
EXPAND and second-half service > stale-twin second-half;

neutral expansions:
EXPAND and second-half service == stale-twin second-half;

harmful holds:
HOLD and second-half service < stale-twin second-half;

beneficial holds:
HOLD and second-half service > stale-twin second-half;

revoked patches that would have been harmful under full A17 activation
over epochs 8-15;

revoked patches that would have been beneficial under full A17 activation
over epochs 8-15;

maximum unproven newborn exposure;

number of epochs during which an unproven patch controls
at least one newborn lineage.

PROSPECTIVE VALIDITY

The key test is not merely total service.

A20 asks whether the sign of:

CANARY_EVIDENCE_DELTA

predicts the sign of independent second-half consequence.

For each arm report a 3x3 table:

decision:
EXPAND / HOLD / REVOKE

versus second-half full-candidate advantage relative to stale:

beneficial / neutral / harmful.

For EXPAND specifically report:

precision for second-half beneficial or neutral outcomes;
strict beneficial precision;
harm rate.

KNOWN HARD CASES

A19 identified two false-confidence cases:

S00/P3;
S11/P4.

A20 reports their C1 / C2 / C3 decisions
and untouched second-half consequences.

They are diagnostic cases only.

No rule is tuned around them.

RESTART / REVERSIBILITY

A20 must prove exact restart equivalence at:

after epoch-0 replacement;
after epoch 3;
immediately before epoch-8 decision;
immediately after REVOKE restore.

REVOKE must restore:

exact cell IDs;
exact roles;
exact stale twin state;
exact active prior authority.

The learned patch record remains immutable and preserved.

No patch deletion.

No C-v3.

No duplicate context.

No new major version.

DEDICATED PROBES

P1 — EPOCH-8 LEAKAGE

If any epoch 8-15 demand is visible to the decision function:

fail closed.

P2 — CANARY EXPOSURE LIMIT

C1 may expose exactly 1 / 4 epoch-0 newborns;
C2 exactly 2 / 4;
C3 exactly 3 / 4.

Never more.

P3 — TWIN STATE IDENTITY

Before epoch-0 replacement,
canary and stale twin must be byte-identical.

P4 — SAME DEMAND STREAM

Epochs 0-7 demand identities must match exactly
between canary and twin.

P5 — STRICT DECISION SIGN

positive -> EXPAND;
zero -> HOLD;
negative -> REVOKE.

No confidence override.

P6 — REVOKE RESTORE

After REVOKE,
pre-epoch-8 state must equal stale twin exactly.

P7 — DORMANT PATCH PRESERVATION

REVOKE cannot delete or mutate the learned patch.

P8 — HOLD EXPOSURE PRESERVATION

HOLD must repeat exactly the arm's original exposure fraction
at epoch 8.

P9 — EXPAND AUTHORITY

EXPAND may give candidate authority
to all four epoch-8 newborns,
but not retroactively rewrite existing cells.

P10 — NO GOVERNANCE GROWTH

Major history remains [v1,v2];
slot count remains 3.

NEGATIVE / LIMIT CONTROLS

N1 — FULL ACTIVATE AT EPOCH 0

Reference A17 behavior.

N2 — USE EPOCHS 8-15 IN DECISION

Invalid future leakage.

N3 — CANARY WITHOUT STALE TWIN

Cannot distinguish patch consequence from ordinary trajectory variation.

N4 — REVOKE WITHOUT STATE RESTORE

Leaves unproven trajectory residue.

N5 — DELETE PATCH ON REVOKE

Destroys learned evidence unnecessarily.

N6 — CANARY FRACTION ABOVE 3 / 4

Outside A20 safety envelope.

N7 — NONSTATIONARY DRIFT INSIDE EPOCHS 0-15

Boundary.

A20 assumes the frozen A17 patch-evaluation demand sequence
represents one bounded evaluation interval.

INTERPRETATION RULES

A20 is primarily a realization experiment,
not a contest to choose the highest-service arm.

Evidence for useful canary activation exists if
at least one bounded arm materially reduces harmful full activation
while preserving a substantial fraction of beneficial second-half activations
and keeping canary-phase regret bounded.

Evidence against simple canary activation exists if:

positive canary evidence frequently predicts harmful second-half outcomes;

or

safe exposure levels provide too little signal
to distinguish beneficial from harmful activation.

C1 / C2 / C3 are all reported.

No exposure fraction becomes canonical
solely because it has the highest observed aggregate service.

Any later production-like sequential controller
requires a new preregistered experiment.

PLAIN-SPEAK PREREGISTERED QUESTION

A19 tried to predict whether a patch was safe
before letting it touch the organism.

That helped,
but even perfect rehearsal consensus could be wrong.

A20 stops pretending we can know everything in advance.

Instead:

learn the patch;
keep it in memory;
let only a few newborn cells try it;
compare what actually happens
with an untouched old-policy twin;
then decide.

If the small trial wins:

give the patch more authority.

If it ties:

keep the trial small.

If it loses:

restore the old trajectory
and put the patch back into dormant memory.

The second half of the world stays hidden
until after that decision.

So A20 asks:

CAN YGGDRASIL LEARN FROM A SMALL REAL CONSEQUENCE
BEFORE RISKING A LARGE ONE?

That is the first direct test of:

provisional authority;
bounded exposure;
real consequence-based self-evaluation;
reversible activation;
and earned trust.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
