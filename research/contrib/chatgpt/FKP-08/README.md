# FKP-08 — Bounded shared-memory causal contradiction/retention falsification

This is an **isolated contributor experiment**, not Yggdrasil native accepted state. It follows Issue #1088 and FKP-05 through FKP-07 development outcomes. FKP-07 demonstrates that prior causal associations help against weaker priors but tie a same-information exact Bayesian control; it did **not** establish an active-policy or native-model advantage.

## Frozen objective

Can direct numerical state weights hold 32 independent 8-bit causal contexts, accept three contradictory version updates in each context using **16 actual consequences/version**, retain *every* previous version's predictions without allocating entire new 256-state arrays, and outperform strong equal-information conventional inference/compression?

Preregistration was committed **alone** at `fb96e9763565d8db956fd1d1bf719b45b0e1dcf4`, before original source, algorithm, regression or first DEV result. Accepted Yggdrasil main remains `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.

## Actual mechanism

The source owner privately creates 32 arbitrary true 256-state base causal response maps. Every base map is learned from **all 256 real state interventions** (32×256=8,192 genuine actions). Each of three successive revisions XORs two unknown two-input conjunction motifs selected from the same source-public set of 112 possible indicators (6,216 possible pairs), potentially contradicting previous results. No motif indices are handed to learner.

An 8-bit state generates one binary effect. Each revision publishes 128 source-public candidate interventions, permits **16 distinct paid consequence observations**, and keeps 128 disjoint states for held testing. A hypothesis-search learner selects the lowest-error two-motif patch consistent with public feedback, stores a pair of numeric learned motif indices and updates a shared 32-byte base bitmap. All prior revisions can be reconstructed by folding cumulative patches; previous-rule predictions are sealed before new version observations. Cold checkpoints verify SHA-256 and reject corruption.

**Raw learned numerical weights = 32 contexts×32-byte base +32×3×2-byte patches =1,216 bytes**, excluding checksum/header metadata. An equal-information conventional delta-coded model has the exact same representation and predictions. Independent strong marginalization over all minimum-error candidate pairs predicts probabilities using only the same paid observations. Conventional zlib9 compressed full 4-version bitmaps and compressed numeric patch checkpoints are measured; **no false unique benefit over ordinary compression** is permitted.

The source function family is finite and known to all arms. This is *not* open-ended invention of unforeseen physics or native Yggdrasil weight modification. Protected primary 1800..1863 and negative 2800..2815 require external owner key and are **never opened**. Tests use disjoint synthetic fixture context IDs 700..703; original DEV IDs 800..831 are never used in preflight tests. A Python attribute boundary is not independent owner-run security.

## Reproduce at exact SHA

```console
python -B -m unittest discover -s research/contrib/chatgpt/FKP-08 -p test_fkp08.py -v
python -B research/contrib/chatgpt/FKP-08/run_dev.py
python -B scripts/build_code_atlas.py --check-if-present
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

Use Python 3.12 standard library, no external APIs or billed inference. The original public DEV run must execute **once** after prereg, source, algorithm, and tests are frozen. Later runs are engineering reproduction, *not* fresh independent science. Report pass/fail for original source identifiability, candidate vs strong conventional accuracy, 96 revision instances, 12,288 held predictions/arm, 8,192 initial and 1,536 revision original actions, past-world retention, exact cold checkpoint, compressed byte sizes, CPU/wall and full-scope matched cost qualification.

## Stop conditions / integration

Original prereg requires candidate greater than strongest fully trained same-information Bayesian/parametric control by >=5pp with positive context-cluster bootstrap lower CI, **or** <=0.005 accuracy loss and >=2x whole-process saving (not compression size alone), with zero old-version collateral forgetting and no invalid source access. Any tie to equal-information conventional delta encoding without measured end-to-end gain is **DEV_NO_GO / NO_NATIVE_INTEGRATION**. If results are negative, preserve the original outcomes without retuning the exposed DEV split. Main, owner loops, CKB-plane, protected scientific first-use, private research cohorts, sibling models and live production remain unchanged.
