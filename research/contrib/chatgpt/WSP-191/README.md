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

The checker SHA256/MD5-hashes each compressed source file, compares MD5 to the pinned third-party archival manifest, checks plain-text metadata structure/counts, checks the MatrixMarket header and declared dimensions, and validates filtered matrix barcodes against the author's cell identity mapping (`cell BC`, `cell_BC`, or `cell_barcode`) and `guide_identity` assignments. It rejects duplicate identifiers, orphan cell identities, ambiguous join keys, missing assigned guides, source file drift, symlinks, corrupted or missing files, mismatched counts, and size anomalies. Its JSON receipt includes only aggregate join counts, not individual cell IDs or guide identities. The checker **does not parse expression matrix numeric values**. It does not establish official GEO publisher-signature verification or a successful gene-pair cohort/split classification. Exact original file bytes still must be supplied and independently verified before the join can actually be executed on research data.

**PASS here is strictly byte-digest-and-metadata-shape custody.** Source admission still requires provenance/licensing, actual archived file hashes and source-dependent join results, intervention pair/condition/replicate identities and contamination audit; a prospective whole-pair protocol with matched full-trained controls; and separately authorized execution. Do not reuse external published pair-class evaluation labels to select a test split. Do not claim science or native training from synthetic fixture tests.

## Current outcome

- Read-only source-free **local engineering fixtures:** **12/12 PASS** on Python 3.13.5/Linux, on code bytes matching the isolated branch Git blobs (6 earlier checks + 6 join/identity checks), **not** GitHub CI, dual-OS qualification, or the mandatory full final repository regression.
- Exact original source archive digests, actual barcode/guide metadata join, and source cohort: **NOT RUN** — original GEO files unavailable from the active execution environment.
- Original-world first-use: **DENIED/NOT ATTEMPTED**, independent source-owner #426 unchanged.
- Accepted Yggdrasil `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` at branch creation, untouched.
- Source code and tests live only on isolated `research/wsp191-geo-source-admission-20261118`; no PR, no merge, no deployment.


## Next metadata-only gate: canonical gene-pair cohorts (conditional)

The investigator's original [GI_generate_populations notebook](https://github.com/thomasmaxwellnorman/Perturbseq_GI/blob/3b25109aeb9c0c2026bd70abd50304a0ad4e5395/GI_generate_populations.ipynb) specifies a crucial distinction the original byte checker alone cannot make: take \`guide_identity.split('__')[0]\`, then split the two gene/negative-control components by \`_\`. Double-negative controls are controls, one negative control is a single-gene intervention, and two distinct gene identities are a true pair. Apply the exact author's \`RHOXF2\` to \`RHOXF2B\` correction; never infer pair identity from an expression outcome or archived interaction labels.

After and **only after** authentic four-file source-byte verification:

\`\`\`sh
python cohort_protocol.py --root /path/to/filtered-geo-files
\`\`\`

The source-gated \`cohort_protocol.py\` defines a frozen, value-independent SHA-256 assignment of *whole canonical pair IDs*: 70% FIT, 15% VALID, 15% DEV, after excluding pairs missing either single-gene parent. No DEV label, guide ID or per-cell barcode is printed; only aggregate counts and hashed roster. It requires at least 40/8/8 independent pair IDs in the three buckets. Insufficient evidence fails closed, with **no** new salt, split rebalancing, post-result cohort selection, or weaker requirement. This is a public-development holdout within one K562 source family, not a virgin blinded scientific result.

\`source_gated_protocol.json\` records the conditional direct-weight composition hypothesis, full-trained matched conventional baselines, leakage exclusions, effect and retention metrics, frozen admission thresholds and required remaining gates. It explicitly **is not a fully executable scientific preregistration**: exact capacity, training seeds and baseline convergence contracts remain to be frozen before any expression outcomes are inspected.

\`\`\`sh
python -m unittest -q test_cohort_protocol
\`\`\`

**Exact-source focused cohort tests:** 8/8 PASS twice under local Linux/Python 3.13.5 with distinct hash seeds; the test module isolates the parsing/split logic using a source-free stand-in for imports from the already separately tested \`source_admission\` module. New executable/test Git blobs \`e14b0ff578d8e42ae6e44eaae18bc36d77694bd2\` and \`8e7889b396f91091f1c6d382f21ed8d38f217297\` matched \`git hash-object\` on those exact locally tested bytes. **No combined end-to-end GEO test, Windows test, full repo regression, CI, real-source admission or science run is claimed.**

Do not promote the conditional protocol or treat a good source-free score as meaningful evidence of biological causality, retention, general intelligence or native Yggdrasil integration.
