TITLE: LU-1C POST-CLOSURE RESIDUAL STAY-HEAD AUDIT
DATE: 2026-09-23
STATUS: OBSERVATION-ONLY DIAGNOSTIC / NO RETRAINING
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

LU1CF1:
10f4a6d4cd012dd200d6df8e0e1e56f38e2606ec

LU-1C CLOSURE:
044685fb09a04a46cb15bbab91b74418221ce3a0

CANONICAL WEIGHT SHA256:
c3cb57e6ac6da729a045bc4866c5020b404f3713c9bd03fced60e64757e7112b

DIAGNOSTIC ARTIFACT

bytes:
10626.

SHA256:
5b09ccd5f0100994c5bff00b72a85dea578cdf013fd333ae36a60b5da6f992bb.

PURPOSE

Determine whether LU-1C changed
the residual stay-head failure family
or merely changed its magnitude.

No retraining.

No changed weights.

No new threshold.

OVERALL STAY ERROR

n:
6000.

mean absolute error:
0.0253735475.

p95:
0.1059142917.

p99:
0.2891320121.

maximum:
0.6110932231.

mean signed bias:
-0.0031067497.

MODE STRATIFICATION

CHALLENGE

n:
2603.

mean absolute error:
0.0352928183.

p99:
0.3185828435.

mean signed bias:
-0.0147126301.

SUPPORT

n:
2631.

mean absolute error:
0.0183046033.

p99:
0.2319254756.

NEUTRAL

n:
766.

mean absolute error:
0.0159460416.

p99:
0.2795739561.

ECHO CONDITIONALITY

CHALLENGE / ECHO DOMINANT

n:
833.

mean absolute error:
0.0534515653.

p99:
0.4452298117.

mean signed bias:
-0.0323975820.

CHALLENGE / NO ECHO

n:
1739.

mean absolute error:
0.0266619221.

p99:
0.1394707835.

SUPPORT / ECHO DOMINANT

n:
845.

mean absolute error:
0.0300508891.

p99:
0.3498274797.

mean signed bias:
+0.0192370214.

SUPPORT / NO ECHO

n:
1746.

mean absolute error:
0.0126207946.

p99:
0.0978936762.

NEUTRAL / ECHO DOMINANT

n:
236.

mean absolute error:
0.0370860408.

p99:
0.3698040724.

mean signed bias:
+0.0363660245.

NEUTRAL / NO ECHO

n:
515.

mean absolute error:
0.0064649886.

p99:
0.0698262811.

The same causal signature seen after LU-1B remains:

ECHO-associated examples are much harder;

the network underestimates stay in
ECHO-dominant CHALLENGE;

and it overestimates stay in
ECHO-dominant SUPPORT / NEUTRAL,
where the exact teacher does not apply ECHO protection.

PRESSURE

pressure = 0

n:
2909.

mean absolute error:
0.0031648845.

p99:
0.0601534081.

The zero-pressure region remains learned well.

pressure (0, 0.05]

mean absolute error:
0.0218186097.

pressure (0.05, 0.10]

mean absolute error:
0.0286403433.

pressure (0.10, 0.25]

mean absolute error:
0.0396287609.

pressure (0.25, 0.50]

mean absolute error:
0.0654066168.

pressure > 0.50

mean absolute error:
0.0430022338.

ABSOLUTE-ERROR CORRELATIONS

opposition:
+0.355494.

pressure:
+0.290865.

qeff:
+0.240341.

qecho:
+0.238079.

own aligned evidence:
-0.210892.

qraw:
+0.041622.

REPRESENTATIVE WORST CASE

mode:
CHALLENGE.

state:
C.

opposition:
0.9599999785.

own aligned evidence:
0.

qraw:
0.

qecho:
0.8557499051.

pressure:
0.1042500734.

teacher stay:
0.9910174608.

student stay:
0.3799242377.

absolute error:
0.6110932231.

REPRESENTATIVE OFF-MODE ECHO LEAK

One of the largest non-challenge residuals:

mode:
SUPPORT.

state:
C.

opposition:
0.8399999738.

own aligned evidence:
0.

qraw:
0.

qecho:
0.9932085276.

teacher stay:
0.1741665155.

student stay:
0.7172695398.

absolute error:
0.5431030244.

The exact teacher ignores ECHO protection in SUPPORT.

The learned model strongly over-predicts stay.

DIAGNOSIS

LU-1C did not create a new dominant failure family.

The residual is still the same local conditional-interaction problem
identified after LU-1B.

The teacher's committed-cell law requires:

identify SELF versus OPPONENT;

aggregate same-side positive neighbor B;

compare local C/S evidence;

condition ECHO on matching focal side;

and apply ECHO protection only
when local evidence places the cell in CHALLENGE.

A shared neighbor encoder plus arithmetic mean
makes repeated-neighbor processing easier,
but does not explicitly provide
a mechanism for conditional multiplicative interaction
between:

local context;

focal memory;

and the stay decision.

The evidence therefore supports
one further narrow architecture hypothesis:

shared focal-neighbor relational encoding
plus an explicit learned multiplicative gate.

No global information is needed.

No additional teacher-derived feature is justified.

No parameter inflation is justified.

NEXT JUSTIFIED EXPERIMENT

LU-1D should preserve:

OBS-V1 exactly;

LU-1B focal-side canonicalization;

the <=18000 parameter ceiling;

the exact V0.2 teacher;

the exact data counts;

the exact optimizer / loss / training schedule;

and the exact qualification bars.

Change only network geometry:

encode each focal-neighbor pair
through one shared pair encoder;

aggregate the six pair encodings symmetrically;

encode focal and focal-extra channels separately;

then use a learned gate multiplied by a learned value stream
before the output head.

Do not precompute:

mode;

pressure;

opposition;

own aligned B;

qraw;

qecho;

qeff;

support margin;

or teacher probability.

PLAIN-SPEAK INTERPRETATION

The neighbor-sharing idea did not solve the hard part.

The neural cell is still making the same kind of mistake.

When echo memory is large,
it has trouble learning the rule:

USE THIS MEMORY
ONLY WHEN I AM ACTUALLY UNDER CHALLENGE.

Sometimes it ignores useful echo during challenge.

Sometimes it lets echo protect the cell
when the cell is in support or neutral conditions.

That is a conditional gate.

So the next network should be shaped
to learn conditional interactions directly.

It will still see only the same local information.

It will still be small.

But it will have a learned gate
that can decide when one local signal
should modulate another.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
