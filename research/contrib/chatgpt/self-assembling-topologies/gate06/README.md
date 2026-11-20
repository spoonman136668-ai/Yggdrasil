# Gate 06 — Shared causal subgraph transfer (exploratory, isolated)

Status: **development signal only; no native scientific qualification or model promotion**.
Evidence recorded 2026-11-19 and preserved here without editing the experimental bytes.

## Source of truth

- [Exact original Gate 06 evidence archive](./gate06_shared_subgraph_evidence.zip)
- Archive length: **14,064 bytes**
- Archive SHA-256: `216d59ad97a3e189ae5d2ebf93331551cbb9274e21dd83908d93378029ca311b`
- Archive Git blob SHA-1: `df33c49244e995fce74ffcd175cf2eade950c6a6`
- Experiment source SHA-256: `1dbe7452b564f3fb0c9b869204a12852765bf95e6b52e9acfd14131e9d3df7d8`
- Frozen protocol SHA-256: `27cefcf209863661f89d36d4392ca51333130d796263de773170663bd2cadd89`
- Original result SHA-256: `4bfda6272feb160c7e51bfdfa94c33e24c48c7a5453547610d09a19350b338c8`

The archive contains `protocol.json`, `experiment.py`, `result.json`, `independent_audit.py`, `audit.json`, and `README.md`.

## Findings

A bounded 64-byte causal pair representation had first-eight-observation Brier **0.12799442** over 64 development seeds, versus a 64-byte flat-memory control **0.24394396**. It tied an equivalently sized fixed factorized control **exactly**, and a memory-unmatched Bayesian control scored **0.12799442**. Accordingly, this is evidence of useful **factorization**, not superiority from dynamic self-assembly.

Random-table out-of-grammar Brier was **0.25733590**, worse than a constant 0.5 forecast (Brier 0.25). No claim of unfamiliar operator discovery, intelligence gain, native Yggdrasil training, or process-level memory improvement follows.

The locally re-executed independent audit reported `AUDIT_PASS_WITH_SCIENTIFIC_NONPROMOTION`; it recomputed all 64 development seeds and 32 negative seeds, checked 23,040 Boolean truths and 20 independent posterior steps. Local process memory was **not measured**. Repository-wide regression, CI, and independent native scientific first-use are **UNVERIFIED**.

## Reproduce (unpack this ZIP into an isolated directory)

```sh
python -B independent_audit.py
python -B experiment.py
```

The audit is tied to the original result SHA; run the audit **before** rerunning the experiment since wall-clock fields can vary. Confirm the archive SHA-256 before extraction.

## Integration / authority

Research contributor evidence only. **Do not merge or promote this evidence directly into accepted Yggdrasil main or the Amalgam learner.** The central **Unified Causal Intelligence Amalgam Work chat** owns any qualified integration and continuation decision. The existing native model, checkpoint lineage, first-use cohorts, owners, controllers and runners remain untouched.

Related native existing work: NCI-04 ST1 PR #1063 (authentic DEV NO_GO), YNCA-09 PR #1232 (inferential edge-atlas, Bayesian comparator wins), and Amalgam PR #1278 (shared evidence and retention path). This is a separate synthetic mechanism study, not a replication of their qualified result.

Next falsifiable hypothesis: blind intermediate channels and require source-controlled interventions to discover unknown causal parents and operator structure under matched byte/compute bounds and cold retention, with a fully fitted Bayesian and fixed factorized control.
