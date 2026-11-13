# WSP-54 — Gradientless causal circuit construction (SELFTEST only)

## Question and method
Can physical consequences of raw, undelimited binary acoustic instructions be used to *construct*, rather than optimize, numerical transition rules?

`compiler.py` never receives an oracle codebook, supplied word boundaries, generator objects, latent entity/verb/destination labels, pretrained representations, or a loss gradient. It observes 48 Phase-A and 12 Phase-B physical transitions. For the anchored-effect world it enumerates causal role and codeword hypotheses, requires global consistency, infers modular transformation coefficients, and compiles integer circuits. Only unanimous, complete hypotheses predict; incompatible or exhausted hypotheses abstain. Phase-B changes raw order and requires relearning the **role ordering**, not the numerical meanings. Cold restoration reconstructs the compiled hypothesis from preserved observed evidence.

## Fixed engineering evidence
At code commit `032318c8929e158b365f1c02f679214a631fc84b`, [source-only SELFTEST run](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43332936876) passed on Linux and Windows. The historical run's final step failed on an out-of-date G29 source atlas, which is **infrastructure**, not a failed model test. The exact per-world receipts and results are in `result.json`, and the source/protocol identities in `provenance.json`.

| Family | Original A heldout | Changed-grammar B heldout | Wrong-confident | Outcome |
|---|---:|---:|---:|---|
| Anchored-effect (6 fixtures) | **288/288** | **504/504** | **0** | One surviving fully consistent rule hypothesis per fixture |
| Noncommuting-order (6 fixtures) | 0/288 | 0/504 | 0 (all abstentions) | Not yet implemented; no demonstration |

The earlier WSP53 count-only anchored-effect control had **191/288 A** and **87/504 B** correct. This is a meaningful *within-source engineering diagnostic*, not an independent scientific superiority claim. There were zero gradient updates, but nonzero computational hypothesis-search cost and substantial memory for raw experiences. Search consumed **34518** nodes across anchored fixtures.

## Limitations and next falsifiable target
- The modular-additive effect hypothesis class strongly matches this synthetic physical world. Correct recovery is **not** evidence that the method learns unfamiliar physics, general language, or arbitrary causal operations.
- Noncommuting operator discovery remains absent; the hard order task currently abstains entirely. The next independent, frozen test should require learning the operator maps and discovering *which of two operations applies first* with no source-side labels.
- Control parity is not established: a fully trained conventional neural control, exhaustive symbolic comparator, hardware-neutral wall/CPU/memory costs, and a genuinely disjoint source are required.
- WSP53 DEV and PRIMARY remain sealed. No WSP54 DEV or PRIMARY evaluation, scientific acceptance, production integration, or merge is performed.

## Reproduction
```bash
python -m unittest discover -s research/contrib/chatgpt/WSP-54 -p 'test_*.py' -v
```
