YGG-A50 CLOSURE
Run 36307037815 SHA 93adebec9c2edd9ee22e0d341346f747e770218f
Classification: STREAM_PROGRAM_COMPONENT_REQUIRED
Valid: true. Duplicate SHA256 a9b389ab7b59a01b6a788797aa9332eb73ec40c3b1aeba409d79e23e7b538740.
Both U_A0 and U_A25 produced:
NATIVE=true
BITS_SWAP_ONLY=true
STREAM_PROGRAM_SWAP_ONLY=false
FULL_SWAP=false
Corruption remained fixed at [16,38,146,118]; rid/t were fixed; only preregistered fields at118/119 changed; all integrity and duplicate checks passed.
Interpretation: the A49 timing-content interaction is carried by stream/program identity, not request bits.
Plain speak: changing the raw bits does nothing. Changing which stream/program package occupies request118 removes the failure.
Next: separate stream label from the four program identities at slots118/119 to determine which part of the stream/program package interacts with corruption timing.
