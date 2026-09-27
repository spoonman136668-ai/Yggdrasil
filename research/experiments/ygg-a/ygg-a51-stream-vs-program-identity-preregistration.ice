YGG-A51 PREREGISTRATION — STREAM LABEL VS PROGRAM IDENTITY AT SLOT118
Parent A50 run 36307037815 valid STREAM_PROGRAM_COMPONENT_REQUIRED.
Question: within the slot118 stream/program package, does the failure interaction depend on stream label, program identities, or both?
Freeze exact A50 substrate: replicate6 runtime, donor3 corruption [16,38,146,118], native request bits, no phase3 corruptions105/113, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Base is the native replicate6 arrival stream. Construct four 118/119 assignments with rid/t and bits fixed:
1 NATIVE.
2 STREAM_SWAP_ONLY: exchange only stream labels between118 and119; program_a..d remain native.
3 PROGRAM_SWAP_ONLY: exchange only program_a..d between118 and119; stream labels remain native.
4 STREAM_PROGRAM_SWAP: exchange stream plus program_a..d, reproducing A50 STREAM_PROGRAM_SWAP_ONLY.
All other 158 arrivals remain exact; corruption stays fixed at118.
Anchors: NATIVE collapses; STREAM_PROGRAM_SWAP does not collapse.
Classification:
STREAM_LABEL_REQUIRED if STREAM_SWAP_ONLY abolishes collapse and PROGRAM_SWAP_ONLY retains it.
PROGRAM_IDENTITY_REQUIRED if PROGRAM_SWAP_ONLY abolishes collapse and STREAM_SWAP_ONLY retains it.
BOTH_INDEPENDENTLY_REQUIRED if both partial swaps abolish collapse.
COMBINED_STREAM_PROGRAM_INTERACTION if both partial swaps retain collapse but combined swap abolishes it.
CROSS_MODE_STREAM_PROGRAM_DIFFERENCE if patterns differ across modes.
ANCHOR_NOT_REPRODUCED if anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact four arms; bits/rid/t fixed; only preregistered fields changed; other158 arrivals exact; corruption set fixed; []/[2] exact; fixed runtime constants; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
