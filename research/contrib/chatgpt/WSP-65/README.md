# WSP-65 — Inferring a hidden mode from action history

## Preregistration and source custody
- Frozen protocol committed **before new source/learner, tests or outcomes**: `aa94845f88c028630a5a34b004b00a05b5efaa1f` (`prereg.json`).
- Parent [WSP64 draft PR #955](https://github.com/spoonman136668-ai/Yggdrasil/pull/955), exact SHA `d847dfc5364622ee92a61863cbe04ec0c5584efc`. WSP64 failed its prospective criterion (111/256 Markov goals, 62 correct unseen, 8 wrong confident on two-mode audit); source and negative result remain immutable. Its mandatory inherited full regression had not completed at this branch point.
- Twelve new source-seed worlds 3101–3112 with a separate WSP65 SHA256 source domain. Six have three visible binary sensors, six four. All have one completely invisible binary mode, four unknown shuffled action channels and shuffled observable sensor roles. This is a finite synthetic source family, **not** independent open-world physics.

## The new hypothesis
- One unknown physical action toggles a hidden binary mode without changing visible sensors. Another action changes a visible sensor depending on that mode. Consequently the current sensor state alone is not enough to predict consequences; full action history may reveal the hidden cause.
- The **source-blind** learner enumerates four candidate mode-toggle channels and one no-mode candidate. For each hypothesis it reconstructs mode parity from the observed *public action history* and constructs all evidence-consistent degree<=2 Boolean numerical laws with at most three nonzero terms over visible bits plus candidate mode.
- It eliminates candidate mode assignments contradicted by public evidence, retaining **all** remaining numerical rules. It predicts only when all surviving models agree; otherwise abstains. All numerical causal knowledge is built without gradient training or autoregressive next-token objectives.
- This is a **strong prewired single-bit parity prior**, aligned with the source by construction. No discovery of arbitrary latent memory dimensionality, natural language understanding, unrestricted representation grammar, or general intelligence is claimed.

## Training and heldout evidence
- Each arm gets **128 charged chronological physical actions** from a single all-visible-zero, hidden-zero initial state; there are no arbitrary-state training queries, free resets, hidden simulator imports or withheld test feedback. The active policy chooses from public state/action-coverage, with occasional deliberate repeated-state actions to uncover ambiguous transitions. Seeded random training action policy uses the same 128 charges for a diagnostic arm.
- **Heldout evaluation** creates 64 *independent, newly sampled* 8–16-step physically replayed public-action-history episodes per world; all models get the same visible consequences along those test prefixes as context, but NONE may add them to persistent learning or refit after seeing them. Source reset is used **only at standardized test-episode start** and is not a no-reset training exception.
- The evaluator privately chooses the final action channel that depends on the hidden mode to make every task a meaningful latent-state prediction. All controls see the resulting public action ID. The labels and private mode are withheld from the learner and used only to audit predictions.
- Freeze **768** new-history next-physical-consequence queries, 64 per world; count correct, abstain, confidently wrong. Public evaluation-prefix steps are charged and reported separately from training. Full heldout action histories are disjoint from the training prefix, and each source/test/ledger SHA256 is retained.

## Controls, including stronger independent symbolic mechanism
- **Visible-only** same-ledger state/action lookup, abstaining when the same observed pair produced contradictory outcomes.
- **Short-history** same-ledger lookup keyed by visible state, previous two public actions and queried action, with contradiction abstention.
- **Independent latent-state empirical automaton** (`independent_automaton.py`): independently enumerates candidate hidden-toggle actions, but memorizes next observations keyed by visible state, candidate mode parity and action. It shares the *single-bit parity prior* but **does not** use the WSP65 polynomial learner. Added as a stronger diagnostic before any test result; the frozen primary criterion does not depend on outperforming it.
- **History scramble** diagnostic deliberately changes public action IDs in the otherwise identical test prefixes, breaking their physically correct parity. Plus identical-algorithm, equal-charge random-trajectory control.

## Frozen primary threshold and guardrails
- Exploratory `SELFTEST_SIGNAL` requires >=576/768 correct candidate consequences, >=154 more than visible-only, >=77 more than the two-action suffix lookup, **zero confidently wrong**, visible-state/action contradictions actually observed in >=8/12 original training streams, all 128 charged actions per arm/world and exact cold memory/source parity with tamper rejection.
- Otherwise the result stays `SELFTEST_NEGATIVE_OR_INCONCLUSIVE`; no retuning source seeds, mode dynamics, action budgets, thresholds or candidate basis in response to outcomes.
- Report all candidate latent toggle counts, independent symbolic automaton baseline, source and action custody, total public evaluation-context steps, stored bits, all-world CPU/wall and active-selection time. **Equal charged training actions do not mean equal whole-process computation.**

## Scientific limitations
Test episodes supply complete observable action history; the learner is not forced to infer hidden state from a single current observation. The environment starts every *evaluation episode* in the known zero-mode condition, and mode transition is an unknown **one-channel parity toggle** by prior. This is far simpler than noisy, multi-latent open-world POMDP learning, independent general intelligence, language acquisition or permanent autonomous learning. No independently fully trained strong neural belief-state baseline with matched total information/compute has been qualified. Even exploratory success is not `SCIENTIFIC_PASS` or deployment authority.

## Reproduce
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-65 -p 'test_*.py' -v
```

Only existing Linux/Windows SELFTEST CI, exact-source G29, and mandatory inherited full regression qualify the final tree. No protected DEV/PRIMARY scientific first-use, merge, official autonomous-loop integration, controller/runner changes, deployment, paid API or scheduled task.
