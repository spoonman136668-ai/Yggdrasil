"""Out-of-memory public-world recovery without pretending prior transfer is safe.

On contradiction of all learned source worlds, abandon source hypotheses,
retain newly observed target evidence, and build independent public truth
slots. No hidden target identity or privileged answer. In-memory hypotheses
can still be wrong on unobserved inputs: this limitation is measured.
"""
from empirical_local_probe import EmpiricalLocalProbe
from unrestricted_operation_cells import INPUTS,TruthSlot

class RecoveringLocalProbe(EmpiricalLocalProbe):
    def __init__(self):
        super().__init__()
        self.fallback=False
        self.target_slots={key:TruthSlot() for key in INPUTS}
        self.public_feedback=0

    def observe_target(self,key,outcome):
        if key not in INPUTS or type(outcome) is not bool:
            raise ValueError("INVALID_PUBLIC_TARGET")
        self.target_slots[key].observe(outcome)
        self.public_feedback+=1
        if key in self.observed:
            if self.observed[key]!=outcome:
                # Contradictory repeat: stop all retained inference.
                self.fallback=True
            return
        if self.fallback:
            self.observed[key]=outcome
            self.target_actions+=1
            return
        super().observe_target(key,outcome)
        if not self._candidate_indices:
            self.fallback=True

    def predict(self,key):
        if key not in INPUTS:raise ValueError("PUBLIC_KEY_REQUIRED")
        if self.fallback:
            return self.target_slots[key].value()
        return super().predict(key)

    def select_probe(self):
        if self.fallback:
            return next((key for key in INPUTS if key not in self.observed),None)
        return super().select_probe()
