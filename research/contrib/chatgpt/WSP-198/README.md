# WSP-198 — Original Olson 2014 GB1 whole-site-pair transfer

**Frozen outcome: `PUBLIC_DEV_NO_GO`.** Source admission and evaluation were completed against actual historical 55-site single/double-mutant counts. This is **not native Yggdrasil training, SCIENTIFIC_PASS, general intelligence, independent action learning or production deployment**.

## Why this experiment was different

Prior [WSP-196](https://github.com/spoonman136668-ai/Yggdrasil/pull/1311) used Wu's 2016 **four-position** GB1 landscape, and remains a frozen negative; no held outcomes were reused. The [WSP-197 original source-admission branch](https://github.com/spoonman136668-ai/Yggdrasil/tree/research/wsp197-olson-gb1-55site-admission-20261119) admitted the separate **Olson 2014 55-position** double-mutant historical count source and recorded exact source fingerprints.

From `lehner-lab/DMS2structure@3c1976b78a743d4d4c73921f047648500e671c8e`:
- Double mutant original Git blob `dc7ab871b69026fc5d7cb2f505cfe7f6dd36b950`, 21,721,634 bytes.
- Single mutant original Git blob `de650d218e3a2aa339fa14f2849060293daa0338`, 19,302 bytes.
- Wildtype original Git blob `f9fb047a2b25b0cde656f6d1760a89524b2bc665`, 43 bytes.
- GB1 reference original Git blob `c1d1deef50b769ccd6a8f7909aa6da66fada68d6`, 61 bytes.
- **4/4 original source SHA-1 IDs independently recomputed and matched**, and separate **SHA-256 digests** recorded in [WSP-197/original_source_receipt.json](https://github.com/spoonman136668-ai/Yggdrasil/blob/research/wsp197-olson-gb1-55site-admission-20261119/research/contrib/chatgpt/WSP-197/original_source_receipt.json).
- Source data was read by GitHub's Git-blob endpoint, **not copied into this research branch**. Repo software MIT licensing does not alone establish separate publication-data redistribution rights.

## Frozen source and development protocol

The [preregistration](./prereg.json) was committed at `27d658bc52b1282b00dc5cd7a0f7461cd99daa19`, **before any Olson 2014 fitness/count values were used to train or score this experiment**.

- Original verified genotypes: **1,045 single mutants** and **535,917 doubles**, covering **55 mutated positions**.
- Each independent **unordered site pair** was assigned deterministically to FIT/VALID/DEV using preregistered SHA-256. **Entire site-pair combinations were held out**, not individual mutant rows.
- FIT **1,060 site-pair groups / 382,536 genotypes**; VALID **235 groups / 84,818 genotypes**; DEV **190 groups / 68,563 genotypes**. No DEV labels used in FIT normalization or validation selection.
- Original integer input/selection counts converted to a fixed `log((selection+0.5)/(input+0.5))` effect normalized by wildtype, then subtract the two measured single-mutant effects to form a pair epistasis residual. Only FIT double residuals supplied normalization.
- **Candidate:** no-gradient directly programmed *shared spectral mutation factors*, rank 2 or 4, evidence-selected alpha in `[0,0.5,1,2]`. Crucially, this model can produce interactions for entirely unseen site pairs; it is not a per-pair lookup table.
- **Strong conventional controls:** fitted additive ridge and fully trained rank 2/4 regularized bilinear ALS factorization (same original FIT data and mutation features), plus FIT-mean, alpha=0 and shuffled FIT-residual negative controls. Hyperparameters chosen by VALID only; un-converged ALS variants remain diagnostic, not qualified controls.
- **Primary metric:** each held site-pair's variants contribute their mean squared error, with equal weight for the **190 independent held site pairs**, followed by RMSE and 2,000 group-bootstrap resamples.

The initial source-free fixture found a mutable-counter coding error, disclosed at commit `5db30750532caa8f917db35bf6c49ef6c5edfc7f`. It was fixed **before exposure to original numeric training outcomes**. Frozen final evaluator commit `8070a1ea3bafaa769a509392117ea1727fc63be3`, exact blob `f4af822a019eb87f2c11f3dfe6228af8a97f1f58`; a synthetic-only integration pass and five negative cases were recorded at pre-score commit `6a2e5086fedd2f913a7db703d16b4bc01c0836e2`. No postscore code or split changes.

## One authentic result

| Model | VALID normalized RMSE | HELD normalized RMSE | Notes |
| --- | ---: | ---: | --- |
| **Converged conventional bilinear ALS** | **0.463162** | **0.464386** | Rank 4, λ=10, 45 sweeps, 8,360 adjustable factor parameters |
| Direct spectral programmed weights | 0.655795 | 0.691282 | Rank 2, alpha 2, 2,090 factor parameters |
| Shuffled FIT-label negative | 1.100704 | 1.133636 | Validation chose alpha 0 |
| Alpha=0 ablation | N/A | 1.133636 | No interaction information |
| Additive ridge (λ=1) | 0.829217 | **NOT REPORTED** | VALID diagnostic; held additive result was not saved |

**Relative held RMSE gain:** `-0.4885929594484253` — the direct spectral program is **48.9% worse** than the strongest converged conventional control. The site-pair-bootstrap 95% confidence interval for relative improvement is **[-64.0%, -37.0%]**, favoring conventional.

Of the conventional ALS variants, rank 2 λ10 converged after 40 sweeps and rank 4 λ10 after 45 sweeps. λ1 variants did not converge within 50 sweeps; their validation metrics must not be used to establish superiority. This experiment does not establish strict parameter/capacity parity: the winning conventional baseline used 8,360 factors versus 2,090 for the candidate. It disproves **this frozen method's** promised superiority under the preregistered stronger comparator, not all spectral/direct weight programming.

### Research and retention boundaries

- **First authentic numeric scoring:** exactly one attempt, sealed in [`result.json`](./result.json), first result commit `e43ab3192999f13965fbf7d28038ddaea7506585` and original result Git blob `5990c877b725a50f3814a71c71f0105d45a31972`. The surrounding code tool timed out after the GitHub result write; it was **verified persisted before any possible replay**, and no replay occurred.
- **Measured internal evaluator runtime:** 290.464 seconds, of which 77.323 seconds preceded completion of source parsing and spectral processing. External data acquisition, RSS, and full experimental cost not measured; no efficiency gain claim.
- The 1,045 single effects survived JSON roundtrip with zero absolute numerical drift. This is a *structural freeze/serialization diagnostic*, not an independently cold-restored long-term memory test, nor interference learning.
- Candidate eigenvalues and parameter counts are stored, but the complete trained spectral factor matrix was **not saved as a durable native-model checkpoint**; cumulative Yggdrasil knowledge was not modified.
- This is public, previously measured within-GB1 developmental evaluation. **No SCIENTIFIC_PASS, native model integration, unfamiliar biological-family transfer, original-world first-use, autonomous controller operation, merge or deployment**.

## Qualification and next mechanism

**ENGINEERING:** WSP-197 exact-blob nine source-free local Python tests PASS; authenticated original source SHA-1/SHA-256 and genotype admission PASS. WSP-198 synthetic V8 smoke and negative cases PASS. Full repository Windows/Linux regression, original-data independent execution, G29 and acceptance **UNVERIFIED**.

**SCIENCE:** `PUBLIC_DEV_NO_GO`. Preserve the negative without tuning or re-scoring these consumed DEV site-pair groups. Future hypotheses should test compact *shared causal state factors* with better inductive bias and matched compute/capacity on **independently new data or a genuinely new reserved intervention**, not reuse WSP-198 DEV as an unseen benchmark.

**DEPLOYMENT:** NONE. Yggdrasil accepted `main` and protected original first-use owner [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) unchanged.

Exact code: [`evaluate.mjs`](./evaluate.mjs); [`pre_score_qualification.json`](./pre_score_qualification.json); [`provenance.json`](./provenance.json). No source raw data redistributed.
