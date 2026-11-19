# Observation-fitted probe allocation

Frozen executable `c21fc02e785de932ad620456b82aa4726ceb4248`, tree `87d409bb5ca00f17b2380da93b73ee5dc9d84f63`.

**DEV_NO_GO.** Under an equal eight-probe budget, the observation-fitted policy
trailed the best fixed allocation in each correlated replica by **0.011094**
Brier on average. Its worst independent-case loss versus direct target
probing was **0.006120**, above the 0.002 bound. The four nonoracle arms score
through the same fitted prediction code. This localizes the comparison to
the probes each arm chooses.

In the strong-donor correlated replicas, the source-aware reference selected
five donor probes in all six. The learned policy selected one donor probe in
two replicas and none in four. In one independent strong-donor replica it
instead assigned four donor probes. The point-estimated allocator did not use
stronger donor evidence reliably.

The benchmark charges all policy probes including matched exposures to common
simulator randomness, as well as shared calibration and held scoring.
**75,456** charged simulated probes, 0.405 s local timed kernel, exact
per-replica trace digests, and zero admissions to the native model.
Source-free independent limiting-case fixtures passed. Neither the source nor
the allocation policy has protected or deployed effects.

The known-law bound remains useful, while point estimates conflate uncertainty
about how sharply each outcome identifies a regime and whether regimes change
together. For a fresh comparison, integrate uncertainty about those quantities
jointly and compare to direct target probing with the same budget. Preserve
the earlier negatives, use a fresh roster, and keep the circuit batch held.
