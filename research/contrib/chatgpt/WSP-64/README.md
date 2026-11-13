# WSP-64 — Variable sensor cardinality, coupled effects and latent-state falsification

## Prospective frozen custody
- Immutable preregistration **before creating any new source/learner/tests**: `aa87006d0da60a1557c55df0e71704147694a4a8` (`prereg.json`), 2026-11-13.
- Parent [WSP63 draft PR #954](https://github.com/spoonman136668-ai/Yggdrasil/pull/954), exact SHA `c32b1d9b7a75fae491948a2af0ea499c8d637519`. Its previous **195/256**, **132 truly unobserved physical consequences**, **zero confidently wrong** frozen SELFTEST signal remains unchanged; prior inherited full two-platform regression still pending at this branch point.
- Independent fresh SHA256 source salt and 12 seeds 3001–3012, **SELFTEST only**. Evaluator-only `source.py` holds hidden action roles, causal physics, task labels and hidden mode. Learner and independent tree control do not import the evaluator.

## What is new and what is deliberately known
- The candidate learns the number of *visible binary sensor registers* dynamically: four 3-bit worlds, four 5-bit worlds and four 4-bit worlds with an unobservable internal mode. Each has four hidden shuffled action channels.
- 3-bit worlds contain actions changing two sensor bits at once. The 5-bit worlds combine variable-bit outputs, different conditional effects in the same action and interactions of up to two input bits.
- The generic gradientless learner enumerates all source-blind GF(2) Boolean polynomials of degree at most 2 with at most 3 nonzero terms, **per action/output bit**, and retains *every* evidence-consistent explanation. It predicts a consequence only when the entire resulting output vector is uniquely determined; otherwise abstains. No privileged affected-bit identifier, single-target assumption, hidden role map, gradient descent or token-based language model.
- **The Boolean, degree-two and three-term limits remain supplied inductive biases** that exactly match the two observable-Markov source families. This does NOT prove discovery of unlimited representational primitives.
- The last four worlds contain a **hidden mode**. One action changes this mode without any visible state change; another action produces different physical consequences for identical visible state/action pairs depending on the unobservable mode. Therefore a deterministic Markov model of the visible state alone **cannot always predict safely**. The learner must flag observed contradictions and abstain; this is a deliberate negative/safety test.
- Markov worlds give each of two policies 48 physically continuous charged actions from a single all-zero start. Latent worlds give 64 actions per policy. The learner has no training reset, arbitrary-state queries or teleport. The active policy selects from the current physical state using public novelty/uncertainty; the seeded random policy has an equal action count.

## Frozen evaluation and controls
- Eight Markov worlds contain 32 new source-reachable 2–6-step goals each, **256** total. All tested task starts/goals are source hidden until scoring and neither arm receives the oracle path.
- The primary qualification requires **>=160/256** successful source goals, **>=20 more** successes than *same-action-ledger exact lookup*, >=70 correct **genuinely unobserved** state/action physical effects, and zero confident wrong in all Markov physical state-action audits.
- The hidden-mode requirement is that **>=3/4** latent worlds produce directly *observed contradictions* for identical visible state/action pairs, and the learner makes **zero confidently wrong** predictions when independently audited under **both hidden modes**. A miss is a permanent `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`, not a reason to change the frozen thresholds.
- Diagnostic controls: same charged-history exact lookup, an independently implemented fully fitted finite binary decision tree (not a fully trained neural baseline), and a random-policy sparse learner under matched charges. All arms log session continuity, source SHA256 and action histories.
- Canonical SHA256 cold-restored knowledge must reproduce all predictions and planning outputs without new observations. Snapshot tamper rejection; memory bits, candidate multiplicities, wall/CPU, and selection overhead recorded.

## Interpretation limits
This is not open-world general intelligence: visible sensors are binary and transparent, the evaluator deliberately chooses finite low-degree source families, goals are exact state vectors, 6-action plans are bounded, hidden mode is not learned as a belief state, and no independently trained conventional neural model with total compute parity is supplied. A synthetic SELFTEST_SIGNAL is only an engineering/development observation, not independent SCIENTIFIC_PASS or deployment authority.

## Reproduction and separate qualifications
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-64 -p 'test_*.py' -v
```

Focused Linux/Windows SELFTEST, exact-source generated-only G29 atlas and full inherited two-platform regression run on the exact candidate tree. No protected DEV/PRIMARY first-use, promotion, merge, scheduled tasks, official owner-loop integration, new controller/runner, paid API, deployment, or live action.
