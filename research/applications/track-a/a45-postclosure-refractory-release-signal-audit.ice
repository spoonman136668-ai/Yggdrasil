TITLE: YGGDRASIL A45 POST-CLOSURE DIAGNOSTIC — REFRACTORY RELEASE SIGNAL AUDIT
DATE: 2026-09-22
STATUS: POST-CLOSURE OBSERVATIONAL GATE AUDIT / NO DYNAMICS CHANGE
PARENT DIAGNOSTIC: 8f67b4aa0a04eb5f140714dc2e482b4b24a925b9
PARENT CLOSURE: d99afa1aefcba407aaf6522f0ba6660f6783381d
F45: c9207c0fd0034160ea546db5e367cda84f5bc1c0
PRIMARY SEED: A45-F45-c9207c0fd0034160ea546db5e367cda84f5bc1c0-PRIMARY
BRANCH: dg1a-ar

PURPOSE

Before changing refractory behavior,
measure whether already-existing
local signals can distinguish:

temporary 5:3 recovery
where former-side participation
should plausibly resume;

from:

true reversal,
balanced periodic noise,
and persistent opposition.

No cell is released early
in this diagnostic.

The A45 dynamics are replayed unchanged.

AUDITED ARMS

D2_ECHO_PHASE.

D3_ECHO_PHASE.

OBSERVATION TIMING

For every FC / FS cell
before the ordinary refractory release step,
record:

former commitment side;

remaining refractory timer;

pre-current-evidence signed margin M_pre;

post-current-evidence signed margin M_post;

current local SUPPORT / CHALLENGE / NEUTRAL mode
relative to the former side;

current raw same-side cooperative field Q_raw;

current environment relation
for diagnostic labeling only.

The environment label
is not part of any candidate cell-local gate.

LOCKED CELL

A refractory cell is LOCKED
when remaining timer > 0.

FIRST LOCKED EPOCH

The first refractory observation
after defection is:

timer = D.

This allows separation of
immediate-release pressure
from later recovery opportunities.

OBSERVATIONAL GATES

Five zero-parameter candidate gates
were evaluated without applying them:

G1 SUPPORT_ONLY:

local mode = SUPPORT.

G2 SUPPORT_MPRE:

local mode = SUPPORT
and M_pre > 0.

G3 SUPPORT_MPOST:

local mode = SUPPORT
and M_post > 0.

G4 SUPPORT_MPRE_Q:

local mode = SUPPORT
and M_pre > 0
and Q_raw > 0.

G5 SUPPORT_MPOST_Q:

local mode = SUPPORT
and M_post > 0
and Q_raw > 0.

G5 is the most conservative
current-evidence candidate.

It requires:

current local support;

current signed evidence
already realigned with the former side;

and at least one positive
same-side cooperative contribution
inside the existing radius.

No threshold,
gain,
new radius,
global phase,
or context identity is used.

5:3 FAVORED-SIDE RECOVERY

D2_ECHO_PHASE

All locked favored-former-side recovery observations:

n = 3293.

Local mode SUPPORT:

100.00%.

M_post > 0:

83.15%.

Q_raw > 0:

29.64%.

G5 SUPPORT_MPOST_Q:

29.64%.

Recovery step 1:

locked n = 1825.

SUPPORT:

100.00%.

M_post > 0:

69.59%.

Q_raw > 0:

0.00%.

G5:

0.00%.

Thus the conservative gate
does not release cells
on the first support epoch.

Recovery step 2:

locked n = 1457.

M_post > 0:

100.00%.

Q_raw > 0:

66.37%.

G5:

66.37%.

Recovery step 3:

locked n = 7.

G5:

85.71%.

D3_ECHO_PHASE

All locked favored-former-side recovery observations:

n = 4811.

SUPPORT:

100.00%.

M_post > 0:

87.51%.

Q_raw > 0:

44.13%.

G5:

44.13%.

Recovery step 1:

locked n = 1789.

M_post > 0:

66.52%.

Q_raw > 0:

0.00%.

G5:

0.00%.

Recovery step 2:

locked n = 1681.

M_post > 0:

99.88%.

Q_raw > 0:

59.85%.

G5:

59.85%.

Recovery step 3:

locked n = 1328.

M_post > 0:

100.00%.

Q_raw > 0:

83.28%.

G5:

83.28%.

INTERPRETATION OF 5:3 TIMING

The conservative gate
naturally waits through
the first recovery epoch.

At that point,
the former-side cell may already
have a positive current signed margin,
but the nearby committed core
has not yet rebuilt enough
to provide positive Q_raw.

By the second support epoch,
both conditions commonly exist.

Thus G5 is not
an immediate refractory bypass.

It is an evidence-and-cooperation
confirmation rule.

TRUE REVERSAL SAFETY AUDIT

For refractory cells
whose former side is the OLD side
after a genuine reversal:

D2 locked observations:

n = 12876.

local SUPPORT:

0.00%.

M_post > 0:

0.00%.

G1 through G5:

0.00%.

D3 locked observations:

n = 18946.

local SUPPORT:

0.00%.

M_post > 0:

0.00%.

G1 through G5:

0.00%.

Therefore the frozen true-reversal worlds
provide complete observational separation:

the proposed conservative gate
never asks an old-side refractory cell
to return early after genuine reversal.

BALANCED-PERIODIC SAFETY AUDIT

D2:

locked observations n = 13307.

SUPPORT_ONLY fires:

50.70%.

SUPPORT_MPOST fires:

34.19%.

G5 SUPPORT_MPOST_Q fires:

3.54%.

On FIRST locked epoch:

n = 6727.

SUPPORT_ONLY:

47.12%.

SUPPORT_MPOST:

35.08%.

G5:

0.178%.

D3:

locked observations n = 18432.

SUPPORT_ONLY fires:

60.75%.

SUPPORT_MPOST fires:

45.31%.

G5 fires:

5.98%.

On FIRST locked epoch:

n = 6296.

SUPPORT_ONLY:

46.98%.

SUPPORT_MPOST:

36.39%.

G5:

0.302%.

Thus SUPPORT alone
is far too permissive
under balanced periodic evidence.

Adding current signed-margin positivity
is still too permissive.

Requiring positive current
same-side cooperative support
suppresses most balanced-periodic
early-release opportunities.

NONPERIODIC AUDIT

Across constant and spatial/nonperiodic contexts:

D2 G5 fires
on 20.64%
of locked refractory observations.

D3 G5 fires
on 20.20%.

This aggregate includes
spatially heterogeneous worlds
where local former-side support
can legitimately differ by region.

CONSTANT-ENVIRONMENT CHECK

When the former side
matches the constant environment:

D2:

locked n = 26;
G5 = 73.08%.

D3:

locked n = 24;
G5 = 83.33%.

When the former side
opposes the constant environment:

D2:

locked n = 3274;
G5 = 0.00%.

D3:

locked n = 4926;
G5 = 0.00%.

This is the desired directional behavior.

CANDIDATE SIGNAL RESULT

G1 SUPPORT_ONLY is rejected
as an A46 candidate.

Balanced-periodic firing
is approximately 51-61%.

G3 SUPPORT_MPOST is also rejected
as insufficiently selective.

Balanced-periodic firing
is approximately 34-45%.

G5:

local SUPPORT
AND
M_post > 0
AND
Q_raw > 0

is the justified candidate.

It:

does not fire
on the first 5:3 support epoch;

fires strongly
on support recovery epochs 2-3;

fires 0%
for the old side after true reversal;

fires 0%
for a former side opposing
a constant environment;

and has much lower
balanced-periodic exposure.

CAUSAL HYPOTHESIS FOR A46

The refractory mechanism
is valuable immediately after defection
because it prevents chatter.

But once all three
existing local signals agree:

1. current local evidence
supports the former side;

2. the cell's signed evidence state
has crossed back in favor
of the former side;

3. a currently committed
same-side neighborhood exists;

continued mandatory refractory delay
may no longer be serving
its anti-chatter purpose.

A46 should therefore test
EARLY RELEASE TO U ONLY

under G5.

It must not directly recommit
the cell to its former side.

Normal U recruitment
must still make the commitment decision.

PLAIN-SPEAK INTERPRETATION

We found a signal
that looks selective enough to test.

Simply saying:

"the neighborhood supports
what I used to believe"

is much too loose.

Balanced noisy worlds
would trigger that constantly.

Even adding:

"and my own evidence
has turned positive again"

still fires too often
in balanced worlds.

But one more requirement
changes the picture:

there must already be
a real committed core nearby
supporting that same side.

Then the cell is not reacting
to one noisy reading.

Its own evidence has recovered,
its local environment agrees,
and an actual same-side organization
has reappeared around it.

In the 5:3 recovery,
that signal usually does not exist
during the first support epoch.

It appears during the second,
exactly while many cells
are still being forced
to sit out by the refractory timer.

After a real reversal,
the old side never sees
this three-part signal.

So A46 has a clean question:

IF A REFRACTORY CELL
IS ALREADY LOCALLY RE-SUPPORTED,
HAS RE-ALIGNED ITS OWN EVIDENCE,
AND HAS A REAL SAME-SIDE CORE NEARBY,

CAN IT RETURN TO U EARLY
WITHOUT REINTRODUCING CHATTER
OR BLOCKING GENUINE REVERSAL?

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
