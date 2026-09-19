TITLE: DG-1A-AR-H90 — Pareto Viability / Lexicographic Constraints + Contextual Tradeoff Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE VECTOR-VIABILITY RESULT + SINGLE-SCALAR / PURE-PARETO LIMITS
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh89-conservation-anchored-viability-audit.ice

PURPOSE
H89 already requires:
several independent consequence dimensions.

H90 asks a more radical question:

SHOULD YGGDRASIL AVOID
COLLAPSING ALL VIABILITY
INTO ONE FIXED SCALAR REWARD?

Candidate alternative:

store:
a VECTOR of causal consequences.

Treat some dimensions as:
HARD CONSTRAINTS.

Treat others as:
CONTEXTUALLY TRADEABLE.

BOUNDARY
This is synthetic.

It does not:
- freeze five viability dimensions;
- freeze context weights;
- prove the safe constraints are known a priori;
- establish final decision theory;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CAUSAL CONSEQUENCE VECTOR
Five dimensions.

Higher is better.

D0:
immediate repair / viability restoration.

D1:
resource-reserve preservation.

D2:
functional-inventory preservation.

D3:
future option / evolvability value.

D4:
downstream / communication stability.

CANDIDATE ACTIONS

FAST_REPAIR
[9,-5,2,-1,1].

SLOW_REPAIR
[6,-1,3,1,2].

CONSERVE
[2,7,2,0,1].

EXPLORE
[1,-2,1,8,-1].

BALANCED
[5,2,4,3,3].

DELETE_LOAD
[7,6,-10,-4,4].

EXPORT_HARM
[6,3,1,1,-8].

NOOP
[0,1,1,0,0].

CACHE_STATE
[3,-1,6,2,-2].

COMM_REPAIR
[4,-2,2,1,8].

IMPORTANT UNSAFE SHORTCUTS
DELETE_LOAD looks attractive on:

repair-like stress
and
resource reserve

because:
it throws useful state away.

EXPORT_HARM looks attractive locally

but:
severely damages downstream stability.

These actions are intentionally included.

HARD SAFETY CONSTRAINTS
Primary diagnostic constraints:

functional inventory:
D2 >= -3.

downstream stability:
D4 >= -3.

Other dimensions remain:
tradeable.

RESOURCE / OPERATING CONTEXTS
Seven contexts.

ACUTE DAMAGE
emphasizes:
repair.

RESOURCE SCARCITY
emphasizes:
reserve preservation.

STABLE GROWTH
emphasizes:
future-option value.

NETWORK DAMAGE
emphasizes:
downstream stability.

MEMORY INTEGRITY
emphasizes:
functional inventory.

LOAD CRISIS
strongly values:
repair
and
load reduction.

LOCAL SHORTSIGHT
tests:
a more immediate local objective.

The contextual weights are:
synthetic diagnostic shadow prices.

COMPARATORS

FIXED SCALAR
One weight vector:

the average of:
all context weights.

Same scalar everywhere.

PURE PARETO
Remove:
strictly dominated safe actions.

Then:
no contextual utility is used.

A random nondominated safe action is selected.

This intentionally tests whether:
Pareto dominance alone
is sufficient.

CONTEXTUAL SCALAR
Use:
current context weights

but:
no hard safety constraints.

LEXICOGRAPHIC SAFE + CONTEXTUAL TRADEOFF
First:

exclude actions violating:
the hard dimensions.

Then:

use current contextual shadow prices
to choose among:
remaining tradeable alternatives.

OBSERVATION NOISE
Each estimated consequence component receives:

Gaussian SD:
0.20.

50,000 synthetic decisions.

Contexts recur:
evenly.

PRIMARY PARETO SET
Among safe actions,
seven remain nondominated:

FAST_REPAIR

SLOW_REPAIR

CONSERVE

EXPLORE

BALANCED

CACHE_STATE

COMM_REPAIR.

PRIMARY PARETO LIMIT
Pareto filtering removes:
obviously inferior choices.

But:
it does NOT tell the organism
which of seven incomparable actions
is appropriate now.

Therefore:

PARETO DOMINANCE
IS A FILTER,
NOT
A COMPLETE ACTION POLICY.

PRIMARY RESULTS

FIXED SCALAR

mean true contextual utility:
3.5471.

safety violations:
0%.

mean regret vs safe contextual oracle:
0.5886.

PRIMARY FIXED-SCALAR NEGATIVE
One universal weighting systematically misprices:
changing operating regimes.

The fixed scalar cannot simultaneously express:

repair urgency

resource scarcity

future-option value

memory integrity

and
network damage

with:
one static tradeoff.

PURE PARETO

mean utility:
2.2823.

safety violations:
0.

mean regret:
1.8535.

PRIMARY PURE-PARETO NEGATIVE
Refusing all scalarization does not solve:
action selection.

Too many useful actions remain:
incomparable.

A context-sensitive tie-break
is still needed.

CONTEXTUAL SCALAR WITHOUT HARD CONSTRAINTS

mean scalar utility:
4.3065.

safety violations:
14.29%.

apparent regret relative to:
SAFE oracle:
-0.1708.

The negative regret is not:
superhuman performance.

It means:
the unconstrained policy receives high scalar score
by choosing:
an action the safe oracle forbids.

LOAD CRISIS
is the main failure.

DELETE_LOAD wins:
the scalar score

because:
it relieves immediate load
and
frees resources

while:
destroying functional inventory.

PRIMARY SINGLE-SCALAR SAFETY NEGATIVE
A scalar objective can:
rationally choose
catastrophic sacrifice

if:
the hard constraint is merely:
another finite weight.

Thus:

SOME CONSEQUENCES
SHOULD NOT BE
TRADED AWAY
FOR ENOUGH REWARD ELSEWHERE.

LEXICOGRAPHIC SAFE + CONTEXTUAL TRADEOFF

mean utility:
4.1334.

safety violations:
0%.

mean regret vs safe contextual oracle:
0.0023.

PRIMARY VECTOR-VIABILITY POSITIVE
The two-stage policy almost exactly matches:
the safe contextual oracle.

It preserves:

HARD FUNCTIONAL BOUNDARIES

while:
adapting
tradeable behavior
to:
current resource / damage context.

This is the strongest tested H90 architecture.

CONTEXT-SPECIFIC EXPRESSION
The safe contextual policy naturally chooses:

ACUTE DAMAGE
->
FAST_REPAIR.

RESOURCE SCARCITY
->
CONSERVE.

STABLE GROWTH
->
EXPLORE.

NETWORK DAMAGE
->
COMM_REPAIR.

MEMORY INTEGRITY
->
BALANCED.

The action changes because:
the current shadow-price vector changes.

No one action is:
globally optimal.

RELATION TO H24
H24 rejected:
one universal confidence scalar.

H90 rejects:
one universal viability scalar.

In both cases:
independent dimensions carry:
different causal meaning.

RELATION TO H67-H68
H67:
compute,
memory,
bandwidth
need:
separate resource prices.

H68:
implementation metabolism changes
with:
the price vector.

H90 generalizes the same architecture to:
functional consequence.

A developmental agent may need:
several consequence currencies

rather than:
one reward.

RELATION TO H89
H89:
typed consequence anchors
protect against:
proxy gaming.

H90:
those typed consequences should not necessarily be:
collapsed back
into:
one fixed number.

That would throw away:
the independence
H89 needed for safety.

LEXICOGRAPHIC INTERPRETATION
H90 does NOT imply:
every safety dimension is eternally absolute.

A higher-order developmental process may:
change which constraints are active
or
how confidence is assigned.

The narrower result is:

if a consequence is currently treated as:
a hard viability boundary,

do not represent it as:
just another small reward coefficient.

GENERAL PRINCIPLE
KEEP:

HARD CONSTRAINTS

TRADEABLE COSTS

AND

CONTEXTUAL PRIORITIES

AS
DIFFERENT KINDS OF STATE.

Do not force:
all three
through:
one scalar objective.

OUTSIDE-STATUS-QUO IMPLICATION
Yggdrasil's endogenous motivation may look less like:

ONE REWARD SIGNAL

and more like:

A LOCAL VIABILITY VECTOR

+
HARD BOUNDARY CONDITIONS

+
CURRENT SHADOW PRICES

+
OPTIONAL PARETO FILTERING.

This resembles:
metabolic / control allocation

more than:
ordinary scalar reinforcement learning.

DECISION
AR-H90 is POSITIVE FOR VECTOR VIABILITY WITH LEXICOGRAPHIC SAFETY,
with clear limits for:
fixed scalar reward
and
pure Pareto choice.

Supported synthetically:

- one fixed scalar underperforms changing viability contexts;
- pure Pareto dominance leaves too many incomparable choices;
- contextual scalarization adapts tradeoffs well;
- contextual scalarization without hard constraints can prefer destructive shortcuts;
- lexicographic safety + contextual prices nearly matches the safe oracle;
- hard constraints and tradeable consequence dimensions should remain representationally distinct.

Not demonstrated:

- how hard constraints are discovered;
- whether constraints should themselves adapt;
- continuous high-dimensional viability;
- distributed local negotiation across conflicting viability vectors;
- real target-free motivational state;
- long-horizon cognitive goals.

NEXT HIGH-VALUE MOVE
AR-H91 — ENDOGENOUS VIABILITY-DIMENSION DISCOVERY / RECOVERABILITY MARGIN

H90 still gives the organism:
the viability vector dimensions.

That remains privileged.

A more radical question:

CAN THE ORGANISM DISCOVER
WHICH INTERNAL VARIABLES
MATTER FOR CONTINUED FUNCTION?

Candidate principle:

a variable is viability-relevant
if:
perturbing it
reduces
the future set of recoverable states / available actions.

Instead of:
maintain a named setpoint,

measure something closer to:

RECOVERABILITY MARGIN.

Compare:

A.
predefined homeostatic variables;

B.
prediction-error variables;

C.
variables selected by correlation with future failure;

D.
variables selected by causal perturbation effect on:
future recoverability / controllability;

E.
sensor-hack variable that predicts stress but does not affect recoverability;

F.
latent bottleneck variable that looks quiet until perturbed.

Desired:

the organism begins to discover:
WHAT COUNTS AS VIABILITY STATE

from:
its own ability to keep future function reachable.

This is highly exploratory.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
viability_dimensions = 5
candidate_actions = 10
contexts = 7
synthetic_decisions = 50000
lexicographic_mean_regret = 0.0023
