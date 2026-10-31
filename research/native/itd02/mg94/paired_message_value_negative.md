# MG94-AA paired message-value reproduction

Classification: SOURCE-FREE SYNTHETIC DEVELOPMENT, NEGATIVE RESULT.

Baseline repo sources: `paired_message_value_assay.py` blob `4c1c9863dbe4e9c0206b407935379664d35bfaff`; `consequential_routing.py` blob `5ab3faf8b2bde44cd525da7954cdd629dc28188d`.

Local Python reproduction of the committed logic, NOT byte-identical Git blobs. Six 24-event streams, prequential correct predictions, one-point fixed per-message cost.

| Stream | Messages | Routed correct | Disabled correct | Net delta |
|---|---:|---:|---:|---:|
| Stable | 0 | 23 | 23 | 0 |
| Reversal | 0 | 21 | 21 | 0 |
| Recurrence | 0 | 20 | 20 | 0 |
| Alternating | 0 | 22 | 22 | 0 |
| Blocks of two | 9 | 6 | 6 | -9 |
| Irregular | 2 | 12 | 13 | -3 |

Total: 11 messages; 1 fewer correct predictions with routing; net delta -12 after message cost.

Result: No observed positive routing value. Offline paired comparison is retrospective and cannot train an online policy without separating training and evaluation outcomes.

Local equivalent implementation PASS; exact-source Python execution UNVERIFIED; original-owner CI UNVERIFIED; full regression UNVERIFIED; original-world experiments NOT EXECUTED. Scientific gain NOT DEMONSTRATED. No promotion.
