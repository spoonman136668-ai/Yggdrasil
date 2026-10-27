"""Public two-stage binary composition learned from completed interactions.

Two independent pair-local cells retain observed intermediate outcomes;
an exchange cell learns a binary affine relation between their messages and
the final public consequence. Coefficients are solved from observed outcomes
by finite-field elimination, not supplied by the environment.
No transformer, tokens, learned shared weights, or privileged task identity.
"""
class PairCell:
    def __init__(self):
        self.examples={}
        self.observations=0

    def observe(self,pair,outcome):
        if (type(pair) is not tuple or len(pair)!=2 or
            any(type(b) is not bool for b in pair) or type(outcome) is not bool):
            raise ValueError("PUBLIC_PAIR_REQUIRED")
        if pair not in self.examples and len(self.examples)>=4:
            raise ValueError("PAIR_CELL_CAP")
        bucket=self.examples.setdefault(pair,[0,0])
        bucket[int(outcome)]+=1
        self.observations+=1

    def predict(self,pair):
        bucket=self.examples.get(pair)
        if bucket is None or sum(bucket)<2 or bucket[0]==bucket[1]:
            return None
        return bucket[1]>bucket[0]

class AffineMessageCell:
    def __init__(self):
        self.equations={}
        self.observations=0

    def observe(self,inputs,outcome):
        if (type(inputs) is not tuple or len(inputs)!=2 or
            any(type(x) is not bool for x in inputs) or type(outcome) is not bool):
            raise ValueError("PUBLIC_COMPOSITION_REQUIRED")
        if inputs not in self.equations and len(self.equations)>=4:
            raise ValueError("AFFINE_MESSAGE_CAP")
        bucket=self.equations.setdefault(inputs,[0,0])
        bucket[int(outcome)]+=1
        self.observations+=1

    def coefficients(self):
        # Solve a0 XOR (a1 & message0) XOR (a2 & message1) = public result.
        rows=[]
        for (a,b),counts in self.equations.items():
            if sum(counts)<2 or counts[0]==counts[1]:
                continue
            rows.append([1,int(a),int(b),int(counts[1]>counts[0])])
        pivots={}
        for column in range(3):
            idx=next((i for i in range(len(rows)) if rows[i][column]),None)
            if idx is None: return None
            pivot=rows.pop(idx)
            pivots[column]=pivot
            rows=[[v^(pivot[j] if v[column] else 0) for j,v in enumerate(v)]
                  for v in rows]
            for prev in pivots:
                if prev!=column and pivots[prev][column]:
                    pivots[prev]=[v^pivot[j] for j,v in enumerate(pivots[prev])]
        if any(row[3] for row in rows):
            return None
        return tuple(bool(pivots[i][3]) for i in range(3))

    def predict(self,inputs):
        coefficients=self.coefficients()
        if coefficients is None:return None
        a,b=inputs
        return bool(coefficients[0] ^ (coefficients[1] and a) ^
                    (coefficients[2] and b))

class CompositionalLocalCells:
    def __init__(self):
        self.pair_cells=(PairCell(),PairCell())
        self.exchange=AffineMessageCell()

    def observe_pair(self,index,pair,public_result):
        if type(index) is not int or index not in (0,1):
            raise ValueError("LOCAL_PAIR_INDEX")
        self.pair_cells[index].observe(pair,public_result)

    def observe_final(self,bits,public_result):
        self._bits(bits)
        messages=self.messages(bits)
        if None in messages:
            raise ValueError("PUBLIC_SUBCAUSE_NOT_LEARNED")
        self.exchange.observe(messages,public_result)

    @staticmethod
    def _bits(bits):
        if type(bits) is not tuple or len(bits)!=4 or any(type(v) is not bool for v in bits):
            raise ValueError("PUBLIC_FOUR_BITS_REQUIRED")

    def messages(self,bits):
        self._bits(bits)
        return (self.pair_cells[0].predict(bits[:2]),
                self.pair_cells[1].predict(bits[2:]))

    def predict(self,bits):
        messages=self.messages(bits)
        if None in messages:return None
        return self.exchange.predict(messages)

    def observations(self):
        return sum(cell.observations for cell in self.pair_cells)+self.exchange.observations
