YGG-A56 PREREGISTRATION — EXHAUSTIVE PHASE3 SINGLE STREAM-LABEL FLIP SWEEP
Parent A55 run 36312696296 valid DISTANT_97_EFFECT.
Question: how distributed is the phase3 stream-history dependency that controls replicate6 singleton-cell2 collapse?
Freeze exact A55 native substrate: replicate6 runtime/programs/arrival stream, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Native phase3 spans requests96..127.
Arms per mode:
- NATIVE anchor.
- For every rid k in 96..127, exactly one arm FLIP_k that changes only arrivals[k].stream C<->S.
rid/t/bits/program_a..d remain native. All other159 arrivals remain exact. Corruption set remains fixed.
Report exact sensitive_rids = flips that abolish collapse and insensitive_rids = flips that retain collapse.
Known inherited examples expected if anchors reproduce: flips97,116,118,119,120 are sensitive.
Classification:
PHASE3_STREAM_SCHEDULE_GLOBALLY_FRAGILE if all32 single flips abolish collapse.
DISTRIBUTED_STREAM_SENSITIVITY if 2..31 flips abolish collapse.
SINGLE_POSITION_STREAM_SENSITIVITY if exactly1 flip abolishes collapse.
NO_SINGLE_STREAM_FLIP_EFFECT if no flip abolishes collapse.
CROSS_MODE_PHASE3_FLIP_DIFFERENCE if sensitive sets differ across modes.
ANCHOR_NOT_REPRODUCED if NATIVE does not collapse.
OTHER_VALID_PATTERN otherwise.
Validity: native anchor exact; exactly32 unique flip arms plus native; only one registered stream label changes per flip; rid/t/bits/programs fixed; other159 arrivals exact; corruption fixed; []/[2] exact; runtime constants fixed; inherited known-sensitive positions reproduced; scientific integrity; duplicate byte-identical; globals restored.
Scientific negatives are valid. No post-result tuning.
