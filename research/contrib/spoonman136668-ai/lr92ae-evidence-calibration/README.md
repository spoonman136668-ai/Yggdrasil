# LR-92AE — Causal evidence budget versus posterior confidence

**Decision: EXTERNAL DEVELOPMENT NO-GO.** This is an independent synthetic research contribution, **not** Yggdrasil native training, official scientific acceptance, first-use, or deployment. The upstream LR-92AD negative result in [PR #1267](https://github.com/spoonman136668-ai/Yggdrasil/pull/1267) remains unchanged.

## Frozen boundary

- Preregistration was committed to GitHub **before scoring**: `fef29879832b283e2e94e15731e5bea9ba29ce2a`, `prereg.json` SHA-256 `70789ddcc70a8dc7097074119e8de31f8976af0ea14a7705435266a8380ac733`.
- New exact runner source committed next, **before scoring**, at `55433f6a07f8b0f7ad8349c961d9f5f449e87bfb`. Decoded runner SHA-256 `4f92fe04640e9c0a2f4b856274e6e49d760f4659629a4caf6a9a3c51434c664b`.
- Prior LR-92AD learner imported with source SHA-256 `32171291d945f7aedca941890b4137caef648a455bbb34a9c2478e3e36087b47`, historical 128-episode training SHA-256 `c5f5fcbe1a6e3d7f5b666a98c2d3f6dfd112399f0b8cbe3c1da58c3bcc6e0df2`, and trained-weights SHA-256 `de4a4369ad31c2000f28871e84361dbbdfc22c559854f3fe32fc1da826fec132`. No primary LR-92AD evaluation worlds reused.
- New world seeds 929200511, 929200512, 929200513, totaling 240 independent synthetic worlds (192 known contextual modes and 48 previously unseen contextual-mode assignments). Training base functions IDs 0–7 and evaluation base functions IDs 8–15 are disjoint; the underlying finite Boolean hypothesis grammar remains shared.
- Seven learners; 112 context-0 fitting observations fixed; context-1 fitting evidence as nested 16, 32, 64, 128, 256 observations; 256 independent validation observations per world. Each policy sees the same data at each budget.
- **Acceptance never relaxed**: maximum posterior ≥0.90 and fitting-only binomial misfit survival probability >0.01. Validation outcomes never determine acceptance. Confidence calibration uses five frozen bins and exact-MAP correctness.

## Main result — nine of ten frozen criteria passed, but the result is NO-GO

| Context-1 fitting observations | Exact accepted familiar / 192: learned relation | Uniform Bayes | Learned relation MAP correct / 240 | Learned relation held-out accuracy | Learned relation confidence ECE |
|---:|---:|---:|---:|---:|---:|
| 16 | 0 | 0 | 107 | 61.78% | 0.15099 |
| 32 | 0 | 0 | 125 | 62.45% | 0.08014 |
| 64 | 15 | 4 | 150 | 63.17% | 0.03425 |
| 128 | 62 | 35 | 180 | 63.84% | 0.03497 |
| 256 | 86 | 66 | 202 | 64.45% | 0.02283 |

At the **frozen primary 64-observation level** the learned relation beat uniform (15 versus 4 accepted familiar mechanisms), pooled global memory (7), and shuffled-context memory (6). It also beat the strongest fully trained conventional predictor by more than the preset 0.5 percentage-point threshold, and its confidence ECE of 0.03425 satisfied the ≤0.10 requirement. **Nevertheless, the original GO required at least 20 more accepted familiar mechanisms at budget 64 than budget 16. It recovered only 15 more.** Classification remains `DEVELOPMENT_NO_GO`, with no postscore threshold change or additional scored cohort.

At budget 64, the new learner selected the right full truth table in 150/240 worlds **before confidence filtering**, but accepted just 17/240: 15 correct familiar, one correct unseen, and one false unseen. In 134/240 worlds it selected the correct truth table yet assigned it less than the preregistered 90% posterior confidence. This is a *postscore diagnostic*, not accepted knowledge. At budget 128 it made two false familiar acceptances; at 256, three. Increasing evidence increases both fitting cost and acceptance, not necessarily safety in every world.

**Plain-language interpretation:** Too little contextual evidence is a real bottleneck in this controlled model. Additional interventions let existing learned relations become more decisive without changing thresholds. That does not mean model-native Yggdrasil can yet learn or transfer general causal mechanisms, and calibrated confidence over this restricted 256-hypothesis grammar may not remain calibrated on genuinely unfamiliar worlds.

## Engineering and custody

- **Pre-primary structural checks:** 7/7 PASS, with no reserved primary seeds evaluated before the GitHub preregistration.
- **One primary scored cohort:** 240 worlds × 5 evidence levels × 7 arms = **8,400 model/budget decisions**, original raw `primary_result.json` is 13,028,601 bytes, SHA-256 `7b94587fafbf9ce2fcc4de84c594b1a02c9137a7c9cead39d928c30dbe0676b0`.
- **Independent read-only auditor:** 87,493 assertions PASS, 4.77 seconds; recomputed the likelihoods, posteriors, classification, confidence calibration and aggregate scores from the original untouched observations. Exact decoded audit source SHA-256 `b9853604ab4d50862a93866bddae0c61f4aa92e01ed3d281d4e9f2eda3d7a887`; audit receipt SHA-256 `00d0696ce5098b9fe8fd3ab966be0bd2280e902cbaf923cfb8705fee45c7e555`.
- **GitHub includes** preregistration, zlib/base64-compressed exact runner and auditor, aggregated `result_summary.json`, `audit_result.json`, `provenance.json`, the bounded scored ledger, **and the complete original raw evidence** stored as `primary_result.json.zlib.b64`. The decoded bounded ledger SHA-256 is `c6abd673de6dc6704b0f296a3be1531322c4f501ffe985331b349d083c0cbb3a` (46,392 bytes). It contains 64-budget seven-arm outcomes and the full five-budget candidate curve, **not** raw fitting/validation observation arrays.
- **GitHub now contains** the original 13.03-MB per-observation primary result in a lossless 571,709-byte zlib/base64 encoding, SHA-256 of encoded file `42e2623025167dfce6157054273ee52cfde15f384a5ce2c6994e9f99bdc41bb8`. GitHub readback of this full encoded file matched that checksum; local decompression matched the 13,028,601-byte original raw SHA-256. Independent cross-host execution remains unverified.
- Local Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0. Full one-shot script wall 5.88 s, including 0.055 s historical model training; this is **not** an end-to-end Yggdrasil intelligence or runtime gain.

## Independent reproduction

For **read-only analysis of the published original raw evidence**, decode it without running the primary experiment:

```bash
python -c "import pathlib,base64,zlib;p=pathlib.Path('primary_result.json.zlib.b64');pathlib.Path('primary_result.json').write_bytes(zlib.decompress(base64.b64decode(p.read_text())))"
sha256sum primary_result.json # expect 7b94587fafbf9ce2fcc4de84c594b1a02c9137a7c9cead39d928c30dbe0676b0
```

For **independent recomputation on the frozen seeds**, use a **fresh isolated directory** with `prereg.json`, the two `*.py.zlib.b64` files, and the exact predecessor LR-92AD source from [PR #1267](https://github.com/spoonman136668-ai/Yggdrasil/pull/1267):

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0 pytest
python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_text())))" lr92ae_run.py.zlib.b64
python -c "import base64,zlib,pathlib,sys;p=pathlib.Path(sys.argv[1]);pathlib.Path(str(p).removesuffix('.zlib.b64')).write_bytes(zlib.decompress(base64.b64decode(p.read_text())))" audit_readonly.py.zlib.b64
# Similarly decode the exact LR-92AD lr92ad_run.py.zlib.b64 from PR #1267
python lr92ae_run.py               # refuses to overwrite an existing primary_result.json
sha256sum primary_result.json      # expect 7b94587fafbf9ce2fcc4de84c594b1a02c9137a7c9cead39d928c30dbe0676b0
python audit_readonly.py           # expect 87493 checks PASS, no primary data-generation replay
```

The original scientific first-use was not consumed. The Yggdrasil source atlas (G29) currently rejects new indexed contributor `.md`/`.json` files because its existing pinned source identity excludes them. This is an **engineering CI source-index issue**, separate from the NO-GO scientific outcome. Do not weaken its integrity checks or merge/promote this draft without owner-controlled qualification.
