# CKAD36 — Discriminating interventions over cold native causal memory

**Research-only. Not an accepted Yggdrasil learning architecture or owner-loop integration.**

The source-locked CKAD35 research [PR #1252](https://github.com/spoonman136668-ai/Yggdrasil/pull/1252) improved held causal-composition Brier from 0.25 to 0.12794/0.13194 in two fresh synthetic worlds, but missed the preregistered 0.08 threshold. Its readout matched conventional Bayesian analogy. Remaining *source-compatible* causal alternatives were 2,4,33 and 1,3,3 for the three in-class targets. CKAD36 tests **which actual interventions should be performed** to discriminate those alternatives on FRESH worlds, not how to fine-tune CKAD35's used labels.

## Frozen, before first use

Preregistration SHA: `029d74fe45f62ca7c0764b137136696761652ad3`. New pilot seeds `13961,13962`; primary `23961,23962,23963` reserved, not automatically eligible. The previous two original pilot seeds `13851/13852` are never replayed.

For each original seed, train the **unchanged** native source-memory checkpoint on three previously unseen synthetic donor causal functions (42 observed actions each). Restore checkpoint from its checksum, add four independently observed 42-action pressure slots and verify all original donor readouts across all 64 actions, cold byte parity, and atomic contradiction rejection. The donor state remains isolated from every target arm. All rules remain synthetic binary action-consequence functions and do not authenticate real-world causality.

Target worlds: three hidden relabeled donor rules, and three quartic-perturbed negative rules. All intervention policies have the **same 10 actual initial interventions** per target, and the same **38 available future inputs**. Sixteen separately reserved held inputs can never be queried or used in learning. Each policy chooses **exactly six** additional distinct real interventions with policy-specific outcomes. All policies score the SAME held outcomes, so the cost and accuracy comparison is not inflated by supplying active with more data.

## Intervention choices

**Active:** maintain all 23,040 source-consistent transforms of cold native donor functions; at each of six steps, choose the input that most evenly divides remaining hypotheses according to their predicted binary consequence. Query the source once, update the hypothesis set from that *observed* result, then repeat. Never enter an inferred outcome into native weights. The committee and scoring are an externally supplied, conventional Bayesian method.

**Fixed:** six outcome-independent public inputs selected before any additional target observations. **Random:** six reproducible uniformly sampled public inputs, likewise outcome-independent. The same 10+6 source budget applies to each. An independent conventional GF(2) donor implementation produces the same 23,040 candidate functions and follows the exact active policy as the strongest required conventional comparator. All action traces must match precisely.

Each policy fits the same **unmodified native target-only cumulative learner**, degree3 conventional GF(2), fully fitted logistic, frequency and sham from its own sixteen target-source observations. The initial-ten posterior is retained as a no-extra-label ablation.

Public source budget **per policy and seed**: 3×42 donor + 6×(10+6) target +4×42 pressure = **390 genuine synthetic source observations**. Cross-policy unique actions can differ; budgets are equal per arm, not identical final observations. Held: 16×3 separate primitives×2 families, scored through three composite graphs = **96 common held composite cases per policy and seed**.

## Frozen go/no-go

**Both pilots** must achieve active in-family held Brier <=0.08, improve by >=0.03 absolute over **both** equal-source fixed and random policies and both matched target-only native/conventional GF(2), match independently fitted conventional active-Bayesian exactly, make >=50% confident primitive predictions with zero confident errors, reject >=2/3 quartic-negative targets, make zero confidently wrong admitted quartic predictions, and achieve no worse OOD Brier than fixed. Source-only inputs, cold/pressure retention and contradiction atomicity must PASS.

Otherwise classify `SCREEN_NO_GO`, keep original negative receipts, and stop. On incomplete source/custody or mismatched conventional controls, classify `INVALID`. Never replay consumed pilot source first-use or retune the original thresholds. An engineering screen cannot be `SCIENTIFIC_PASS` because the candidate is the same conventional intervention-selection algorithm, merely reading native stored donor coefficients.

## Independent evidence custody

`seal_pilot.py` imports neither the synthetic generator nor native learner. It independently reconstructs every bit of the donor GF(2) source model, the full source-consistent transform committee, each source-only action selection and posterior size, held predictions, Brier and confidence counts from original per-policy source and evaluator captures. Its only function is verification of already generated original evidence. GitHub should preserve the two original raw JSON receipts, their SHA256 checksums, frozen scientific screen and pinned atlas source. Final two-platform full regression is mandatory on the exact post-evidence SHA.

This work does not create a new learning subsystem, accepted model change, Forge orchestration, controller, paid API, scheduled task, merged PR or deployment.
