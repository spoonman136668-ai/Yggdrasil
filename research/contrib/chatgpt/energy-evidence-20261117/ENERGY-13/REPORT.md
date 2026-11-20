# ENERGY-13 — Stateful causal reasoning with persistent hidden history

**Classification:** ISOLATED LOCAL ENGINEERING PASS (post-score independent audit v2); SCIENTIFIC DEVELOPMENT NO-GO; NATIVE YGGDRASIL REGRESSION UNVERIFIED; DEPLOYMENT NONE.

## Verified context and source boundary

The current-turn read-only GitHub check found `spoonman136668-ai/Yggdrasil` main at `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. ENERGY-01 [PR #1201](https://github.com/spoonman136668-ai/Yggdrasil/pull/1201) is open/draft/unmerged at `69123bc92cad8bc14fe6596f42d9b2f4e71a2542`; CKAD [PR #1182](https://github.com/spoonman136668-ai/Yggdrasil/pull/1182) is separately open/draft at `5df8dbf506027b914f66e19441376d1347a3e09d`. No repository modification, new PR, runner execution, CI run, acceptance, model integration, deployment, original scientific source first-use or paid API was performed for ENERGY-13. The Mind-Palace governance and Yggdrasil isolation constraints were treated as advisory context, not as execution authority.

The experiment was run in a local Linux Python 3.13.5/NumPy 2.3.5/PyTorch 2.10.0 CPU sandbox and does **not** reproduce CRAM or benchmark optimized HRM/TRM models. The source-free task is independently generated and contains no original heldout Yggdrasil data. This task supplies a finite XOR-with-lag causal grammar, not unconstrained invention of causal primitives.

## Protocol frozen before scored run

The binary hidden state follows a noisy second-order causal recurrence:

`h[t] = h[t-1] XOR (w0*a0[t] XOR w1*a1[t] XOR w2*a0[t]*h[t-2] XOR w3*a1[t]*h[t-2]) XOR transition_noise`.

The observed sensor `y[t]` is a noisy readout of `h[t]`; both initial hidden bits are unknown at test. Four worlds have unknown 4-bit rule vectors, learnt from **320 fully witnessed sequences of length 16 each**, without exposing true rule coefficients. Sensor and transition reliabilities are estimated from the same observations. Each world also supplies 80 validation sequences to its recurrent control. Training interventions include action codes 00, 01, 10 only; withheld tests introduce 11 and include 16- and 32-step histories, unknown initial state and noisy transitions/sensors. Every arm receives the same recorded intervention/observation information at inference. The GRU is separately trained on the same labelled training corpus, but the rule-based methods possess an explicit compositional grammar that the GRU does not, so architecture-level superiority would not be established even after full convergence.

The learnt-energy arm uses at most 10 initializations, greedy bit-flip updates, 10 sweeps; exact temporal Viterbi optimizes **the same learnt energy** globally using a four-state dynamic program. Controls are GRU (48 hidden, 7,681 parameters), exact inference without lag-dependent coefficients, and energy on independently scrambled sensor evidence. Fixed seeds, data generation, target, cost accounting and thresholds are in `prereg.json`. The `freeze.json` source digests were recorded **after** the smoke and independent smoke audit, **before** scoring. Frozen experiment source and preregistration were not modified after scored results.

## Scored results

Four worlds × 32 new sequences × two lengths = **256 sequences and 6,144 hidden-state bits**. Exactly 2,080 test steps involve double interventions excluded from training; the model must compose the effects of the separate action components.

| Arm | Correct hidden-state bits | Accuracy | Correct terminal states |
|---|---:|---:|---:|
| Learned energy search | 4,933 / 6,144 | 80.29% | 197 / 256 |
| Exact learnt-model temporal inference | **5,096 / 6,144** | **82.94%** | **207 / 256** |
| Recurrent GRU | 4,692 / 6,144 | 76.37% | 197 / 256 |
| History-ablated exact inference | 4,681 / 6,144 | 76.19% | 188 / 256 |
| Energy with scrambled sensors | 3,754 / 6,144 | 61.10% | 158 / 256 |

Per-step energy accuracy: **80.32%** on length-16 and **80.27%** on length-32. Exact: **82.71%** and **83.06%**, respectively. All four unknown causal rules were recovered identically from witnessed training transitions, and cold energy/GRU checkpoint readback matched all four recorded first-sequence predictions.

The energy search matched exact minimum energy on only **160/256 (62.5%)** scored sequences. Exact was 163 hidden-state bits more accurate. History ablation loses **6.76 percentage points** relative to exact, supporting genuine dependence on persistent hidden history. Scrambled sensors lose **19.19 percentage points** relative to energy, supporting dependence on observations.

GRU training: all four worlds reached a preregistered stop (validation threshold in one, patience early-stop in three). **Only 1/4 reached the 0.42 validation BCE threshold.** Do not call the GRU fully converged or treat its inferior task performance as architectural evidence against recurrent reasoning.

## End-to-end cost and inference-specific tradeoff

Measured CPU times include each method's in-world training and test inference, summed over the same four worlds. Data generation, audit and report packaging are outside method sums.

| Arm | Training + inference | Inference stage alone |
|---|---:|---:|
| Learned energy | **1.057 s** | 0.882 s |
| Exact temporal | **0.210 s** | 0.034 s |
| GRU | **4.337 s** | 0.014 s |
| Lag-ablated exact | 0.080 s | 0.030 s |

Energy's whole-process cost is **5.04× higher than exact temporal inference**, not ≥2× faster. It takes less total time than the GRU only because the recurrent training is substantially more expensive in this implementation; at inference alone the GRU is much faster. These are CPU/Python implementation numbers, not normalized hardware/FLOP results.

## Independent audit: preserve failed first audit and corrected audit

Original independent `audit.py` was frozen before scoring and passed **145** independent smoke assertions, including brute-force exact optimization. After scoring, that first audit **failed** (`audit-run.log`) because it incorrectly demanded that an energy candidate's reported objective equal the **minimum over all possible hidden initial states** for its chosen later sequence. The frozen greedy solver is allowed to return a suboptimal initial state. An independent diagnostic verified that **one scored case** had such a non-minimal initial state; it was retained as an optimizer shortfall.

Without altering the scored solver, its protocol or the scored results, a **separate post-score audit revision**, `audit_v2.py`, changed the check to require that the reported objective equal the cost for **at least one** possible initial state; it retains the exact-global lower-bound and independent dynamic-program checks. This revision is expressly not a preregistered audit pass. The revised independent audit **PASS: 7,485 assertions** across all 256 sequences / 6,144 state bits; it independently regenerated all test sequences, fitted all four rules, checked every reported accuracy and cost, verified exact global optima and cold recurrent model predictions. Its evidence counts one non-minimal-initialization episode. The post-score audit change and original failure are preserved in this package. No retries or revisions of the scored model were made.

## Qualification and decision

- **Engineering:** Source frozen before primary score; smoke+brute force PASS; primary scored run complete; audit v1 failed on an overstrong premise; audit v2 PASS with amendment disclosed. CPU implementation is locally reproducible, but no full native dual-OS final regression or code atlas qualification.
- **Science:** **DEVELOPMENT NO-GO.** Exact same-model temporal inference wins both accuracy and time. Frozen ≥80% each-world/length, accuracy noninferiority to exact, and ≥2× exact cost improvement cannot all pass. The GRU is trained but not proven fully converged. The test confirms stateful causality matters, not that energy reasoning is the most efficient mechanism.
- **Deployment:** NONE. No accepted-model updates or research loop changes.

**Recommended next direction:** Stop extending this local XOR/parity test family. If classical energies remain a priority, independently reproduce the actual CRAM training/inference architecture on its stated benchmarks, compare fairly qualified looped models and exact controls at matched accuracy and measured whole-process compute, then only consider native Yggdrasil relevance. Any future original-world science requires separate authorized source custody and preregistration.

## Reproduce

Unzip the archive into a clean writable directory, retaining the directory structure:

```bash
python ENERGY-13/experiment.py --smoke --output smoke-reproduction.json
python ENERGY-13/audit_v2.py --input scored.json
```

For a new scored regeneration, run the experiment in a *separate copy* so the original frozen receipts are not overwritten. Recomputed numerical outcomes should be checked against the existing aggregates; wall timing and PyTorch checkpoint bytes may differ by environment. `freeze.json` binds the original scored experiment, preregistration and the original (v1) audit, while `audit_v2.py` is an explicitly post-score audit amendment.