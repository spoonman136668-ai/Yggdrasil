# DG1-SL06 — paid discriminating actions after cold memory restoration

**Frozen preregistration:** `2d3e530cf21e0a87596246eff648832c66737058` before source and result.

SL05's conservative three-bank memory reduced confident errors but failed to beat conventional controls on old-context retention. SL06 isolates a distinct causal question: *Can a learner use physical interventions to distinguish its retained memories after cold restart, rather than waiting for a fixed stream of observations?*

The seven arms include native active selection, native passive and random controls, a no-confidence-gate ablation, an independently coded conventional posterior-weighted active learner, its passive equivalent, and the frozen two-bank predecessor. The original SL05 three-bank and HMM inference code are unchanged. Every intervention is a **real paid causal action** whose effect changes its own physical world. There are **no free simulator probes**.

The first 60 paid steps of every arm are identical; every model is cold serialized/restored at 60. Then its physical trajectory may diverge due to action selection, unlike SL05/SL04's identical-trajectories design. Each of 32 prospectively registered physical worlds runs 80 paid steps per arm (10 paid exogenous flips and 70 genuine causal observations per arm/world). The full study costs 17,920 actual paid actions across seven arms, not 2,560 shared actions. Since later interventions differ, the *information obtained differs*, even with equal budgets. Report cost/bytes separately, do not claim equal compute.

Evaluator-only 64-pair audits at 60/64/72/80 include unseen state-action pairs and prequential actual action results. No learner receives hidden phase, seed, physics oracle or evaluator answer. Frozen primary thresholds demand improvements over **the strongest** of native passive, native random and independently coded conventional active control without inflated confident error. Synthetic DEV cannot establish AGI, a native-substrate advantage, sleep-specific improvement, or independent scientific acceptance.

Reproduction (from repository root):

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-sl06-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-sl06-20261113/sl06.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

All evidence, frozen negative outcomes and source qualification receipts belong **on GitHub only**. No main/native model/accepted refs, protected scientific first use, research controller, scheduled work, deployment or other research lines are modified. This PR stays draft and unmerged.
