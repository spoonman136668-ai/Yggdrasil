YGG-A50 PREREGISTRATION — SLOT118 REQUEST CONTENT COMPONENT DECOMPOSITION
Parent A49 run 36304392376 valid SLOT_CONTENT_INTERACTION.
Question: which request-content component at absolute corruption slot118 is required for the A49 failure interaction: request bits, stream/program identity, or both?
Freeze exact A49 replicate6 runtime/programs, donor3 corruption set [16,38,146,118], no phase3 corruptions105/113, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Use native replicate6 arrivals as base. Construct four slot118/119 content assignments while rid/t stay fixed:
1 NATIVE: no change.
2 BITS_SWAP_ONLY: exchange only bits between records118 and119.
3 STREAM_PROGRAM_SWAP_ONLY: exchange only {stream,program_a,program_b,program_c,program_d} between118 and119; bits remain native.
4 FULL_SWAP: exchange both bits and stream/program fields, reproducing A49 SWAP_118_119 at corruption slot118.
All other 158 arrivals remain byte-exact. Corruption remains fixed at slot118 in every arm.
Anchors:
- NATIVE must collapse;
- FULL_SWAP must not collapse.
Classification:
BITS_COMPONENT_REQUIRED if BITS_SWAP_ONLY abolishes collapse while STREAM_PROGRAM_SWAP_ONLY retains collapse.
STREAM_PROGRAM_COMPONENT_REQUIRED if STREAM_PROGRAM_SWAP_ONLY abolishes collapse while BITS_SWAP_ONLY retains collapse.
BOTH_CONTENT_COMPONENTS_INDEPENDENTLY_REQUIRED if both partial swaps abolish collapse.
COMBINED_CONTENT_INTERACTION if both partial swaps retain collapse but FULL_SWAP abolishes it.
CROSS_MODE_CONTENT_COMPONENT_DIFFERENCE if arm patterns differ by mode.
ANCHOR_NOT_REPRODUCED if NATIVE/FULL_SWAP anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact four arms; rid/t fixed; only preregistered fields changed; other158 arrivals exact; corruption set fixed [16,38,146,118]; []/[2] exact; fixed runtime constants; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
