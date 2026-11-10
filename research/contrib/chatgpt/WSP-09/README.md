# WSP-09 — Neural self-allocation of unseen association identities

**Public synthetic development experiment only**. Stacked on draft [WSP-08 PR #873](https://github.com/spoonman136668-ai/Yggdrasil/pull/873); no merge, research-loop integration, scheduler, owner/controller/runner change, paid API, independent scientific first-use or deployment.

## Why this advances the weight-programming experiment

WSP-08 learned *which* of three predetermined feature depths to enable. WSP-09 instead tests whether a homogeneous neural circuit can **choose a previously unused representation slot and program its own address and label synapses** in response to an observed input/consequence pair.

The circuit has **16 blank, structurally identical slots**. Each slot contains a 1-bit occupied weight, four address-bit weights and one binary consequence weight. Plus one numeric contradiction latch, that gives **97 initially zero, experience-writable synapses**. The compiler adds only two distinct fixed numeric coefficient values (+1 and -1), shared by directed neural edges, and neuron thresholds.

A fixed numeric circuit compares observed context bits with learned slot addresses, recognizes whether a pattern is known, chooses the first free slot when novel, and routes the actual observed label into that slot's synapses. The **generic runtime** executes one neuron rule (weighted incoming sum ≥ fixed threshold) and one local three-factor Boolean-OR synaptic update. **Python does not select a slot, compute a pattern key, look up learned consequences or choose an outcome** in the direct circuit. All subsequent inference requires the learned numeric address/reward weights. Checkpoint serializes every fixed/plastic numeric coefficient, graph hash and integrity digest.

**Precise novelty limit:** This constructs new learned representation **instances**, but the compiler supplies the equality operation, first-free allocation policy, address/label slot format and local learning rule. It does **not** invent new computational operator **types**, discover causal dynamics outside a provided feature vocabulary, or remove the external generic Python neuron virtual machine.

## Frozen data, information limit, and controls

[protocol.json](protocol.json) was committed before any WSP-09 model run, followed by [prereg.json](prereg.json). Input is four raw binary bits plus an actually observed binary consequence; three-bit worlds pad the fourth bit with zero. No latent class, truth-table oracle or preenumerated input representations are passed to the neural model.

- **All 256 three-input Boolean truth tables**, each with eight distinct input/reward interventions in a frozen deterministic order.
- **72 four-input Boolean truth tables**: eight predeclared structured masks plus 64 SHA-256-derived, distinct sampled masks; each has 16 genuine observations.
- **328 independently instantiated functions and 3,200 actual observed context/reward pairs.** Before each *first* observation the neural model must abstain (unknown); after each observation it must correctly recall that label. After full exposure all 3,200 labels must remain available, cold-restored and equal to an independent exact symbolic associative memory receiving identical data.
- **Trained comparator:** a deterministic full-batch Adam logistic output layer with 16 trainable weights over a fixed 16-hot encoder, trained on exactly the same observations from eight predeclared 4-input functions. Seed17, learning rate0.05, max3000 epochs, BCE stop<=0.02; report any nonconvergence rather than treating an unqualified baseline as a scientific advantage. This is an in-sample memory comparator, **not** a heldout generalization test.
- **Frozen negatives:** An unobserved input must trigger abstention, not a guessed prediction. In all 328 worlds, a genuine *contradictory* second outcome for one already witnessed input must activate a numerical safety latch, suppress all predictions and claim **zero recovery of unknown changed labels**. Reject fifth-bit inputs and corrupted/noncanonical checkpoints; verify used/label/address ablations.
- **Worst-case data bound:** An arbitrary 4-bit Boolean truth table contains 16 independent unknown labels. Without a useful prior, guaranteeing correctness on all 16 requires up to **16 actual observations**. WSP-09 deliberately measures weight-space *construction* rather than claiming fewer data samples.

## Qualification

Read-only GitHub-hosted dual-platform full regression on **exact final source SHA**. Original Yggdrasil tests and all WSP-01–WSP-09 tests must pass, plus 328-world frozen DEV run, G29 source atlas integrity and clean tree:

```sh
python -m unittest discover -s tests -p "test_*.py" -v
for i in 01 02 03 04 05 06 07 08 09; do
  python -m unittest discover -s "research/contrib/chatgpt/WSP-$i" -p "test_*.py" -v
done
python research/contrib/chatgpt/WSP-09/run_dev.py
python scripts/build_code_atlas.py --check-if-present
```

New research source belongs only under `research/contrib/chatgpt/WSP-09/**`. The read-only `pull_request` workflow and three generated G29 atlas companions are explicitly disclosed **engineering-only** changes outside the research path.

**SCIENTIFIC STATUS: UNVERIFIED** even if engineering passes. Exact symbolic memory is expected to tie on all memorized outcomes, and a fully trained control may likewise tie. No unobserved Boolean truth-table prediction, unknown causal operator invention, general intelligence, matched energy/compute advantage or first-use of independent unfamiliar environments follows from this author-visible synthetic pilot.
