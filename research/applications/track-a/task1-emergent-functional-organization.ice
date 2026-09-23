TITLE: YGGDRASIL TASK-1 — Emergent Local Service Organization Under Perturbation
DATE: 2026-09-22
STATUS: PREREGISTERED / FIRST POST-SUBSTRATE TASK-BEARING EXPERIMENT / NON-CANONICAL
TRACK: DG-1 / TASK-1
PARENT SUBSTRATE: DEVELOPMENTAL SUBSTRATE V0
BRANCH: dg1a-ar

NAMING NOTE

TASK-1 here means
the first task-bearing experiment
after DEVELOPMENTAL SUBSTRATE V0.

It is distinct from
the historical A07 / Training T1 label,
which tested supervised
experience-dependent hereditary learning.

TASK-1 does not reopen A07
and does not claim a learned updater.

PURPOSE

Test whether
an initially similar
cellular population

running the frozen
hand-designed developmental substrate

can organize useful computation
under changing local demand
and bounded perturbation

without permanent manual role assignment.

The required functional chain is:

SENSE
->
PROCESS
->
ROUTE
->
VERIFY
->
REPAIR.

The central comparison is:

dynamic local functional allocation

versus

a conventional fixed-role controller

with the same cell count,
same task programs,
same arrivals,
same topology,
same corruption events,
and same lesion schedule.

SUBSTRATE BINDING

DEVELOPMENTAL SUBSTRATE V0:

92654adf407310a01e368e2c53934beae749482c.

V0 architecture record:

research/architecture/developmental-substrate-v0.ice.

A53 closure parent:

a9f8472da56ae749393a1e281bcf27a8e3da3763.

TASK-1 uses V0 unchanged.

PRIMARY V0 FAMILY

D2.

Reason:

TASK-1 is an adaptation /
reorganization experiment.

D2 is selected before
any TASK-1 primary execution
as the shorter frozen
refractory family.

D3 is not a hidden
post-result alternate.

A later D3 replication,
if justified,
must be separately preregistered.

OPTIONAL RECOVERY LAYER

G5_FULL:

OFF.

TASK-1 first asks
what the frozen core substrate
can do without adding
the optional recovery layer.

G5_FULL may not be enabled
after seeing TASK-1 results.

A later G5 comparison,
if justified by a recovery-specific failure,
must be separately preregistered.

EXCLUDED MECHANISMS

No A49 challenge push-pull.

No A51 TTL field memory.

No A52 fixed phase delay.

No A53 vetoed phase memory.

No new recovery threshold.

No new persistence knob.

No new radius.

No learned NCA updater.

No dynamic topology.

No resource economy.

No long-term role DNA.

No Byzantine-cell machinery.

No central planner.

CELL POPULATION

64 cells.

All cells begin
with the same task capability set.

No cell begins
with a permanent task role.

No cell index
may encode a role.

No lineage identifier
may encode a role.

No hidden role table
may be consulted
by the emergent arm.

TOPOLOGY

Fixed one-dimensional ring.

Modulo-neighbor semantics.

This preserves
the inherited bounded local topology class.

TASK-1 changes population size
from the pulse benchmark's 48
to 64 cells,

but does not change
the topology rule.

V0 local radii remain unchanged.

TASK PROGRAM

Each request carries:

a four-bit input;

a task-program identifier;

a direction:

C
or
S;

a creation epoch;

a unique deterministic request identifier.

The PROCESS operation
uses the generic
four-bit truth-table interpreter
already established
in Application Track A:

input_index =
a
| (b << 1)
| (c << 2)
| (d << 3).

output =
(program >> input_index) & 1.

TASK-1 primary truth tables
must not be hand-selected
after execution.

The implementation harness
must freeze first.

Let the exact TASK-1
implementation freeze commit be:

T1F1.

After T1F1 exists,
derive four balanced,
non-constant,
non-affine
16-bit truth tables
deterministically from T1F1.

Bind them in
the TASK-1 manifest
before primary execution.

No program replacement
after execution begins.

TASK FLOW

There are two directional
job streams:

C stream;

S stream.

Each stream has
an ingress anchor
and an egress anchor
on the 64-cell ring.

C jobs move clockwise.

S jobs move counterclockwise.

Ingress / egress anchors
are environment locations.

They are not cell roles.

Cells near an anchor
are not permanently assigned
to that function.

REQUEST LIFECYCLE

Every request moves through:

RAW;

SENSED;

PROCESSED;

ROUTING;

AT_EGRESS;

VERIFIED;

DONE.

A verification failure creates:

REPAIR_PENDING.

Successful repair returns to:

AT_EGRESS

for independent re-verification.

A request may never skip:

SENSE;

PROCESS;

VERIFY.

ROUTE may consist
of multiple local hop operations.

REPAIR occurs only
after a failed verification.

SENSE

A RAW request exists
only at its ingress anchor.

A local eligible cell
may SENSE it.

SENSE copies
the immutable request payload
into the local task packet.

The request's original
four input bits
and program identifier
remain immutable provenance
for later verification / repair.

PROCESS

A SENSED request
may be processed
by any locally eligible cell
matching its C/S stream commitment.

PROCESS evaluates
the frozen generic truth-table interpreter.

The computed output bit
is stored in the task packet.

ROUTE

A processed request
moves one ring edge
per ROUTE operation

in its stream direction.

No teleportation.

No global path lookup.

No dense message broadcast.

No cell may read
future destination state.

The packet knows:

its stream direction;

whether its local position
is the egress anchor.

That is sufficient
for local forwarding.

VERIFY

At egress,
an eligible local cell
recomputes the expected bit

from:

immutable original input;

frozen program identifier.

VERIFY compares
the recomputed bit
to the processed packet bit.

The verifier does not receive
an evaluator correctness label.

If equal:

VERIFIED -> DONE.

If unequal:

REPAIR_PENDING.

REPAIR

A REPAIR_PENDING request
is locally recomputed
from its immutable provenance.

The repaired output
must then pass VERIFY again.

REPAIR may not
restore a saved full phenotype.

It repairs only
the task packet.

TASK CORRUPTION

After PROCESS
and before final VERIFY,

a deterministic stateless
corruption schedule
may flip the processed output bit.

Corruption identity
is common across all arms.

Corruption probability:

5%.

The corruption schedule
is derived post-T1F1
from the bound task seed.

No sequential RNG cursor.

No arm-specific corruption stream.

TASK DEMAND PHASES

160 epochs.

Exactly five
32-epoch phases.

PHASE 0
epochs 0-31:

balanced C/S arrivals;

initial ingress / egress anchors;

no lesion.

Purpose:

steady-state organization.

PHASE 1
epochs 32-63:

C-heavy demand:

C:S arrival ratio = 3:1.

Same anchors.

Purpose:

test demand-responsive
functional allocation.

PHASE 2
epochs 64-95:

S-heavy demand:

C:S arrival ratio = 1:3.

Same anchors.

Purpose:

test reversal
of functional demand
without retuning.

PHASE 3
epochs 96-127:

balanced arrivals.

At epoch 96,
apply a 12-epoch
functional lesion
to one deterministic
8-cell contiguous ring block.

Lesioned cells:

continue frozen V0
internal state updates;

cannot execute task operations;

cannot carry task packets
during the lesion.

At epoch 108
task execution capacity returns.

The lesion block
is derived post-T1F1
and is identical across arms.

Purpose:

test local rerouting,
functional replacement,
and post-lesion recovery.

PHASE 4
epochs 128-159:

balanced arrivals.

Rotate both stream
ingress / egress anchor pairs
by exactly 16 ring positions.

No task role map
is rotated in the fixed-role arm.

Purpose:

test whether useful function
can reorganize spatially
when environmental demand moves.

ARRIVAL LOAD

Six requests per epoch.

Balanced phases:

3 C;
3 S.

C-heavy phase:

approximately
3:1 C:S
under a deterministic
epoch-level schedule
that preserves six total arrivals.

S-heavy phase:

the exact directional mirror.

The exact per-epoch
arrival sequence
must be bound
in the post-T1F1 manifest.

No load tuning
after primary execution.

EMERGENT FUNCTIONAL ALLOCATION

The emergent arm
does not store
a permanent task-role variable.

A cell's observed role
for an epoch
is simply the operation
it executes:

SENSE;

PROCESS;

ROUTE;

VERIFY;

REPAIR;

or IDLE.

All task-capable cells
share the same operation policy.

A cell may execute
at most one task operation
per epoch.

Operation selection
uses only:

the frozen V0 local cell state;

local task packets;

local task anchor marker,
when physically at an anchor;

local packet waiting age;

local stream direction;

and stateless tie-breaking.

No global queue length.

No global throughput.

No future phase identifier.

No context/family shortcut.

If multiple local operations
are eligible,

select the operation
belonging to the oldest
local request.

Ties are resolved
by stateless hash
from:

task seed;

epoch;

cell position;

request identifier;

operation identifier.

Thus no permanent role
is assigned.

Functional specialization,
if it appears,
must arise from:

local demand;

ring position;

cellular state;

and the evolving task workload.

TASK-TO-SUBSTRATE EVIDENCE

Local C-stream
unserved demand
contributes only
to the local C evidence channel.

Local S-stream
unserved demand
contributes only
to the local S evidence channel.

The mapping is frozen
before T1F1.

It must use
the existing V0 evidence interface.

It may not change:

B update law;

rho;

local radii;

ECHO_PHASE;

Hill law;

refractory semantics;

recruitment law.

The task adapter
supplies evidence.

V0 remains authoritative
for cellular state transition.

FIXED-ROLE CONTROL

Same 64 cells.

Same D2 V0 state evolution.

Same task programs.

Same arrivals.

Same corruption schedule.

Same lesion block.

Same anchors.

Same one-operation-per-cell-per-epoch
task capacity.

But task operation eligibility
is permanently assigned
before primary execution.

The fixed controller
uses exactly:

4 SENSE cells;

4 PROCESS cells;

48 ROUTE cells;

4 VERIFY cells;

4 REPAIR cells.

The role map
is optimized only
from known pipeline mechanics
before any primary result:

SENSE cells
are placed at initial ingress anchors;

VERIFY cells
at initial egress anchors;

PROCESS cells
adjacent to ingress anchors;

REPAIR cells
adjacent to egress anchors;

ROUTE cells
fill all remaining positions.

Direction eligibility
is split symmetrically
between C and S.

The fixed role map
does not adapt
to Phase 1 demand skew,
Phase 2 reversal,
Phase 3 lesion,
or Phase 4 anchor rotation.

This is the
assigned-role comparator.

NO-REPAIR CAUSAL CONTROL

A third arm:

EMERGENT_NO_REPAIR.

Identical to
EMERGENT_V0

except:

REPAIR_PENDING requests
cannot be repaired
and eventually expire.

Purpose:

prove whether
the REPAIR operation
causally contributes
to end-to-end resilience.

No other behavior changes.

PRIMARY ARMS

Exactly three:

EMERGENT_V0;

EMERGENT_NO_REPAIR;

FIXED_ROLE.

No additional primary arm
after T1F1.

REQUEST EXPIRY

A request expires
if it remains unfinished
for 32 epochs.

Expiry is failure.

No retry outside
the local REPAIR mechanism.

PRIMARY METRICS

For each arm and phase report:

arrivals;

correct DONE count;

incorrect DONE count;

expired count;

completion fraction;

correct-completion fraction;

median end-to-end latency;

p90 latency;

operations per correct completion;

queue backlog;

maximum local backlog.

For corrupted requests report:

corruption count;

verification-detected count;

repaired count;

correctly completed after repair;

repair latency.

For lesion / shift transitions report:

pre-event completion rate;

minimum post-event completion rate;

epochs to recover
90% of the pre-event
moving completion rate;

post-event backlog area;

cells newly performing
each operation.

FUNCTIONAL ORGANIZATION METRICS

Use rolling
16-epoch windows.

For every cell report:

count of each operation;

dominant operation;

dominant-operation fraction;

operation entropy.

Population report:

number of active cells
per operation;

number of operations
represented by at least
four active cells;

median dominant-operation fraction;

spatial concentration
for each operation;

fraction of cells
whose dominant operation changes
after demand reversal;

fraction changing
after lesion;

fraction changing
after anchor rotation.

These metrics measure
functional differentiation.

They do not create
a task-role state.

ASSIGNED-VS-EMERGENT INFORMATION GAIN

TASK1_EMERGENT_ORGANIZATION_GAIN = TRUE iff
all are satisfied:

1. EMERGENT_V0
   correct-completion fraction
   in Phase 0
   is at least 95%
   of FIXED_ROLE;

2. across Phases 1-4,
   EMERGENT_V0
   correct-completion area
   is at least 10%
   higher than FIXED_ROLE;

3. after Phase 2
   demand reversal,
   EMERGENT_V0 returns to
   at least 90%
   of its Phase-0
   correct-completion rate
   within 8 epochs;

4. after Phase 3 lesion,
   EMERGENT_V0 returns to
   at least 90%
   of its Phase-0
   correct-completion rate
   within 8 epochs
   after lesion onset
   or demonstrates
   a strictly smaller
   backlog area than FIXED_ROLE;

5. after Phase 4
   anchor rotation,
   EMERGENT_V0
   correct-completion fraction
   over the final 16 epochs
   is at least 85%;

6. at least 25%
   of active cells
   change dominant operation
   between the final Phase-0 window
   and the final Phase-4 window;

7. at least three
   distinct task operations
   are represented by
   at least four active cells
   in the final Phase-0 window
   and final Phase-4 window;

8. incorrect DONE count = 0;

9. operations per correct completion
   does not exceed
   125%
   of FIXED_ROLE
   over the full run;

10. all integrity probes pass.

REPAIR INFORMATION GAIN

TASK1_REPAIR_GAIN = TRUE iff:

1. at least 95%
   of injected corruptions
   reaching egress
   are detected by VERIFY;

2. at least 90%
   of detected corruptions
   in EMERGENT_V0
   are correctly completed
   after REPAIR
   before expiry;

3. EMERGENT_V0
   correct-completion fraction
   exceeds EMERGENT_NO_REPAIR
   by at least
   3 percentage points
   over corrupted requests;

4. incorrect DONE count = 0;

5. repair does not increase
   non-corrupted-request
   median latency
   by more than 10%
   versus EMERGENT_NO_REPAIR;

6. all integrity probes pass.

TASK-1 QUALIFICATION

TASK1_QUALIFIED = TRUE iff:

TASK1_EMERGENT_ORGANIZATION_GAIN = TRUE;

and

TASK1_REPAIR_GAIN = TRUE;

and

full-run correct-completion fraction
for EMERGENT_V0 >= 90%;

and

final Phase-4
correct-completion fraction >=85%;

and

incorrect DONE count = 0;

and

no forbidden global information
enters cellular decisions.

This is the first
task-bearing qualification.

It is not a claim
of general intelligence.

INTEGRITY PROBES

P1:
exact V0 parent commit.

P2:
D2 selected before primary.

P3:
G5_FULL OFF.

P4:
64 cells.

P5:
fixed ring topology.

P6:
V0 B update unchanged.

P7:
V0 ECHO_PHASE unchanged.

P8:
V0 refractory semantics unchanged.

P9:
V0 radii unchanged.

P10:
no A49 push-pull.

P11:
no A51 TTL.

P12:
no A52/A53 phase memory.

P13:
no permanent task-role state
in EMERGENT_V0.

P14:
all emergent cells
share identical operation policy.

P15:
no cell index encodes a role.

P16:
no global queue length
enters cell decisions.

P17:
no global performance metric
enters cell decisions.

P18:
no future phase identifier
enters cell decisions.

P19:
generic truth-table interpreter only.

P20:
four task programs
derived only after T1F1.

P21:
program manifest bound
before primary execution.

P22:
arrival manifest bound
before primary execution.

P23:
corruption manifest bound
before primary execution.

P24:
lesion block bound
before primary execution.

P25:
same task manifestations
across all arms.

P26:
same task RNG identities
across all arms.

P27:
stateless RNG only.

P28:
same one-operation-per-cell
capacity across arms.

P29:
FIXED_ROLE map frozen
before primary.

P30:
FIXED_ROLE map never adapts.

P31:
NO_REPAIR differs
only in repair availability.

P32:
VERIFY never reads
external correctness labels.

P33:
REPAIR uses only
immutable request provenance.

P34:
no saved full phenotype restoration.

P35:
two complete mechanical sweeps
byte-identical before T1F1.

P36:
T1F1 exists
before primary task programs.

P37:
post-T1F1 manifest
bound before primary execution.

P38:
two complete primary runs
byte-identical
before scientific interpretation.

MECHANICAL GATE

Before T1F1:

prove V0 parent identity;

prove 64-cell ring mechanics;

prove all three arms;

prove fixed-role counts;

prove identical arrivals
across arms;

prove identical corruption
across arms;

prove request lifecycle;

prove no stage skipping;

prove route one-hop semantics;

prove verification recomputation;

prove repair re-verification;

prove expiry;

prove no permanent emergent role;

prove local-only operation selection;

prove no forbidden global input;

prove two complete
mechanical sweeps byte-identically.

Mechanical worlds
must not be interpreted scientifically.

FREEZE DISCIPLINE

After the mechanical gate:

freeze implementation as T1F1.

Then derive:

task programs;

task seed;

arrival schedule;

corruption schedule;

lesion block;

initial anchors;

from T1F1.

Bind one manifest
before primary execution.

Then run
two complete primaries
byte-identically.

Only after duplicate identity
may TASK-1 scientific metrics
be opened.

NO POST-RESULT TUNING

Do not change
after results:

role counts;

task programs;

arrival load;

phase lengths;

lesion size;

lesion duration;

anchor rotation;

corruption rate;

expiry;

operation-selection law;

qualification thresholds;

D family;

G5 status;

or V0 dynamics.

FAILURE ATTRIBUTION

If EMERGENT_V0
fails Phase 0
before perturbation:

diagnose the task interface
or service-capacity design
before blaming developmental organization.

Do not tune V0 first.

If Phase 0 is strong
but demand reversal fails:

the hand-designed substrate
does not reorganize task allocation
fast enough under shifted demand.

If lesion recovery fails
but demand reversal succeeds:

the failure is recovery-specific.

That would justify
a separately preregistered
G5_FULL comparison.

If anchor rotation fails
while demand reversal succeeds:

functional allocation is adaptable
but spatial organization
is too position-bound.

Do not add dynamic topology
inside TASK-1.

If REPAIR does not outperform
NO_REPAIR:

the verify/repair loop
does not create useful resilience
under this task.

If EMERGENT_V0
matches or beats FIXED_ROLE
through perturbations
with bounded cost:

the frozen cellular substrate
has crossed from
mechanism-only behavior
into useful task organization.

NEXT-STAGE RULE

A successful TASK-1
does not immediately authorize
a learned NCA.

It supplies the empirical requirements
for the later learned updater:

which local observations matter;

which task-state abstractions matter;

which role transitions matter;

which communication bottlenecks matter;

which repair signals matter;

and which invariants
must remain hard constraints.

A failed TASK-1
also does not automatically
invalidate Yggdrasil.

It localizes the next question to:

task interface;

communication;

functional role allocation;

repair;

or substrate dynamics.

PLAIN-SPEAK QUESTION

We are finally asking
the organism to do work.

Every cell starts
with the same capabilities.

Nobody is permanently told:

"you are the sensor,"

"you are the processor,"

"you are the router,"

"you are the verifier,"

or

"you are the repair cell."

Jobs arrive locally.

The job itself
has to move through:

see it;

compute it;

move it;

check it;

fix it if it was corrupted.

We then change
which direction needs more work,

damage part of the tissue,

and move the places
where work enters and exits.

The fixed controller
keeps its assigned jobs.

The cellular organism
is allowed to reorganize
only through local information
and the frozen V0 dynamics.

The question is:

CAN THE SAME LOCAL ORGANISM
REASSIGN WHO DOES WHAT

FAST ENOUGH
TO KEEP USEFUL WORK MOVING

WITHOUT A CENTRAL SCHEDULER?

That is TASK-1.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
