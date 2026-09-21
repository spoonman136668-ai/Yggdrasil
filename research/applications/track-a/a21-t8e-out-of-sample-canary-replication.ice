TITLE: YGGDRASIL A21 / T8E — Out-of-Sample Canary Activation Replication
DATE: 2026-09-21
STATUS: PREREGISTERED CONFIRMATORY REPLICATION / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8E / APPLICATION-A
PARENT: A20 Provisional Canary Patch Activation
BRANCH: dg1a-ar

PURPOSE

A20 discovered a one-sided activation signal on the known A17 worlds:

positive real-canary evidence
was followed by zero harmful expansion decisions
across C1 / C2 / C3.

But A20 reused the same frozen A17 demand / turnover worlds
whose behavior had already been exposed by A17-A19.

A21 is therefore a true out-of-sample replication.

It keeps:

the exact 48 learned patch contexts;
the exact A17 pre-evaluation starting cell states;
the same candidate and stale developmental priors;
the same A20 C1 / C2 / C3 canary decision rule.

It replaces:

the held-out demand sequence;
the epoch-0 replacement set;
the epoch-8 replacement set

with fresh post-F21 trajectories
that cannot exist before the A21 implementation freeze.

PRIMARY QUESTION

Does:

positive first-half real-canary consequence

continue to predict:

non-harmful second-half expansion

on fresh demand / turnover trajectories
that were unavailable during A17-A20 design?

FROZEN INPUT

A20 closure:

baa499248e98066d9b9ba5adbe30fb488dec631d.

A20 source SHA-256:

4e39349fba10c51116164d46a8cdda0d27bc23c0cae08742b281f3d19d6f7cb2.

A17 F17:

3ec24f8242285688a537f5e7dd6e9a231a645597.

The 48 patch contexts remain the exact A17:

12 scenarios x 4 patches.

For each context:

candidate prior = learned A17 patch target;
stale prior = immediately previous A17 learned prior;
starting cell state = exact A17 pre-evaluation candidate state.

A21 does not redraw patch targets.

A21 tests generalization across trajectory uncertainty,
not generalization across patch semantics.

A21 FREEZE

Let the exact A21 implementation freeze commit be:

F21.

No real A21 trajectory may be derived before F21 exists.

POST-FREEZE REPLICATION MANIFEST

After F21,
derive exactly:

8 independent trajectory replicas

for each of the 48 patch contexts.

Total fresh trajectories:

384.

For replica r in 0..7:

derive 16 evaluation demands as eight symmetric zero-mean pairs
around the already-learned candidate target
under:

YGG-A21-EVAL|F21|scenario|patch|replica|pair.

Derive epoch-0 and epoch-8 four-cell replacement sets under:

YGG-A21-REPLACE|F21|scenario|patch|replica|epoch|cell_id.

Replacement sets contain exactly four unique IDs.

The complete 384-trajectory manifest
must be hash-bound in the repository
before primary A21 execution.

No trajectory may be rejected
because of its expected result.

CANARY RULE

Exactly the frozen A20 rule.

C1:
1 / 4 candidate-controlled epoch-0 newborns.

C2:
2 / 4.

C3:
3 / 4.

Remaining epoch-0 newborns use stale prior.

A preserved all-stale twin starts from the identical state.

Run fresh epochs 0-7.

Decision:

canary service > stale twin:
EXPAND.

canary service == stale twin:
HOLD.

canary service < stale twin:
REVOKE.

At epoch 8:

EXPAND:
continue canary state;
4 / 4 candidate newborns.

HOLD:
continue canary state;
repeat the arm's original exposure fraction.

REVOKE:
restore exact stale-twin state;
0 / 4 candidate newborns.

Then run fresh epochs 8-15.

Epochs 8-15 remain invisible to the decision.

REFERENCE TRUTH

For every fresh trajectory also run:

R0 all-stale;
R1 all-candidate.

These are evaluation references only.

PRIMARY CONFIRMATORY SIGNAL PER ARM

An arm is REPLICATION-QUALIFIED iff all are true:

EXPAND decisions >= 48
AND
actual second-half harmful EXPAND rate <= 0.05
AND
full-candidate second-half harmful labels among EXPAND decisions <= 0.05
AND
actual EXPAND harm rate is no greater than half
the unconditional R1 second-half harm rate
when the unconditional harm rate is nonzero
AND
all restart / leakage / exposure / restore probes pass.

Coverage floor:

48 expansions

means the arm must earn expansion
on at least 12.5% of 384 fresh trajectories.

The 5% harm ceiling is fixed before F21.

No post-result threshold changes.

MINIMUM-EXPOSURE SELECTION RULE

A21 does not choose the highest-service arm.

If multiple arms are REPLICATION-QUALIFIED,
the selected arm for a future sequential-controller experiment is:

lowest unproven exposure first.

Selection order:

C1;
then C2;
then C3.

If C1 qualifies:
select C1.

Else if C2 qualifies:
select C2.

Else if C3 qualifies:
select C3.

Else:
no arm selected.

This hierarchy is frozen before results.

SECONDARY METRICS

For each arm report:

EXPAND / HOLD / REVOKE counts;

actual second-half harmful / neutral / beneficial EXPAND outcomes;

full-candidate second-half harmful / neutral / beneficial labels among EXPAND decisions;

canary-phase regret versus stale twins;

second-half delta versus stale twins;

complete service delta versus R0;

complete service delta versus R1;

revoked beneficial / neutral / harmful R1 opportunities;

held beneficial / neutral / harmful R1 opportunities;

maximum unproven exposure.

Report per-replica and per-patch-context concentration.

A result must not be carried by one scenario alone
without being disclosed.

INTEGRITY PROBES

P1:
A17 replay still equals 3978 / 3950 / 37-of-48 / 38 before A21 trajectory derivation.

P2:
384 unique trajectory identities.

P3:
each trajectory has exactly 16 demands
whose exact mean equals candidate target.

P4:
each trajectory has exactly four unique replacement IDs
at epoch 0 and epoch 8.

P5:
no A21 trajectory tag equals an A17 evaluation / replacement tag.

P6:
decision uses epochs 0-7 only.

P7:
C1 / C2 / C3 exposure limits exact.

P8:
stale twin and canary start byte-identical.

P9:
REVOKE restores exact stale-twin state.

P10:
two complete primary sweeps byte-identical.

P11:
no patch deletion;
no C-v3;
no duplicate context;
major history remains [v1,v2];
slot count remains 3.

P12:
all 8 replicas per each of 48 patch contexts are present.

NEGATIVE / LIMIT CONTROLS

N1:
always-patch R1 establishes unconditional fresh-world harm rate.

N2:
future leakage invalidates experiment.

N3:
dropping stale twin invalidates causal decision evidence.

N4:
selecting the highest-service arm after results is prohibited.

N5:
changing 5% harm ceiling after results is prohibited.

N6:
new patch semantics are not tested here.

N7:
sequential interaction between decisions remains untested.

INTERPRETATION

A21 is confirmatory.

A20 asked:

can bounded real exposure look useful?

A21 asks:

does that signal survive
when the future trajectory is genuinely new?

If no arm qualifies,
the A20 signal is not robust enough
for sequential autonomous authority.

If an arm qualifies,
only the preregistered minimum-exposure selection rule
may nominate it for the next experiment.

Even then,
A21 does not authorize production use.

A later experiment must test sequential patch decisions
where one activation decision changes the state inherited by the next.

PLAIN-SPEAK QUESTION

A20 looked promising,
but it tested worlds we already knew a lot about.

A21 creates hundreds of fresh futures
after the experiment is frozen.

The cells do not get to see those futures early.

They try the patch on a few newborns,
watch eight real steps,
and decide whether to expand.

Then we reveal the second half.

If positive canary evidence still almost never leads to harm
across hundreds of fresh futures,
we have something much stronger than a lucky result.

And if more than one canary size works,
we deliberately choose the smallest one,
not the one with the prettiest score.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A21 OUT-OF-SAMPLE CANARY REPLICATION

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY REAL A21 TRAJECTORY.

IMPLEMENTATION COMMIT

ec883251552c80873697eb085eba5c90657ce3d2.

SOURCE BUNDLE

Loader:

research/applications/track-a/a21_t8e_out_of_sample_canary_replication_v1.py

Loader Git blob:

dddee328faaa1a96d625a58a9c43b205fc4dc289.

Payload:

research/applications/track-a/a21_t8e_out_of_sample_canary_replication_v1.py.gz

Payload Git blob:

520d5671ecd93a95918d34008c08809cde376b2b.

Decompressed source SHA-256:

7a9779ef291d828bc124eb6b8d00ee33e03bd7ea6122952ed0ae1b183b457f6d.

Decompressed source bytes:

15041.

Deterministic gzip SHA-256:

9ffae8743f395e1bc84cbb430fbe484fa51bc028edc0b5fe762171360ed54aba.

Compressed payload bytes:

4912.

FROZEN SUBSTRATE VALIDATION

Exact A17 replay:

3978 candidate first-four;
3950 stale first-four;
37 / 48 candidate >= stale;
38 migrations avoided.

Exact 11 A17 below-stale pairs:

MATCH.

MECHANICAL PRECHECK — NON-EVIDENCE

Fake freeze seed:

MECHANICAL-F21-NONPRIMARY.

Two complete sweeps:

BYTE-IDENTICAL.

Serialized file SHA-256:

3d2a5e089ee7f1052957f38f56242ba3f1ff28c752b20be8adb9cd5f0b7babde.

Serialized semantic output SHA-256:

14707104c8afb091d3fcf2d4de6d24b8855c6db83e3e90a8fb90791d35c0820f.

All P1-P12 mechanical probes:

PASS.

Fake-world unconditional R1 second-half harm rate:

0.140625.

No C1 / C2 / C3 arm met the preregistered replication qualification.

This mechanical result is NON-SCIENTIFIC.

It demonstrates that:

- the 5% harm ceiling is not trivially satisfied;
- the coverage floor is active;
- the minimum-exposure selection rule can legitimately select NONE.

PRE-FREEZE REPAIR

The first mechanical pass found one probe-only representation defect:

P4 indexed in-memory integer replacement-epoch keys
using JSON-style string keys.

The probe was corrected before implementation freeze.

No scientific rule,
trajectory rule,
threshold,
canary decision,
or result was changed.

REAL A21 STATUS

No real post-F21 trajectory has been derived.

No real replication manifest exists.

No real A21 canary outcome exists.

Let the resulting commit SHA be:

F21.

After F21 exists:

1. derive exactly 384 fresh trajectories from F21;
2. bind the complete manifest SHA in the repository;
3. only then run two complete primary sweeps;
4. require byte-identical output;
5. apply the frozen C1 -> C2 -> C3 minimum-exposure selection hierarchy.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-FREEZE PRIMARY MANIFEST — A21 OUT-OF-SAMPLE REPLICATION

DATE:
2026-09-21.

STATUS:
BOUND BEFORE FIRST REAL A21 CANARY OUTCOME.

F21:

f0467a9aaf92aab4b57e1b299c99ffa688164d99.

FROZEN SOURCE SHA-256:

7a9779ef291d828bc124eb6b8d00ee33e03bd7ea6122952ed0ae1b183b457f6d.

TRAJECTORY COUNT:

384.

STRUCTURE:

48 fixed A17 patch contexts
x
8 fresh F21-derived replicas per context.

COMPLETE MANIFEST SHA-256:

9f0dddac51009f46ea5ded21a86d77ea8487ab6af149da1209d1c6a6fa2bf070.

Serialized manifest-wrapper JSON SHA-256:

719f4feca1db36245b1a74fa3820b541b83a6eae2c58a9182a9b1515e2afeb55.

The complete manifest deterministically binds,
for all 384 trials:

- scenario;
- patch;
- replica;
- candidate target prior;
- stale prior;
- all 16 fresh evaluation demands;
- epoch-0 replacement target set;
- epoch-8 replacement target set;
- unique trajectory identity.

Every 16-demand sequence has exact mean equal to its frozen candidate target.

Every replacement set contains exactly four unique cell IDs.

All trajectory namespaces are:

YGG-A21-*

and are distinct from the original A17 evaluation / replacement namespaces.

PRIMARY STATUS AT MANIFEST BIND

A21 canary outcomes observed:

0.

A21 EXPAND / HOLD / REVOKE decisions observed:

0.

A21 selected arm:

NONE / NOT YET EVALUATED.

The next permitted operation is:

two complete deterministic A21 primary sweeps
over this exact manifest.

NO TRAJECTORY REDRAW.
NO THRESHOLD CHANGE.
NO ARM REORDERING.
NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-RUN CLOSURE — A21 / T8E OUT-OF-SAMPLE CANARY ACTIVATION REPLICATION

DATE:
2026-09-21.

STATUS:
CLOSED / CONFIRMATORY REPLICATION FAILED /
NO CANARY ARM QUALIFIED /
NO SEQUENTIAL CONTROLLER AUTHORIZED /
NON-CANONICAL.

FROZEN IMPLEMENTATION

Implementation commit:

ec883251552c80873697eb085eba5c90657ce3d2.

F21:

f0467a9aaf92aab4b57e1b299c99ffa688164d99.

Source SHA-256:

7a9779ef291d828bc124eb6b8d00ee33e03bd7ea6122952ed0ae1b183b457f6d.

BOUND PRIMARY MANIFEST

Manifest-bound commit:

07259c714616c78d43167994b5edcfdb0115b331.

384-trajectory manifest SHA-256:

9f0dddac51009f46ea5ded21a86d77ea8487ab6af149da1209d1c6a6fa2bf070.

Manifest-wrapper serialized SHA-256:

719f4feca1db36245b1a74fa3820b541b83a6eae2c58a9182a9b1515e2afeb55.

PRIMARY REPRODUCIBILITY

Two complete real F21-derived primary sweeps were byte-identical.

Serialized result-file SHA-256:

f5f42006a681af49d9c7c433aea477925f83c7a8ce87b77b24afaf4b51f68b70.

Serialized semantic output SHA-256:

dca6a819bc3d2669d2fc915202113ac4ed5c3a144f30d0bdcf462234cf8b2ae0.

All P1-P12 integrity probes:

PASS.

A17 replay remained exact:

3978 / 3950 / 37-of-48 / 38.

FRESH-WORLD BASELINE

Fresh R1 all-candidate second-half harmful trajectories:

48 / 384.

Unconditional R1 second-half harm rate:

0.125.

Thus the fresh post-F21 worlds contain substantial nontrivial activation risk.

C1 — 25% UNPROVEN EXPOSURE

EXPAND:

14.

HOLD:

364.

REVOKE:

6.

Actual second-half EXPAND outcomes:

beneficial = 6;
neutral = 5;
harmful = 3.

Actual EXPAND harm rate:

0.2142857143.

Full-candidate second-half labels among EXPAND:

beneficial = 5;
neutral = 6;
harmful = 3.

Full-label EXPAND harm rate:

0.2142857143.

Canary evidence-phase aggregate delta:

+15.

Second-half aggregate delta versus stale twins:

+17.

Complete service delta versus R0 all-stale:

+32.

Complete service delta versus R1 all-candidate:

-320.

Coverage floor:

FAIL.

Harm ceiling:

FAIL.

C1 REPLICATION-QUALIFIED:

FALSE.

C2 — 50% UNPROVEN EXPOSURE

EXPAND:

35.

HOLD:

317.

REVOKE:

32.

Actual second-half EXPAND outcomes:

beneficial = 10;
neutral = 17;
harmful = 8.

Actual EXPAND harm rate:

0.2285714286.

Full-candidate second-half labels among EXPAND:

beneficial = 9;
neutral = 19;
harmful = 7.

Full-label EXPAND harm rate:

0.20.

Canary evidence-phase aggregate delta:

-11.

Second-half aggregate delta versus stale twins:

+23.

Complete service delta versus R0:

+12.

Complete service delta versus R1:

-340.

Coverage floor:

FAIL.

Harm ceiling:

FAIL.

C2 REPLICATION-QUALIFIED:

FALSE.

C3 — 75% UNPROVEN EXPOSURE

EXPAND:

85.

HOLD:

221.

REVOKE:

78.

Actual second-half EXPAND outcomes:

beneficial = 36;
neutral = 38;
harmful = 11.

Actual EXPAND harm rate:

0.1294117647.

Full-candidate second-half labels among EXPAND:

beneficial = 35;
neutral = 38;
harmful = 12.

Full-label EXPAND harm rate:

0.1411764706.

Canary evidence-phase aggregate delta:

+13.

Second-half aggregate delta versus stale twins:

+67.

Complete service delta versus R0:

+80.

Complete service delta versus R1:

-272.

Coverage floor:

PASS.

Harm ceiling:

FAIL.

Relative-harm requirement:

FAIL.

C3 REPLICATION-QUALIFIED:

FALSE.

MINIMUM-EXPOSURE SELECTION

C1:
not qualified.

C2:
not qualified.

C3:
not qualified.

Selected arm:

NONE.

A21_OUT_OF_SAMPLE_CANARY_REPLICATION_SUCCESS:

FALSE.

DIAGNOSTIC DISTRIBUTION

The failure is not isolated to one trajectory replica.

For C3,
harmful EXPAND labels occurred across all eight replica indices.

The failure is not isolated to one patch context.

Multiple scenarios and patch positions contributed harmful expansions.

Positive evidence magnitude alone is not a reliable repair.

For C3:

evidence delta +1:
58 expansions;
9 full-label harmful.

delta +2:
16 expansions;
2 harmful.

delta +3:
4 expansions;
0 harmful.

delta +4:
5 expansions;
1 harmful.

delta +5:
1 expansion;
0 harmful.

delta +8:
1 expansion;
0 harmful.

For C2,
even one delta +4 expansion was harmful.

Therefore a simple:

"require a larger positive margin"

is not justified by A21.

TECHNICAL INTERPRETATION

A20's one-sided positive signal
was a real property of the known A17 worlds,
but it did not generalize to fresh trajectory variation.

A21 falsifies the stronger claim:

ONE POSITIVE 8-EPOCH CANARY WINDOW
IS SUFFICIENT TO EARN SAFE EXPANSION AUTHORITY.

Even under:

fresh post-freeze trajectories;
exact stale twins;
bounded exposure;
exact state restoration;
no future leakage;
deterministic replay;

the sign of one observed canary window
can reverse in the next independent window.

The problem is therefore temporal,
not merely geometric.

The organism is seeing:

REAL CONSEQUENCE,

but still only one finite slice
of a variable future.

A positive first window
does not prove that the underlying patch effect is persistent.

PLAIN-SPEAK INTERPRETATION

A20 looked like a breakthrough:

when the small live trial won,
expanding it never hurt us.

A21 gave that idea hundreds of futures
we had never seen before.

It did not hold up.

Sometimes the canary really did better
for the first eight steps,
we expanded the patch,
and the next eight steps were worse.

That happened too often
for any canary size to pass our safety rule.

The important lesson is not:

"canaries do not work."

The lesson is:

ONE GOOD CANARY WINDOW IS NOT ENOUGH.

The trial gave us real information,
but the environment can fluctuate enough
that one good stretch can still be misleading.

Making the first win bigger
does not obviously solve it either.

We saw harmful cases
even after larger positive margins.

So the next sensible move is hysteresis again:

do not grant full authority
because the patch won once.

Require it to prove itself
across more than one independent real window.

A likely next experiment is:

CANARY WINDOW 1
->
still provisional

CANARY WINDOW 2
->
if positive again, earn expansion

then:

WINDOW 3
->
untouched confirmation.

This combines what A16 taught us about sustained drift
with what A20-A21 taught us about bounded live experimentation.

A17 remains closed mixed / negative.

A18 explanatory.

A19 shadow authority failed.

A20 discovery positive but unconfirmed.

A21 confirmatory replication failed.

No canary arm is authorized for sequential autonomous control.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
