# YNCA-02 — when every causal expert is wrong

**Result: EXPLORATORY DEVELOPMENT NO-GO.** Independent of CKAD's integrated learner and YNCA-01; this is source-free toy causality research only. It does not use an LLM or alter the Yggdrasil owner model.

## Research question

Can a tokenless native context-dependent failure memory predict when observational, interventional and proxy-adjusted causal experts *all* make the same wrong decision, rather than simply reweighting their votes? All experts share the same generated observations and interventions. The referee can inspect only their predictions and observable sample metadata; it cannot inspect the hidden cause, latent confounder, or outcome label at inference.

## Frozen-comparison design and evidence

- Parent: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Prereg commit `aacb92cfa0ce82e467effa32f8e96eebbe8b73cc`.
- Source committed as `af324ae296f2273cb66547cdf5c4c5bbdc180db7` after the local first heldout run. Source SHA-256 was already observed in the local DEV output, but the source commit was not an adequate pre-first-use custody boundary. The prereg input hash was a placeholder. **Therefore the heldout remains exploratory/UNPREREGISTERED for confirmatory purposes**, despite the seed split and fixed metrics.
- 4096 synthetic train worlds, 1024 exploratory shifted dev worlds and 2048 shifted heldout worlds from disjoint seeds. Three deterministic experts, local 48-cell sparse failure-memory with shrinkage, trained confidence-only calibration, trained ridge logistic, global, disagreement and random controls.
- Target metric: failures among the retained 80% of cases (lower is better), plus Brier, AUROC and fixed 1000-draw paired bootstrap.
- Local Python 3.13.5/Linux: eight focused tests PASS and two heldout reproductions byte-identical.

## Local 2048-world heldout

| Comparator | Wrong-all-experts rate at 80% coverage ↓ | Failure AUROC |
|---|---:|---:|
| Confidence-calibration baseline | **0.04212454** | **0.62278535** |
| Contextual native failure memory | 0.05555556 | 0.56482873 |
| Global rate | 0.06043956 | 0.50000000 |
| Fully trained fixed ridge logistic | 0.06776557 | 0.48484650 |
| Disagreement-only diagnostic | 0.07264957 | 0.25453603 |

Failure prevalence was 119/2048 = 5.81%. Native minus best baseline **+0.01343102** absolute failure risk; baseline-minus-native paired bootstrap 95% interval **[-0.02014652, -0.00549451]**. Native is worse than simple confidence calibration. This **falsifies the superiority prediction for this implementation**; it does not invalidate the larger idea of native causal arbitration. No post-result tuning, no retroactive promotion.

## Reproduce (development only)

From repository root with Python 3.12+ (tested on Linux/Python 3.13.5):

```bash
python -B -m unittest discover -s research/contrib/chatgpt/YNCA-02 -p 'test_*.py' -v
python -B research/contrib/chatgpt/YNCA-02/experiment.py --heldout > result-reproduced.json
sha256sum result-reproduced.json
```

Expected source SHA-256: `e35bd55aef5c6839c2e9ebd773454b888ed5431faddab3e8d525a60c9c45c467`. Expected result JSON SHA-256 on verified local environment: `70a3e2cf27822de88c0085ba9fdd3ed270d03ee8648a56ce145b6cc2df88b721`.

## Technical interpretation and next direction

The sparse context buckets learned from edge votes and sample metadata did not add information beyond a coarse global confidence calibration. They may also overfit scarce all-experts-wrong cases (~6%). More training worlds alone are not justified. A useful separate follow-up is to obtain *new evidence* through independently randomized, discriminating interventions when every expert is simultaneously confident; evaluate utility net of intervention cost against exact Bayesian and confidence-only abstention controls.

**ENGINEERING:** focused local 8/8 PASS; G29/full dual-platform qualification UNVERIFIED. **SCIENCE:** exploratory development negative, not SCIENTIFIC_PASS. **DEPLOYMENT:** none. Keep this negative unmerged and distinct from the CKAD model.
