# Yggdrasil 2.0 — CCE-04: Evidence-selected causal beliefs under partial observability

**Outcome: MIXED (scientific gain NOT verified).** This is a bounded synthetic
development experiment on the isolated draft research branch, not a new native
Yggdrasil architecture acceptance.

## Frozen identities and custody

- Original candidate parent: `274b470507fa892a408252a3e98315d19f534b69`.
- Preregistration was committed first: `8ac9dbebaba21b50a27f3bbbc64870656cf831bd`.
- Pre-result code, tests and evaluator commit: `9fa5ad2a3b6b7e8cc8014d92f8c357c3a6e277f9`.
- Original pre-result source tree: `a8759545a37f49d228c21c275115bf853baa8198`, verified directly using GitHub git/commits.
- All three executed local code files matched GitHub's actual Git blob SHA before the primary experiment.
- Original frozen primary result and its original stdout share SHA-256
  `03a964cb92cd60308df974a57ced56cf1570b0d604c285cbe2b98396b9cf137e`.
  The committed `result.json` is a field-preserving normalized reconstruction,
  **not byte-identical original output**; original source JSON remains in the
  isolated working environment. No rerun was used to construct this record.

## Hypothesis

Can a small population of independently scored causal mechanism hypotheses
infer a hidden binary state from action-conditioned, noisy observations, and
forecast an untrained sequence of actions? Each candidate computes an online
Bayesian belief about hidden state while evaluating *only public observations
and actions*. Different candidates compete via complete-public-trajectory
likelihood. An iid null hypothesis is preferred unless evidence exceeds a
precommitted penalty. The surviving model is stored in a small, integrity-
checked cold checkpoint.

This is a **fixed 36-candidate central selector**, not autonomous invention of
state variables, neural cellular topology, spontaneous scientific discovery or
a proof of general intelligence.

## Frozen experiment

Positive world: hidden bit initialized uniformly; action 0 holds it and action
1 flips it; independent disturbance probability 0.07 and sensor noise 0.18.
The public learner receives observation bits and actions, not hidden states,
transition values or generator labels.

Null world: publicly observed iid fair bits with no causal signal.

For each of five seeds per world, 128 training episodes each have 12 actions,
and **no training episode contains 111**. Each independent evaluation has six
public prefix steps followed by the untrained action string **11111**. The
model predicts five future observations **open loop** without reading the
future outcomes. There are 1,536 training transitions per seed/world and
96 five-step evaluation suffixes.

Controls receive identical public training trajectories. The principal
trained HMM has **432** candidate model configurations versus **36** for
CCE-04, and is selected via training likelihood and the same null penalty.
The other controls are an action-independent fitted two-state HMM, a
trained two-observation suffix memory, and a constant 0.5 predictor.
A source-parameter oracle appears only as a noncompetitive reference.

## Frozen results

| Five-step heldout observation Brier, average across positive seeds | Value |
|---|---:|
| CCE-04 coarse causal-belief contracts | **0.225975647999** |
| **Fine-grid fully trained HMM** | **0.224026646694** |
| Trained observation-suffix memory | 0.235015573448 |
| Trained action-ignorant HMM | 0.250000000000 |
| IID baseline | 0.250000000000 |
| Source-parameter oracle (noneligible upper bound) | 0.224037248848 |

CCE-04 is **0.001949 Brier WORSE** than the strongest trained HMM; the frozen
development requirement was at least **0.010 Brier better**. It did not pass.

Additional findings:
- The correct action-causal-effect family (hold on 0; flip on 1) was selected
  in **5/5** positive-world seeds.
- The iid null model was selected in **5/5** null-world seeds.
- Cold snapshot predictions and content were identical in **5/5** positive
  seeds.
- The CCE candidate used **36** scored hypotheses versus **432** for the fine
  HMM, but this is not a compute-matched efficiency win. Fine-grid likelihood
  training had more work, and no native hardware or deployment benefit is
  established.
- CCE checkpoint bytes: **215–218 positive**, **204–205 null**; these omit
  full model source and the shared pre-specified hypothesis definitions.

All individual seeds, training times, selected parameters and controls are in
`result.json`. Negative results are retained without retuning.

## Engineering qualification

The eight isolated engineering unit tests in `test_cce04.py` **PASS** on
CPython 3.13.5 Linux, including invalid public histories, action-dependent
predictions, real training-budget enforcement, selected causal-action family,
cold recovery, tampered checkpoint and recomputed forged-evidence rejection.

```powershell
python -B -m unittest discover -s research/contrib/chatgpt/y2-cce04 -p test_cce04.py -v
```

Original primary execution (consumed once, recorded for audit; not an
instruction to replay or change the established result):

```powershell
python -B research/contrib/chatgpt/y2-cce04/run_cce04.py --output research/contrib/chatgpt/y2-cce04/result.json
```

The G29 generated source atlas remains a **separate Windows/Linux CI
qualification blocker**. The existing checker sees a changed indexed file set.
No generated .ice file was manually edited, no checker bypass attempted, and
no workflow/runner/controller dispatched. Full candidate regression, original
native scientific first-use, independent reproduction and deployment remain
**UNVERIFIED / NOT PERFORMED**.

## The actual lesson and next falsification

A compact coarse hypothesis set successfully recognized an action-sensitive
latent state and rejected spurious action dependence, but a conventional
higher-resolution HMM slightly outperformed it on the unseen action sequence.
The result does not establish emergent cognition or transfer across task
families. We should **not** keep adding fixed hypothesis templates and call
it a new intelligence architecture.

A more discriminating CCE-05 should ask whether the learner can **invent
needed latent variables and reusable causal mechanisms**, with no fixed
two-state structure or known effect-family library. Compare with fully trained
variable-order HMMs, factored dynamic Bayes models and predictive-state
representations at matched public information, computation and memory. Add
interference and cold reuse across changed environments. Freeze an entirely
new experiment protocol before any new original result.

**Status: development MIXED, scientific NO GAIN, G29 CI FAIL, deployment NONE.**
