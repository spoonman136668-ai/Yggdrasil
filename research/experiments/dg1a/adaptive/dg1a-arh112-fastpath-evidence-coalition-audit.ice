TITLE: DG-1A-AR-H112 — Fast-Path Evidence Coalition / Copy-Stuffing Resistance Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE FAILURE-FAMILY COALITION RESULT + MESSAGE-COUNT VOTE-STUFFING FAILURE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh111-learned-fast-path-authority-audit.ice

PURPOSE
H111 credentials:
one urgency signal.

H112 asks:

WHAT IF
DIFFERENT URGENT EVENTS
ARE VISIBLE
TO DIFFERENT SIGNAL FAMILIES?

Can:
several low-duty signals
form:
temporary evidence coalitions

without:
letting:
copied alarms
stuff the vote?

BOUNDARY
This is synthetic.

It does not:
- freeze the number of evidence families;
- freeze naïve-Bayes aggregation;
- prove family provenance is always known;
- establish final fast-action utility;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

URGENT EVENT RATE
Approximately:
5.5%.

URGENT SUBTYPES

A-family event:
45%.

B-family event:
45%.

X cross-family event:
10%.

LOCAL FAST GATE
Fast action still requires:
a separate local corroboration signal.

Urgent sensitivity:
~0.78.

ordinary false activation:
~0.07.

FAST-ACTION VALUE
Correct urgent override:
+5.

False override:
-0.7.

EVIDENCE FAMILIES

FAMILY A

root alarm A1.

Strong on:
A events.

Moderate on:
cross-family X.

weak baseline false-positive.

A2,
A3,
A4

are:
high-fidelity copies
of:
A1.

They are NOT:
independent evidence.

FAMILY B

root:
B1.

Strong on:
B events.

Moderate on:
X.

B2:
highly related copy.

FAMILY C

C1:
independent,
rare,
high-specificity consequence signal

with:
moderate sensitivity
across:
all urgent event types.

PRIMARY TRAIN / TEST
300 matched runs.

20,000 training events.

50,000 fresh test events.

COMPARATORS

SINGLE BEST SIGNAL

Choose:
A1,
B1,
or
C1

from:
training utility.

SIMPLE MESSAGE MAJORITY

Count:
all alarm messages.

Fast support if:
at least 3
of:
7 messages
are active.

MESSAGE-LEVEL NAIVE EVIDENCE

Treat:
every message
as:
independent evidence.

FAILURE-FAMILY EVIDENCE

Collapse:
A copies
into:
one A-family evidence variable.

Collapse:
B copies
into:
one B-family variable.

C remains:
its own independent family.

Then:
combine:
family evidence.

SINGLE BEST
Selected:

B1:
155 / 300 runs.

A1:
142.

C1:
3.

Mean incremental value:
0.09675 / event.

overall urgent capture:
36.42%.

subtype capture:

A:
34.98%.

B:
37.50%.

X:
37.47%.

PRIMARY SINGLE-SIGNAL LIMIT
No one signal family
covers:
the full urgent-event ecology.

Selecting:
one historically best alarm

leaves:
large blind regions.

SIMPLE MESSAGE MAJORITY

value:
0.13516.

urgent capture:
50.57%.

false-fast rate:
0.542%.

Subtype capture:

A:
67.39%.

B:
34.68%.

X:
46.53%.

PRIMARY MAJORITY BIAS
Because:
A-family has:
more copied messages,

simple vote count
creates:
more authority
for:
A evidence

without:
more independent information.

The urgent-event ecology becomes:
representation-count biased.

MESSAGE-LEVEL EVIDENCE
With:
the baseline copied-message set

value:
0.18913.

urgent capture:
71.56%.

false-fast:
1.093%.

subtype:

A:
72.21%.

B:
72.07%.

X:
66.37%.

At this baseline,
naïve message evidence
looks:
excellent.

COPY-STUFFING ATTACK
Add:

5 exact copies
of:
A1.

They contain:
zero new information.

The message-level inference engine
is retrained
with:
those messages
as if:
they were separate evidence.

RESULT

value:
0.14448.

urgent capture:
54.09%.

false-fast:
0.593%.

subtype A:
69.06%.

subtype B:
39.83%.

subtype X:
50.97%.

PRIMARY COPY-STUFFING NEGATIVE
Adding:
zero-information copies

changes:
the system's emergency behavior.

B-family capture falls:

~72.1%
->
~39.8%.

The evidence system has been:
vote-stuffed
by:
one failure family.

This is:
not acceptable authority accounting.

FAILURE-FAMILY COALITION

value:
0.18797.

urgent capture:
71.99%.

false-fast:
1.443%.

subtype:

A:
72.56%.

B:
72.51%.

X:
67.06%.

PRIMARY FAMILY-COALITION POSITIVE
Aggregating:
independent failure families

rather than:
message count

produces:
balanced urgent coverage.

Exact duplicate A messages:
do not create:
a new family

and therefore:
do not increase:
A's epistemic authority.

The family-aware result
is structurally unchanged
by:
copy stuffing.

FALSE-POSITIVE TRADEOFF
The primary family policy
has:
slightly higher
false-fast activation

than:
the naïve message model
at its baseline.

Thus:
provenance-aware evidence
is not:
automatically lower-cost.

Its key advantage is:
AUTHORITY STABILITY
under:
evidence duplication.

Threshold / stake tuning remains:
a separate problem.

CROSS-FAMILY EVENT
X events are:
only moderately visible
to:
A
and
B
individually.

Combining:
independent family support

raises:
cross-family capture
to:
~67%.

Thus:
temporary coalitions
can detect:
events
that:
no one signal
owns.

RELATION TO H18
H18:
multiple context messages
sharing:
one failure mode

do not create:
independent evidence.

H112:
multiple urgency messages
sharing:
one root alarm

do not create:
more emergency authority.

RELATION TO H40
H40:
copied canaries
must not:
multiply validation.

H112:
copied alarms
must not:
multiply fast-path voting weight.

Same architectural law.

RELATION TO H86
H86:
future-option diversity
needs:
multiple independent axes.

H112:
fast evidence diversity
also needs:
failure-family structure.

GENERAL PRINCIPLE
COUNT:

INDEPENDENT EVIDENCE PATHS,

NOT:

MESSAGES.

Fast authority should grow from:

FAILURE-MODE DIVERSITY

+

CURRENT CREDENTIAL

+

EVENT STAKE

not:
raw alarm multiplicity.

DECISION
AR-H112 is POSITIVE WITH A MESSAGE-COUNT VOTE-STUFFING FAILURE.

Supported synthetically:

- different urgent event families require different signals;
- one best alarm leaves large blind spots;
- simple majority is biased by duplicated alarm families;
- naïve message-level inference can be corrupted by exact copies;
- failure-family aggregation is stable to copy stuffing;
- independent signal families can form useful temporary evidence coalitions;
- cross-family events benefit from combined evidence.

Not demonstrated:

- learned failure-family clustering;
- adversarial forged provenance;
- continuous coalition membership;
- dynamic event stakes;
- propagation of coalition authority;
- real urgent actions.

NEXT HIGH-VALUE MOVE
AR-H113 — CREDENTIALLED EMERGENCY WAVE / PANIC-CONTAINMENT AUDIT

H110-H112 establish:
local fast authority.

H62 and H77 establish:
event-wave propagation.

Question:

if:
a locally credentialed urgent event
needs:
neighbor response,

how far should:
fast authority propagate?

Compare:

A.
global broadcast;

B.
unconditional relay wave;

C.
provenance-preserving wave;

D.
local relevance / viability-gated relay;

E.
false credentialled source;

F.
real expanding emergency.

Desired:

LOCAL EMERGENCY
->
FAST LOCAL COORDINATION

without:

ORGANISM-WIDE PANIC.

A cell should relay:
urgent authority
only if:
the event is:
locally relevant
or:
credible evidence indicates
the threat is:
approaching.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
matched_runs = 300
train_events = 20000
test_events = 50000
family_coalition_value = 0.18797
family_coalition_capture = 0.71986
copy_stuffed_message_capture = 0.54087
