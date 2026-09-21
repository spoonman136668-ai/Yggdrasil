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
