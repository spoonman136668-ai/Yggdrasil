# ENERGY-01 — Classical-energy reasoning for native-style causal chains

**Outcome: DEVELOPMENT NO-GO.** Isolated source-free Linux exploratory benchmark only. No native Yggdrasil acceptance, training, controller, scheduler, PR merge, scientific first-use, or deployment.

## Question and source

Does a compact learned pairwise energy solve unseen binary causal-chain completion problems faster than learned-weight iterative propagation and a fully exact graph solver? Motivated by Hoover, Blayney, Whittington (2026), [*Classical Energies Learn to Reason 1,000× Faster than Looped Models*](https://arxiv.org/abs/2611.17309), with [reference code](https://github.com/Prefrontal-AI/CRAM) under Apache-2.0. **This is an independently written CRAM-inspired toy mechanism, not a port or reproduction of the paper.**

The experiment is relevant to the optional Yggdrasil CKAD work because it isolates one potential *fast relationship-composition* mechanism, while keeping the project’s native, tokenless architecture and accepted state unchanged. It does **not** use or edit CKAD-02–06 source, actual learned CKAD checkpoints, the 21.3-million-record historical resource, or any reserved original causal environment.

## Prospective protocol and custody

- Frozen source-free preregistration at `6b83b2bf7c7fc0489ad7c8f0baa3cfb6e351701b` **before primary outcome**.
- Tested code-only commit `7a2be2aae692009758811de6870fc3456ad4646b`, tree `a7dedaccfa65b851289dcf7a15967401173b73e0`, code SHA-256 `3e4febe1670b295e1f6328634df18945c816a66ef4dd20bd30aea2f6bb9cc3a7`.
- Five seeds: 101, 202, 303, 404, 505. Each seed trains two signed relation weights from 512 synthetic interventions **per relation**, then evaluates 100 wholly new rooted trees of 12 variables and 100 of 20 variables.
- All methods see identical learned couplings and edge labels. The hidden true nonroot states are used only for scoring, not inference. Binary variables are numeric, not text tokens.
- Energy solver: greedy monotone coordinate descent from up to eight seeded random initializations, max 64 sweeps. The iterative baseline is a recurrent **graph-propagation proxy**, not a retrained HRM/TRM. Exact propagation provides a stronger baseline with the same learned relationship weights. Incorrectly flipped edge signs serve as a negative control.
- Preregistered threshold requires energy accuracy at least 99% on **every** seed/size and at least 2× faster whole-process time than **both** baselines with no accuracy loss.

## Results

| Graph size | Energy exact | Looped proxy exact | Exact graph | Shuffled-sign energy |
|---|---:|---:|---:|---:|
| 12-node (500 puzzles) | 360/500 (72.0%) | 500/500 | 500/500 | 0/500 |
| 20-node (500 puzzles) | 141/500 (28.2%) | 500/500 | 500/500 | 0/500 |

Median measured **training + inference** elapsed time per 100 graphs, across five seeds, on this local Linux/Python 3.13.5 sandbox with tracemalloc enabled:

| Graph size | Energy | Looped proxy | Exact graph |
|---|---:|---:|---:|
| 12 nodes | 52.09 ms | 2.75 ms | 3.01 ms |
| 20 nodes | 128.90 ms | 3.74 ms | 4.19 ms |

The energy method is around **19× slower** than the looped proxy at 12 nodes and **34× slower** at 20 nodes on this implementation. All weights were fitted from synthetic data; code uses relation-type priors, so this is not discovery of unknown causal laws. It is not the actual CRAM training recipe, paper benchmark, GPU timing, or model-family comparison. The exact control solves all trees and is the important efficiency ceiling.

The source-free test is a legitimate **negative result for this particular greedy energy and workload**. Local minima increase with graph size. There is no post-result restart/budget tuning, no promotion, and no evidence that general energy-based inference or CRAM itself fails. A different prospective study would be needed for non-tree, noisy, ambiguous or contradictory constraints, and must include a new preregistration and stronger exact/fully trained controls.

## Reproduce and verify

From the repository root at the tested code commit (or the finalized contribution branch with its code blob unchanged):

```shell
python research/contrib/chatgpt/ENERGY-01/pilot.py --smoke
python research/contrib/chatgpt/ENERGY-01/pilot.py --output result.json
```

Output includes all seed, graph size, method, CPU/wall timings, work estimates, per-bit and whole-graph accuracy, and prediction digests. Wall-clock times are environment-dependent. `result.json` in this contribution is the recorded aggregate plus per-seed table; original full local result SHA-256 is in `provenance.json` and is regenerable from the pinned script, but its exact timing bytes are not expected to reproduce on different hardware.

**Qualification:** engineering smoke PASS locally; source-free evaluation executed as preregistered, DEVELOPMENT_NO_GO; Windows dual-OS and full final native regression UNVERIFIED; scientific acceptance, GPU qualification, actual learned CKAD integration, and deployment NONE.
