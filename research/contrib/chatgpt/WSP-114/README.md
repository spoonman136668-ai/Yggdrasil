# WSP-114 — High-first nonlinear causal weight-programming frontier

**Status:** isolated experimental development; **NO original heldout WSP-114 primary use before exact-source qualification**. Stacked on WSP-113 draft [PR #1082](https://github.com/spoonman136668-ai/Yggdrasil/pull/1082), exact parent `e814137946e20452d7db4595f9c1fa7214a6e228` and tree `a59e7c9b81af9c0d53f5e1fc3fcce9f22aa2e770`. **Frozen prereg FIRST** in commit `2c0dcf3270d19ec23b4f0197b5a02a06a14a7f54`, before the generator, learning mechanism, independent controls or fixtures.

## High-first design: begin 128x above the earlier 8-probe ceiling

Start with **64 interdependent state nodes**, up to **12 potential predecessors per node**, and a hidden causal function that combines direct and pairwise (quadratic) previous-state influences. This has up to **78 candidate causal features per downstream node** and thousands of directly written numerical synapses. An action forces one 64-node state bit to 0/1, causing consequences to propagate across later nodes.

The first original test receives up to **1,024 actual action consequences per transfer world**, across **16 novel 64-node quadratic worlds**, and predicts **512 never-shown state/action effects per world** (8,192 heldout complete 64-bit-state predictions for each method and budget checkpoint). Thirty-two disjoint public training worlds contain linear-only laws; transfer introduces previously unseen quadratic causal interactions while preserving the fixed generic Boolean feature grammar.

The frozen **high-to-low budget ladder** is: `1,024 → 512 → 256 → 128 → 64 → 32 → 16 → 8`. Although the evaluator collects 1,024 effects first, it retains the exact pre-oracle prediction and parameter snapshots from each smaller prefix. Those prefixes quantify the actual observation threshold; they are not independent original first-uses.

**Only if the 64-node/1,024-probe result misses 95% whole-state exact accuracy** does the same sealed code proceed to **48 nodes, then 32 nodes**, each with independent hidden laws and the same 1,024 ceiling. No postresult rule tuning or arbitrary extra interventions.

## What is actually programmed

The native model incrementally learns a local GF(2) equation for each node from *observed action consequences*, writes every inferred direct and pairwise coefficient into explicit IEEE float32 synapse slots, and uses its compiled numerical synapse state for future causal propagation. A 64-bit original sensory state and 7-bit intervention identify each experiment; no hidden labels, mechanism masks or oracle coefficients are imported into the model.

The implemented computer program still supplies the generic Boolean algebra, node order and recurrent causal execution semantics. These are task-specific synthetic mechanics—not newly invented general-purpose cognition, or a claim that dense Yggdrasil model weights have been updated.

## Hard comparison and scientific stop

The independently authored full GF(2) symbolic learner receives the same data ceiling and novel worlds. A conventional full-convergence ridge fitter receives identical linear/pairwise features (but its real-valued regression is not expected to match exact GF(2) parity). Random and passive probing, zero-memory, pair-feature ablation, exact same-feedback independent symbolic, cold restoration and checkpoint-tamper rejection are measured.

The test quantifies whole **64-bit-state exact**, per-bit accuracy, candidate feature identifiability/rank, intervention budget frontier, originally heldout new-law transfer, native knowledge retention and process resource use. The strongest independent control is **never** the deliberately mismatched ridge model if the exact symbolic solver performs better.

**Scientific superiority needs independently replicated outperformance of the strongest exact symbolic control or demonstrably equivalent accuracy at substantially lower matched end-to-end compute/memory.** Mechanism engineering and sample-capacity success alone are not SCIENTIFIC_PASS.

## Source custody and authority

- Fixture tests fabricate world coefficients from a separate namespace. They do **not** import or call the original hidden quadratic oracle.
- Mandatory full inherited WSP80–WSP114 and Yggdrasil root tests must pass on Linux and Windows at a candidate exact source/tree, plus independent two-OS G29 source-atlas acceptance, **before** a one-shot original synthetic test.
- The first-use evaluator may only read the selected intervention outcomes until **all** world/arm/budget predictions and evidence are SHA256 sealed; only then may it open heldout outcomes.
- No merge, accepted Yggdrasil state, FORGE loop, Wingless/Hybrid changes, controller, new schedule, private runner, paid API, protected historical WSP101–WSP113 first-use source reuse, or deployment.

Fabricated fixture command:

    python -m unittest discover -s research/contrib/chatgpt/WSP-114 -p 'test_*.py' -v

First-use-only 1,024-intervention high-budget command (forbidden until complete qualification):

    python research/contrib/chatgpt/WSP-114/experiment.py --frozen-1024-first-primary-dev
