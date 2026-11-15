# FKP-18 — Two-step delayed causal credit, public-only falsification

**Disposition:** \`PUBLIC_DIAGNOSTIC_STRONG_CONTROL_TIE_NO_GO\`. Research-only; no Yggdrasil native integration, no original FKP-17 DEV/TRANSFER first use, no claim of general intelligence. This experiment is distinct from active FKP-17 PR #1109.

## Frozen question and chronology

Does a tokenless, direct-written compositional relationship memory learn from **earned consequences delayed by two actions**, generalize beyond exact history lookups, and beat a fully informed conventional symbolic learner given **identical public observations**?

- Frozen protocol FIRST: \`eda3eb3d6ba33a99980e8d0d54ac05bd748306f2\`
- Candidate + test method before result: \`2fa725e9d1b52108151b48de4c6910880551a024\`
- Original result commit: \`8a49b10d1905f1513f4ff007c18a0c3fb257eb61\`
- Permanent frozen metrics: \`result.json\`; exact code, cohort, runtime and source receipts: \`provenance.json\`

The task is an intentionally simple **synthetic public diagnostic**. Its 32 permitted PUBLIC worlds (\`880000..880031\`) contain 8 actions and 8 public registers, 24 common public exploration interventions and 16 genuinely on-policy scored interventions. An earned reward at step \`t\` comes from an actual intervention at \`t-2\`, conditional on the *previously publicly observed* context bit and predecessor action. The generator's private world shift is **never passed to learner calls**. All learners receive precisely the same public exploration tape and are independently reset.

The candidate maintains an eight-hypothesis bounded support mask and resolves consequences back to the proper action. The conventional symbolic comparator has the **same exact compositional hypothesis grammar**, public data and action budget, with a separate implementation. Other controls are exact-history tabulation, incorrect current-step reward assignment, a seeded random policy, and a private-label oracle upper bound. Hence a comparison against the flat table **alone cannot demonstrate algorithmic novelty**.

## Actual public diagnostic results

32 worlds × 6 arms × (24 exploration + 16 scored) = **7,680 genuinely simulated source actions**.

| Arm | Mean actually earned 16-step reward |
| --- | ---: |
| Native-style direct-written compositional memory | 13.6953125 |
| Equal-information conventional exact symbolic | 13.6953125 |
| Conventional exact-history lookup | 2.4453125 |
| Wrong action-credit assignment | -0.8359375 |
| Source-private oracle upper diagnostic | 13.8515625 |
| Seeded random | -1.65625 |

Candidate minus strongest conventional symbolic **0.0**, frozen 1000-resample paired-world bootstrap 95% interval **[0.0, 0.0]**. The predeclared +0.10 / lower-95% >0.02 strong-control criterion **fails**. Every one of 32 matched public worlds ties the symbolic learner exactly. The candidate does learn delayed action consequences and generalize compared with a memorization table, but the same result is attainable through ordinary exact symbolic inference.

## Qualification and limitations

- Local Linux Python 3.13.5 **8/8 focused tests PASS**, syntax compilation PASS. Code and test content matched GitHub Git blob SHAs exactly. Exact source hashes and deterministic output digest are in \`provenance.json\`.
- An existing GitHub push workflow [run #43771189014](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43771189014) failed **without starting a job**. This is **infrastructure/permission**, not a failed test or a passing dual-OS regression.
- G29 source atlas, mandatory complete Ubuntu and Windows regression, independent evaluator custody, retained/repaired capability, disjoint family transfer and separate scientific qualification **UNVERIFIED**.
- Because the method includes the source family's exact compositional grammar, this is **not** proof of spontaneous discovery of unfamiliar physical or cognitive laws, and should not be merged into Yggdrasil's native model.
- Logical support bitmask size (1 byte) is not a measured Python resident-memory or total-compute advantage. The source has no genuinely private held oracle for original FKP-17 science.

## Reproduction (public local diagnostic only)

\`\`\`sh
cd research/contrib/chatgpt/FKP-18
python -m unittest discover -s . -p 'test_*.py' -v
python -m compileall -q .
python public_delayed_study.py
\`\`\`

The stored \`per_world_scores_sha256\` in \`provenance.json\` is the SHA-256 of the canonical JSON array of 32 per-world outcome objects, ordered by seeded world, with sorted object keys and compact separators.

**Next falsifiable direction:** An independently generated disjoint causal-law family with context switches and multiple reachable goals; equal-information generic model selection/causal inference, trained recurrent, and source-private identifiability and cold-retention gates. Do not retune or retroactively reclassify these outcomes as a win.
