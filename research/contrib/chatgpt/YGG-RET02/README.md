# YGG-RET02 — Temporal causal-context readout (opt-in, source-only)

**Status:** engineering candidate only. **No new native scientific result.**
The original [RET01 PR #1285](https://github.com/spoonman136668-ai/Yggdrasil/pull/1285)
at `f3b906c03730f7f3efb64683d77e00ba631dd409` remains frozen with
`DEVELOPMENT_NO_GO`; accepted `main` remains unchanged.

Frozen source-only contract committed **before any code** at
`a8face01c23fcc661ba59cb192fdca97dc2dc411`.

## What is implemented

`yggdrasil/native_temporal_context.py` exposes
`NativeTemporalContextReadout`, a small **opt-in readout** over the
**same existing trained, cumulative Yggdrasil native+six-head model**
and its immutable original archived reader. It never creates a new native
learner, source controller, world simulation or external actor.

The new 17-number causal-context feature consists of current public views
and commanded action bits, previous TWO actually admitted and witnessed
public action/state/consequence/reward quadruplets, and two
**current-target-independent** source-model forecast differences. No
evaluator phase, private regime, source seed, current truth s2/y or hidden
environment state is a feature. The second-step feature difference is
computed using a neutral `s2=0` hypothesis, not the actual observed
`s2`. The original RET01 comparison forecasts, however, do condition
their second-step reward prediction on the observed current `s2`; this
inherited evaluation-design issue must be corrected or explicitly
time-scoped before any prospective scientific scoring.

One online 17-float readout starts from archive probability 1/8. After
the existing native model *actually accepts* a novel public source
action/consequence witness, the readout takes **one** bounded online
Brier-gradient update toward the observed two public outcomes. Its
persistent causal context is therefore a small learned temporal numeric
readout over witnessed history, **not** a static current-view lookup or
rank-credit proxy. Original native memory, prior ledger and specialist
weights are never overwritten or reset; an entirely new feature cannot
issue a source action or override Yggdrasil's intervention planner.

The source identifier is a deterministic hash; that alone is NOT
independent source-owner authentication. Duplicate observation is
idempotent, conflicted original history is rejected, total development
witnesses are capped at 64, and a cold restore independently replays every
newly observed public event through the original native learner and
readout, requiring matching original checkpoint and learned readout
weights byte-for-byte. `forecast(..., no_history=True)` is a negative
ablation, but does not mutate trained state.

## Engineering and science split

Six tests in `tests/test_native_temporal_context.py` cover:
- feature no-current-target leak and strict public-history ablation;
- original native cumulative learned prefix, archive, and prior head
  retention after admitted public-shaped mechanical events;
- deduplication, conflicting evidence, consumption and 64-event budget;
- rejection of forged cold weights and forged source receipts even when
  the attacker rehashes them;
- exact cold replay and deterministic readout forecasts.

Tests use only constructed public-shaped mechanical records, **not** the
previously scored RET01 synthetic development worlds, and do not prove
native novelty, real training on authenticated sources, unfamiliar causal
transfer, practical benefit, autonomous causal context discovery,
prediction gain versus conventional methods, or faster reasoning.

**No new original protected-world first-use is authorized.** The
independently controlled source-owner boundary [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426)
is still BLOCKED. Do not re-evaluate the old RET01 scored seeds or
promote this code. If independently authorized fresh source cohorts
become available, the separate prospective study must compare the
same-information and same-action trained history-aware conventional
Beta, recurrent and symbolic controls, with untouched unfamiliar held
families, old context return, source provenance and whole-process cost.
The candidate remains **DRAFT/UNMERGED**, `SCIENTIFIC_PASS=false`,
deployment NONE; no CKB/FORGE worker/controller/scheduler changes.
