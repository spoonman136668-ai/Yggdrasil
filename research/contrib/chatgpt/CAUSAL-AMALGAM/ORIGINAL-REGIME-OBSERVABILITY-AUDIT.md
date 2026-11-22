# G41-R16 read-only sequential observability audit — original 1,025-to-2,048 evidence

**Classification:** RETROSPECTIVE_DEVELOPMENT_ONLY. Not a trained native model, not a preregistered statistical alarm, not new source first-use, not a retention or transfer improvement. No checkpoint/learner/accepted-ref change.

## Pinned original evidence and independent readback

- Accepted `main@5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; coordinator draft [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) head `86264b41a08d49f558418c0fba367f3a2636befa`; supporting [PR #1329](https://github.com/spoonman136668-ai/Yggdrasil/pull/1329) head `bbcca1d06d394a7bcfdc514f4e04bb269cb023cb`.
- Preexisting original archives [Actions #44499793023](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44499793023): Linux artifact `14517860401`, ZIP SHA256 `b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d`; Windows artifact `14516669671`, ZIP SHA256 `bb2b689f84caf939b76bea669eff7efb26506b602eed81ac79a81b42efb0a5a6`.
- Inner native SHA256 `5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d` and inner episode SHA256 `9158254b80f147d7eb7516d630f6003441df4b8373375b994d864ee1d55568f4` match Linux and Windows. Original Linux joint JSON SHA256 `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`. Original `accepted_native=false`, `scientific_pass=false`, `source_mode=engineering_fixture_only`.
- Verified [R13 source `d55c5038`](https://github.com/spoonman136668-ai/Yggdrasil/blob/d55c5038c560aa96f6401462df47def9009ea340/tests/test_g41_amalgam_capacity_integration.py#L275-L289): 1,023 existing source-free DEV continuation records always have `views=((0,0),(0,0))`, first action 0, observed state 0, second action 0, reward 0. Source test Git blob `7c14f04bce86645af3fea7d743567ed33fc622f9`; this is NOT the real protected world.
- Original [R11 Linux+Windows run #44935461661](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44935461661) reports native context reset at episode **1,035**, with original prefix preserved and no native source promotion. Later [R12](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44944949527) finds oldest reward mixture degradation and novel-expert weight surge, again on consumed witnesses.
- The 67-collision source fact was previously identified by [G41-R14 audit #7070346132](https://github.com/spoonman136668-ai/Yggdrasil/pull/1329#issuecomment-7070346132). This audit adds the consecutive-outcome sequence and retrospective reference surprisal calculation, **not** a new claim of causal novelty.

## New exact source-only observation

Read the 1,025 `episodes` from the original joint state; for the public query key `(view0=(0,0), first=0, observed_state=0, second=0)`, there are **67** observations: reward 1 **61** times, reward 0 **6** times. Among those 67 in chronological order, the **longest consecutive zero-reward streak is two**. Windows and Linux inner episode streams agree byte-for-byte.

For a post hoc, query-specific **Beta(1,1)** reference distribution on positive-reward probability, the predictive posterior is `Beta(62,7)`. The probability of the **next four** matching public outcomes all being zero **without a change** is exactly:

```
(7/69) * (8/70) * (9/71) * (10/72) = 1/4899
                                                   = 0.00020412329046744235
```

At a descriptive one-shot reference threshold of `0.001`, the first zero-run length with probability at or below the threshold is **4**, which the preexisting all-zero continuation would reach at episode **1,029**; the actual native stream-rebuild event is recorded at episode **1,035**. This shows an available *observable reward-change signal* in the constructed development stream. **It is not a valid fair comparison of detector speed**: the Beta reference and exact query were selected retrospectively, it does not model multiple repeated alarms, and the native detector uses a different full-stream definition.

For replication, hash both original ZIPs and extract their `amalgam-joint-state.json -> native_ascii -> experience_ascii -> episodes`, check the exact inner SHA256s, filter the exact public query and evaluate:

```python
from fractions import Fraction
p = Fraction(1, 1)
for j in range(4):
    p *= Fraction(7 + j, 69 + j)
assert p == Fraction(1, 4899)
```

Local isolated Linux verification: source bytes checked against the exact archive hashes; Python 3.13 `py_compile` and internal negative count tests PASS; second independently launched process produced byte-identical JSON. Local source SHA256 `dd0c44a0e84dccd75bc36acad3eaed1603f7406dbdbc971f00e91dedd79de674`, result SHA256 `7460c7532cbe08eb607f399e87912e6b8582eb51c7c48caf28a005cac4a5ca0f`; measured process 0.64 seconds, 111,740 KiB peak RSS. The standalone local script is **not** claimed committed or full-native qualified.

## Engineering / science / deployment decision

**ENGINEERING:** original archive checks, exact collision extraction, source snippet, and deterministic arithmetic PASS. No original native module restore or final full-platform regression in this gate.

**SCIENCE:** `scientific_gain_verified=false`. Under the same visible query, the old data contain 61/67 positive rewards whereas the synthetic continuation has 0/1023. A query-only predictor cannot produce two conflicting conditional distributions simultaneously. Historical A-return after the synthetic B has **not** been sampled in the G41 2,048 continuation: retrospective scoring of old windows is not a prospective A-return test. This experiment is **not evidence of restored memory**. R13 fixed caps and CAID-04 retrospective synthetic regime-posteriors are separately NO-GO; do not retune them.

**DEPLOYMENT:** none. No owner runner, source actor, new-world first use, model write, candidate merge, schedule, or new controller authorized here.

**Required next research gate:** a genuinely *pre-action, sequence-evidence-conditioned* regime representation must be evaluated on an owner-qualified, fresh A→B→A action-consequence sequence with actual observed A-return, matched information/actions/compute versus a fully trained fixed native baseline and action-matched conventional change-point/HMM controls. Freeze hypotheses, early-return Brier, false reactivations on AAA/ABB, old retention, cold readout, provenance and stop thresholds before exposure. Source-owner [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) remains NO-GO for new original-world first-use. Do not infer authorization from this audit.

## Committed minimal reproduction (exact local bytes)

The optional, concise source-authenticated reproducer is checked into the **same isolated diagnostic branch** at `research/contrib/chatgpt/CAUSAL-AMALGAM/g41_regime_signal_repro.py` (Git blob `1c435dfead5ece243618cc49180492310042fffb`, SHA256 `057d0cef059d54c2085c1a968886b12ef8904d662de070372dbfd78ad4db1890`). Its byte-identical, double-run output is `g41-regime-signal-result.json` (Git blob `8079452a3c3f4f79d37a1098d28b2007b819b348`, SHA256 `df87bb55f77c3a9e4679decc2e823f116bf6356364cda8e87672e7ba168438bc`). Python 3.13 `py_compile` and direct execution PASS on the two existing verified ZIP inputs, without a repository-native import or any new source outcomes. This minimal committed reproducer is distinct from the more extensive uncommitted local scratchpad script described above.
