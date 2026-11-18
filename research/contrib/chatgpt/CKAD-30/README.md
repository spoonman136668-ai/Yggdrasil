# CKAD30 — Sparse native causal composition, source-only pilot

**Stage:** FROZEN SOURCE PREPARATION; no primary cohort B scored. External research only, isolated from accepted Yggdrasil \`main\`, FORGE, owner/runner scheduling and protected first-use.

## What this measures

CKAD29 retained old native observations but abstained on many unfamiliar primitive interventions, so its public causal compositions were close to a coin flip. CKAD30 asks whether the **existing** \`NativeCumulativeLearner.repair_sparse\` fallback can improve that capability on a disjoint and harder family containing *two* simultaneous quadratic interactions, without replacing the native learner or changing its memory model.

The three-primitive composite graphs are disclosed: XOR, majority and a gated XOR. Hidden source law IDs/masks are used only by the evaluator; the model and matched control arms see the exact same public action/consequence witnesses. A complete 2,880-law Bayesian posterior is the strongest prespecified comparison; scientific superiority is not presumed.

## Frozen sequence

1. Original preregistration: \`d320fb29b5cd186a71f09a5bc01de2e2ce5ffa38\`. Exact parent: \`b2960465f419bc26026488777c7d7b0fa7ca8f92\`.
2. Commit code/test/workflow/auditor, then independently lock the precise committed campaign Git blob **before** any pilot.
3. Qualify syntax, source lock, and non-scoring tests on Linux and Windows.
4. Run exactly **two independent screening seeds**, 9101 and 9102, at one budget each. Seal originals and source receipts in this Git branch; no B first-use.
5. Stop with \`SCREEN_NO_GO\` unless at least one screening seed improves composite Brier by ≥0.03 and primitive coverage by ≥0.20 relative to unchanged native, with both preserving cold state, old memory and quarantine.
6. A later separately controlled, frozen-primary run is eligible **only** after a successful source-hash-bound pilot certificate. Primary seeds 707, 808, 909 remain untouched otherwise.
7. Final candidate must pass full Linux and Windows regression, plus independent audit, before engineering can be marked PASS. No scientific promotion.

## Source custody

Synthetic results are provenance-pinned, not authenticated real-world interventions. There are 16 revealed source actions per each of nine native primitive slots and 16 disjoint held inputs per world. The screening data are independent from primary B. Every completed pilot and all negative outcomes are preserved on GitHub.

Run preflight (no scoring) from the repository root after source lock:

\`\`\`bash
python -B -m unittest discover -s research/contrib/chatgpt/CKAD-30 -p 'test_ckad30.py' -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-30/campaign.py --mode preflight
\`\`\`

Pilot execution is on the pinned GitHub Actions workflow and uses \`--mode pilot --seed 9101\` and \`--mode pilot --seed 9102\` once each. No workstation use, paid APIs, production source, live deployment, accepted-ref mutation or competing autonomous training loop is part of this external experiment.
