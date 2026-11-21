# FCR02 DEV: independent public-stage conditioning-mask selection — NO-GO

## Question and custody

Can stage-separate prequential selection of input-conditioning masks cheaply recombine previously witnessed causal relationships without a monolithic context archive? This is **source-free developmental screening only**, not a new canonical Yggdrasil learner, source actor, accepted checkpoint, or scientific first-use.

- Parent coordinator: [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) at `86264b41a08d49f558418c0fba367f3a2636befa`.
- Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` (unchanged).
- FCR01-S cost negative: source-subset `07b0e0322afba132befa9ed9eed4b763613b98bb`, **5.462× native CPU** (>2×), preserved on its own branch.
- FCR02 prereg **before outcomes**: `e4d152ed1d7cb2e07bc1e3f0c5c24283a30905e3`. Source/test/trial commit `669c442c56c6c92a82e45a15b78d3f8445e722b8` later; this source commit followed the local exploratory execution, so **DO NOT treat as confirmatory precommitted code evidence**.

## Implementation and method

`mask_index.py` has independent per-stage Q1e6 integer Jeffreys-Beta sufficient-statistic counters for 2 transition masks and 8 terminal-reward masks, with public interventions always conditioned upon. Prequential Brier updates choose minimum accumulated risk with smaller-mask deterministic tie breaking. Readouts are supposed to be pure (a fixture negative initially caught and fixed a mutating-defaultdict on read **before outcome execution**). No hidden phase signal, oracle, teacher, new source acquisition, trained parameters or cross-project controller. After each public episode the fixture-only adapter updates its counters; no authenticated native admission API or original-source custody is claimed. Serialized sidecar is source-pinned, and `restore` recomputes every count from its supplied immutable public fixture ledger.

`test_mask_index.py` has **7/7 local Python 3.13 tests PASS**: read purity, evidence ordering, cold replay, duplicate/conflicting ID refusal, tamper/false-scientific-claim refusal, input masks and a nonidentifiable correlated-joint counterexample.

`dev_trial.py` follows the frozen deterministic SHA256-based public-action fixture and synthetic A, B, C generator (64 rows each; four new seeds `215001..215004`; total **768 development observations**). The candidate never receives the phase label. C recombines A's transition and B's reward laws. Matched controls are fully fitted full-history Jeffreys-Beta, pooled Jeffreys-Beta, and trailing-32 fully fitted Jeffreys-Beta. Outcome Brier is prequential. The per-arm CPU numbers are local Python pure-fixture only; **not** native regression.

## Preset gate: **DEV_NO_GO**

| On recombined C (lower is better) | Candidate FCR02 | Best matched control |
|---|---:|---:|
| Transition Brier | 0.08021770 | 0.08021770 (full-history) |
| Reward Brier | 0.28100103 | 0.03847833 (trailing 32) |

Candidate rewards underperform best matched control by **+0.24252270 Brier**. All four seeds selected transition mask `[0]` and reward `[0,1,2]` at end; this selector retained full reward conditioning instead of switching appropriately. This observation is diagnostic **not** permission to tune the consumed seeds.

Four independent candidate cold checkpoints: **1,504–1,510 bytes**, exact fixture-ledger replay PASS. For the 768 rows (four cohorts), local process CPU totals: candidate **0.00820366 s average/cohort**, full-history control **0.00033467 s average/cohort**, trailing-32 **0.00035303 s average/cohort**. Timings are too small for a native CPU-limit claim and only show higher pure-Python fixture overhead. **Native 2× CPU gate UNVERIFIED**; full two-OS final regression NOT RUN.

## Reproduction

From this exact branch root (Python 3.12+ stdlib):

```bash
cd research/contrib/chatgpt/CAUSAL-AMALGAM/FCR02
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_mask_index.py
PYTHONDONTWRITEBYTECODE=1 python dev_trial.py > /tmp/fcr02-result.json
# Compare non-timing metrics and reproduce full receipt; CPU numbers vary by platform
```

Saved `result-summary.json` is readable JSON with each seed's metrics. `dev_result.json.gz` is the complete original local JSON result (deterministic gzip mtime=0), whose uncompressed bytes SHA256 is `3642ed7355f1b1c2ec896a701972e51e3f5db2fbbc6e6c2b1b2b93d3033002b1`; this archive includes local nondeterministic CPU timing and must **not** be byte-compared with a rerun.

## Disposition / authority

- **ENGINEERING:** source-free 7 focused local tests PASS; 768 synthetic event check PASS; native ABI, full test suite, exact final cross-OS candidate CI, archive owner custody UNVERIFIED.
- **SCIENTIFIC:** DEV_NO_GO versus strongest matched reward control; no original-world first-use, disjoint science, learned transfer, cold scientifically measured improvement, independent reproduction or SCIENTIFIC_PASS.
- **DEPLOYMENT:** NONE, no merge, no external actor, no paid APIs, no workflows or owner runner. This branch is frozen negative evidence, not an alternative Yggdrasil canonical learner.
- Do **not** repeat consumed seeds `215001..215004` as if new. Do not adapt the rule to these outcomes and reuse the same data to claim new science. A truly different mechanism needs new preregistration, disjoint source, stronger controls, independently qualified owner and budgets.
