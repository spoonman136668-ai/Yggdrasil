# WSP-13 — Learn new conjunction *instances* in weight space

**Public synthetic DEV only. Draft research stacked on [WSP-12 PR #878](https://github.com/spoonman136668-ai/Yggdrasil/pull/878).** Frozen prereg is committed independently at `34a150f7fa77fa28756532b8f11fb41f62055923`, before implementation or primary model evaluation.

## What changed
WSP-12 supplies all eleven constant/single/pair feature **identities** in the compiled grammar. WSP-13 still supplies sixteen low-degree (zero/single/pair) features and universal neural operations, but its ten **composite slots have no assigned feature address or coefficient**. Actual three-active-bit observations trigger numerical residual gates: when the existing structure is contradicted, a numerical first-free allocator writes a new conjunction's input address directly into synaptic weights. Subsequent four/five-active-bit inputs fire these learned clauses by weighted subset-match and parity readout. The task-specific identity of any triple clause is NOT selected by Python or prelisted in the model's architecture.

This constructs new *feature instances* but **does not invent a new operator type**, infer unknown physics, or avoid all training: writing weights from actual witnessed outcomes is an adaptation/learning process with no gradient descent.

## Frozen scientific evaluation
Exactly 1,024 worlds enumerate all ten cubic coefficient patterns over 5 input bits, with a fixed nonzero lower-degree base polynomial `0xA65D`. The model sees 16 low-degree basis observations and 10 actual triple-context outcomes (26/public world); it predicts all six unseen four/five-active-bit contexts (6,144 hidden). Matched-info independent GF(2) Möbius solver MUST tie 6,144/6,144; fixed base-only, new-feature-ablated, and zero-output controls each 3,072/6,144. All 1,024 models cold restore, and a true contradictory new witness activates the fail-closed latch. No gradient training, paid API, private test, or model inference services.

**Frozen negative:** a genuinely hidden four-way term `x0*x1*x2*x3` changes two of the six withheld outcomes per world but no training observation. The circuit MUST make 2,048 wrong predictions on the alternative, then abstain after witnessing a real contradiction. It **cannot invent a missing new operator** or solve an information-theoretically indistinguishable perturbation.

## Run/review
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-13 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-13/run_dev.py
```
Full qualification requires original Yggdrasil plus all WSP-01–WSP-13 suites and the frozen DEV evaluator on exact final candidate SHA on Ubuntu and Windows 2022, with permanent G29 atlas acceptance and clean-tree checks. The new PR-only CI is read-only and hosted, never scheduled. Research code stays in `research/contrib/chatgpt/WSP-13/**`, with only the CI/G29 companion exceptions.

**SCIENTIFIC SUPERIORITY UNVERIFIED:** exact symbolic ties; no cost, fully trained baseline or independent unknown-world improvement is demonstrated. **DEPLOYMENT NONE:** no merge, controller, FORGE, owner, queue, scheduler, self-hosted runner, accepted ref, or scientific first-use change.
