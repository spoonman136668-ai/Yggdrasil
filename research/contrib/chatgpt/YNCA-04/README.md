# YNCA-04 — information-cost-aware causal probing (design only)

Status: **PROPOSED — not implemented, not executed, no scientific outcome**.

## Motivation

YNCA-01 lost to global reweighting, YNCA-02 lost to confidence-only calibration, and YNCA-03 improved over random probing but lost to fixed and exact Bayesian intervention controls. Do not replicate these consumed runs or change their results. The new hypothesis is that learning the *net value* of acquiring evidence, including downstream decision loss and the actual cost of interventions, might be beneficial when mechanisms are unfamiliar or costly to probe.

## Planned experiment

- One tokenless/native action-value learner, no LLM or model architecture replacement.
- Environment exposes observations, available interventions and their prices. Hidden causal mechanisms are only revealed to evaluation, never to the policy.
- Shared observation and action budgets across trained policy, fixed-probe, random, exact Bayesian decision-value, exact Bayesian information-gain, confidence/no-probe, shuffled-reward and oracle-diagnostic arms.
- Primary outcome: terminal decision regret plus observed intervention cost. Support requires >=5% improvement against the strongest nonprivileged matched baseline and paired interval excluding zero.
- New causal mechanism families will be disjoint from training, not merely existing AND/OR laws with altered parameters.
- Preserve results including null/negative outcomes. No retuning consumed heldout data.

## Custody stop

`prereg.json` is a **successor design record**, not yet a source-locked primary preregistration. The specific generator, exact hypothesis classes, frozen first-use identity hashes and budgets must be committed before the primary test. The input hash placeholder is intentional and forbids claiming first-use provenance from this document alone.

The existing YNCA-03 candidate already has successful full dual-platform regression at [run 44273675964](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44273675964) on `2638a53dbd121966080894c125bfc92d43db0d3a`. YNCA-04 does not modify that candidate, the CKAD integrated model, or accepted `main`.

External contributor research only. No runner/controller/scheduler modification, protected scientific first-use, promotion or deployment.
