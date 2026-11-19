# Staged Amalgam retention - DEV_NO_GO

Protocol and producer were frozen before the run in commit
`c5bebd6df41360594abde98aea5309f950b83bf3`. Three isolated evaluation replicas of
the same 1,025-witness native-plus-JEPA joint state each continued through 72
new public synthetic witnesses. Their predecessors retained all 1,025 original
witnesses. All four existing specialist heads trained for 216 additional
gradient steps each per replica. The physical model, witness format and default
readout were unchanged. Each replica used 144 training interventions and
768 synthetic validation and reporting interventions. The 71.22-second producer
loop used 71.17 CPU seconds and 56,340 KiB peak RSS. No protected scientific source was used.

Historical and unfamiliar validation gates are separate from reporting draws.
The native-only, full Beta, trailing Beta and change-point Beta controls saw the
same online witnesses, using the complete pinned starting ledger for fitting.
All nine prospective checkpoint stages exceeded at least one retention bound
before committing. The guard selected its 1,025-witness fallback on all seeds.
All 1,097-witness experimental descendants are cold-reproducible from their
preserved traces and the pinned original checkpoint. Checkpoints have no
operational or promotion role.

## First altered structure

Held combined Brier loss, averaged over the transition and reward targets:

| Seed | Frozen/guarded native | Fully continuing native | Best fitted control |
| --- | ---: | ---: | ---: |
| 818621 | 0.277576 | 0.124653 | 0.100894 |
| 818653 | 0.252696 | 0.143653 | 0.134863 |
| 818687 | 0.236234 | 0.184743 | 0.151352 |

The continuing learner adapted on this structure but lagged the fitted
change-point baseline on all three seeds. On separate familiar reporting
draws, its transition loss rose by 0.186 to 0.254 absolute Brier in the same
stage. The two later stages did not clear both constraints. Gate failure does
not prove that the original witnesses disappeared. It shows that the
available live readout was not good enough across both familiar and changed
structures. Guarded state selection alone prevented regression by blocking
all advances, supplying no continual-learning advantage.

Full prequential predictions, stage decisions, recorded costs, report scores
and independent same-platform cold custody are in this directory. From the
repository root, use Linux with Python 3.12, the three pinned checkpoint
inputs named in selection_protocol_dev.json, and:

```sh
PYTHONPATH=.:research/contrib/chatgpt/CAUSAL-AMALGAM python -B \
  research/contrib/chatgpt/CAUSAL-AMALGAM/staged_retention_audit.py \
  CHECKPOINT_DIR \
  research/contrib/chatgpt/CAUSAL-AMALGAM/staged_retention_protocol.json \
  research/contrib/chatgpt/CAUSAL-AMALGAM/staged-retention-dev-01
```

The audit reconstructs committed witness suffixes without generating more
outcomes. This result covers matched fixed action sequences. It provides no
evidence about adaptive intervention efficiency, policy value, protected
first-use, cross-platform numerical trial reproducibility or deployment.
