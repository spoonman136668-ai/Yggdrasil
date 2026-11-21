# RS01 — source/donor semantic compatibility gate (2026-11-21)

**RESULT: CURRENT PAIRING NO-GO.** This is a static code/metadata and prior-evidence comparison, **not** a protected world action, donor execution, model fit, new scientific evaluation, new source-family admission, native integration, or checkpoint. Do not open another source-screen PR, propose a new controller, or repeat original consumed splits.

## Repo custody
- Yggdrasil accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; this contributor branch had head `c8b20cd1125347aa45b67b9e289a78dfaee4bff6`, tree `ea0f0c951127ecb4957555028671c4729643f6a0` before the disposition file.
- Existing [RS01 source-free development protocol](PROTOCOL.md), [interface](identity_gate.mjs), and [regression tests](identity_gate.test.mjs) remain unchanged. Their `VALIDATION_ADMITTED` response is **only a fixture-rule outcome**, not original learned donor evidence.
- Original real-data [DWSA-64 result](https://github.com/spoonman136668-ai/Yggdrasil/pull/1347#issuecomment-7069020649) is **already consumed**: the pretrained LunarLander WM280 `rssm.obs_encoder` consumed original historical data, took **8 physical observations** and used **4 discrete actions** in the tested task; it lost to a raw-input model on B-held Brier (`0.01329291` versus `0.00558477`). No independent learning gain.
- Upstream donor: `nsmoly/LunarLander_RSSM@85c5c38b61b028af67d9120f516fb2f01bce4b9c`, `models.py` Git blob `2bdba38c63d9a87797c85ab867fee315c69d8672`, lines 19–45 and 142–179: RSSM observation encoder is initialized with `obs_dim`; source world model defines six physics and two contact dimensions. The actual historical WM280 weights belong to that published task.
- Upstream alternative benchmark **already** qualified as provisional by existing native research owners: [WSP-173 issue #910](https://github.com/spoonman136668-ai/Yggdrasil/issues/910), [WSP-179 graph selection correction](https://github.com/spoonman136668-ai/Yggdrasil/issues/426#issuecomment-6990521536), [WSP-181 graph-vs-mechanism distinction](https://github.com/spoonman136668-ai/Yggdrasil/issues/426#issuecomment-6991748585). No new benchmark acquisition is justified.

## Independent pinned upstream contract — chemistry graph world
- Source: `dido1998/CausalMBRL@2c595988b06b3d568fdde53213029e97841acb03`, `envs/chemistry_env_rl.py` blob `58af54d7e7e30f8abe059df3d68565845a5b2c51`; MIT `LICENSE` blob `cff393fe08ddf5fdd6fa4b8f509df9789bf54900`.
- Source constructor default `num_objects=5`, `num_colors=num_objects`, `width=5`, `height=5`; `action_space=Discrete(num_objects*num_colors)` = **25 intervention actions**. Original `observation_space` is **(3,50,50)**, i.e. **7,500 raw image values**; original `get_state()` returns **(num_objects*num_colors,width,height)`** = **(25,5,5)**, **625 encoded state values**.
- Source `step` returns `(state_obs,reward,False,None)`, where `state_obs` is a tuple of original state image and rendered RGB image; `reward` is proportion of target object-color matches. This is not a four-action flight-contact domain. An arbitrary 8-value projection, zero-padding or renaming source variables would destroy original semantic parity and is **not** demonstrated donor knowledge assimilation.
- No pretrained weights/checkpoints (`.pt`, `.pth`, `.ckpt`, `.h5`, `.onnx`, `.npz`, `.pkl`) appeared in the pinned upstream repository's complete Git tree (108 entries, `truncated=false`). This is **not** evidence that no trained donor exists externally; it means no **source-pinned matching pretrained donor** is currently established in this gate.
- Original source code includes `set_graph(g)` to select defined topologies, while `reset(graph=...)` ignores its graph argument. Earlier [owner-source evidence](https://github.com/spoonman136668-ai/Yggdrasil/issues/426#issuecomment-6990521536) **already** diagnosed that fact. This audit does not repeat a source run.
- **Already-proven benchmark saturation:** [WSP-176](https://github.com/spoonman136668-ai/Yggdrasil/issues/426#issuecomment-6987272427) demonstrates that a fixed ascending five-object target-setting sequence reaches perfect final goal under the pinned mechanics; `terminal_goal_success` and five-step reward cannot support a novel learner gain. Later [WSP-181](https://github.com/spoonman136668-ai/Yggdrasil/issues/426#issuecomment-6991748585) also shows graph-only reconfiguration reuses original MLP parameters. Do not claim independent unseen mechanism transfer from a graph-name switch.

## Executed static gate: scientific input compatibility
| Required attribute | Existing WM280 LunarLander donor | Original chemistry source | Gate |
| --- | --- | --- | --- |
| Public input | 8D physical flight/landing state | 625 one-hot state values OR 7,500 image pixels | **FAIL** — no source-authenticated feature map |
| Intervention/action schema | 4 discrete actions | 25 object/color interventions | **FAIL** — semantic and dimensional mismatch |
| Prediction target | LunarLander leg-contact from original task | Chemistry object-color transitions / target-match reward | **FAIL** — no source-native donor readout |
| Independent donor prior | Published LunarLander-trained encoder; historical source already seen | No pinned compatible pretrained chemistry donor | **UNVERIFIED** |
| Scientific headroom | Raw baseline beat donor+repair in prior test | Final goal saturated by fixed five-step control | **NO-GO** for terminal objective |
| Original first-use | None authorized by this artifact | Existing issue #426 explicitly **NO-GO** | **BLOCKED** |

These are **static contract facts**, not a claim that numerical prediction on chemistry was run. A source-matched pre-trained donor might be found elsewhere, but neither this original donor nor RS01 proves any cross-domain causal assimilation.

## Decision and only meaningful future science gate
**STOP this donor→chemistry pairing.** Preserve the original BR01/DWSA-64 negatives and RS01 source-free gate tests. Do not create an 8→625 arbitrary projection, synthesize replacement ground truth, reuse the prior LunarLander splits, train another source-only toy, invoke original chemistry construction/`set_graph`/`reset`/`step`, or dispatch any workflow/runner on this basis.

A future native RS01 science attempt requires **before first use**:
1. A source-/semantics-matched *already pretrained* donor checkpoint with exact weight bytes, independent original training provenance, licensed source and a documented public observation/action/target mapping. If unavailable, **stop DWA** for that source, or explicitly reclassify a new equal-data trained feature learner as **not** a direct pretrained-weight transplant.
2. An independently qualified unfamiliar source mechanism/cohort under existing [source owner #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426); exact authentic source/family/rng/model identities, signed one-shot lease, no-replay effects, full public information/action parity and conditional budget. New graph names/seeds from one MLP do not suffice.
3. A nontrivial prospective causal-consequence/cold-retention target with a demonstrably non-saturating original-world oracle-free baseline. Fully optimized supervised/Bayesian/tabular/symbolic/recurrent source-native controls, same exposure, compute and actions, and frozen numerical gain/stop criteria. No HELD tuning; the source owner alone may authorize physical actions.
4. Existing single native Yggdrasil learner and coordinator PR #1278, not another learner/controller. Preserve native tokenless architecture and negative outcomes.

**ENGINEERING:** source compatibility **CHECK PASS** (mismatch conclusively identified), RS01 native integration/mandatory full-platform regression **UNVERIFIED**. **SCIENCE:** current pairing **NO-GO**; unfamiliar transfer and gain **NOT TESTED**. **DEPLOYMENT:** NONE. **PROTECTED ACTIONS:** zero in this gate. Accepted main and current native checkpoints unchanged. **User action:** none for this static stop; an actual future protected experiment requires existing native owner admission.
