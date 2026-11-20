# ENERGY-09 — Native HiGHS MIP warm starts versus cold exact search

**Outcome: DEVELOPMENT NO-GO for faster certified reasoning.** Completed source-free local synthetic experiment 2026-11-17. Scored results were independently audited. No native Yggdrasil qualification, original scientific first-use, FORGE integration, model promotion, runner change, branch change, scheduled task, or deployment.

## Read-only source checkpoint

- Repository `spoonman136668-ai/Yggdrasil`; main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` at the read-only checkpoint.
- ENERGY-01 PR #1201 remained open, draft/unmerged at `69123bc92cad8bc14fe6596f42d9b2f4e71a2542`; the independent CKAD PR #1182 was also open and draft, but its head advanced independently. None was modified.
- This experiment is the isolated ENERGY-09 continuation of ENERGY-08's documented negative, using the same unchanged ENERGY-07 generator (`source07.py` SHA-256 `c67ab62bff3ee640a53140a176c850b681a7081cf2b476f1c6b96e1d3f1b5046`) and unchanged five-start, 20-sweep energy search. It reuses no scored seed, original native source, or held-out data.

## Prospective protocol, source freeze, and exact implementation

- Frozen protocol `prereg.json`, frozen source identity `freeze.json`, and independent smoke `smoke.json` were written before any scored-run query. `freeze.json` contains content hashes of all scoring, solver, comparator, audit, and protocol files. Post-run source hashes matched the frozen hashes exactly.
- Nine worlds: seeds **1609, 1907, 2203**, sizes **16, 24, 32** variables. Four independent `energy09_test` queries per world: **36 total**. Training uses 320 full labeled interventions per world and 48 validation interventions to learn factors' noise rates and sensors' reliability. Test truth is held from inference.
- Same fitted numerical relationship factors and known factor scopes for all arms. Task: noisy 3/4-way parity observations, masked unary sensors, one truthful hard state clamp, MAP full-state assignment. Factors are *not* discovered in this experiment.
- Industrial exact backend is **HiGHS 1.10.0 C API** via the installed CasADi-distributed native `libhighs.so`, with `Highs_passMip`, no artificial objective cutoff, a single thread, standard presolve, zero target MIP relative gap, and 0.20s nominal per-case solver time. Cold uses no start. Warm gets a **complete feasible assignment** including XOR residual and integer slack variables through `Highs_setSolution`, then a residual solver time budget after candidate-generation cost.
- A separate smoke with solver logging enabled confirms: `MIP start solution is feasible`; the native library performed an actual MIP start (not merely receiving a Python parameter). The native start returned status 0 in every scored case. `native-start-diagnostic.log` is an independent preflight, **not** a scored-result amendment.
- Shared recurrent factor network: 8 synchronous message-passing rounds, learned per-factor and per-sensor gates plus four shared scalars (**3N+4** trainable parameters), initialized from the same fitted noise rates, Adam lr=.025, at most 60 epochs, patience 12, 320 training/48 validation examples. Parameter counts 52/76/100 for 16/24/32 variables. Same data access, different actual training compute; comparison does not establish equal compute.
- Full negative-control rerun: flip all factor syndrome observations with `index % 3 == 0`, rerun identical energy-search budget on the corrupted input, score corrupted predictions **against the unmodified true objective**.
- The preregistered pass rule: no reduction in certified optima in **any** size, no worse feasible solution against cold on any case, **at least 2x lower full fit+energy+exact elapsed time**, nine/nine recurrent validations converged, and the complete negative-control condition passed. No promotion even if it had passed.

## Exact results

| Graph size | Cold certified | Energy-warm certified | Warm strictly better feasible | Warm strictly worse feasible | Negative changed |
|---:|---:|---:|---:|---:|---:|
| 16 | 8/12 | 10/12 | 4/12 | 0/12 | 12/12 |
| 24 | 2/12 | 1/12 | 10/12 | 1/12 | 12/12 |
| 32 | 0/12 | 0/12 | 12/12 | 0/12 | 12/12 |
| **Total** | **10/36** | **11/36** | **26/36** | **1/36** | **36/36** |

The remaining nine cases have equal best feasible objective. All native cold and warm calls returned some feasible assignment; but exact certification is scarce at larger sizes under fixed budgets. The one worse warm case is an objective failure, not a proof that the start corrupted the exact solver. Different solver budgets and time limits mean the warm-start method is **not guaranteed** to match the best cold incumbent unless explicitly retaining it, which the protocol forbids (cold result cannot be leaked to warm).

The warm method has more total optimality certificates (11 versus 10) but *fewer at 24 variables*, failing the per-size nonregression requirement. At 32 variables, none is independently certified as globally optimal.

### Whole-process local CPU wall time, seconds

| Graph size | Energy only | Cold native HiGHS | Energy-warm native HiGHS | Fitted recurrent |
|---:|---:|---:|---:|---:|
| 16 | 0.128 | 1.451 | 1.247 | 2.689 |
| 24 | 0.167 | 2.502 | 2.479 | 4.122 |
| 32 | 0.218 | 2.711 | 2.668 | 3.821 |
| **Total** | **0.513** | **6.663** | **6.394** | **10.632** |

These include the factor noise-fit time for all arms, candidate generation for energy-warm, and separately counted recurrent training for recurrent. Warm-vs-cold ratio **1.042x**, a **4.0%** total time saving rather than the required 2x. Timing includes Python/C-interface overhead and is not an equal-compute or GPU benchmark. Single CPU machine; no cross-platform reproducibility claim.

The recurrent control achieved initial-to-best validation loss reductions in all worlds and a mean best validation BCE **0.467**. It achieved the explicit plateau-convergence test in **8/9** worlds. The **1907, size-24** world reached the 60-epoch maximum without patience-stopping and remains unqualified by the preregistered criterion. The control is a trained 8-loop recurrent factor model, **not** HRM, TRM, or a general neural model family.

Hidden-ground-truth entire-state exact scores (36 cases): energy **9**, cold native **6**, energy-warm **13**, recurrent **3**. Those scores are not equivalent to objective optimality: the task has incomplete noisy evidence; a certified MAP state can differ from the original latent state.

The negative-control inputs changed **36/36** energy assignments and increased the original objective by a mean of **11.50**, **20.32**, and **25.68** across the three sizes. The prospective negative-control criterion passed.

## Independent audit and remaining limits

`audit.py` does not import the scoring implementation, recurrent model, or HiGHS. It independently validates case coverage, candidate objective values, parity constraints, clamps, native status receipts, both primal/dual objective consistency for certificates, and all reported aggregates. **393,901 audit checks PASS**, including exhaustive enumeration of **12 x 2^15 = 393,216** clamp-feasible states on the 16-node cases. Exhaustive checks on 24/32 nodes are not claimed; larger-graph certificates are native solver optimal statuses with matching primal/dual bounds, not an independent full enumeration.

A status code of successful `Highs_setSolution` by itself would not prove use of the solution. The separate native log records a feasible MIP start with an objective, confirming this is an actual solver warm-start path. It does not establish that the start always improved the search.

**Engineering (local): PASS**—native C API start, independent smoke, frozen scored run, hash custody, audit. **Science: NO-GO**—2x time threshold failed, per-size certificate nonregression failed, one warm feasible solution worse, and 1/9 recurrent controls did not satisfy convergence. **Deployment/native qualification: NONE/UNVERIFIED**—no Yggdrasil owner regression or runner acceptance.

## Decision

This is a credible but narrow result for using energy descent as a *feasible-solution heuristic*, not evidence of faster certified reasoning. Do **not** integrate this solver into native Yggdrasil. Repeating more seeds of the same task without a new falsifiable architectural hypothesis would be a poor use of the research budget. The next useful investigation would use genuine causal hypothesis competition where observed interventions cannot be reduced to the fixed known-scope parity MAP problem, with novel structure discovery, cold retention, and source-qualified controls.

## Reproduce (separate new output names; preserve scored.json)

```bash
python experiment.py --smoke --output independent-smoke.json
python experiment.py --output independent-new-score.json
python audit.py --file scored.json
```

The locally bundled HiGHS native shared library in `highs_native.py` is an environment-specific dependency; install/identify a compatible HiGHS C library before reproducing outside this sandbox. A cold replay cannot promise identical wall-clock times, but the frozen source and stimuli are deterministic. Do not overwrite original receipts.