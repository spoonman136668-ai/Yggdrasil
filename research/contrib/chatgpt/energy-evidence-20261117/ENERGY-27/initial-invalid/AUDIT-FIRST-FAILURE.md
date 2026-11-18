# ENERGY-27 first independent audit attempt

After frozen scoring, the independently implemented exact-Fraction auditor stopped at its first `correct == c['correct']` assertion. Its exact posterior had already matched scorer logged posterior probabilities to 2e-12. The scorer uses IEEE-754 log-weight normalization and `q>0.5` to classify. The audit uses exact rational posterior. The failure requires inspecting whether the disagreement is a near-0.5 tie; scored results and frozen source have not been modified. This was an **audit failure**, not a pass.
