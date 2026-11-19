# WSP-197 — Independent Olson 2014 GB1 55-site source admission

**Current result:** `SOURCE_IDENTITY_PINNED / ORIGINAL_BYTES_UNVERIFIED / SCIENCE_NOT_RUN`.

This is **not** a new training result. WSP-195/196 already tested the separate Wu 2016 four-position GB1 fitness landscape in [draft PR #1311](https://github.com/spoonman136668-ai/Yggdrasil/pull/1311), which is `PUBLIC_DEV_NO_GO`. Do not rescore, retune, reuse or alter that consumed holdout. WSP-197 seeks distinct original Olson 2014 GB1 *55-site* measurements of single and double mutants, with independently identifiable source records and a new evaluation contract.

## Original source custody and permissions

Read-only source commit: `lehner-lab/DMS2structure@3c1976b78a743d4d4c73921f047648500e671c8e` (original research data reprocessed in Schmiedel & Lehner, Nature Genetics 2019). The original repository's `GB1_pipeline.R` (blob `340d74803a2e0871264ca96f2bf1b94a1ea2bd70`) confirms the original filenames and required single/double/wild-type count columns. The original historical Olson 2014 measurements are not new causal interventions.

| Original file | Size, bytes | Git blob SHA-1 |
| --- | ---: | --- |
| `GB1/dataset/Olson2014_TableS2_doubles.txt` | 21,721,634 | `dc7ab871b69026fc5d7cb2f505cfe7f6dd36b950` |
| `GB1/dataset/Olson2014_TableS2_singles.txt` | 19,302 | `de650d218e3a2aa339fa14f2849060293daa0338` |
| `GB1/dataset/Olson2014_TableS2_wildtype.txt` | 43 | `f9fb047a2b25b0cde656f6d1760a89524b2bc665` |
| `GB1/dataset/GB1_sequence.fasta` | 61 | `c1d1deef50b769ccd6a8f7909aa6da66fada68d6` |

**Not verified:** actual original doubles bytes are too large for the current GitHub text-fetch connector (returned empty), and current raw-web download route failed. A listed Git SHA is a metadata reference, **not proof we accessed the source bytes**. Do not substitute earlier GB1 four-position source bytes or mirror, do not guess missing numbers. Original measurement-data reuse license needs verification apart from the repo code LICENSE; no original source data is copied into Yggdrasil.

## Bounded offline byte/metadata gate

The standard-library-only `source_admission.py` verifies **all four** exact original Git blob IDs using `SHA1("blob " + original_bytes_length + NUL + bytes)`, verifies original compressed file sizes, then reads only reference amino acid and first 3 or 6 genotype metadata fields from the source TSVs. It rejects duplicate or same-site genotype pairs, invalid reference positions/alleles, missing/changed source files and malformed schema; only aggregate site/single/double counts and independent SHA256 fingerprints enter the receipt.

It specifically does **not** parse numerical input, selection counts, existing author fitness columns, or held outcomes. Thus it cannot construct a model or calculate a score. **A PASS from this checker is source-byte/genotype metadata custody only, not scientific acceptance, first-use permission or full source preprocessing qualification.**

On an authorized local holder with the four *unchanged* original files in one directory:

```sh
python -m unittest -v test_source_admission
python source_admission.py --root /path/to/original-GB1-files
```

The six unit tests use **source-free** small synthetic fixtures and guard against genotype corruption, source modification, duplicate reversed pairs, same-site pairs and missing files. They are code only; **their execution remains UNVERIFIED** for this branch in the current tool route. No original-source admission, official Linux+Windows full regression, GitHub G29 or standalone scientific experiment has run. No self-hosted runner/owner lane was dispatched.

## What a subsequent scientific gate would need

Commit a completely new prospective preregistration **before** accessing numeric count/fitness values: fixed FIT/VALID/HELD independent mutation-pair identities, FIT-only score normalization and reference counts, exact seeds/splits/budgets, factorized shared native interaction weights that can predict *unseen* site pairs, independently fully fitted degree-2 ridge/low-rank kernel and nonlinear same-information controls, data/capacity/compute equivalence, cold serialization/retention before and after cumulative pair updates, a small frozen qualification budget and one held outcome test.

If original byte verification or contamination/license rights fail, STOP. No training reset or source relaxation, no SCIENTIFIC_PASS or native Yggdrasil integration claim, no original-world first-use, no accepted-ref edits, controller/queue/scheduler changes, merge or deployment.

**Current gate:** original source identity and author-defined metadata interface recorded, read-only code/tests committed; authentic offline source and engineering tests **not yet qualified**.
