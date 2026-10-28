# ITD-02 V31J — independent executed ring-message ledger (frozen before implementation)

Parent: **Yggdrasil V31I draft PR #632**, immutable commit `78df5918c785879895092ae8d2eeb677c9260638`. This preregistration MUST be the first new commit on the branch, before adding or executing V31J code. V31I's successful 24-event cold-restart custody remains unchanged; this gate is **source-only engineering instrumentation**, not an original-native or independent scientific experiment.

## Falsifiable concern

V22 maintains three virtual edge-scalar counters (`forward_input_messages`, `forward_output_messages`, `reverse_credit_messages`) per protected source/fast bank. Its `_site_features` recomputes `forward_local` for source inputs when scoring; `_coefficients` invokes `_mix_scalars` for reverse weights when scoring. Existing state counters may therefore omit executed neighbor computations. **Do not presume a mismatch, add counter corrections, reinterpret counters as actual physical bytes, or modify the learner. Measure the existing implementation independently.**

## Frozen procedure

- Reuse `research/itd02_v31i_cold_restart_audit.py`'s **unchanged** `train_source()`, exact development `cue_second` x12 then `source` x12 public selected-action cases, and unchanged `replay(source, with_restart)` in both uninterrupted and cold-restored modes. No Q1–Q3 or novel held-out calls.
- Add audit-process-only wrapping of `yggdrasil.itd02_v22_shared_context_ring_dev.forward_local` and `_mix_scalars`. Count each actual invocation and each reported original ring directed-edge scalar transmission. Restore original function bindings in `finally`; fail closed if a wrapper sees malformed counts or the unchanged model trace/checkpoint differs.
- Independently extract the two V22 bank counters from the V31I checkpoint after the same 24 legal public events. Report both *nominal state counters* and *observed executed scalar-hop computations*, their deltas, call counts, and the exact same model-output/cold-restore SHA. Compare Linux and Windows canonical, non-timing fields; any inconsistency is a qualification failure.
- Distinguish modeled scalar-hop operations from serialized wire bytes, physical memory traffic, runtime network I/O, and actual retail-device performance. Do **not** infer those from Python scalar counts. Protected-source parameter hash must remain unchanged.
- Predeclared classification: if all canonical identities match, counters are equal, and no unmetered work appears: `V31J_LEDGER_CONSISTENT__NO_SCIENCE`. If identities match but the recorded counters undercount observed edge-scalar operations: `V31J_UNMETERED_RECOMPUTATION_FOUND__NO_SCIENCE`. If any source, model, checkpoint, holdout, tracing, counter, or host identity is inconsistent: `V31J_INVALID_FAIL_CLOSED__NO_SCIENCE`. An undercount is an **engineering finding**, not a positive cognitive-science result.
- Mandatory checks: exact original ring/bridge and V22 blob identities, this prereg-first ancestry, scoped V26/V31I consistency, Windows 2022 + Ubuntu 24.04 reproducibility, one full inherited Python regression on Ubuntu (record any failure; no waiver), and immutable working source. Existing independent G29 Atlas remains blocking unless regenerated/requalified on exact source by its own path.

No main/accepted-ref changes, original native modification, controller/CKB-plane/FORGE mutation, automated research authority, provider/model invocation, promotion, new scheduler/queue, merge, science first-use, or G29 bypass. Keep DRAFT and explicitly preserve V31I results.
