# LR-92AB: preregistered evidence-gated causal-memory falsification

**Disposition: DEVELOPMENT NO-GO.** External synthetic research contribution only. This is not Yggdrasil native training, general causal intelligence, accepted science, scientific first-use, integration, or deployment.

## Source and frozen boundary

- Yggdrasil parent commit: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`
- Preregistration committed **before primary scoring**: `129339cd21d566a123bb83680568ecb45f24a360`
- Frozen `prereg.json` SHA-256: `3cc0272b162cdcd50d60d746c20cb081cb3a19475fd0fbad48088bc5e6f6d396`
- Original one-shot runner `lr92ab_run.py` SHA-256: `06d817e340b2fcf485533b6781edde7524bb851e95c436e8eb4f61fede3a94a7`
- Original independent audit `audit_lr92ab.py` SHA-256: `ec07152377893dae4cefc00c6d82ca3c3e4120aba64dfd6f5c2130e2a04e731e`
- Seed 929200201; 80 new synthetic worlds: 52 stationary, 12 regime switches, 8 foreign hidden-cause, 8 null.
- Each arm receives the same 144 fitting interventions and 288 separate validation interventions per world; 35% outcome flip noise; 16 fixed Boolean two-cause truth tables.
- Input learned prior derives from recovered historical LR-92AA development evidence; its 16 exact float64 values are frozen directly in `prereg.json` (SHA-256 `c6fb2451be0e7f9907a45e20c068614da41bcef462a8035d5236d6c15e2cbfc9`).

## Method

Compare fixed historical-memory, fixed uniform, reversed-memory and random prior-choice controls, alongside CART and RF16. The candidate compares marginal fit evidence after the *first 36 fitting observations* and retains historical memory only when the Bayes factor is at least two. All Bayesian learners then fit a fixed 144 observations. None of the policies can inspect validation labels before fitting.

The conventional classifiers do **not** use the Bayesian posterior-acceptance cutoff, so their counts are descriptive, not an equal-acceptance scientific superiority comparison.

## Primary results (one frozen run)

| Arm | Exact stationary mechanisms / 52 | False constructions | Accepted foreign/null |
|---|---:|---:|---:|
| Evidence-gated memory | 36 | 1 | 0 |
| Fixed historical memory | 29 | 5 | 0 |
| Uniform prior | 36 | 1 | 0 |
| Random memory gate | 34 | 2 | 0 |
| Scrambled historical memory | 31 | 3 | 0 |
| CART | 48 | 8 | 0 |
| RF16 | 48 | 8 | 0 |

The gate retained historical memory in only 8 of 80 worlds. It recovered seven more exact stationary mechanisms than always using the historical prior, but recovered **zero more than the uniform prior**. The primary preregistered GO required at least three more exact identifications than uniform, with all the other safety criteria met. It failed.

No post-result retuning, new scored cohort or reclassification was conducted. Result is **DEVELOPMENT NO-GO**, not an infrastructure failure.

## Independent audit and reproducibility

The independent, read-only audit checked 5,242 fields: prereg/source hashes, action balance, prior identities, marginal-likelihood gate, Bayesian posterior scores, validation misfit, true/false classifications and aggregate summaries. **PASS.** An initial auditor-only strict argmax check was corrected to accept numerically tied posterior maxima; the original runner and result bytes were unchanged.

Original local primary result `result.json`: 1,023,625 bytes; SHA-256:
`c7d195a115169926988cd9ad0e369728f7fd846fc99b0814519ca90685118566`.

**Important distinction:** The `result.json` committed to GitHub is a compact *summary*, not the original 80-world raw result. The raw primary result bytes have not been uploaded. GitHub contains exact frozen runner and audit source, frozen protocol, result summary, audit receipt, and provenance. It does not yet contain the full source predecessor archives or the original raw cohort. Source can be independently re-executed to produce the raw cohort, subject to matching pinned dependency versions and floating-point tie behavior.

To reproduce **in a fresh throwaway directory**, not inside the checked-out contribution directory (which already contains the summary named `result.json`):

```bash
mkdir -p /tmp/lr92ab-repro
cp research/contrib/spoonman136668-ai/lr92ab-memory-gate/{lr92ab_run.py,audit_lr92ab.py,prereg.json} /tmp/lr92ab-repro/
cd /tmp/lr92ab-repro
python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0
python lr92ab_run.py > run_stdout.json
sha256sum result.json    # expected c7d195a115169926988cd9ad0e369728f7fd846fc99b0814519ca90685118566
python audit_lr92ab.py  # expected PASS, 5242 checks
```

Primary scored run used Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, local Linux CPU. Cross-platform byte-identical reproduction, official owner CI and the original 427-test predecessor full regression are **UNVERIFIED**.

## Limits and disposition

This exercise exposed additional world assignments but did not introduce new causal mechanisms outside the original Boolean grammar. The transferred prior was not updated through native Yggdrasil training. Do not generalize the outcome to JEPA, persistent native memory, unfamiliar-world transfer, or native learner integration.

Historical LR-series intake: PR #1256 (UNPREREGISTERED). LR-92AB prospective external experiment: PR #1257. Neither PR is a scientific acceptance or promotion request.
