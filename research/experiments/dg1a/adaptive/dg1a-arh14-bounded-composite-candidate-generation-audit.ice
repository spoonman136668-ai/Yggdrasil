TITLE: DG-1A-AR-H14 — Bounded Composite Candidate Generation Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE CANDIDATE-NOMINATION RESULT + DECOY-CROWDING LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh13-cooperative-structural-utility-audit.ice

PURPOSE
H13 showed that useful permanent structure can be non-additive.

A purely individual structural-credit gate can reject every member of a useful pair.

Exhaustive pairwise causal probing recovers the pair,
but pair search scales quadratically and violates Yggdrasil's resource objective.

H14 separates two questions:

1.
WHAT COMPOSITE STRUCTURE IS WORTH TESTING?

2.
DOES THE TESTED STRUCTURE CAUSALLY EARN PERMANENT CAPACITY?

QUESTION
Can cheap local residual / co-activation statistics nominate a SMALL candidate subset,
while H12-style causal confirmation remains the only authority for permanent structural write?

BOUNDARY
This is synthetic.

It does not:
- prove current Yggdrasil residual statistics have this exact form;
- freeze shortlist size;
- authorize nomination statistics to write heredity directly;
- solve higher-order structure search;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PRIMARY COOPERATIVE TASK
Same non-additive target family as H13.

Candidate directions:
12.

All candidate latent streams:

AR(1)
rho = 0.95

variance:
0.25.

Observation-noise variance:
0.04.

Hidden useful pair:

candidate 0
+
candidate 1.

Functional target:

y_t
=
z_0(t)
*
z_1(t).

No candidate receives a semantic label.

CURRENT MODEL
Before the cooperative structure is discovered,
the model predicts:

0.

Local unresolved functional residual is therefore:

r_t = y_t.

CHEAP NOMINATION SIGNAL
For each individual candidate i,
track a low-cost residual co-activation statistic:

score_i
=
Cov(
    x_i^2,
    r^2
).

Intuition:

if an unresolved functional error repeatedly becomes large when a candidate's local activity magnitude becomes large,
that candidate may participate in missing structure.

This is only a NOMINATION heuristic.

It does not establish causal utility.

State / update cost grows:

O(N)

in candidate count.

No all-pairs covariance table is required at the nomination stage.

SHORTLIST
Select top-K candidate directions by nomination score.

Then spend expensive H13-style cooperative functional probes only on pairs within that shortlist.

Primary:

N = 12.

K = 4.

Thus expensive pair tests fall from:

C(12,2)
=
66

to:

C(4,2)
=
6.

NOMINATION MATURATION
Fresh 200-seed sweep.

Probability that BOTH true pair members appear in top-4:

100 observation samples:
82.5%.

300:
99.0%.

1000:
100%.

3000:
100%.

Median ranks of the two true candidates at 1000 samples:

1
and
2.

PRIMARY POSITIVE
A cheap O(N) residual co-activation statistic can identify the members of the missing cooperative structure well enough to reduce the expensive causal search surface dramatically.

It requires maturation.

Very short nomination history can miss one member.

CAUSAL CONFIRMATION
Nomination does not write structure.

Candidate pairs still require H13-style repeated causal functional microprobes.

Primary pair-probe settings:

consequence-noise SD:
0.06.

8 microprobes per tested pair per block.

pair-utility EMA:
0.25.

permanent write persistence:
7 positive candidate-pair evaluations.

PRIMARY CLEAN CONFIRMATION
64 matched seeds.

Nomination history:
1000 samples.

Top-4 shortlist.

TRUE PAIR INCLUDED:
64 / 64.

TRUE PAIR PERMANENT GROWTH:
64 / 64.

FALSE PAIR GROWTH:
0 / 64.

median structural discovery block:
11.

median expensive pair-probe evaluations before growth:
576.

EXHAUSTIVE N=12 COMPARATOR
All 66 pairs causally tested.

64 matched seeds.

TRUE PAIR GROWTH:
64 / 64.

FALSE FIRST-GROWTH:
0 / 64 in this confirmation.

median growth block:
13.5.

median expensive pair-probe evaluations:
7656.

RESOURCE RESULT
Clean top-4 nomination reduces median expensive pair-probe evaluations from:

7656

to:

576.

Reduction:
approximately 92.5%.

This is the core H14 gain.

The cheap nomination stage is not itself trusted as structural evidence.

It only allocates the expensive causal-probe budget.

MISLEADING NOMINATION / DECOY STRESS
The nomination signal is now deliberately corrupted.

Four decoy candidates:
2
3
4
5

receive a residual-correlated measurement-energy artifact.

The artifact raises:

Cov(x_i^2, r^2)

without making those candidate directions functionally useful.

Random sign is used so the decoy measurement artifact does not become a stable useful bilinear predictor.

This stress asks:

CAN A CHEAP NOMINATION HEURISTIC BE FOOLED
WITHOUT CAUSING FALSE HEREDITARY WRITE?

TOP-4 TRUE-PAIR INCLUSION
1000 nomination samples.

200 fresh seeds.

decoy strength 0:
100%.

0.5:
100%.

1.0:
57%.

1.5:
0.5%.

2.0:
0%.

PRIMARY NOMINATION NEGATIVE
Cheap residual co-activation is NOT causal.

Strong residual-correlated decoys can completely crowd the shortlist.

Therefore:

NOMINATION CONFIDENCE
IS NOT
STRUCTURAL-WRITE CONFIDENCE.

CAUSAL-CONFIRMATION SAFETY
Decoy strength:
1.5.

64 matched seeds.

TOP-4 ONLY:

initial true-pair inclusion:
0 / 64.

true permanent growth:
0 / 64.

false permanent growth:
0 / 64.

no growth:
64 / 64.

Interpretation:

the misleading nomination causes a STALL,
not false heredity.

This is the desired authority boundary.

The cheap stage may waste time or miss structure.

It cannot directly allocate permanent capacity.

WIDER SHORTLIST
At decoy strength 1.5:

top-6 true-pair inclusion
in the broader 200-seed nomination sweep:

99%.

64-seed full causal confirmation:

true growth:
63 / 64
=
98.4%.

false growth:
0 / 64.

no growth:
1 / 64.

median growth block:
14.

median expensive pair-probe evaluations:
1800.

Thus widening the shortlist recovers most missed structure
while remaining far cheaper than exhaustive all-pairs search.

ADAPTIVE SHORTLIST EXPANSION
A simple synthetic fallback begins with:

top-4.

If no pair earns structural write by:

15 structural blocks,

expand to:

top-6.

No semantic "nomination failed" label is supplied.

The trigger is simply:

NO CAUSALLY CONFIRMED STRUCTURE YET.

Decoy strength:
1.5.

64 matched seeds.

initial top-4 true inclusion:
0%.

eventual true growth:
98.4%.

false growth:
0%.

no growth:
1.6%.

median growth block:
27.

median expensive pair-probe evaluations:
2280.

EXHAUSTIVE DECOY COMPARATOR
All 66 pairs:

true growth:
100%.

false first growth:
0% in the matched 64-seed run.

median expensive pair-probe evaluations:
6072.

Thus adaptive shortlist expansion uses approximately:

62.4%

fewer expensive pair-probe evaluations than exhaustive search in this decoy stress,
at the cost of slower discovery and one unrecovered seed within the tested horizon.

PRIMARY ARCHITECTURAL RESULT
Candidate generation and structural authority should be separate.

CHEAP NOMINATION
answers:

WHAT MIGHT BE WORTH TESTING?

CAUSAL STRUCTURAL CREDIT
answers:

WHAT DESERVES PERMANENT CAPACITY?

Only the second question can authorize slow structural growth.

FAIL-SAFE DIRECTION
When nomination is wrong,
the preferred failure is:

NO STRUCTURAL WRITE
+
OPTIONAL SEARCH EXPANSION.

Not:

PROMOTE THE NOMINATION.

This mirrors prior Yggdrasil patterns:

source exists
!=
source is trusted.

memory exists
!=
memory should control phenotype.

candidate is correlated
!=
candidate deserves hereditary capacity.

CURRENT COMPOSITE-SEARCH PIPELINE
LOCAL FUNCTIONAL RESIDUAL

+

CHEAP CANDIDATE ACTIVITY

->

O(N) NOMINATION SCORES

->

SMALL SHORTLIST

->

BOUNDED COMPOSITE CANDIDATE SET

->

H12/H13 FUNCTIONAL CAUSAL MICROPROBES

->

PERSISTENT COOPERATIVE UTILITY

->

PERMANENT STRUCTURAL WRITE.

IMPORTANT NEGATIVE
H14's nomination statistic works because the true bilinear pair leaves an individual residual-energy signature.

Not every non-additive structure will do that.

A parity-like or cryptographic interaction may have:

no useful individual nomination statistic.

In that case:
top-K individual nomination can fail systematically.

Therefore H14 reduces search only when useful composite structure leaves some low-order local trace.

COMPUTATIONAL PRINCIPLE
A bounded developmental system should exploit:

CHEAP WEAK EVIDENCE
TO ALLOCATE
EXPENSIVE STRONG EVIDENCE.

It should not confuse the two evidence classes.

This principle now appears across:

context sensing;

causal controls;

value-of-information;

structural growth.

DECISION
AR-H14 is POSITIVE WITH A DECOY-CROWDING LIMIT.

Supported synthetically:

- low-cost residual/co-activation statistics can nominate cooperative structural candidates;
- nomination can reduce expensive pairwise causal probing by over 90% in the clean working point;
- nomination requires maturation;
- residual-correlated artifacts can crowd a fixed shortlist;
- causal confirmation prevents nomination error from becoming false permanent structure;
- widening the shortlist after failed causal confirmation can recover missed structure at additional cost.

Not demonstrated:

- real Yggdrasil nomination residual;
- scalable nomination for structures with no low-order signature;
- learned shortlist size;
- higher-order interaction nomination;
- spatially distributed composite structures;
- optimal search-expansion policy.

NEXT CLEAN QUESTION
AR-H15 — NOMINATION TRUST / SEARCH EXPANSION UNDER RECURRENT DECOYS

Question:

Can candidate-generation heuristics themselves acquire reversible trust from their history of:

NOMINATION
->
CAUSAL CONFIRMATION
or
CAUSAL REJECTION?

A nomination source that repeatedly proposes causally useless decoys should lose search-budget authority.

A source that repeatedly nominates useful structure should gain it.

Desired:

reduce repeated probe waste from persistent decoy mechanisms

without permanently suppressing a nomination channel that may become useful after topology change.

This should reuse the S9 pattern:

identity
!=
current trust.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
primary_candidates = 12
primary_shortlist = 4
expanded_shortlist = 6
nomination_primary_samples = 1000
clean_confirmation_seeds = 64
decoy_confirmation_seeds = 64
primary_pair_consequence_noise_sd = 0.06
pair_write_persistence = 7
