TITLE: YGGDRASIL A46 / T9D — Cooperative-Confirmed Refractory Re-entry
DATE: 2026-09-22
STATUS: PREREGISTERED RECOVERY-CONTROL EXPERIMENT / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T9D / APPLICATION-A
PARENT: A45 One-Epoch Cooperative Support Echo
PHENOTYPE PARENT: A45 Uncertainty / Refractory Cycle Diagnostic
GATE PARENT: A45 Refractory Release Signal Audit
BRANCH: dg1a-ar

AUTHORITATIVE PARENTS

A45 closure:

d99afa1aefcba407aaf6522f0ba6660f6783381d.

A45 uncertainty / refractory diagnosis:

8f67b4aa0a04eb5f140714dc2e482b4b24a925b9.

A45 refractory release signal audit:

aea0c2a10c0700f39509bf3b8f3455d50edb81a2.

A parallel later diagnostic note
considered the less selective
SUPPORT + M_post gate.

A46 does not use that weaker gate.

The governing audit is the earlier
three-signal gate audit above
because it provides substantially better
balanced-periodic separation.

A45 RESULT RELEVANT TO A46

A45 materially improves
third-hit core survival
without producing wrong-side capture.

In frozen 5:3 worlds:

direct favored-to-adverse majority flips = 0;

adverse-majority entries = 0;

post-epoch-8 adverse-majority epochs = 0.

The inherited oscillator detector
is primarily counting:

favored majority
-> unresolved
-> favored majority.

At 5:3 adverse-burst end,
approximately 45-47%
of the ECHO_PHASE population
can be refractory.

Thus the residual problem
is recovery latency,
not wrong-side pulse chasing.

GATE AUDIT RESULT

The local zero-threshold gate:

G5
=
local SUPPORT
AND
M_post > 0
AND
Q_raw > 0

has the following observational behavior.

5:3 favored recovery:

D2 locked recovery observations:
G5 = 29.64%.

D3:
G5 = 44.13%.

Recovery step 1:

D2 G5 = 0.00%.
D3 G5 = 0.00%.

Recovery step 2:

D2 G5 = 66.37%.
D3 G5 = 59.85%.

Recovery step 3:

D2 G5 = 85.71%.
D3 G5 = 83.28%.

True reversal old-side refractory cells:

D2 G5 = 0.00%.
D3 G5 = 0.00%.

Balanced-periodic locked cells:

D2 G5 = 3.54%.
D3 G5 = 5.98%.

Balanced-periodic first locked epoch:

D2 G5 = 0.178%.
D3 G5 = 0.302%.

Therefore G5 naturally waits
through the first recovery epoch
and tends to appear
only after both cell-internal
and neighborhood evidence have rebuilt.

QUESTION

Once a refractory cell has:

1. current local evidence
   supporting its former side;

2. positive post-update signed margin
   for that former side;

3. positive current raw cooperative support
   from committed neighbors
   on that former side;

can it safely return to U
before its fixed refractory timer expires?

Does that reduce
favored -> unresolved -> favored cycling

without:

creating wrong-side majority capture;

manufacturing a majority
under balanced evidence;

increasing chatter pathologically;

or resisting genuine reversal?

F46 FREEZE

Let the exact A46 implementation freeze commit be F46.

No real A46 world,
population result,
or scientific comparison
may be derived before F46 exists.

WORLD SHAPE

384 fresh post-F46 trials.

48 contexts x 8 replicas.

48 cells.

48 epochs.

Environmental families remain structurally identical
to A45.

PARENT DYNAMICS

Use A45 ECHO_PHASE unchanged
except for the explicit refractory re-entry rule
in the G5 arm.

Preserve:

A36 ecology;

A40 signed temporal state;

A43 margin cooperation;

A44 local SUPPORT / CHALLENGE / NEUTRAL mode;

A44 support-gated active recruitment;

A45 one-epoch non-recursive cooperative echo.

No A37 lineage state exists.

REFRACTORY STATES

Committed C defection:

C -> FC.

Committed S defection:

S -> FS.

Fixed parent refractory duration:

D2 = 2.

D3 = 3.

Parent behavior remains unchanged
in control arms.

A46 G5 RE-ENTRY SNAPSHOT

The G5 decision occurs
after current signed-B update
and before ordinary refractory timer processing.

For every currently locked
FC or FS cell i:

former side s
=
C for FC;
S for FS.

Read:

M_post(i,s)
=
aligned margin
from the already-updated
current signed B.

Read:

mode(i,s)
=
the existing A44 local
SUPPORT / CHALLENGE / NEUTRAL mode
relative to former side s.

Read:

Q_raw(i,s)
=
the existing A43 raw
margin-weighted cooperative field
from currently committed same-side neighbors
within radius 3.

The snapshot is current-state local information only.

No future evidence.

No environment-family identity.

No global phase.

No majority label.

G5

gate_G5(i)
=
1

iff all are true:

cell i is FC or FS;

remaining refractory timer > 0;

mode(i,s) = SUPPORT;

M_post(i,s) > 0;

Q_raw(i,s) > 0.

Otherwise:

gate_G5(i) = 0.

G5 ACTION

If gate_G5(i) = 1:

state_i := U;

timer_i := 0.

This is EARLY RE-ENTRY TO U ONLY.

The cell is not directly recommitted
to former side s.

The cell enters the ordinary
same-epoch U recruitment stage
and must pass the existing
A34/A35/A36/A44 recruitment machinery
like any other eligible U cell.

No favored-side recruitment bonus
is added specifically for released cells.

No direct memory of former side
enters the recruitment decision.

If gate_G5(i) = 0:

use the parent A45 refractory timer
exactly unchanged.

NEW COMMITMENT TRACE

If an early-released cell
is subsequently recruited
to C or S in the same epoch:

it is a new commitment.

Its A45 cooperative echo trace starts at zero,
exactly like every other newly recruited commitment.

No old cooperative echo crosses
through refractory re-entry.

ARMS

Exactly four arms.

D2:

D2_ECHO_PHASE;
D2_G5_REENTRY.

D3:

D3_ECHO_PHASE;
D3_G5_REENTRY.

No SUPPORT-only arm.

No M_post-only arm.

No Q-only arm.

No fixed timer-shortening arm.

No direct recommitment arm.

No threshold arm.

No gain arm.

No new radius.

RNG DISCIPLINE

Inherited ECHO_PHASE controls
must reproduce A45 exactly.

D2_ECHO_PHASE and D3_ECHO_PHASE
retain the A45 RNG namespace and arm identity.

New G5_REENTRY arms use:

YGG-A46-ARM-SEED.

G5 itself is deterministic.

PRIMARY TARGET

Primary causal target:

5:3 contexts 46 and 47.

Preserve full reporting
for all 48 contexts.

BALANCED CONTROL

Contexts:

40;
41;
42;
43.

TRUE REVERSAL CONTROL

Preserve all A45 reversal contexts
and reversal metrics.

WRONG-SIDE PHENOTYPE METRICS

For contexts 46/47 report:

direct favored-to-adverse majority flips;

adverse-majority entries;

adverse-majority epochs;

maximum consecutive adverse-majority duration.

A46 must not reduce
unresolved cycling
by enabling wrong-side capture.

UNRESOLVED-CYCLE METRICS

For contexts 46/47 report:

favored-to-unresolved transitions;

unresolved-to-favored transitions;

number of unresolved episodes;

duration of each unresolved episode;

mean unresolved episode duration;

median unresolved episode duration;

maximum unresolved episode duration;

favored-majority recovery latency
after every adverse burst.

Retain the inherited oscillator metric
for lineage comparability.

REFRACTORY RECOVERY METRICS

At adverse-burst end
and support-recovery steps 1 through 5 report:

favored committed fraction;

adverse committed fraction;

U fraction;

H fraction;

FC fraction;

FS fraction;

total refractory fraction;

total unresolved fraction.

G5 MECHANISM METRICS

For every locked refractory observation report:

former side;

remaining timer;

local mode;

M_post;

Q_raw;

G5 true/false;

whether early re-entry occurred;

whether same-epoch recruitment occurred;

same-epoch recruited side if any.

Aggregate separately for:

5:3 recovery;

balanced periodic;

true reversal old side;

nonperiodic contexts.

For G5 early re-entries report:

fraction recruited same epoch;

fraction joining former side;

fraction joining opposite side;

fraction remaining U/H;

time until next defection if recommitted.

CHATTER SAFETY

Report per arm:

total commitment defections;

total commitments;

number of cells with
commit -> refractory -> U -> same-side commit -> defect
within 4 epochs;

number of cells with
opposite-side recommitment
within 4 epochs;

mean commitment dwell time;

median commitment dwell time.

TRUE REVERSAL SAFETY

For old-side refractory cells
during the first four epochs
after true reversal report:

G5 opportunities;

G5 fires;

early re-entries;

same-epoch old-side recommitments.

Desired:

zero G5 fires
for old-side refractory cells
during this window.

BALANCED SAFETY

Report:

G5 fire rate;

early-reentry rate;

false-majority rate;

majority residence duration;

C-majority epochs;

S-majority epochs;

unresolved epochs;

chatter metrics.

A46_RECOVERY_INFORMATION_GAIN

TRUE iff at least one G5_REENTRY arm
satisfies all:

1. mean 5:3 unresolved-episode duration
   is at least 25% lower
   than paired ECHO_PHASE;

2. mean 5:3 favored-majority recovery latency
   is at least 1 epoch lower
   than paired ECHO_PHASE;

3. mean refractory fraction
   across support-recovery steps 1-3
   is lower than paired ECHO_PHASE;

4. direct favored-to-adverse majority flips
   remain zero
   in 5:3 worlds;

5. adverse-majority entries
   remain zero
   in 5:3 worlds;

6. reversal acquisition >= 80%;

7. balanced false-majority <= 10%;

8. aggregate service >= 90%
   of paired ECHO_PHASE;

9. all integrity probes pass.

A46 QUALIFICATION

D2_G5_REENTRY
or
D3_G5_REENTRY

is A46-QUALIFIED iff all are true:

1. overall inherited oscillator rate <= 5%;

2. 5:3 inherited oscillator rate <= 25%;

3. 5:3 favored-to-unresolved transitions
   are reduced at least 50%
   versus paired ECHO_PHASE;

4. mean 5:3 unresolved-episode duration
   is reduced at least 50%
   versus paired ECHO_PHASE;

5. median favored-majority recovery latency
   after an adverse burst <= 2 epochs;

6. direct favored-to-adverse majority flips = 0;

7. adverse-majority entries = 0;

8. balanced false-majority <= 10%;

9. reversal acquisition >= 80%;

10. median old-majority loss <= 4 epochs;

11. aggregate service >= 90%
    of paired ECHO_PHASE;

12. G5 fires = 0
    for old-side refractory cells
    during the first four post-reversal epochs;

13. same-side short-cycle chatter
    does not exceed
    125% of paired ECHO_PHASE;

14. all integrity probes pass.

FAILURE ATTRIBUTION

If G5 materially shortens
unresolved recovery
without adverse-majority capture:

fixed refractory debt
was a real residual bottleneck.

If G5 fires appropriately
but unresolved duration barely changes:

refractory cells are not
the dominant recovery bottleneck
once they become eligible.

If G5 shortens recovery
but balanced false-majority rises:

the gate is too permissive
under ambiguous evidence.

If G5 causes old-side re-entry
after true reversal:

the gate does not safely distinguish
temporary displacement
from genuine environmental change.

If early-released cells
mostly remain U
or fail recruitment:

the remaining bottleneck
is recruitment capacity,
not refractory availability.

If early-released cells
recommit and immediately defect:

the refractory timer
was preventing real chatter,
and the recovery rule is premature.

INTEGRITY PROBES

P1:
384 trials.

P2:
48 contexts x 8 replicas.

P3:
48 cells.

P4:
48 epochs.

P5:
A45 parent dynamics unchanged
outside refractory re-entry.

P6:
D2 fixed parent refractory D = 2.

P7:
D3 fixed parent refractory D = 3.

P8:
G5 uses current local mode only.

P9:
G5 uses post-update signed margin only.

P10:
G5 uses current raw cooperative field only.

P11:
G5 requires Q_raw > 0.

P12:
G5 requires M_post > 0.

P13:
G5 requires mode SUPPORT.

P14:
G5 uses no threshold magnitude.

P15:
G5 uses no gain.

P16:
G5 uses no new radius.

P17:
G5 uses no majority label.

P18:
G5 uses no environment-family identity.

P19:
G5 uses no future evidence.

P20:
early re-entry goes to U only.

P21:
normal U recruitment decides any recommitment.

P22:
early-released cells receive no special recruitment bias.

P23:
new commitments start A45 echo trace at zero.

P24:
no old echo crosses refractory re-entry.

P25:
parent refractory timer is unchanged
when G5 is false.

P26:
A45 ECHO_PHASE controls
reproduce parent behavior.

P27:
no A37 lineage state exists.

P28:
two complete mechanical sweeps
are byte-identical before F46.

P29:
F46 exists before real worlds are derived.

P30:
post-F46 world manifest is bound
before primary arm execution.

P31:
two complete primary sweeps
are byte-identical.

RESEARCH DISCIPLINE

Mechanical fake-world validation
must pass twice byte-identically
before F46.

Focused ECHO_PHASE parent parity
must pass before F46.

F46 must exist
before fresh A46 primary worlds are derived.

The 384-world manifest
must be bound after F46
and before primary arm execution.

No post-result:

gate threshold;

timer length;

recruitment gain;

radius;

arm;

qualification rule;

or world-family tuning.

PLAIN-SPEAK QUESTION

A45 stopped
the dangerous kind of flipping
in the 5:3 worlds.

The organism usually does not
join the wrong side anymore.

Instead,
many recently displaced cells
are forced to sit out
while the correct side
is already rebuilding.

A46 asks:

when one of those benched cells
can see that:

its old side is supported again;

its own evidence
has turned back toward that side;

and a real committed core
has re-formed nearby;

does it still need
to serve the rest
of its fixed waiting period?

A46 does not
put it straight back
on the old team.

It only lets the cell
stand up and become undecided again.

Then the normal local recruitment system
has to convince it
like any other uncertain cell.

The test is whether
that evidence-confirmed plasticity
lets the organism recover faster

without bringing back
the very chatter and wrong-side instability
the refractory state was created to prevent.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F46 AMENDMENT 01 — G5 COOPERATIVE-FIELD TIMING PARITY

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F46
AND BEFORE ANY A46 SCIENTIFIC OUTCOME.

AUDIT TIMING

The A45 refractory release signal audit
computed G5 cooperative support as:

Q_raw(i,s)
=
the existing A43 raw
margin-weighted cooperative field

using:

the current committed-neighbor state snapshot

and

the pre-current-evidence signed margins B_pre.

The same audit computed:

M_post(i,s)

from the already-updated
current signed state B_post.

A46 must preserve this asymmetry exactly.

Therefore G5 reads:

mode:
current local evidence;

M_post:
post-update current cell signed margin;

Q_raw:
current committed-neighbor topology
weighted by B_pre margins.

RATIONALE

Using B_post inside Q_raw
would allow the current evidence sample
to strengthen both:

the cell's own M_post;

and its neighbors' cooperative field

inside the same re-entry decision.

That was not the audited signal
and would introduce same-epoch double counting.

No other A46 rule changes.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F46 IMPLEMENTATION / MECHANICAL BINDING

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F46
AND BEFORE ANY A46 SCIENTIFIC OUTCOME.

IMPLEMENTATION

Candidate source bytes:
78919.

Candidate source SHA256:
60ed341643ea8934d1ce360a841ebf5e5b272371aa686e0342b57b0071353493

Focused parent-parity audit:

D2_ECHO_PHASE:
zero mismatches.

D3_ECHO_PHASE:
zero mismatches.

Audited world classes included:
constant;
spatial;
true reversal;
balanced periodic;
6:2 biased periodic;
5:3 biased periodic.

G5 focused causal smoke:

early re-entry is active
in intended recovery worlds;

old-side true-reversal
early re-entry count = 0;

A45 trace-freshness probes all pass.

MECHANICAL VALIDATION

Mechanical seed:
MECHANICAL-A46-F46-CANDIDATE

Complete sweeps:
2.

Worlds per sweep:
384.

Arms:
4.

Output bytes per sweep:
49396.

Output SHA256:
07cb52b178972724d11182e3d244bd9e989aa990b0ae7b5f3974c2f6465a13dc

BYTE IDENTICAL:
true.

All executable integrity probes:
PASS.

D2_G5_REENTRY
old-side true-reversal early re-entry:
0.

D3_G5_REENTRY
old-side true-reversal early re-entry:
0.

No mechanical-world population outcome
is used as scientific evidence.

PUBLICATION PACKAGE

Exact source will be published
as deterministic gzip/base64
split into seven text chunks.

Source bytes:
78919.

Source SHA256:
60ed341643ea8934d1ce360a841ebf5e5b272371aa686e0342b57b0071353493

Gzip bytes:
18953.

Gzip SHA256:
db32e84ca763847ccb2a9475a5ecc500738f9f9a6767b4c80fa0b4dfe7521f51

Concatenated base64 characters:
25272.

Base64 SHA256:
59ea70f8142cee5489b0fc8ac973a036816cc2ed14595af442c794ecd7e83d12

Chunk count:
7.

The F46 loader must verify
all three identities
before execution.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


PRE-F46 AMENDMENT 02 — MECHANICAL GATE AND SOURCE-BUNDLE IDENTITY

DATE:
2026-09-22.

STATUS:
BOUND BEFORE F46
AND BEFORE ANY A46 SCIENTIFIC OUTCOME.

FOCUSED PARENT PARITY

A45 ECHO_PHASE parent behavior
was compared against A46 inherited controls
across 36 representative cases spanning:

constant environments;
spatial environments;
true reversal;
balanced periodic;
6:2 biased periodic;
5:3 biased periodic.

Behavioral mismatches:

0.

MECHANICAL VALIDATION

Candidate source SHA256:

efee5637a1ba709b5299199489f02988517abc49392788b72ea25b295119fcec

Mechanical seed:

MECHANICAL-A46-F46-CANDIDATE

Complete sweeps:

2.

Output bytes per sweep:

44606.

Output SHA256:

1ad8f436649825fae8a644c1260127fbe23d05e6ebf545578b4b07dec962c905

BYTE IDENTICAL:

true.

stderr:

empty for both sweeps.

All executable pre-primary integrity probes:

PASS.

No mechanical-world population outcome
is used as scientific evidence.

SOURCE-BUNDLE FORMAT

F46 will publish the exact candidate source
as a deterministic gzip/base64 source bundle
split into six text source parts.

Source bytes:

75169.

Source SHA256:

efee5637a1ba709b5299199489f02988517abc49392788b72ea25b295119fcec

Gzip bytes:

18136.

Gzip SHA256:

4e0d2b5ded1f71f55cf3e94652d52224c3bae10bfe9e308a6e101de44f4037f3

Concatenated base64 characters:

24184.

Base64 SHA256:

b6edfab88e74753d5d32c113ccee30941ce3421f9a15dc38664d25e214479a5b

The F46 loader must verify
all three identities
before execution.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


POST-F46 PRIMARY MANIFEST BINDING

DATE:
2026-09-22.

F46:
80c1673f5fccfe55e98e85a2dad8453b6ad3291e

SOURCE SHA256:
efee5637a1ba709b5299199489f02988517abc49392788b72ea25b295119fcec

PRIMARY SEED:
A46-F46-80c1673f5fccfe55e98e85a2dad8453b6ad3291e-PRIMARY

WORLD COUNT:
384.

WORLD SHAPE:
48 contexts x 8 replicas.

PRIMARY WORLD MANIFEST SHA256:
8f87ed0b890d299456ef693d66ee04a791e7885c5daf262c78c83c76b4b4657c

STATUS:
BOUND AFTER F46
AND BEFORE ANY PRIMARY ARM EXECUTION.

No A46 arm outcome,
population metric,
qualification result,
or scientific comparison
was observed before this binding.

P31 remains pending
until two complete primary sweeps
are byte-identical.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.


A46 PRIMARY CLOSURE

DATE:
2026-09-22.

F46:
80c1673f5fccfe55e98e85a2dad8453b6ad3291e

MANIFEST-BINDING COMMIT:
58bed4d9c2e75956c62b19ff81f026cd1d9a38d7

SOURCE SHA256:
efee5637a1ba709b5299199489f02988517abc49392788b72ea25b295119fcec

PRIMARY SEED:
A46-F46-80c1673f5fccfe55e98e85a2dad8453b6ad3291e-PRIMARY

PRIMARY WORLD MANIFEST SHA256:
8f87ed0b890d299456ef693d66ee04a791e7885c5daf262c78c83c76b4b4657c

PRIMARY OUTPUT SHA256:
53ff44daf08eae604d2801f23527b441e56280012dc8984e580864a19deddf5b

PRIMARY RUNS:
2.

PRIMARY OUTPUT BYTES:
44435.

BYTE IDENTICAL:
true.

P31:
PASS.

All executable integrity probes:
PASS.

A46_RECOVERY_INFORMATION_GAIN:
FALSE.

QUALIFICATION

D2_G5_REENTRY:
NOT QUALIFIED.

D3_G5_REENTRY:
NOT QUALIFIED.

TECHNICAL EVIDENCE

D2 ECHO_PHASE parent:

aggregate service 237801;
harm rate 15.36%;
overall inherited oscillation 5.99%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 3.12%;
reversal acquisition 89.06%;
median old-majority loss 3 epochs.

5:3 recovery:

favored-to-unresolved transitions 71;
unresolved-to-favored transitions 78;
mean unresolved episode 3.616 epochs;
median unresolved episode 3 epochs;
mean favored-majority recovery latency 4.580 epochs;
median recovery latency 3.5 epochs;
recovery-never count 8.

Mean refractory fraction
across recovery steps 1-3:

33.29%.

D2 G5_REENTRY:

aggregate service 237525;
harm rate 16.67%;
overall inherited oscillation 10.68%;
biased-periodic oscillation 93.75%;
5:3 oscillation 100.00%;
6:2 oscillation 87.50%;
balanced false-majority 0.00%;
reversal acquisition 92.97%;
median old-majority loss 2 epochs.

5:3 recovery:

favored-to-unresolved transitions 64;
unresolved-to-favored transitions 71;
mean unresolved episode 5.863 epochs;
median unresolved episode 5 epochs;
mean favored-majority recovery latency 6.253 epochs;
median recovery latency 4 epochs;
recovery-never count 9.

Mean refractory fraction
across recovery steps 1-3:

28.27%.

Thus G5 reduces
short-term refractory occupancy
but makes unresolved episodes
approximately 62% longer

and mean favored-majority recovery
approximately 37% slower.

D2 G5 mechanism:

early re-entries 3772;
same-epoch recruitments 1523;
same-epoch former-side commitments 981;
same-epoch opposite-side commitments 107;
same-epoch H entries 435.

Approximately:

40.38% of early re-entries
are recruited in the same epoch;

26.01% of all early re-entries
immediately recommit to the former side;

2.84% immediately commit
to the opposite side.

Same-side short-cycle chatter:

parent 632;
G5 932.

Mean commitment dwell:

parent 9.217 epochs;
G5 8.301 epochs.

D2 biased context detail:

parent:
44 = 0/8 oscillatory;
45 = 0/8;
46 = 8/8;
47 = 8/8.

G5:
44 = 8/8;
45 = 6/8;
46 = 8/8;
47 = 8/8.

Thus G5 destabilizes
the previously controlled 6:2 contexts.

D3 ECHO_PHASE parent:

aggregate service 234093;
harm rate 14.84%;
overall inherited oscillation 7.03%;
biased-periodic oscillation 50.00%;
5:3 oscillation 100.00%;
6:2 oscillation 0.00%;
balanced false-majority 0.00%;
reversal acquisition 87.50%;
median old-majority loss 3 epochs.

5:3 recovery:

favored-to-unresolved 67;
unresolved-to-favored 75;
mean unresolved episode 4.795 epochs;
median unresolved episode 4 epochs;
mean favored-majority recovery latency 6.000 epochs;
median recovery latency 4 epochs;
recovery-never count 8.

Mean refractory fraction
across recovery steps 1-3:

46.14%.

D3 G5_REENTRY:

aggregate service 233596;
harm rate 15.36%;
overall inherited oscillation 10.42%;
biased-periodic oscillation 100.00%;
5:3 oscillation 100.00%;
6:2 oscillation 100.00%;
balanced false-majority 0.00%;
reversal acquisition 88.28%;
median old-majority loss 2 epochs.

5:3 recovery:

favored-to-unresolved 55;
unresolved-to-favored 62;
mean unresolved episode 6.986 epochs;
median unresolved episode 5 epochs;
mean favored-majority recovery latency 7.941 epochs;
median recovery latency 5 epochs;
recovery-never count 11.

Mean refractory fraction
across recovery steps 1-3:

38.90%.

Thus G5 reduces
short-term refractory occupancy
but makes unresolved episodes
approximately 46% longer

and mean favored-majority recovery
approximately 32% slower.

D3 G5 mechanism:

early re-entries 5168;
same-epoch recruitments 2017;
same-epoch former-side commitments 1289;
same-epoch opposite-side commitments 157;
same-epoch H entries 571.

Approximately:

39.03% of early re-entries
are recruited in the same epoch;

24.94% immediately recommit
to the former side;

3.04% immediately commit
to the opposite side.

Same-side short-cycle chatter:

parent 0;
G5 334.

Mean commitment dwell:

parent 9.290 epochs;
G5 8.362 epochs.

D3 biased context detail:

parent:
44 = 0/8;
45 = 0/8;
46 = 8/8;
47 = 8/8.

G5:
44 = 8/8;
45 = 8/8;
46 = 8/8;
47 = 8/8.

WRONG-SIDE SAFETY

In both D2 and D3 G5:

5:3 direct favored-to-adverse majority flips = 0;

5:3 adverse-majority entries = 0;

5:3 adverse-majority epochs = 0.

Therefore G5 does not fail
by restoring wrong-side pulse chasing.

TRUE REVERSAL SAFETY

Old-side G5 fires
during the first four true-reversal epochs:

0.

Reversal acquisition remains:

92.97% D2;
88.28% D3.

Thus G5 also does not fail
by preserving the obsolete side.

BALANCED SAFETY

Balanced false-majority:

0.00% in both G5 arms.

Therefore the main failure
is not balanced majority capture.

CAUSAL INTERPRETATION

The A45 diagnosis was correct
that fixed refractory debt
contributes to temporary unresolved occupancy.

But A46 shows that
refractory debt is not simply removable latency.

The refractory interval
also provides temporal separation
between:

defection;

plasticity;

and recommitment.

G5 removes part of that separation.

The cell becomes U earlier,
and roughly 39-40%
of early re-entries
are recruited again immediately.

Approximately one quarter
of all early-released cells
recommit to their former side
in that same epoch.

The system therefore converts
some refractory debt
into faster commitment cycling.

The strongest evidence is:

short-term refractory occupancy falls;

yet unresolved episode duration rises;

commitment dwell shortens;

same-side short-cycle chatter rises;

and previously stable 6:2 contexts
become oscillatory.

This is not a wrong-side instability.

It is a plasticity-timing instability.

The refractory state was not merely
keeping useful cells on the bench.

It was also preventing
recently unstable cells
from re-entering the commitment process
before their local dynamics had settled.

NEXT JUSTIFIED DIAGNOSTIC

Do not strengthen G5.

Do not add a looser gate.

Do not shorten the timer globally.

Measure the trajectory
of every G5 early re-entry:

time of release relative
to environmental pulse phase;

same-epoch destination;

time to next commitment;

side of next commitment;

time to next defection;

whether refractory debt
is restarted;

and contribution
to favored -> unresolved -> favored cycling.

Compare:

G5 cells that remain U/H
for at least one full epoch

against:

G5 cells recruited
in the same epoch.

The immediate question is:

is SAME-EPOCH RECRUITMENT
the causal source
of the new chatter and 6:2 instability?

If yes,
a successor may test
evidence-confirmed early re-entry
with one epoch of plastic U
before recruitment eligibility.

That would separate:

ending refractory lock

from:

immediate recommitment.

No such mechanism is authorized
until the trajectory diagnostic confirms it.

PLAIN-SPEAK INTERPRETATION

A46 found that
the waiting period was doing
two jobs, not one.

We thought it was mostly
keeping useful cells sidelined
after the disturbance was over.

So we let well-supported cells
get off the bench early.

They did get off the bench.

But many of them
jumped straight back into play
in the same turn.

That created a new problem.

Some recommitted quickly,
became unstable again,
and ended up cycling
through commitment and recovery
more often.

So there were fewer cells
sitting in refractory state
at any one moment,

but the organism actually took
longer to settle.

Even the easier 6:2 disturbances,
which A45 handled cleanly,
started oscillating again.

The important safety result is:

the cells did not
start choosing the wrong side,

and they did not
fight a true reversal.

The problem is timing.

A cell may be ready
to stop being locked,

without being ready
to make another commitment
in that same instant.

The next thing to measure is whether
that immediate re-recruitment
is what causes the new instability.

If it is,
the next design should separate:

YOU MAY BECOME PLASTIC AGAIN

from:

YOU MAY IMMEDIATELY COMMIT AGAIN.

NORTH-STAR IMPLICATION

A46 identifies refractory state
as an active temporal coordination mechanism,
not just dead time.

Developmental plasticity therefore
appears to require
controlled staging:

commitment;

destabilization;

refractory reset;

plastic uncertainty;

then recommitment.

Compressing those stages
too aggressively
can increase global instability
even when every local decision
is evidence-aligned.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
