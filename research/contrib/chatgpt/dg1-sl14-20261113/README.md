# DG1-SL14 — Causal DNA (six-bit modular causal fingerprints)

**External synthetic development contribution. Scientific classification: `MIXED_DEV`, preregistered primary `NO-GO`. Not a native Yggdrasil architecture improvement and not AGI evidence.** Leave PR #996 draft and unmerged.

## Research question

Could a compact per-mechanism causal fingerprint recognize when a previously learned context returns, preserve its rules without full episode replay, and generalize predictions to never-seen action/input combinations more efficiently than conventional controls? SL07–SL13 repeatedly failed robust whole-program archived context recovery. SL14 deliberately changed to a six-bit physical environment with three independent Boolean causal mechanisms.

The [preregistration](prereg.json) was committed first, at `272cbb87542d87c779161780602cfddfb7439e8a`. This experiment's original prospective scientific source was `d110b4507dad2f4d62736b4106c6bfca3ee43fd3`. Raw per-world original receipts are in [GitHub Actions run 43530221844](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43530221844), Ubuntu artifact ID `14087056972`, Windows artifact ID `14087710334`.

## Physical test

Four cohorts of eight genuinely new seeded worlds, six comparison arms, 96 paid physical steps per world/arm: **18,432 paid steps**, **14,784 real causal action-consequences** and **3,648 physically charged input perturbations**. Contexts are A→B→A→B, A→B→A→C (new recombination), A→B→C→A, and stable A. Three public inputs and three outputs form the six-bit state. Each action tests an independently composed Boolean mechanism; phase labels and hidden rules are evaluator-only. Active and four control learners independently execute the exact same physically paid trajectory. The passive arm has identical charged count but different information. All arms restore sealed memory at 43,67,89 and audit after 24,48,54,72,78,96 without training on audit truth.

The candidate stores six-rule error registers per module, bounded bank selection evidence and actual bank activation provenance, not complete episode logs. Controls: same candidate representation with retrieval disabled, separately implemented online exponentially decayed Bayesian six-rule posterior, rolling 18-event six-rule fitter, and a non-compositional 18-event majority lookup; all on matched original charged physical events.

## Frozen outcome

| Final A→B→A→B full audit | Correct / 192 |
|---|---:|
| Causal DNA candidate | **168** |
| Same physical trace, no archived retrieval | 118 |
| Independent online decayed Bayesian | **172** |
| Rolling rule fitter | 166 |
| Flat lookup | 148 |

Genuine archived return-A in **4/8** worlds (minimum 5), return-B in **6/8** (minimum 5). The candidate improved final returning-B correctness by **50/192 versus no-archive**, but not over the Bayesian control, and failed true unseen-pair superiority. It falsely retrieved an earlier full context in **4/8** new-C worlds (maximum 2) and degraded C performance to 124/192 versus no-archive 142/192. Its inference/selection CPU ratio to the Bayesian control was **6.31× Ubuntu / 5.27× Windows** (maximum 2.0).

**Conclusion:** modular physical mechanism fingerprints produced a stronger synthetic B-return signal than previous whole-context archive attempts, but they still hallucinate returning memory in recombinations and are too computationally expensive. This does not qualify for native promotion. Next **distinct** research question, if separately frozen and authorized, is low-cost partial-mechanism recognition plus a veto for falsely matched full contexts, not post-result tuning here.

## Reproduce

Checkout the exact frozen scientific source SHA and run from repository root with Python 3.12 stdlib:

```bash
python -m unittest discover -s research/contrib/chatgpt/dg1-sl14-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-sl14-20261113/sl14.py > sl14-result.json
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

The original source requires a **mechanical generated code-atlas reanchor** before the inherited G29 test can pass. Never modify any hidden physical rule, learning source, seed, primary threshold, audit, or control after the original result. The complete scientific metrics and exact artifact provenance are in [result-summary.json](result-summary.json) and [provenance.json](provenance.json). Do not store raw trials in ChatGPT Library.

## Isolation and limits

Only a draft external research contribution stacked on prior drafts; no modification to Yggdrasil native source, accepted state, main, Forge, Wingless, Hybrid, weight research, owners, controllers or autonomous loops. All tests are synthetic; a success signal in this simplified six-bit physics would still not establish independent scientific replication, robust lifelong cognition, generalization to real environments or AGI.
