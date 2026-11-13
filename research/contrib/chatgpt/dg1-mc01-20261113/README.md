# DG1-MC01 — local causal-motif substrate development probe

## Scope and isolation

This is an **opt-in developmental prototype**, not the original native runtime, official model replacement, an autonomous controller, an accepted experimental result, or a weight-programming continuation. Parent is Yggdrasil main at \`5e74f8db85b2f5839c42148c0dfba69a88b1a2c9\`. WSP63 PR #954 remains independent. No changes to FORGE, Mind-Palace, Wingless, ckb-plane, or the WSP program.

Frozen preregistration commit: \`340d54de415160aae962d2ce7d47c57c5bc85cbc\`, *before* learner code and evaluator were added.

## Question

Can four locally trained developmental-effect cells learn action-conditioned physical changes from only chronological public consequences, and then compose transitions on unseen global states? The learner knows the four-site ring topology and a fixed left/right feature map. It does **not** discover geometry, state variables, the hidden gate laws, or a general-purpose causal representation. The action channel identifies the public site being acted on; the learner only sees public before/action/after records.

## Experiment

- Four functional sites within seven possible active and nine reserved retained cells.
- Four online logistic coefficients per active cell; fixed global ceiling of 28 coefficients/224 logical bytes, with versioned SHA-256 checkpoint and 64 source-action hard cap.
- In-family worlds: locally triggered state-bit changes using hidden left/right rules.
- Explicit out-of-family negative: effects depend on the selected site's own bit, outside the model's representational prior.
- 64 chronological source steps per world. Evaluation uses never-observed state/action pairs and fixed two-action rollout composition. The evaluator may inspect hidden laws; the learner may not.
- Controls: identical trained model with neighbor features absent, always no-change, exact public-transition lookup (zero coverage on previously unobserved pairs), and post-training no-neighbor ablation. No tuned threshold or training restart is permitted after results.

Source-only focused tests:

\`\`\`sh
python -m unittest discover -s tests -p "test_local_causal_motif_dev.py" -v
\`\`\`

Frozen synthetic development diagnostic:

\`\`\`sh
python research/contrib/chatgpt/dg1-mc01-20261113/dev_eval.py
\`\`\`

The second command is DEV/SELFTEST only, not an authorized sealed scientific first use. Preserve negative outcomes. This work still needs exactly pinned cross-platform source qualification, G29 atlas where applicable, inherited full regression, and independent scientifically strong recurrent/symbolic controls before any protected trial.

## Interpretation

Even a favorable result would establish only bounded local-feature generalization in a deliberately structured toy world. It would **not** establish learned topology, autonomous representation discovery, repair, cumulative language learning, AGI, or a win over a trained conventional world model. Future genuine substrate work must add (a) learned representation construction, (b) retention across sequential worlds within the fixed resource budget, (c) causal ablations and actual unfamiliar-world transfer, and (d) authentic source custody.

No owner-loop, runner, scheduler, science acceptance, merge, promotion, deployment, paid API or live environment is triggered by this document.
