TITLE: LU-2P LU2PF1 PRIMARY CLOSURE
DATE: 2026-09-24
STATUS: CLOSED / CONTIGUOUS-LESION ROBUSTNESS QUALIFIED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
b1a02b436c223d75ceca40b00d0af852e52d128f

MECHANICAL GATE:
36b981849c92470098ba1d2b71d5fd6794cae197

LU2PF1:
6cf5ac96c4357fa3d065f2076ee64fe401e542e9

TEN-MANIFEST BINDING:
665a44f7f23679b6aff18770ae4d02d369434635

BOUND PRIMARY RUN:
36058520738

BOUND PRIMARY HEAD:
5c24d3806efe39898a756437a6da295577e11d49

BOUND PRIMARY ARTIFACT:
10833153255

DUPLICATE PRIMARY SWEEPS

bytes each:
243510

SHA256 both:
11f3d7372827a903f741a399ea9e73179168df5a688149ae2968671230dd24b4

byte-identical:
TRUE

EXACT-ARTIFACT QUALIFICATION

run:
36058683115

head:
fea4121d1c796f5eb72b2fd639542d3ebb61a96e

qualification artifact:
10834175042

SCIENTIFIC STATUS

LU2P_CONTIGUOUS_LESION_ROBUSTNESS:
TRUE

baseline-feasible U_A0 worlds:
9 / 10

required:
>= 8 / 10

evidence coverage:
PASS

causal learned-U participation:
TRUE

H teacher preserved:
TRUE

median paired completion-area ratio:
1.0

CAUSAL TOTALS ACROSS BASELINE-FEASIBLE WORLDS

U evaluations:
10437

U evaluations with nonzero teacher-vs-A25 TV:
10437

realized learned-U transition differences:
50

H learned probability differences:
0

H realized learned-controlled differences:
0

PAIRWISE PRESERVATION

All nine baseline-feasible paired worlds passed every preregistered gate.

Every feasible pair passed:

completion area >= 90 percent of U_A0;
final-16 backlog area <= 125 percent U_A0;
final backlog <= 125 percent U_A0;
operations per correct completion <= 125 percent U_A0;
phase/stream noncollapse;
anchor recovery finite and <= U_A0 + 8;
demand recovery finite and <= U_A0 + 8;
contiguous-lesion paired recovery criterion;
incorrect DONE = 0;
maturity-conditioned repair integrity;
matching integrity.

All nine completion-area ratios:
1.0

DESCRIPTIVE TOTALS

U_A0 correct DONE:
1462

U_A25 correct DONE:
1462

U_A0 incorrect DONE:
0

U_A25 incorrect DONE:
0

U_A0 expired:
0

U_A25 expired:
0

valid terminal in-flight detections:
U_A0 = 2
U_A25 = 2

state-divergence epochs:
758

first divergence epochs:
0, 17, 17, 9, 10, 9, 28, 4, 5, 7

TERMINAL IN-FLIGHT EVIDENCE

Both legitimate terminal in-flight cases occurred in replicate 3 and were
identical in U_A0 and U_A25.

detection at epoch 158:
repair completed at 159;
terminal state AT_EGRESS;
reverification first physically possible at 160.

detection at epoch 159:
terminal state REPAIR_PENDING;
repair first physically possible at 160.

Both pass the preregistered mechanics-derived maturity contract.

BASELINE-EXCLUDED REPLICATE

replicate 10 was excluded by the exact-parent baseline rule.

One scheduled corrupted request:

rid 430;
arrival epoch 143;
reached AT_EGRESS by the horizon;
was not yet verified/detected by epoch 159;
terminal state AT_EGRESS;
no expiry;
no incorrect DONE.

The maturity contract does not excuse an undetected corruption that has
already reached egress.

Therefore replicate 10 correctly remains baseline-infeasible.

Coverage remains 9/10 and passes the preregistered requirement.

INTERPRETATION

The apparent LU-2N contiguous-lesion repair failure was an evaluation-horizon
artifact for the three diagnosed final-epoch detections.

On ten new worlds with the same organism dynamics and the preregistered
mechanics-derived maturity contract, bounded learned U recruitment qualifies
under the 16-cell contiguous lesion.

The learner still controls only 25 percent of U recruitment probability.

It still receives no lesion flag, task program, stage, phase, global queue,
or future information.

It caused 50 real U transition differences while preserving every required
functional comparison in every fair pair.

This supports robustness of the transferred learned recruitment behavior to
both distributed and spatially concentrated 25-percent damage.

BOUNDARY

Do not increase alpha.

Do not give learned authority to C/S.

Do not add online adaptation or recursive self-modification.

NEXT SCIENTIFIC QUESTION

Increase task distance while returning perturbation to a validated baseline.

The smallest clean next step is a three-stage compositional transform task
under exact-parent U authority first.

Validate that environment before reintroducing U_A25.

PLAIN-SPEAK INTERPRETATION

This one worked.

The concentrated sixteen-cell injury was not breaking the neural recruiter.

Once the scorecard stopped demanding impossible post-horizon repair steps,
the learned recruiter changed real developmental decisions and still kept
pace with the hand-written parent in every fair comparison.

No wrong answers.
No expirations.
No recovery loss.
No repair shortcut.
No extra authority.

We have now pushed the same bounded learned behavior through:

a different two-step task;
larger distributed damage;
and equally large concentrated damage.

The next useful test is a genuinely deeper job, not more neural control.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
