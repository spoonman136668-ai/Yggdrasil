TITLE: YGG-A7 Learned Developmental Arm Integrity Compatibility Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_CLOSURE: c2432d153f6e21e89173cd46e5ee822b65a5df86
PARENT_EXPERIMENT: YGG-A6
MECHANISM_PARENT: YGG-A4
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Does the confirmed atomic egress integrity handoff remain compatible with the learned U_A25 developmental arm, preserving fork/join task capability and the prospective horizon-aware integrity contract relative to the U_A0 control arm?

FROZEN
- exact YGG-A4 atomic egress handoff mechanism;
- exact YGG-A6 horizon-aware terminal integrity contract;
- exact ten A1/A4/A6 primary manifests;
- exact 160-epoch horizon;
- exact fork/join task graph A -> {B,C} -> D;
- exact programs, seeds, arrivals, lesions, anchors, corruption schedule, routing, expiry, repair, verification, and DONE semantics;
- exact local service capacity;
- exact inherited scheduler used by A4/A6;
- exact frozen maturity rules including TERMINAL_159;
- no online adaptation;
- deterministic execution.

SCIENTIFIC CHANGE
Evaluate the exact same atomic-handoff world under two developmental modes:
CONTROL: U_A0
TREATMENT: U_A25

No other mechanism, task, manifest, horizon, scheduler, or integrity-rule change is permitted.

CAUSAL EXERCISE
The learned arm is considered materially exercised iff at least one of the ten paired worlds has a different state_sha256 between U_A0 and U_A25.
Report divergence count and paired task outcomes.

HORIZON-AWARE INTEGRITY
Use the exact YGG-A6 rule prospectively for both arms:
- incorrect_done == 0;
- matching duplicate counts zero;
- maturity.pass == true;
- verification_detected == corruptions_reaching_egress;
- every detected corruption is repaired or an exact passing TERMINAL_159 row;
- verification_detected == repaired + TERMINAL_159 count.

PRIMARY CAPABILITY GATES FOR U_A25
- all ten worlds horizon_aware_repair_integrity == true;
- all ten worlds incorrect_done == 0;
- all ten worlds matching integrity exact;
- all ten worlds maturity.pass == true;
- aggregate U_A25 correct_done >= 95% of matched U_A0 aggregate correct_done;
- every U_A25 world correct_done >= 90% of its matched U_A0 correct_done;
- learned arm materially exercised;
- inherited fork/join mechanical fixture remains exact;
- duplicate complete paired execution byte-identical.

REPORT
Per replicate and arm:
- correct_done, backlog, incorrect_done;
- maturity pass;
- horizon-aware and legacy repair integrity;
- corruption reached/detected/repaired/TERMINAL_159;
- state_sha256;
- atomic egress checks/detections.

Also report:
- aggregate A25/A0 correct_done ratio;
- per-world A25/A0 correct_done ratios;
- state-divergence count.

FAILURE
Any unmet frozen gate is a scientific negative.
Do not change alpha/mode, thresholds, manifests, horizon, scheduler, atomic handoff, or integrity contract after observing results.

INTERPRETATION
Positive:
The learned developmental A25 dynamics are compatible with the accepted local integrity semantics and preserve the fork/join capability envelope.

Negative:
The learned developmental arm introduces a compatibility/capability boundary that must be isolated before more autonomous developmental control is added.

BOUNDARY
No shared-baseline promotion from A7 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
