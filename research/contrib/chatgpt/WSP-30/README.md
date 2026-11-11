# WSP-30 — composition-limit diagnosis: DIAGNOSTIC_SUPPORTED

Missing source information dominates the **information-limited** part of the
frozen composition task. Of 1,088 ambiguous heldout answers under the original
evidence, revealing full source information raises the evidence-group upper
bound by **1,020**, leaving **68** ambiguous about the connection. That is 93.75%
versus 6.25% of the ambiguity component, meeting the frozen dominance threshold.

**No learner improved in this experiment.** The unchanged native model still
scores **4,000/5,760**, with 8,760/9,600 observed target labels correct. All other
numbers below are evaluator-only counterfactuals or information bounds. They
must not be reported as acquired skills, allowed training results or deployment.

| Evidence-group bound | Correct upper bound /5,760 |
|---|---:|
| Original source evidence and five actual target labels | 4,672 |
| Complete true source information plus same target labels | 5,692 |
| All heldout labels, unconstrained diagnostic ideal | 5,760 |

The exact partition of original **evidence-group uncertainty** is
1,088 = 1,020 source-information value + 68 remaining connection ambiguity.
The actual learner also falls **672** below the original 4,672 bound. That gap
can include routing policy, representation, imperfect acquisition and priors;
this experiment does not assign a unique cause to every one of those errors.
The information-only bounds do not guarantee the fixed six-NAND source graphs
can represent all revealed knowledge or that a learning rule can attain them.

## Separate counterfactual diagnostics

| Diagnostic condition | Observed correct /9,600 | Heldout correct /5,760 | Native-correct observed points sacrificed |
|---|---:|---:|---:|
| Actual unchanged learned model | 8,760 | 4,000 | 0 |
| Hidden-answer oracle choosing among equally fitting actual-bank routes | 8,760 | 4,451 | 86 |
| Hidden-answer oracle choosing any actual-bank route | 8,083 | 5,102 | 833 |
| Perfect true source tables, original five-example first-tie rule | 9,600 | 5,080 | 0 |
| Perfect sources plus hidden-answer tie oracle | 9,600 | 5,760 | 0 |

These rows are **not an additive decomposition** of native error. The two learned-
bank oracles use heldout answers for selection and can sacrifice earlier correct
observed points, even when total observed accuracy is unchanged. They cannot be
substituted for real learning or safe local repair. The perfect-source condition
also changes implementation capacity: arbitrary eight-output truth tables may
not fit the original six-NAND module architecture. Its gain is not a pure effect
of one achievable weight update. The original first-tie rule becomes worse in
**138 worlds** under that source substitution; complete source information does
not make every fixed selector monotone.

The true recipe is in the supplied 12-routing language by construction. Therefore
the full perfect-source oracle's 5,760 is a structural control, not proof of a
new composition capability. No true tables, oracle route indices or heldout labels
are supplied to Composition.learn or saved as learned candidate checkpoints.

## Exact reuse and independent checks

The cohort is byte-identical to WSP29: all 120 acquired module checkpoints,
including 13 imperfect modules; 60 pairs x 16 completions x two recipes = 1,920
public correlated worlds. The original 707/720 source fit is unchanged. All
1,920 native routes, predictions and checkpoint hashes reproduce exactly. All
1,920 cold restores, bank-byte checks and 30,720 base predictions are preserved.
All 5,760 cached learned response entries are checked against the generic circuit.

The original bound 4,672 is independently reproduced. The refined bound is
computed twice: per-output majority counting and separate enumeration of all
eight possible three-output predictions for every evidence group. Refinement
only adds complete source information and cannot lower the bound. Tests include
small hand-checkable source/connection ambiguity cases, oracle training-fit
tradeoffs, corrupted source hashes and duplicate/truncated/malformed traces.

The 5,880 converged WSP29 conventional fits and their exact score receipts are
reused from their immutable qualified result, source and data. **No new gradient
fit or source adaptation is claimed or executed.** This diagnostic does not alter
the prior comparison, its negative five-point hypothesis or its trained baselines.
Mandatory prior unit/interface/fit checks still rerun in the final regression.

## Freeze, cost and reproduction

Remote preregistration preceded implementation and the first diagnostic outcome.
The exact prereg/implementation/result identities and all input source hashes are
in `provenance.json`. Full per-world counterfactual choices/fit tradeoffs are in
`result.json`, explicitly as evaluator evidence. No prior source or result changes.
The first complete local diagnostic took about **7.18 seconds**; it reuses qualified
module acquisition instead of repeating upstream training. That is a diagnostic
runtime, not a faster end-to-end learning result. Current learner capacity and
state are unchanged; no efficiency, energy or independent scientific superiority
claim is made.

Reproduce: `python research/contrib/chatgpt/WSP-30/run_dev.py`.
Full final qualification: `python research/contrib/chatgpt/WSP-30/qualify.py` —
all original and WSP01–17/WSP19–30 unit suites, full frozen diagnostic, G29 and clean
source at one exact final SHA/tree on hosted Ubuntu and Windows. Receipts are on
the draft PR. Existing workflow reused; no new workflow, private runner,
owner/controller/queue/scheduler, merge, accepted state, integration or deployment.

## Next research implication

The next learning experiment should test **acquiring missing source facts under
a fixed actual-query budget**, with a matched connection-feedback control and
retention checks. It must also test how the new facts are represented, rather
than assuming perfect truth-table substitutions are attainable in the old graph.
The 672 selection/representation gap and residual connection ambiguity remain.
No successor protocol or run has started here; complete learning remains unproven.
