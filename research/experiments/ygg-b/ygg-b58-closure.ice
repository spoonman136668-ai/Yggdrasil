YGG-B58 CLOSURE
Run 36331204340 SHA b4fa7395b9c75403e3d6214dce32f955acc4cc24
Classification: ORDER_SHIFTS_HORIZON_WITH_RECOVERY
Valid: true. Duplicate SHA256 650004322a15936da2b37fcf28dd5c1e7f3f1ca1053e8299ec2dda1c180b21fd.
Using the same six distinct competitor identities as B57 but in reverse order:
loss counts by depth were 0,0,8,20,25,25 for depths1..6.
18 of25 seed/query strata changed first-loss depth relative to B57.
Despite those order-dependent shifts, every lost stratum was restored by the one final exact target refresh.
Interpretation: cumulative interference depth matters, but competitor identity/order materially shifts when failure first appears. Recovery remains robust to both tested orders.
Plain speak: how quickly memory breaks depends on the sequence of competing writes, but one precise rewrite still repairs it afterward.
Next: evaluate a bounded order family consisting of every cyclic rotation of the forward and reverse six-competitor sequences. This maps the range of first-loss depths while keeping identities and total load fixed.
