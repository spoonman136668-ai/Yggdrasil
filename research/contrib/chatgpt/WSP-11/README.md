# WSP-11 — Direct neural weight compilation from incomplete evidence

**Public isolated DEV only, stacked on [WSP-10 PR #876](https://github.com/spoonman136668-ai/Yggdrasil/pull/876).** The frozen protocol is [prereg.json](prereg.json), committed FIRST at `aaa52aef5bfc4ea4a511635405196f7d84d0ef18` before the first primary test. No authority to merge, promote, deploy, alter the owner loop, schedule jobs or conduct independent scientific first-use.

## New test (versus WSP-10)
WSP-10 converted all eight truth-table labels into crossbar synapses. WSP-11 receives only four actual Boolean observations for each of the 16 possible 3-input affine parity functions. A **programmed external GF(2) rule** completes the unknown four labels, then uses the unchanged WSP-10 numerical `DirectCrossbar` to write all task-specific synaptic connections. The numeric circuit reads its weights for heldout predictions, never a function mask. It takes zero gradient steps.

This is conditional generalization, **not zero-information learning, invention of the affine prior, or neural discovery of an unknown computational operator**. It uses a strong prior and an external symbolic coefficient solver. The equal-information exact symbolic control MUST tie 64/64.

## Falsifiable controls
The four public contexts are `000, 100, 010, 001`; four withheld contexts are `110, 101, 011, 111` in low-bit-first indexing. An observed-only crossbar and all-zero baseline are expected to score 32/64. An alternative function adding `x0 AND x1` agrees with **all four observations** while reversing two hidden labels per world: a required **32/64 wrong hidden predictions**. After a real contradictory witnessed outcome, the model latches a fault and abstains; it cannot repair the unknown rule.

All 16 world checkpoints must cold restore; reject malformed inputs, tampered snapshots and 2-input checkpoints. No classifier accuracy superiority over symbolic, total compute/data savings, native operator invention, independent transfer or scientific qualification is claimed.

## Local reproduction
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-11 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-11/run_dev.py
```
Only Python 3.12 standard library and inherited WSP-10 source. For final engineering acceptance run **all original Yggdrasil tests and WSP-01 through WSP-11**, including this evaluator, against the **exact final SHA on Ubuntu and Windows**. Require separate permanent G29 atlas acceptance, clean source, and CI receipts. No claim of completion before those receipts.

Research changes stay under `research/contrib/chatgpt/WSP-11/**`; one PR-only read-only hosted CI workflow and generated G29 atlas artifacts are qualification companions, not hidden science.
