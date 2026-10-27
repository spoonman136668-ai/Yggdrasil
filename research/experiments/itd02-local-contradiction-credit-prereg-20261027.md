# ITD-02 native local contradiction-credit preregistration (source-free, 2026-10-27)

Authority: engineering-only; not scientific first-use, not authentic task-source data, not model promotion. Frozen parent Yggdrasil draft PR #582 head: `a39171a76d0d7817e3563682bb139a9d7ecf37c4`. This experimental branch must never update that parent or any accepted reference.

## Hypothesis and bounded scope
The existing eight-cell neighbor-routed local reward learner has fixed normalized response gain. A **confident, sign-inconsistent public reward** may justify a stronger selected-head adjustment and local two-hop eligibility credit. Change only `NativeRingMemoryDev.feedback`; keep exactly 8 gate logits + 9 head coefficients, original eight-cell ring, immutable external source and authorized public reward observations. No additional state fields, no changed checkpoint schema, no oracle/model-writing agent, no global skip-edge, no FSA admission.

Fixed hypothesis before code:
- Contradiction means previous *selected-action* public reward prediction and newly observed reward have opposite non-zero sign, and |prediction| >= 1; it does not include unchosen action labels.
- Bounded gain multiplier for selected action head: 1.6x existing 0.7 normalized update (0.7 -> 1.12), otherwise unchanged.
- Neighbor-only gate plasticity step multiplier: 1.25x existing 0.12 under contradiction, otherwise unchanged.
- Preserve existing finite checks, clamping, frozen veto, source checkpoint identity and existing tests.

## Held-out development evaluation
Run the original **unfamiliar-family** source-only qualification harness, but with **families=6..13** and **seeds=4..11** (64 pairs), distinct from the six families/4 seeds used to initially select PR #582. Same 90 initial and 90 unfamiliar-phase episodes per acting learner; four independently acting public-feedback learners including EMA(0.5), rolling-six count and full-history count. All use identical deterministic, rotating source-blind exploration opportunities; no reward mapping is provided to actors. Freeze both parent/candidate source SHA, run on Linux and Windows, assert matching behavior, cold interpreter restore and fixed parameter count.

Per-implementation: 64 trials × 180 steps × 4 actors = 46,080 public events. Measure train and unfamiliar-phase on-policy reward, last-24 reward, frozen held-out success, retained checkpoint bytes and process CPU; Linux resource observations are preferred for comparative process timing; hosted CI does not establish retail-PC performance.

**Decision rule**: reject this contradiction-credit mechanism if its mean unfamiliar reward does not improve on the exact frozen parent under same task budget, or if native regressions fail. Even if it improves, leave draft/unaccepted unless resource and performance compare favorably to the best recency-aware conventional controls and separately complete G29, original source custody, retail-hardware, external-world and independent science gates. Preserve all negative controls and trial-level losses. Do not tune coefficients after inspecting these held-out results; a new independently preregistered gate is required.
