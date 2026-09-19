TITLE: DG-1A-AR-H114 — Residual-Only Perception / Predictive-Coding Bandwidth Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE MODEL-FIT-GATED RESIDUAL-CODING RESULT + GLOBAL RESIDUAL-STORM FAILURE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh113-credentialled-emergency-wave-audit.ice

PURPOSE
H108-H110 create:
coarse context
plus:
local exception handling.

H114 asks:

SHOULD LOCAL TISSUE TRANSMIT:
FULL STATE

or:

ONLY
WHAT THE CURRENT COARSE MODEL
FAILED TO PREDICT?

Candidate architecture:

TOP-DOWN / SHARED PREDICTION

+

LOCAL RESIDUAL PULSES.

The critical failure is:

WHAT IF
THE SHARED PREDICTION ITSELF
BECOMES WRONG?

BOUNDARY
This is synthetic.

It does not:
- freeze binary residual coding;
- freeze the global mismatch threshold;
- establish real hardware bandwidth;
- prove perfect residual delivery;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TISSUE
20 x 20.

400 local states.

STREAM
1,000 steps.

0..299

global context:
0.

300..499

global context:
0

plus:
one persistent local 5 x 5 anomaly
with context:
1.

500..699

whole tissue shifts:
to context 1.

700..999

whole tissue returns:
to context 0.

LOCAL OBSERVATION NOISE
Approximately:
2%
of cell states
flip
each step.

COMPARATORS

FULL-STATE BROADCAST

Every cell transmits:
every step.

FIXED BLOCK COMPRESSION

4 x 4 block majority summary.

RESIDUAL CODING
FIXED SHARED MODEL

Shared prediction remains:
context 0.

A cell transmits only if:
its actual state
differs from:
the shared prediction.

MODEL-FIT-GATED RESIDUAL CODING

Same residual scheme.

But:
if:
more than 60%
of tissue
disagrees with:
the shared prediction

for:
3 consecutive steps,

the coarse prediction is:
re-estimated
from:
current tissue majority.

One coarse-update event
is sent.

PRIMARY CONFIRMATION
300 matched streams.

FULL STATE

messages:
400,000.

reconstruction accuracy:
100%.

FIXED BLOCK

messages:
25,000.

accuracy:
96.90%.

PRIMARY FIXED-COMPRESSION RESULT
A fixed low-resolution summary
strongly reduces:
bandwidth

but:
throws away:
local detail.

RESIDUAL FIXED SHARED MODEL

total messages:
~89,605.

accuracy:
100%.

PHASE MESSAGE COUNTS

ordinary phase:
~2,399.

local-anomaly phase:
~6,397.

global-shift phase:
~78,401.

return:
~2,397.

PRIMARY RESIDUAL POSITIVE
When:
the shared prediction fits,

normal communication becomes:
very sparse.

A local anomaly costs:
only:
local residual traffic.

The whole organism does not need:
full-state transmission.

GLOBAL RESIDUAL-STORM NEGATIVE
When:
the shared context changes globally

but:
the prediction remains:
old,

almost every cell becomes:
a residual transmitter.

During:
the 200-step global shift,

~78.4k messages
are emitted.

Thus:

PREDICTIVE CODING
CAN BECOME
A BANDWIDTH STORM

when:
the shared prediction
has:
lost model fit.

MODEL-FIT-GATED RESIDUAL CODING

total messages:
~15,114.

accuracy:
100%.

coarse context updates:
2.

mean update times:

global 0 -> 1:
step 502.

global 1 -> 0:
step 702.

Thus:
approximately:
3 observations
after:
each global context transition.

PHASE MESSAGES

ordinary:
~2,399.

local anomaly:
~6,397.

global shift:
~2,752.

return:
~3,549.

PRIMARY MODEL-FIT POSITIVE
The model-fit gate reduces:
global-shift residual traffic

from:

~78,401
to
~2,752.

Overall communication falls:

400,000
full-state

->
15,114
adaptive residual.

Reduction:
approximately 96.2%.

The toy retains:
perfect reconstruction
because:
every residual bit
is assumed:
delivered.

LOCAL ANOMALY DOES NOT REWRITE GLOBAL CONTEXT
The 5 x 5 local exception affects:
only:
6.25%
of tissue.

It raises:
local residual traffic

but:
does not cross:
the global fit threshold.

Therefore:
the shared model remains:
global context 0.

This is:
the correct behavior.

A local exception should not:
rewrite:
organism-wide prediction.

SCALE-APPROPRIATE MODEL FIT
H114 therefore needs:
fit
at:
the same scale
as:
the prediction being challenged.

LOCAL residual density:
may justify:
local context split.

GLOBAL residual density:
may justify:
global model update.

Do not collapse:
those two.

RELATION TO H108
H108:
coarse representations should form
only where:
local evidence supports:
homogeneity.

H114:
once coarse representation exists,
its continued authority
must depend on:
ongoing fit.

RELATION TO H109
H109:
top-down context is:
a prior,
not:
an absolute veto.

H114:
top-down prediction is:
a compression codebook,
not:
a permanent truth.

When:
fit fails,
the codebook must:
change.

RELATION TO H62-H64
Residuals are naturally:
sparse event-like signals

rather than:
continuously maintained fields.

Thus:
H114 provides:
a potential information substrate
for:
H62-H64 adaptive signaling.

GENERAL PRINCIPLE
COMMUNICATE:

SURPRISE,

NOT:

EVERYTHING.

But:

WHEN
EVERYTHING
IS SURPRISING,

DO NOT:
MAKE EVERY CELL
SHOUT FOREVER.

QUESTION:
IS THE WORLD SURPRISING

or

IS THE MODEL
WRONG?

DECISION
AR-H114 is POSITIVE WITH A GLOBAL RESIDUAL-STORM FAILURE.

Supported synthetically:

- residual-only communication drastically reduces traffic when shared predictions fit;
- local anomalies remain local communication events;
- a stale shared model creates organism-wide residual storms;
- scale-appropriate model-fit can detect global prediction failure;
- updating the shared prediction restores sparse residual communication;
- adaptive residual coding strongly outperforms full-state broadcast in the tested stream.

Not demonstrated:

- lossy residual transport;
- analog/high-dimensional residuals;
- learned prediction models;
- local residual compression;
- message collision;
- real bandwidth/latency.

NEXT HIGH-VALUE MOVE
AR-H115 — RESIDUAL HABITUATION / LOCAL EXCEPTION MODEL BIRTH

H114 still sends:
the SAME local anomaly residual
every step.

Question:

if:
a local exception persists,

should:
that residual itself
become:
a new local predictive model

so:
communication becomes quiet again?

Candidate process:

persistent residual
->
local context candidate
->
validation
->
local exception model

while:
the global model remains:
unchanged.

Compare:

A.
keep transmitting:
persistent residual forever;

B.
global model rewrite;

C.
local exception model birth;

D.
transient anomaly
that should NOT:
earn local model memory;

E.
local anomaly moves
to:
a different region.

Desired:

PERSISTENT SURPRISE
should:
become:
LOCAL KNOWLEDGE.

TRANSIENT SURPRISE
should:
remain:
an event.

This would connect:
H114 predictive coding
with:
H98 model birth
and
H102 context splitting.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
grid = 20x20
stream_steps = 1000
matched_streams = 300
full_state_messages = 400000
fixed_residual_messages = 89605
adaptive_residual_messages = 15114
