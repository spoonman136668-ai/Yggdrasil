# WSP-12 — Numeric selection of pairwise rules from observations

**Isolated public development only**, stacked on [WSP-11 PR #877](https://github.com/spoonman136668-ai/Yggdrasil/pull/877). Frozen [prereg.json](prereg.json) committed at `238921f1eebc7e7d32be0c0d833dcd2084752ac2` **before** implementation, testing or metric inspection.

## What changed
WSP-11's Python code explicitly inferred all affine coefficients and then compiled the resulting complete function into WSP-10 numerical weights. WSP-12 provides a *fixed* family of 11 polynomial features (bias, four main effects, six two-way interactions) and a common numerical threshold kernel. Each genuine public observation activates numerical context recognizers and discrepancy gates; an eligible local rule writes the newly supported coefficient to its initially blank plastic synaptic weight. The model uses its own synaptic weights to calculate all future XOR/parity outcomes. **Python validates witness order but does not choose which coefficient to write or predict from a stored function mask**.

This is genuine **evidence-conditioned selection of preexisting rule terms**, not creation of new mathematical primitives. It uses deterministic, monotone non-gradient updates (a form of training/adaptation), rather than zero-data intelligence.

## Frozen comparison
All 2,048 possible four-input GF(2) degree-two functions, all 11 constant/single/pair observations, five unseen triple/quadruple contexts per world = **10,240** heldout binary predictions. Matched-information exact symbolic GF(2) solver must tie **10,240/10,240**. Linear-only, pair-synapse-ablated and zero-output controls must each tie at **5,120/10,240**; all 2,048 cold checkpoints and contradiction latches must pass; zero gradient updates.

The **unalterable OOD negative** adds a cubic `x0*x1*x2` that is false at all 11 public contexts and reverses two of the five hidden labels per world. A perfectly trained degree-two prior must make **4,096** incorrect hidden predictions under this alternative. After one truly observed contradiction it must latch a fault and abstain; that is detection, not recovery. A hidden data-leak or post-outcome protocol change invalidates the experiment.

## Reproduction (Python 3.12 stdlib)
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-12 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-12/run_dev.py
```
Full engineering qualification requires the original Yggdrasil suite, WSP-01 through WSP-12, the frozen exhaustive evaluator and permanent exact-source G29 atlas, with clean-tree guard, on both Windows and Linux at the **same exact final commit**. A run on an intermediate commit is only development evidence.

**Scientific status remains unverified**: feature grammar and order are preprogrammed; identical-information exact symbolic inference ties; no strong converged trained-model/cost comparison, unknown-operator synthesis, independent general-cognition evidence, or measured end-to-end cost advantage. **Deployment none**. No merge, owner/controller/autonomy loop changes, schedules, paid API, accepted-state edit or independent scientific first-use.
