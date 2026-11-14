# WSP87 — first compositional knowledge substrate using direct numerical weight writes

**Track:** external isolated weight-programming research, not Yggdrasil accepted cognition or a controller.

**Base:** WSP86 draft PR #982 at `6db3296197ba75aa83a87549ad1a1742d206b7c2`. Preregistration was committed **alone** at `fb0eb522a0c7a3155ca28d30ed4dba9d993dbcc5`, before WSP87 code and developmental outcomes. The WSP86 development result is preserved as **DEV_COVERAGE_NEGATIVE** (10/13; no gain over active/random; residual abstention confined to cold start).

## Objective, not a claim

The next constraint on broader knowledge is to preserve and compose acquired relationships without using a predefined fact-answer table. WSP87 writes directly executable numerical relation matrices from grounded observations, extends the matrix as entities appear, and performs exact two-hop numerical composition via a matrix product. The observation interface provides full-string grounded identities; it does NOT learn names, parse prose, tokenize linguistic input, discover arbitrary inference rules, or train a world model.

This is intentionally a conservative necessary-substrate experiment, not evidence of human-level general knowledge. An equally expressive symbolic graph is expected to **tie exactly**. Any claimed superiority would be false.

## Frozen experimental design

Eight never-used synthetic DEV seeds 12011–12018. Each world contains 12 initial opaque entities, 4 additional entities and 3 source-salted opaque relations. Stage A pays 22 directed factual observations about two relations; Stage B pays 23 observations including a third relation, entity growth and two explicit retractions/replacements. No evaluator labels are accessible to the writer or independent graph. All query outputs and numerical snapshots freeze before evaluator truth is used.

Score every exact 1- and 2-hop query on known identities, unknown-identity abstentions, unseen exact-two-hop true implications, retained unaffected old truths, actual contradictory updates, numerical cold restoration, checksum rejection, zero-matrix negative controls and whole-process CPU. The strongest exact-expressivity comparator is an **independently implemented set-based graph** trained on the same observations; a literal one-hop lookup shows what composition adds, not an intelligence comparison. Controlled graduated world sizes are future separate tests, not silently substituted for this preregistration.

Frozen DEV thresholds: Stage A/B each >=99% correctness; 100% unaffected true-fact retention; 100% correction of the two retracted edges per world; >=100 novel correct two-hop consequences over 8 worlds; exact numerical vs symbolic query parity, no confident unknown labels, checksum-validated cold restore, all process timing. Passing these says only `DEV_SUBSTRATE_FEASIBLE`, not `SCIENTIFIC_PASS`. Failure is `DEV_SUBSTRATE_NEGATIVE`; never revise frozen conditions to recover a pass.

## Execution and isolation

Public structural fixture only:

```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-87 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-87/experiment.py --structural-fixtures-only
```

Reserved unregistered DEV source **must not be used until candidate source, inherited full regression and G29 atlas are qualified on both Ubuntu and Windows**. Then run once with `--frozen-unregistered-dev-only` and preserve the negative or feasibility outcome in the existing repository. All model weights are numerical floats stored in the snapshot; no paid API, pretrained transformer, official research loop, protected science, deployment, runner or scheduled task is changed.

## Roadmap toward meaningful knowledge

1. WSP87: direct-weight relational storage and unseen two-hop composition (an engineering substrate milestone, not language intelligence).
2. A prospectively separate **raw-utterance grounding** test: learn to bind new natural phrasing to entities/relations from action consequences, rather than hardcode a vocabulary; contrast WSP51/WSP52 negatives and fully trained controls.
3. A prospectively separate **source-backed factual knowledge** test: ingest real, redistributable attributed statements; preserve source identity, time, conflicting reports, abstention and correction without erasing unrelated evidence.
4. A disjoint-domain **generalization and lifelong-memory** test: unfamiliar predicates, changed entity distributions, multistep interventions, cold retention, interference, memory/compute scaling and a strong independently trained baseline.
5. Only then benchmark practical question answering and reasoning on unseen corpora against modern general-purpose assistants. No synthetic parity milestone is a surrogate for this outcome.

**No main merge, accepted-ref promotion, official Yggdrasil/FORGE integration, scientific first-use, library artifacts, deployment, scheduled work or new executor authority.**
