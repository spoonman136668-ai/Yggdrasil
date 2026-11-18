# YNCA-13 — new operator creation with retained old laws

This is an isolated, tokenless source-free developer falsification, **not native CKAD/Yggdrasil model training**.

YNCA-12 demonstrated confident failures on an unseen causal operator. The next question is whether an unlabeled episodic operator memory can allocate new rules from intervention consequences alone, and whether four adaptive do-actions are sufficient to avoid repeating novelty harm.

* Frozen prereg commit: `8df5ad7bca6b71c9f1f5a52e2d4fa57104f1cd3d`.
* Frozen evaluator source commit: `e7ceaf6bb95970074809711ec4dea313bf5557fe`.
* Accepted parent: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. No protected source first-use.
* Input: 32 episodes of complete action/outcome tables (16 familiar AND/OR followed by 16 previously unseen XOR/MAJ); memory only sees interventions and responses, not generator family names.
* Eval: four adaptive do-actions per episode, four withheld actions, across five laws including never-trained MUX. Three fixed seeds, fully fitted exact 256-function posterior, matched four-function posterior, no-memory, last-world and equal-budget random-probe controls.
* Rules are **3-bit truth tables**; mere allocation of two new tables is not proof of unbounded hypothesis discovery or general intelligence. Repeated test episodes of the same rule are not independent causal families; they estimate probe-sequence effects only.
* Frozen development verdict is explicitly defined in prereg, including the unseen-MUX harm ceiling. This is not scientific acceptance even if the developmental screen succeeds.

Reproduce after the source freeze:

```bash
python -B research/contrib/chatgpt/YNCA-13/experiment.py --output research/contrib/chatgpt/YNCA-13/run-result.json
```

Evidence is collected by the read-only Linux/Windows source-free GitHub Actions workflow. Postrun file insertion must not modify the frozen source or prereg. Preserve a failed verdict unchanged. Do not merge/promote/deploy, access original protected worlds, change Yggdrasil weights, or dispatch FORGE.
