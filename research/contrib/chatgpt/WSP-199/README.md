# WSP-199 — Original GFP ortholog source admission (metadata only)

**Status: SOURCE_METADATA_VERIFIED / SCIENTIFIC UNRUN.** This is a new, disjoint source-admission branch; not a preregistered model evaluation, an accepted Yggdrasil branch, native training, or an attempt to replay WSP-194 / WSP-196 / WSP-198 held data.

## Exact original source
- Somermeyer et al., *Heterogeneity of the GFP fitness landscape and data-driven protein design*, eLife 2022, DOI: https://doi.org/10.7554/eLife.75842.
- Upstream `aequorea238/Orthologous_GFP_Fitness_Peaks@799bd76889918bf1551c60016fb23278024cac73`.
- Original `data/final_datasets/amacGFP_cgreGFP_ppluGFP2__final_aminoacid_genotypes_to_brightness.csv`: Git blob `ee1d9d885a36e2d88b049f92e3af7bf90833ddad`, **8,069,873 ASCII bytes**, independently computed full-byte SHA-256 **`41eb96cbaba255e64f4d229b20f6e53bf2e512ba0953bc032697e7b82c6f3ca8`**.
- Data definitions: [original upstream data README](https://github.com/aequorea238/Orthologous_GFP_Fitness_Peaks/blob/799bd76889918bf1551c60016fb23278024cac73/data/README.md). Four-background reference FASTA Git blob `1b8f459eb35b400a6b8b3b3dd4e4f4b49cb6e382` (971 bytes). The primary CSV is the **three new backgrounds** (not avGFP).
- Root repository [license](https://github.com/aequorea238/Orthologous_GFP_Fitness_Peaks/blob/799bd76889918bf1551c60016fb23278024cac73/LICENSE) states GPLv3. Underlying measurements' redistribution/derivative rights are **not independently resolved**. **No raw upstream data or code copied to Yggdrasil.**

## Exact genotype-only audit (no brightness labels used)
- 93,925 genotype records: amacGFP **35,500**, cgreGFP **26,165**, ppluGFP **32,260**. No duplicate `gene + pseudo genotype` keys and no row-structure parse failures.
- Strict standard-residue two-mutation records with observed parent singles: **10,822 / 9,517 / 15,717**, respectively (36,056 total), across **7,789 / 7,396 / 10,335** distinct within-background unordered site-pair groups (25,520 total).
- The original CSV also contains stop/nonstandard genotypes and higher-order mutations. The strict subset is **a proposed eligibility check only**; its final inclusion/exclusion policy, target transformation, reproducible splits and primary scoring must be committed in a separate prereg **before model use of fluorescence labels**.
- Original full CSV was retrieved solely to recompute SHA-256 and inspect the first three genotype/identity columns. Its numeric `total_cell_count`, `n_replicates` and `replicates_mean_brightness` columns were **not parsed, printed, fitted, or scored** in this admission. No numerical result was generated.

## Proposed successor and hard stops
Candidate: fixed-capacity native/tokenless shared interaction factors with bounded, feedback-gated direct-weight corrections and durable cold restarts, on **previously unseen site-pair groups**. Fit strong conventional ridge/bilinear and equal-capacity controls to the same source observations; preserve no-update spectral, shuffled, random-gated and always-update ablations. Freeze seeds, group splits, evaluator, capacity, compute and thresholds **before** any original outcome use. Never recycle consumed WSP-194 / WSP-196 / WSP-198 DEV labels as unseen. Three backgrounds from one paper are **not independent scientific worlds**.

**Scientific first use: NOT AUTHORIZED/NOT RUN.** No Yggdrasil owner #426 action, autonomous loop, queue, runner, controller, accepted-main write, merge or promotion. This branch contains only a source-admission receipt.

## Reproduce byte identity without copying it into Yggdrasil
Obtain the pinned original CSV from upstream; verify Git blob SHA-1 `ee1d9d...` via `git hash-object <file>` and full-file SHA-256 `41eb96...` via `sha256sum <file>` or `Get-FileHash -Algorithm SHA256`. Verify genotype-only counts and guards before any result or prereg. If original bytes differ: **fail closed**.
