TITLE: DG-1A-AR-H117 — Endogenous Transition-Friction Learning / State-Specific Hysteresis Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE PER-STATE FRICTION LEARNING RESULT + GLOBAL-HYSTERESIS / UNNECESSARY-AUDIT LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh116-integrated-cognitive-tissue-composition-audit.ice

PURPOSE
H116 found:
hysteresis is useful only when:
state change
is actually expensive.

H117 asks:

CAN THE ORGANISM LEARN
THE COST OF
CHANGING ITSELF

for:
different internal state families?

Candidate state changes:

ROLE EXPRESSION
cheap / reversible.

MACRO IMPLEMENTATION MODE
moderate transition cost.

DEVELOPMENTAL / LINEAGE STATE
expensive.

A single global persistence constant
should be:
structurally wrong
if:
those transition economics differ.

BOUNDARY
This is synthetic.

It does not:
- freeze three state families;
- freeze EMA learning rate;
- prove transition cost is directly observable in real Yggdrasil;
- freeze one persistence forecast;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

THREE STATE FAMILIES

ROLE

functional match value:
0.10 / step.

true switch friction:

phase 1:
0.15.

phase 2:
0.75.

phase 3:
0.15.

Thus:
role change becomes:
temporarily expensive

then:
cheap again.

MACRO

match value:
0.50 / step.

switch friction:
0.60.

LINEAGE

match value:
0.80 / step.

switch friction:
2.00.

PREFERENCE STREAM
3,000 steps.

PHASE 1
mean preferred-state persistence:
~18 steps.

PHASE 2
volatile:
~4.

PHASE 3
very fast:
~3.

A noisy local predictor estimates:
remaining current preference duration.

Every policy receives:
the same persistence estimate.

POLICIES

NO PERSISTENCE

always switch
to:
current preferred state.

GLOBAL HYSTERESIS

assume:
one switch cost:
0.60

for:
all state families.

LEARNED PER-STATE FRICTION

each state family stores:
its own estimated transition cost.

When:
a switch actually occurs,

realized transition consequence
updates:
that estimate.

Switch only if:

expected remaining match value
>
estimated transition cost.

LEARNED + FORCED AUDIT

same,
but:
occasionally forces
otherwise rejected transitions

to:
refresh
self-knowledge.

PRIMARY CONFIRMATION
500 matched synthetic streams.

NO PERSISTENCE

total value:
~2286.82.

mean switches per state family:

ROLE:
640.74.

MACRO:
640.74.

LINEAGE:
640.74.

PRIMARY ALWAYS-SWITCH NEGATIVE
Treating:
all internal state
as:
free to change

causes:
massive over-switching
for:
expensive lineage state.

GLOBAL HYSTERESIS

total:
~2511.08.

switches:

ROLE:
87.20.

MACRO:
331.51.

LINEAGE:
640.74.

PRIMARY GLOBAL-HYSTERESIS NEGATIVE
One fixed friction:
0.60

is:

too conservative
for:
cheap role changes

and

far too permissive
for:
expensive lineage changes.

Thus:

ONE HYSTERESIS CONSTANT
CANNOT REPRESENT
HETEROGENEOUS SELF-CHANGE.

LEARNED PER-STATE FRICTION

total:
~3070.99.

switches:

ROLE:
166.82.

MACRO:
331.51.

LINEAGE:
225.99.

Improvement:

~22.3%
vs:
global hysteresis.

~34.3%
vs:
always-switch.

PRIMARY SELF-FRICTION POSITIVE
The controller learns:
different persistence economics
for:
different internal variables.

PHASE-1 ESTIMATES
Mean learned transition costs:

ROLE:
~0.151.

MACRO:
~0.600.

LINEAGE:
~2.000.

These closely match:
the true tested costs.

PHASE-2
Role switch friction rises:
0.15
->
0.75.

Learned role estimate:
~0.738.

Macro:
~0.601.

Lineage:
~2.000.

PRIMARY CHANGING-FRICTION POSITIVE
The self-model can update:
how expensive:
a state transition is

when:
the underlying transition mechanics change.

PHASE-3
Role friction becomes:
cheap again:
0.15.

Final learned role estimate:
~0.153.

Thus:
friction memory
is:
reversible.

PHASE VALUES
LEARNED

phase 1:
~1264.07.

volatile expensive-switch phase:
~934.83.

cheap-switch return:
~872.09.

GLOBAL HYSTERESIS

~1249.96.

~721.42.

~539.70.

NO PERSISTENCE

~1248.61.

~556.08.

~482.13.

The largest gain appears exactly where:
state persistence
and
switch economics
interact.

FORCED SELF-AUDIT NEGATIVE
A separate policy adds:
small random forced transitions
when:
the ordinary friction model
would not switch.

RESULT

total:
~3052.86.

This is:
slightly worse
than:
ordinary learned friction.

Why?

In this stream,
naturally profitable switches already provide:
enough observations
to:
track transition cost.

The forced audits:
spend:
real transition value
without:
meaningful extra self-knowledge.

PRIMARY AUDIT LIMIT
H94 showed:
self-audits are useful
when:
policy suppresses:
the evidence needed
to:
update itself.

H117 shows:
do NOT generalize that into:

ALWAYS AUDIT SELF-MODELS.

Audit only when:
self-knowledge is:
actually becoming:
unobservable / stale.

RELATION TO H68
H68:
implementation mode needs:
hysteresis
when:
mode switching has:
real cost.

H117:
the appropriate hysteresis
can be:
derived
from:
learned transition friction

rather than:
hardcoded globally.

RELATION TO H94
H94:
learn:
developmental transition duration.

H117:
learn:
transition cost
across:
several state families.

Together:

THE ORGANISM SHOULD MODEL
ITS OWN:
CHANGE DYNAMICS

AND:
CHANGE ECONOMICS.

GENERAL PRINCIPLE
HYSTERESIS
SHOULD BE:

AN EMERGENT CONSEQUENCE
OF:
TRANSITION COST

NOT:

A UNIVERSAL DESIGN CONSTANT.

Different internal state variables
can deserve:
very different:
persistence.

DECISION
AR-H117 is POSITIVE WITH GLOBAL-HYSTERESIS AND UNNECESSARY-AUDIT LIMITS.

Supported synthetically:

- internal state families can have very different switch costs;
- one global hysteresis constant is structurally suboptimal;
- per-state transition-cost learning improves total value substantially;
- transition friction can itself change over time;
- learned friction can track both increases and decreases;
- expensive lineage state becomes appropriately more persistent;
- cheap role state remains more responsive;
- forced self-audits are not useful when ordinary transitions already provide sufficient calibration evidence.

Not demonstrated:

- real transition-cost measurement;
- coupled transitions among multiple state variables;
- state-change costs with delayed consequence;
- transition-cost inheritance;
- endogenous discovery of state families;
- nonstationary cost under resource scarcity.

NEXT HIGH-VALUE MOVE
AR-H118 — COUPLED STATE TRANSITIONS / CHANGE-DEBT AND DEVELOPMENTAL TRANSACTION AUDIT

H117 treats:
each state variable's transition
independently.

But:
real developmental changes
may share:
migration,
cache flush,
communication,
or
reconfiguration costs.

Question:

if:
ROLE,
MACRO,
and
SENSOR
all need:
to change

should the organism:

change them:
one at a time

or:

bundle:
compatible transitions
into:
one developmental transaction?

Potential gain:

pay:
shared transition overhead
once.

Potential failure:

large bundled change
creates:
rollback difficulty
and
causal-credit ambiguity.

Compare:

A.
independent switching;

B.
always bundle;

C.
compatibility-aware transition transaction;

D.
one component fails validation;

E.
partial rollback;

F.
resource crisis during transition.

Desired:

SELF-CHANGE
may have:
transaction structure

just like:
H44 version leases
and
software atomic updates.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
stream_steps = 3000
matched_streams = 500
learned_total_value = 3070.99
global_hysteresis_value = 2511.08
always_switch_value = 2286.82
