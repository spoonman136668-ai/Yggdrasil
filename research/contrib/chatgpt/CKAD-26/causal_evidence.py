"""Frozen exact-rational evidence for competing public causal explanations.

Marginal Beta(1,1) likelihood of a sequential Bernoulli evidence group.
A change hypothesis splits the previous 32 public action-consequence
observations into two windows of 16. The stable hypothesis pools both
windows. The split-vs-shared Bayes factor is computed exactly, with no
access to source-side phase labels, hidden variables or held-out rewards.

This is a conventional causal-conditional statistical challenger, NOT
proof of native model learning or a new Yggdrasil controller.
"""
from fractions import Fraction
from hashlib import sha256
from math import factorial

WINDOW=32
HALF=16
THRESHOLD=16
PERSISTENCE=2
SPACING=8
MODES=("causal_bayes","unconditional_bayes","native_joint","random_alarm")


def require(condition,reason):
    if not condition:
        raise ValueError("CKAD26_EVIDENCE_"+reason)


def _beta(positive,negative):
    require(type(positive) is int and type(negative) is int
            and positive>=0 and negative>=0,"NONNEGATIVE_COUNTS")
    return Fraction(factorial(positive)*factorial(negative),
                    factorial(positive+negative+1))


def marginal_bayes_factor(observations,feature_names,target):
    """Strictly ordered, exact conditional B_split/B_shared, no fitting on future."""
    require(type(observations) is list and len(observations)==WINDOW,"EXACT_WINDOW")
    require(target in ("next_state","reward"),"TARGET")
    require(type(feature_names) is tuple,"FEATURES")
    counts={}
    for i,row in enumerate(observations):
        require(set(row)=={"public_state","first_action","next_state",
                          "second_action","reward"},"PUBLIC_ONLY")
        require(all(type(x) is int and x in (0,1) for x in row.values()),
                "BINARY_ONLY")
        key=tuple(row[name] for name in feature_names)
        if key not in counts: counts[key]=[[0,0],[0,0]]
        counts[key][0 if i<HALF else 1][row[target]]+=1
    value=Fraction(1)
    for pair in counts.values():
        a,b=pair
        value *= (_beta(a[1],a[0])*_beta(b[1],b[0]) /
                  _beta(a[1]+b[1],a[0]+b[0]))
    return value


class ChangeEvidence:
    """One chosen detector, all public source events passed one at a time."""
    def __init__(self,mode,namespace):
        require(mode in MODES and type(namespace) is str and namespace,"MODE")
        self.mode=mode
        self.namespace=namespace
        self.rows=[]
        self.previous=448
        self.strength=0
        self.alarms=[]

    def observe(self,identifier,count,row):
        require(type(identifier) is str and len(identifier)==64
                and all(x in "0123456789abcdef" for x in identifier),
                "PUBLIC_IDENTIFIER")
        require(type(count) is int and count==448+len(self.rows)+1,
                "SEQUENTIAL_COUNT")
        require(set(row)=={"public_state","first_action","next_state",
                          "second_action","reward"} and
                all(type(x) is int and x in (0,1) for x in row.values()),
                "ONLY_PUBLIC_ACTION_CONSEQUENCES")
        self.rows.append(row)
        if self.mode=="random_alarm":
            if count-self.previous<SPACING:return
            draw=sha256(f"ckad26-random-v1/{self.namespace}/{count}".encode()).digest()
            if draw[0]<4:
                self.alarms.append({"event_id":identifier,"evidence_count":count,
                                    "evidence":"label_free_hash","score":[1,1]})
                self.previous=count
            return
        if len(self.rows)<WINDOW:return
        window=self.rows[-WINDOW:]
        if self.mode=="causal_bayes":
            trans=marginal_bayes_factor(window,("public_state","first_action"),"next_state")
            reward=marginal_bayes_factor(window,
                ("public_state","first_action","next_state","second_action"),"reward")
        elif self.mode=="unconditional_bayes":
            trans=marginal_bayes_factor(window,(),"next_state")
            reward=marginal_bayes_factor(window,(),"reward")
        else:
            return  # original native joint is handled by unchanged independent reference monitor
        strongest=max(trans,reward)
        if strongest>=THRESHOLD and count-self.previous>=SPACING:
            self.strength+=1
        else:
            self.strength=0
        if self.strength>=PERSISTENCE:
            cause="transition" if trans>=reward else "reward"
            self.alarms.append({"event_id":identifier,"evidence_count":count,
                                "evidence":cause,"score":[strongest.numerator,
                                                         strongest.denominator]})
            self.previous=count
            self.strength=0

    def summary(self):
        return {"mode":self.mode,"alarms":self.alarms,"observations":len(self.rows)}
