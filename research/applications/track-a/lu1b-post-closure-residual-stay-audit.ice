TITLE: LU-1B POST-CLOSURE RESIDUAL STAY-HEAD AUDIT
DATE: 2026-09-23
STATUS: OBSERVATION-ONLY DIAGNOSTIC / NO RETRAINING
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1BF1:
bdda0fab372187f71b889065698a7b0bf953f95a

LU-1B CLOSURE:
0579573b3483c17a1932210eca245ec37c65b63e

CANONICAL WEIGHT SHA256:
387a6348704e381046e4d0cd05f6a32b2e5da00864e9a9c718f61e2190cd4387

DIAGNOSTIC ARTIFACT

bytes:
9061

SHA256:
979a8f8ffe496c98d40f22e57f65ea3773a5049e0b576be70b786f268316ebca

PURPOSE

Localize the residual committed-cell imitation error
after focal-side canonicalization.

No retraining.

No weight change.

No threshold change.

No alternative hyperparameter.

CORRECTED FULL-MIRROR AUDIT

The LU-1B closure identified that the inherited LU-1A
symmetry helper historically failed to swap FC <-> FS.

This observation-only audit generated the exact preregistered mirror:

C <-> S;
FC <-> FS;
B -> -B;
LC12 <-> LS12;
Q-side C <-> S;
LC3 <-> LS3.

Held-out committed pairs:
1000.

Canonical model-facing input identities:
1000 / 1000.

identity rate:
1.0.

maximum exact teacher stay-probability difference:
0.0.

Therefore the LU-1B canonical representation itself
implements the intended focal-side symmetry correctly.

The prior 0.086 identity rate
was an evaluation-helper defect,
not a canonicalization defect.

This does not change LU-1B qualification:
the stay error bars independently failed.

OVERALL RESIDUAL STAY ERROR

n:
6000.

mean absolute error:
0.0275619427.

p95:
0.1192661330.

p99:
0.2435178667.

maximum:
0.6803559810.

mean signed bias:
+0.0044643717.

MODE STRATIFICATION

CHALLENGE

n:
2658.

mean absolute error:
0.0392022684.

p99:
0.2538299274.

mean signed bias:
+0.0018202257.

SUPPORT

n:
2616.

mean absolute error:
0.0184496264.

p99:
0.1972122051.

NEUTRAL

n:
726.

mean absolute error:
0.0177793447.

p99:
0.3332225382.

Thus average error remains largest in CHALLENGE,
but the extreme tail is not confined to CHALLENGE.

ECHO CONDITIONALITY

CHALLENGE / ECHO ACTIVE / ECHO DOMINANT

n:
876.

mean absolute error:
0.0471913234.

p99:
0.3613770977.

mean signed bias:
-0.0081405915.

CHALLENGE / NO ECHO

n:
1740.

mean absolute error:
0.0350891586.

p99:
0.1904214582.

NEUTRAL / ECHO ACTIVE / ECHO DOMINANT

n:
230.

mean absolute error:
0.0403100765.

p99:
0.4834652892.

mean signed bias:
+0.0401014467.

NEUTRAL / NO ECHO

n:
481.

mean absolute error:
0.0068828447.

p99:
0.0768261969.

SUPPORT / ECHO ACTIVE / ECHO DOMINANT

n:
774.

mean absolute error:
0.0314441222.

p99:
0.3054284397.

mean signed bias:
+0.0118524170.

SUPPORT / NO ECHO

n:
1801.

mean absolute error:
0.0126339173.

p99:
0.1199393272.

This is the central residual result.

The teacher uses Q/ECHO protection only in CHALLENGE.

The flat LU-1B MLP still shows large ECHO-associated errors
in SUPPORT and NEUTRAL,
where Q/ECHO should not reduce pressure at all.

Representative worst residual:

mode:
NEUTRAL.

state:
S.

opposition:
0.7599999905.

own aligned evidence:
0.

qraw:
0.0492882530.

qecho:
0.9947570562.

teacher stay:
0.2216406316.

student stay:
0.9019966125.

absolute error:
0.6803559810.

The student behaves as though
the large matching-side ECHO should protect the cell.

Under the exact teacher law,
NEUTRAL ignores ECHO,
so it should not.

PRESSURE STRATIFICATION

pressure = 0

n:
2872.

mean absolute error:
0.0025669379.

p99:
0.0401139420.

This regime is learned very well.

pressure (0, 0.05]

mean absolute error:
0.0239932136.

pressure (0.05, 0.10]

mean absolute error:
0.0253133183.

pressure (0.10, 0.25]

mean absolute error:
0.0364878724.

pressure (0.25, 0.50]

mean absolute error:
0.0697158979.

pressure > 0.50

mean absolute error:
0.0513725749.

The residual is therefore not simply
a sharp pressure=0 hinge failure.

The model is excellent at pressure exactly zero.

The harder problem is constructing the correct pressure
from relational local inputs
before applying the nonlinear stay law.

ABSOLUTE-ERROR CORRELATIONS

opposition:
+0.387004.

pressure:
+0.362688.

own aligned evidence:
-0.229843.

qeff:
+0.167922.

qecho:
+0.161158.

qraw:
+0.051450.

DIAGNOSIS

LU-1B removed the focal C/S coordinate problem.

The remaining failure is a local relational-aggregation problem.

The flat MLP must simultaneously learn:

which neighbors are SELF;

positive aligned B from those SELF neighbors;

the symmetric neighborhood aggregate;

whether focal local demand is SUPPORT / CHALLENGE / NEUTRAL;

whether Q_prev_side matches SELF;

and that Q/ECHO only participates in pressure
when CHALLENGE is active.

All required information is present in OBS-V1.

LU-0E already proved
the V0.2 stochastic law is staged-local identifiable.

Therefore the evidence does not support adding global context.

It also does not support simply making the flat MLP larger.

NEXT JUSTIFIED EXPERIMENT

Test a structured,
permutation-invariant local relational updater
using exactly the same OBS-V1 information.

Use:

one shared encoder for each radius-3 cell slot;

a separate focal-cell representation;

a symmetric aggregate of the six nonfocal neighbors;

the unchanged focal extras;

and a small shared output trunk.

Do not precompute:

mode;

pressure;

qraw;

qecho;

qeff;

support margin;

teacher probability;

or any target-derived feature.

The architecture should make
"same local rule applied to each neighbor"
cheap to learn
without handing the rule's answer to the model.

Keep:

the parameter ceiling <=18000;

the same dataset counts;

same optimizer;

same training schedule;

same loss;

same qualification bars;

same focal-side canonicalization;

and fresh post-freeze seeds.

PLAIN-SPEAK INTERPRETATION

The neural cell now knows
which side is "me."

That helped.

But it still has trouble
combining the neighborhood correctly.

The clearest mistake is this:

it sees a strong echo memory
and sometimes lets that memory protect the cell
even when the cell is not actually under challenge.

The hand-designed teacher has a strict rule:

ECHO matters during challenge.

Outside challenge,
ignore it.

All the information needed to know that is local.

The problem is that a flat neural network
has to rediscover several repeated neighborhood relationships
from 70 flat numbers.

So the next test will not make it bigger.

We will give it a structure
that treats every neighbor with the same small encoder
and then combines those neighbor summaries symmetrically.

Same information.

Fewer parameters.

Better match to the actual local law.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
