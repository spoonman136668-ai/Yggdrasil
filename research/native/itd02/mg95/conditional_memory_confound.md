# MG95-B conditional lookup screening: confound identified

Source commit `cb7d466ded6708765d8670469321e50a9d040e59`; blob `b7f450e58922649a31354766b102cb4c02d040ca`.

Independent JavaScript equation-level reproduction (NOT exact-source Python execution):

| Learner | Held-out correct/24 | Allocated state |
| --- | ---: | ---: |
| Full three-feature conditional lookup | 24 | 16 bits |
| Action-only lookup | 24 | 16 bits |
| Context-only lookup | 12 | 16 bits |

Major confound: training iterates action, context, intervention with intervention last; since action-only and context-only learners overwrite their most recent value, action-only stores the intervention outcome at the end and becomes accidentally perfect on exclusively intervened heldout. Full 8-entry lookup is conventional. Allocated 16-bit arrays do not mean matched **effective** information capacity for action-only/context-only learners, which use 2 entries each.

Scientific disposition: NON-DIAGNOSTIC, NOT A POSITIVE NATIVE RESULT. The next experiment must order-randomize training, balance observation/intervention heldout with genuine distribution shifts, account for active state bytes and matching baselines, and verify cold restart. Exact committed Python execution UNVERIFIED. Original-world experiment and mandatory full regression NOT EXECUTED. No promotion.
