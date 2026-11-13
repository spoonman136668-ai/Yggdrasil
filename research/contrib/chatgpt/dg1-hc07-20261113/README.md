# DG1-HC07 — Learning an unknown causal dependency graph with no gradient

**Purpose.** Test a bounded executable causal-graph learner against an
independently coded conventional Bayesian graph learner and an unchanged
fixed-ring HC05 baseline. This is source-only experimental evidence, not
native Yggdrasil adoption.

**Preimplementation preregistration:** `71add4127f4e566344d136439f6afda7668183fe`.
**Exact predecessor source:** draft HC06 `3619bf342a4cc41890ac797208683e030ae6c6fa`.
The prior HC06 negative structural-transfer and majority observations remain
frozen. The native `main`, weight programming and owner loops are unchanged.

## Mechanism

An unknown physical action flips its own addressed bit according to a causal
program `effect = parity(state_bits & unknown_parent_mask) XOR unknown_sign`.
The HC07 candidate begins with **all 32 possible programs per action**, stored
as 4 bounded version-space masks (128 logical bits). Real before/action/after
observations eliminate impossible programs. A public next-state prediction is
only returned when **all** remaining programs agree; otherwise the model
abstains. With no viable program it abstains and records contradictions.

The unconventional architectural question is whether physically grounded
executable rule programs are a useful non-token substrate for discovering
*previously unknown causal edges*, rather than requiring the graph to be fixed
in the model. The program grammar (affine binary functions) and four exposed
state variables are nevertheless human-specified. The system does not
discover new senses, continuous world states, or universal program syntax.

## Prospective falsification

Four disjoint cohorts, eight seeds each, frozen in `prereg.json`:

* **Rewired graphs 51001–51008:** true action effects depend on unfamiliar
  public dependencies. 32 real physical actions per policy/world. Primary
  candidate criterion: **zero confident errors, ≥32/64 correct for every
  seed, and aggregate ≥128/512 more correct than fixed HC05**.
* **Old-ring 51009–51016:** original ring graph, potentially extra
  own-bit dependence. Same budget; candidate correct ≥256/512 and zero
  confident errors required.
* **Non-affine 51017–51024:** three-input majority, outside candidate affine
  hypothesis class. Confident errors count as a substantive failure.
* **Rewired A→B→A 51025–51032:** 16 A, 8 B, 1 return A public actions
  physically contiguous; no labels. Candidate must have zero confident
  errors and ≥256/512 correct for this limited DEV threshold.

Independent conventional Bayesian control is **separately implemented**
in `bayesian_graph_control.py`, without importing the candidate. It
maintains the same 32 rule hypotheses/action and uniform posterior; next
action maximizes Shannon entropy. The candidate maximizes Gini disagreement.
The two policies receive matched causal prior capacity, **identical real
action allowances**, and identical initial states. Trajectories can diverge
by intervention choices. They are not guaranteed equal CPU complexity.

Other controls: unchanged smaller-capacity HC05 fixed-ring active learner,
and same HC07 representation paired with cyclic physical actions.
These can illuminate mechanism but do not establish superiority over a
same-capacity conventional graph learner.

The evaluator alone knows the true graph, signs and phase. After *all* real
actions, it audits exact 16 state ×4 action next-state transitions. This
held-out audit does **not** update any learner. Counters report correct,
confidently wrong, abstained, and first-time state/action subsets. Actual
checkpoint bytes, Python peak allocated bytes, source-action ledgers and
policy timings are retained separately from logical bit counts.

### Reproduction

From the checked-out branch:

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-hc07-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-hc07-20261113/eval_dev.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

Every branch change requires exact-source G29 atlas pinning and final
Linux+Windows qualification. **Engineering PASS is not SCIENTIFIC_PASS**;
a synthetic source-aligned experiment and fixed Boolean grammar cannot prove
general intelligence, natural-world transfer or better efficiency than
conventional Bayesian graph discovery. All negative results are preserved,
not retuned or merged into the official owner loop.
