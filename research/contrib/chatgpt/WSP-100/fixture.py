"""WSP100: fixture-only multivalued causal environment; no original-world path.

Only the eight DEV identities exist. Never treat fixture program parameters as
an allowed input to learners. Original scientific source remains unimplemented.
"""
from __future__ import annotations
import hashlib
import json

CHANNELS = 6
VALUES = 4
HIDDEN = 2
ACTIONS = 4
STEPS = 4
PASSIVE_EPISODES = 24
INVESTIGATIVE_EPISODES = 8


def rank(fid: int, stream: str, index: int) -> int:
    return int.from_bytes(hashlib.sha256(
        f"WSP100|v1|FIXTURE|{fid}|{stream}|{index}".encode("ascii")
    ).digest(), "big")


def valid_visible(x):
    if not isinstance(x, (tuple, list)) or len(x) != CHANNELS or any(
        type(v) is not int or not 0 <= v < VALUES for v in x
    ):
        raise ValueError("six integer four-valued visible observations required")
    return tuple(x)


def digits4(code: int):
    if type(code) is not int or not 0 <= code < 4096:
        raise ValueError("invalid six-channel base4 code")
    return tuple((code >> (2*j)) & 3 for j in range(CHANNELS))


def identity_code(x):
    x = valid_visible(x)
    return sum(v << (2*i) for i,v in enumerate(x))


def canonical_digest(data):
    return hashlib.sha256(json.dumps(
        data, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _op(f: int, a: int, b: int):
    if f == 0: return (a+b) % 4
    if f == 1: return a ^ b
    if f == 2: return a if b % 2 == 0 else 3-a
    if f == 3: return (a*b+b) % 4
    raise ValueError("invalid fixture operator")


class FixtureWorld:
    """Source oracle; only reset and step may be used by source gathering."""
    def __init__(self, fixture_id: int, *, _no_latches: bool = False):
        if type(fixture_id) is not int or not 0 <= fixture_id < 8:
            raise PermissionError("WSP100 original PUBLIC/RESERVED worlds unavailable")
        if type(_no_latches) is not bool:
            raise ValueError("invalid evaluator-only ablation")
        self.fixture_id = fixture_id
        self._program = tuple(rank(fixture_id, "PARAM-"+k, 0) % 4
            for k in ("FAMILY","WIRING","TRIGGER","PHASE"))
        self._no_latches = _no_latches
        self.reset((0,) * CHANNELS)

    def reset(self, visible):
        self._visible = valid_visible(visible)
        self._hidden = (0, 0)
        self._steps = 0
        return self._visible

    def step(self, action: int):
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError("action must be an integer 0..3")
        if self._steps >= STEPS:
            raise ValueError("fixture episode budget exhausted")
        f,w,t,p = self._program
        x = self._visible
        h = self._hidden
        outgoing = []
        for i in range(CHANNELS):
            a, b = x[(i+w)%CHANNELS], x[(i+w+1)%CHANNELS]
            c = _op(f, a, b)
            v = (_op((f+1+i%3)%4, c, x[(i+3)%CHANNELS])
                 + p*(1+i%2)) % VALUES
            if i < 4 and not self._no_latches:
                v = (v + h[i%HIDDEN]) % VALUES
            outgoing.append(v)
        nxt_h = list(h)
        if not self._no_latches:
            for j in range(HIDDEN):
                condition = (x[(w+j)%CHANNELS] +
                    x[(w+j+2)%CHANNELS] + p + j) % 2 == 1
                if action == (t+j) % ACTIONS and condition:
                    nxt_h[j] = (h[j] + 1 + (p+j)%3) % VALUES
        self._visible = tuple(outgoing)
        self._hidden = tuple(nxt_h)
        self._steps += 1
        return {"observation": self._visible,
                "reward": int((self._visible[0]+self._visible[1])%4 == 3)}


def _episode(world, initial, policy):
    x = world.reset(initial)
    rows = []
    for step in range(STEPS):
        action = policy(step, x)
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError("invalid source action")
        result = world.step(action)
        if set(result) != {"observation", "reward"}:
            raise ValueError("unexpected hidden oracle field")
        y = valid_visible(result["observation"])
        reward = int((y[0]+y[1])%4 == 3)
        if result["reward"] != reward:
            raise ValueError("reward inconsistent with visible result")
        rows.append((x, action, y, reward))
        x = y
    return tuple(rows)


class _CoveragePolicy:
    """Source-only action selector; no hidden state or program inputs."""
    def __init__(self, passive, fixture_id):
        self.fixture_id = fixture_id
        self.seen = set()
        self.count = [0,0,0,0]
        for episode in passive:
            for x, a, _y, _reward in episode:
                self.record(x,a)

    def record(self,x,a):
        self.seen.add((x,a))
        self.count[a] += 1

    def choose(self, global_step, visible):
        options=[]
        for a in range(ACTIONS):
            options.append((
                int((visible,a) in self.seen),
                self.count[a],
                rank(self.fixture_id,"ACTIVE-TIE",global_step*ACTIONS+a),
                a,
            ))
        return min(options)[-1]


def sources(fixture_id):
    """Exactly 24 passive + 8 active + 8 random 4-step episodes."""
    if type(fixture_id) is not int or not 0 <= fixture_id < 8:
        raise PermissionError("only WSP100 DEV fixture sources are permitted")
    w = FixtureWorld(fixture_id)
    passive = tuple(
        _episode(w, digits4(rank(fixture_id,"PASSIVE-INIT",i)%4096),
                 lambda step,_x,i=i: rank(
                   fixture_id,"PASSIVE-ACT",4*i+step)%ACTIONS)
        for i in range(PASSIVE_EPISODES))
    policy=_CoveragePolicy(passive,fixture_id)
    active_world=FixtureWorld(fixture_id)
    random_world=FixtureWorld(fixture_id)
    active,random=[],[]
    for i in range(INVESTIGATIVE_EPISODES):
        initial=digits4(rank(fixture_id,"INVESTIGATE-INIT",i)%4096)
        def choose(t,x,i=i):
            action=policy.choose(4*i+t,x)
            # A source-only choice is made BEFORE the environment transition.
            return action
        # Record the visible/action pair after the outcome is acquired.
        x=active_world.reset(initial)
        rows=[]
        for t in range(STEPS):
            a=choose(t,x)
            reply=active_world.step(a)
            y=valid_visible(reply["observation"])
            reward=int((y[0]+y[1])%4 == 3)
            if set(reply)!={"observation","reward"} or reward!=reply["reward"]:
                raise ValueError("oracle/reward leakage")
            rows.append((x,a,y,reward))
            policy.record(x,a)
            x=y
        active.append(tuple(rows))
        random.append(_episode(
            random_world,initial,
            lambda step,_x,i=i:rank(fixture_id,"RANDOM-ACT",4*i+step)%ACTIONS))
    record={"schema":"wsp100.fixture-source.v1","fixture_id":fixture_id,
            "passive":passive,"active":tuple(active),"random":tuple(random)}
    return {**record,"source_sha256":canonical_digest(record)}


def validate_sources(bundle):
    if not isinstance(bundle,dict) or set(bundle)!={"schema","fixture_id","passive","active","random","source_sha256"}:
        raise ValueError("invalid bundle schema")
    if bundle["schema"]!="wsp100.fixture-source.v1" or type(bundle["fixture_id"]) is not int or not 0<=bundle["fixture_id"]<8:
        raise ValueError("original source use forbidden")
    if len(bundle["passive"])!=24 or len(bundle["active"])!=8 or len(bundle["random"])!=8:
        raise ValueError("source episode budget drift")
    for name in ("passive","active","random"):
        for episode in bundle[name]:
            if len(episode)!=4:
                raise ValueError("not four source transitions")
            for step,(x,a,y,reward) in enumerate(episode):
                x,y=valid_visible(x),valid_visible(y)
                if type(a) is not int or not 0<=a<4 or type(reward) is not int or reward!=int((y[0]+y[1])%4==3):
                    raise ValueError("invalid source tuple")
                if step and x!=episode[step-1][2]:
                    raise ValueError("episode state continuity drift")
    if any(a[0][0]!=b[0][0] for a,b in zip(bundle["active"],bundle["random"])):
        raise ValueError("active/random episode starting states differ")
    raw={k:bundle[k] for k in ("schema","fixture_id","passive","active","random")}
    if canonical_digest(raw)!=bundle["source_sha256"]:
        raise ValueError("source seal mismatch")
    return True


def heldout_plan(bundle):
    validate_sources(bundle)
    fid=bundle["fixture_id"]
    source_starts={ep[0][0] for key in ("passive","active","random")
                   for ep in bundle[key]}
    states=[digits4(x) for x in range(4096)
            if digits4(x) not in source_starts]
    states.sort(key=lambda x: rank(fid,"HELDOUT-INIT",identity_code(x)))
    plan=[]
    for i,initial in enumerate(states[:12]):
        a=rank(fid,"HELDOUT-A",i)%ACTIONS
        b=(a+1+rank(fid,"HELDOUT-B",i)%3)%ACTIONS
        second=rank(fid,"HELDOUT-C",3*i+1)%ACTIONS
        third=rank(fid,"HELDOUT-C",3*i+2)%ACTIONS
        plan.append((initial,(a,second,third),(b,second,third)))
    return {"schema":"wsp100.fixture-heldout-plan.v1",
            "fixture_id":fid,"source_sha256":bundle["source_sha256"],
            "targets":tuple(plan),"plan_sha256":canonical_digest(plan)}
