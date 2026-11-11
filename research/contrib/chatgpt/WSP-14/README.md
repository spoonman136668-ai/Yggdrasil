# WSP-14 — From examples to synthesized *operations* using only NAND

**Public isolated synthetic DEV.** Stacked on draft [WSP-13 PR #879](https://github.com/spoonman136668-ai/Yggdrasil/pull/879). The protocol was frozen at `98c2391537c02a31165490c49b3102add5928bec` **before implementation or first primary evaluation**.

## What changes versus WSP-13
WSP-13 writes newly addressed conjunction instances while keeping all operation types preprogrammed. WSP-14 starts from a **single universal two-input NAND primitive**, three raw input wires, and 14 blank numeric gate sites. A deterministic bounded **external program synthesizer** enumerates minimal NAND expression trees and selects a program compatible with five actual public examples. It then compiles the selected previously unnamed composite function directly into weighted-threshold synapses. Runtime executes only generic numeric sums and thresholds. XOR, majority, parity, MUX, etc. are *not provided as named compiled functions*, but may be expressible as NAND compositions.

**Critical honesty:** The search algorithm and NAND vocabulary are programmed by Python. This is **conventional bounded program synthesis plus numeric circuit compilation**, *not autonomous discovery of a new neural primitive*, no-learning intelligence, or native general reasoning. The model receives no target function mask, hidden labels, or task-specific full table at synthesis time.

## Frozen information stress test
Every one of the **256** three-input Boolean functions is evaluated. Give exactly five public contexts (indices 0,1,2,4,7) and withhold the three others (3,5,6), for 1,280 public and 768 hidden binary labels. All 256 Boolean functions must fit in 14 NAND expression-tree nodes; every selected circuit must fit all public examples and exactly match its separately evaluated NAND expression for all 2,048 input queries. Independent equal-information symbolic minimum-NAND solver must tie.

**Information bound:** Exhaustive unrestricted worlds always contain eight indistinguishable possible hidden truth vectors per five public examples. Thus any deterministic inference method must score **exactly 384/768 hidden correct**, even with perfect program synthesis. Also compare a genuinely converged Adam-trained 8-hot 8-parameter logistic memorizer using exactly the same five observed labels (frozen BCE <= 0.02 and <=2048 steps), zero-output, and an observed-only abstaining memory. Full converged multi-layer conventional comparison and whole-process cost superiority are **not established**.

Report a **predeclared lower-complexity subset** of target functions (minimum NAND tree cost <=4) without changing search rules or frozen thresholds; this can show the impact of the explicitly supplied simplicity prior but is not a blind external test. Flip all three hidden labels, keeping all observed labels unchanged, to preserve an information-theoretic OOD negative; do not claim a hidden-rule fix. Cold restore 256 compiled numeric circuits; require at least one gate ablation to alter output; reject malformed input, corrupt and noncanonical checkpoints.

## Reproduce (Python 3.12 stdlib)
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-14 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-14/run_dev.py
```
Final engineering qualification requires **all original Yggdrasil tests and WSP-01 through WSP-14**, frozen runner, source integrity, committed G29 atlas and matching exact-final-SHA GitHub-hosted Windows/Linux CI. PR-only, contents:read; no schedule, self-hosted runner or paid API.

**SCIENTIFIC SUPERIORITY UNVERIFIED; DEPLOYMENT NONE.** Draft/unmerged. No owner/controller/research-loop, accepted refs, main, FORGE, Wingless, private scientific first-use, or live training changed.
