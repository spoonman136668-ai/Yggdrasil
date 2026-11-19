# WSP-193 — Protein G direct-weight composition: first source gate INVALID

**Decision:** `INVALID — SOURCE_GENOTYPES_INSUFFICIENT`. No native Yggdrasil training or measurable scientific comparison was executed. This is an independent protein-fitness source probe, **not** a retune of the WSP-192 negative result.

## Actual source

The original historical measured data are the Protein G mutational-fitness assays of Olson (2014) and Wu (2016), assembled as `luo-group/SynFit@4a11c268b5719ea3c64459a5bb5b4f3a45f0b09a/dataset/multi_fitness_data/SPG1_STRSG.csv`, exact source Git blob `ee5df92d6c1e070c2876fbe7d27cf3a440c83e37`, file size **725,365 bytes**. The repository's code license does not by itself establish independent redistribution rights for the published experimental fitness values. No source data is copied into Yggdrasil.

After preserving the first fail-closed result, an independent **metadata-only** roster count established **1,458 unique genotype rows total**, consisting of **76 single-mutation and 1,382 multi-mutation records** (76 distinct substitution feature labels). Counts do not establish per-assay target availability; this metadata audit intentionally did **not** inspect or score original numerical fitness values.

## Exact provenance and stop rule

- Original research preregistered **before any source numerical outcome rows were read** at Git SHA `231e0f0989a6b90f032822e744ff040b9fc56724`.
- A frozen source-study correction, **before any numerical outcomes were opened**, was committed at `1b99dea1fe8192279abe2fa5b20ebd4d95bbdbc4`. It corrected an impossible uniform ten-site requirement for the independently known four-site Wu (2016) source; Olson retains the ten-site requirement.
- Frozen evaluator was committed at `3316067296499d0116c5e5284ea4bd7020fc6024`, Git blob `bc6517419f06544f2a5f96e30ab49830bb042c89`.
- Prior to opening original outcomes, source-free focused fixture checks of the exact evaluator+tests Git blob passed. These fixtures are engineering checks, not scientific data.
- On the **first real-source admission attempt**, the exact 725,365-byte Git blob was authenticated and the evaluator rejected the complete dataset under the preregistered requirement of **at least 1,500 distinct genotypes**. **1,458 is below 1,500 by 42.** Stop reason `SOURCE_GENOTYPES_INSUFFICIENT`. No fitted weights, validation selection, DEV model scoring, bootstrap, hypothesis success or failure.
- First invalid result was **committed immediately**, before this explanatory readme, at `43314646e93052686a39cd5176df52a9ec8e704c`. The frozen `result.json` is NOT to be replaced.
- **No lowering the threshold to 1,458 or less, no same-dataset retune or replay.** This is an invalid source admission, not a direct-weight program scientific loss.

## Planned but NOT executed scientific comparison

Tokenless site-state weight programming with a persistent additive site effect scaffold and one-pass direct pair-weight writes, against fully fitted additive and polynomial pairwise-ridge baselines, independent model training on Olson-2014 and Wu-2016 assays, variant-identity-wide FIT / VALID / DEV partitions and equal-compute source constraints. All of those remain *proposed*, not scientific results.

The next admissible scientific source must have sufficient independently verified raw provenance and data richness **before any outcome inspection** to meet its own preregistered minimums. Do not reuse this source's already-opened outcome file as if it were a new virgin holdout. A separate public-development exploratory question would require a new, clearly non-confirmatory design and must not retrospectively repair this preflight.

## Engineering / scientific / deployment

- **ENGINEERING:** isolated script+fixture focused PASS before primary attempt; authentic source digest identity PASS; authentic source **admission FAIL** under frozen minimum size. No CI, Linux+Windows full repository regression or independent G29.
- **SCIENCE:** `INVALID`; no causal transfer, retention, model convergence, direct-weight benefit or negative treatment effect established.
- **DEPLOYMENT:** NONE. The WSP-192 frozen developmental NO-GO in [draft PR #1299](https://github.com/spoonman136668-ai/Yggdrasil/pull/1299) and accepted Yggdrasil main remain unchanged. Original protected-world owner [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) is not authorized for virgin first-use.
