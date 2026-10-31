# MR32-K — held-out synthetic retention transfer receipt

Date: 2026-10-31
PR #716: OPEN / DRAFT / UNMERGED.
Code/test head qualified: `0127df9b4f8a5ffd86bc8841e2d66721c91e0925`.
Dedicated workflow: `41226802007`.
- Ubuntu job `124612551133`: PASS, 49 tests, Python compilation, resource inventory, held-out evaluation script and clean checkout.
- Windows job `124612551464`: PASS, 49 tests, Python compilation, resource inventory, held-out evaluation script and clean checkout.

## Frozen experiment definition

FIT contains eight metadata profiles: all combinations of high/low evidence, low/high prediction error and low/high contradiction. The target label is positive when at least two of the three metadata properties indicate usefulness. The learned linear utility scorer receives 30 rounds of explicit post-use feedback on these FIT profiles.

TRANSFER creates a fresh allocator, copies only the FIT-learned utility weights, and inserts 16 disjoint-key records (two instances of each profile). No TRANSFER memory is marked used and no TRANSFER outcome is supplied. The fixed active budget is seven. Controls select the same cohort's top seven by last-use recency and by evidence count only.

## Exact results

Identical JSON output on Windows and Ubuntu:

| Selection rule | Useful memories in active 7 | Precision@7 |
|---|---:|---:|
| Learned utility scorer | 7 / 7 | **1.000** |
| Evidence-only | 5 / 7 | 0.714 |
| Fixed recency | 4 / 7 | 0.571 |

TRANSFER cohort: 16 records, 8 labeled useful; transfer feedback events: **0**.

The learned scorer therefore exceeds the evidence-only control by 0.286 absolute precision and recency by 0.429 on this constructed cohort.

## Interpretation and limits

This demonstrates that the small scorer can learn and transfer a simple metadata-to-usefulness relationship to new records under the **same synthetic generating rule**. It does NOT demonstrate a learned memory representation, improved authentic task reward, causal decision-making, useful retention under a changing query distribution, cold-restart interference resistance, or transfer to an unfamiliar task family.

The metadata features, linear function class, update rate and synthetic label rule are explicitly hand-designed. Only the scorer weights are learned. It is one deterministic cohort/one generating rule, with no confidence intervals or statistical generalization claim. The test is susceptible to its designed correlation structure and must not be presented as native intelligence improvement.

## Separate integration boundary

At the same code head, G29 Atlas run `41226801978`:
- Windows job `124612537189`: FAIL at canonical `scripts/build_code_atlas.py --check-if-present` due stale indexed file set.
- Linux job `124612537307`: reached the same fail-closed freshness check and was still executing its canonical base64 regeneration step at last inspection.
G29 and full final integration regression are NOT PASS. Do not hand-edit or waive the generated atlas.

## Disposition

`MR32_K_SYNTHETIC_FIT_TRANSFER=PASS`
`TRANSFER_FEEDBACK_EVENTS=0`
`LEARNED_PRECISION_AT_7=1.000`
`EVIDENCE_ONLY_PRECISION_AT_7=0.714`
`RECENCY_PRECISION_AT_7=0.571`
`AUTHENTIC_TASK_EFFICACY=NOT_TESTED`
`UNFAMILIAR_WORLD_TRANSFER=NOT_TESTED`
`G29_ATLAS=BLOCKED_STALE_INDEX`
`FSA04_ORIGINAL_FIRST_USE=BLOCKED`

Evidence is retained in this repository. No original environment, protected evaluation, accepted source, production architecture, merge, or promotion was touched.
