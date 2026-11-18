# ENERGY-43 — Native-free discovery and retention of unknown causal factors

External synthetic intervention-consequence learning contribution for Yggdrasil. This is NOT native Yggdrasil training or scientific acceptance. No controller, runner, scheduler, accepted ref, main, or deployment modifications.

Prior ENERGY-41/42 fitted three provided reliability groups on XOR graph constraints. ENERGY-43 instead fits one sequential, persistent sparse factor learner that must discover five underlying signed causal interactions from noisy labeled interventions: three persistent shared mechanisms, one old-context-only and one new-context-only. Ground-truth factor supports/weights are never passed to a learner. A finite known grammar (unary parity, pair/triple parity, pairwise AND) is available to all models: this does not constitute arbitrary new operator invention or genuine open-world cognition.

The learner carries three discovered structures from old-context training into new-context acquisition, refits them with bounded anchoring, adds new structures, and then faces a third cold nuisance-distribution shift. Eight arms use identical 96 old + 96 new labeled interventions per world: structural-energy candidate, no-memory ablation, anchored conventional OMP, standard exhaustive-grammar OMP, Ridge, ElasticNet, 60-tree random forest, and shuffled-label negative. Each prediction uses 128 disjoint old/new/cold interventions per world.

Source and auditor freeze precede prospective prereg and primary scoring. Exactly three smoke-only source worlds from seed 99811 were exercised before freezing and independently checked (9,753 source/fit/prediction checks PASS). Primary seeds 8617,8629,8651 remain untouched until after prereg is committed. No after-score tuning.

Unpack and run locally from the pinned source:

    python -c "import bz2; from pathlib import Path; [Path(n).write_bytes(bz2.decompress(Path(n+'.bz2').read_bytes())) for n in ('experiment.py','audit.py')]"
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python experiment.py --primary --out scored.json
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python audit.py scored.json --out audit_result.json

The data are locally generated, not protected scientific first-use; the fixed grammar and synthetic observation generator are explicit limitations. Compare against frozen prereg.json and REPORT.md before drawing conclusions.
