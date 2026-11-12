# WSP52 — independent symbolic corpus comparator (developmental prototype)

This *prototype* is a separate implementation from the numeric direct writer and its evidence-gated readouts. It reads only complete undelimited acoustic bit strings and actual before/after physical states. It does not receive source codewords, role identity, grammar order, destination/verb labels, heldout targets or a trained model.

- Repeated visibly changed entity positions provide corpus-only intersections of candidate binary word boundaries, under the explicitly supplied 4..6-bit / three-word structural prior. No-ops never identify an entity.
- Ordered residual acoustic pairs map to observed final locations only where a unique parse exists. Pair contradictions result in abstention; missing concepts are not guessed.
- For phase-B adaptation, it considers three new entity positions and both possible residual pair orientations, scored only on the six observed B consequences. That is *resubstitution*, not independent validation; count all comparisons and do not assert learned independent grammar semantics.
- Competing highest-support interpretations must agree before returning an answer. The implementation does **not** exhaustively maintain all codebooks, all segmentations and all hypothesis assignments. It is **not yet the strong exhaustive symbolic baseline required by prereg.json**.
- Retains all 42 paid experiences in its snapshot to support reproducible parsing and cold restoration. Full persistent serialized bits are reported. It is not capacity- or compute-matched to the direct writer or a neural model.

Reproduce SELFTEST-only: `python -m unittest -v test_symbolic.py` from the WSP-52 directory. The test prints all six original SELFTEST seed/encoding conditions, including failures, into GitHub CI logs. No DEV or PRIMARY cohort has been sampled. A direct instance of this class cannot by itself enforce scientific first-use; enforcement must live in a segregated, owner-admitted harness.

**Scientific boundaries:** The physical simulator has a destination/verb observational symmetry, and the prototype does not infer separate meanings. Its phase-B selector uses B observations for resubstitution, so there may be optimistic selection and confident errors. Results here are preliminary software-development diagnostics, not a scientifically qualified comparison or a claim of superior language learning.

**Remaining:** exhaustive symbolic consistency comparator, genuinely trained conventional temporal comparator, exact-64-step warmup hybrid, matched source/capacity/whole-process cost, independent protocol review, final G29 Linux/Windows qualification, and separately admitted protected primary tests. No merge or production integration.
