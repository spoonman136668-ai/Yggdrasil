# NCI-04D / Yggdrasil — distributed functional setpoint repair
**Status:** source-grounded theoretical feasibility; **no successful regeneration result**.  
**Source base:** `e5b2596fd7972c9a577427902f917887f37ee4a6` (T45-O native candidate, not protected main).  
**Scientific first-use:** **0**. NCI-04C local teaching's 24-step loss to conventional retraining is preserved.

## The distinct principle

Instead of restoring a damaged cell's lost parameter vector, learn a **distributed target of function** expressed through continually predicted local interaction outcomes. Each intact cell holds local prediction, predictive uncertainty, an eligibility trace and a compact local *error/setpoint message*. A lesion produces observable local functional error, which propagates only by actual neighbor-to-neighbor exchanges. Surviving cells self-organize specialization by reducing their local prediction errors under shared compute and activity constraints.

This is inspired by developmental pattern regulation and distributed homeostasis (Levin 2023; bioelectric patterning reviews) but computational novelty or efficacy is **not** assumed. Crucially, it changes the information source for recovery from **newly supervised regeneration of the missing cell** (which lost to conventional retraining) to **previously accumulated distributed functional constraints held in surviving local cells**. If those constraints are absent, recovery cannot be inferred and the gate must fail.

- **Only local data:** at update t, each cell i may read its own raw sensor, last state, two immediate neighbors' *previous-round* messages and the next locally measured outcome. No global best-match, centrally selected cell roles, hidden function label, broadcast target, full-network state, or old lesion-site weights.
- **Cell state:** small bounded trainable local predictor; message channel for predicted neighbor contribution and confidence; local eligibility/plasticity; optional shared birth genome that may not encode a specific lost-cell function. Cells must actually differentiate measured response functions by learning, not by designer-assigned port indexes.
- **Local update:** minimize one-step prediction mismatch plus a bounded cooperative consistency/homeostatic term inferred from messages and a resource penalty. A missing cell is replaced with a **blank** one. Compensation may begin in surviving neighbors before replacement and propagate hop-by-hop. No neighbor-weight copy is permitted in the candidate (but retain that exact operation as a **control**).
- **Functional loss/recovery:** assess the performance of the *entire network* on a previously learned task after a lesion and repair, not the damaged cell's next-bit probability alone. Include A→B→A retention and unfamiliar lesion location. Measure recovery steps and total active CPU/bytes/communications, not only final error.

## Feasibility and impossibility boundary

**Locality lower bound:** for an eight-cell ring, a signal originating at cell i cannot affect a cell d edges away in fewer than d synchronous, one-hop rounds. Max shortest-path distance is four hops. **Any instantaneous globally coordinated recovery is evidence of prohibited nonlocal information.**

**Information preservation condition:** if the pre-lesion function's essential information exists *only* in the destroyed cell, and no surviving sensors/messages or environmental feedback distinguish the desired output, no local repair rule can reconstruct it reliably. A proposed fast-regeneration gain is feasible only when surviving local states store predictive constraints, and there is a recoverable learning signal or redundant task structure. Include an **irrecoverable-lesion** negative control that must fail safely, not hallucinate target recovery.

**Current native blocker:** `yggdrasil/cells.py` has eight independent seven-feature binary logistic predictors. Each uses its own and neighbors' current **observed input bits** but stores no persistent per-cell message/phenotype, no learned self-organized role or homeostatic setpoint; `neighbor_copy_baseline` copies adjacent weights and is correctly identified as a conventional baseline. Preserve this maintained interface and add isolated, opt-in local message/state operations only after their memory/CPU ledger is specified.

**Bounded compute:** with N cells, degree two, per-cell message dimension m and local state dimension d, communication per round is `2 N m` scalars and local update scales `O(N(d+m))` plus bounded learning arithmetic. Budget the entire lesion-and-recovery interval including extra rounds, training, memory and messages. Both copied-parameter baselines and freshly trained local recurrent/developmental controls must receive identical sources and activity cost allowance.

## One feasibility decision *before* scientific first-use

1. Establish two **functionally separable** tasks learned through local observations (not supplied cell roles). Pre-register observable network-level function and random held-out lesion sites. Include a *zero-information irreversible lesion* negative control; never count cosmetic regrowth as recovery.
2. Demonstrate a new functional error signal emerges from local prediction alone, propagates **exactly one edge per round**, and persists long enough for survivors to compensate. Verify source loss, network-level task outcome, newly reconstructed function, and A→B→A retention.
3. Compare, at matched total CPU/RSS/bytes/communication, against fully trained local GRU/recurrent rules, ordinary equal-budget post-lesion retraining, neighbor-weight copy, recovery-disabled ablation, and intact and irreparably damaged baselines. Ensure no hidden pre-lesion lesion-site checkpoint or globally supplied target.
4. **Go** only if network-level function recovers faster *and* more reliably than strongest equally informed conventional control on previously unseen damage/structure at no greater total cost, with zero hard false positives. Otherwise retain a real negative and stop the mechanism. No first-use scientific evidence may be consumed before feasibility.

## Why this is not the previously failed local-teaching variant

The primary predictor is **collective functional error stored outside the lost cell**, not a newly blank cell mixing its error target with adjacent predictions. This has an explicit information-preservation test and a graph-speed lower bound. A gain explained by ordinary local re-training, neighbor copying or extra message rounds is a disqualifying result.

Background: https://pmc.ncbi.nlm.nih.gov/articles/PMC10770221/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC10478168/
