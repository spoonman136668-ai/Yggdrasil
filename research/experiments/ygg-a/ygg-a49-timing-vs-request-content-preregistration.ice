YGG-A49 PREREGISTRATION — CORRUPTION SLOT VS REQUEST CONTENT FACTORIAL
Parent A48 run 36286531409 valid THIRD_EVENT_TIMING_SUFFICIENT.
Question: does the request118-vs119 failure boundary follow the absolute developmental slot/rid being corrupted, or the request content normally occupying that slot?
Freeze exact A48 replicate6 runtime/programs, donor3 non-phase3 corruptions [16,38,146], no phase3 corruptions 105/113, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic. No retraining/adaptation/threshold/topology/baseline changes.
Factorial:
- corruption slot C in {118,119};
- request-content assignment X in {NATIVE, SWAP_118_119}.
NATIVE uses the exact replicate6 arrival stream.
SWAP_118_119 keeps rid and t fixed but exchanges only the request content fields {stream,bits,program_a,program_b,program_c,program_d} between arrival records118 and119. Thus absolute time/rid positions are unchanged while the two request contents exchange slots. Both records remain in phase3; the phase3 stream-count totals are preserved.
All other 158 arrival records and all other corruption IDs remain exact.
Inherited native anchors:
- NATIVE,C=118 must collapse;
- NATIVE,C=119 must not collapse.
Classification:
ABSOLUTE_SLOT_DOMINANT if both content assignments collapse at C=118 and do not collapse at C=119.
REQUEST_CONTENT_DOMINANT if under SWAP the collapse follows the content originally at118, yielding NATIVE 118=T/119=F and SWAP 118=F/119=T.
SLOT_CONTENT_INTERACTION if the four-arm pattern matches neither dominant case but native anchors reproduce.
CROSS_MODE_SLOT_CONTENT_DIFFERENCE if patterns differ across modes.
ANCHOR_NOT_REPRODUCED if native anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact four arms per mode; only 118/119 content fields exchanged in SWAP; rid/t fixed; other 158 arrivals exact; stream-count totals preserved; corruption set exactly [16,38,146,C]; []/[2] exact; fixed runtime/program constants; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
