# YNCA-07 — two-pass compositional Popperian falsifier

**Result: DEVELOPMENT_MIXED.** A real, bounded source-free Minimalist + Falsifier prototype was implemented and tested twice. This is not the full internal coevolutionary IPFC engine or native Yggdrasil intelligence.

## Actual mechanism

The Minimalist maintains the least-complexity causal program consistent with observations. A Falsifier synthesizes an alternative compositional Boolean world from a fixed 59-program grammar that agrees with verified observations but disagrees with the Minimalist on a candidate intervention. Only actual source feedback updates survivors and the falsifier's per-world family preferences—dreamed outcomes never become witnesses. All arms have 2 passive observations and up to 4 intervention probes, each costing 0.02.

The **single targeted Pass B correction** stopped pursuing lopsided contradictions and instead favored balanced candidate-world splits, while retaining a small evidence-updated family preference. This correction was written and source-locked *before* B was evaluated.

Controls were exact uniform Bayesian EIG, Bayesian EIG with a trained 64-world Dirichlet-smoothed prior, fixed probes, random probes, and the unchanged Pass A implementation on the same B worlds.

## Results

| B development arm, 128 new worlds | Mean 16-action Brier ↓ | Correct bits ↑ |
| --- | ---: | ---: |
| IPFC_B balanced falsifier | **0.09410943** | 73.73% |
| Fixed probing | 0.09720486 | **79.69%** |
| Uniform exact EIG | 0.09743245 | 73.83% |
| Prior-trained exact EIG | 0.10187826 | 73.34% |
| Random probing | 0.10471498 | 76.86% |
| IPFC_A uncorrected | 0.12233724 | 73.44% |

On the separate, already-consumed A exploratory cohort, IPFC_A had Brier 0.12379710 versus uniform EIG 0.10074870, and no positive signal.

**Interpretation:** The one targeted correction cut Brier from 0.12233724 to 0.09410943 on the *same B worlds* (23.1% lower error). It beat B's best conventional control by 3.18% Brier, but the frozen threshold required at least **5%**, with no more than **2 percentage points** loss of bit accuracy. Compared to fixed probing, accuracy fell **5.96 percentage points**. Hence the original B acceptance conditions failed; this is a bounded promising diagnostic, not a qualifying new intelligence mechanism.

**Disposition:** Do not spend multiple further passes tuning this IPFC algorithm or reuse B/its reserved untouched cohort to fish for significance. A genuinely new hypothesis—such as learning new primitive operators, source-grounded family memory or decision-aware counterexample value—would require a new independent experiment and baseline.

## Evidence custody

- Accepted `main` parent `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, unchanged.
- Original prereg `c35981ca44d9d5f6b9b57e0f787abea97735ef98`; source-bound freeze before B `5c5b2f37d987f8e75ffaddf12e36ea92cbc40524`.
- Frozen source `e5ee9031ff1cef63ef50c1c6f6ec0f89bf92997b`, SHA256 `ae1df1d71754d8d0449dcd2b5f48275e25f1b54b36cb9cb623644684aed0245c`.
- [Original independent dual-OS B run #44293196873](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44293196873): Linux/Windows 7/7 focused PASS each, byte-identical result SHA-256 `f8c0d79c33927727846e772f945d198c638a399ea25b77a57c223c7d58b2066a`.
- Original result saved unchanged in `result.json`; exact custody and limitations recorded in `provenance.json`.
- Python 3.12+ stdlib reproduction: `python -B -m unittest discover -s research/contrib/chatgpt/YNCA-07-IPFC -p 'test_*.py' -v` and `python -B research/contrib/chatgpt/YNCA-07-IPFC/experiment.py --split B`. This reproduces already-consumed B data, *not* a new scientific result.

### Scope

The fixed grammar already contains every true causal program; no out-of-grammar novelty or generalization is proven. The agent only adjusts per-world falsifier preferences, not an autonomous evolved model. No native Yggdrasil model weights, CKAD source, owners, schedules, controllers, protected first-use or deployment were altered. Full final cross-platform inherited regression must be verified separately before engineering qualification.
