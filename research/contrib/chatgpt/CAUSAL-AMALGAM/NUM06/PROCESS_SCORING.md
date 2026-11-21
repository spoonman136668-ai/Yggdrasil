# NUM06 process qualification (fixture only)

Each arm uses two fresh Python processes, with the first fully exited before
the second starts. Transfer only the model's serialized state and its digest
at the prescribed return boundary, plus evaluator fixture configuration.
Both use the same deterministic synthetic fixture (no reserved cohort).
The restore process verifies exact state bytes, and predicts the first return
case before observing it; the supervisor verifies equality to the live
prefix forecast and matches full/late/return scores against the same-process
reference for all eleven arms. Restore uses only witnessed history in model
checkpoint or control state. This is still fixture evidence, not genuine
unfamiliar-world learning. The source and scoring metadata are evaluator-only.

RSS is the maximum of two isolated worker peak resident-memory readings
(Linux getrusage self, Windows PeakWorkingSetSize); it includes interpreter,
source fixture realization and evaluation bookkeeping. CPU is separately
measured for prediction/update/restore and whole worker body. Process startup,
IPC and host load are not included in the worker CPU numbers. Actual resource
parity requires an admitted fitted comparison and explicit matched budgets;
there is no resource-qualification or science PASS field here.

## Timing portability correction

Windows fixture run 44885876308, job 136791057941, reported a zero CPU delta
for cell_recent40 and zero_sham; the positive-only timer assertion failed.
This is an unresolved measurement, not a zero-cost claim or a forecast failure.
Preserve raw nonnegative deltas, explicitly classify zero as BELOW_TIMER_DETECTION,
and distinguish nominal reported clock resolution from actual effective detection.
Report worker-body wall time and end-to-end supervised wall time separately.
Never substitute wall time for CPU or compute ratios from unresolved CPU timings.
Resource parity remains false pending sufficiently measurable matched-budget
qualification. Exact restoration, scoring and reserved-seed denial are unchanged.
