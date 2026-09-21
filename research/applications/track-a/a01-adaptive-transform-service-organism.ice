TITLE: YGGDRASIL APPLICATION TRACK A — A01 Adaptive Transform-Service Organism
DATE: 2026-09-20
STATUS: PREREGISTERED / FIRST PERSISTENT STANDALONE APPLICATION PROTOTYPE
TRACK: APPLICATION-A / PERSISTENT SYNTHETIC ORGANISM
BRANCH: dg1a-ar
RESEARCH GATE: DG-1R-05AC PASSED

PURPOSE

DG-1R-05AC closed the preregistered pre-application integration gate positive.

A01 crosses from isolated mechanism research into attempted application.

The task is deliberately simple enough to evaluate exactly,
but external to the governance mechanisms themselves.

A population of 12 software cells must operate a small transform service.

Requests arrive for four different deterministic functions.
Demand shifts over time.
Each active healthy cell can process only one request per epoch.
Cells therefore need to specialize,
reallocate roles,
hibernate under a resource cap,
reactivate,
survive damage,
continue through a communication partition,
and preserve lineage / authority while still performing useful work.

The evaluator knows the correct transform outputs.

The organism does NOT receive evaluator truth labels for governance,
repair,
role assignment,
or health authority.

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No production deployment.
No network service exposure.
No CKB / KTRADE integration.
No financial task.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

A01 is disposable application research.

APPLICATION TASK

Every request carries four input bits:

a;
b;
c;
d.

Four service roles exist.

ROLE 0:
a XOR b.

ROLE 1:
b XOR c.

ROLE 2:
c XOR d.

ROLE 3:
a XOR d.

A healthy active cell in role R computes exactly the corresponding function.

Each active cell can serve at most one request per epoch.

Cells that are:

DORMANT;
QUARANTINED;
MID_MIGRATION

serve zero requests.

A corrupted cell would emit an inverted answer if allowed to serve.

The candidate must quarantine injected damage before that corrupted cell serves.

INPUT STREAM

No randomness during the primary.

Payload bits are generated deterministically from:

scenario;
epoch;
request_index;
role.

The exact generator is frozen in the harness before primary execution.

WORKLOAD

256 epochs per scenario.

Eight 32-epoch demand phases.

Base demand vectors:

P0 = (3,3,3,3)
P1 = (6,2,2,2)
P2 = (2,6,2,2)
P3 = (2,2,6,2)
P4 = (2,2,2,6)
P5 = (5,3,3,1)
P6 = (1,5,3,3)
P7 = (3,1,5,3)

Every vector sums to 12 requests per epoch.

Run four deterministic scenarios.

Scenario S rotates role labels by S positions.

Thus the same workload pressure is presented to every functional role
without changing total demand.

Total primary workload:

4 scenarios x 256 epochs x 12 requests
=
12,288 requests.

INITIAL POPULATION

12 cells.

Initial role:

ROLE(cell) = cell mod 4.

Thus initial capacity is:

(3,3,3,3).

Every cell starts:

ACTIVE;
healthy;
caught up;
with current causal authority.

SELF-ALLOCATION RULE

The evaluator does not assign new roles.

Each active healthy cell observes:

- its current role;
- current queue pressure for its role;
- public unserved-demand counters;
- current active healthy role counts.

For each role:

deficit(role) =
max(0, demand(role) - active_healthy_count(role)).

surplus(role) =
max(0, active_healthy_count(role) - demand(role)).

Eligible cells in surplus roles emit migration proposals toward the highest deficit role.

Ties:

lowest target role number,
then lowest proposing cell ID.

This ordering resolves simultaneous proposals.
It does not use request truth labels.

The distributed migration transaction may accept no more proposals
than the current deficit requires.

A migration uses the closed lineage-qualified role-authority contract.

Migrating cells serve zero requests in that migration epoch.

No cell may migrate while:

damaged;
quarantined;
dormant;
causally stale;
or lacking qualified governance provenance.

RESOURCE PRESSURE / HIBERNATION

Normal active budget:

12.

Epochs 80 through 87:

active budget = 10.

Epochs 208 through 215:

active budget = 9.

When active count exceeds budget,
eligible cells with the greatest current role surplus propose hibernation.

Ties:

largest surplus,
then highest cell ID.

Hibernation:

- revokes current witness authority;
- stores hereditary / dormancy state;
- contributes zero service and zero votes.

When budget rises,
dormant cells wake through the closed R0-R4 reactivation contract.

They do not automatically recover an old witness slot.

DAMAGE SCHEDULE

Inject one logical damage event at the beginning of epochs:

47;
111;
175;
239.

Target cell:

(epoch // 16) mod 12.

Damage occurs before service.

The cell would produce incorrect output if it served.

Candidate health / repair logic must:

1. detect and quarantine before service;
2. withhold authority;
3. execute qualified bounded repair;
4. restore service only after health qualification.

Repair may complete no earlier than the following epoch.

Thus damage has an availability cost,
but must have zero correctness cost.

COMMUNICATION PARTITION

Epochs 144 through 151.

Partition A:

cells 0..5.

Partition B:

cells 6..11.

Incoming requests are routed deterministically between the two partitions by request index parity.

During partition:

- each side sees only its local routed queue;
- eligible role reallocations are provisional;
- current authority remains partition-qualified;
- no population-size tie breaker exists.

At epoch 152:

causal re-merge executes before normal allocation.

Compatible provisional role changes may survive.

Conflicting or stale provisional changes must abstain / roll back under the closed merge rule.

PERSISTENCE / RESTART

After completing epoch 127:

serialize the complete application-organism state.

The serialization must include enough state to resume:

- cell roles / status / health;
- causal cursor;
- governance holders and lineage generations;
- registry state;
- hereditary capsules;
- dormancy snapshots;
- workload position;
- cumulative task metrics.

Resume into a fresh process / namespace for epoch 128.

A shadow uninterrupted execution is evaluator-only.

Required:

the restarted candidate must produce byte-identical authoritative state,
task outputs,
and cumulative metrics
to the uninterrupted candidate from epochs 128..255.

No evaluator state may be injected into the resumed organism.

BASELINES

STATIC BASELINE

Same cells.
Same workload.
Same damage schedule.
Same resource budgets.
Same health quarantine / repair timing.

But:

no role migration.

Initial allocation remains (3,3,3,3).

This tests whether developmental role reallocation creates useful task value.

ORACLE CAPACITY CEILING

Evaluator-only.

At each epoch,
compute the maximum number of requests that could be served correctly
with the same number of currently service-capable cells
if roles could be reassigned instantly with zero migration cost.

The oracle is not available to the organism.

It is a performance ceiling,
not an authority source.

PRIMARY METRICS

For candidate,
static baseline,
and oracle where applicable:

total requests;
served requests;
correct served requests;
incorrect served requests;
unserved requests.

Candidate also reports:

role migrations;
migration service-cost epochs;
hibernations;
reactivations;
damage quarantines;
repairs;
partition provisional transitions;
rolled-back transitions;
stale vote attempts;
authority violations;
causal regressions;
duplicate effective provenance;
restart mismatches.

DERIVED METRICS

TASK_ACCURACY =
correct_served / served.

TASK_COVERAGE =
served / total_requests.

ORACLE_EFFICIENCY =
candidate_served / oracle_served.

STATIC_GAIN =
candidate_TASK_COVERAGE - static_TASK_COVERAGE.

FAULT_RECOVERY

For each injected damage event:

measure epochs from quarantine to restored healthy service eligibility.

Required maximum:

2 epochs.

DEMAND_REALLOCATION

At every demand-phase transition:

measure epochs until candidate role capacity has no avoidable surplus while another role has deficit,
subject to:

- active budget;
- currently unavailable damaged cells;
- migration cost.

Required maximum outside partition:

3 epochs.

PRIMARY APPLICATION SIGNAL

A01_APPLICATION_SUCCESS

TRUE iff all are TRUE:

TASK_ACCURACY == 1.0

AND

incorrect_served_requests == 0

AND

ORACLE_EFFICIENCY >= 0.90

AND

STATIC_GAIN >= 0.08

AND

all four scenarios individually outperform their static baseline

AND

maximum qualified fault recovery <= 2 epochs

AND

maximum non-partition demand reallocation <= 3 epochs

AND

restart authoritative state equivalence == TRUE

AND

restart output equivalence == TRUE

AND

stale_vote_attempts_accepted == 0

AND

authority_violations == 0

AND

causal_regressions == 0

AND

duplicate_effective_provenance == 0

AND

split_brain_final_states == 0

AND

resource_budget_violations == 0.

NEGATIVE CONTROLS

CONTROL A — STATIC ROLE ALLOCATION

Expected lower task coverage under shifted workload.

CONTROL B — NO DAMAGE QUARANTINE

Evaluator-only.

A damaged cell is permitted to serve during the fault epoch.

Expected:

at least one incorrect result.

This establishes that correctness is not automatic from the workload.

CONTROL C — OLD ROLE RESTORE ON WAKE

Evaluator-only.

A reactivated cell overwrites current role with its pre-sleep role.

Expected:

at least one workload-capacity regression or authority violation.

CONTROL D — HEADCOUNT PROVENANCE

Copied witness holders are counted as independent.

Expected:

false authority becomes reachable in the injected copied-lineage control case.

These controls are not candidate alternatives.

They establish that the safety machinery affects application behavior.

HOLDOUTS / LIMITS

A01 does not test arbitrary malicious collusion.

Carry forward explicit constitutional limits:

- all independent governance roots may collude;
- registry roots may collude;
- a false state may be honestly sealed;
- a real event may disappear from every surviving history;
- constitutional genesis may be replaced.

A01 tests whether the architecture remains useful
without crossing those known boundaries.

MECHANICAL CONTROLS

Harness MUST assert:

- 12 cells;
- four exact transform functions;
- initial capacity (3,3,3,3);
- 256 epochs;
- 8 exact 32-epoch workload phases;
- 4 role-rotated scenarios;
- 12 requests per normal workload epoch;
- damage epochs exactly 47,111,175,239;
- resource caps exactly 10 at 80..87 and 9 at 208..215;
- communication partition exactly 144..151;
- restart after epoch 127;
- candidate migration tie rules;
- no evaluator truth label available to allocation / governance;
- no canonical DG-1R-05 execution;
- no STAB-18-R1 execution.

REPRODUCIBILITY

Two complete deterministic primary sweeps.

Serialized result SHA-256 must match exactly.

The restart sub-run must also reproduce the uninterrupted shadow result exactly.

NO POST-RESULT TUNING

After first primary A01 request is served,
do not alter:

- transform functions;
- workload vectors;
- scenario rotations;
- allocation rule;
- tie rules;
- damage schedule;
- hibernation schedule;
- partition interval;
- restart point;
- thresholds;
- primary metrics;
- success signal.

PLAIN-SPEAK PREREGISTERED QUESTION

This is the first time Yggdrasil has to earn its keep.

Twelve artificial cells run a tiny service.

Customers keep asking for four kinds of calculation,
but the mix of requests changes.

A cell can only do one job at a time.

If too many cells are doing a job nobody needs
while another queue is backed up,
the population has to move healthy cells to the busy job.

Then we make life harder.

We damage cells.
We force some to sleep because resources are tight.
We wake them back up.
We cut the population in half for several epochs.
We restart the whole program from saved state halfway through.

The organism does not get the answer key for deciding who is healthy
or who should have authority.

The answer key is only used afterward to score whether the service did its job.

A01 passes only if the organism is both:

USEFUL:
it serves materially more work than a static population
and stays close to an ideal capacity ceiling;

and

SAFE:
damage never produces a wrong served answer,
sleep does not resurrect stale authority,
history never moves backward,
and restart does not change what the organism believes.

This is still a small synthetic application.

But it is no longer an isolated rule test.

The architecture has to operate under task pressure.

canonical_scientific_execution = false.
stab18_r1_touched = false.
