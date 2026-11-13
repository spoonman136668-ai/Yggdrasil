# WSP-56 — Out-of-family physical-rule construction (SELFTEST only)

## Source custody and isolation
- Pre-registered before the new source or model was committed: `b6e1e99528bd8741033317e606aa8a7588a29304` (`prereg.json`).
- Exact parent: Yggdrasil WSP55 PR #946 at `a86ce905c31d4e68164a4ba799a7ae47bc68c87b`.
- New evaluator-only `source.py`: independently sampled, nonlinear and non-affine derangement permutations of seven physical states, four operators and eight addressable registers. No WSP53 fixture functions are imported.
- `table_writer.py` sees **only** charged before/raw-bits/after observations. It never imports source.py, oracle codebooks, hidden semantics or grammar labels.
- The **declared prior** is considerably easier in one respect: twelve 4-bit fixed-width codewords and 28 identifying unary interventions. No claim is made that it solves unsegmented natural language.

## Frozen engineering protocol
- Six SELFTEST fixtures = two seeds × three encodings, 28 unary + 20 A composition + 12 B composition actions each, followed by independent withheld composition challenges.
- Each world has 96 A and 96 B heldout challenges; aggregate 1,152. No DEV or PRIMARY first use.
- Discover four 7-entry operator tables and latent word roles from physical consequences; infer a new grammar from a longest evidence-consistent recent suffix, not a phase selector.
- Charge actions and persistent evidence, count correct/wrong/abstain and physically distinguishable order-swap contrasts; cold restore before and after the grammar shift.
- Compare against exact observation lookup and best-fitting modular-affine projection using the candidate's learned roles, explicitly **not** a fully trained neural or independent symbolic baseline.

## Prospective success and limitations
- SELFTEST_SIGNAL: ≥768/1,152 exact, zero wrong-confident, ≥24 correct order-swap contrasts, with all six fixtures and cold restore valid. Otherwise preserve the negative/indeterminate outcome.
- Non-affine source generation means this challenges WSP55's affine law family, but it remains a synthetic finite-world task with an identifying unary intervention advantage.
- This result, even if positive, cannot establish external physics, general language learning, scientific superiority, or general intelligence. Strong independently trained neural and exhaustive symbolic matched baselines remain necessary.
- No merge, acceptance/promotion, deployment, paid API, scheduled task, or autonomous-loop integration.

## Local focused reproduction
```sh
python -m unittest discover -s research/contrib/chatgpt/WSP-56 -p 'test_*.py' -v
```

GitHub Actions runs the same frozen SELFTEST on Ubuntu and Windows; inherited full regression and exact-source G29 atlas are separately required for engineering qualification.
