# Matched specialist selection and historical readout protection

The saved PR #1278 joint state from run 44432722069 starts with 1,025 witnesses.
The fixed selection protocol admitted 96 public synthetic witnesses into the
same native model and updated all four existing JEPA heads. The native/action
planner remained unchanged. On Linux, the checkpoint round-tripped exactly
in a separate process. The resulting 1,121-witness candidate's joint SHA-256
is recorded in producer.json, including its parent, all update counts,
process time, peak RSS and trace digest.

**Development NO-GO.** The selector used native forecasts for 64/64 scored
decisions and tied native Brier at 0.167332. Direct and temporal head Brier
were 0.265219 and 0.261731. Fresh protected science and policy utility were
unmeasured. Each phase had one synthetic seed, so phase and seed were
confounded. See audit.json and selection_protocol_dev.json.

No checkpoint files are copied into this directory. On Linux, reconstruct
the candidate byte-for-byte without new source actions using the original
joint checkpoint artifact and the pinned native and donor inputs, then run
retention_replay.py with this directory as the existing-evidence argument.
The original artifact can also be reconstructed with joint_update_preflight.py
from the original native and donor inputs. This retains every actual receipt
without making the negative descendant an active training parent.

## Historical readout diagnostic

The guard compares the pinned historical readout with the new candidate
on the same 96 already-consumed old episodes, across three fixed windows.
It tests transition and reward losses separately and preserves the original
anchor when either target exceeds the 0.02 Brier drift bound in any window.
The original 1,025-event witness prefix is byte-identical. The latest
historical window's transition Brier rose from 0.102145 to 0.126531
(+0.024386), so the guard rejected the 1,121-witness candidate. The result is
a retrospective diagnostic. No new actions, training run, policy change or
scientific promotion occurred while evaluating the guard.

[YGG-RET01](https://github.com/spoonman136668-ai/Yggdrasil/pull/1285) already
tested evidence-weighted archive selection. The archives preserved historical
scores. The combined reader lost to fitted online Beta baselines on both fresh
development seeds. Its artifacts and the CKAD39/40 negative results stay
separate. This check reuses immutable historical readout comparison. It
does not insert an archive selector into the action policy, conflate
observations with imagined consequences or copy RET01 weights into Amalgam.

A prospective follow-up needs distinct historical competence and new-domain
gates in the same frozen comparison, multiple independent seeds, unrevealed
observations and intervention outcomes separated by provenance, matched
conventional and exact controls, negative/mispaired specialists, whole-process
cost, and cold restoration. The candidate update should remain reversible
until both gates pass.
