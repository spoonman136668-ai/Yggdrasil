TITLE: DG-1A-AR-H105 — Temporal Observable Morphogenesis / Memory-Bearing Sensor Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE RECRUITED-TEMPORAL-SENSOR RESULT + PERMANENT-HISTORY COST LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh104-derived-sensor-synthesis-audit.ice

PURPOSE
H104 constructs:
instantaneous derived observables.

H105 asks:

WHAT IF
THE MISSING CONTEXT
DOES NOT EXIST
IN
THE CURRENT INSTANTANEOUS STATE?

Can:
MEMORY ITSELF

be recruited as:
a small sensing organ?

BOUNDARY
This is synthetic.

It does not:
- freeze one-step memory;
- prove autoregressive context is the final temporal representation;
- freeze temporal-state costs;
- establish production recurrent architecture;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

LATENT MODE
Binary hidden context.

Outcome success:

Z=0:
0.88.

Z=1:
0.35.

RAW SIGNAL
Current scalar:

x_t.

In BOTH latent modes:

x_t
has approximately:
standard-normal marginal distribution.

Therefore:
one instantaneous sample
cannot:
identify
the hidden mode.

TEMPORAL STRUCTURE
The modes differ only in:
lag relationship.

Z=0:

corr(x_t, x_(t-1))
≈
+0.78.

Z=1:

corr(x_t, x_(t-1))
≈
-0.78.

Thus:
CONTEXT IS DYNAMICAL.

CANDIDATE OBSERVABLES

INSTANTANEOUS

x_t.

current unrelated noise.

TEMPORAL

x_t * x_(t-1).

|x_t - x_(t-1)|.

sign agreement.

two-lag product.

three-lag mean product.

noise lag product.

Each temporal feature pays:
synthetic state / compute cost.

PRIMARY AUDITION
100 training events.

100 validation events.

600 deployment events.

3,000 matched synthetic trials.

INSTANTANEOUS-ONLY SENSORIUM

mean validation gain:
+0.00035.

deployment gain:
-0.00171.

net after sensing cost:
-0.00271 / event.

PRIMARY INSTANTANEOUS NEGATIVE
The latent context is:
not present
in:
the instantaneous marginal.

No amount of:
current-only threshold tuning

creates:
the missing temporal information.

RECRUITED TEMPORAL SENSOR

mean validation gain:
+0.02959.

deployment gain:
+0.02203.

net:
+0.01793 / event.

PRIMARY TEMPORAL POSITIVE
A tiny amount of:
local state

turns:
an unobservable instantaneous context

into:
a useful observable.

Frequently selected candidates include:

SIGN AGREEMENT
~38.2%.

THREE-LAG MEAN PRODUCT
~23.3%.

ONE-LAG PRODUCT
~17.9%.

TWO-LAG PRODUCT
~9.3%.

ABSOLUTE LAG DIFFERENCE
~9.5%.

Thus:
several small temporal encodings
can expose:
the same hidden dynamic.

INDIVIDUAL FEATURE NET VALUES
Approximate deployment information value
after:
feature-specific cost.

THREE-LAG MEAN PRODUCT:
+0.01859.

SIGN AGREEMENT:
+0.01817.

ONE-LAG PRODUCT:
+0.01784.

TWO-LAG PRODUCT:
+0.01587.

ABSOLUTE LAG DIFFERENCE:
+0.01318.

CURRENT X:
-0.00349.

CURRENT NOISE:
-0.00350.

NOISE-LAG PRODUCT:
-0.00559.

PRIMARY MEMORY-DEPTH RESULT
Longer history can:
improve predictive structure

but:
the gain is:
small
and
not monotonic
after:
state cost.

One-step or short-window memory
captures:
most of the available context.

PERMANENT FULL-HISTORY CONTROL
A multivariate temporal model keeps:
all tested instantaneous
and
history-derived state active.

Primary full-history state cost:
0.025 / event.

1,500 matched deployments.

Raw predictive gain:
approximately +0.01768 / event.

Net after:
permanent history/state cost:

-0.00732 / event.

PRIMARY PERMANENT-HISTORY NEGATIVE
The richest temporal sensorium
is:
worse

after:
resource cost

than:
a single recruited temporal observable.

Thus:

MEMORY
SHOULD NOT
AUTOMATICALLY BE:
PERMANENTLY MAXIMAL.

TEMPORAL MEMORY AS SENSOR STATE
H105 suggests:
history state can be treated like:
a sensor.

A local process may carry:

HISTORY DEPTH

+

CURRENT INFORMATION VALUE

+

ACTIVE STATE COST

+

FIT / FRESHNESS

+

DORMANT / ACTIVE MEMORY STATUS.

This is:
different
from:
keeping a large generic recurrent state
everywhere.

RELATION TO H103
H103:
choose:
which variable
is worth sensing.

H105:
choose:
whether:
PAST STATE
is itself:
worth sensing.

Thus:
the sensorium can recruit:

SPACE

VALUE TRANSFORMS

and
TIME.

RELATION TO H44
H44:
local version leases create:
bounded persistence.

H105:
temporal observation also benefits from:
bounded retained state.

Do not infer:
infinite memory
from:
one useful lag.

RELATION TO H80
H80:
permanent executable grammar
must be:
memory priced.

H105:
permanent temporal sensor state
must also be:
memory priced.

The same resource law applies to:
cognition
and
observation.

GENERAL PRINCIPLE
IF:
CURRENT STATE
DOES NOT EXPLAIN
PERSISTENT RESIDUALS,

THE ORGANISM MAY NEED
TO OBSERVE:

HOW STATE IS CHANGING.

But:

TEMPORAL DEPTH
SHOULD GROW
ONLY WHILE
ITS INFORMATION VALUE
REPAYS:
STATE COST.

DECISION
AR-H105 is POSITIVE WITH A PERMANENT-HISTORY COST LIMIT.

Supported synthetically:

- latent context can exist entirely in temporal dependence while instantaneous marginals are identical;
- instantaneous sensing fails in that case;
- small recruited temporal memory exposes useful context;
- several short temporal observables work;
- additional history has diminishing value;
- permanently maintaining all tested temporal history becomes net harmful after state cost.

Not demonstrated:

- temporal sensor birth online;
- irregular/asynchronous event time;
- very long memory;
- memory compression;
- spatial-temporal joint observables;
- interaction with dormancy.

NEXT HIGH-VALUE MOVE
AR-H106 — COLLECTIVE OBSERVABLE / DISTRIBUTED SENSOR MORPHOGENESIS

H105 discovers:
hidden state from:
one cell's recent history.

A cellular organism can also face context that exists only in:
SPATIAL RELATION.

Question:

what if:
every cell's local scalar
has:
the same marginal distribution,

but:
the hidden mode changes:
neighbor correlation / spatial coherence?

No single cell can infer:
the context
from:
its own value.

Candidate observables:

nearest-neighbor agreement.

local covariance.

short-range contrast.

small neighborhood vote.

Compare:

A.
cell-autonomous sensing;

B.
global centralized field readout;

C.
two-hop local collective sensor;

D.
communication cost;

E.
localized context where:
different tissue regions
occupy:
different modes.

Desired:

PERCEPTION
can become:
a distributed tissue computation

without:
a global observer.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_lag_correlation = 0.78
primary_matched_trials = 3000
primary_temporal_net_per_event = 0.017933
full_history_net_per_event = -0.007316
