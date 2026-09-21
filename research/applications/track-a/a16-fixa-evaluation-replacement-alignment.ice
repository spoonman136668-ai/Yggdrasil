TITLE: YGG-A16-FIXA — Eight-Epoch Evaluation Replacement Alignment
DATE: 2026-09-21
STATUS: PREREGISTERED / EVALUATION-ONLY CORRECTIVE REPLICATION / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8
PARENT: A16 Hysteretic Working-State Plasticity Under Moving Developmental Drift
BRANCH: dg1a-ar

PURPOSE

The exact F16-frozen A16 harness correctly executed its moving-drift learning and hysteresis logic,
but its inherited service helper did not execute the preregistered second replacement episode at epoch 4.

A16-FIXA asks:

DOES THE A16 MOVING-DRIFT RESULT REMAIN POSITIVE
WHEN EVERY FROZEN 8-EPOCH HELD-OUT EVALUATION
EXECUTES BOTH PREREGISTERED CLEAN-REPLACEMENT EPISODES:

epoch 0
and
epoch 4?

FROZEN A16 WORLD

A16 implementation commit:

c6d4bd66bb9bde1dc72a3176ac0ffa1c40ee16f8.

Freeze F16:

90279bc5b90682e2538721ef152aa3accdedbddf.

A16 source SHA-256:

cd89dbc46174c97e0bea0bc0a1db4b65eea9b5732521ca30f00ed30f06b792fa.

A16 moving-drift manifest SHA-256:

5feef8c8bde1e8a6380d68fb7ab55f57ab7f29c93879b766fc4f48b30041313e.

Historical exact-F16 result SHA-256:

c4ecb7c90742fd737d370e2f378f398ccddd948bf5154c46d917fd3250fb339f.

Historical closure:

a4f0a5d2263f9eeb3c5061d5acc11d153af4e62c.

Post-closure evaluation audit:

0b32a1d2c52841f47c3dd457662db926a45093a8.

ALLOWED CORRECTION

Only the held-out service evaluation helper may change.

Correct helper semantics for one 8-epoch evaluation:

- begin from supplied cell state;
- at epoch 0:
  replace exactly the frozen target set replacements["0"];
- at epoch 4:
  replace exactly the frozen target set replacements["4"];
- at each epoch:
  score served requests before migration;
- after service:
  perform the same one-step migration rule;
- accumulate:
  service_total;
  first-four service after each replacement episode;
  migrations;
  replacement assignments.

The role-selection rule for replacement cells remains exactly:

A11.choose_birth_role.

The replacement implementation remains exactly:

A11.replace_cells.

The service rule remains exactly:

A11.served.

The migration rule remains exactly:

A11.migrate_one_step.

FORBIDDEN CHANGES

Do not change:

F16;
A16 manifest;
P0..P4 path priors;
reverse path;
transient P1/P0 blocks;
all true-drift observations;
attestation roots;
learner orders;
working-state digest construction;
hysteresis;
authorization;
durable C-v1/v2 records;
replacement TARGET SETS;
held-out demand sequences;
restart location;
stale-v2 baseline prior;
oracle target prior;
thresholds;
P1..P10 probes;
N1..N8 controls.

CORRECTIVE PRIMARY

Execute the same A16 scenario logic
but route candidate,
stale-v2 baseline,
and oracle held-out evaluations
through the corrected 0/4 helper.

Required structural counts:

12 scenarios.

7 true working-state updates per scenario.

7 held-out evaluations per scenario.

2 replacement episodes per held-out evaluation.

Therefore:

84 held-out evaluations total.

168 candidate replacement episodes.

168 stale-baseline replacement episodes.

168 oracle replacement episodes.

For the 72 non-P0 evaluations,
use the original frozen usefulness thresholds:

candidate aggregate first-four service
>
stale-v2 aggregate;

candidate >= stale-v2 in at least:

60 / 72;

candidate oracle efficiency >=:

0.98;

at least one migration avoided.

For the 12 final P0 returns:

candidate service must match P0 oracle.

LEARNING / HYSTERESIS EQUIVALENCE

The corrected evaluation helper must not change:

12 / 12 transient P1 no-update results;

12 / 12 transient P0 clear results;

all first-block abstentions;

all second-block updates;

all complete working paths;

all final P0 priors;

all final working generations = 7;

all durable-history checks;

all parent-digest checks;

all restart checks;

all P1..P10 probe outcomes;

all N1..N5 unsafe-control outcomes.

PRIMARY CORRECTIVE SIGNAL

A16_FIXA_EVALUATION_ALIGNMENT_VALID

TRUE iff:

F16 unchanged
AND
manifest SHA unchanged
AND
all 84 candidate evaluations execute exactly two replacement episodes
AND
all 84 stale evaluations execute exactly two replacement episodes
AND
all 84 oracle evaluations execute exactly two replacement episodes
AND
all A16 learning / hysteresis / ancestry / restart / probe signals remain TRUE
AND
candidate non-P0 aggregate service > stale-v2 aggregate
AND
candidate >= stale-v2 in at least 60 / 72 non-P0 evaluations
AND
candidate oracle efficiency >= 0.98
AND
at least one migration is avoided
AND
all final-P0 candidate service matches P0 oracle
AND
TASK_ACCURACY == 1.0
AND
incorrect served == 0
AND
stale-program served == 0
AND
existing constitutional safety totals remain zero.

CORRECTED ACCEPTANCE SIGNAL

A16_T8_HYSTERETIC_MOVING_DRIFT_ACCEPTED

TRUE iff:

A16_FIXA_EVALUATION_ALIGNMENT_VALID.

The original exact-F16 result remains historical and is not rewritten.

REPRODUCIBILITY

Two complete deterministic FIXA sweeps.

Serialized FIXA outputs must be byte-identical.

NO POST-RESULT TUNING.

PLAIN-SPEAK PREREGISTERED QUESTION

The A16 learner passed its moving-drift test,
but the service stress test skipped the halfway cell replacement.

FIXA does not teach the organism anything new.

It does not change the drift path.

It does not change when the working developmental state is allowed to move.

It simply makes the evaluation do what the preregistration already said:

replace cells at step 0
and again at step 4.

Then we ask whether the same learned working state
still helps under the complete turnover schedule.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A16-FIXA EVALUATION ALIGNMENT

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE FIRST CORRECTED A16-FIXA PRIMARY EXECUTION.

IMPLEMENTATION COMMIT

5baae9f8146661844500a3a3ac13e5da6afb5f6b.

SOURCE BUNDLE

Loader:

research/applications/track-a/a16_fixa_evaluation_alignment_v1.py

Loader Git blob:

95c41b0062dfe5275c2bde7f6e9cdcf8e503e8e3.

Payload:

research/applications/track-a/a16_fixa_evaluation_alignment_v1.py.gz

Payload Git blob:

e7f1428e02a23ddf11cc70be6d942aecc9acf7f5.

Compressed payload SHA-256:

7226ecf6fc34562fd68899cf28f64c246dafcc173c6b47bc33388cc56d065646.

Compressed payload bytes:

2451.

Decompressed source SHA-256:

a3760a2857c06dd12e3bbaf293c600147b98c45384bde24e69b3edaddf4476f3.

Decompressed source bytes:

5537.

FROZEN PARENT

F16:

90279bc5b90682e2538721ef152aa3accdedbddf.

Exact A16 source SHA-256:

cd89dbc46174c97e0bea0bc0a1db4b65eea9b5732521ca30f00ed30f06b792fa.

A16 manifest SHA-256:

5feef8c8bde1e8a6380d68fb7ab55f57ab7f29c93879b766fc4f48b30041313e.

Historical exact-F16 result SHA-256:

c4ecb7c90742fd737d370e2f378f398ccddd948bf5154c46d917fd3250fb339f.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Parent source / manifest verification:

PASS.

Frozen replacement keys in all 84 held-out evaluations:

0 and 4.

Corrected helper mechanically executes:

epoch 0;
epoch 4.

No corrected primary service aggregate
was executed or observed before this freeze.

The wrapper changes no moving-drift scientific state.

It substitutes only the evaluation helper.

PRIMARY STATUS

NOT EXECUTED.

Two complete deterministic corrective sweeps are required.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — A16-FIXA EVALUATION REPLACEMENT ALIGNMENT

DATE:
2026-09-21.

STATUS:
CLOSED / POSITIVE CORRECTIVE PRIMARY / REPRODUCIBLE /
A16 FULL PREREGISTERED ACCEPTANCE RESTORED VIA FIXA / NON-CANONICAL.

FROZEN FIXA

Implementation commit:

5baae9f8146661844500a3a3ac13e5da6afb5f6b.

Freeze commit:

0428232691de48226523faa1229a42d44dce6e4c.

Source SHA-256:

a3760a2857c06dd12e3bbaf293c600147b98c45384bde24e69b3edaddf4476f3.

Source bytes:

5537.

Compressed payload SHA-256:

7226ecf6fc34562fd68899cf28f64c246dafcc173c6b47bc33388cc56d065646.

Compressed payload bytes:

2451.

FROZEN A16 WORLD

F16:

90279bc5b90682e2538721ef152aa3accdedbddf.

A16 source SHA-256:

cd89dbc46174c97e0bea0bc0a1db4b65eea9b5732521ca30f00ed30f06b792fa.

A16 moving-drift manifest:

5feef8c8bde1e8a6380d68fb7ab55f57ab7f29c93879b766fc4f48b30041313e.

Historical exact-F16 result:

c4ecb7c90742fd737d370e2f378f398ccddd948bf5154c46d917fd3250fb339f.

That historical result remains preserved.

Its usefulness evaluation omitted the preregistered epoch-4 replacement episode.

REPRODUCIBILITY

Two complete deterministic FIXA sweeps.

Sweep 1 serialized output SHA-256:

11247f545cc8fa398e10ff0cde8fa9578b0a17deece942fff6483c923312a3f3.

Sweep 2 serialized output SHA-256:

11247f545cc8fa398e10ff0cde8fa9578b0a17deece942fff6483c923312a3f3.

Byte-identical:

TRUE.

CORRECTIVE SIGNALS

A16_FIXA_EVALUATION_ALIGNMENT_VALID:

TRUE.

A16_T8_HYSTERETIC_MOVING_DRIFT_ACCEPTED:

TRUE.

EVALUATION EPISODE EXECUTION

Held-out evaluations per sweep:

84.

Candidate replacement episodes executed:

168.

Stale-v2 baseline replacement episodes executed:

168.

Oracle replacement episodes executed:

168.

Every held-out evaluation executed:

epoch 0 replacement;
epoch 4 replacement.

Thus the corrective run exactly matches
the originally preregistered A16 turnover schedule.

LEARNING / HYSTERESIS EQUIVALENCE

Transient one-block P1 no-update:

12 / 12.

Transient P0 clear:

12 / 12.

All true first blocks abstain:

TRUE.

All true second blocks authorize update:

TRUE.

All working trajectories:

P0 -> P1 -> P2 -> P3 -> P4 -> P3 -> P2 -> P0.

Final working prior:

P0
in 12 / 12.

Final working generation:

7
in 12 / 12.

Durable history:

[v1,v2]
unchanged in 12 / 12.

Parent-digest chains:

exact.

Restart comparisons:

equivalent.

All P1..P10 probes:

PASS.

All N1..N5 unsafe controls:

exposed as preregistered.

CORRECTED USEFULNESS

Non-P0 moving-drift evaluations:

72.

Candidate first-four service:

5984.

Stale-v2 baseline:

5870.

Evaluator-only oracle:

5984.

Oracle efficiency:

1.0.

Candidate >= stale-v2:

66 / 72 evaluations.

Migrations avoided relative to stale-v2:

70.

Final P0 return service:

matched P0 oracle exactly.

TASK / CONSTITUTIONAL SAFETY

Task accuracy:

1.0.

Incorrect served:

0.

Stale-program served:

0.

Existing constitutional safety violations:

0.

TECHNICAL INTERPRETATION

The original A16 learning result was real,
but its service evaluation executed only half of the preregistered turnover episodes.

A16-FIXA corrects only that evaluation mismatch.

The same frozen F16:

- moving paths;
- evidence;
- hysteresis;
- learner results;
- working-state digest chains;
- durable developmental history;
- restart state;
- probes;
- controls

were reused unchanged.

When the complete replacement schedule was actually executed,
the working developmental overlay still improved service,
still matched the oracle,
and avoided more migrations than the stale durable C-v2 baseline.

Therefore the full preregistered A16 T8 claim is now accepted via FIXA.

PLAIN-SPEAK INTERPRETATION

We found a test-harness mistake after A16.

The learner was doing the right thing,
but the service test was supposed to replace cells twice in each short evaluation
and only replaced them once.

We did not hide that.

We marked the old usefulness result incomplete
and reran the exact same frozen worlds
with both replacements actually happening.

The result still passes.

With the full turnover stress:

Yggdrasil served:

5984

immediate post-replacement requests

versus:

5870

for staying stuck on the old durable policy.

It matched the oracle
and avoided:

70

migrations.

The moving developmental state still ignored temporary noise,
followed sustained drift,
reversed correctly,
and returned exactly to its durable anchor.

So A16 is now fully accepted,
with the missing test condition explicitly repaired rather than hand-waved away.

ACCEPTED FRONTIER

A16 / T8:

positive hysteretic moving-drift working-state plasticity
via A16-FIXA evaluation alignment.

A17:

preregistered / unexecuted bounded incremental patch-journal tracking.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
