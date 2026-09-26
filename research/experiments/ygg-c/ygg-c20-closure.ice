YGG-C20 CLOSURE
Run 36255033844 SHA 5d0964e6eb90ccf03e538d9672e84e7b002fad6a
Classification: MIXED_IDENTITY_CONTEXT
Valid: true. Duplicate SHA256 4af4cc5718de0aef1381f35dc2df90da86c291ca135ccdf81e23c01a55f7476b.
Parent C19 failure reproduced exactly at alpha 0.134765625 and levels 8..16: replicate8 alone failed maturity at every level.
All non8 exchange partners were tested. Explicit non-lesion-byte preservation passed for replicate8 and each partner in every exchange, satisfying the preregistered evidence contract. Duplicate analysis was byte-identical.
For every level and every non8 partner, assigning the partner lesion to replicate8 made replicate8 pass maturity, and assigning replicate8's lesion to the partner also left the partner mature.
Interpretation: the failure is not identity-bound and not lesion-context-bound independently. It requires the original replicate8 identity together with its original lesion/context pairing. The exact local fragility of that pairing remains unknown.
Plain speak: replicate8 fails only with its own original damage pattern. Give replicate8 somebody else's equally sized damage pattern and it recovers; give replicate8's damage pattern to somebody else and they also recover. The bad outcome comes from the pairing, not either ingredient alone.
Next: perturb the original replicate8 lesion by exactly one lesion-cell substitution toward a fixed preregistered rescuing partner to determine whether the failing pairing is locally brittle or robust.
