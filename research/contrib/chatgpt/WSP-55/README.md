# WSP-55 — Noncommuting operator identification (research-only)

## Source and provenance
- Parent candidate: WSP54 source `52971ffc53279ae93f74b98c1f2301b560d27cee`; draft predecessor PR #945.
- Prospective protocol frozen before the implementation/outcome: `6e999618b29fc812afb82d70b677755a4a981913` (`prereg.json`).
- This successor is draft PR #946, source-blind and unmerged. No DEV/PRIMARY/production/official-loop use.
- Learner sees public 48 A + 12 B chronological physical action-consequence rows. No heldout outputs, oracle codebook, true operation definitions or evaluator phase selector are passed to the learner.
- Strong *declared family-specific prior*: four latent unary affine maps over Z7, prefix-free three-segment 4–6-bit words, 8 entities, 4 operations, 300k search-node and 512-model caps.
- A known 48/12 training boundary remains a protocol-side context cue; completely unsupervised grammar-shift discovery is **not** proven.

## Exploratory WSP53 SELFTEST diagnostic (not scientific qualification)
[Two-platform focused GitHub run #43336232966](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43336232966) on source `4311f9126a8e45ebc08952d2df0bbbf270542b2d` reported exactly **792/792** correct (6 worlds × (48 A + 84 B)), **0** wrong confident, and **243** correct swapped-order physical contrasts on both Windows and Ubuntu. Every fixture had 1 surviving A hypothesis and 1 B hypothesis. The inferred models use zero gradient steps; per-world stored payload is 31,400–32,112 bits including raw observed evidence. The output is deliberately labeled SELFTEST_SIGNAL.

These results are a promising bounded compositional *engineering* demonstration of source-blind operator search. They do **not** show unfamiliar physics, natural language grounding, model-scale knowledge acquisition, efficient whole-process general training, or superiority over an independently fully trained neural/symbolic baseline. The training and evaluation simulator uses the same restricted affine family as the declared search prior. Those shortcomings must remain visible.

## Reproduction
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-55 -p 'test_*.py' -v
```

## Qualification
New source/README/workflow SHA requires requalification. The isolated WSP55 tests and G29 atlas have separate CI duties. The one-shot G29 job is scoped only to a source-pinned, three-file generated-artifact commit; it cannot modify code or the scientific protocol. The inherited full two-platform regression is necessary before any ENGINEERING_PASS. No protected science first-use, merge, promotion or deployment.
