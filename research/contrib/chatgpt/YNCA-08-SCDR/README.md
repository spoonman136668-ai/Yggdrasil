# YNCA-08 — a genuine sheaf obstruction, then one temporal-memory correction

**Classification: DEVELOPMENT_SIGNAL / SCIENTIFIC_SUPERIORITY_UNVERIFIED.** External, source-free SCDR research only; no native Yggdrasil model trained or promoted.

## Motivation

YNCA-06's Stage0 graph cycle was not a valid sheaf obstruction. This gate implements an actual **constant-F2 cellular sheaf on a three-edge cycle**, tests its defect detection under sensor noise, then makes **one targeted correction** when a real weakness appears. No open-ended tuning.

### Mathematically specified sheaf

The stalk at each vertex and edge is F2, and edge restriction maps are the identity. On vertices A/B/C, cochains C0=F2^3 and C1=F2^3, with coboundary

`d0(gA,gB,gC) = (gA xor gB, gB xor gC, gC xor gA)`.

There are four possible coboundaries; rank d0=2. The quotient H1=C1/im(d0) has dimension **one**. The XOR of three measured edge parities distinguishes its two cohomology classes. This is a real, explicitly defined algebraic obstruction to gluing a single consistent global vertex assignment—not a graph-cycle count masquerading as sheaf cohomology.

**Crucial limit:** A nontrivial obstruction is not automatically proof of a hidden physical variable. It could reflect contextual inconsistency, geometry, model misspecification, or noisy measurements.

## Source-free environment

Each of 24 time steps/world generates three independent random local gauge bits and a switching binary obstruction h(t). Observed edges are vertex-gauge differences with h(t) added to one closing edge, then independent 10% noise per sensor. A true obstruction survives vertex-gauge changes; observed parity flips with probability `q=0.244`. Hidden h switches with probability `0.08`.

160 separate training worlds supply a **fully supervised** two-state HMM control. The candidate's transition probability is derived **without hidden-state labels** from the rate of successive observed defect flips and known sensor-noise calibration. The exact Bayesian control receives the actual generator transition probability and noise, a privileged stronger comparator.

Every method receives the **same three edge observations per time step**. No additional interventions, privileged test labels, or paid model calls.

## Pass A — already consumed, exploratory

| Method | Mean Brier ↓ | Accuracy ↑ |
| --- | ---: | ---: |
| Exact Bayes | **0.12761882** | **82.68%** |
| Fully supervised raw-observation HMM | 0.12768446 | 82.60% |
| Sheaf with no temporal memory | 0.18642489 | 75.22% |
| Single-edge uninformative control | 0.25000000 | 48.83% |

Pass A demonstrated the sheaf invariance but failed to accumulate temporally correlated evidence. This was observed before this branch's GitHub preregistration, so it is **exploratory**, not confirmatory.

## Pass B — one correction, new frozen development worlds

Source and threshold were committed *before* inspecting 96 disjoint B worlds. The one correction introduced a noise-calibrated two-state temporal filter, with switching rate estimated from **unlabeled training** defect changes.

| Same 96 B worlds | Mean Brier ↓ | Accuracy ↑ |
| --- | ---: | ---: |
| Exact true-parameter Bayesian filter | **0.14922935** | 78.08% |
| **SCDR_B sheaf + self-supervised temporal memory** | **0.14941996** | **78.39%** |
| Fully trained supervised HMM | 0.15054122 | 77.86% |
| Original sheaf SCDR_A | 0.18931378 | 74.65% |
| Single-edge control | 0.25000000 | 50.87% |

Corrected SCDR Brier improves **21.1%** against A on the *same B worlds*. It is **0.13% worse** than the exact Bayesian oracle, slightly better than the supervised HMM, and meets the preregistered high-confidence noise-only false-positive cap: `0.00086806` (0.087%) at probability threshold 0.95. High-confidence sensitivity to true obstruction is modest (~20% of positive frames).

No independently tested significant superiority over exact Bayes or fully trained HMM is claimed. The two-state memory is mathematically Bayesian inference over a manually given sheaf invariant.

## Full evidence custody

- Accepted `main` at experiment fork: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, unchanged.
- Prereg before B: `18e5a1d57c918aa9593339dab0f4d862ec0b352b`.
- Source frozen before B at `749ff6e3d7ee1719bbbc11e62bbc942d8ebe7d3e`, SHA-256 `bec99d3b9f4123582de66cf823ca4dae286e18f0619b46457128aae7b20eebde`.
- Original B [GitHub Actions run #44297890044](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44297890044): **Linux 6/6 PASS and Windows 6/6 PASS**, byte-identical 2,231-byte output, SHA-256 `785bac870d5f9d949a0e5fe54ad30b5f6c3924b89e96895f0a069193f1951e0c`.
- Original B preserved in `result_B.json` at commit `431956114a105d5283b1c807d938e9a9f3ab5f97`; exploratory A in `result_A.json`; complete provenance in `provenance.json`.
- Reproduce in Python 3.12+ stdlib: `python -B -m unittest discover -s research/contrib/chatgpt/YNCA-08-SCDR -p 'test_*.py' -v`; `python -B research/contrib/chatgpt/YNCA-08-SCDR/experiment.py --split B`.

## Decision after two passes

**Preserve the useful sheaf invariant; stop tuning this exact source-free two-state implementation.** Pass B shows that a coherent, gauge-invariant structural feature plus temporal accumulation can nearly reach an informed Bayesian optimum without requiring labeled latent states. It does **not** demonstrate automatically invented world concepts or superiority over Bayesian HMM inference.

The next independent scientific hypothesis is whether a *learner can discover the sheaf structure/restriction maps itself* from unfamiliar observations, with less supervision/compute than a fully trained HMM/POMDP or symbolic structure learner—and retain/transfer that learned atlas. That requires its own preregistration, disjoint structured worlds and locked owner qualification; do not retroactively retune the consumed B.

No CKAD integration, controller, scheduler, model promotion or deployment. Full final source-indexed dual-OS regression can qualify the external research branch separately.
