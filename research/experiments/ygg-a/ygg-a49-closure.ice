YGG-A49 CLOSURE
Run 36304392376 SHA 1fe84a3f6f55aab87e4643e8863eafa86d6e10e4
Classification: SLOT_CONTENT_INTERACTION
Valid: true. Duplicate SHA256 cbc9fe571a1f4c02e31f46e689ba78d48475210fd31f34d01e54649ac22bbcf3.
Both U_A0 and U_A25 produced the identical four-arm matrix:
NATIVE slot118=true
NATIVE slot119=false
SWAP_118_119 slot118=false
SWAP_118_119 slot119=false
The 118/119 content swap exchanged only {stream,bits,program_a,program_b,program_c,program_d}; rid/t positions remained fixed; the other 158 arrivals and phase3 stream totals were unchanged.
Interpretation: neither absolute slot alone nor request content alone is sufficient. Collapse requires the native request content to occur at absolute corruption slot118.
Plain speak: request118 fails only when the right request is corrupted at the right moment. Moving the request content or moving the corruption one step later both prevent the failure.
Next: hold corruption at slot118 and separately swap the request bits versus the stream/program identity between 118 and119 to identify which content component interacts with timing.
