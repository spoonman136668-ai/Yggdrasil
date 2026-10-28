"""Independent conventional factorization with matched operation library."""
from conventional_composition_controls import ConventionalFactorized

class ConventionalOperationControl(ConventionalFactorized):
    def predict(self,bits):
        messages=self.messages(bits)
        if None in messages:return None
        # Each operation is independently evaluated; do not import the
        # native candidate hypothesis engine.
        a,b=messages
        candidates=(a^b, not(a^b),a and b,not(a and b),a or b,not(a or b))
        valid=set(range(len(candidates)))
        checked=0
        for (x,y),counts in self.final.items():
            if sum(counts)<2 or counts[0]==counts[1]:continue
            checked+=1
            choices=(x^y,not(x^y),x and y,not(x and y),x or y,not(x or y))
            valid={i for i in valid if choices[i]==(counts[1]>counts[0])}
        if checked<2 or not valid:return None
        results={candidates[i] for i in valid}
        return next(iter(results)) if len(results)==1 else None
