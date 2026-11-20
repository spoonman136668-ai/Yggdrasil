# ENERGY-58 — Three-episode cumulative causal readout retention

External synthetic research only, never native Yggdrasil training, accepted-science status, controller activity, model deployment, or merge. Existing draft PR #1210, archived under `research/contrib/chatgpt/energy-evidence-20261117/ENERGY-58/`.

The central falsifiable question is whether stage-invariant relation sharing learned from three consecutively observed episodes improves held cold consequence predictions **relative to a matched separate-relations / stage-specific rehearsal regression**, while preserving the exact earlier historical functional readouts across checkpoint serialization and a fresh Python process. This is not a native tokenless Yggdrasil model or evidence of general reasoning.

**Design:** in each synthetic world, 10 independent causal action bits plus two observed nuisance cues. Hidden four paired parity primitives and relations; one shared, one variant, or a new triple relation depending on world family. Three consecutive labeled episodes OLD, MIDDLE, NEW with 84 witnessed randomized causal interventions each, 64 disjoint held OLD/MIDDLE/NEW/COLD assignments. Every learner sees identical observed consequences, no held labels or hidden planted causal coefficients. Candidate selects four parity primitives in OLD only, fits stage-local models, classifies pair relations as invariant based on training estimates across all three episodes, and fits invariant coefficients jointly with stage-specific correction coefficients. Candidate checkpoints retain old/middle readout weights unchanged. Matched controls: independent stage regression on the exact same selected features, a separate stage-encoded rehearsal Ridge with all historic training labels, unconditional sharing, full-feature ElasticNet, RBF KernelRidge, no-update, shuffled new-label update. All methods use 252 factual observations per world. More complex controls differ in capacity.

**Cold restore:** `restore.py` uses only the Python standard library to read a JSON model checkpoint and held **input actions only**. `restart_check.py` launches a distinct isolated Python process for every scored world and requires historical and new/cold predictions within 1e-11 of in-process predictions. Previous episode readout preservation is consequently tested, but this is multiple readout heads conditioned on known episode identity, not autonomous lifelong-learning policy performance or feature-drift resilience.

**Audit:** `audit.py` does not import scorer; it independently reconstructs action/consequence generator, refits every model, checks all held predictions, metric summaries, primitive support decisions and checkpoint values. Both use NumPy/sklearn numerical backends; the scientific claim remains synthetic and bounded.

Excluded source-development smoke seeds `999211` and `999227` evaluated on only world ID 0 for each family (3 worlds each); not confirmatory. They passed independent refit audit and separate-process restore. Frozen primary seeds `100181, 100193, 100207` × source IDs 0..3 × three mechanism families = **36 unseen worlds**; this can run only after source and separate preregistration commits are verified.

Reproduce (single CPU thread; Python3.13.5 NumPy2.3.5 SciPy1.17.0 sklearn1.8.0):

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
tar -xjf source.tar.bz2
python -B experiment.py --seeds 100181 100193 100207 --out primary.json
python -B audit.py primary.json --out audit_result.json
python -B restart_check.py primary.json --out cold_restart_result.json
```

No primary tuning. No data outside self-authored synthetic generator, no paid APIs. Cold shift specifically randomizes two nuisance cues; some mechanisms not expressible by a single pairwise relation. Old/mid historical readout is frozen, not necessarily optimal versus conventional jointly trained hindsight controls. Compute and memory sizes are empirical local measurements, not physical joules.
