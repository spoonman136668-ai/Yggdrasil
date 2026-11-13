# DG1-SL04 — stronger conventional context and cold-retention challenge

**Preregistration:** frozen commit `7ca7da2595727ebf719d77c51c1c97be7c9d892c`, before this source or any SL04 results.
**Parent:** fully engineering-qualified draft SL03 PR #985, source `dacb637b034189029d6b22a885c63d520aedf1fd`.
**Scope:** isolated external synthetic research, not native Yggdrasil integration.

This challenge **does not revise SL03**. It compares its frozen selective consolidation and conventional offline/online controls against an independently coded **HMM-style two-bank online Bayesian hazard filter** over the same 40-rule/action grammar, and a strong bounded recent-window conventional version-space baseline. The HMM-style baseline is **not full Bayesian online change-point detection**, uses two extra continuous weights, and is not claimed to be capacity/compute identical. Frozen candidate returns cannot be explained as novel architecture superiority if conventional/selective/same-compute models tie.

The 24 precommitted worlds cover unlabeled A→B→A recovery, three-context interference exceeding the two-bank capacity, and cubic out-of-grammar transfer. All models see the **same actual paid 64-step trajectory per world**, including 8 paid physical flips and 56 learning-capable physical actions. No model receives the seed, regime label, transition oracle, or evaluator-only audits. Cohort labels exist only at evaluation time.

Evaluator full 64-pair audits are performed at physical steps 20, 40 and 64; the no-training unseen subset is separately scored. All negative/abstention/confident-error results must be preserved. Preliminary scientific classification is **UNVERIFIED**, until prospective execution and qualification.

Reproduce from repo root:
```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-sl04-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-sl04-20261113/sl04.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

Scientific outcomes, actual per-arm CPU/serialization sizes, source hashes, and full per-world receipts will be committed as `result.json` and `provenance.json` **in this repo**, never in a ChatGPT Library attachment. No protected science first-use, accepted ref/main/native model, controller, autonomous loop, Wingless, or parallel weight programming modification is allowed.

## SL04 frozen result — independent context challenge (2026-11-13)

**Scientific NO-GO / NEGATIVE_DEV:** prospective 24-world run [43498971634](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43498971634), identical deterministic audits on Ubuntu/Windows. Freeze: `7ca7da2595727ebf719d77c51c1c97be7c9d892c`. The full per-world traces (SHA-256), physical action counts, unseen-query metrics, abstentions and platform timing receipts are stored in [result.json](result.json) and [provenance.json](provenance.json).

| Final cohort | Frozen native SL03, correct/wrong | Conventional comparator |
|---|---:|---:|
| A→B→A return (512 queries) | 358 / 20 | Conventional selective replay 358 / 20 (tie) |
| Three-context capacity (512) | 219 / 191 | HMM-style online 222 / 186; conservative 12-per-action recent-window 18 / 10 (mostly abstains) |
| Out-of-grammar cubic (512) | 260 / 49 | HMM-style online 270 / 19; recent-window 313 / 53 |

SL03 improved over its original no-sleep learner on A→B→A (358/20 vs 304/44), but the **stronger offline conventional control tied**, meaning no native-specific gain. Under three-context interference and OOD, confident errors remain unacceptable. Primary gain over strongest conventional controls and error tolerances **failed**. The HMM comparator is a separate finite-context Bayesian hazard approximation, **not full Bayesian online change-point detection**; its two extra posterior confidence weights also mean exact capacity and whole-process compute matching are not established.

**Implementation:** unchanged frozen SL03 candidate plus independently coded conventional HMM-style and windowed controls; 1,536 paid real actions across 24 synthetic worlds; all 24 evaluator-only audits/cold restorations/receipts matched across Ubuntu and Windows. This is not evidence of AGI, novel rule acquisition, or a sleep timing effect.

**Engineering:** initial run had source-atlas G29 fail-closed on newly indexed files (not a scientific failure); the generation repair and full final source-SHA dual-OS qualification are separate from the frozen outcome. Do not merge or deploy this exploratory contribution.
