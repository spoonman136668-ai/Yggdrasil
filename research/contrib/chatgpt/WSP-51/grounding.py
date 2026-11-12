"""WSP51 finite synthetic grounding; public DEV substrate, not general language."""
import hashlib
import json
import math

ROLES = ('noun', 'destination', 'verb')
SIZES = {'noun': 4, 'destination': 2, 'verb': 2}
BITS = {'noun': 2, 'destination': 1, 'verb': 1}


def pulse(tag, used):
    """First SHA256-derived byte, increment until unused; fixed before outcomes."""
    byte = hashlib.sha256(tag.encode('ascii')).digest()[0]
    while byte in used:
        byte = (byte + 1) & 255
    used.add(byte)
    return byte


class World:
    def __init__(self, cohort, seed, encoding):
        if cohort not in ('DEV', 'PRIMARY') or encoding not in ('identity', 'permuted', 'shifted'):
            raise ValueError('world')
        self.cohort, self.seed, self.encoding = cohort, seed, encoding
        used = set()
        self.forms = {}
        for role in ROLES:
            for meaning in range(SIZES[role]):
                self.forms[role, meaning] = pulse('WSP51|%s|%s|%s|%s|%s' % (cohort, seed, encoding, role, meaning), used)
        self.unknown = [pulse('WSP51|%s|%s|%s|unknown|%s' % (cohort, seed, encoding, j), used) for j in range(4)]
        self.synonym = pulse('WSP51|%s|%s|%s|synonym|0' % (cohort, seed, encoding), used)
        self.digest = hashlib.sha256(json.dumps(sorted((k[0], k[1], v) for k,v in self.forms.items()),separators=(',',':')).encode()).hexdigest()

    def evidence(self):
        """Only witnessed pointing and before/after consequences, no oracle lexical dict."""
        e = []
        for obj in range(4):
            e.append(('noun', self.forms['noun',obj], obj))
        for side in range(2):
            e.append(('destination', self.forms['destination',side], side))
        for v in range(2):
            for target in range(2):
                obj = (v+target)%4
                before = target if v else 1-target
                after = (1-target) if v else target
                # Source event reveals raw pulse and observable physical outcome, not verb ID.
                e.append(('verb_effect', self.forms['verb',v], obj, target, before, after, 1))
        return e

    @staticmethod
    def true_result(verb,obj,target,state):
        s = list(state)
        s[obj] = target if verb==0 else 1-target
        return tuple(s)


class NumericPlane:
    def __init__(self, width):
        self.width = width
        self.data = [0]*width
        self.seen = 0
        self.conflicts = 0
        self.updates = 0

    def observe(self, acoustic, value):
        if not isinstance(acoustic, int) or not 0 <= acoustic <= 255:
            raise ValueError('pulse')
        if not isinstance(value, int) or not 0 <= value < 1<<self.width:
            raise ValueError('concept')
        bit = 1<<acoustic
        previous = self.read(acoustic)
        if self.seen & bit and previous != value:
            self.conflicts |= bit
        if not self.seen & bit:
            for j in range(self.width):
                self.data[j] |= ((value>>j)&1)*bit
        self.seen |= bit
        self.updates += 1

    def read(self, acoustic):
        bit = 1<<acoustic
        if not self.seen & bit or self.conflicts & bit: return None
        return sum(((self.data[j]>>acoustic)&1)<<j for j in range(self.width))

    def dump(self):
        return {'width':self.width,'data':self.data,'seen':self.seen,'conflicts':self.conflicts,'updates':self.updates}

    @classmethod
    def load(cls, d):
        if not isinstance(d,dict) or set(d)!= {'width','data','seen','conflicts','updates'}:raise ValueError('plane schema')
        if d['width'] not in (1,2) or type(d['width']) is not int:raise ValueError('width')
        p=cls(d['width'])
        if type(d['seen']) is not int or d['seen']<0 or d['seen'].bit_length()>256: raise ValueError('seen')
        if type(d['conflicts']) is not int or d['conflicts']&~d['seen'] or d['conflicts']<0:raise ValueError('conflicts')
        if type(d['updates']) is not int or d['updates']<0:raise ValueError('updates')
        if not isinstance(d['data'],list) or len(d['data'])!=p.width:raise ValueError('data')
        if any(type(v) is not int or v<0 or v.bit_length()>256 or v&~d['seen'] for v in d['data']):raise ValueError('bits')
        p.data,p.seen,p.conflicts,p.updates=d['data'],d['seen'],d['conflicts'],d['updates']
        return p

class DirectLearner:
    def __init__(self):
        self.planes={r:NumericPlane(BITS[r]) for r in ROLES}
        self.source_events = 0
        self.sensor_resets = 0

    def observe(self,event):
        role,acoustic,*rest=event
        if role=='verb_effect':
            obj, target, before, after, resets = rest
            if not (0<=obj<4 and target in (0,1) and before in (0,1) and after in (0,1) and before != after):raise ValueError('physical event')
            meaning=0 if after==target else 1
            self.planes['verb'].observe(acoustic,meaning)
            self.sensor_resets+=resets
        else:
            self.planes[role].observe(acoustic,rest[0])
        self.source_events+=1

    def decode(self, utterance):
        if len(utterance)!=3:return None
        v=self.planes['verb'].read(utterance[0])
        o=self.planes['noun'].read(utterance[1])
        t=self.planes['destination'].read(utterance[2])
        return None if v is None or o is None or t is None else (v,o,t)

    def result(self,utterance,state):
        d=self.decode(utterance)
        return None if d is None else World.true_result(*d,state)

    def snapshot(self):
        body=json.dumps({'schema':'wsp51.numeric.grounding.v1','planes':{r:self.planes[r].dump() for r in ROLES},'source_events':self.source_events,'sensor_resets':self.sensor_resets},separators=(',',':'),sort_keys=True).encode()
        return body+b'|'+hashlib.sha256(body).hexdigest().encode()

    @classmethod
    def restore(cls,raw):
        try:
            body,digest=raw.rsplit(b'|',1)
            if hashlib.sha256(body).hexdigest().encode()!=digest:raise ValueError('digest')
            d=json.loads(body)
            if set(d)!={'schema','planes','source_events','sensor_resets'} or d['schema']!='wsp51.numeric.grounding.v1':raise ValueError('schema')
            if set(d['planes'])!=set(ROLES):raise ValueError('roles')
            obj=cls()
            obj.planes={r:NumericPlane.load(d['planes'][r]) for r in ROLES}
            for k in ('source_events','sensor_resets'):
                if type(d[k]) is not int or d[k]<0:raise ValueError('count')
                setattr(obj,k,d[k])
            if obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,KeyError,TypeError,AttributeError,IndexError):raise ValueError('invalid checkpoint') from None

class TableLearner:
    """Exact evidence-table control; zero unobserved semantics."""
    def __init__(self):
        self.maps={r:{} for r in ROLES}
    def observe(self,event):
        role,x,*args=event
        meaning=(0 if args[3]==args[1] else 1) if role=='verb_effect' else args[0]
        role='verb' if role=='verb_effect' else role
        old=self.maps[role].get(x,'missing')
        self.maps[role][x]=meaning if old=='missing' or old==meaning else None
    def decode(self,u):
        if len(u)!=3:return None
        a=[self.maps[r].get(x) for r,x in zip(('verb','noun','destination'),u)]
        return tuple(a) if all(v is not None for v in a) else None
    def result(self,u,s):
        d=self.decode(u)
        return None if d is None else World.true_result(*d,s)

class Erased:
    def observe(self,event):pass
    def decode(self,u):return None
    def result(self,u,s):return None

class TrainedLearner:
    """Independent supervised one-hot/softmax head; same observed meanings, fixed SGD budget."""
    def __init__(self):
        self.examples={r:[] for r in ROLES}
        self.weight={r:[[0.0]*SIZES[r] for _ in range(256)] for r in ROLES}
        self.seen={r:set() for r in ROLES}
        self.conflicts={r:set() for r in ROLES}
        self.training_updates=0
    def observe(self,event):
        role,x,*args=event
        meaning=(0 if args[3]==args[1] else 1) if role=='verb_effect' else args[0]
        role='verb' if role=='verb_effect' else role
        if x in self.seen[role] and any(v!=meaning for xx,v in self.examples[role] if xx==x):self.conflicts[role].add(x)
        self.seen[role].add(x)
        self.examples[role].append((x,meaning))
    def train(self):
        for role in ROLES:
            for _ in range(100):
                for x,y in self.examples[role]:
                    w=self.weight[role][x]
                    scale=max(w)
                    exp=[math.exp(v-scale) for v in w]
                    total=sum(exp)
                    for j in range(len(w)):
                        w[j]+=0.2*((j==y)-exp[j]/total)
                        self.training_updates+=1
    def decode(self,u):
        if len(u)!=3:return None
        out=[]
        for role,x in zip(('verb','noun','destination'),u):
            if x not in self.seen[role] or x in self.conflicts[role]:return None
            w=self.weight[role][x]
            out.append(max(range(len(w)),key=lambda j:w[j]))
        return tuple(out)
    def result(self,u,s):
        d=self.decode(u)
        return None if d is None else World.true_result(*d,s)
