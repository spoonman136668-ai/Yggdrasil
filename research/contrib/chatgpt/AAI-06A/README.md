# AAI-06A — Growing causal expression graphs under bounded memory

This is an isolated external contributor experiment, **not** a native Yggdrasil change. It follows AAI-05, where direct learning was simply MAP selection from a complete 60-rule library. AAI-06 instead builds *two-level composite expressions* from 30 primitive input-pair gates without pre-storing the 5,400 possible full programs per consequence bit. The learner selects six promising first-stage primitives, expands them with candidate partner gates/root/bias, and retains its best assembled graph.

**Matched strong control:** exhaustive MAP over the *exact same* grammar of 5,400 programs/bit and the same 16 noisy interventions. Conventional 300-epoch polynomial logistic, random graph, and shuffled-label controls share the same observations. Development worlds have XOR roots; transfer worlds have AND/OR roots. All algorithms know the primitive and root vocabulary, so this is **compositional program search**, not invention of a never-before-seen primitive. Numerical thresholds, cohort splits, inference time, rule-search counts, and shared memory are preregistered at commit `71941d3d825050977ab5fb8a4d8dd6489d5bd546`.

The memory test writes three unrelated worlds into one two-slot mutable store. World A has a *publicly supplied* priority higher than B/C; a value-aware policy preserves A, whereas LRU loses it. Both graph-growth and exhaustive MAP get the same retention policy. This is a controlled capacity/eviction demonstration, **not** learned importance or unconstrained continual learning.

Scientific validity requires exact candidate provenance, all controls, no post-result changes, and cross-platform full regression. A positive result is still only an external developmental candidate, and cannot authorize model integration.

Mechanical tests use reserved seeds only:

```bash
python -B -m unittest discover -s research/contrib/chatgpt/AAI-06A -p test_aai06a.py -v
```

Primary source command (run once under source-locked workflow):

```bash
python -B research/contrib/chatgpt/AAI-06A/run.py
```

Evidence and provenance are stored in this GitHub research contribution only; not in user file storage.
