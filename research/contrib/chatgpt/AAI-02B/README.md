# AAI-02B: learned associative value under eight-slot memory

This is an **isolated external, synthetic-only contributor** experiment layered on AAI-02A. It does not change the Yggdrasil model, owner loop, controller or accepted scientific state.

## Question

Can a one-pass direct update of 16 association strengths learn which interventions are informative more effectively than a fully trained 16-weight conventional logistic model? Both have the same 32 active interventions, 64 distractors and eight retained-event slots. The **expert** knows the hidden diagnostic channel and is a privileged ceiling only.

Preregistration was committed separately at `32f4b7f3c05bf29533b1e571270c8df4f820de08` **before** code or evaluation results. Do not revise after seeing results.

## Frozen controls

512 TRAIN worlds; 128 each for DEV, disjoint-context TRANSFER and negative; reversal is a separate fixed follow-on with eight more interventions for every arm. Exact paired comparison vs fully trained logistic; active-recent, recent, reservoir, scrambled-label and expert-ceiling checks. Each candidate is exposed to identical active/passive events and eight event slots. Training budgets differ by preregistered algorithm (one-pass direct vs 400-epoch gradient logistic); comparative time is not claimed to be compute-matched.

## Reproduction

```bash
python -B research/contrib/chatgpt/AAI-02B/run.py
python -B -m unittest discover -s research/contrib/chatgpt/AAI-02B -p test_aai02b.py -v
```

This task is a **four-channel synthetic association family**, not novel causal-law discovery, external scientific acceptance or AGI. No claimed performance superiority absent frozen matched control and two-platform qualification. Artifacts and measured results belong here, not in the user's Library.
