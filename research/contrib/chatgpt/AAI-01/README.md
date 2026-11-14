# AAI-01 — Associative Intelligence: knowledge quantity versus useful links

**Status:** local development mechanism supported, **no superiority**. This is a bounded contributor experiment; it is **not** an accepted Yggdrasil model change, a proof of AGI, a new research-loop worker, or cross-platform engineering qualification.

## Scientific question

Does evidence-based association between two observed relations support new combinations better than adding disconnected facts? Can the learned route be restored and revised after contradictory public evidence?

The candidate learns two numerical vote weights from 96 observed answer examples across 16 generated worlds. It then applies one of two programmer-supplied relation-composition operators to complete **public** A/B edges from 16 previously unseen generated worlds. The route-selection votes are direct scalar edits, **not a neural model learning a novel relational operator**. Extra facts use a separate tagged C relation. After a rule reversal, all methods receive four actual answer demonstrations per new world; the candidate uses an explicitly reset local gate, not a lifelong persistent model update.

## Freeze, identity, and result

- Protected main parent: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9.
- Preregistration committed **before local outcomes**: b9ad110a54e5e2a631270bf45409777de2973314 (prereg.json).
- Exact source commit: 684295d8c6866d9ee3c0d2f99a7cf993b9b0970c, source Git blob f34236375d4f62249361d6e147f37219be2be0a0.
- Source SHA-256: 2c5389ac1182742f1d8c6d182db0b250ce8b27d4583b7e3f3ebfbfaf16780964.
- Local result: result.json; custody, early debug and qualification limitations: provenance.json.
- Input cohorts: train seeds 1000–1015, DEV 2000–2015, rule reversal 3000–3015. These are **consumed public development** cohorts; do not reuse them as independently unseen.
- No original protected scientific first use, paid API, model write, main mutation, owner/controller change, promotion or deployment.

### Local source-only result

| Arm | DEV correct / 384 | Accuracy |
| --- | ---: | ---: |
| Numerical associative gate | 384 | 100.00% |
| Exact symbolic rule learner | 384 | 100.00% |
| Converged logistic route learner | 384 | 100.00% |
| Deterministic random route | 203 | 52.86% |
| Single-step flat association | 11 | 2.86% |

The same candidate results held for 0, 24 and 96 typed, unrelated facts. Candidate, symbolic and conventional arms each obtained **320/320 after four paid rule-reversal examples per world**. Local cold-state, missing-edge, changed-edge, disjoint-seed and shuffled-label checks passed. The conventional two-route logistic classifier reached mean BCE 0.00974628 after 25 epochs. Seven additional focused Python unittest checks passed.

**Interpretation:** the numerical gate can reuse a supplied relational composition route in new generated worlds, but it **ties** two stronger controls and has no demonstrated scientific or computational superiority. The extra C facts do not compete for the same associative capacity, so this does **not** show that large-scale knowledge growth avoids interference. Reversal occurs in a fresh local state rather than a persistent network; do not claim continual learning. No general-language knowledge, grounded new operator discovery or independent unfamiliar-world scientific gain was established. **Integration: NO-GO.**

An initial local pre-source-commit dry run failed because the conventional classifier attempted to fit inherently ambiguous training examples as decisive negative labels. The comparator was repaired by excluding route-ambiguous samples before the final source commit, without touching seeds, scoring thresholds or the tested candidate. The post-source-commit run and repeat produced identical outcome metrics (apart from measured elapsed wall time). The complete development disclosure is in provenance.json.

## Reproduce from a checkout of the exact source branch

Run from the repository root:

    python research/contrib/chatgpt/AAI-01/run.py
    python -m unittest discover -s research/contrib/chatgpt/AAI-01 -p 'test_aai01.py' -v

Requires Python 3 standard library only. Source-only local checks ran in a Linux container using Python 3.13.5; **GitHub Ubuntu/Windows CI, full Yggdrasil regression, G29 source atlas, independent scientific acceptance and actual target-model integration remain UNVERIFIED.** A reported local wall time is not a cross-system or end-to-end efficiency claim.

## Next decision

Do **not** add this into an existing neural model merely because it beats flat lookup. A separately preregistered successor should force genuine competition for a bounded shared knowledge budget, blinded new relation roles, and causal interventions; compare to exact symbolic search, a fully trained model and native candidate on matched information, compute, footprint and cold retention. Only independently qualified benefits can be proposed for each target model's owner-controlled integration path. Preserve Yggdrasil, Weight Programming, Wingless and Hybrid isolation.
