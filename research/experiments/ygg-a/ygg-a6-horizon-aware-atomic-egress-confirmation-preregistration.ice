TITLE: YGG-A6 Prospective Horizon-Aware Atomic Egress Confirmation Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_A5_CLOSURE: fb9ba4904e799c96b0a2b5a71d655d9a01262749
SOURCE_A4_CLOSURE: c493896e4552f2bc9c9b0190bf105212a66ec572
SOURCE_A4_PREREGISTRATION: 6c7d11b0a2acf1b97b39f5510d2c02f83cc31acd

QUESTION
When evaluated prospectively with a horizon-aware integrity contract frozen before execution, does the exact YGG-A4 atomic egress handoff preserve the fork/join capability and terminal integrity across all ten frozen worlds?

PURPOSE
A5 established that the historical compact repair_integrity summary conflicts with the already-frozen TERMINAL_159 maturity rule.
A6 does not change or reclassify A4.
It prospectively freezes one coherent terminal contract and re-executes the exact A4 mechanism so future developmental work has an internally consistent accepted measurement boundary.

SCIENTIFIC MECHANISM
Use the exact YGG-A4 atomic egress handoff unchanged:
- when ROUTE first lands on the request's exact local egress, perform the existing VERIFY observation atomically;
- correct output -> VERIFIED at the same epoch;
- corrupt output -> detected=true and REPAIR_PENDING at the same epoch;
- no atomic repair;
- no extra matched service operation;
- no added epoch;
- no added routing or processing capacity.

FROZEN
- exact ten A1/A4 primary manifests;
- exact 160-epoch horizon;
- exact fork/join task graph;
- exact programs, seeds, arrivals, lesions, anchors, corruption schedule, routing, expiry, repair, verification, and DONE semantics;
- exact inherited scheduler used by A4;
- exact local service capacity;
- exact U_A0 arm;
- exact A4 mechanical contract;
- exact frozen maturity rules, including TERMINAL_159;
- no model RNG;
- no learned authority;
- no online adaptation.

HORIZON-AWARE INTEGRITY CONTRACT
For each world define horizon_aware_repair_integrity=true iff all are true:
1. incorrect_done == 0.
2. matching duplicate cell/request counts are zero.
3. maturity.pass == true.
4. verification_detected == corruptions_reaching_egress.
5. Every detected corruption is either:
   a. repaired under the inherited repair/reverify semantics; or
   b. represented by exactly one passing maturity row with:
      kind=TERMINAL_159,
      detection_epoch=159,
      repair_epoch=null,
      verified_epoch=null,
      done_epoch=null,
      terminal_state=REPAIR_PENDING.
6. verification_detected == repaired + count(TERMINAL_159).

The historical compact repair_integrity field is retained and reported unchanged but is NOT a success gate in A6.

PRIMARY
Execute the exact A4 primary mechanism twice over all ten frozen worlds.
The complete canonical outputs must be byte-identical.

SUCCESS
- baseline_feasible_count >= 8;
- all ten worlds zero incorrect DONE;
- all ten worlds matching integrity exact;
- both sibling orders exercised;
- D never before B/C join;
- fork dependencies exact;
- all ten worlds maturity.pass == true;
- all ten worlds horizon_aware_repair_integrity == true;
- inherited repair/reverify fixture true;
- duplicate complete execution byte-identical;
- replicate 10 request 141 is detected at epoch 159 and is either exact TERMINAL_159 REPAIR_PENDING or a stronger completed-valid state without incorrect DONE.

REPORT
Per world:
- legacy repair_integrity;
- horizon_aware_repair_integrity;
- corruptions_reaching_egress;
- verification_detected;
- repaired;
- TERMINAL_159 count and rows;
- maturity pass;
- incorrect DONE;
- matching integrity.

FAILURE
Any unmet frozen A6 gate is a scientific negative.
Do not change A4 mechanism, horizon, manifests, maturity definitions, terminal rule, scheduler, or capacity after observing results.

INTERPRETATION
Positive:
The atomic egress handoff is prospectively confirmed under a terminal contract that is internally consistent with the frozen horizon semantics, establishing a valid forward measurement state for later developmental experiments.

Negative:
A5's contract diagnosis is insufficient to validate the atomic handoff prospectively; the remaining failure must be isolated before advancing the developmental substrate.

BOUNDARY
A4 historical verdict remains negative.
No shared-baseline promotion from A6 alone.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
