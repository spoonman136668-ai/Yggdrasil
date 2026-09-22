TITLE: YGGDRASIL FUTURE LINEAGE NOTE — A42 / A43 / A44
DATE: 2026-09-22
STATUS: NON-BINDING FUTURE HYPOTHESES / NOT A PREREGISTRATION
TRACK: YGGDRASIL TRAINING / APPLICATION-A
CURRENT ACTIVE FRONTIER: A41 / T8Y
BRANCH: dg1a-ar

PURPOSE

Preserve three post-A41 hypotheses
without changing A41,
without creating F42/F43/F44,
and without allowing future mechanisms
to leak into the active A41 experiment.

A41 remains the sole active experiment.

No A42, A43, or A44 implementation is authorized
by this note.

No thresholds,
gains,
kernels,
or arm sets are frozen here.

DIRECTION 1 — A42 ACTIVE CORE RECRUITMENT

PLAIN QUESTION

Can a surviving veteran core
actively recruit nearby uncertain cells
toward its own commitment,
rather than only suppress recruitment
toward the opposition?

CAUSAL STRUCTURE TO TEST AFTER A41 CLOSES

A41 exclusion alone:
does blocking opposition suffice?

A42 active recruitment alone:
does attracting support suffice?

A41 + A42:
does simultaneous negative and positive signaling
produce a push-pull mechanism
that neither component can produce alone?

KEY HYPOTHESIS

If the combined arm breaks oscillators
that neither mechanism alone breaks,
the relevant mechanism is synergistic:

barrier plus magnet.

The core both:

reduces local rebuilding of the opposing population;

and increases local rebuilding of its own population.

EVIDENCE-DEPTH QUESTION

Recruitment strength may be weighted
by the committed neighbor's aligned support margin M.

If margin weighting improves active recruitment
relative to occupancy-only recruitment,
evidence depth has a second causal use:

not only persistence,
but outward recruitment signaling.

BIOLOGICAL ANALOGY

Honeybee nest-site decisions combine
positive waggle-dance recruitment
with inhibitory stop signaling.

This is analogy and hypothesis support only.

The Yggdrasil M-weighting
is an engineering hypothesis;
the biological literature does not directly establish
a Yggdrasil-equivalent support-margin variable.

PARAMETER DISCIPLINE

Do not introduce an arbitrary fitted delta
after A41 results.

At A42 preregistration,
prefer a normalization tied to existing constants
or freeze one new gain before implementation.

Do not tune recruitment strength
after seeing A42 outcomes.

DIRECTION 2 — A43 COOPERATIVE CORE REINFORCEMENT

PLAIN QUESTION

Does a committed cell become more stable
because nearby same-side veterans
reinforce the commitment?

This differs from:

A30:
opposition-driven committed-state inhibition;

A41:
periphery recruitment exclusion;

A42:
positive recruitment of U cells.

A43 would modify
committed-to-committed reinforcement.

BIOLOGICAL ANALOGY

The PU.1 / GATA-1 lineage-switch literature
supports a broader design principle:

a downstream program can feed back
and reinforce an upstream commitment decision,
and weakening that feedback can restore reversibility.

This does not imply a literal mapping
from FOG-1 to spatial neighbor reinforcement.

ENGINEERING CAUTION

Do not implement reinforcement
as an unconstrained additive term directly on p_stay.

That can create clipping artifacts
and obscure causal attribution.

At A43 preregistration,
choose one bounded transformation
that preserves p_stay in [0,1]
without post-result tuning.

CRITICAL-DENSITY HYPOTHESIS

A cooperative core may exhibit
a density-dependent stability threshold.

Above the threshold:
same-side neighbors reinforce one another
and the core survives a short counter-pulse.

Below it:
reinforcement collapses
and defection can propagate.

Measure this explicitly
rather than inferring it from final majority alone.

DIRECTION 3 — A44 PHASE-DEPENDENT LOCAL SIGNALING

PLAIN QUESTION

Should the same surviving core
recruit when local evidence supports it
and defend when local evidence opposes it?

SUPPORT MODE:
positive active recruitment.

OPPOSITION MODE:
recruitment exclusion.

This would combine
A41 and A42 conditionally
rather than applying both identically at all times.

IMPORTANT LOCALITY GUARD

A44 must not read
a hidden global environmental phase label.

That would introduce an oracle
and violate the distributed architecture.

Mode switching must be derived
from locally available current evidence
relative to the cell's present commitment,
using only information already available
to the cell.

No future environment may be consulted.

HYPOTHESIZED CYCLE

support evidence:
core grows;

counter-pulse:
core defends;

next support interval:
surviving core starts larger
than it would under passive dynamics.

This could create a net positive
core-size balance over a full cycle
without central coordination.

ORDER OF OPERATIONS

Finish A41 first.

Then, if still justified by A41:

A42:
active recruitment / push-pull test.

A43:
cooperative committed-core reinforcement.

A44:
local phase-dependent switching
between recruitment and defense.

Do not skip directly to A44.

Each experiment should add
one causal behavior at a time.

CURRENT PLAIN-SPEAK LINEAGE

A41:
the core learns to HOLD THE LINE.

A42:
the core learns to RECRUIT.

A43:
the core learns to REINFORCE ITSELF.

A44:
the core learns to RECRUIT WHEN SUPPORTED
and DEFEND WHEN CHALLENGED.

The long-range target remains:

local;
distributed;
evidence-sensitive;
reversible under genuine change;
without a central judge.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
