# CKAD42 — Cumulative online causal-intervention relation learning (DEV only)

**Source parent:** `c4aca6373211487f8cbe07ef0f64f88b937bd0f2` (CKAD41 draft PR #1290). **Preregistered before source** at `05f37a8675177b102b041741a1d3b678598a411e`. All changes are under this CKAD42 contribution and its isolated development-only GitHub workflow; original native learner and accepted `main` remain untouched.

## Why this successor is different

CKAD41 demonstrated a consistent failure of 16/32-event learned-native memory blocks to beat the original cumulative native stream. CKAD42 does not add new block recall. It tests whether **learned, persistent causal interaction weights** provide more transferable action→next state→terminal consequence knowledge than counting individual intervention cells.

The experimental native component learns posterior log weights on a **fixed, generic Boolean causal expression library** from genuine revealed source interventions and consequences. Transition uses the observed causal view and first action (2 input bits), terminal uses causal view, first action, *already observed* next state, and second action (4 input bits). The grammar is declared before any DEV outcome: literals, negations, pairwise AND/OR/XOR and two-term combinations. It contains no hidden scenario ID or future rule label.

Each genuine event updates:
- A full-history persistent causal hypothesis basis.
- A 0.93 geometrically discounted causal hypothesis basis.
- A prequential Hedge readout over the two, using **previously observed outcomes only**.
- An action-masked negative-control basis with equal expression class, which cannot see x1 or x2.
- The **unmodified** original `NativeEpisodeExperience` plus the fully trained conventional Beta/window/discount/Hedge controls on identical source actions.

The full and discounted native-template readouts are also competitors, so an ensemble cannot win by merely being a causal-grammar predictor. All trained relation weights are serialized, source IDs deduplicated, conflicting duplicate rejected atomically, cold restore required to recreate exact checkpoint bytes, and the original first-48 native source ledger must remain byte-exact.

This is an opt-in, standalone **research component in Yggdrasil's native causal-experience pathway**. It is not an accepted redesign, a novel deep architecture, or a claim that generic finite Boolean priors constitute general intelligence. The source environment remains stochastic *synthetic*, not real-world grounding.

## Frozen screen and stop

One original DEV attempt on **42111, 42112**, each two independent source worlds, with authentic A→novel B→A rule shifts. Earlier CKAD37–41 DEV/pilot cohorts are explicitly forbidden for this gate. Pilots `42211, 42212` and primary `42311,42312,42313` are reserved, not executable.

Both DEV seeds must have pooled late-B + late-return Brier <=0.15 and gain >=0.01 absolute over all: original native stream; strongest fully fitted conventional Beta/Hedge arm; fixed full-history causal basis; fixed 0.93 discounted causal basis; and action-masked causal ablation. Candidate cannot worsen early B or early-return vs original native by >0.01. Any failure is **DEV_NO_GO**, and no DEV retuning, original pilot replay or held primary first-use follows. A favorable DEV would be a development candidate, **not scientific qualification**; a genuinely unfamiliar-world held comparison with independent owner, stronger matched conventional/exact controls, cold retention and final full regression is still required.

## Development-only reproduction

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-42 -p 'test_ckad42.py' -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-42/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-42/screen_dev.py
```

GitHub Actions uses only an exact commit-message-triggered read-only development workflow on Ubuntu and Windows. No Forge/Yggdrasil owner/controller changes, scheduled task, external paid API, main mutation, training restart, merge, or deployment.
