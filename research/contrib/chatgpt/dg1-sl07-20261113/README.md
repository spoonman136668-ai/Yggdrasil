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
