TITLE: YGGDRASIL A18 / T8B — Local Turnover Geometry and Horizon Attribution
DATE: 2026-09-21
STATUS: PREREGISTERED EXPLANATORY DIAGNOSTIC / NON-ACCEPTING / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8B / APPLICATION-A
PARENT: A17 T8 Bounded Incremental Developmental Patch Tracking
BRANCH: dg1a-ar

PURPOSE

A17 demonstrated that the bounded patch mechanism can:

- learn 48 / 48 one-unit patch targets;
- bind provenance and parent ancestry;
- preserve the immutable A15 C-v2 checkpoint;
- restart equivalently;
- roll backward and forward exactly;
- stop at four patches;
- preserve major history [v1,v2];
- preserve three context slots.

But A17 failed one preregistered usefulness-consistency requirement:

candidate >= stale-previous in at least 40 / 48 patch evaluations.

Observed:

37 / 48.

The candidate still:

beat stale in aggregate;
matched the target-policy evaluator oracle;
and avoided migrations.

A18 asks why a target-correct patch can temporarily underperform
the immediately previous developmental prior.

A18 is explanatory only.

It does NOT reopen A17 acceptance.
It cannot change the A17 threshold.
It cannot discard unfavorable scenarios.
It cannot redraw A17 paths.
It cannot create a new accepted frontier claim by itself.

FROZEN A17 INPUT

Original A17 scientific seed F17:

3ec24f8242285688a537f5e7dd6e9a231a645597.

Corrected executable freeze F17A:

c33df49a8b171c1f6cd8e64820dd3bca0e2f4492.

A17 primary manifest SHA-256:

8284e3f1e47a17f234eb02f2b427cddaee16999e0df795d38f1b0b457cf8e43f.

A17 authoritative corrected primary result SHA-256:

ee53b151295a5d31ba1e54e4cd8d4deae0aff604ff3b66406fb87b748a08306d.

A17 authoritative closure:

d225ab1a8168660afb0c0c6547c3c67594428e3d.

A17 disposition ledger:

7abf44d9d83e7b49422e35fe68c348087e0c117c.

A18 must replay exactly the same:

12 scenarios;
four patch paths per scenario;
16 evaluation demands per patch;
replacement episodes at epochs 0 and 8;
four replaced cells per episode;
candidate target prior;
stale-previous prior;
initial cell state and sequential scenario state.

No A18 diagnostic may alter those A17 facts.

PRIMARY DIAGNOSTIC QUESTION

For each of the 48 A17 patch evaluations,
especially but not only the 11 cases where candidate < stale,
determine whether the deficit is explained by one or more of:

D1 — SHORT-HORIZON EFFECT

The first-four score may reward a transient local arrangement
that does not reflect the full 16-epoch evaluation.

Measure candidate minus stale service at:

each replacement episode's first 1 epoch;
first 2 epochs;
first 4 epochs;
all 8 epochs before the next boundary/end;

and over the complete 16-epoch patch evaluation.

Classify an A17 loss as horizon-limited if:

candidate < stale on the frozen first-four metric
but candidate >= stale over the complete 16-epoch evaluation.

No alternative horizon becomes an A17 acceptance metric.

D2 — REPLACEMENT-GEOMETRY SENSITIVITY

For each patch and each replacement episode,
enumerate every possible four-cell replacement target set:

C(12,4) = 495.

Use the exact pre-episode candidate and stale cell states
that arise from replaying the frozen A17 evaluation up to that boundary.

For each of the 495 common target sets:

apply the candidate target prior to candidate replacement births;
apply the stale-previous prior to stale replacement births;
score the next four frozen demand epochs with the same migration rule.

Record:

candidate-minus-stale distribution;
fraction of geometries candidate >= stale;
canonical A17 geometry percentile/rank within that distribution;
best and worst observed geometry delta.

This is diagnostic only.
No replacement target is substituted into A17.

D3 — EXISTING-CELL INERTIA UPPER BOUND

At each replacement episode,
construct a diagnostic counterfactual population
whose 12 roles exactly equal the candidate target prior
before scoring the same next four frozen demands.

This is a non-candidate upper-bound diagnostic.
It is not an allowed production update rule.

Compare:

birth-only candidate;
stale birth-only baseline;
instant target-aligned population.

If target alignment removes a canonical deficit,
record that the loss is consistent with inherited cell-state inertia /
partial-turnover lag.

D4 — LOCAL-BIRTH-PRIOR OBJECTIVE MISMATCH

At each canonical replacement episode,
hold fixed:

the exact pre-episode cell state;
the exact canonical four-cell replacement target set;
the next four frozen demand epochs;
the migration rule.

Evaluate every prior in the frozen 124-prior catalog
as the birth-role prior for those four replacements.

Record:

maximum achievable first-four service;
all priors tied for maximum;
candidate target-prior rank;
stale-previous rank;
whether stale is locally optimal or closer to the local optimum
than the target prior.

This diagnostic distinguishes:

"the patch target is wrong"

from

"the patch target is correct for the 16-epoch mean,
but the first-four local demand realization temporarily favors another birth allocation."

No locally optimal diagnostic prior may become a candidate policy inside A18.

D5 — FAILURE ATTRIBUTION

For all 48 patch evaluations,
report the overlap of:

horizon-limited;
geometry-sensitive;
inertia-sensitive;
local-objective-mismatch.

Do not force each loss into exactly one category.

A loss may have multiple causes.

A18 must report the complete 48-evaluation table,
not only the 11 A17 losses.

PRE-REGISTERED INTERPRETATION RULES

A18 is evidence-generating, not pass/fail.

Strong evidence for scoring-window mismatch exists if
most A17 first-four losses disappear by full-16 scoring.

Strong evidence for replacement geometry exists if
the canonical four-cell target set falls in the unfavorable tail
of the 495-set candidate-minus-stale distribution
for multiple A17 losses.

Strong evidence for inherited-state inertia exists if
instant target alignment removes deficits
that remain under birth-only patching.

Strong evidence for local-objective mismatch exists if
the candidate target prior is not first-four optimal
while another frozen-catalog prior is,
especially when stale-previous is tied with or nearer that local optimum.

These are descriptive interpretations.
No post-result threshold will convert them into an acceptance claim.

NEGATIVE CONTROLS / SANITY CHECKS

N1 — A17 replay must reproduce exactly:

candidate first-four = 3978;
stale first-four = 3950;
oracle first-four = 3978;
candidate >= stale = 37 / 48;
migrations avoided = 38.

If not,
A18 is invalid.

N2 — the exact 11 A17 below-stale scenario/patch pairs must reproduce.

N3 — every geometry enumeration must contain exactly 495 unique four-cell sets.

N4 — candidate and stale geometry comparisons use the same replacement target set in each counterfactual.

N5 — local-prior sweep must use exactly the frozen 124-prior catalog.

N6 — no A17 path, demand, replacement schedule, patch target, or threshold is mutated.

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No production deployment.
No CKB / KTRADE integration.
No financial task.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

PLAIN-SPEAK PREREGISTERED QUESTION

A17's patches were correct.

They were reversible.
They kept their ancestry.
They matched the target-policy oracle overall.

But eleven times,
the old prior briefly did better right after four cells were replaced.

A18 asks:

Was the patch actually bad?

Or did four other things make a good patch look bad for a few moments?

1. We may be judging too soon.
2. We may have happened to replace an awkward set of four cells.
3. Most of the old cells may still carry the old developmental arrangement.
4. The long-run target may be right,
   while the next four demand samples temporarily favor a different birth mix.

We will replay the exact same A17 worlds
and separate those effects.

A18 does not change A17's result.

It tells us what experiment should come next.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — A18 / T8B LOCAL TURNOVER GEOMETRY AND HORIZON ATTRIBUTION

DATE:
2026-09-21.

STATUS:
CLOSED / EXPLANATORY DIAGNOSTIC COMPLETE /
A17 RESULT UNCHANGED /
NON-ACCEPTING /
NON-CANONICAL.

EXECUTION INTEGRITY

Before interpreting A18,
the independent reconstruction reproduced the frozen lineage exactly:

A11 manifest SHA-256:

b0e00f29d36637a1365ab2407678aacf232ac4f4cf05d387f68af975a5b4bedd.

A12 manifest SHA-256:

502009818ea9d6e57089a91424e7cf399e7c5e95024a9623816e733c58c3f63a.

A14 exact-F14 manifest SHA-256:

83a0ad4d67d7a3f3625e49c311f5d2a85c73fee40cde96e24937ae79e1e944ae.

The exact F17 replay reproduced A17:

candidate first-four = 3978;
stale first-four = 3950;
target-policy reference = 3978;
candidate >= stale = 37 / 48;
migrations avoided = 38.

The exact 11 A17 below-stale scenario / patch pairs reproduced:

S00/P1;
S00/P2;
S00/P3;
S02/P4;
S04/P1;
S04/P2;
S04/P3;
S10/P2;
S10/P4;
S11/P1;
S11/P4.

N1 and N2:

PASS.

Every geometry enumeration contained:

495

unique four-cell target sets.

The same target set and deterministic A17 replacement-order rule
were used for candidate and stale in every geometry counterfactual.

The local-prior sweep used exactly:

124

frozen catalog priors.

No A17 path,
demand,
replacement schedule,
patch target,
threshold,
or result
was mutated.

D1 — SHORT-HORIZON EFFECT

A17 first-four losses that became candidate >= stale
over the complete 16-epoch evaluation:

0 / 11.

Thus:

NO A17 LOSS WAS HORIZON-LIMITED.

Across all 48 evaluations,
full-16 service was:

candidate = 7929;
stale = 7906;
aggregate delta = +23.

Candidate >= stale over full 16 epochs:

35 / 48.

Breakdown:

candidate > stale = 24 / 48;
candidate == stale = 11 / 48;
candidate < stale = 13 / 48.

The longer horizon therefore did not repair A17's local-consistency problem.
It slightly reduced the count of non-inferior evaluations
from the A17 first-four result:

37 / 48
to
35 / 48.

INTERPRETATION

The A17 miss is not primarily an artifact of judging the patch too early.

D2 — REPLACEMENT-GEOMETRY SENSITIVITY

Across the 96 replacement episodes,
15 canonical episodes had:

candidate first-four < stale.

For each of those episodes,
all 495 four-cell replacement sets were enumerated.

In:

6 / 15

negative episodes,
more than half of all possible replacement geometries
would have produced:

candidate >= stale.

These geometry-sensitive negative episodes contributed to:

4 / 11

A17 losing patch evaluations.

Strong examples:

S10/P2 episode 0:

canonical delta = -2;
candidate >= stale in 93.5% of all replacement geometries;
canonical geometry percentile = 4.0%.

S10/P4 episode 0:

canonical delta = -2;
candidate >= stale in 96.8% of geometries;
canonical percentile = 2.8%.

S04/P1 episode 8:

canonical delta = -1;
candidate >= stale in 94.5% of geometries;
canonical percentile = 5.5%.

S11/P4 episode 8:

canonical delta = -1;
candidate >= stale in 80.4% of geometries;
canonical percentile = 19.6%.

Thus some A17 losses were genuine bad-luck interactions
between a correct patch and which four cells happened to turn over.

But geometry is not the whole explanation.

Geometry-independent / nearly geometry-independent examples:

S00/P2 episode 0:

candidate < stale for 100% of 495 geometries.

S00/P3 episode 0:

candidate < stale for 100% of 495 geometries.

S02/P4 episode 0:

candidate < stale for 100% of 495 geometries.

S04/P3 episode 0:

candidate >= stale in only 3.0% of geometries.

Therefore several losses remain even after replacement geometry is exhaustively varied.

D3 — EXISTING-CELL INERTIA UPPER BOUND

For each negative canonical episode,
A18 constructed a diagnostic population
whose 12 roles exactly matched the learned target prior
before scoring the next four demands.

This is an upper-bound diagnostic only.

Target-aligned state removed or equaled the stale deficit in:

7 / 15

negative episodes.

Those episodes occurred in:

4 / 11

A17 losing patch evaluations:

S04/P1;
S10/P2;
S10/P4;
S11/P1.

Examples:

S10/P4 episode 0:

birth-only candidate service = 38;
stale = 40;
instant target-aligned diagnostic = 41.

S11/P1 episode 0:

birth-only candidate = 39;
stale = 42;
instant target-aligned = 43.

S04/P1 episode 0:

birth-only candidate = 40;
stale = 41;
instant target-aligned = 42.

Thus inherited cell state / partial-turnover lag
can materially suppress the immediate benefit of a newly correct patch.

But inertia also does not explain every loss.

D4 — LOCAL-BIRTH-PRIOR OBJECTIVE MISMATCH

This was the strongest result.

For each canonical replacement episode,
A18 held fixed:

the actual patched-organism pre-episode state;
the canonical four-cell replacement order;
the next four frozen demands;
the migration rule.

It then evaluated all:

124

catalog priors as the birth-role prior.

Negative canonical episodes:

15.

In all:

15 / 15

the learned A17 target prior was NOT the locally service-optimal birth prior.

All:

11 / 11

A17 losing patch evaluations contained at least one such locally mismatched episode.

In:

13 / 15

negative episodes,
the stale-previous prior itself ranked first
for the local four-epoch service objective
when evaluated from the patched organism's state.

Examples:

S00/P2 episode 0:

target rank = 2;
stale rank = 1.

S00/P3 episode 0:

target rank = 2;
stale rank = 1.

S02/P4 episode 0:

target rank = 2;
stale rank = 1.

S04/P1 episode 0:

target rank = 40;
stale rank = 1.

S10/P2 episode 0:

target rank = 17;
stale rank = 1.

S11/P1 episode 0:

target rank = 63;
stale rank = 1.

S10/P4 episode 0:

target rank = 92;
stale rank = 8.

This exposes a critical semantic distinction.

A17's learned patch target is correct as the exact mean developmental prior
for the 16-epoch frozen niche.

But:

CORRECT DEVELOPMENTAL TARGET

does not imply:

SERVICE-OPTIMAL IMMEDIATE BIRTH PRIOR

under:

partial turnover;
current embodied cell state;
deterministic migration;
and a particular near-term demand realization.

A17's object named:

oracle

was therefore a:

TARGET-POLICY REFERENCE,

not a service-maximizing oracle.

The candidate matched that target-policy reference by construction.

The A18 catalog sweep proves that other priors can produce
higher local service
even while the learned target itself is statistically correct.

D5 — ATTRIBUTION OF THE 11 A17 LOSSES

Horizon-limited:

0 / 11.

Geometry-sensitive
using the preregistered descriptive criterion
that a canonical negative episode occurs while
a majority of the 495 replacement geometries are non-inferior:

4 / 11.

Inertia-sensitive
where instant target alignment removes / equals
the stale deficit in at least one negative episode:

4 / 11.

Local-objective mismatch:

11 / 11.

These mechanisms overlap.

The dominant explanation is:

LOCAL CONTROL OBJECTIVE MISMATCH.

Replacement geometry and inherited state
amplify that mismatch in a meaningful subset of cases.

COMPLETE 48-EVALUATION TABLE

Legend:

Δfirst4 =
A17 candidate minus stale summed across the two four-epoch post-replacement windows.

Δfull16 =
candidate minus stale over the complete 16-epoch evaluation.

For E0 / E8:

Δ =
canonical four-epoch candidate minus stale.

geom>= =
fraction of all 495 replacement geometries with candidate >= stale.

pct =
canonical delta percentile in the 495-geometry distribution,
where a low value means an unusually unfavorable geometry.

T-rank =
learned target prior rank among all 124 birth priors
for the local four-epoch service objective.

S-rank =
stale-previous prior rank.

align-cand =
instant target-aligned diagnostic service
minus birth-only candidate service.

S/P | Δfirst4 | Δfull16 | E0 Δ / geom>= / pct / T-rank / S-rank / align-cand | E8 Δ / geom>= / pct / T-rank / S-rank / align-cand
S00/P1 | -1 | -2 | +0 / 0.913 / 0.406 / 35 / 35 / +4 | -1 / 0.451 / 0.549 / 6 / 1 / +0
S00/P2 | -1 | -1 | -1 / 0.000 / 1.000 / 2 / 1 / +0 | +0 / 0.929 / 0.648 / 1 / 1 / +0
S00/P3 | -1 | -1 | -1 / 0.000 / 1.000 / 2 / 1 / +0 | +0 / 0.889 / 1.000 / 1 / 1 / +0
S00/P4 | +1 | +1 | +1 / 1.000 / 1.000 / 1 / 8 / -1 | +0 / 0.970 / 0.952 / 2 / 2 / +0
S01/P1 | +1 | +1 | +0 / 1.000 / 0.263 / 3 / 3 / +0 | +1 / 0.990 / 0.576 / 1 / 7 / +0
S01/P2 | +1 | +1 | +1 / 1.000 / 0.519 / 2 / 19 / +0 | +0 / 0.980 / 1.000 / 1 / 1 / +0
S01/P3 | +1 | +0 | +0 / 1.000 / 0.970 / 2 / 2 / +0 | +1 / 1.000 / 0.958 / 2 / 26 / +0
S01/P4 | +0 | -1 | +0 / 0.960 / 1.000 / 4 / 4 / +0 | +0 / 0.998 / 0.929 / 13 / 13 / +0
S02/P1 | +0 | +0 | +0 / 0.632 / 0.976 / 1 / 1 / +0 | +0 / 0.661 / 0.885 / 1 / 1 / -1
S02/P2 | +0 | +0 | +0 / 0.653 / 0.727 / 7 / 7 / +2 | +0 / 0.927 / 0.968 / 1 / 1 / +0
S02/P3 | +2 | +2 | +0 / 0.594 / 1.000 / 1 / 1 / -1 | +2 / 1.000 / 1.000 / 2 / 64 / +0
S02/P4 | -1 | -2 | -1 / 0.000 / 1.000 / 2 / 1 / +0 | +0 / 0.986 / 0.919 / 1 / 1 / +0
S03/P1 | +1 | +1 | +1 / 0.891 / 0.701 / 1 / 9 / +0 | +0 / 1.000 / 0.646 / 1 / 24 / -1
S03/P2 | +1 | +1 | +0 / 0.578 / 0.972 / 2 / 2 / +0 | +1 / 1.000 / 0.529 / 1 / 4 / +0
S03/P3 | +1 | +1 | +0 / 1.000 / 0.657 / 3 / 3 / +0 | +1 / 1.000 / 0.501 / 3 / 14 / +0
S03/P4 | +0 | +1 | -1 / 0.291 / 0.709 / 2 / 1 / -1 | +1 / 0.711 / 0.594 / 1 / 21 / +0
S04/P1 | -2 | -3 | -1 / 0.655 / 0.345 / 40 / 1 / +2 | -1 / 0.945 / 0.055 / 94 / 104 / +2
S04/P2 | -1 | -2 | +0 / 1.000 / 0.939 / 3 / 3 / +0 | -1 / 0.255 / 0.745 / 6 / 1 / +0
S04/P3 | -1 | -1 | -1 / 0.030 / 0.970 / 4 / 1 / +0 | +0 / 1.000 / 0.580 / 4 / 4 / +0
S04/P4 | +0 | +0 | +0 / 0.869 / 0.929 / 15 / 15 / +0 | +0 / 0.711 / 0.988 / 1 / 1 / +0
S05/P1 | +4 | +3 | +2 / 0.960 / 0.749 / 1 / 28 / +0 | +2 / 1.000 / 1.000 / 1 / 18 / +0
S05/P2 | +2 | +1 | +1 / 1.000 / 0.834 / 3 / 36 / +0 | +1 / 0.990 / 1.000 / 3 / 3 / +0
S05/P3 | +2 | +3 | +0 / 0.998 / 0.580 / 4 / 4 / +0 | +2 / 0.994 / 1.000 / 4 / 76 / +0
S05/P4 | +0 | +0 | -1 / 0.246 / 0.754 / 3 / 1 / +1 | +1 / 1.000 / 0.998 / 3 / 3 / +0
S06/P1 | +3 | +3 | +3 / 0.970 / 0.994 / 1 / 42 / +1 | +0 / 1.000 / 0.578 / 9 / 9 / +0
S06/P2 | +0 | +0 | +0 / 1.000 / 0.798 / 2 / 2 / +0 | +0 / 0.859 / 0.741 / 5 / 60 / +0
S06/P3 | +2 | +2 | +2 / 0.978 / 1.000 / 1 / 12 / +0 | +0 / 0.515 / 0.980 / 1 / 1 / +0
S06/P4 | +3 | +4 | +1 / 1.000 / 1.000 / 6 / 66 / +0 | +2 / 1.000 / 1.000 / 11 / 69 / +0
S07/P1 | +1 | +1 | +0 / 0.828 / 0.798 / 1 / 1 / +0 | +1 / 1.000 / 0.899 / 1 / 8 / +0
S07/P2 | +1 | +1 | +0 / 1.000 / 1.000 / 2 / 2 / +0 | +1 / 0.994 / 0.966 / 5 / 55 / -1
S07/P3 | +0 | +0 | +0 / 1.000 / 1.000 / 2 / 2 / +0 | +0 / 0.966 / 0.978 / 1 / 1 / +0
S07/P4 | +2 | +3 | +0 / 0.972 / 0.477 / 2 / 2 / +1 | +2 / 1.000 / 0.867 / 1 / 16 / +0
S08/P1 | +0 | +0 | +0 / 1.000 / 1.000 / 1 / 1 / +1 | +0 / 1.000 / 0.855 / 4 / 4 / +0
S08/P2 | +0 | +0 | +0 / 0.578 / 0.972 / 6 / 6 / +0 | +0 / 1.000 / 0.552 / 6 / 6 / +0
S08/P3 | +3 | +3 | +3 / 0.929 / 1.000 / 1 / 90 / +0 | +0 / 0.980 / 0.465 / 10 / 10 / +0
S08/P4 | +2 | +2 | +1 / 0.994 / 0.954 / 4 / 39 / -1 | +1 / 1.000 / 0.756 / 3 / 29 / +0
S09/P1 | +0 | +1 | +0 / 0.913 / 0.768 / 3 / 3 / -1 | +0 / 1.000 / 0.745 / 1 / 25 / +0
S09/P2 | +1 | +1 | +0 / 0.663 / 0.830 / 5 / 5 / +0 | +1 / 1.000 / 0.869 / 11 / 30 / +0
S09/P3 | +0 | +0 | +0 / 0.968 / 1.000 / 7 / 7 / +0 | +0 / 0.972 / 0.507 / 1 / 1 / +0
S09/P4 | +1 | +1 | +0 / 0.972 / 0.762 / 4 / 4 / +0 | +1 / 1.000 / 1.000 / 6 / 38 / +0
S10/P1 | +3 | +5 | +0 / 0.691 / 0.970 / 1 / 1 / +0 | +3 / 1.000 / 0.988 / 2 / 72 / +0
S10/P2 | -1 | -2 | -2 / 0.935 / 0.040 / 17 / 1 / +2 | +1 / 0.927 / 1.000 / 2 / 17 / +0
S10/P3 | +0 | +0 | -2 / 0.992 / 0.002 / 66 / 1 / +2 | +2 / 1.000 / 1.000 / 2 / 2 / -1
S10/P4 | -1 | -3 | -2 / 0.968 / 0.028 / 92 / 8 / +3 | +1 / 0.980 / 0.794 / 1 / 19 / +0
S11/P1 | -3 | -3 | -3 / 0.418 / 0.228 / 63 / 1 / +4 | +0 / 0.796 / 0.931 / 1 / 1 / +0
S11/P2 | +0 | -1 | +0 / 0.737 / 1.000 / 7 / 7 / +0 | +0 / 1.000 / 1.000 / 3 / 3 / +0
S11/P3 | +3 | +3 | +0 / 1.000 / 1.000 / 3 / 3 / +0 | +3 / 0.966 / 1.000 / 1 / 22 / +0
S11/P4 | -1 | -1 | +0 / 1.000 / 0.970 / 1 / 1 / +0 | -1 / 0.804 / 0.196 / 5 / 1 / +0

TECHNICAL INTERPRETATION

A18 falsifies the simplest explanation:

"the A17 threshold failed only because first-four service is too short."

The deficits survive the complete evaluation horizon.

A18 also shows that replacement geometry
and inherited-state inertia matter substantially,
but only for a subset of failures.

The universal feature of the negative episodes is instead:

the learned developmental mean
is not always the control action that maximizes immediate service
when only four cells are being reborn into an already-structured population.

This means Yggdrasil currently has two concepts
that A17 treated as if they were the same:

ESTIMATED DEVELOPMENTAL TARGET

and

SAFE / USEFUL NEXT ACTUATION.

They are not equivalent.

A patch can be statistically correct
while immediate activation of that patch is locally disadvantageous.

That is exactly the kind of distinction
a self-evaluating developmental architecture must learn to represent.

PLAIN-SPEAK INTERPRETATION

We found the reason A17 missed.

It was not mainly because we judged the patch too quickly.

The old policy still beat the new patch
even when we watched the whole test window.

Sometimes we were simply unlucky
about which four cells died and were replaced.

Sometimes too many old-state cells were still hanging around,
so the new patch could not express itself cleanly yet.

But the biggest issue was deeper.

Yggdrasil learned the right long-term developmental target.

Then it immediately used that target as the instruction for newborn cells.

Those are two different jobs.

A target can correctly say:

"this environment averages out to this role balance"

while the next few moments say:

"given the cells I already have alive,
putting the newborns directly toward that average is not the best move yet."

In every one of the bad local episodes,
some other birth allocation served the immediate situation better.

In 13 of the 15 bad replacement episodes,
the old prior was actually the locally best choice
from the patched organism's current state.

So the missing capability is becoming clearer:

Yggdrasil should not automatically equate

"I learned a valid patch"

with

"I should activate that patch right now."

The next justified experiment should separate:

PATCH LEARNING

from

PATCH ACTIVATION.

The organism should be able to preserve a learned,
provenance-qualified patch in memory
while running a bounded self-evaluation /
counterfactual shadow test
before that patch is allowed to control new cell births.

That directly advances:

self-evaluation;
confidence calibration;
internal drift detection;
and healthy-cell consensus with constitutional limits.

A17 remains:

CLOSED NEGATIVE / MIXED.

A18 is explanatory only.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
