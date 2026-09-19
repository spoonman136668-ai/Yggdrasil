TITLE: DG-1A-AR-H108 — Multi-Scale Perceptual Hierarchy / Adaptive Information-Scale Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE AGREEMENT-GATED SCALE-SELECTION RESULT + FIXED-SCALE ALIASING LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh107-sensory-relay-specialization-audit.ice

PURPOSE
H106-H107 establish:
local collective sensing
and
local sensory relays.

H108 asks:

WHEN SHOULD
LOCAL CONTEXT SUMMARIES
BE ALLOWED TO:
MERGE
INTO
LARGER-SCALE REPRESENTATIONS?

The desired rule is:

homogeneous local evidence
->
compress upward.

spatial disagreement
->
stop aggregation
and
preserve:
fine resolution.

BOUNDARY
This is synthetic.

It does not:
- freeze a 4x4 tile hierarchy;
- freeze confidence thresholds;
- prove the final Yggdrasil perceptual hierarchy;
- establish real communication costs;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

FINE PERCEPTUAL TILES
A synthetic tissue region is represented by:

4 x 4
fine local relay summaries.

Each fine summary receives:
noisy local evidence
for:
binary context.

Local evidence is:
approximately 89%
accurate
before:
higher-scale condensation.

CANDIDATE SCALES

FINE LOCAL
16 independent summaries.

REGIONAL
four:
2 x 2
summary blocks.

GLOBAL
one organism-scale summary.

ADAPTIVE HIERARCHY
Start:
fine.

For each:
2 x 2
region,

merge upward only if:

- regional mean evidence is:
sufficiently decisive;
- within-region evidence dispersion is:
sufficiently low.

Then:
global merge is allowed only if:
all four regional summaries
are themselves:
successfully compressed

and:
their evidence remains:
coherent.

Thus:
higher scale requires:
agreement.

PRIMARY WORKING POINT
mean-evidence margin:
0.12.

within-region variance limit:
0.08.

These are:
diagnostic,
not frozen.

HOMOGENEOUS WORLD
All 16 fine regions
share:
one context.

10,000 matched synthetic episodes.

ALWAYS LOCAL

accuracy:
approximately 89.09%.

summary-state cost:
16.

ALWAYS GLOBAL

accuracy:
100%.

cost:
1.

FIXED FOUR-REGION PYRAMID

accuracy:
approximately 99.41%.

cost:
4.

ADAPTIVE

accuracy:
approximately 95.70%.

mean retained summaries:
3.81.

PRIMARY HOMOGENEOUS COMPRESSION POSITIVE
When:
the world is actually homogeneous,

the adaptive hierarchy:
collapses perception upward

and:
reduces:
active representational state
by:
approximately 76%
relative to:
fine-local representation.

It does not always reach:
one global summary

because:
local observation noise
sometimes blocks:
promotion.

That conservatism costs:
some accuracy

but:
protects:
heterogeneous cases.

IRREGULAR PATCH WORLD
Fine contexts form:
spatially coherent
but
non-aligned
random patches.

The patch boundaries do NOT:
respect:
the fixed regional hierarchy.

10,000 matched episodes.

ALWAYS LOCAL

accuracy:
89.13%.

cost:
16.

ALWAYS GLOBAL

accuracy:
50.0%.

cost:
1.

FIXED FOUR-REGION

accuracy:
68.55%.

cost:
4.

ADAPTIVE

accuracy:
86.10%.

mean summaries:
11.53.

PRIMARY PATCH POSITIVE
When:
spatial structure becomes:
heterogeneous,

the hierarchy:
automatically retains:
much more fine detail.

It avoids:
most
of the destructive averaging
performed by:
fixed regional
or
global representations.

The remaining gap versus:
fully local sensing

is the cost of:
occasional incorrect compression.

MIXED-WORLD TEST
50%:
homogeneous episodes.

50%:
irregular patch episodes.

MEAN RESULTS

LOCAL

accuracy:
89.06%.

cost:
16.

GLOBAL

accuracy:
75.00%.

cost:
1.

FIXED REGIONAL

accuracy:
83.97%.

cost:
4.

ADAPTIVE

accuracy:
90.90%.

cost:
7.67.

PRIMARY ADAPTIVE-SCALE RESULT
Across:
changing spatial structure,

agreement-gated scale selection
achieves:
the highest tested mean accuracy

while:
using less than:
half
the active summary state
of:
always-local perception.

At a diagnostic state-price:
0.005 per active summary,

accuracy-minus-cost value:

LOCAL:
0.8106.

GLOBAL:
0.7450.

FIXED:
0.8197.

ADAPTIVE:
0.8706.

This is:
a synthetic resource objective,
not:
a universal weighting.

FIXED-SCALE FAILURE
No one spatial scale
works well
across:
all contexts.

GLOBAL

is excellent when:
the world is global.

It destroys:
local distinctions
when:
the world is patchy.

FINE LOCAL

preserves:
local truth

but:
pays:
maximum permanent state / communication.

FIXED REGIONAL

fails when:
real context boundaries
do not align with:
the developer's partition.

Thus:

PERCEPTUAL SCALE
SHOULD NOT NECESSARILY
BE:
A PERMANENT ARCHITECTURE CONSTANT.

CURRENT SCALE-SELECTION OBJECT
LOCAL SUMMARY

+

NEIGHBOR AGREEMENT

+

WITHIN-REGION DISPERSION

+

INFORMATION / STATE COST

+

PARENT-SCALE FIT

->

KEEP LOCAL

or

MERGE UPWARD.

The representation can:
grow coarse
or:
refine
as:
spatial causal structure changes.

RELATION TO H7
H7:
inherited representation should carry:
model-fit confidence.

H108:
higher perceptual scale
also needs:
FIT CONFIDENCE.

If:
fine evidence does not fit:
one coarse representation,

do not:
force compression.

RELATION TO H36
H36:
shared generative basis
compresses:
many related lineages.

H108:
shared perceptual summary
compresses:
many related local contexts.

Both require:
shared-structure fit.

RELATION TO H106
H106:
global averaging fails
under:
simultaneous local contexts.

H108:
global perception is still useful
when:
evidence proves:
the context really is global.

Thus:
the lesson is NOT:

NEVER GLOBALIZE.

It is:

GLOBALIZE
ONLY
WHEN:
LOCAL EVIDENCE SUPPORTS
THE COARSER SCALE.

OUTSIDE-STATUS-QUO IMPLICATION
Perceptual hierarchy itself
can be:
developmental.

Instead of:
a fixed number of encoder layers
or:
fixed-resolution feature pyramid,

the organism can:
grow
and
collapse:
representational scale

according to:
the spatial structure
of:
current evidence.

GENERAL PRINCIPLE
COMPRESS:

WHERE
THE WORLD IS
REDUNDANT.

KEEP DETAIL:

WHERE
THE WORLD IS
DIFFERENT.

DECISION
AR-H108 is POSITIVE WITH A FIXED-SCALE ALIASING LIMIT.

Supported synthetically:

- homogeneous context can be compressed to coarser representations;
- irregular local context should retain fine structure;
- one fixed perceptual scale is inferior across changing spatial regimes;
- agreement/dispersion gating adaptively changes representational scale;
- adaptive scale can improve mean accuracy while reducing active state;
- global representation is useful when supported, harmful when assumed.

Not demonstrated:

- continuous spatial scale;
- asynchronous hierarchical updates;
- learned merge criteria;
- top-down prediction;
- cross-scale causal credit;
- real sensory encoder growth.

NEXT HIGH-VALUE MOVE
AR-H109 — TOP-DOWN CONTEXT AS PRIOR, NOT AUTHORITY

H108 creates:
higher-scale perceptual summaries.

That introduces a new danger:

A STRONG REGIONAL / GLOBAL MODEL
MAY OVERRIDE:
REAL LOCAL ANOMALY.

Question:

how should:
top-down context

interact with:
bottom-up evidence?

Compare:

A.
top-down override;

B.
bottom-up only;

C.
top-down prior
+
local likelihood;

D.
local contradiction / novelty gate;

E.
rare local anomaly inside:
a strongly homogeneous global context;

F.
false local noise spike.

Desired:

coarse context
should:
denoise weak local evidence

but:
must lose authority
when:
persistent local evidence
proves:
a genuine exception.

This would connect:
H108 perception
to:
H6 fast suppression,
H7 model-fit,
and
H25 authority separation.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
fine_tiles = 16
mixed_adaptive_accuracy = 0.90898
mixed_adaptive_cost = 7.6709
mixed_local_accuracy = 0.89059
mixed_global_accuracy = 0.75
