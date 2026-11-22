# CKAD19 composed DTR decisions

The integrated learner combines its existing transition and terminal forecasts
to compare first actions. It selects a contingent second action for each
possible next state. Both decision stages use the original Beta estimates.

The standalone conventional dynamic program reconstructs all values and actions
from the identical witnessed prefix. The three full CKAD18 snapshots restore
the same plan with their complete learned bytes preserved.

On 192 already-consumed held episodes, 49 entire
logged paths match the final policy. Only those paths reveal its actual reward.
Its finite-cohort return bounds have numerators [34, 177]
over 192. The paired full-policy gate is False.
The final terminal choice matches 97 logged actions
at factual histories. The terminal-only paired gate is
False.

The bounds allow all binary outcomes compatible with the public log.
A terminal recommendation at a factual history cannot resolve the reward or
state that would follow a different first action. The source was already
consumed. Science remains unqualified and deployment status is NONE.

The campaign took 13.461 seconds on Linux and
21.969 seconds on Windows, including three cold
restores per run and excluding CI setup and final qualification.

Reproduce with python -B research/contrib/chatgpt/CKAD-19/campaign.py
--output-directory /tmp/ckad19. Run independent_audit.py in the same directory
to verify the sealed evidence.
