"""NCI-04G3: candidate-only learned local recovery with off-cell evidence.

Prelesion target feedback is sent only over immediate edges. Each surviving
neighbor learns its *own* conditional response evidence for a recipient; it
does not copy the recipient's weights. A lesion destroys the recipient's
local memory. Repair solicits local evidence from surviving neighbors, and
abstains when no neighbor is informative. No postlesion target access.
This is engineering feasibility, not accepted scientific evidence.
"""
import json

N=8
PER_CELL=4*N
MAX_PRELESION_EVENTS=128

class LocalReconstructor:
    def __init__(self, neighbors=None):
        if neighbors is None:
            neighbors=[((i-1)%N,(i+1)%N) for i in range(N)]
        if (type(neighbors) not in (tuple,list) or len(neighbors)!=N or
            any(type(e) not in (tuple,list) or len(e)!=2 or
                type(e[0])!=int or type(e[1])!=int or
                e[0]==e[1] or i in e or not 0<=e[0]<N or
                not 0<=e[1]<N for i,e in enumerate(neighbors))):
            raise ValueError("invalid neighbor graph")
        self.neighbors=tuple(tuple(x) for x in neighbors)
        # Each neighbor j stores its OWN learned target-prediction statistics.
        # No global learned route table. Fixed 8*32=256 counter bytes.
        self.cells=[bytearray(PER_CELL) for _ in range(N)]
        self.damaged=set()
        self.prelesion_events=0
        self.message_bytes=0
        self.repair_calls=0

    @staticmethod
    def _bits(values):
        if type(values) not in (list,tuple) or len(values)!=N or any(type(x)!=int or x not in (0,1) for x in values):
            raise ValueError("eight binary local observations required")

    @staticmethod
    def _slot(target,bit,outcome):
        return target*4+bit*2+outcome

    def observe_prelesion(self,bits,outcomes):
        self._bits(bits);self._bits(outcomes)
        if self.damaged:
            raise ValueError("postlesion labels are forbidden")
        if self.prelesion_events>=MAX_PRELESION_EVENTS:
            raise ValueError("prelesion data budget exhausted")
        # A message travels from the owner cell to EACH immediate neighbor.
        # Each neighbor updates its distinct locally held conditional evidence.
        for i,outcome in enumerate(outcomes):
            for j in self.neighbors[i]:
                slot=self._slot(i,bits[j],outcome)
                if self.cells[j][slot]==255:
                    raise ValueError("local counter saturated")
        for i,outcome in enumerate(outcomes):
            for j in self.neighbors[i]:
                self.cells[j][self._slot(i,bits[j],outcome)]+=1
                self.message_bytes+=2  # target ID + outcome; bits[j] local
        self.prelesion_events+=1

    def lesion(self,damaged):
        if type(damaged) not in (list,tuple) or not damaged or len(set(damaged))!=len(damaged) or any(type(i)!=int or not 0<=i<N for i in damaged):
            raise ValueError("invalid lesion")
        for i in damaged:
            self.cells[i]=bytearray(PER_CELL)  # destroy ONLY local custody
            self.damaged.add(i)

    def neighbor_message(self,target,j,bit):
        if j not in self.neighbors[target] or j in self.damaged:
            return None
        a=self.cells[j]
        y0=a[self._slot(target,bit,0)]
        y1=a[self._slot(target,bit,1)]
        a0=a[self._slot(target,0,0)]
        b0=a[self._slot(target,0,1)]
        a1=a[self._slot(target,1,0)]
        b1=a[self._slot(target,1,1)]
        p0=(b0+1)/(a0+b0+2)
        p1=(b1+1)/(a1+b1+2)
        observed=a0+b0+a1+b1
        informativeness=abs(p1-p0)*observed/(observed+4) if observed else 0.
        estimate=(y1+1)/(y0+y1+2)
        return (informativeness,estimate,observed)

    def reconstruct(self,bits,target):
        self._bits(bits)
        if type(target)!=int or target not in self.damaged:
            raise ValueError("reconstruction requires a damaged target")
        candidates=[]
        for j in self.neighbors[target]:
            self.message_bytes+=5  # bounded one-hop request and response
            reply=self.neighbor_message(target,j,bits[j])
            if reply is not None:
                candidates.append(reply)
        self.repair_calls+=1
        if not candidates:
            return (None,False)
        candidates.sort(key=lambda x:x[0],reverse=True)
        strength,estimate,seen=candidates[0]
        # Frozen candidate confidence gate. No postlesion label can tune it.
        if strength<=.15 or seen<8 or abs(estimate-.5)<=.15:
            return (None,False)
        return (int(estimate>.5),True)

    def snapshot(self):
        return json.dumps({
            "schema":"yggdrasil.nci04g.local-recovery.v1",
            "neighbors":self.neighbors,
            "cells":[list(c) for c in self.cells],
            "damaged":sorted(self.damaged),
            "prelesion_events":self.prelesion_events,
            "message_bytes":self.message_bytes,
            "repair_calls":self.repair_calls,
        },sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,payload):
        if type(payload)!=str or len(payload)>16384:
            raise ValueError("invalid snapshot size")
        doc=json.loads(payload)
        if type(doc)!=dict or set(doc)!={"schema","neighbors","cells","damaged","prelesion_events","message_bytes","repair_calls"} or doc["schema"]!="yggdrasil.nci04g.local-recovery.v1":
            raise ValueError("invalid snapshot schema")
        obj=cls(doc["neighbors"])
        if (type(doc["cells"])!=list or len(doc["cells"])!=N or
            any(type(c)!=list or len(c)!=PER_CELL or any(type(x)!=int or not 0<=x<=255 for x in c) for c in doc["cells"])):
            raise ValueError("invalid local memory")
        damaged=doc["damaged"]
        if type(damaged)!=list or damaged!=sorted(set(damaged)) or any(type(i)!=int or not 0<=i<N for i in damaged):
            raise ValueError("invalid destroyed cells")
        for k,maxval in (("prelesion_events",MAX_PRELESION_EVENTS),("message_bytes",10000000),("repair_calls",1000000)):
            if type(doc[k])!=int or not 0<=doc[k]<=maxval:
                raise ValueError("invalid usage counter")
        obj.cells=[bytearray(c) for c in doc["cells"]]
        obj.damaged=set(damaged)
        if any(any(obj.cells[i]) for i in obj.damaged):
            raise ValueError("damaged cell retained learned memory")
        obj.prelesion_events=doc["prelesion_events"]
        obj.message_bytes=doc["message_bytes"]
        obj.repair_calls=doc["repair_calls"]
        return obj
