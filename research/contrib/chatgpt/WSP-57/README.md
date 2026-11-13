# WSP-57 — Sparse active causal interventions (SELFTEST only)

## Exact custody
- Frozen prospective protocol: `a7a1d3c6f6ec6bd53b1e642a200ad4b3dab5f88a` committed before implementation or results.
- Predecessor WSP-56 draft PR #947 source/candidate `5160227ab731f76501e2803afed403d9aa1d51d1`; predecessor full inherited regression was pending at branch creation.
- New evaluator-only `source.py` constructs six unseen-seed nonlinear four-operation permutation worlds over seven physical states, with no WSP56 world functions imported.
- Learner `sparse_writer.py` never imports the generator, true operator maps, heldout outputs, or oracle action advice. The observation format uses primitive action channels, not language tokens.

## Prospective control
- Both the gradientless active learner and seeded-random control receive the same 12 charged unary probes (three known inputs per operation; 24 possible completions per operation).
- Each arm then chooses 24 new causal compositions adaptively or uniformly at random. The evaluator reveals the physical result **only after** choosing the charged action.
- Candidate elimination operates on possible 7-state permutation tables with bounded arc-consistency. Predict only when all evidence-consistent candidates agree; otherwise abstain.
- Evaluate on the common pool of pair-action state queries that neither arm has sampled, preserving equivalent heldout inputs. Six independent SELFTEST seeds 2301–2306.
- Measure exact coverage, wrong-confident predictions, candidate-set restriction, charged action parity, cold snapshots, search checks, time and persistent bits; the unary-only control is clearly identified as unmatched action budget.

## Frozen exploratory criterion and limitations
- SELFTEST_SIGNAL only if active accuracy exceeds random by at least 10 percentage points, active covers at least 40% of the common heldouts, neither arm makes wrong-confident predictions, and all six seeds finish with 36 charged actions and cold restore parity.
- Any failure is preserved without retuning the prospective threshold. Linux/Windows focused tests and complete inherited regression plus G29 atlas are required for engineering closure.
- A positive result is only active-intervention usefulness in a small discrete permutation family. It does not establish general language, natural-world causal transfer, memory beyond snapshots, or superiority over fully trained neural/independently qualified symbolic baselines.
- No protected DEV/PRIMARY first-use, merge/promotion, deployment, paid API, scheduled task or official autonomous loop integration.

## Reproduction
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-57 -p 'test_*.py' -v
```
