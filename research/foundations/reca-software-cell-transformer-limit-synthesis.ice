TITLE: DG-1 — ReCA / Software-Cell / Transformer-Limit Research Synthesis
DATE: 2026-09-20
STATUS: LITERATURE SYNTHESIS / EXPERIMENT GENERATOR / NON-CANONICAL EVIDENCE
TRACK: DG-1 / DEVELOPMENTAL INTELLIGENCE / CELLULAR RESERVOIRS
BRANCH: dg1a-ar

PURPOSE

Evaluate how:
software-cell architectures,
Reservoir Cellular Automata (ReCA),
and:
Neural Cellular Automata (NCA)

can:
reduce:
or:
avoid:
some:
Transformer limitations

relevant to:
Yggdrasil.

PRIMARY QUESTION

Can:
local:
fixed:
or:
slowly changing:
cellular dynamics

supply:

- temporal memory;
- reusable feature expansion;
- rule induction;
- low-cost state evolution;
- developmental growth;

without:
requiring:

- full:
  end-to-end:
  backpropagation
  through:
  the entire:
  active system;
- quadratic:
  attention;
- a:
  large:
  KV cache;
- one:
  new:
  full network
  per:
  new capability?

SCOPE NOTE

This synthesis distinguishes:

A.
Reservoir computing
as:
a Transformer alternative.

B.
ReCA
as:
a:
specific:
cellular reservoir substrate.

C.
NCA-generated data
as:
a:
training curriculum
for:
a Transformer.

These:
are:
different mechanisms.

Do NOT:
collapse them
into:
one claim.

VERIFIED SOURCE 1

Reservoir Computing as a Language Model.

Felix Köster,
Atsushi Uchida.

arXiv:
2507.15779.

Submitted:
2025-07-21.
v3:
2026-01-09.

Core result:

character-level:
language modeling
compares:

- traditional reservoir;
- attention-enhanced reservoir;
- Transformer.

Only:
the reservoir output/readout
is:
trained
in:
the classical reservoir condition.

Reported conclusion:

Transformers:
retain:
better:
prediction quality.

Reservoirs:
offer:
substantial:
training/inference:
efficiency advantages.

YGGDRASIL INTERPRETATION

This is:

DIRECT:
evidence

that:
a:
frozen:
dynamic substrate

plus:
small:
trainable readout

can:
perform:
language-model-like:
sequence processing.

It is NOT:

direct ReCA evidence.

It supports:
the:
reservoir principle,

not:
a:
specific:
cellular rule family.

VERIFIED SOURCE 2

Benchmarking Learning Efficiency in Deep Reservoir Computing.

Hugo Cisneros,
Josef Sivic,
Tomas Mikolov.

CoLLAs:
2022.

arXiv:
2210.02549.

Core result:

compares:
reservoir models

against:

- RNNs;
- LSTMs;
- Transformers;

on:
sequential:
learning tasks
requiring:

- memory;
- Boolean computation;
- compositional:
  primitives.

Reported:
dynamically evolving:
reservoir feature maps

can:
learn:
from:
fewer:
training examples

than:
fully supervised:
SGD-trained:
sequence models

while:
reaching:
comparable:
accuracy
on:
the benchmark.

IMPORTANT CORRECTION

This paper:

is NOT:
a:
ReCA-specific:
benchmark.

Do NOT:
cite it
as:
proof:
that:
cellular automata
specifically
beat:
Transformers.

Use it as:

GENERAL:
reservoir-learning-efficiency:
evidence.

YGGDRASIL INTERPRETATION

The relevant:
mechanical idea is:

move:
complex:
state transformation

into:
a:
fixed:
or:
non-gradient-trained:
dynamic substrate

and:
learn:
small:
readouts.

This matches:
Yggdrasil's:
goal
of:
minimizing:
per-capability:
permanent:
learned structure.

VERIFIED SOURCE 3

Deep Reservoir Computing Using Cellular Automata.

Stefano Nichele,
Andreas Molund.

2017.

arXiv:
1703.02806.

Core architecture:

Elementary Cellular Automata
serve:
as:
the reservoir.

Input:

is:
mapped:
into:
cell states.

The automaton:

evolves:
under:
a:
fixed:
local rule.

The resulting:
space-time states

become:
the:
reservoir feature map.

A:
readout
is:
trained.

The paper:

tests:
5-bit:
memory

and:
adds:
a:
second:
stacked:
reservoir layer.

Rules discussed / tested include:

90,
150,
22,
30,
126,
182,
110,
54,
62,
60,
and:
related rules.

Two-layer:
reservoirs
can:
improve:
some:
memory-task:
performance.

YGGDRASIL INTERPRETATION

This is:

DIRECT:
ReCA evidence.

The key reusable pattern:

LOCAL RULES
+
STATE EVOLUTION
+
SPACE-TIME FEATURE VOLUME
+
SMALL READOUT.

This gives:
a:
candidate:
software-cell:
temporal memory organ

that:
does NOT:
need:
attention
to:
revisit:
every:
previous token.

VERIFIED SOURCE 4

Reservoir Computing using Cellular Automata.

Ozgur Yilmaz.

2014.

arXiv:
1410.0162.

Core result:

randomly map:
input
into:
CA initial state.

Apply:
fixed:
CA rule

for:
several:
iterations.

Use:
the:
space-time:
CA volume

as:
the:
reservoir.

Reported:

long:
short-term:
memory behavior

with:
substantially:
lower:
computation

than:
Echo State Network:
comparators
in:
the reported tasks.

Additive:
rules

also:
allow:
Boolean:
feature-space:
operations.

YGGDRASIL INTERPRETATION

Rule-90-like:
additive:
reservoirs

may:
be:
especially useful

for:

- cheap:
  temporal traces;
- reversible-ish:
  distributed:
  feature transforms;
- symbolic:
  composition;
- memory:
  expansion
  through:
  computation.

VERIFIED SOURCE 5

Reservoir Computing Hardware with Cellular Automata.

arXiv:
1806.04932.

Core point:

Rule 90:

is:
hardware-friendly

because:
its update

is:
neighbor:
XOR.

This can:
be:
implemented
with:
shift registers
and:
XOR gates.

YGGDRASIL INTERPRETATION

For:
software:

Rule 90
maps:
extremely well
to:

- bit-packed arrays;
- SIMD;
- GPU bitwise kernels;
- CPU vector operations.

This is:
useful
if:
Yggdrasil
needs:
a:
high-throughput:
cheap:
memory substrate.

CAUTION 1 — RULE 90

2023:
Glover,
Lind,
Yazidi,
Osipov,
Nichele

explicitly:
criticize:

- overreliance:
  on:
  Rule 90;
- weaknesses:
  in:
  the:
  standard:
  5-bit:
  memory benchmark.

They show:
the:
benchmark
can:
favor:
particular:
simple:
properties

and:
should not:
be:
treated:
as:
sufficient:
evidence
of:
general:
reservoir intelligence.

Therefore:

do NOT:

select:
Rule 90
because:
it:
wins:
5-bit memory.

Use:

Rule 90
as:
one:
cheap:
linear/additive:
reference point.

Compare:

multiple:
rule classes.

CAUTION 2 — EDGE OF CHAOS

The:
"edge of chaos"
idea

is:
useful:
as:
a:
hypothesis

about:
memory /
nonlinearity:
balance.

It is NOT:
a:
universal:
selection rule.

For:
Yggdrasil:

measure:

- memory capacity;
- perturbation propagation;
- input separability;
- state entropy;
- prediction fidelity;
- compute cost;

directly.

Do NOT:
choose:
a rule
only:
because:
it is:
labeled:
edge-of-chaos.

VERIFIED SOURCE 6

Training Language Models via Neural Cellular Automata.

Dan Lee,
Seungwook Han,
Akarsh Kumar,
Pulkit Agrawal.

arXiv:
2603.10055.

Core mechanism:

use:
NCA-generated:
non-linguistic:
spatiotemporal:
trajectories

as:
synthetic:
pre-pre-training data

for:
a:
Transformer.

Reported:

164M:
NCA tokens

improve:
downstream:
language modeling

and:
accelerate:
convergence

up to:
approximately:
1.6x

in:
the reported:
training setup.

Transfer:
also appears
on:
math,
code,
and:
reasoning:
benchmarks.

The paper reports:

attention layers:
as:
especially:
transferable

and:

optimal:
NCA:
complexity
depends:
on:
target domain.

IMPORTANT CORRECTION

This paper:

does NOT:
replace:
Transformers
with:
NCA.

It:

uses:
cellular:
dynamics

to:
create:
a:
synthetic:
learning curriculum

for:
a:
Transformer.

YGGDRASIL INTERPRETATION

The useful idea is:

CELL-WORLD:
CURRICULUM.

A:
developmental:
system
may:
learn:

- rule induction;
- local causality;
- long-range:
  consequences
  of:
  local updates;
- latent:
  transition:
  structure;

from:
synthetic:
cell trajectories

before:
task-specific:
experience.

This can:
be:
adapted
to:
Yggdrasil
without:
requiring:
a:
Transformer.

VERIFIED TOOLING 1

ReservoirComputing.jl
+
CellularAutomata.jl.

SciML:
provides:
native:
RECA:
support

and:
a:
5-bit:
memory:
tutorial.

The implementation follows:
the:
Nichele/Molund:
ReCA family.

YGGDRASIL USE

Useful as:

reference:
implementation
and:
behavioral:
oracle

for:
small:
ReCA:
experiments.

Not required:
as:
a:
runtime dependency.

A:
NumPy:
or:
Go:
implementation

should be:
straightforward
for:
bounded:
home-scale:
testing.

VERIFIED TOOLING 2

TransformerECA.

Mikhail Burtsev.

Repository:
burtsev/TransformerECA.

Purpose:

train:
Transformers
to:
learn /
predict:
Elementary Cellular Automata:
state transitions
and:
related:
rule tasks.

IMPORTANT CORRECTION

TransformerECA:

is NOT:
a:
Transformer replacement.

It is:

a:
useful:
dataset /
task /
evaluation:
reference

for:
whether:
a:
model
learns:
local:
cellular:
transition laws.

YGGDRASIL USE

Borrow:

- CA:
  task generation;
- rule-prediction:
  benchmarks;
- look-ahead:
  prediction;
- state-to-rule:
  inference;

as:
tests
of:
Yggdrasil:
cell-rule:
reasoning.

CORE SYNTHESIS

The literature supports:

THREE:
distinct:
Yggdrasil:
opportunities.

OPPORTUNITY A

FROZEN:
CELLULAR:
TEMPORAL RESERVOIR.

Use:
software cells

with:
fixed:
local:
update rules

as:
a:
cheap:
temporal:
state substrate.

Train:

only:
small:
readouts
or:
capability-specific:
decoders.

Potential benefit:

avoid:
full:
attention
over:
all:
history.

OPPORTUNITY B

DEEP /
HETEROGENEOUS:
CELLULAR:
RESERVOIR.

Use:

multiple:
reservoir patches

with:

- different:
  rules;
- different:
  timescales;
- different:
  update rates;
- stacked:
  outputs;
- parallel:
  local:
  dynamics.

Potential benefit:

long:
memory
without:
one:
monolithic:
recurrent:
network.

OPPORTUNITY C

CELLULAR:
CURRICULUM.

Use:

CA /
NCA:
trajectories

as:
synthetic:
developmental:
experience

to:
train:

- rule inference;
- local causality;
- prediction;
- compression;
- repair;
- role switching;
- state reconstruction.

Potential benefit:

teach:
general:
computational:
priors

without:
requiring:
large:
natural-language:
pretraining.

RELATION TO CURRENT H191 RESULTS

H191-P7:

showed:
one-factor:
micropatching
can:
repair:
a:
new capability
without:
old-state drift.

ReCA suggests:

a:
micropatch
need not:
only be:
a:
static:
Gaussian:
factor.

Future:
patches
could be:

LOCAL:
DYNAMIC:
RESERVOIR:
PATCHES.

H191-P8:

showed:
partial:
geometry reuse.

ReCA suggests:

heterogeneous:
rule patches

may:
increase:
reuse

because:
different:
dynamics
supply:
different:
temporal:
feature bases.

H191-P10:

showed:
strong:
family-level:
novelty reuse.

ReCA suggests:

the:
next:
research axis
after:
P11 sleep consolidation

should include:

whether:
a:
small:
shared:
cellular reservoir

can:
replace:
part:
of:
static:
patch geometry

with:
reusable:
time-evolving:
state.

PROPOSED EXPERIMENT FAMILY

Do NOT:
modify:
the:
already-preregistered:
H191-P11.

Open:
a:
separate:
DG-1R:
reservoir-cellular:
line
after:
P11 reaches:
a:
clean:
pause point.

DG-1R-01 —
RULE-SWEEP MEMORY / SEPARATION AUDIT.

Compare:

rules:
90,
110,
150,
22,
30

plus:

a:
non-uniform:
mixed-rule:
reservoir.

Metrics:

- delayed-bit:
  recall;
- nonlinear:
  parity;
- sequence:
  classification;
- state:
  entropy;
- perturbation:
  propagation;
- linear:
  separability;
- runtime;
- memory footprint.

Avoid:
5-bit memory
as:
the:
only:
benchmark.

DG-1R-02 —
STACKED PATCH / MULTI-TIMESCALE ReCA.

Compare:

single:
reservoir

versus:

two-stage:
stacked:
reservoirs

versus:

parallel:
fast /
slow:
rules.

Question:

can:
stacking
increase:
long-range:
memory

without:
increasing:
trainable:
state
proportionally?

DG-1R-03 —
DYNAMIC MICROPATCH.

Replace:
one:
static:
H191-style:
new factor

with:

a:
small:
ReCA:
patch.

Freeze:
the:
rule.

Train:
only:
a:
new:
readout.

Question:

can:
a:
time-evolving:
patch

cover:
multiple:
later:
capabilities

better
than:
one:
static:
basis factor?

DG-1R-04 —
RESERVOIR SLEEP CONSOLIDATION.

Feed:

developmental:
patch histories

into:
a:
small:
ReCA.

Train:

a:
compact:
sleep readout

to:
reproduce:
pre-sleep:
state.

Question:

can:
time
replace:
stored:
patch geometry?

This directly tests:

SPACE-TIME:
TRADEOFF.

DG-1R-05 —
CELL-WORLD CURRICULUM TRANSFER.

Generate:

CA /
NCA:
trajectories

with:
controlled:
complexity.

Train:

a:
small:
Yggdrasil:
rule-prediction /
state-prediction:
module

before:
real:
task:
learning.

Compare:

- no:
  pretraining;
- random:
  synthetic:
  sequences;
- CA:
  trajectories;
- curriculum:
  matched:
  by:
  complexity.

Measure:

- sample efficiency;
- convergence speed;
- rule induction;
- OOD:
  transition:
  inference;
- downstream:
  task:
  transfer.

NORTH-STAR HYPOTHESIS

A:
useful:
Yggdrasil:
cell

may:
not:
need:
a:
large:
learned:
weight block.

Instead:

a:
cell
could contain:

1.
small:
persistent:
state;

2.
fixed:
or:
rarely changed:
local:
update rule;

3.
local:
neighbor:
communication;

4.
optional:
small:
linear /
low-rank:
readout;

5.
bounded:
developmental:
micropatches;

6.
sleep-time:
consolidation.

The:
collective:
computation

would come
from:

STATE
x
LOCAL RULE
x
TIME
x
NEIGHBORHOOD

rather than:

PARAMETER COUNT
alone.

PLAIN-SPEAK SUMMARY

The useful lesson is NOT:

"cellular automata beat Transformers."

The literature does NOT support:
that:
blanket claim.

The stronger:
supported lesson is:

a:
large amount
of:
useful:
sequence processing

can be:
moved
out of:
trainable weights

and into:

cheap:
fixed:
dynamics.

ReCA is:
one:
concrete:
way
to:
do that.

For:
Yggdrasil,
that means:

we should test
whether:
some:
software cells
can:
remember
and:
transform:
history

by:
evolving:
their:
local state

instead of:
asking:
a:
large:
attention model
to:
recompute:
relationships
over:
the:
entire:
history.

And:

we should test:
whether:
time:
and:
cell dynamics

can:
replace:
some:
permanent:
stored:
neural structure.

SOURCE INDEX

Reservoir Computing as a Language Model:
https://arxiv.org/abs/2507.15779

Benchmarking Learning Efficiency in Deep Reservoir Computing:
https://arxiv.org/abs/2210.02549

Deep Reservoir Computing Using Cellular Automata:
https://arxiv.org/abs/1703.02806

Reservoir Computing using Cellular Automata:
https://arxiv.org/abs/1410.0162

Reservoir Computing Hardware with Cellular Automata:
https://arxiv.org/abs/1806.04932

Training Language Models via Neural Cellular Automata:
https://arxiv.org/abs/2603.10055

ReservoirComputing.jl ReCA tutorial:
https://docs.sciml.ai/ReservoirComputing/stable/tutorials/reca/

TransformerECA:
https://github.com/burtsev/TransformerECA

Rule-90 / 5-bit benchmark criticism:
https://doi.org/10.25088/ComplexSystems.32.3.309
