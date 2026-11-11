# WSP-34 — numerical operator construction: MIXED

**Frozen before implementation:** preregistration commit `78ffd3288098c419a454dba98a5a5f85dc76a872`. **Original evaluated candidate:** `055dadeb616571de0a523ed9f031de52632953a6`, tree `44f5851ffabe92cb546b71d11cb9aaff24d6c8e1`. The preregistered learner and evaluator were not altered after a primary score was produced.

This study addresses WSP-33's reproducible unfamiliar-rule negative, not the already-solved problem of storing more source facts. A blank *operator layer* contains all 256 generic three-input GF(2) polynomial coefficient masks. Five actual target facts suppress inconsistent numeric candidates. An integer simplicity-weighted vote produces previously unqueried outputs; source query policy, original WSP29 source banks and WSP32 factual memories are reused unchanged. No XOR/switch-specific rule template or evaluator-hidden operator identity enters that layer.

| Frozen arm | Correct /5,760 |
|---|---:|
| WSP33 unchanged selected-two native | 3,184 |
| WSP34 degree-one-only ablation | 3,672 |
| WSP34 full numerical operator layer | **3,896** |
| WSP33 strongest converged source+head trained control | 3,636 |

New numerical layer: **+712** correct vs WSP33, **+224** vs linear ablation, and +260 over the previously qualified (not capacity-matched) trained control. **The frozen rule-nonregression requirement FAILS**, so the result is **MIXED**, not DEV_SUPPORTED or SCIENTIFIC_PASS:

- XOR: 988 old -> **1,900 new** (+912); linear ablation 1,960 (the full interaction layer actually loses 60 on this subgroup).
- Conditional switch: 2,196 old -> **1,996 new** (**-200**); linear ablation 1,712 (full interactions recover 284 vs this ablation).
- All 1,920 authored synthetic worlds and all 5,760 original heldout labels retained without filtering. 3,840 actual selected source answers. All 32,640 established fact checks, 3,840 acquired-fact checks, 3,840 source cold restorations, 1,920 operator cold restorations, and 1,920 source-bank preservation checks passed.
- Fixed static 2,048 coefficient bits and 256 plastic eligibility bits in the operator sublayer; largest serialized operator checkpoint 443 bytes. WSP29 source machines, WSP32 routing/fact machines and Python runtime are **not** included in those counts.

**Engineering qualification:** Linux and Windows both passed **344/344 tests** plus unchanged WSP33 primary, WSP34 primary, G29 atlas and clean tree at the exact original result source. Both independently reproduce scores and WSP34 trace SHA256 `67df05f53b6f290f3bee44fb3d3d42f5f27d114ea1bfa408da742737e431ab2b`. [Regression run](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43114175460), [G29 run](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43114175395). Precise receipts in `provenance.json`; full original Linux DEV JSON in `result.json`.

**Scientific boundary:** This is zero-gradient *operator-layer* construction from observed facts inside an authored fixed universal polynomial language. It is not ground-up programming of the full model, invention of a new primitive, matched all-in training-cost superiority or independent unfamiliar-world scientific acceptance. Preserve the negative conditional-switch result; a separately preregistered successor can investigate rule-specific aliasing/generalization and capacity-matched alternatives, without retuning this result. No merge, accepted refs, FORGE integration, controller/runner/queue/scheduler change, paid API or protected scientific first-use.

Reproduce: `python research/contrib/chatgpt/WSP-34/run_dev.py`; full suite: `python research/contrib/chatgpt/WSP-34/qualify.py`.
