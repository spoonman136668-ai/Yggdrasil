# WSP-194 — KRAS cumulative weight programming, real measured fitness

**Result: `PUBLIC_DEV_NO_GO`**. The experiment used historical measured KRAS mutational fitness in six independent *readout assays* but one source family, not new physical interventions or native Yggdrasil training. Original biological assay source CSVs are **not copied into this repo**.

## Hypothesis and original data custody

Can persistent site-state weights learned from measured KRAS single mutations be extended with one-pass local pair-residual writes to predict previously excluded multi-mutation genotypes better than a fully converged pairwise ridge control with the exact same FIT data and pair-coordinate dictionary?

Original public author dataset: `luo-group/SynFit@4a11c268b5719ea3c64459a5bb5b4f3a45f0b09a`. Two original CSVs:
- `dataset/KRAS_data/KRAS_6_binding_single_mutation.csv`: Git blob `064c356b09ba9a951a9e635f78aecc9c8fd32c74`, **764,573 bytes**, 2,417 unique single mutants.
- `dataset/KRAS_data/KRAS_6_binding_multi_mutation.csv`: Git blob `13fadeb5ca181a041d7c432c2728df673153410c`, **4,226,513 bytes**, 13,229 double mutants (every multi-mutation row was exactly two-site, confirmed after scoring by **metadata-only** count).
- Six target/readout columns: **RAF, PI3, RAL, SOS, K27, K55**. Distinct measured binding targets are **not six independent biological source worlds**.
- SynFit repository code MIT; underlying original fitness-data usage and redistribution terms require independent confirmation. No data bytes are redistributed, and no private/paid source was used.

**Frozen before values**: [`prereg.json`](./prereg.json) first commit `5ea08782aacd270b69c56f6393532d46d622cc06`. Frozen [`evaluate.mjs`](./evaluate.mjs) original commit `ed38e37b349148aad1e5a24ff03075c10402ad11`, exact Git blob `5260f172880c5836f494ab076efa989ca4122192`. [Source-free focused tests](./test_evaluate.mjs) committed before first scoring; [pre-score qualification](./pre_score_qualification.json) commit `e963843d009f768a8ff7022e643e1b93e009c513`. **One primary original-source DEV score**, sealed at commit `1189e7d07390671b6710facef37f11658341c14d`, unchanged afterward.

## Method / experiment

The evaluator inferred the 187-residue reference sequence from majority identity in the single-mutation source (no numerical labels needed for reference inference), encoded differences as native position:amino-acid state features, and assigned **whole genotypes** by one frozen SHA256 salt: 70% FIT, 15% VALID, 15% DEV.

Every assay passed its preregistered minimums: 1,690 observed FIT singles, 9,379 FIT doubles, 1,945 VALID doubles, 1,905 DEV doubles. Single mutation weights are stored and frozen during pair learning. A single pass writes residual corrections to observed FIT pair coordinates, with `beta`/penalty chosen only on VALID.

Strong conventional comparison: same FIT single and double labels, normalization, genotype split, feature dictionary and memory coordinates; converged pairwise ridge coordinate descent for lambda 0.1/1/10, plus additive-only and shuffled-FIT-residual negatives. All declared conventional ridge models converged. The selected strongest baseline on VALID was additive-only in every assay.

## Held DEV results — lower normalized RMSE is better

| Assay | Programmed candidate | Strongest trained conventional baseline | Candidate beta | Gain |
| --- | ---: | ---: | ---: | ---: |
| RAF | 1.221100 | 1.221100 (additive) | 0 | 0% |
| PI3 | 1.115207 | 1.115207 (additive) | 0 | 0% |
| RAL | 1.092577 | 1.092577 (additive) | 0 | 0% |
| SOS | 1.034851 | 1.034851 (additive) | 0 | 0% |
| K27 | 1.186156 | 1.186156 (additive) | 0 | 0% |
| K55 | 1.155731 | 1.155731 (additive) | 0 | 0% |

Every assay's 1,000-replicate variant-level bootstrap difference is `[0,0]` because the candidate and additive comparator predicted identically, **not** because a real scientific advantage was established. No independent improvement, no efficiency gain or new-world causal reasoning demonstrated.

### Decisive postscore, *outcome-free* structural diagnosis

The [separate source-only structural receipt](./postscore_genotype_structure.json) was collected **after sealing the primary score**, solely from genotype identities; it does not rerun predictors or use numerical held outcomes. It shows:

- Every multi-mutant in this source comprises **exactly two mutations**.
- FIT contains 9,379 observed pair-identity coordinates for 9,379 FIT double mutants.
- **VALID: 0 of 1,945** genotypes have any pair feature available from FIT.
- **DEV: 0 of 1,905** genotypes have any pair feature available from FIT.

This means a direct program that stores one residual per observed pair has **literally no addressable learned pair coordinate** for any unseen genotype. No parameter tuning can repair that model class under the same split. Both the direct program and conventional pairwise ridge fall back to frozen additive single features. The next distinct hypothesis should use *factorized shared interactions of single-site features*, tested against fully fitted standard low-rank/bilinear controls on a NEW disjoint source, not rescore these 1,905 DEV variants.

The single-mutant retention RMSE before/after pair stage is identical by construction because single weights never move. This is **not** independent cold-restored retention, persistent native cognition or multi-task interference learning.

## Read-only source reproduction

If an independent researcher already has both exact original author CSV bytes available locally, the evaluator is a pure JS function:

```js
import { readFileSync } from "node:fs";
import { evaluateWSP194 } from "./evaluate.mjs";
const result = evaluateWSP194(
  readFileSync("/authorized/source/KRAS_6_binding_single_mutation.csv", "utf8"),
  readFileSync("/authorized/source/KRAS_6_binding_multi_mutation.csv", "utf8")
);
```

Ensure original bytes match the Git blob identities before execution. Reproduction with unseen run environment and exact results **not yet independently qualified**. Do not perform extra primary DEV scoring for successor model selection.

## Qualification / authority

- **ENGINEERING:** frozen exact-source V8 **19/19** source-free focused assertions PASS. Authenticated source bytes and admission for all six assays PASS. Full dual-platform repository regression / independent qualified GitHub CI **UNVERIFIED**; no claim of source acceptance or build.
- **SCIENTIFIC:** frozen public-development result **NO-GO**, `scientific_pass=false`. No model generalization benefit, no independent new-world learning, no evidence of cold retention.
- **DEPLOYMENT:** NONE. No original protected source owner [#426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) first-use, autonomous controller, accepted-main mutation, merge/promotion, paid API, or live action.

This negative result must be retained without re-tuning the public held DEV pool. It is a measured model-class coverage failure, **not** a failure of all future direct or factorized weight programming.
