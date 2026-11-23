# Yggdrasil 2.0 / CCE-03: compositional causal-delta contracts

**Research-only; standalone successor hypothesis, not native Yggdrasil admission.**

- Existing draft PR: #1367.
- Parent before CCE03: `44938e86e8e18ff2fc52b999b809a3c1cf008a0e`
- Preregistration committed *before implementation and result*: `a5075e14068ace2d1e7de1b0b9b644ea3cf84a40`
- Frozen code/test/evaluator commit *before primary result*: `05828736cfa48c75f0b80194671a2ba6a81b927f`
- Source tree for the code candidate: `5006143b4cce30e2de6688d6cd5f9e58da50ba97`
- All five independent positive and null seeds are in `result.json`; the result is marked `MIXED`.

## Tested mechanism

A fixed ecology of 18 independently updating action/target-bit cells observes only public
`state, action, next_state` transitions. Every cell maintains 16 competing hypotheses
about whether none, one or two *other* input bits determine the observed flip of its
target bit. It updates Beta-Bernoulli counts without gradients, tokens, an identity
oracle or a privileged map of the source world's relationships.

After 768 one-step training events, each cell selects an evidence-supported
parent set using a frozen penalty on prequential Brier loss. At evaluation, its
predictions are composed to predict two consecutive actions, even though it
was never explicitly trained on two-step trajectories.

This is **not** autonomous discovery of objects, state variables or action types.
Input bits and action IDs are given; local causal dependencies are inferred
under randomized interventions on synthetic source worlds. The candidate
expends substantially more training compute and memory than simple baselines.

## Original frozen result

| Positive-world metric | Mean over five seeds |
|---|---:|
| CCE03 two-step exact six-bit final state | **100.00%** |
| Full-state/action trained Beta tabular control | **96.875%** |
| Selected one-parent local control | 46.667% |
| Pooled action-conditioned control | 40.781% |
| Improvement over **strongest** trained comparator | **3.125 percentage points** |
| Preregistered improvement required for development signal | **10 percentage points** |
| Null seeds with zero unnecessary parent selections | **5/5** |
| Exact cold restoration of all 64x3 one-step predictions | **5/5** |
| Learned parent-bearing action/target slots | 5 of 18 |
| Candidate cold payload per positive seed | 43,060–43,258 bytes |
| Final classification | **MIXED / not SCIENTIFIC_PASS** |

There are no hidden evaluation labels used for training. Both control models
consume exactly the same 768 one-step transitions; full-state memorization
remains an especially strong comparator (96.875%). The candidate's exact
compositional behavior does **not** meet the preregistered gain threshold;
this outcome is preserved without changing models, seeds or thresholds.

## Engineering and evidence boundaries

- Local engineering unit fixtures: **9/9 PASS**, including positive XOR parent
  discovery, zero-effect controls, selected-parent audit, checkpoint recovery,
  malformed public event rejection, event budget, and forged record rejection.
- Primary DEV synthetic evaluation executed exactly once after committing the
  full code, tests, evaluator and preregistration; no native scientific first-use.
- Original local primary output SHA256 is pinned in `provenance.json`.
  `result.json` is a field-preserving normalized JSON recording of the primary
  output, **not a byte-identical copy**; no new run was performed to create it.
- No independent matched scientific reproduction, full repository regression,
  Windows qualification, accepted code path or measured AGI progress.
- Existing G29 code-atlas CI is **FAIL** because research files change its indexed
  source set. Do not bypass the validator, edit generated `.ice` manually, start a
  new workflow/controller, or treat local tests as acceptance.

## Reproduction (unit tests only)

```powershell
python -B -m unittest discover -s research/contrib/chatgpt/y2-cce03 -p test_cce03.py -v
```

The original frozen benchmark command is recorded for audit (already consumed;
do not rerun it as a new primary result):

```powershell
python -B research/contrib/chatgpt/y2-cce03/run_cce03.py --output research/contrib/chatgpt/y2-cce03/result.json
```

## What should come next?

CCE04 should move beyond these fully observed, stationary six-bit systems:
latent state, changed causal contexts, delayed interventions, genuine novel
compositions, and stronger trained context-sensitive HMM/POMDP and sparse
factored-DBN controls. Freeze separate thresholds and input provenance before
an original first-use trial. No promise of a positive scientific outcome.

**No merge, deploy, accepted ref mutation, runner dispatch or checkpoint promotion.**
