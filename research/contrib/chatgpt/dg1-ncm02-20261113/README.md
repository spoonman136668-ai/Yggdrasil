# DG1-NCM02 — native public causal-cell consolidation

This is an isolated, **opt-in source candidate** based on Yggdrasil `main` at
`5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Its frozen preregistration
preceded implementation at `beb77b929eb4fc3cfa72f7f334255bd20919741f`.

## What it actually changes

`PublicCausalCells.consolidate_and_recycle(active_address, retained_address)`
copies the already-observed two-action binary outcome counters from one active
slot to a previously empty retained slot, then zeros the active slot. Both
action arms require real public evidence. Occupied retained slots, invalid
addresses, and incomplete source evidence are rejected without mutation.
All other slots retain their exact counts.

The default `observe`, `choose`, `choose_wilson`, `snapshot` and
`restore` interfaces remain unchanged. The 7-active/9-retained memory budget,
128 learned bytes, and 164-byte SHA256-authenticated checkpoint remain fixed.
Retained slots are not cryptographically immutable: existing `observe(...,
retained=True)` can still update them, so callers must separately enforce
lifecycle custody.

## Frozen development controls

1. Train the native cell from public action/outcome examples until action 0
   is preferred; archive to unused retained slot 0, recycle active slot 0.
2. Train contradictory examples into that now-free active slot until action 1
   becomes preferred. Require retained action 0 to remain unchanged, including
   after cold restore.
3. Compare against unchanged original reusing only the active slot, which
   demonstrably suffers interference in this *constructed* source-only case.
4. Check occupied-retained and underobserved-source rejection without mutation,
   invalid types/addresses, every retained slot, independent unrelated slots,
   existing checkpoints and corruption rejection.
5. An equal-capacity control that explicitly writes public evidence into
   retained slots can implement equivalent memory retention. Thus success
   **cannot** establish superiority over conventional memory or scientific
   generalization. A positive result is a useful bounded native API, not AGI.

## Reproduction and acceptance

Run from the exact checkout root:

```sh
python -m unittest discover -s tests -p 'test_native*.py' -v
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

The first command is narrow development; the others must pass unchanged on
Linux and Windows before an engineering promotion recommendation. Because
new source paths change the repository's G29 code atlas, exact-SHA atlas
regeneration and the final regression are mandatory. Until then:
**ENGINEERING UNQUALIFIED / SCIENCE UNVERIFIED / NO MERGE**.

No original-world training, new/paid model calls, hidden-world access,
controller/runner/scheduling changes, accepted ref mutation, production
deployment or edits to the WSP weight-editing research. Prior DG1-MC01's
INVALID_DEV is unchanged. This program targets *continual retained memory*
rather than a new causal-generalization claim.
