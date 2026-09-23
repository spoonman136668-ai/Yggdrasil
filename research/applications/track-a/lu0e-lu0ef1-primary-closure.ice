TITLE: LU-0E LU0EF1 PRIMARY CLOSURE
DATE: 2026-09-23
STATUS: CLOSED / V0.2 STAGED-LOCAL IDENTIFIABLE / MINIMALITY PASS / STAGING REQUIRED
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PREREGISTRATION:
a29e08d0764d54f5e78c44f52a1fed8e922a73fb

MECHANICAL GATE:
4b42bcf9d5546e297dddc2b555d017a5245a7622

LU0EF1:
8e5662805c7f2d7b40903396eac9d5f07db7a89f

AUDIT-SUITE BINDING:
4d183dd1912f044e972f6bc77f87069fbdde2b39

PARENT V0.2:
e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

FROZEN SOURCE

bytes:
15981

SHA256:
1285839a69545b3a1623bcecc8f1e40d5954197e6afead5b8d58f91a6f141778

EXECUTION ENVIRONMENT

Isolated ChatGPT sandbox.

KTRADE:
NOT USED.

ckb-plane:
NOT USED.

Windows self-hosted runner:
NOT USED.

Python site initialization:
DISABLED.

PRIMARY DUPLICATE GATE

runs:
2.

bound counterfactual pairs:
64.

raw bytes per audit:
15043.

raw SHA256:
0bf86413560e3bbc295237f1d5917b71cbb24207ae3f961539d5fe27f800fc08.

byte identical:
TRUE.

external open bytes:
15179.

external open SHA256:
fdd3fd51ad5134954cfdde1a91c93707d7bbfd83055c36190a7819c22286fc48.

SCIENTIFIC STATUS

LU0E_V02_STAGED_LOCAL_IDENTIFIABLE:
TRUE.

LU0E_MINIMALITY_CONTROLS_PASS:
TRUE.

LU0E_STAGING_REQUIRED:
TRUE.

IDENTIFIABILITY RESULT

All 64 counterfactual pairs had:

byte-identical OBS-V1 focal observations;

a material difference
in at least one distant/global diagnostic;

and exact agreement
of the V0.2 teacher transition law.

Maximum paired H-release probability difference:
0.0.

Maximum paired C/S stay probability difference:
0.0.

Maximum paired U-recruitment
[C,S,H,U] total-variation distance:
0.0.

Tolerance:
1e-12.

All three exact-identifiability bars:
PASS.

The pair matrix included:

16 local templates

x

4 distant perturbation families:

STATE;

B;

REQUEST;

COMBINED.

Distant perturbations changed
state composition,
B values,
request composition,
or combinations thereof
outside the bounded local causal envelope.

Thus the zero differences
are not duplicate-world artifacts.

NO_POOL / V0.2 BOUNDARY

Audited parent source identity:
PASS.

V0.2 NO_POOL semantics:
PASS.

Organism-wide pc / ps recruitment input:
ABSENT.

OBS-V1 contains no:

global majority;

global C/S/H count;

global queue length;

phase id;

task id;

future request;

future lesion;

future anchor;

global score.

MINIMALITY CONTROL A — Q/ECHO TRACE

Reduced observation with:

Q_prev_i;

Q_prev_side_i

removed:

paired signature identical.

Full OBS-V1:
distinguishes the pair.

Teacher stay-probability difference:
0.06015037593984962.

Required:
> 1e-6.

PASS.

Therefore the one-epoch Q/ECHO trace
is genuinely necessary
for exact C/S challenge behavior.

MINIMALITY CONTROL B — NEIGHBOR LC12 / LS12

Reduced observation
without neighbor LC12 / LS12:

paired signature identical.

Full OBS-V1:
distinguishes the pair.

Teacher U-transition TV:
0.06893722029597726.

Required:
> 1e-6.

PASS.

Therefore focal LC12 / LS12 alone
is insufficient.

The student needs either:

neighbor local-evidence channels;

or an information-equivalent raw local task field
large enough to reconstruct them.

MINIMALITY CONTROL C — RAW TASK RADIUS

A boundary request at ring distance 17
is invisible to a raw radius-16 request observation.

Raw radius-16 signatures:
identical.

The same request
changes a neighbor LC12 / LS12 value
needed by focal U recruitment.

Radius 17 detects the boundary request.

Exhaustive geometry check:

requests strictly outside radius 17
do not change the OBS-V1 task-perception fields.

Therefore:

raw radius 16:
INSUFFICIENT.

raw radius 17:
SUFFICIENT
for the audited task-perception dependency.

This does not require
a flattened radius-17 MLP input.

The preferred representation remains
fixed bounded local perception
feeding the compact radius-3 student vector.

STAGED-ORDER CONTROL

A local H neighbor
had teacher release probability:

0.11524895584864114.

Deterministic fixture seed:

LU0E-STAGING-13.

The H neighbor released
during the earlier teacher microstage.

Focal U observation
before versus after that local release:
DIFFERENT.

Focal U transition distribution
pre versus post local release:

TV =
0.02570320181868435.

Therefore:

LU0E_STAGING_REQUIRED = TRUE.

The current exact teacher
contains causally meaningful
same-epoch local ordering.

A first student should preserve
the teacher's staged local lifecycle
rather than pretend the entire epoch
is one simultaneous indivisible update.

This is not evidence
that one-shot approximation is impossible.

It is evidence
that one-shot exact imitation
would require marginalizing
same-epoch local stochastic events
that the teacher currently resolves explicitly.

ACCEPTED STUDENT OBSERVATION V1

For focal cell i:

own lifecycle:

state_i;

timer_i;

B_i / B_pre_i as stage appropriate;

Q_prev_i;

Q_prev_side_i.

Radius-3 local vector,
seven cells total:

state_j;

B_pre_j;

LC12_j;

LS12_j.

Focal local task perception:

LC3_i;

LS3_i.

Equivalent raw request-space causal radius:
17.

Sampling remains external
under deterministic stateless RNG.

FIRST-STUDENT HARD / LEARNED BOUNDARY

The first learned model is authorized
to learn the stochastic decision heads:

H RELEASE;

C/S STAY-DEFECT;

U RECRUITMENT C/S/H.

The following may remain
fixed/hard in the first imitation experiment:

local perception operators;

B recurrence;

refractory timer lifecycle;

Q/ECHO bookkeeping;

released-this-epoch exclusion;

state validity;

hard resource and safety guards;

stateless sampling.

This keeps the first learned question narrow:

can one small shared local function
recover the V0.2 stochastic decision law?

ARCHITECTURE CONSEQUENCE

The information-boundary gate
for first teacher imitation is satisfied.

The next authorized experiment is:

FIRST LEARNED SHARED PER-CELL
STAGED TEACHER IMITATION.

Use:

Developmental Substrate V0.2
as teacher/reference;

OBS-V1
or an exactly information-equivalent encoding;

one small shared feed-forward model;

no per-cell learned parameters;

no global context;

no task id;

no future information.

Training success alone
must not promote the learned updater.

It must subsequently pass
closed-loop Task-1,
perturbation,
and functional-regeneration tests.

PLAIN-SPEAK INTERPRETATION

The hidden-wire check passed.

We made 64 pairs of worlds.

Each pair looked exactly the same
to one cell and its allowed neighborhood.

Far away,
we deliberately changed
other cells,
their internal evidence,
the workload,
or all three.

The cell's correct decision probabilities
did not move at all.

Not a little.

Exactly zero
to the audit tolerance.

We also removed pieces of local information
on purpose.

Without the one-epoch echo memory,
the correct stay decision changed by about six percentage points.

Without neighboring local-evidence fields,
the recruitment distribution changed by about 6.9 percentage points.

And a raw task view stopping at radius 16
missed information
that radius 17 correctly captures.

So the local input is not padded arbitrarily.
Those pieces actually matter.

Finally,
we confirmed that the order inside an epoch matters.

A nearby uncertain cell can release first,
and that local change alters
what a recruitable cell should do later
in the same epoch.

So the first learned updater
should learn the organism
in the same local stages.

We have now removed
the known global dependency
and proven that the remaining stochastic decisions
are exactly locally identifiable.

The next step is the first actual learned cell.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
