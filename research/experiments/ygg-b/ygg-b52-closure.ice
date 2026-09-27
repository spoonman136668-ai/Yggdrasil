YGG-B52 CLOSURE
Run 36310819187 SHA f124d7974fb939d7042856cf7d71778c271ee6e1
Classification: DOSE_NONMONOTONIC
Valid: true. Duplicate SHA256 dacb2229cbf89aa37a68232382742bd5234cd5f4419d26917793876024591336.
D1, D2 and D3 all preserved universal target rescue.
Aggregate collateral NEW_ERROR was exactly identical:
D1 = 3724
D2 = 3724
D3 = 3724
The classification is DOSE_NONMONOTONIC only because the preregistered SINGLE_REFRESH_MINIMAL class required D1 to be strictly lower. Empirically, the measured behavior is dose-invariant across 1..3 exact consecutive target rewrites.
Interpretation: once the target is refreshed once, repeating the identical target write does not change measured retrieval outcomes through dose3.
Plain speak: one rewrite appears to do all the useful work. Repeating the same repair two more times neither helps nor hurts the measured memories.
Next: inspect the native persistent memory state and logits after D1/D2/D3 to determine whether the update itself is an exact fixed point after one rewrite or whether hidden state changes are behaviorally silent.
