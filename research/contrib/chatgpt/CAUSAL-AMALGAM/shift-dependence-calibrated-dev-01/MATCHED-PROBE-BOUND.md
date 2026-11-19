# Matched donor versus target probe bound

Exact evaluator calculation with fixed action allocations and a known
two-regime source. The query budget is identical across allocations. No
new simulator actions, training, or circuit witnesses.

At four total probes and strongly linked changes, low-contrast cells have
optimal Brier gain **0.012443** from four direct target probes versus
**0.007963** from four donor probes. Under unbalanced contrast strength, the
stronger donor gives **0.011395** versus **0.005047** from the direct target.
At eight probes in the latter family, five donor and three target probes
give **0.012744**, ahead of using all eight on either address. Under independent
changes, direct target probes win in both families. The implementation checks
probability mass and the independent zero-gain limit. Its donor-only figures
match the separately computed bounds.

This sets the design for the next eligible native development experiment.
Freeze balanced fixed, target-only, donor-only, learned allocation and known-law
oracle arms over a fresh source. Include correlated, independently changing,
and shifted-focus cases. Charge each source action. Compare both action value
and old-law retention against the strongest fitted controls. Treat learned
allocation as shadow-only until those criteria qualify.
