# CKAD25 — Factorized causal surprise on disjoint synthetic streams

**DEVELOPMENT_SIGNAL_NO_GO** — frozen development signal test,
not proof of superior policy/learning/retention. The alternative alarms
were shadow monitors, sharing the unchanged native learner's decisions
and public intervention consequences. No split signal changed the model.

Existing joint alarm uses prequential p(T,Y) with factor4; transition
and reward alarms each use their observed marginal likelihood with
factor2. All use threshold16 and 8 min local observations; factorized
OR fires on either component, resetting both component scores.

| Schedule | Alarm | Detection 48 /3 | 96 /3 | 144 /3 | Total true detections | False alarms |
|---|---|---:|---:|---:|---:|---:|
| transition_only | joint | 2 | 2 | 2 | 6 | 3 |
| transition_only | transition | 3 | 2 | 3 | 8 | 8 |
| transition_only | reward | 0 | 0 | 0 | 0 | 0 |
| transition_only | factorized_or | 3 | 2 | 3 | 8 | 8 |
| reward_only | joint | 2 | 0 | 1 | 3 | 3 |
| reward_only | transition | 1 | 0 | 0 | 1 | 3 |
| reward_only | reward | 0 | 0 | 0 | 0 | 1 |
| reward_only | factorized_or | 1 | 0 | 0 | 1 | 4 |
| stationary_null | joint | — | — | — | 0 | 4 |
| stationary_null | transition | — | — | — | 0 | 5 |
| stationary_null | reward | — | — | — | 0 | 1 |
| stationary_null | factorized_or | — | — | — | 0 | 6 |

## Frozen gates

- recognition_per_boundary_each_schedule: FAIL
- gain_at_least_four_true_detections: FAIL
- changed_world_false_alarms_lte3_each: FAIL
- stationary_null_false_alarms_lte1_each: FAIL
- exact_source_and_replay_custody: PASS

Total true detections: existing joint 9 vs factorized OR 9 (delta 0).

Every negative result, held null schedule and original checkpoint
witness prefix is preserved. Nine byte-exact Linux and Windows native
checkpoint pairs and event proofs are stored as deterministic gzip
blobs in this GitHub folder. Additional source namespaces are not
independent retrained parent seed groups or novel real-world sources.

This result measures alarm timing/specificity only, not reward gain,
world-rule discovery, scientific generalization or learning improvement.

Frozen aggregate SHA256: 868d908567a3f553d05f1ae5b3a46ea4a6a2ec91a12596e46d7590629ffb5a38

**ENGINEERING:** subject to mandatory final cross-platform full regression.
**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**
