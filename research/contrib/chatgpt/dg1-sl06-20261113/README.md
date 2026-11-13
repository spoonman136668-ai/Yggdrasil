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

## SL06 outcome — frozen paid causal interventions (2026-11-13)

**Scientific classification: NEGATIVE_DEV / primary FAIL.** Prospective run [43505562622](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43505562622), preregistered before implementation at `2d3e530cf21e0a87596246eff648832c66737058`. The 32-world, seven-arm study executed **17,920 paid physical actions** (15,680 genuine cause/action observations). The first 60 physical steps per world were shared across arms; after cold restoration at step 60, learner-selected interventions changed each arm's trajectory. It is **matched physical action budget but not matched information or whole-process compute**.

| Final cohort (512 evaluator-only queries) | Native active correct / wrong | Native passive correct / wrong | Independently coded conventional active correct / wrong |
|---|---:|---:|---:|
| ABCA return A | 167 / 28 | 239 / 61 | 295 / 59 |
| ABCB return B | 176 / 68 | 158 / 12 | 318 / 61 |
| Stationary A | 490 / 0 | 386 / 0 | 486 / 0 |
| Fourth unfamiliar context D | 116 / **103** | 89 / **7** | 195 / **176** |

The native active learner made more **correct early, on-policy post-return physical action forecasts** (91 vs native passive 57 and conventional active 53 in ABCA), but these were evaluated on *different chosen actions*. They must **not** be interpreted as equal-difficulty, paired predictive capability gains. Final held-out full audits exposed degraded return-context generalization and substantial confident errors on OOD. The most conservative random/passive controls abstain more; their low errors cannot be compared without reporting coverage. The frozen final-accuracy, transfer, and safety criterion FAILED.

The full `result.json` preserves original 32-world × 7-arm prospective prediction histories, evaluator-only 60/64/72/80 audits, unseen-pair coverage, charged physical trajectory SHA-256 receipts, post-cold physical action selections, exact per-arm checkpoint sizes and both platforms' measured CPU/update times. `provenance.json` seals independent Ubuntu/Windows identical deterministic scientific metrics. Source tests and full cohort passed both OS before G29 stale-source indexing caused **separate** inherited regression failure; final G29-only update and exact source regression remain independently required.

**Scientific limits:** Three-bank candidate did not beat strongest conventional active selector; no evidence for general reasoning, AGI, causal memory improvement, learned context discovery, sleep timing, or superiority of Yggdrasil's native substrate. Freeze this negative; do not tune thresholds, seeds, or physical action policies afterward. Remain draft/unmerged and outside the native model or autonomous research loop.
