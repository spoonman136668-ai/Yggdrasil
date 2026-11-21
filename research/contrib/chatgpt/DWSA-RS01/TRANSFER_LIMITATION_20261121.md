# DWSA-RS01 — unfamiliar-context transfer limitation (source-level negative)

Date: 2026-11-21. **Read-only source analysis only.** No new data, source-first-use, learner mutation, training, CI, local or remote runner dispatch, or scientific gain.

## Exact source and scope

- Contributor branch before this note: `experiment/dwsa-br01-bounded-correction-dev-20261121` at `7c3061eecff1619cd27970e3dcf03be027191190`.
- `identity_gate.mjs` blob `c73225ad322206dc6b308823d9f3a7a95a476d10`, read from that exact commit.
- Accepted `main` `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; coordinator [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), untouched.
- Owner source-first-use gate [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426): **NO-GO**.

## Verified mechanism-level limit

1. `gateDonor` derives `donorKeys` exclusively from the **union of VALID_OLD and VALID_NOVEL context keys**. It has no independent source-family transfer mapping.
2. `predict` applies the donor difference only when `donorKeys.includes(row.key)`; if not, donor contribution is identically zero, regardless of `gamma` or how informative donor probabilities are.
3. A previously unseen context key also has no fitted correction cell, so its correction shift is zero. Thus for **any held row whose key is absent from FIT and both validation partitions**, output is exactly `raw`, apart from clipping of already-valid probabilities. Example: `key=HELD_UNSEEN, raw=0.60, donor=0.95, gamma=1` gives **0.60**.
4. This is an intentional safety fallback (also checked by the existing focused test), not necessarily an implementation defect. But it makes **zero-shot improvement on a genuinely unseen context key impossible with this utility**. Validation admission on known keys cannot establish unfamiliar-context transfer. Reusing known keys under a different seed also does not establish transfer to a new causal structure.
5. Existing retrospective [RS01 alignment result](native_alignment_result.json) separately rejected both historical donor modes, with `gamma=0`, no active capsules, and `predictions_frozen=false`. Those consumed prequential forecasts cannot be reclassified as a frozen prospective scientific comparison.

Six exact source-pattern checks and the pure arithmetic counterexample were inspected separately through the connected GitHub read interface. **Source-level finding: PASS; new scientific outcome: NONE.** No Node CLI, native Yggdrasil, root regression, Linux/Windows qualification, or cold functional retention was executed for this finding.

## Smallest meaningful future test (PROPOSED, not admitted)

Before original-world first-use, an independent source owner would need to freeze a transferable **pre-action observable representation** and donor-admission rule whose eligibility does not come from held/validation labels or held-context identities. Retain raw prediction as a reversible skip path; cap and isolate corrections; record old-world per-context Brier and cold retention. Include held **keys and causal-structure families absent from FIT/VALID**, plus a donor-permuted negative. Compare against fully trained equal-data raw-only, raw+bounded correction, donor-only, raw+donor and strong conventional causal controls under equal actions/information/compute. Require ≥0.005 absolute unfamiliar-family Brier improvement over the strongest trained control, old-world drift ≤+0.02, repeated independent qualification, and owner authorization under issue #426.

If a gate cannot make nonzero predictions on held unseen keys without breaching custody or retention, **stop this RS01 pathway rather than promoting it**. Do not retune or reuse the already-consumed DWSA-64, BR01 or RS01 retrospective cohorts.

**Disposition:** ENGINEERING source audit PASS; SCIENCE no fresh result / zero-shot unseen-key transfer structurally unsupported; DEPLOYMENT NONE.
