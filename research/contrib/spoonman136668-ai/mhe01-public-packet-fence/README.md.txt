# EXT-MHE01 — Shadow public-packet fence for external causal driving

**Research contributor, source-free engineering only. No environment execution, scientific first-use, model state, native trainer, owner authentication, or integration.**

## Problem

At pinned [MetaHighwayEnv source](https://github.com/leejisue/MetaHighwayEnv/tree/a194c73b3261a137d84521e1520dfa4f4c690faa), the wrapper can reveal weather through `info["task"]["confounder"]` and `difficulty=weather`. Its underlying highway environment also appends reward decomposition and can report `driver_aggressiveness` in its ordinary `info`. Merely disabling the wrapper's optional causal logger is **insufficient** to make raw `info` safe. With `include_task_id=true`, a numeric task identifier can be appended to observations.

The original source has distinct driving steps and `intervene()` operations. Some intervention requests change reward weights; others only update configuration until the next reset. An intervention request receipt cannot establish that a learner witnessed its consequence.

## Scoped engineering contract

This package accepts **only Python list/tuple** two-dimensional, bounded finite numeric observation fixtures with an explicitly supplied shape. It allows the public core-highway five-action driving policy (`0..4`), numeric scalar reward and boolean termination flags. It requires an asserted pinned source SHA and requires `include_task_id=false`, `enable_causal_logging=false`; the settings have **not** been independently authenticated against an actual executed environment. The future authorized source actor must separately convert real NumPy arrays to lists, verify the actual learner-visible observation shape and pin a source-owned configuration receipt. No guessed reshaping or action cardinality for another road environment is permitted.

The projection **drops all raw reset and step `info` fields** regardless of optional logging settings. No source task ID, task object, `difficulty`, latent weather, reward components, SCM graph or oracle/counterfactual data is output or included in the local packet digest. Both source flags are still checked because task identity may arrive *inside* the raw observation, not only `info`. A correct static shape is **necessary but not sufficient** to establish that the actual underlying source observations are public.

A separate `inspect_intervention_metadata` function validates exact known core-highway intervention variable, timing and `applied/requires_reset` consistency. An episode-level scene change awaits authenticated reset and public effect. A mid-episode physical change still awaits a public effect. Reward-weight and duration modifications are not accepted as causal-action comparison gains. Nothing produced by the inspector is learner-visible or a witnessed-do receipt.

All projected packets explicitly state `source_owner_authenticated=false`, `native_admission=false`, and `scientific_pass=false`. Their SHA-256 digests certify local packet content **only**; they do not authenticate who generated a source event.

## Source and compatibility

The immutable original upstream commit is `a194c73b3261a137d84521e1520dfa4f4c690faa`, MIT license blob `1993f2e1a1e4993cbff028f6d4140a7ffe3290ae`. The preregistration lists individual upstream file blobs. Current accepted Yggdrasil `main` was `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` at this contributor's fork point.

**No native adapter:** `NativeCausalAmalgam.observe_experience(identifier,views,row,source_sha256,packet_sha256)` has a separate verified event ABI. WSP-156 has independently qualified *six-bit* source-do receipt prerequisites. Neither accepts this static core-highway packet as an actual native learning event. Do not inject synthetic trace bytes or infer a valid source owner signature from this research module.

## Reproduction

These GitHub files use `.py.txt` so they remain **isolated research sources**. In an independent stdlib Python 3.12 sandbox copy `packet_fence.py.txt` to `packet_fence.py`, `test_packet_fence.py.txt` to `test_packet_fence.py`, and `prereg.json.txt` unchanged, then run:

```
python -B -m unittest -v test_packet_fence
```

A separate one-shot exact-research-SHA CI gate verifies these 21 static tests, full original native regression on Linux/Windows, chronological prereg Git blob, G29 source atlas, and no candidate-tree contamination; it neither instantiates nor imports the external simulator.

**Scientific and deployment classification:** NOT TESTED; original first-use remains denied by source owner issue #426; canonical Yggdrasil checkpoint remains unauthenticated under LINEAGE01 #1322; central Amalgam Work chat alone coordinates accepted native lineage. No runner, scheduled task, original world actions, model training, or deployment is authorized or requested here.
