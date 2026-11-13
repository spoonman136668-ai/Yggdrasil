# DG1-SL07 — contradiction witnesses before paid causal interventions

**Protocol frozen before implementation/outcome:** `27d0ad88fdb64dda815cfb248cf47faf8b2f8e5a`. Parent: qualified but scientifically negative SL06 PR #988 at `30f57be961c15915fd1ad1d58f2d39cadf93d581`.

This source-only experiment tests whether a **context-switch witness**—a paid physical observation that contradicts the active learned mechanism and is consistent with a distinct retained one—is sufficient reason to spend subsequent paid actions selecting discriminating interventions. A two-distinct-event trigger prevents treating one ordinary prediction surprise as proof of a changed world. The original non-token SL05/SL06 learners, causal-rule grammar, and physical world semantics are unchanged.

Seven arms include the contradiction-triggered native memory learner, original always-active and passive controls, a deliberately noncausal sham-trigger control, confidence-gate ablation, an independently implemented Bayesian-style conventional contradiction trigger, and conventional always-active. All worlds are new preregistered seeds. Every arm gets the same 60 physical steps and is cold restored before selecting actions on its own paid physical branch. All 32 worlds × seven arms × 80 paid steps = 17,920 charged actions, with 15,680 causal observations and no free simulator calls. The action choices diverge after restart; even though the physical budgets match, **the information acquired and CPU cost differ**. All full 64-state/action evaluator-only audits are held out from learners.

The frozen result threshold requires return-to-A and return-to-B coverage gains against the strongest alternative controls *and* no material confident-error increase in stable or unfamiliar-world cohorts. An untriggered candidate or worse generalization is a negative result, not a reason to retune thresholds.

To replicate from repository root (Python 3.12 stdlib):

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-sl07-20261113 -p "test_*.py" -v
python research/contrib/chatgpt/dg1-sl07-20261113/sl07.py
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build_code_atlas.py --check-if-present
```

Source, outcomes, per-world physical SHA-256 receipts, cold-restoration tests and dual-OS CI must remain directly on GitHub. No ChatGPT file attachments. **No main, native Yggdrasil model, accepted ref, autonomous controller/loop or other research line changes. No scientific first-use, deployment or merge.**

## SL07 frozen prospective outcome (2026-11-13)

**Scientific NEGATIVE_DEV / primary NO-GO.** A prospective seven-arm, 32-world, real-paid-action comparison completed at exact source `ec3543ac93b4ecde14f7b88743bbaa3fe19ef827` in [run 43509015952](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43509015952). All 17,920 paid physical actions (15,680 actual causal action observations) were charged, the first 60 actions were identical before cold restore within each world, then policy-dependent arms diverged. No evaluator truth was used to learn. No thresholds, physics or model policy were changed following the first outcome.

| Final cohort / 512 evaluator-only queries | Native witnessed correct / wrong | Native passive correct / wrong | Strong conventional witness correct / wrong |
|---|---:|---:|---:|
| ABCA return A | 234 / 28 | 203 / 34 | 280 / 33 |
| ABCB return B | 327 / 22 | 332 / 23 | 365 / 29 |
| Stable old world | 370 / 0 | 370 / 0 | 370 / 0 |
| Out-of-rule fourth context D | 118 / **102** | 53 / 29 | 117 / 92 |

On the stationary cohort, the always-active native and conventional controls reached **504 correct / 0 wrong**, substantially above the witness-gated 370/0. On ABCA, witnessed intervention fired in only **3 of 8 worlds**, failing the preregistered four-world minimum. ABCB was 4/8, OOD 5/8, stationary 0/8. Although witnessed actions improved ABCA correct coverage over passive (234 vs 203), they fell below the separately coded conventional witness model (280); the strong conventional always-active baseline achieved 279 correct/101 wrong on ABCA, showing a real coverage/precision tradeoff. On the OOD cohort, 102 wrong-confident predictions exceeded the passive 29, violating the frozen safety bound.

The two-distinct-physical-contradictions gating concept **did not** satisfy robustness, safety, or independent-conventional superiority. No AGI, native Yggdrasil learning superiority, or sleep timing claim follows. Full per-world audit, unseen-state/action prediction counts, trigger activations, prequential physical prediction receipts and physical SHA-256 trace custody remain in [result.json](result.json); [provenance.json](provenance.json) records the prereg and source/CI receipts. Ubuntu/Windows deterministic science matched on every world; checkpoint lengths also matched, while compute timings differ.

**ENGINEERING:** Initial dual-OS focused and original study runs succeeded; inherited full regression and G29 atlas acceptance failed because the generated source index was stale after adding SL07 files. An atlas-only follow-on commit and final full exact-source qualification are still required. This is an engineering indexing issue, not a scientific failure.

**Disposition:** Keep draft/unmerged. No protected first-use, main, native Yggdrasil accepted model, autonomous research loop/controller, Wingless, FORGE or weight-editing mutation. No ChatGPT Library artifacts.
