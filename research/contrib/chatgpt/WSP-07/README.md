# WSP-07 — Weight-programmed neural control graph

**Public synthetic development only.** Stacked on draft [WSP-06 #871](https://github.com/spoonman136668-ai/Yggdrasil/pull/871). No merge, autonomous research-loop admission, controller change, scheduled task, paid API or independent scientific first-use.

## Change from WSP-06

WSP-06 stored state information as weights but ran a named sequence of 44 Python-level task-specific learning and inference opcodes. WSP-07 compiles the entire bounded task's **control and learning eligibility** into an explicit, inspectable graph of fixed numeric threshold-neuron connections. That includes:

- Action-0 vs action-1 route selection, with numeric synapses instead of Python `if action`
- Two-hop causal consequence readout from learned transition synapses
- Four fixed numeric causal-signature detector neurons, plus action1 reward and coverage synapses
- Numeric contradiction detection for reward errors, successor mismatch, missing causal evidence
- Numeric confidence gating, fault latch and local learning permissions
- One generic activation kernel: each neuron fires when the sum of weighted upstream activity meets its compiled threshold
- One universal gated local synapse rule, applied to *all* writable weights after activation: `w <- bool(w OR (pre AND post AND modulatory_neuron))`

A **single homogeneous neural VM** executes an ordered list of numeric nodes/edges; it does not interpret task-specific `READ_TAPE` or `LEARN_TAPE` instructions. All persistent task-specific memories reside in **177 initially-zero plastic coefficients** (144 transition, 12 action0 reward, 12 action0 coverage, 4 action1 reward, 4 action1 coverage, 1 fault). The compiler programs the *fixed* routing, detector and contradiction-recognition coefficients before experience. The runtime does not instantiate symbolic state-to-class maps, action-conditioned Python logic, reward rule generators or a gradient optimizer.

**Critical limitation:** This is still a **Python implementation of a generic neural virtual machine**, not an autonomous physical neural processor, arbitrary program synthesis or generalized cognition. The compiler was supplied a two-hop causal reasoning design. We are testing whether the cognitive task's control logic can be *represented as weights*, not whether any mathematically unknown inductive bias was independently discovered.

## Frozen experiment

[protocol.json](protocol.json) and [prereg.json](prereg.json) were committed before primary model execution. Use the exact public WSP-05 synthetic generator through the WSP-06 predecessor source. In 32 deterministic worlds, present 12 action0 reward-and-transition events and 8 action1 events (20 public observations), then predict 4 unobserved action1 binary rewards/world (**128 heldouts**). Correct abstention is not credited in this binary outcome task.

Compare numeric threshold graph against WSP-06 numeric opcode predecessor, independent WSP-05 symbolic two-hop signature matcher and 33-parameter **fully converged** Adam MLP, all with identical observations. The frozen trained baseline has seed17, full-batch Adam learning rate 0.03, <=2048 gradient steps/world, BCE <=0.02, and must converge in all 32 worlds for a qualified parity claim. Preserve prior one-step, ID memorization and experience-erasure controls.

### Falsification and safety

A heldout-only reward reversal leaves the 20 public observations unchanged. This is deliberately information-theoretically indistinguishable before seeing a hidden outcome: report all confidently false predictions, rather than claiming the learner can predict unknowable facts. After **one genuinely observed contradictory heldout action1 reward**, the fixed numeric conflict recognition must set the learned fault synapse and suppress all heldout predictions. Abstention is detection, **not** learning the changed rule. Also remove the transition synapses, signature detector fixed edges and action1 coverage, each of which must destroy transfer; cold-restore all weights; replay four previously seen events; isolate separate worlds; reject bad raw inputs and tampered checkpoints.

### Reproduction

Python 3.12 standard library, no ML package required:

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m unittest discover -s research/contrib/chatgpt/WSP-01 -p 'test_*.py' -v
python -m unittest discover -s research/contrib/chatgpt/WSP-02 -p 'test_*.py' -v
python -m unittest discover -s research/contrib/chatgpt/WSP-03 -p 'test_*.py' -v
python -m unittest discover -s research/contrib/chatgpt/WSP-04 -p 'test_*.py' -v
python -m unittest discover -s research/contrib/chatgpt/WSP-05 -p 'test_*.py' -v
python -m unittest discover -s research/contrib/chatgpt/WSP-06 -p 'test_*.py' -v
python -m unittest discover -s research/contrib/chatgpt/WSP-07 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-07/run_dev.py
python scripts/build_code_atlas.py --check-if-present
```

Full final regression must pass at **the final candidate SHA on Ubuntu and Windows**, including all 54 original repo tests, every prior WSP suite, the frozen new public DEV runner, source atlas integrity and clean-tree guard. New research source is confined to `research/contrib/chatgpt/WSP-07/**`. One read-only PR-triggered GitHub Actions workflow and three generated G29 `.ice/code-atlas.*` files are disclosed engineering qualification exceptions outside that source scope.

**Scientific status remains unverified even with perfect engineering results**: no demonstration of intelligence, better sample or compute efficiency, external unknown-world transfer, self-bootstrapped control architecture, or superiority to trained/symbolic baselines. Only the fixed design's task-specific control instructions were compiled into neural weights; a generic numeric runtime remains external.
