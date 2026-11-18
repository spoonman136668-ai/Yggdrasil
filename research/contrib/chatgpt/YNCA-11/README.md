# YNCA-11 — Two-operator memory under interference and causal composition

**Result: FROZEN DEVELOPMENT_NO_GO for the evidence-gating correction; ungated two-slot memory showed measurable synthetic retention and composition gains.** No native Yggdrasil training or scientific acceptance.

## Scientific question and limits

YNCA-10 learned one finite Boolean operator and transferred its table memory to new input permutations. This follow-up asks whether **two learned operators can survive alternated training, be retrieved after interference, and be reused to predict an unobserved two-stage composition**.

Every operator is chosen from the same fixed 24-function 3-input Boolean truth-table grammar, and input-role permutation is hidden for each world. The two labeled contexts **A/B are supplied** to every fitted learner, so context discovery is *not* demonstrated. The compound task is explicitly specified as `C(x) = B(A(x),x1,x2)`; composition algebra is also *given*, not autonomously invented.

Each cohort trains with 16 interleaved small worlds in sequence `AAAA-BBBB-AAAA-BBBB`, each offering 4 noisy action outcomes (12% independent flips). All evaluations use 64 new worlds per A (cold return after B), B (recent context) and C (unfamiliar composition). Single tasks allow 3 observed actions; composition allows **2**, and predictions are scored only for unobserved action assignments.

## Matched controls

- **LAST_B_OVERWRITE:** Replace A storage with the learned B posterior, revealing catastrophic overwriting
- **SHARED_UNTAGGED:** Fully fit one pooled posterior from all the A/B data, ignoring supplied context tags
- **NO_MEMORY:** Exact untrained uniform posterior over 24 candidates for each operator
- **TRAINED_FREQUENCY:** Fully trained per-context frequency baseline using all 16 worlds
- **TWO_SLOT_TOP3:** Two separately trained context posteriors, storing only the top three operator tables per context
- **FULL_CONTEXT_BAYES:** Full exact context-separated 24-table Bayesian posterior for each operator, given precisely the same observations
- **GATED_TOP3:** Proposed Pass B correction: compare stored memory versus no-memory prior using Bayesian evidence from the same two new composition outcomes; mix predictions with 50/50 prior odds
- **GATED_FULL_BAYES:** Identical evidence gate but allowing complete full Bayesian memory
- **ORACLE_TABLE:** Privileged true operator tables; must still infer per-world role permutations; diagnostic only

No extra observations, hidden answers, model calls, capacity upgrades or outside information are supplied to the actual learner.

## Pass A — exploratory, already consumed

| A world diagnostic | Brier ↓ |
| --- | ---: |
| Return to A: two-slot memory | 0.19517037 |
| Return to A: last-B overwritten memory | 0.31895454 |
| Composition: ungated two-slot | 0.21402614 |
| Composition: evidence-gated two-slot | 0.19425172 |
| Composition: no memory | **0.18865013** |
| Composition: gated full Bayes | 0.19131024 |

The evidence gate improved composition on these **already inspected exploratory worlds**, but still underperformed no-memory. One fixed correction, unchanged source and preregistered thresholds were then frozen before B first-use. A is **not** confirmatory.

## Pass B — first-use, source-locked independent development

| Policy (64 new worlds per task) | Return A Brier ↓ | Recent B Brier ↓ | New composition Brier ↓ |
| --- | ---: | ---: | ---: |
| Last-B overwrite | 0.13323888 | 0.12740946 | 0.19280740 |
| No memory | 0.22421778 | 0.23826310 | 0.23401509 |
| Full context exact Bayes | 0.07846513 | 0.12740946 | 0.18291118 |
| **Ungated two-slot top3** | **0.07807697** | **0.11800380** | **0.16618257** |
| **Evidence-gated top3** | 0.07807697 | 0.11800380 | 0.19051315 |
| Evidence-gated full Bayes | 0.07846513 | 0.12740946 | 0.20030368 |
| Privileged true tables | 0.07420618 | 0.08252543 | 0.07972578 |

**Positive underlying mechanisms:**

- Context-indexed storage reduced cold-return A error **41.4%** relative to overwriting the first operator with the second.
- Ungated finite two-slot memory reduced unseen-composition Brier **29.0%** versus the no-memory Bayesian baseline. On these particular worlds it also scored below the 24-table full Bayesian control (0.16618 versus 0.18291). This is an observed cohort difference, *not* a statistically supported claim of superiority over the strongest learner.
- The representation contains **three learned operator tables plus weights per context** (6 entries), versus full exact memory with 24 per context (48 entries). No measured end-to-end efficiency improvement is claimed.

**Negative corrected mechanism:**

The observation-evidence gate **increased** composition Brier from 0.16618257 to 0.19051315, **14.64% worse**. Its frozen admission rule required a **10% improvement**, which failed. Other retention and Bayes-parity checks passed. The exact gate is classified **DEVELOPMENT_NO_GO**, not relabeled mixed or promoted. **Stop this source and do not tune the B cohort again.**

## Exact GitHub custody

- Accepted main parent: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, untouched.
- Initial prereg `7b6e26fd7231fbcd4eca0aec5947bfa92bb2aa83`.
- Frozen source commit `b6443a349a4c2838efa47ef5a31d5c467fa8efc4`, SHA-256 `70d38215a4cba3419c3d706d9c5078a3de56e28f2bf895c3de9c0be847de874a`.
- Source-bound prereg **before B**: `38d9d3b4274d5e11f8e16cc05a9d6c18236e6fea`; focused tests source SHA256 `d9b1c8a6f5522b740674fcce12e59b952a0a93be67c572f45737c1d71dbc9180`.
- [Original B run #44319945553](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44319945553) **Linux/Windows 9/9 focused tests PASS each; exact 1,661-byte B output byte-identical**, SHA256 `7077e47ca08684ec71861f124e8c44b8445a795678c03e3aef06c63f550053d7`.
- Original output archived unchanged in `result_B.json`, commit `b96e1aedf531e0de04820939068c6e7ce63caaa6`. `result_A.json` is explicitly exploratory. Original model memory SHA-256 reported as `c956d24c7367e012928f157b0d51fd7bba3cbf9586dab54806125bc6695a3e9b`.
- Exact result, full source and limited conclusions are preserved in `provenance.json`; final inherited/G29 regression to be qualified separately.

Reproduce in CPython 3.12 standard library:

```bash
python -B -m unittest discover -s research/contrib/chatgpt/YNCA-11 -p 'test_*.py' -v
python -B research/contrib/chatgpt/YNCA-11/experiment.py --split A
python -B research/contrib/chatgpt/YNCA-11/experiment.py --split B
```

**B is already consumed**; reproduction does not become an additional independent evaluation.

## Decision and next research hypothesis

The failed evidence gate should **not** receive another tuning pass. The **ungated** two-slot memory, however, warrants an independently preregistered successor studying *unknown context discovery, previously unmodeled composition rules, longer interference chains, and multi-operator cold retention*, with matched fully trained symbolic/Bayesian controls and measured whole-process costs. Retain this negative outcome unchanged.

This contribution never edited CKAD's integrated learner, native Yggdrasil weights, accepted state, owner runtime, controller, scheduler, scientific first-use datasets, or deployment.
