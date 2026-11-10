# WSP-08 — Evidence-driven neural representation growth

**Public synthetic development; draft, unmerged; stacked on [WSP-07 PR #872](https://github.com/spoonman136668-ai/Yggdrasil/pull/872).** No change to the existing FORGE, Wingless or Yggdrasil owner/controller, research queue, schedule, training loop or accepted `main`. No paid API, autonomous research dispatch, independent scientific first-use or deployment.

## Why this is not another fixed-depth causal demonstrator

WSP-07 compiled a complete *two-hop* causal state solver into fixed numeric threshold circuitry and plastic memory synapses. Its feature structure was explicitly programmed before exposure, including the need for two action-0 reward observations to identify an action-1 consequence.

WSP-08 tests whether the **numeric circuit can choose how much representation it needs from evidence**. It begins at a one-hop action-0 consequence representation, which is sufficient in one subset of worlds. When publicly witnessed action-1 labels contradict for the same current representation, numeric neural conflict gates allocate a **plastic depth-two feature-enabling synapse**. If conflicts remain at depth two, a **depth-three synaptic switch** activates. A contradiction at the full known depth sets the numeric safety latch and suppresses predictions.

The generic runtime executes only weighted sums, thresholds and the same three-factor plastic OR rule. Its task-specific causal feature derivation, contradiction recognition, memory readout, write permissions and confidence/safety logic are compiled into a flat fixed numeric graph. All experience-dependent transition, reward, coverage, training-feature and representation-depth information lives in **747 initially-zero plastic scalar weights**.

**Limit:** The *family* of one-, two-, and three-hop action-0 consequence features and the structural splitting rule are programmed in advance. The system chooses among them using genuine public outcomes; it does **not** invent a previously unavailable causal operation or a general-purpose representation language. The generic numerical VM and one-hot identity encoder are still Python software.

## Frozen challenge (committed before outcomes)

See [protocol.json](protocol.json) and [prereg.json](prereg.json). The authored DEV simulator contains eight hidden behavioral classes q=0..7 with three opaque integer-ID replicas each, randomized separately for 12 deterministic seeds. Three modes require different causal representation depths for action-1 reward: 1, 2 or 3 public action-0 successor-reward hops. The learner is never provided the hidden state class, world mode or generated label function.

Each of 36 worlds supplies **24 real action-0 transitions** plus **16 real action-1 outcomes** from two replicas per class; the third replica remains unseen for action1. Predict eight heldout action-1 binary rewards, for **288 predictions** total, counting abstention as incorrect.

Required controls are an **independent exact minimal-depth symbolic learner**, two fixed-depth (one-hop/two-hop) controls, experience-erased circuit, and a **fully trained** 3-input/8-hidden/1-output Adam MLP with 41 trainable floats, using identical 16 public action-1 training labels and three publicly observed consequence features. The MLP training criterion is frozen: seed17, full-batch Adam LR0.03, up to 2048 steps/world, binary cross entropy <=0.02. Report every failure to converge; an unqualified MLP is never evidence of algorithmic superiority.

The frozen **unobservable alternative** flips only the eight never-before-seen replica2 action-1 rewards, preserving all 40 exposed training outcomes. It is impossible to distinguish from public evidence alone. Before a true hidden outcome is witnessed, count all false confident predictions. After one real contradiction, the numeric fault weight must activate and the circuit must abstain, **not claim hidden-rule recovery**.

Test exact cold weight restoration in all 36 worlds, replay of four already-observed interactions, separate model/world isolation, transition-memory ablation, action-1 coverage ablation, malformed inputs, corrupted checkpoints and complete source provenance.

## Qualification

```sh
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-01 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-02 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-03 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-04 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-05 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-06 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-07 -p "test_*.py" -v
python -m unittest discover -s research/contrib/chatgpt/WSP-08 -p "test_*.py" -v
python research/contrib/chatgpt/WSP-08/run_dev.py
python scripts/build_code_atlas.py --check-if-present
```

Exact-source full Windows and Ubuntu GitHub-hosted qualification is mandatory after **all final commits**, including permanent evidence; maintain G29 atlas and clean checkout. Research scope is `research/contrib/chatgpt/WSP-08/**`. One read-only PR-triggered CI workflow and three mandatory generated `.ice/code-atlas.*` artifacts are engineering companion deviations, not additions to the experiment's frozen hypothesis.

**SCIENCE UNVERIFIED** even if numeric feature selection passes all public worlds: exact symbolic and converged trained controls are strong baselines; inference and data budgets are not matched to independent unknown-world scenarios, hardware operation or total compute/energy. No merge, promotion or research-loop deployment from this development experiment.
