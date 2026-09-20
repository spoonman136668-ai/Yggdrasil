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
