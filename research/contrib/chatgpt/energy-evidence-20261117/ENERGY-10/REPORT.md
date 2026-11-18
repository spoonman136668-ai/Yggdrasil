# ENERGY-10 — Competing causal hypotheses, double interventions and cold retention

**Outcome: DEVELOPMENT NO-GO** (2026-11-17). A fully executed, source-free, synthetic local research experiment. All primary source and protocol hashes were frozen before the scored run and unchanged after. **No native Yggdrasil qualification, scientific first-use, source/PR mutation, model integration, runner activity or deployment.**

## Why this was the next gate

ENERGY-09's frozen known-scope parity optimization provided at most modest certified-search benefits and had one nonconverged recurrent control. ENERGY-10 therefore tests a different, causally motivated question: can learned classical violation energies identify competing causal parent/operator hypotheses from interventions and then reason about *previously unseen pairs* of interventions faster and at matched accuracy than independent exact inference and a trained four-step neural recurrent control?

The synthetic causal grammar is intentionally restricted; results must **not** be described as unrestricted causal-law discovery, autonomous reasoning, or native Yggdrasil learning.

## Source custody

- `spoonman136668-ai/Yggdrasil` `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` read-only verified; ENERGY-01 draft PR #1201 at `69123bc92cad8bc14fe6596f42d9b2f4e71a2542` still open. CKAD draft PR #1182 was active independently and was not edited.
- Disjoint authored local seeds: 731, 919, 1103, 1297, 1429, 1693. Smoke used seed 99991; none draws from original or reserved Yggdrasil science data.
- Protocol frozen as `prereg.json` SHA-256 `c1617106b1344147ed5054a7108fc36c5da948d51402891dbb643803c3265533`.
- Executable `experiment.py` SHA-256 `0af58ab2ea55145732de297d21b80c2fdd188ce5a0d47aceb0c31f4ab5e182f6`; independent `audit.py` SHA-256 `8f27f30d2cbb271171cb7a9c330e1c052821dcb1b816583a23d28609b3ce39f6`.
- `freeze.json` records these before smoke/scored evaluation. Exact hashes were verified again after all runs. Original scored result `scored.json` SHA-256 `78b89a4c7a266ad665bae5e740d7dfdfbb1374c8e50a467efce1832045c027f5`.

## Mechanism and training

Each world has four binary exogenous variables and three ordered endogenous variables (H0, H1, Y). The causal parents and local mechanism for each endogenous node are initially unknown. Each rule has two parents and one operation from `AND, OR, XOR, XNOR, AND-NOT`; the generator constrains H0 → H1 → Y ancestry. These structural priors and the operator vocabulary **are given** to the learners. They must identify exact parent choices and operations from 320 labeled training intervention examples per world; 80 disjoint validation examples per world support recurrent fitting. At most one variable is clamped in any training/validation intervention. Sensor readings may be flipped independently. An intervened target is excluded when fitting that target's endogenous causal equation.

The learned energy method selects local hypotheses by minimizing empirical violation costs and then uses two-start, ten-sweep monotone coordinate descent to infer latent X3 and endogenous states under noisy H0/H1 evidence. An independently implemented exact method exhaustively enumerates all 16 latent assignments using the **same learned rules and objective**. A separate independent symbolic learner fits candidate rules and then performs exact inference. A genuinely trained 4-step, 3,913-parameter GRU control uses the same training/validation observations, input masks and intervention flags, with a 200-epoch cap and 20-epoch validation patience. The true-rule oracle is evaluation-only, never a candidate model.

Test sets contain 48 familiar single interventions and 96 never-trained double intervention combinations per world, **864 total test queries**. The test target Y is hidden, X3 is masked unless explicitly intervened upon, and H0/H1 sensor observations may be noisy. The task is predicting Y under evidence and `do`-interventions. A negative control changes learned operations; a serializable rule checkpoint is cold-restored before inference.

## Results

| Cohort | Queries | Learned energy correct | Independent exact correct | Independent symbolic correct | 4-loop trained GRU correct | Oracle correct | Energy matched exact optimum |
|---|---:|---:|---:|---:|---:|---:|---:|
| Familiar single intervention | 288 | 268 | 277 | 277 | 271 | 277 | 274 |
| Unseen double intervention | 576 | 533 | 544 | 544 | 510 | 544 | 565 |
| **Total** | **864** | **801 (92.7%)** | **821 (95.0%)** | **821 (95.0%)** | **781 (90.4%)** | **821 (95.0%)** | **839 (97.1%)** |

- The energy learner recovered **18/18 true local parent/operator mechanisms** in the six authored worlds. This is bounded learning from randomized interventions, not a discovery of previously unknown mathematical operators.
- Its optimizer reached the independent minimum of its own learned energy **839/864** times, failing **25** times; the exact method answered **20 more true targets**. Its residual accuracy deficit is predominantly an inference-optimization limitation after successful mechanism fitting.
- Exact model inference and the true-rule oracle gave identical predictions on all test queries. The oracle itself is correct **821/864**, showing information loss or ties under missing/noisy evidence in this task, not an unlearned structure error.
- The recurrent network improved validation loss in **6/6** worlds but satisfied the *predeclared* validation-patience convergence criterion in only **5/6**. World 1297 reached the 200-epoch cap. This is a real trained recurrent control, but its full comparator-convergence gate **failed**, so no claim about the looped model class is supported.
- Negative operation corruption changed only **354/864** target predictions. The demanding frozen 100%-degradation negative-control criterion was therefore **not met**; it is retained as a failure, not tuned after scoring.
- All **864/864** source-serialized rule checkpoints reproduced the original energy prediction exactly after cold restoration.

### Measured CPU cost

| Instrumented stage totals over all six worlds and 864 queries | Elapsed seconds |
|---|---:|
| Learned energy fit + energy-search inference | 0.0628 |
| Same learned energy fit + independent exhaustive exact inference | 0.0646 |
| Independent symbolic fit + exact inference | 0.1258 |
| Four-step GRU fit + recurrent inference | 2.8079 |

The energy implementation is ~1.03× faster than independently exact inference using the same fitted energy model, **far short of 2×**. It is ~44.7× faster in these *instrumented fit/inference calls* than the trained Python/PyTorch recurrent network, but that network has different capacity, operating characteristics, and one nonconverged world. Comparisons to the Python symbolic implementation are additionally affected by vectorization versus scalar loops. The timing counters **exclude** data generation, framework initialization, archive/audit overhead and other setup: do not interpret them as truly complete end-to-end process times or matched FLOPs. The entire scored process occupied ~10.34 seconds on this local host, which includes additional overhead. No GPU, real action-consequence benchmark or cross-platform qualification was run.

## Engineering and independent audit

**LOCAL ENGINEERING PASS**: frozen sources, detached smoke, deterministic scored six-world run, cold replay parity, and a standalone `audit.py` that does not import the experiment's optimizer or inference code. The audit performed **14,447 passing assertions** on all 864 cases: independent objective evaluation and 16-assignment exhaustive minima; per-case assignments, clamps, masks and predictions; checkpoint hashes; mechanisms; and summary reconciliation.

**Post-score, nonprimary diagnostic:** The original stored evidence contains a binary value in the masked X3 `sensed` field even when its `observed` mask is false. A separate *read-only diagnostic* changed that masked field in **825** cases and verified that learned energy inference, exact/symbolic inference, oracle and recurrent feature encoding remained identical (**4,125 checks PASS**). The other 39 cases explicitly intervened on X3 and therefore treated that value as observed; they were not perturbed. No original score or frozen source was changed. Nevertheless a future independent first-use test should physically omit masked values as a stronger data-custody defense.

**SCIENCE NO-GO**: the exact-objective-recovery and rule-fit subcriteria passed, but energy was 20 answers below independent exact, total cost advantage over independent exact was only 1.03×, 1/6 recurrent fits failed the frozen convergence definition, and the negative-control criterion failed. No cross-platform/root regression or native model test exists for ENERGY-10.

**DEPLOYMENT NONE**: Yggdrasil's independent runtime, accepted state, PRs, controllers, runners, scheduled tasks, protected science resources and FORGE integration remained untouched.

## Decision

Do **not** integrate this energy learner into native Yggdrasil. The test establishes that restricted causal structures and consequences can be inferred from intervention data and applied to unseen combinations, but independent exact inference recovers more correct targets with effectively the same computation at this size. Repeating local-restart tuning on the already scored cohort would be invalid. The next worthwhile *new* scientific hypothesis is not another exact-solver warm start: test learned uncertainty over competing causal laws under genuinely incomplete intervention evidence, and compare against a well-fitted Bayesian/active-experiment control on independently admitted novel mechanism families. Freeze that experiment separately; do not claim unbounded causal discovery or scientific acceptance before it passes.

## Reproduce

With Python 3.13, NumPy and PyTorch available:

```shell
python experiment.py --smoke --out new-smoke.json
python experiment.py --out new-score.json
python audit.py --file scored.json --out new-audit.json
python diagnostic.py
```

The original `scored.json` must not be overwritten. CPU timing depends on machine/software versions; stable source, dataset identities and primary numerical aggregates are the custody evidence. Post-score `diagnostic.py` is explicitly separate from frozen primary sources.