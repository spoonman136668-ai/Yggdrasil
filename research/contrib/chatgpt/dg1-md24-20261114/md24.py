"""DG1-MD24 public-observation effect-memory transfer; toy-only module.

The obstacle is NOT identified by a literal ball ID, environment name, mission,
global map or privileged agent position. Its relocatability is tested through a
general pickup/drop effect learned on disjoint earlier-family trajectories.
The actual navigation/relocation motion is still scripted and must not be
misreported as a learned route planner or a native model.
"""
import hashlib
import importlib.util
import json
import heapq
import zlib
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"dg1-md23-20261114"/"md23.py"
spec=importlib.util.spec_from_file_location("md24_pinned_md23",str(BASE))
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m=d.m

FREEZE="81e167c174097df83e50e57e0ae6494231cbd032"
PARENT="9b0557f2cfe829d7991fd41c9f131c41a141626f"
SCHEMA="yggdrasil.dg1-md24-original.v1"
ARMS=("learned_transfer","permuted_effect","blind_generic",
      "md23_causal","tabular_q","recurrent_imitation")
TOY=(11,17,19,23,29,31)
TRAIN_DOOR="MiniGrid-DoorKey-6x6-v0"
TRAIN_BOX="MiniGrid-UnlockPickup-v0"
NOVEL="MiniGrid-BlockedUnlockPickup-v0"
SIZED="MiniGrid-DoorKey-8x8-v0"
COLD=TRAIN_DOOR
TRAIN_SEEDS=tuple(range(990001,990025))
INTERFERENCE_SEEDS=tuple(range(991001,991013))
COLD_SEEDS=tuple(range(992001,992013))
SIZE_SEEDS=tuple(range(993001,993013))
NOVEL_SEEDS=tuple(range(994001,994013))


def manifest():
    return json.loads(Path(__file__).with_name("prereg.json").read_text())


def verify_manifest():
    x=manifest()
    f=x["frozen_design"]
    if (x["experiment_id"]!="DG1-MD24-20261114" or
        x["base_commit"]!=PARENT or
        x["status"]!="PREREGISTRATION_ONLY_NO_PRIMARY_FIRST_USE" or
        f["arms"]!=list(ARMS) or
        f["toy_development_seeds"]!=list(TOY) or
        f["train_seeds"]!=[990001,990024] or
        f["novel_family_seeds"]!=[994001,994012] or
        f["max_episode_actions"]!=256 or
        f["total_original_episodes"]!=348 or
        f["max_charged_env_steps"]!=89088):
        raise AssertionError("MD24_FROZEN_DESIGN_DRIFT")
    regs=TRAIN_SEEDS+INTERFERENCE_SEEDS+COLD_SEEDS+SIZE_SEEDS+NOVEL_SEEDS
    if len(regs)!=len(set(regs)) or set(regs)&set(TOY):
        raise AssertionError("MD24_SEED_CUSTODY_COLLISION")
    return x


def toy_only(seed):
    if type(seed) is not int or seed not in TOY:
        raise AssertionError("MD24_REGISTERED_SEED_USE_FORBIDDEN_BEFORE_PR_OPENED")


def versions():
    import minigrid
    import gymnasium
    import numpy
    if (minigrid.__version__,gymnasium.__version__,numpy.__version__)!=(
       "3.2.0","1.4.0","2.3.4"):
        raise AssertionError("MD24_PINNED_DEPENDENCY_DRIFT")


class TransferPolicy(d.GraphPolicy):
    """Three exact matched structural arms, same scripted motion, different edge gate."""
    KINDS=("learned_transfer","permuted_effect","blind_generic")

    def __init__(self,kind):
        if kind not in self.KINDS: raise ValueError("MD24_UNKNOWN_TRANSFER_KIND")
        self.effects={"pickup_clear":0,"drop_place":0,"toggle_shift":0}
        self.effect_trials={"pickup":0,"drop":0,"toggle":0}
        super().__init__("causal_graph",probe_first=True)
        self.kind=kind
        self.start(11)

    def start(self,seed):
        super().start(seed)
        self.phase=None
        self.unknown_attempts=0
        self.causal_transfer_uses=0
        self.new_obstacle_cleared=0
        self.resolved=set()
        self.failed=set()
        self.last_opaque=None
        self.relobj=None
        self.task_family_box=False

    @staticmethod
    def opaque_type(t):
        from minigrid.core.constants import OBJECT_TO_IDX
        safe={"unseen","empty","wall","floor","door","key","box","goal",
              "lava","agent"}
        # A candidate can probe a novel ID, but no particular ID is known here.
        return t not in {OBJECT_TO_IDX[k] for k in safe if k in OBJECT_TO_IDX}

    def gate(self):
        # Learn pickup->clears-cell and drop->places-on-empty from physical
        # examples. An equal-capacity permuted edge points to absent toggle
        # relocation evidence. A blind generic operator uses no training edge.
        if self.kind=="blind_generic":return True
        if self.kind=="permuted_effect":
            return self.effects["toggle_shift"]>=8
        return (self.effects["pickup_clear"]>=6 and
                self.effects["drop_place"]>=6)

    def feedback(self,before,action,after,reward,training=False):
        from minigrid.core.constants import OBJECT_TO_IDX
        old=m.front_type(before)
        new=m.front_type(after)
        pre=int(m.objects(before)[3,6])
        post=int(m.objects(after)[3,6])
        empty=OBJECT_TO_IDX["empty"]
        pickup=(action==3 and old!=empty and new==empty
                and pre==empty and post==old)
        drop=(action==4 and old==empty and new==pre
              and pre!=empty and post==empty)
        if training:
            if action==3:self.effect_trials["pickup"]+=1
            if action==4:self.effect_trials["drop"]+=1
            if action==5:self.effect_trials["toggle"]+=1
            if pickup:self.effects["pickup_clear"]+=1
            if drop:self.effects["drop_place"]+=1
        super().feedback(before,action,after,reward,training=training)
        # The public agent-centered carrying pixel is the only confirmation.
        if not training and self.last_opaque is not None and action==3:
            if pickup and old==self.last_opaque:
                self.relobj=old
                self.phase="forward"
                self.new_obstacle_cleared+=1
                if self.kind=="learned_transfer":
                    self.causal_transfer_uses+=1
            else:
                fx,fy=self.vectors(int(before["direction"]))[0]
                self.failed.add((self.pose[0]+fx,self.pose[1]+fy))
            self.last_opaque=None
        if not training and action==4 and drop and self.relobj==new:
            fx,fy=self.vectors(int(before["direction"]))[0]
            self.resolved.add((self.pose[0]+fx,self.pose[1]+fy))
            self.relobj=None

    def target_action(self):
        """BFS over visible own map and pose orientation, to face opaque tile."""
        start=(self.pose[0],self.pose[1],self.current_dir)
        q=[(0,0,start,())]
        visited={start}
        seq=0
        while q:
            depth,_,state,acts=heapq.heappop(q)
            if depth>90:break
            x,y,heading=state
            fx,fy=self.vectors(heading)[0]
            front=(x+fx,y+fy)
            value=self.tiles.get(front)
            if (value is not None and self.opaque_type(value) and
                front not in self.resolved and front not in self.failed):
                return acts[0] if acts else 3
            for action,next_state in ((0,(x,y,(heading-1)%4)),
                                      (1,(x,y,(heading+1)%4)),
                                      (2,(x+fx,y+fy,heading))):
                if action==2 and not self.traversable(front):
                    continue
                if next_state in visited:continue
                visited.add(next_state)
                seq+=1
                heapq.heappush(q,(depth+1,seq,next_state,acts+(action,)))
        return None

    def act(self,obs,t):
        from minigrid.core.constants import OBJECT_TO_IDX
        if self.phase is not None:
            step=self.phase
            # Relocate to an actual empty side cell rather than dropping the
            # obstruction back onto the approach to the locked door.
            if step=="forward":
                self.phase="turn_right";return 2
            if step=="turn_right":
                self.phase="right_side";return 1
            if step=="right_side":
                if m.front_type(obs)==OBJECT_TO_IDX["empty"]:
                    self.phase="restore_from_right";return 4
                self.phase="turn_forward";return 0
            if step=="turn_forward":
                self.phase="turn_left";return 0
            if step=="turn_left":
                self.phase="left_side";return 0
            if step=="left_side":
                if m.front_type(obs)==OBJECT_TO_IDX["empty"]:
                    self.phase="restore_from_left";return 4
                # Both side cells are blocked; abandon without fake success.
                self.phase=None
            if step=="restore_from_right":
                self.phase=None;return 0
            if step=="restore_from_left":
                self.phase=None;return 1
        self.current_dir=int(obs["direction"])
        self.ingest(obs)
        if self.gate() and not self.has_key and self.relobj is None:
            candidate=self.target_action()
            if candidate is not None:
                if candidate==3:
                    self.last_opaque=m.front_type(obs)
                    self.unknown_attempts+=1
                return candidate
        return super().act(obs,t)

    def dump(self):
        x=super().dump()
        x.update(kind=self.kind,effects=self.effects,effect_trials=self.effect_trials)
        return x

    def load(self,x):
        super().load(x)
        if set(x["effects"])!=set(self.effects) or set(x["effect_trials"])!=set(self.effect_trials):
            raise AssertionError("MD24_CHECKPOINT_EFFECT_SCHEMA_CHANGED")
        self.effects=x["effects"]
        self.effect_trials=x["effect_trials"]


def make_agent(kind):
    if kind in TransferPolicy.KINDS:return TransferPolicy(kind)
    if kind=="md23_causal":return d.GraphPolicy("causal_graph",probe_first=True)
    if kind in ("tabular_q","recurrent_imitation"):return m.make_agent(kind)
    raise ValueError("MD24_UNKNOWN_CONTROL")


def save(agent):
    state=agent.dump()
    if isinstance(agent,d.GraphPolicy) and not isinstance(agent,TransferPolicy):
        state=dict(state,kind="md23_causal")
    data=zlib.compress(m.canon(state).encode(),9)
    if len(data)>65536:raise AssertionError("MD24_CHECKPOINT_CAP")
    return data


def restore(data):
    state=json.loads(zlib.decompress(data))
    obj=make_agent(state["kind"])
    if state["kind"]=="md23_causal":
        obj.load(dict(state,kind="causal_graph"))
    else:obj.load(state)
    if save(obj)!=data:raise AssertionError("MD24_NONCANONICAL_RESTORE")
    return obj


def physical_teacher(env,seed,permit_registered=False):
    if not permit_registered:toy_only(seed)
    teacher=d.GraphPolicy("fixed_scripted",probe_first=True)
    ep=m.make_trace(env,seed,teacher)
    if ep["steps"]!=len(ep["transitions"]) or not 0<ep["steps"]<=256:
        raise AssertionError("MD24_UNPAID_PHYSICAL_ACTION")
    return ep


def train_shared(agents,episode):
    seed=episode["seed"]
    keys=ARMS[:4]
    for key in keys:
        agents[key].start(seed)
        agents[key].training_episodes+=1
    previous=6
    sequence=[]
    for t,(before,action,reward,after,terminal) in enumerate(episode["transitions"]):
        for key in keys:
            agents[key].feedback(before,action,after,reward,training=True)
        agents["tabular_q"].feedback(before,action,after,reward,training=True,terminal=terminal)
        sequence.append(m.public_features(before,previous,t))
        sequence=sequence[-m.HISTORY:]
        agents["recurrent_imitation"].learn(sequence,action,2. if episode["success"] else 1.)
        previous=action


def score_toy(agents,env,seeds):
    for seed in seeds:toy_only(seed)
    frozen={name:save(agent) for name,agent in agents.items()}
    metrics={}
    for name,agent in agents.items():
        rows=[]
        for seed in seeds:
            ep=m.make_trace(env,seed,agent)
            receipt={"seed":seed,"success":ep["success"],
                     "discounted_reward":ep["discounted_reward"],
                     "steps":ep["steps"],"sha256":ep["sha256"],
                     "new_obstacle_cleared":getattr(agent,"new_obstacle_cleared",0),
                     "causal_edge_uses":getattr(agent,"causal_transfer_uses",0)}
            if seed==11 and name in ("blind_generic","learned_transfer"):
                receipt["toy_debug"]=[
                    {"t":i,"action":action,"front":m.front_type(before),
                     "carry":int(m.objects(before)[3,6]),
                     "front_after":m.front_type(after),
                     "carry_after":int(m.objects(after)[3,6])}
                    for i,(before,action,reward,after,done) in
                    enumerate(ep["transitions"])
                    if i<85 and (i<35 or action in (3,4,5))]
            rows.append(receipt)
        if frozen[name]!=save(agent):raise AssertionError("MD24_HELDOUT_CHECKPOINT_DRIFT")
        metrics[name]=rows
    return metrics


def toy_study():
    verify_manifest()
    versions()
    agents={name:make_agent(name) for name in ARMS}
    training={"door_goals":0,"box_goals":0,"charged":0}
    for env,label in ((TRAIN_DOOR,"door"),(TRAIN_BOX,"box")):
        for seed in (11,17,19,23,29,31):
            ep=physical_teacher(env,seed)
            train_shared(agents,ep)
            training[label+"_goals"]+=ep["success"]
            training["charged"]+=ep["steps"]
    a,b=agents["learned_transfer"],agents["permuted_effect"]
    if a.effects!=b.effects or a.effect_trials!=b.effect_trials:
        raise AssertionError("MD24_NOT_MATCHED_TRAINING")
    snapshots={k:save(v) for k,v in agents.items()}
    if any(save(restore(value))!=value for value in snapshots.values()):
        raise AssertionError("MD24_BAD_COLD_SNAPSHOT")
    toy=score_toy(agents,NOVEL,(11,17,19,23,29,31))
    return {"schema":"yggdrasil.dg1-md24-toy.v1","classification":"TOY_ONLY",
            "original_seeds_touched":False,"training":training,
            "learned_effects":a.effects,"control_effects":b.effects,
            "novel":{k:{"goals":sum(x["success"] for x in rows),
                        "charged_steps":sum(x["steps"] for x in rows),
                        "cleared":sum(x["new_obstacle_cleared"] for x in rows),
                        "edge_used":sum(x["causal_edge_uses"] for x in rows)}
                     for k,rows in toy.items()},
            "novel_traces":toy,
            "checkpoint_sha256":{k:hashlib.sha256(v).hexdigest()
                                   for k,v in snapshots.items()}}


if __name__=="__main__":
    print(m.canon(toy_study()))
