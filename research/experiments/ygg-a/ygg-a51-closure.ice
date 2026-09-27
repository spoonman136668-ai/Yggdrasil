YGG-A51 CLOSURE
Run 36309192379 SHA ce39545317ba0f9b20c29e73817a8ff4e7903088
Classification: STREAM_LABEL_REQUIRED
Valid: true. Duplicate SHA256 a7298af8f311118ab4e797afacfa99b7207c3a2a9c8649bf4a6bb74062509af1.
Both U_A0 and U_A25 produced:
NATIVE=true
PROGRAM_SWAP_ONLY=true
STREAM_SWAP_ONLY=false
STREAM_PROGRAM_SWAP=false
Bits, rid/t, corruption set [16,38,146,118], and all other 158 arrivals remained fixed as preregistered.
Interpretation: the slot118 timing-content interaction depends on the stream label rather than the four bound program identities.
Plain speak: request118 fails because it is labeled as the native stream at that moment. Swapping the programs alone does nothing; swapping the stream label removes the failure.
Next: change the stream label at request118 and request119 separately to determine whether the causal label is specifically the corrupted request118 or the neighboring request119 context.
