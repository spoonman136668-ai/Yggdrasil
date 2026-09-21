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
