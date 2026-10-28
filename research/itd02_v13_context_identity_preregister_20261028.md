# ITD-02 V13 — preregistered public-context identifiability feasibility (development only)

**Immutable parent:** Yggdrasil PR #594 head `61786dc802e8a646ca623121ab02b33ebab05909`, unmerged V12 native two-step eligibility NO-GO. The source file under audit is `yggdrasil/itd02_native_task_bridge_dev.py`, Git blob `71eff80e3cfabb627e9d08d558b63f4043ce1fd5`. Reference original native source: `658b855d1b217d20ed9d431fe99b2e866469b7e9`. This document is committed **before** the new executable audit. There is no accepted-model mutation.

## Motivation and locked question

V12 genuine selected-action study #40618242669 improved reversal (+127.83 mean earned reward against original) but **regressed unfamiliar** (-36.83) and lost to the strong history-aware EMA. V12 constructs the source-public two-phase native input as `_temporal_public_bits(Nothing, second, phase) XOR _temporal_public_bits(first_cue, first_action, phase)`. Hypothesis: different legal (first public cue, actual first action, actual second action) histories collide in these input vectors, limiting even a fully competent native reward fit. Test the encoding itself before implementing another learning rule.

## Frozen source-free audit

- Context universe: exactly `(LRV, MRV, docked_LRV, docked_MRV) × (TurnAround, GoForward, Backup) × (TurnAround, GoForward, Backup)`: 36 distinct legal public histories. No sampled rewards, secret source parameters, private observations, fitted weights, or original-world episodes.
- Reconstruct *both* 8-bit phase vectors using the exact original source-visible public encoding, then compare them with the actual bridge's frozen `start_observation → accept_public_transition(learning=False, terminal=False) → start_observation(Nothing) → _task_bits` interface. All 36 two-phase vectors must match. No scientific credit from frozen scores.
- Count `unique_combined_context_codes`, collision groups, `aliased_contexts`, and a stable SHA-256 of sorted canonical public tuple/code records. Assert `len(universe)==36`, and record rather than suppress aliasing. Distinguish distinct full-vector collisions from *additional* reward-head local-neighborhood indistinguishability.
- Negative-control test: alter only public histories, never hidden law; changing the second selected action should not silently change the stored first public action. Native weights, learned memory, source-owner journal, and all checkpoint identities remain unchanged after frozen readouts; restore and terminal clearing must be enforced.
- Run deterministic audit on Linux and Windows using exact source checkout. Source-free read-only audit is not protected first-use, live training, native scientific acceptance, or retail-PC qualification.

## Predeclared decision, before seeing new audit

- If **any** two legal histories collide on the complete 16-bit concatenated pair, classify `V12_CONTEXT_NONIDENTIFIABLE` and **DO NOT** reuse V12's XOR context representation for a new positive claim. An explicit collision witness is required.
- If full concatenated representations are all distinct but the original native reward heads cannot distinguish relevant histories through their existing one-hop sites, classify `LOCAL_READOUT_NONIDENTIFIABLE`; no new training experiment until the representational boundary is resolved.
- A next candidate must preserve the authentic original eight-cell ring and native `LocalTaskRuntime`, strict source-only observations, bounded neighbor-local information propagation, bounded checkpoint, no global source-law/answer table and no additional hidden evaluator features. It must obtain 36/36 distinct full public contexts and separately check local reward-head distinguishability **before** any new acting/science claim.
- Following capacity qualification, a **separate** new preregistration must freeze independent unfamiliar families/seeds, matched acting/observation budgets, stronger history-aware EMA/count/TD controls, real two-step selected feedback, cold-start retention, composition/transfer and whole-process Windows retail CPU/RAM. Do not reuse consumed families 300–305 or 312–317 as unseen evidence. No positive claim unless unfamiliar and reversal both beat the strongest legitimate control without familiar regression at comparable resources; no post-result threshold edits.

## Authority and negative custody

No mutation of original model, PR #594, accepted source or checkpoints, G29 indexes, FORGE/CKB-plane, controller, launcher, worker, scientific ledger, source-first-use, or production/runtime activation. No merge or promotion. This is only a bounded frozen-source feasibility gate; preserve all previous V12 negatives and exact source provenance.
