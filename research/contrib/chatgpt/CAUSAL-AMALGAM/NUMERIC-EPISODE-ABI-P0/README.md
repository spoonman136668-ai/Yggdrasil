# NUMERIC-EPISODE-ABI-P0 — research-only source-neutral public-event interface

Parent coordinator: `spoonman136668-ai/Yggdrasil` draft Amalgam PR #1278 at `86264b41a08d49f558418c0fba367f3a2636befa`. Frozen engineering contract and owner fence: `PROTOCOL.md`, committed as `6449640b026e2bb61f7b21a92769dfbfe176fed8` before the executed tests.

`numeric_public_episode.py` holds only *supplied* public one-step observations, exact floating-point values, five distinct actions, scalar reward and termination/truncation flags. No external environment is instantiated or acted upon. There is no model, inference, learned causal structure, owner signature, native CKAD adapter or source permission. Public packet shape is exact: nine visible fields. Private `info` / hidden task identities / forged authority are rejected. The 2048-row cap is an independent research-log capacity, **not** a native CKAD capacity extension.

`test_numeric_public_episode.py`: 12/12 focused source-free Python stdlib tests PASS, including negative injection/replay/digest tests, all five action identities, signed zero/subnormal preservation, cold restoration and the 2049 hard veto. Initial harness-only invalid substring assertion was corrected to check JSON keys; model code unchanged. Two fresh processes' normalized suite outputs identical. See `RESULT.json` for SHA256, Git blob hashes and scoped qualification; any actual native import, full Ubuntu/Windows regression, G29, original-world first-use, unfamiliar causal transfer, model improvement and deployment remain UNVERIFIED or blocked.

Reproduce with Python 3.13+ from the extracted bundle:

```
python -m py_compile numeric_public_episode.py test_numeric_public_episode.py
python -m unittest -v test_numeric_public_episode
```

This is a **data interface only**. Future use in native Amalgam must be separately approved by its owner and shown to preserve actual upstream source semantics, then subjected to mandatory final regression and separately authorized source-first-use. Existing MHE01-D fail-closed packet fence and source-owner #426 remain controlling. Do **not** present this as a memory repair.
