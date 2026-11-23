# WSCM-GRID5-INGRESS-01 — five-action public witness ingress (development only)

**Outcome:** Engineering focused local PASS (15/15 normal and 15/15 -O); native learner integration / exact candidate full Linux+Windows regression UNVERIFIED; scientific transfer UNVERIFIED; deployment NONE.

## Existing-architecture boundary

A stateless *validator only*, not a second memory substrate, actor, source authority, trainer or controller. It does NOT modify `NativeExternalActionIdentity`, `NativeEpisodeExperience`, `NativeCumulativeLearner`, `NativeCausalAmalgam.plan`, any checkpoint version, or an active PR ref. It is an additive research-only prerequisite for a **future** owner-qualified source actor to feed authenticated public consequences into the EXISTING cumulative memory. No source actor or native learner consumes these records yet.

## Provenance and declared contract

- Parent exact WSCM PR #1364 `628ab0022f3fd7d3cb3f0925d9b93e8aa788b9cf` tree `7a9440a80af12183941e2d4fcf2824be6dedd319`; coordinator #1278 `86264b41a08d49f558418c0fba367f3a2636befa`; accepted main unchanged. Current work is a **detached Git commit**.
- Public upstream *Distillation for In-Context Planning* `jaehyeon-son/dicp@e36b3f713fdca775728525dc621820a1989691f8`: original `gridworld/env/darkroom.py` blob `54f12df08dbe9215d0b7be91a94f0b059f2787ab`; `gridworld/cfg/env/darkroom_permuted.yaml` blob `7d2c2f7c2dc26cbb854a8aaf071e947f20461891`.
- Source contract: five **native** action labels 0–4, 9×9 state coordinate, original reset at (0,0), 50-step horizon, next public coordinate, integer reward bit, paired terminated/truncated flags. A SHA-256-pinned canonical source-free `engineering_fixture_only` receipt contains only `episode_id`, `step_index`, `public_state`, `public_action`, `source_id`, `next_state`, `reward`, `terminated`, `truncated`, `schema` and `source_mode`.
- No `perm`, `perm_idx`, `goal`, `optimal_action`, evaluator truth, private role labels, or other hidden fields. Exact type guards prohibit Python `True`/1 aliases and negative indexes at the source boundary. The physical delta must be zero or one orthogonal step in-grid, without assuming a specific hidden mapping.
- The validator verifies exact request/receipt equality, bounded canonical bytes, witness SHA, unique episode/source IDs, strict within-episode continuity, terminal at step 49, no early reset or reentry, and 256-record batch maximum. It returns immutable public tuples only; it stores no state and does not select an action.
- A receipt SHA pins *bytes*, not independently authenticated original-world custody. `source_id` / `episode_id` are untrusted dev placeholders; a real actor must provision owner-controlled no-replay identifiers, independently prove source and split custody, and not leak hidden environment information in any metadata.

## Focused local result

Exact `grid5_public_ingress.py` Git blob `2733e0c587ae64ec7e17a550bda243569353dbc4`, SHA256 `86df0534a5cb12bee34691a3aa42a2f0eca5c79f2aea52ed3b7f3fc3cdb0b471`. Test blob `d2b15af3c02197d4135c30c72da03d1f363ab428`, SHA256 `51be49e4dfa95e0c3e9f5bae365ab2eea0687a797b3ad8b88449636605fa6218`. The original files were run locally on Linux CPython 3.13.5:
- `python -B -m unittest -v test_grid5_public_ingress` => **15/15 PASS**, 0.009 s.
- `python -O -B -m unittest -v test_grid5_public_ingress` => **15/15 PASS**, 0.009 s.
- `python -m py_compile grid5_public_ingress.py test_grid5_public_ingress.py` => PASS.
- Strict negative tests cover hidden-field injection, invalid action IDs, impossible movement, forged canonical pin, duplicate JSON keys, inconsistent episodes, replay, premature reset, terminal drift, and capacity.

## Hard HOLD

This is *not* an original environment world step, verified source license, owner-approved scientific first-use, native memory read/write, recovered cold checkpoint, trained policy, source-native 120-permutation identification result, 5.5-probe improvement, accepted runner regression, or deployment. Existing WSCM reference baseline `WSCM-PERMUTE-EXACT-01` detached commit `c158932ae29f7affc9a5e011052f950ca08fcea7` remains an exact symbolic comparator only. The original source has no identified license file for vendoring. Protected Yggdrasil #426 first-use stays HOLD. Do **not** promote this as learned transfer, nor wire it into an unchecked hot planner or a second memory.

**Next real engineering gate:** Preserving v1-v7 binary checkpoints and all G29 source atlas provenance, add qualified optional fixture-only ingress to existing `NativeEpisodeExperience` / `NativeCausalAmalgam` with immutable witnessed rows, exact cold replay, no binary-counter alias and an explicit five-action planner input. Then execute mandatory full final regression on the exact candidate across Linux and Windows, before any independent owner-authorized original-source trial.
