# MR32-O frozen development verdict — 2026-10-31

**Decision: NO-GO (development efficacy FAIL); engineering qualification PASS.**

- Exact code commit: `25d8965f2f6d2207b67d3a4785f71056e023f8b0`.
- Qualification: https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/41230748061
- Ubuntu: 21/21 focused tests PASS.
- Windows: 21/21 focused tests PASS.
- Cross-platform: event, fitted checkpoint and transfer score parity PASS.
- Frozen development signal: `False` on both hosts.
- Strongest comparator: `uniform_mc`.
- Candidate DECA-Q16 mean terminal success minus uniform Monte Carlo: `-0.04296875` (negative).
- Frozen efficacy criteria: `delta_at_least_0_02=false`, `wins_at_least_24_of_32=false`, `wins_at_least_12_of_16_each_regime=false`, `bootstrap_lower_above_zero=false`.
- Frozen safeguards: `fit_transfer_seed_disjoint=true`, `transfer_feedback_zero=true`, `deca_checkpoint_bytes_within_1_25x_uniform_mc=true`, `deca_cpu_within_1_25x_uniform_mc=true`.
- The 32 independent TRANSFER seed clusters cold-restore the same FIT checkpoint, with no outcome feedback or learned-weight changes.
- Separate workflow `prepare-ckb-research-write-proxy-fanout-r3.yml` failed at the same SHA; it is **not** evidence of failure of this source-only experiment and is not waived by this result.

This is a frozen negative result. **Do not retune DECA-Q16 against the consumed TRANSFER cohort, move thresholds, merge, promote or claim original-source validation.** Preserve MR32-H as failed historical work and S4C1's reproducible implementation as a reference only. FSA-04 issue #83 remains the independent science-authority boundary; no protected first-use or independent source admission is authorized.
