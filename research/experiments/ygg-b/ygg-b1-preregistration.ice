TITLE: YGG-B1 Sequence Memory
DATE: 2026-09-24
STATUS: PREREGISTERED
LANE: YGG-B
BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Can bounded recurrent cellular state preserve information from earlier sequence positions and use it for a delayed target?

FROZEN TASK
vocabulary 8
sequence length 16
dependency lag 8
state width 16
five training seeds
disjoint held-out evaluation

CONTROLS
persistent state
state reset between positions
fixed-seed shuffle of earlier symbols

SUCCESS
persistent held-out accuracy >= 0.90
reset accuracy <= 0.70
persistent-reset gap >= 0.20
shuffle degradation >= 0.15
median persistent accuracy >= 0.95
all five seeds preserve the expected causal direction

RULE
Any unmet gate is a scientific negative. Thresholds remain frozen after results.
This lane cannot promote the shared baseline by itself.
