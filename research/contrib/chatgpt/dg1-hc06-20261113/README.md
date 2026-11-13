# DG1-HC06 — Independent Bayesian active-learning challenge

This *qualification/falsification* gate holds the HC05 Gini-based two-step
intervention mechanism **unchanged** and tests it against an independently
implemented conventional Bayesian Shannon-entropy two-step planner.

**Preregistration:** `7aea3eed4f2091d6d4e78f1e82862b456092fec7`
committed before this evaluator, baseline and tests.
**Frozen parent:** `3fa5b59208b250df14b0775d3134fd187dfc540b`,
the engineering-qualified HC05 draft #966.
**Known prior failure:** HC05 MIXED_DEV with 38 confidently wrong predictions
in the majority-of-three-bit out-of-family cohort. All earlier results remain
untouched.

## Exactly what is being compared

The unconventional candidate retains the source-frozen `CausalProbeCells`
from HC05: 24 logical hypothesis-mask bits over four public actions and
six fixed Boolean models per action. It selects interventions with two-step
expectimax of **Gini disagreement**. The comparator, independently
implemented in `bayesian_control.py`, uses an exact uniform posterior over
the same six deterministic hypotheses and a two-step **Shannon entropy**
lookahead instead. The independent comparator does *not* subclass or import
HC05. Both observe only public action consequences, never hidden physics,
source labels, evaluator predictions or phase indicators.

Each receives exactly the same **number** of real actions from the
same initial state; action ledgers may naturally differ due to policy. Neither
receives a free training query or reset. A greedy HC05 planner, cyclic
action policy and seeded random policy provide additional action-matched
controls. Planning CPU costs are *not matched* merely by action equality.
This limits the interpretation of efficiency claims.

## Frozen prospective sources

* 8 new same-family worlds (seeds 41001–41008), 12 charged actions/arm.
* 8 **rewired-neighbor causal graphs** (41009–41016): learner assumes fixed
  original left/right dependencies, while real physics uses alternate
  neighbors. A structural transfer/OOD falsification.
* 8 majority-of-three-site sources (41017–41024), another independent
  negative family outside the fixed candidate grammar.
* 8 A→B→A phase-switching worlds (41025–41032), 16 + 8 + 1 = **25 physically
  charged** actions per arm without environment reset or regime labels.
  Tests forgetting and return-to-A rule retrieval, not just one-step fit.

A private-to-evaluator law generator picks a per-action base family and sign
using frozen independent Python random seeds. After real training is complete,
the evaluator scores 16 public states × four actions as an uncharged **audit
only**, never fed back to the learner. Results include exact correct,
confidently wrong, abstained, and specifically unseen state/action categories.
All uncharged audit queries occur only after the final action.

## Prespecified decision rules

* **Same-family main:** zero confidently wrong and at least **+4 correct/64
  per seed on average** beyond independent Bayesian entropy over all eight.
* **Rewired transfer:** zero confidently wrong and at least 256/512 correct.
* **A→B→A retention:** zero confidently wrong and at least 256/512 correct.
* **Majority negatives:** any confident wrong predictions preserved as
  out-of-basis failure; even zero in this finite cohort is no safety proof.

If some gates pass and others do not: MIXED_DEV. If none pass: NEGATIVE_DEV.
No outcome in this source-only study constitutes SCIENTIFIC_PASS.

## Runtime, provenance and isolation

Run in the research repository checkout:

```bash
python -m unittest discover -s research/contrib/chatgpt/dg1-hc06-20261113 -p "test_*.py" -v
python research/contrib/chatgpt/dg1-hc06-20261113/eval_dev.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

Both Linux and Windows must qualify against the final candidate's exact
SHA/tree and an exact pinned G29 atlas. Complete raw evidence, cross-platform
per-world hashes, action counts and CPU timings are retained. A passing
engineering regression is *not* learning superiority, original-world science,
or license to integrate into Yggdrasil's accepted model.

No native model source edit, no owner runner/controller change, no CKB-plane
authority, no scheduler, paid API, protected scientific first-use, unapproved
merge or WSP weight-editing ref mutation.
