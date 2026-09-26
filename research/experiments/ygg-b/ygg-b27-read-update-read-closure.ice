TITLE: YGG-B27 Read-Update-Read Sequence Episode Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: 968ddbc85106e0589f0d412ebd5cba2849ce7bd1
PARENT_CLOSURE: f1b9726614af1c57841310c25f5d1daa57c5e2fa
EXECUTION_HEAD: 94aea1d7473a9dec6886419c7f1cc5d09d802c60
WORKFLOW_RUN_ID: 36202939708
DUPLICATE_SHA256: 3f4ede632b639a781374f7fdf7b60cf6353f4d7b9a9ca7353d51d38d7717d3d0

RESULT
YGG_B27_READ_UPDATE_READ_SEQUENCE_EPISODE=false
mechanical_gate=true
duplicate_byte_identical=true
all_causal_direction=true
state=32
parameters=120

Persistent joint two-read accuracy:
seed111=.740234375
seed222=.738525390625
seed333=.736328125
seed444=.7255859375
seed555=.739990234375

All reset and perturbation controls behaved in the preregistered causal direction.
The failure is therefore scientific: the unchanged compact substrate does not meet the frozen >=.90 joint two-read criterion.

INTERPRETATION
Seven-binding terminal overwrite capacity does not automatically imply reliable multi-output sequence episodes. The new sequence demand exposed a capability boundary without any evidence-integrity or causal-control failure.

NEXT QUESTION
Keep the exact B27 task, architecture, data split, seeds, optimizer, training budget, controls, state, and parameter count. Measure READ-1 and READ-2 accuracies separately to determine whether the deficit is in one read stage, both individual reads, or only their conjunction.

BOUNDARY
Synthetic sequence task only.
No architecture expansion.
No language corpus yet.
No online adaptation.
No recursive self-modification.
