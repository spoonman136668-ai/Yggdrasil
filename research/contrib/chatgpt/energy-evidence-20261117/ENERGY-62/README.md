# ENERGY-62 — Constructive causal programs from primitive operations

**Scope: external synthetic development falsification only.** This does not modify native Yggdrasil training, accepted refs, controllers, schedulers, queues, deployments or production weights. It does not prove novel open-ended causal intelligence.

The code supplies **only elementary unary bit tests and binary AND/XOR operations**. It does **not** supply the generator's five-variable conditional, nested XOR or threshold motifs as a dictionary of named high-level operators. The learner first ranks primitive operations by old/new witnessed consequences, carries a bounded old feature-memory to the new episode, constructs higher-order candidate expressions by composing selected primitive operations, then greedily fits five terms (with an explicit small bias toward previously selected old factors). This is finite author-designed *expression search*, not unbounded operator invention or a native architecture.

Fair tests fit a new five-term OMP model, ElasticNet and Ridge **on the identical generated feature bank**, as well as a softmax blend of learned old/new OMP snapshots, raw-input KernelRidge, ExtraTrees, primitive-only OMP, old-only frozen memory, and shuffled new-label negative. All methods see 64 OLD and 64 NEW factual witnessed do-intervention outcomes in each world, without hidden factor roles or held outcomes. 32 held OLD/NEW/COLD test interventions per world, all 224 underlying eight-bit causal assignments are unique. Two nuisance input bits switch correlations; cold nuisance bits become independent. Only 8 causal bits plus 2 nuisance bits are observed, with no tokenization. High-order primitives and context shifts are generator-designed synthetic data.

Source and independent auditor are frozen in `source.tar.bz2` with exact hashes in `source_manifest.json`. The audit does **not** import `experiment.py`; it reconstructs generator interventions and hidden consequences, refits every conventional and candidate method and checks each held prediction. It uses the same NumPy/sklearn numerical solvers and published generator specification, so it is not completely independent science.

An excluded implementation seed `889811`, world ID 0, three families, was scored before freeze and **must not be counted** as prospective evidence. A stronger softmax-memory comparator was added after that development test and before source freeze; development test then reran unchanged after source revisions. The fresh confirmatory screen and stop decisions are in a **separately committed preregistration**, not retrospectively inferred.

Reproduce in a Python 3.13 environment with NumPy 2.3.5 and sklearn 1.8.0, single-thread BLAS:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir source && tar -xjf source.tar.bz2 -C source
cd source
python experiment.py --seeds 997711 997733 --out /tmp/e62.json
python audit.py /tmp/e62.json --out /tmp/e62_audit.json
```
