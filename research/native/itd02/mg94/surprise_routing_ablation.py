"""MG94-U developmental local-cell surprise routing and ablation.

A source-free mechanism hypothesis, not native scientific evidence. Public binary
observations only. No reward labels, hidden state or original-world execution.
Compare identical local cells with routing enabled vs disabled. The context
selector is externally supplied and therefore does NOT constitute learned binding.
"""
from collections import defaultdict

class RoutedCells:
    def __init__(self, route=True):
        self.route = route
        self.local = [[1, 1], [1, 1]]
        self.alert = [0, 0]
        self.previous = None
        self.messages = 0

    def step(self, bit):
        if bit not in (0, 1) or type(bit) is not int:
            raise ValueError("PUBLIC_BIT_REQUIRED")
        if self.previous is None:
            self.previous = bit
            return None
        receiver = self.previous
        prediction = int(self.local[receiver][1] >= 2)
        error = int(prediction != bit)
        counter = self.local[receiver][1]
        self.local[receiver][1] = min(3,counter+1) if bit else max(0,counter-1)
        self.alert[receiver] = min(3,self.alert[receiver] + error) if error else max(0,self.alert[receiver]-1)
        if self.route and self.alert[receiver] == 3:
            # Public disagreement notification; no direct label sent to peer.
            other = 1-receiver
            self.alert[other] = min(3,self.alert[other]+1)
            self.messages += 1
        self.previous = bit
        return prediction

def compare():
    streams={"stable":[0]*24,"reversal":[0]*8+[1]*16,"recurrence":[0]*8+[1]*8+[0]*8,"alternating":[0,1]*12}
    results={}
    for name,seq in streams.items():
        routed,isolated=RoutedCells(True),RoutedCells(False)
        pr=[routed.step(x) for x in seq]
        pi=[isolated.step(x) for x in seq]
        # Routing only modulates alerts. Prediction equivalence is expected.
        assert pr == pi
        results[name]={"predictions_equal":True,"correct":sum(a==b for a,b in zip(pr,seq)),"routed_messages":routed.messages}
    return results

if __name__=="__main__":
    import json
    print(json.dumps(compare(),sort_keys=True))
