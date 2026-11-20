# ENERGY-52 — Evidence-gated update under unfamiliar causal shifts

**Verdict: SCREEN_NO_GO.** Date: November 19, 2026. 24 prospective synthetic worlds in 2 disjoint seed cohorts; 36-world primary **NOT RUN**. External research only, not native Yggdrasil training.

## Freeze and custody

Existing draft Yggdrasil PR #1210, branch `research/archive/energy-evidence-20261117`. Parent baseline `73664df0440b1d8e8f017d7ba417c7ceb5c77d90`. Original scorer and auditor in `source.tar.bz2` were frozen in GitHub commit `a5d87e5b96ea1e7585a9215c60af1ed5b9959f57`; the **prospective screen seeds and eight pre-registered gates** were separately committed at `48250090a7fe8f35c6b36c19dc1faa472677f85a` BEFORE the two fresh seed cohorts were scored. Original scorer SHA256 `1e80168f86d65e2ccd250e6975ed5df414653f064812007e723109d3178348c9`, audit SHA256 `1ac95760f049a04ddc745491857ced76404dea9bc45a454170214054ffe8fbe7`. Pre-freeze exploratory seeds 99991 and 99997 (12 cases each) were already tested and are archived separately. They are **not preregistered confirmations**.

## Frozen mechanism and information parity

One staged sparse-energy regression learner (Walsh monomials of order 1–5 on 12 observed action bits, 1,585 preauthored candidate features) fits 72 OLD labeled intervention outcomes, then 48 NEW labeled outcomes. A held-out group of 24 NEW training-context outcomes determines whether a fitted correction earns a >5% relative validation-MSE reduction against the old model. If accepted, the correction is refitted on all 72 NEW witnessed outcomes. The OLD checkpoint remains frozen. All controls see 72 OLD plus the same 72 NEW factual intervention labels, including fully trained separate-context ElasticNet, OMP, ungated corrections, a no-adaptation ablation and shuffled new-label negative. Every world contains 360 disjoint underlying 10-bit intervention assignments; 72 held OLD, 72 held NEW, 72 held COLD labels are never used for fitting or gating. COLD nuisance cues independently change from the OLD/NEW correlation regimes. Authored feature grammar is supplied and is not unrestricted new operator invention.

## Prospective screening: 24 worlds

| Policy | Held OLD MSE ↓ | Held NEW MSE ↓ | Held COLD MSE ↓ |
|---|---:|---:|---:|
| **ElasticNet** | 3.1462 | 2.6655 | **2.9556** |
| Ungated correction | 3.5603 | 3.6877 | 3.8515 |
| **Gated correction** | 3.5603 | 4.3040 | **4.4043** |
| Frozen OLD/no adaptation | 3.5603 | 4.8478 | 5.1375 |
| Shuffled corrective labels | 3.5603 | 6.5181 | 6.6688 |

**Per-seed conventional comparison:**

| Prospective seed | Gated cold MSE | ElasticNet cold MSE | Gated error excess |
|---|---:|---:|---:|
| 99973 | 3.7780 | 2.8426 | +32.9% |
| 99979 | 5.0306 | 3.0685 | +63.9% |

The gated learner was **49.0% worse** than fully trained ElasticNet and **14.4% worse** than its own ungated version, pooled. It accepted 13 corrections and rejected 11. Old checkpoint predictions were preserved exactly; the shuffled-label negative and no-adaptation baseline were weaker.

## Exact eight frozen gates

| Gate | Result |
|---|---|
| cold_vs_enet_each | FAIL |
| cold_vs_ungated_pooled | FAIL |
| new_vs_enet_pooled | FAIL |
| old_checkpoint_exact | PASS |
| shuffled_negative_pooled | PASS |
| no_adapt_pooled | PASS |
| audit | PASS |
| meaningful_gate | PASS |

**5/8 criteria numerically met, including the audit after the transparent adapter.** Three quantitative gates failed: per-seed ElasticNet cold, pooled ungated cold, and pooled ElasticNet NEW. The preregistered early-stop condition is met because BOTH prospective seeds are >10% worse than ElasticNet on COLD and the gating mechanism shows no pooled positive gain over ungated correction. This is a defensible negative **screen**, not an invalid primary or a three-seed SCIENTIFIC_PASS.

## Audit and limitations

The **original frozen audit CLI failed** at a non-scientific hardcoded seed whitelist: its accepted top-level lists contain the earlier exploratory seeds and reserved PRIMARY seeds, but not the prospectively frozen screen list [99973,99979]. After scoring, `audit_screen_adapter.py` verified both exact original source hashes, temporarily reset only the in-memory accepted-seed list to [99973,99979], and then called the **unchanged frozen audit checks**. All 45,480 refit/assignment/loss check items passed across 24 worlds; 24-world deterministic semantic replay also passed SHA256 `5e159bd33610030f06bb3f98484e8aff73a9648385de009cc5fc86b067153a45` excluding timing fields. This is a **disclosed audit qualification exception**, not an unchanged-source standalone audit CLI pass. The audit shares the source generator and estimator implementations with scorer (only the aggregation/loss checks are independently rerun), so fully independent science and native platform regression remain **UNVERIFIED**. The archived `prospective_screen.json` and `prospective_audit.json` preserve exact case-level receipts. No primary result was manufactured.

## Decisions and authority

Preserve negative outcomes and do **not** retune using 99973/99979 or earlier exploratory seeds. Reserved PRIMARY seeds 9419/9431/9449 are **UNCONSUMED**. No accepted Yggdrasil checkpoint, native model, Forge loop, scheduler, runner, queue, `main` or deployment was changed. The next experimental hypothesis would need an independently justified alternative to validation-only gating (e.g. mechanism-specific action interventions), fresh seeds, and separate preregistration. This screen does not qualify it.
