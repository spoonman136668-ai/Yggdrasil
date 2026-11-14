# WSP81 — hidden-state falsification outside WSP80's visible Markov assumption

**Scope:** isolated unregistered developer-only exploration of a one-bit latent
regime. All evidence, tests, CI logs, receipts and outcomes remain in GitHub.

The original WSP80 candidate PR #982 stays draft, unmerged. Its registered
16-world SELFTEST seeds (5601–5616) and scientific source-custody authority
remain untouched.

## Prospective freeze and claim boundary

\`prereg.json\` was committed FIRST at
\`a3782028045759994a5a3c3de3765a1d939ed6e3\`
(Git blob \`954041015a52a3cc215964511be04abebec114fd\`), before
source, model code, tests, outcomes or hidden parameters were generated.

This environment is **genuinely outside the WSP80 public Markov assumption**:
the same public state/action pair may have a different result depending on an
unobserved regime driven by earlier actions. The learner sees only charged,
ordered public observations, never regime labels.

This is **not completely open-ended model discovery**. The new learner searches
an expressly predefined 31-member two-state hypothesis class: one Markov
control plus trigger/action-offset hypotheses. The strong independent symbolic
comparator has the same hypothesis class, so a predictive tie is expected and
must not be called a neural or AGI advantage.

## Components

- \`source.py\`: separate evaluator-private hidden-state source, six
  predeclared unregistered seeds 9401–9406, no paid reset, 384 one-unit actions.
- \`history_weights.py\`: source-blind charged-history learner that compiles
  selected models to numeric ReLU outputs and mode-transition weights. Cold
  inference uses only restored numbers and public action history; a disagreeing
  hypothesis ensemble abstains rather than inventing certainty.
- \`independent_control.py\`: independent, separately implemented finite
  symbolic state-machine control, trained on identical public observations.
- \`experiment.py\`: frozen source admission; exact budget; original WSP80
  deterministic Markov editor failure check; memoryless, paid lookup, independent
  symbolic, numerical and genuine three-restart conventional Adam controls.
  It freezes ALL 768 context-conditioned public predictions/model/world before
  evaluator-private truth and computes correct/wrong/abstain/unpaid metrics.
- \`test_history_dev.py\`: synthetic non-cohort unit fixtures, cold restoration,
  parity, paid-ledger negative controls, snapshot corruption, and no-source
  import checks.
- Workflows: pinned two-OS development engineering tests and explicit one-shot
  six-world unregistered-only comparison.

## Limits and scientific decision

Development thresholds are frozen in \`prereg.json\`. A failed threshold is
recorded as a negative; source, conditions, thresholds and seeds are not changed
after first run. Memoryless Adam is **not** a matched-capacity recurrent neural
control. An independent symbolic model *is* same-expressivity, and any tie
precludes a neural-intelligence superiority claim. Counterfactual evaluator
query states may be unreachable for their supplied history, so causal
competence on naturally occurring trajectories is still unverified.

Only a registered, independently admitted and appropriately controlled future
experiment could justify a scientific gain. No merge/promotion/automation/
runtime/controller/first-use permission is implied.
