TITLE: DG-1A-CLR3-H190 — Sparse Sleep-Proxy Basis Distillation Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / CAPABILITY HIBERNATION / SPARSE RESIDUAL REUSE
BRANCH: dg1a-ar
PARENT: dg1a-clr3-h189-dormancy-cross-branch-residual-distillation-audit.ice

PURPOSE

H189 established:

- low-compute hibernation preserves task competence;
- tiny global polynomial compensation does not reconstruct the structured
  cross-capability residual closely enough.

H190 asks:

CAN:
A VERY SMALL
SPARSE SET
OF:
EXISTING PARENT BASIS FUNCTIONS

carry:
the dormant cross-branch residual

without:
reactivating:
the full dormant capability branches?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT PHENOTYPE

Exact H188/H189
WARP48_ROLE48_C stored phenotype.

No:
A/B/C coefficient,
warp,
router,
or:
physical-cell
change.

DISTILLATION INPUTS

Per capability context:

128 deterministic
unlabeled context coordinates.

Target:

full phenotype output
minus:
that capability's
branch-only output.

No:
task target
is read.

CANDIDATE PROXY BASIS

Candidates:

all:
3209 original parent-cell
Gaussian basis functions.

No:
new center.

No:
new physical cell.

Each:
sleep proxy

reuses:
an already-existing
parent basis location.

SPARSE OMP RECRUITMENT

At each step:

for every:
unselected parent basis column x_j

score:

Q_j
=
(
x_j^T r
)^2
/
(
x_j^T x_j
+
0.001
).

Select:
maximum Q_j.

Tie:
lower parent-cell index.

Then:
refit:
all selected proxy coefficients
jointly

by:
ridge alpha=0.001

and:
update residual.

Repeat
until:
K proxy sites
are selected.

No:
task target,
validation target,
or:
held-out target
enters:
recruitment.

PROXY BUDGETS

PROXY4.

PROXY8.

PROXY16.

Primary:

PROXY8.

At inference:

selected capability branch
+
selected capability's
proxy-basis residual
is evaluated.

Dormant:
full branches

remain:
asleep.

LEARNED ROUTING

Exact H188/H189.

No:
routing update.

COMPUTE ACCOUNTING

Base full phenotype:

3322
proxy units / sample.

Learned scheduler before proxy:

A:
3221.

B:
65.

C:
60.

For:
K proxy sites,

count:

K:
basis evaluations

+
K:
coefficient multiply-adds.

Thus:
extra:
2K.

PROXY8:

A:
3237.

B:
81.

C:
76.

Equal A/B/C:

approximately:
1131.3.

Ratio:

approximately:
34.05%
of:
full.

B-only:

approximately:
2.44%.

C-only:

approximately:
2.29%.

PROXY4:

extra:
8.

PROXY16:

extra:
32.

MEMORY

Each:
proxy site

stores:

- one:
  proxy coefficient;
- one:
  parent-site index
  as:
  structural metadata.

Functional learned-state
parameter growth:

3*K
proxy coefficients

across:
A/B/C.

PROXY8:

24:
new learned scalar parameters

relative to:
3322.

Approximately:
0.72%.

No:
physical cells.

PRIMARY METRICS

Per capability:

- full R^2;
- branch-only R^2;
- PROXY4 / 8 / 16
  known-context R^2;
- learned-scheduled R^2;
- normalized MSE
  versus:
  full phenotype;
- residual reconstruction NMSE;
- selected proxy site count;
- selected-site overlap
  across:
  capabilities;
- proxy coefficient RMS;
- compute;
- memory.

Routing:

same:
H188.

Wake / switch:

same:
300-switch sequence.

No:
refit
during:
switching.

PRIMARY FACTORIAL

Held-out worlds:
20.

Contexts:
3.

Proxy budgets:
4,
8,
16.

60:
context worlds
with:
all proxy-budget metrics.

PRIMARY ACCEPTANCE SHAPE

H190 supports:
SPARSE SLEEP-PROXY
BASIS DISTILLATION

if:

1.
Stored full phenotype:
median A/B/C R^2 >=0.90.

2.
Stored joint competence:
>=90%
worlds
A/B/C all >=0.85.

3.
PROXY8
known-context prediction fidelity:

median normalized MSE
<=0.01
for:
A,
B,
C.

4.
PROXY8
learned-scheduled prediction fidelity:

median normalized MSE
<=0.02
for:
A,
B,
C.

5.
PROXY8
known-context task R^2:

median drop
from:
full
<=0.01
for:
A,
B,
C.

6.
PROXY8
learned-scheduled task R^2:

median drop
<=0.02
for:
A,
B,
C.

7.
Routing accuracy:
median >=0.95.

8.
B-only compute:
PROXY8
<=3%
of:
full.

9.
C-only compute:
<=3%.

10.
Equal A/B/C compute:
<=36%
of:
full.

11.
Sleep-proxy memory:
24 learned coefficients
add:
<=0.80%
to:
H188 learned state.

12.
ZERO task-target replay.

13.
Wake learning cost:
0.

14.
Switch drift:
<=1e-12.

15.
Physical cells:
remain:
3257.

16.
PROXY16 diagnostic:

if:
PROXY8
fails:
strict fidelity

but:
PROXY16
passes,

report:
16:
as:
the minimum tested
sleep-proxy budget.

17.
PROXY4 strong diagnostic:

if:
PROXY4
also passes:
all fidelity/task gates,

report:
four proxies
per capability
as:
sufficient.

STRONG SUPPORT

H190 receives:
STRONG support

if:

all:
PROXY8
primary gates pass

AND:

learned-scheduled
B and C
prediction fidelity

both:
<=0.01.

MIXED / NEGATIVE CONDITIONS

Treat H190 as:
mixed / negative
if:

- eight proxy bases
  do not:
  reconstruct:
  B/C cross-residual structure;

- sixteen proxies
  are:
  still insufficient;

- selected sites
  become:
  effectively:
  a hidden duplicate
  of:
  the dormant branches;

- compute advantage
  collapses;

- proxy recruitment
  overfits:
  unlabeled distillation coordinates.

NEXT

If H190 succeeds:

proceed to:
CLR3-H191 —
FOURTH-CAPABILITY
ACCUMULATION UNDER:
HIBERNATION /
ROLE REUSE /
SLEEP PROXIES.

If H190 fails:

test:
shared:
low-rank
cross-capability
latent factors

rather than:
larger:
sparse caches.

SANITY WORLD SEEDS

20260923990000...

PRIMARY WORLD SEEDS

20260923900000
through:
20260923900019.

Sanity:
NON-EVIDENCE.

No:
parent phenotype,
distillation sample count,
candidate basis,
OMP rule,
ridge,
proxy budgets,
routing rule,
compute accounting,
or:
acceptance gate

may change
after:
the first held-out H190 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SPARSE_SLEEP_PROXY_BASIS_DISTILLATION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — SPARSE SLEEP-PROXY HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H190 HELD-OUT PRIMARY EXECUTION.

FINAL H190 SANDBOX HARNESS

File:

h190_sparse_sleep_proxy_v1.py

SHA-256:

518fb8b96d7118784e3bdd73d5e7d2c1b3395ab8e0be1b36dbb73a01fc3a7bba.

PARENT PHENOTYPE

Exact H188/H189
WARP48_ROLE48_C.

No:
A/B/C
functional state
is:
modified.

DISTILLATION

128:
unlabeled
context coordinates
per:
capability.

Target:

full phenotype
minus:
selected branch.

No:
task target
is:
read.

CANDIDATE PROXIES

All:
3209 existing:
parent basis sites.

No:
new center.

No:
new physical cell.

OMP

Select:
one parent basis
at:
a time

using:

squared residual correlation
divided by:
basis energy
+
0.001.

Refit:
all selected
proxy coefficients

by:
ridge:
0.001

after:
every:
selection.

Frozen budgets:

4,
8,
16.

Primary:

8.

COMPUTE

PROXY8:

B-only:

approximately:
2.438%
of:
full.

C-only:

approximately:
2.288%.

Equal A/B/C:

approximately:
34.056%.

Memory:

24:
proxy coefficients

=
approximately:
0.7225%
of:
H188 learned state.

No:
physical-cell growth.

SANITY

Disjoint family:

20260923990000
and:
20260923990001.

2 worlds.

3 contexts / world.

6 rows.

Accepted sanity-output SHA-256:

35a50c909375fc53e06496839e739b1d1f350c4c4e7c894c64ced3de7ad3b171.

Mechanical checks:

- exact:
  3 contexts / world;
- exact:
  proxy budgets:
  4,
  8,
  16;
- no:
  task-target
  replay;
- no:
  functional-state
  update;
- no:
  physical cell
  addition;
- wake learning:
  0;
- switch drift:
  0.

NON-EVIDENCE SIGNAL

Sparse proxies:

strongly reduce:
some:
cross-branch residuals.

Representative:

world:
20260923990001.

B:
branch mismatch:
approximately:
0.0290.

PROXY8:
approximately:
0.0103.

C:
branch:
approximately:
0.0497.

PROXY8:
approximately:
0.0132.

But:

world:
20260923990000.

B:
branch:
approximately:
0.0530.

PROXY8:
approximately:
0.0503.

PROXY16:
approximately:
0.0425.

Thus:

the sparse:
existing-basis
representation

is:
helpful

but:
may:
remain:
insufficient
for:
the hardest:
B residual worlds.

No:

- OMP rule;
- ridge;
- proxy budget;
- candidate basis;
- compute accounting;
- acceptance gate

was changed.

PRIMARY FAMILY

20260923900000..20260923900019.

20 held-out worlds.

3 contexts / world.

60 rows.

H190 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H190 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — SPARSE SLEEP-PROXY BASIS DISTILLATION

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE FOR LEARNED-SCHEDULED FIDELITY / NEGATIVE FOR STRICT KNOWN-CONTEXT FIDELITY AND STORED JOINT RELIABILITY.

FINAL H190 HARNESS SHA-256

518fb8b96d7118784e3bdd73d5e7d2c1b3395ab8e0be1b36dbb73a01fc3a7bba.

ACCEPTED PRIMARY MATRIX SHA-256

bf44f9751d5c4cf442ca14be13171fd5406f8b5b7fa7de81df19be86257f4bfd.

ACCEPTED PRIMARY FAMILY

20260923900000..20260923900019.

PRIMARY MATRIX

20 held-out worlds.

3 contexts / world.

60 context rows.

STORED FULL PHENOTYPE

Median full held-out R^2:

A:
approximately:
0.98833.

B:
approximately:
0.95522.

C:
approximately:
0.97736.

Median competence:
PASS.

Worlds:
A,
B,
C
all:
R^2>=0.85:

15 / 20
=
75%.

Frozen target:
>=90%.

FAIL.

Thus:

this fresh H190 family
contains:
a substantial:
stored-phenotype
joint tail

before:
sleep proxies
are considered.

PROXY8
KNOWN-CONTEXT
PREDICTION FIDELITY

Median normalized MSE
versus:
full phenotype:

A:
approximately:
0.00180.

B:
approximately:
0.01682.

C:
approximately:
0.01314.

Frozen target:
<=0.01.

A:
PASS.

B:
FAIL.

C:
FAIL.

PROXY8
LEARNED-SCHEDULED
PREDICTION FIDELITY

Median normalized MSE:

A:
approximately:
0.01216.

B:
approximately:
0.01785.

C:
approximately:
0.01314.

Frozen target:
<=0.02.

PASS:
A,
B,
C.

This is:
the strongest:
positive H190 result.

Eight:
reused parent-basis
sleep proxies

are:
sufficient
to bring:
the practical:
learned-router
scheduled path

inside:
the frozen:
2%
prediction-fidelity
ceiling

for:
all three
capability contexts.

TASK PERFORMANCE

PROXY8
known-context
task R^2

does NOT:
drop:
more than:
0.01
from:
full

for:
A,
B,
or:
C.

PASS.

PROXY8
learned-scheduled
task R^2

also:
stays:
within:
0.02

for:
all contexts.

PASS.

ROUTING

Median:
learned route accuracy:

approximately:
0.99674.

Minimum world:

approximately:
0.99154.

PASS.

COMPUTE

PROXY8:

B-only:

approximately:
2.438%
of:
full.

C-only:

approximately:
2.288%.

Equal A/B/C:

approximately:
34.056%.

Frozen limits:

3%,
3%,
36%.

PASS.

MEMORY

PROXY8:

8 coefficients
per:
capability

=
24:
sleep-proxy
learned coefficients.

Growth relative to:
3322:
H188 learned-state
parameters:

approximately:
0.722%.

Frozen limit:
<=0.80%.

PASS.

WAKE / SWITCH

Wake learning:

0.

Maximum:
300-switch
prediction drift:

0.

Physical cells:

3257.

PASS.

PROXY16 DIAGNOSTIC

Known-context
median normalized MSE:

A:
approximately:
0.00195.

B:
approximately:
0.01348.

C:
approximately:
0.01065.

Thus:

doubling:
from:
8
to:
16
proxy bases

still does NOT:
clear:
the frozen:
1%
known-context
fidelity threshold

for:
B

and:
misses narrowly
for:
C.

Therefore:

the remaining:
known-context
residual

is NOT:
efficiently eliminated
by:
simply:
doubling:
sparse proxy count.

PROXY4 DIAGNOSTIC

Also:
fails:
the strict:
B/C
fidelity gates.

Thus:

the result
is:
not:
a four-proxy
strong support.

PRIMARY GATE REVIEW

PASS:

1.
Stored median competence.

4.
PROXY8 learned-scheduled fidelity.

5.
Known-context task R^2.

6.
Learned-scheduled task R^2.

7.
Routing.

8.
B compute.

9.
C compute.

10.
Equal-mix compute.

11.
Sleep-proxy memory.

12.
Zero task-target replay.

13.
Zero wake learning.

14.
Zero switch drift.

15.
Physical cells unchanged.

FAIL:

2.
Stored joint competence.

Observed:
75%.

3.
PROXY8 known-context
strict prediction fidelity
for:
B/C.

16.
PROXY16
does NOT:
fully rescue:
strict known-context fidelity.

17.
PROXY4
does NOT:
pass:
all fidelity gates.

STRONG SUPPORT:

FAIL.

FINAL INTERPRETATION

H190 is:

MIXED-POSITIVE.

Sparse:
reused basis proxies

are:
materially more effective

than:
the H189
global-polynomial
sleep summary.

For:
the actual:
learned-router
scheduled path,

eight:
proxy basis functions
per:
capability

bring:
all three contexts

inside:
the:
2%
prediction-fidelity
ceiling

while:

- B/C active compute
  remains:
  below:
  2.5%
  of:
  naive:
  all-branch compute;

- equal:
  A/B/C
  scheduled compute
  remains:
  near:
  34%;

- added sleep memory
  remains:
  below:
  1%;

- no:
  physical cells
  are added;

- wake:
  remains:
  zero-learning
  and:
  drift-free.

But:

the:
1%
strict:
known-context
fidelity target

is not:
efficiently reached

even:
with:
16 proxies.

Do NOT:

keep:
increasing:
sparse proxy count.

The remaining residual
appears:
distributed /
low-rank

rather than:
well represented
by:
a handful:
of:
independent:
local basis sites.

NEXT:

CLR3-H191 —
LOW-RANK
CROSS-CAPABILITY
SLEEP-FACTOR
DISTILLATION.

Use:
the same:
unlabeled:
full-minus-branch
residual targets.

Construct:
a tiny:
shared:
low-rank
latent basis

across:
all:
A/B/C
contexts,

rather than:
separate:
sparse sites
per:
capability.

Primary question:

can:
a small:
shared:
latent factor set

capture:
the cross-capability
sleep residual

with:

less:
memory
and:
equal or:
better:
fidelity

than:
24 separate:
PROXY8
coefficients,

while:
retaining:
the:
~2%
B/C
active-compute regime?

H190 DOES NOT AUTHORIZE

- production use;
- live model modification;
- biological claims;
- canonical scientific claims;
- STAB-18-R1 execution.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
