TITLE: YGGDRASIL APPLICATION TRACK A — A06 Lineage-Qualified Online Program Inheritance
DATE: 2026-09-20
STATUS: PREREGISTERED / ONLINE HEREDITARY PROGRAM-UPDATE GATE / NON-CANONICAL
TRACK: YGGDRASIL APPLICATION TRACK A
PARENT: A05 Post-Freeze Task-Semantic Transfer
BRANCH: dg1a-ar

PURPOSE

A05 showed that the developmental architecture can organize the population independently of the exact computation attached to each role.

A05 still supplied each scenario's role programs as a static scenario-level lookup.

A06 asks the next DNA-like question:

CAN AN ORGANISM ACQUIRE A NEW ROLE PROGRAM DURING ITS OWN LIFETIME,
GRANT THAT PROGRAM AUTHORITY ONLY AFTER INDEPENDENT QUALIFICATION,
AND THEN MAKE CELLS INHERIT THE CURRENT PROGRAM VERSION
THROUGH REPAIR,
WAKE,
MIGRATION,
AND RESTART?

A06 separates:

PROGRAM DEFINITION

from

PROGRAM AUTHORITY.

Seeing a new program is not sufficient to make it authoritative.

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No production deployment.
No network exposure.
No CKB / KTRADE integration.
No financial task.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

FROZEN PARENTS

Carry forward:

A02 developmental / constitutional organism source SHA-256:

b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b.

A03-FIXA environment / lifecycle source SHA-256:

f38fbe4823c6f8e3093a45b701cc39054c3bc814a67a97053d180bacb5087234.

A03 blind environment freeze:

6f010ce561d958a324664b2d3e0c04e3e113d91b.

A03 schedule manifest:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

A05 task-program freeze:

30d2b2ad4cc9126cbeba3854dbfe7551611e1ac8.

A05 task-program manifest:

3fbc3a77eef9068dba92f4206c8c5c7a180efafec2a0105aa52e978dea0fc7f6.

A05 accepted task-output stream SHA-256:

375753496d79b599af25e3c7d9abf9d5d924cde0106e5d4e293bd09278b590a4.

A06 begins every scenario with the exact A05 role programs.

PROGRAM STATE BECOMES CELLULAR / HEREDITARY

A06 may no longer compute a cell's answer by consulting only a scenario-global role table.

Each cell carries explicit program state:

program_role;
program_version;
program_truth_table;
program_digest.

At genesis:

program_role = current role;
program_version = 0;
program_truth_table = A05 P[scenario][role].

A cell may serve a request only if:

cell.program_role == cell.role

AND

cell.program_version == authoritative_program[cell.role].version

AND

cell.program_digest == authoritative_program[cell.role].digest.

A stale-program cell MUST NOT serve.

AUTHORITATIVE PROGRAM RECORD

For every role:

authoritative_program[role] contains:

role;
version;
truth_table;
parent_digest;
program_digest;
commit_epoch.

Version 0 corresponds to the exact A05 program manifest.

PROGRAM UPDATE CAPSULE

A proposed update contains:

scenario;
role;
new_version;
truth_table;
parent_digest;
proposal_digest.

proposal_digest is SHA-256 over the canonical capsule fields.

A valid update must have:

new_version = current_version + 1;

parent_digest = current authoritative program digest;

truth_table != current truth_table;

truth_table belongs to the frozen 12,840-entry balanced nonlinear catalog.

INDEPENDENT PROGRAM-SOURCE ATTESTATION

A06 introduces two program-specification provenance roots:

PROGRAM_SOURCE_A = 1 << 40.
PROGRAM_SOURCE_B = 1 << 41.

They are task-definition sources,
not evaluator truth sources.

A primary update is source-qualified only if:

- both roots independently attest;
- both attest the exact same proposal_digest;
- roots are pairwise disjoint.

Two copies derived from one root count as one source.

PROGRAM GOVERNANCE

Source agreement alone does not grant execution authority.

Commit additionally requires the existing organism:

_governance_ok()

AND

registry_ok().

Thus a program update requires both:

independent task-definition provenance

AND

current constitutional organism authority.

If either fails:

ABSTAIN;
old program remains authoritative.

PROGRAM COMMIT

When a valid proposal commits:

- authoritative_program[target_role] advances atomically to new_version;
- one causal-history record is appended;
- currently ACTIVE healthy cells already in target_role adopt the new program before serving that epoch;
- DORMANT cells keep their old local program state;
- QUARANTINED cells keep their old local program state until repaired;
- REACTIVATING cells must catch up before they can become service-authorized.

The update is not retroactively written into a dormant cell's local memory.

That is deliberate.

It creates a real stale-inheritance condition to test.

WAKE / REPAIR CATCH-UP

Before a cell can serve after:

reactivation

or

qualified repair,

its local program state must be reconciled to:

authoritative_program[cell.role].

A stale program may be replaced only after:

current causal ancestry verifies

AND

current program authority verifies.

A stale program cell that cannot verify the current authoritative record:

remains non-serving.

ROLE MIGRATION INHERITANCE

The accepted A02 migration decision remains unchanged.

When migration from role X to role Y completes:

the cell must inherit:

authoritative_program[Y]

before it is eligible to serve as Y.

It must NOT carry X's program into Y.

Migration ordering may not inspect truth-table contents.

DORMANCY

Dormancy snapshot stores the cell's current local:

role;
program_version;
program_digest;
causal cursor.

A dormant cell does not silently receive later program changes.

This is the explicit DNA-like stale-lineage test.

PERSISTENCE / RESTART

A06 restart state MUST include:

authoritative_program records;
cell-local program state;
program update history;
program-source provenance state.

Restart must not reconstruct program state from evaluator truth.

POST-FREEZE PRIMARY UPDATE DERIVATION

The A06 harness must be frozen before any primary update program is derived.

Let F06 be the exact A06 freeze commit.

For scenario s:

derive update program from:

SHA-256(
"YGG-A06-UPDATE|"
+ F06
+ "|"
+ decimal(s)
+ "|"
+ decimal(counter)
).

Map deterministically into the same frozen 12,840-entry balanced nonlinear catalog.

Reject only if the selected table equals the scenario's current target-role table.

On equality:

increment counter and derive again.

TARGET ROLE / UPDATE EPOCH

These are derived deterministically from the already-frozen A03 environment schedule,
without evaluator truth.

For each scenario:

consider demand-regime transitions whose start epoch is:

>= 96
AND
< partition_start.

For each transition,
compute for every role:

increase =
new_demand(role) - prior_demand(role).

Choose the transition with the largest positive role increase.

Ties:

earliest transition start;
then lowest role number.

target_role =
the selected role.

update_epoch =
selected transition start - 1.

Therefore the new program becomes authoritative immediately before a demand increase for that role,
creating natural pressure for later inheritance through role migration.

If no positive transition exists in that interval:

mechanical environment failure;
primary invalid.

PRIMARY SIZE

Use the exact 12 accepted A03 blind environment schedules.

384 epochs x 12 requests x 12 scenarios
=
55296 primary requests.

PROGRAM EXPECTATION

Before update_epoch:

evaluator expected output uses version 0.

At and after successful authoritative update commit:

evaluator expected output uses version 1 for target_role.

Other roles remain version 0.

The evaluator answer is never visible to:

program authorization;
governance;
registry;
role allocation;
migration;
repair;
hibernation;
reactivation.

PRIMARY PROGRAM UPDATE

Every primary scenario presents:

two independent matching program-source attestations

for the derived version-1 proposal.

Therefore the candidate SHOULD commit exactly one authoritative program update per scenario.

This is a sensitivity test for the valid path.

INHERITANCE EVIDENCE

For every scenario report:

program commit epoch;
target role;
old / new program digest;
number of active target-role cells updated at commit;
number of stale dormant / quarantined target-role cells left unchanged;
wake catch-up events;
repair catch-up events;
migration inheritance events;
stale-program service attempts;
stale-program served requests.

Required primary:

program commits = 12 / 12.

stale-program served requests = 0.

stale-program service attempts accepted = 0.

At least one of the 12 primary scenarios must exercise:

migration inheritance after the program update.

If natural workload produces zero such cases,
A06 primary FAILS the inheritance-coverage gate.

DEDICATED HEREDITARY PROBES

In addition to natural primary workload,
run deterministic evaluator-isolated clones of post-update organism state.

These do NOT alter the primary service run.

PROBE H1 — STALE DORMANT WAKE

Select a DORMANT healthy cell whose role equals the updated target role
and whose local version is stale.

If none exists naturally,
create the probe from a pre-update snapshot by placing one otherwise-qualified target-role cell through the existing dormancy transition before applying the same valid update.

Then run the normal wake path.

Required:

the cell cannot serve stale code;
it catches up to current authoritative program before serving.

PROBE H2 — POST-UPDATE MIGRATION

Select an eligible healthy donor under the existing governance / registry contract.

Execute the existing role migration into the updated target role.

Required:

after migration completes,
local program version / digest equal current authoritative target-role record
before service eligibility.

PROBE H3 — REPAIR AFTER UPDATE

From a post-update clone,
damage one target-role cell carrying current version.

Run the existing bounded repair.

Required:

repair returns the cell with current authoritative program;
no stale program service.

SOURCE / AUTHORITY NEGATIVE CONTROLS

CONTROL S1 — ONE SOURCE ONLY

Only PROGRAM_SOURCE_A attests.

Expected:

no program commit.

CONTROL S2 — SAME-ROOT FANOUT

Two nominal witnesses both descend from PROGRAM_SOURCE_A.

Expected:

effective source count = 1;
no commit.

CONTROL S3 — SOURCE DISAGREEMENT

PROGRAM_SOURCE_A and PROGRAM_SOURCE_B attest different proposal digests.

Expected:

no commit.

CONTROL S4 — STALE PARENT

Both sources agree,
but parent_digest does not equal current authoritative program digest.

Expected:

no commit.

CONTROL S5 — GOVERNANCE UNAVAILABLE

Both program sources agree
but organism governance / registry qualification is unavailable.

Expected:

no commit.

CONTROL S6 — AUTO-TRUST NEW PROGRAM

Evaluator-only unsafe control.

One observed program proposal immediately becomes authoritative.

Expected:

false authority reachable under one-source forged proposal.

CONTROL S7 — STALE WAKE WITHOUT PROGRAM CATCH-UP

Evaluator-only unsafe control.

Allow a dormant pre-update cell to regain service while retaining old program.

Expected:

at least one wrong served result for a discriminating input.

PRIMARY METRICS

Carry forward A03/A05 task metrics plus:

program_updates_committed;
program_update_abstentions;
stale_program_service_attempts;
stale_program_service_attempts_accepted;
stale_program_served_requests;
wake_program_catchups;
repair_program_catchups;
migration_program_inheritances;
program_authority_regressions;
program_parent_chain_breaks;
program_digest_mismatches;
program_state_restart_mismatches.

PRIMARY SIGNAL

A06_ONLINE_PROGRAM_INHERITANCE_SUCCESS

TRUE iff:

12 / 12 primary program updates commit

AND

TASK_ACCURACY == 1.0

AND

incorrect_served_requests == 0

AND

stale_program_served_requests == 0

AND

stale_program_service_attempts_accepted == 0

AND

migration_program_inheritances >= 1

AND

all dedicated hereditary probes pass

AND

all source / authority negative controls fail closed as preregistered

AND

all 12 restart authoritative states are equivalent

AND

all 12 restart task-output / metric suffixes are equivalent

AND

program_state_restart_mismatches == 0

AND

program_authority_regressions == 0

AND

program_parent_chain_breaks == 0

AND

program_digest_mismatches == 0

AND

all existing authority / provenance / causal / resource safety totals remain zero.

NO POST-RESULT TUNING

After F06 exists,
do not alter:

- update derivation;
- target-role selection;
- update-epoch selection;
- source roots;
- source quorum;
- program governance rule;
- cell-local program state;
- wake catch-up;
- repair catch-up;
- migration inheritance;
- task programs;
- A03 environments;
- thresholds;
- probes;
- controls;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

A05 proved that the same organism can run jobs we did not write into its developmental policy.

A06 goes further.

Now one of those jobs changes while the organism is alive.

A cell hearing about the new program is not enough.

Two genuinely independent program sources must agree,
and the organism's own healthy governance must still authorize the change.

Once the new program becomes official,
cells that are awake can adopt it.

Sleeping cells do not magically learn it.

They wake with old memory
and must catch up before they are allowed to work.

A cell changing jobs must inherit the current program for its new job,
not carry its old program across.

That starts to look much more like the hereditary mechanism we were discussing:

a compact program is inherited through lineage and developmental transitions,
while authority to change that program remains distributed.

A06 still does not create an entirely new fifth role.

That should remain a later experiment
so we do not confuse:

safe program inheritance

with

expanding the organism's role vocabulary.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A06 ONLINE HEREDITARY PROGRAM INHERITANCE

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A06 UPDATE PROGRAM.

IMPLEMENTATION COMMIT

f1dd0c3fec863e5f2e27b8f735511527290183a1.

SOURCE BUNDLE

Loader:

research/applications/track-a/a06_online_program_inheritance_v1.py

Loader Git blob:

22101de688643249318698be95ef628e51c99208.

Exact gzip payload:

research/applications/track-a/a06_online_program_inheritance_v1.py.gz

Payload Git blob:

a0191548c477e131a21169140edf2a06bf4ae3f6.

Compressed payload SHA-256:

e89436630aaecc6eb7fb455252613e952cb63138cdd49b4abad1cf8a187a68dc.

Compressed payload bytes:

7989.

Decompressed exact source SHA-256:

eb7a83320983168fe63d46852ee5d84bebf4c4cf80674ab2a885502e3bfb5a73.

Decompressed source bytes:

31344.

FROZEN PARENT DEPENDENCIES

A05 source SHA-256:

9efc8e31c08b60b6decff06c7ffc5b5a1ad10df7bb4440d4b2ab4d1fb5876fce.

A05 task-program manifest:

3fbc3a77eef9068dba92f4206c8c5c7a180efafec2a0105aa52e978dea0fc7f6.

A03 environment manifest:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Program catalog size:

12840.

Program-source roots:

2 independent pairwise-disjoint roots.

Mechanical update manifest used only:

MECHANICAL-NONPRIMARY-FREEZE.

Mechanical update manifest SHA-256:

fe0c8624b65897268fce493ce85fa0d7b3044da2f21c3726258615468873cea6.

No real primary update program derived:

TRUE.

Full non-primary structural smoke:

12 / 12 mechanical updates committed;
candidate served 52273;
candidate incorrect 0;
stale-program served 0;
stale-program attempts accepted 0;
migration inheritance exercised;
all dedicated hereditary probes PASS;
all source / authority negative controls FAIL CLOSED;
all restarts equivalent;
all existing safety totals zero;
partition / re-merge complete.

These mechanical outcomes are implementation checks only.
They are not A06 scientific evidence.

SEMANTIC FREEZE

The harness freezes:

- cell-local program role / version / truth table / digest;
- authoritative per-role program record;
- parent-digest version chain;
- two independent program-source provenance roots;
- source quorum distinct from organism governance;
- source agreement plus existing governance / registry requirement for commit;
- active healthy target-role adoption at commit;
- dormant stale-memory preservation;
- wake catch-up before service;
- repair catch-up before service;
- target-role program inheritance through migration;
- program authority / local program persistence through restart;
- stale-program service exclusion;
- dedicated hereditary probes H1 / H2 / H3;
- source / authority controls S1..S7.

PRIMARY UPDATE STATUS AT THIS FREEZE

NOT DERIVED.

Let the resulting commit SHA of this freeze update be F06.

For scenario s,
the primary version-1 program remains exactly:

SHA-256(
"YGG-A06-UPDATE|"
+ F06
+ "|"
+ decimal(s)
+ "|"
+ decimal(counter)
)

mapped into the frozen 12,840-entry balanced nonlinear catalog,
rejecting only equality with that scenario's current target-role program.

No post-freeze update replacement,
difficulty shaping,
or source change is allowed.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
