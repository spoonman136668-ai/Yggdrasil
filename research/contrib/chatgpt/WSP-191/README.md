# WSP-191 — Norman GSE133344 offline source-admission gate

**Status:** Engineering implementation only; original GEO bytes **NOT ACQUIRED**, source cohort **NOT ADMITTED**, scientific result **NOT RUN**, native Yggdrasil integration **NONE**.

This isolated branch contains a read-only local-file checker for the four *filtered* GEO GSE133344 supplementary files. It does not download any data, open gene-expression matrix entries, learn weights, select pair splits, queue a job, or access protected original worlds. It never modifies accepted `main` or the WSP-190 draft.

## Independent references

- Original research: Norman et al. (2019), *Science*, DOI 10.1126/science.aax4438.
- Original public source: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344
- Original investigator code: `thomasmaxwellnorman/Perturbseq_GI@3b25109aeb9c0c2026bd70abd50304a0ad4e5395`.
- Expected compressed-file MD5 manifest (third-party archival source, **not** a GEO publisher signature): `datasets-mila/datasets--perturbseq--perturbseq_2019@6cf272024e0bf47010880b2660a10f092e57752e/md5sums`, blob `c12edbb4f4afd9ad0ff70fac7be9cca0a925e3d6`.
- The original author's design CSV has 105 gene identities, but includes `bulk_fitness` measured outcome values. Do **not** use those outcomes in splitting or as learner features.
- Prior WSP-190 frozen NO-GO: https://github.com/spoonman136668-ai/Yggdrasil/pull/1284. Protected source owner remains https://github.com/spoonman136668-ai/Yggdrasil/issues/426.

## Reproduction on a qualified, already-authorized local source checkout

From this directory, the source-free **engineering fixture** tests are:

```sh
python -m unittest -v test_source_admission
```

Only after a source owner has independently provided the original four filtered GEO files in a *local* directory, run the **read-only** byte/metadata validation:

```sh
python source_admission.py --root /path/to/filtered-geo-files
```

The checker SHA256/MD5-hashes each compressed source file, compares MD5 to the pinned third-party archival manifest, checks plain-text metadata structure/counts and checks the MatrixMarket header and declared dimensions. It refuses symlinks, corrupted or missing files, mismatched counts and size/drift anomalies, and it returns a JSON receipt. The checker **does not parse expression matrix numeric values**. It does not establish official GEO publisher-signature verification or a successful gene-pair join.

**PASS here is strictly byte-digest-and-metadata-shape custody.** Source admission still requires provenance/licensing, barcode-to-identity pairing, guide/condition/replicate keys and contamination audit; a prospective whole-pair protocol with matched full-trained controls; and separately authorized execution. Do not reuse external published pair-class evaluation labels to select a test split. Do not claim science or native training from synthetic fixture tests.

## Current outcome

- Read-only source-free **local engineering fixtures:** 6/6 PASS (both implementation and tests prepared in this session), **not** GitHub CI or full regression.
- Exact original source archive digests: **NOT RUN** — files unavailable from the active execution environment.
- Original-world first-use: **DENIED/NOT ATTEMPTED**, independent source-owner #426 unchanged.
- Accepted Yggdrasil `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` at branch creation, untouched.
- Source code and tests live only on isolated `research/wsp191-geo-source-admission-20261118`; no PR, no merge, no deployment.
