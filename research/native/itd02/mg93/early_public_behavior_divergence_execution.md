# MG93-AK exact-source early behavior diagnostic execution

Classification: RETROSPECTIVE AUTHENTIC ORIGINAL-LEDGER DIAGNOSTIC; NOT CAUSAL.

Original immutable input:
- Yggdrasil workflow run: `41047254253`
- Artifact ID: `12972852607`
- Artifact ZIP SHA-256: `9f284ce2b793a2f6e0d0d8a1cb097efb5a9e5ce9b5d75f5c53a77f8474d0104a`
- `heldout.json` SHA-256: `0cdb155ce150717c3a678f6c536a81f5f4203dd96acafee459b2fdc1d2a36427`
- Exactly 48 held-out episodes, 12 paired (family,seed) keys × four roles.

Executed script Git blob matched current committed source exactly:
- Commit `da0777dedb66314dd89cc1efe62ae7321644be66`
- Path `research/native/itd02/mg93/early_public_behavior_divergence.py`
- Git blob SHA-1 `faea586ea8617b0beab6f2924f49d9adf5be4489`
- Raw SHA-256 `3b57292c7c28d51da78225edc1c249f075e5c0986b485fc04882810716cf7c4d`

Command: `python early_public_behavior_divergence.py heldout.json --output result.json`
Execution: isolated local Linux Python, source file byte-identical to fetched GitHub blob. Artifact ZIP and heldout JSON both hash-verified before execution.

| Role | Episodes | Unique returned views / observed prefix | Unique before/action/after edges / prefix | Mean action entropy (bits) | Prefix positive reward events | Eventual successes |
|---|---:|---:|---:|---:|---:|---:|
| MG92 native feedback | 12 | 59.375% | 70.833% | 1.42047 | 0 | 0/12 |
| MG91 frozen native prototypes | 12 | 45.833% | 53.125% | 1.07219 | 0 | 0/12 |
| Independent linear | 12 | 14.583% | 19.792% | 0.17492 | 0 | 0/12 |
| MG86 frozen teacher | 12 | 97.396% | 100% | 1.89050 | 1 | 10/12 |

Paired MG92 versus teacher:
- Teacher has more distinct returned views: 12/12 pairs.
- Teacher has more distinct transition edges: 11/12 pairs; 1 tie.
- The teacher is a hand-coded comparator, not an equally trained conventional learner.

The diagnostic uses up to the first 16 selected source actions, with shorter terminal/truncated prefixes retained at their actual length (no padding). Fractions are per-episode unique counts divided by actual prefix length, then averaged. There are no hidden state inputs, no future action inputs to a policy, no training, no original reset/step, and no new cohort.

Interpretation limit: early public trajectory diversity is associated with the successful hand-coded teacher on this exposed sample. Diversity may be a symptom of navigation competence rather than its cause. No counterfactual unselected action exists, so neither causality nor a policy benefit from maximizing novelty/entropy is identified. The teacher receives 1 positive reward event within its first-16 prefixes; all learned roles receive zero. Eventual teacher success is 10/12 versus 0/12 for learned roles. This is a descriptive diagnostic, not an acceptance or scientific breakthrough.

Result JSON SHA-256: `92a4065b0c04059a509828daf42b1aaa3005cd2c3da0d3f33bb79756e2e08479`
