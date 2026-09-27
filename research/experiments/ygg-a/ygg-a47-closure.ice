YGG-A47 CLOSURE
Run 36285542450 SHA 29d6dd8098bc2f016d0aacf318259043c5fe5830
Classification: SINGLE_EVENT_TIMING_SENSITIVE
Valid: true. Duplicate SHA256 490c31a09c7fc5cf53cc6566938ad6effdb5e43df83683721319d2d493243038.
Base donor3 phase3 events are 105(offset9), 113(offset17), 118(offset22).
Both U_A0 and U_A25 produced identical results.
- Moving event105 alone to every valid nonduplicate phase3 offset never abolished collapse.
- Moving event113 alone to every valid nonduplicate phase3 offset never abolished collapse.
- Moving event118 alone was highly selective: collapse remained only at offsets [22,24,26]; all other valid offsets abolished collapse.
All family base anchors reproduced; one-event-only mutation, non-phase3 schedule, phase3 count, runtime/program/arrival integrity, duplicate execution and restoration checks passed.
Interpretation: the phase3 timing sensitivity is localized to the third corruption event, originally request118. The first two phase3 event timings are individually noncritical under the tested background.
Plain speak: one event is doing the timing-sensitive work. The first two corruption moments can move around freely, but the third only causes failure in a very narrow late-phase window.
Next: test whether that third-event timing effect survives when the other two phase3 corruption events are independently absent, using a frozen 2x2x2 factorial.
