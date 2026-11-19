# ENERGY-67 — Evidence-triggered causal representation growth

External synthetic Yggdrasil contributor research, not native training, scientific acceptance, or an authorized autonomous-loop execution.

**Research question:** Can a sparse representation select how many novel fourth-order causal factors to add from witnessed action–consequence evidence, preserve the OLD response exactly, and outperform conventional *same-feature, same-data* model selection?

Each fully specified synthetic world uses nine binary controllable actions, three OLD unknown pair-parity factors, and 2 or 4 NEW fourth-order Walsh factors. In the `four_quad_plus_fifth` family an out-of-grammar fifth-order causal factor is added. There are 512 possible action assignments; **288 are unique and disjoint** across OLD80, NEW64, and held OLD/NEW/COLD 48 each. The cold set has new intervention identities under the NEW regime, not a truly new world, changing nuisance context or unbounded semantic transfer. Gaussian outcome noise sigma=0.18. There are no nuisance cues in this experiment. All methods use the same OLD and NEW witnessed labels; the OLD model is cloned frozen for reported historical readout.

An ordinary OMP-style greedy search learns three OLD support terms from a supplied 36-pair parity bank. The NEW search uses a supplied 126-term degree-four parity bank, identical 48-fit/16-validation split, and a shared five-term greedy path. The candidate stops at the first proposed new factor that fails to reduce validation loss by at least **3%**; the conventional `cv_growth` baseline selects the best validation count from the **same path and fits**. `fixed_two` and `fixed_five` use the same path. Strong other controls are train-only alpha-selected ElasticNet on the identical OLD supports plus all 126 degree-four terms, a five-term full-bank OMP, old-support-only Ridge, frozen-old and shuffled-NEW negative. All arms see the same 80 OLD+64 NEW factual outcomes and 48-held OLD/NEW/COLD targets per world, but estimator capacity/compute differs outside the exact matched growth-path comparisons. No physical energy measurement.

The **excluded engineering pilot** seed `109701`, world ID 0, all three families, ran before GitHub source/prereg freeze, with original scorer and independent auditor PASS. It is not confirmatory and must not count toward prospective outcomes. New screening seeds `109711`, `109727`, four world IDs and all three families (24 worlds); reserved primary `109801`, `109819`, `109837` remain unconsumed until a prospectively qualified screening pass. The preregistration and GitHub source-freeze SHA are authoritative for the classification rules. Never reuse consumed seed results to revise them.

Reproduce using Python 3.13.5, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0, single-thread CPU:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -B experiment.py --seeds 109711 109727 --out screen_scored.json
python -B audit.py screen_scored.json --out screen_audit.json
```

Source and auditor are independently authored but share numpy/sklearn/Scipy solvers and the same disclosed synthetic mechanism definition. A refit PASS does not establish general intelligence, independent scientific replication, native Yggdrasil memory, or self-improvement. Remain inside existing evidence-only draft PR #1210; do not merge, change main, native checkpoints, owner, runner, scheduler, queue, accepted refs or deployment.
