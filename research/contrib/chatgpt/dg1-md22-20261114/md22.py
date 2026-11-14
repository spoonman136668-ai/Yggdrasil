"""DG1-MD22 real MiniGrid key/locked-door intervention research.
Frozen preregistration separate ancestor; all registered seeds first-used on draft PR opened only.
This is a rule-scaffolded partial-observation action learner, NOT native AGI.
"""
import hashlib
import importlib.util
import json
import heapq
import statistics
import zlib
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"dg1-mg20-20261113"/"mg20.py"
spec=importlib.util.spec_from_file_location("md22_exact_mg20",str(BASE))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FREEZE="ada17791db5ba3892f2d8012e38dffd024b55dbb"
PARENT="8edf7b5563f5a37f3284a96354c9985266d58c18"
MANIFEST_HASH="839a7d4f6e6731d93b012527bb1fdde9ddeaa9f18d541f87d73a4a96f542fbb7"
SCHEMA="yggdrasil.dg1-md22-original.v1"
TRAIN_SEEDS=tuple(range(930001,930025))
INTERFERENCE_SEEDS=tuple(range(940001,940013))
COLD_SEEDS=tuple(range(950001,950013))
SIZE_SEEDS=tuple(range(960001,960013))
FAMILY_SEEDS=tuple(range(970001,970013))
TRAIN_ENVS=("MiniGrid-DoorKey-5x5-v0","MiniGrid-DoorKey-6x6-v0")
INTERFERENCE_ENV="MiniGrid-Empty-6x6-v0"
COLD_ENV="MiniGrid-DoorKey-6x6-v0"
SIZE_ENV="MiniGrid-DoorKey-8x8-v0"
FAMILY_ENV="MiniGrid-UnlockPickup-v0"
ARMS=("causal_affordance","sham_affordance","reactive","tabular_q","recurrent_imitation")
MAX_STEPS=256
m.MAX_STEPS=MAX_STEPS  # same fixed normalized clock and action cap for all arms


def manifest():
    return {"schema":"yggdrasil.dg1-md22-keydoor-actions.v1",
            "train_seeds":list(TRAIN_SEEDS),
            "interference_seeds":list(INTERFERENCE_SEEDS),
            "cold_seeds":list(COLD_SEEDS),
            "unseen_size_seeds":list(SIZE_SEEDS),
            "unseen_family_seeds":list(FAMILY_SEEDS),
            "train_envs":list(TRAIN_ENVS),
            "interference_env":INTERFERENCE_ENV,
            "cold_env":COLD_ENV,
            "unseen_size_env":SIZE_ENV,
            "unseen_family_env":FAMILY_ENV,
            "max_steps":MAX_STEPS,"arms":list(ARMS),
            "teacher":"public_keydoor_probe_then_pickup_then_unlock_then_goal"}


def verify_manifest():
    if m.digest(manifest())!=MANIFEST_HASH:
        raise AssertionError("MD22_FROZEN_MANIFEST_DRIFT")
    if m.SCHEMA!="yggdrasil.dg1-mg20-original.v1":
        raise AssertionError("MD22_PINNED_BASE_CHANGED")


class AffordancePlanner(m.MapPolicy):
    """Same navigation scaffold with active or sham learned key->unlock ordering.

    A deliberately rule-guided planner; claimed learning variable is ONLY the
    observed conditional intervention relation, not the coordinate search.
    """
    def __init__(self,kind,teacher=False):
        if kind not in ("causal_affordance","sham_affordance"):
            raise ValueError("MD22_INVALID_PLANNER")
        self.teacher=teacher
        self.failed_without_key=0
        self.unlocked_with_key=0
        self.picked_key_total=0
        self.training_episodes=0
        super().__init__(kind)

    def start(self,seed):
        super().start(seed)
        self.has_key=False
        self.probed_without_key=False
        self.opened_door=False
        self.door_states={}
        self.used_affordance_at_start=(
            (not self.teacher) and self.kind=="causal_affordance"
            and self.failed_without_key>=3 and self.unlocked_with_key>=3)
        self.guided_decisions=0
        self.episode_failed_probes=0
        self.episode_successful_unlocks=0

    def ingest(self,obs):
        """Build known tiles from ONLY the local 7x7 view/direction/estimated pose."""
        from minigrid.core.constants import OBJECT_TO_IDX
        super().ingest(obs)
        img=obs["image"]
        front,right=self.vectors(int(obs["direction"]))
        ax,ay=self.pose
        for dx in range(7):
            for dy in range(7):
                if int(img[dx,dy,0])==OBJECT_TO_IDX["door"]:
                    pos=(ax+(6-dy)*front[0]+(dx-3)*right[0],
                         ay+(6-dy)*front[1]+(dx-3)*right[1])
                    self.door_states[pos]=int(img[dx,dy,2])
        if any(v==0 for v in self.door_states.values()):
            self.opened_door=True

    def feedback(self,before,action,after,reward,training=False):
        from minigrid.core.constants import OBJECT_TO_IDX
        old=m.front_type(before)
        new=m.front_type(after)
        if action==3 and old==OBJECT_TO_IDX["key"] and new!=old:
            self.has_key=True
            if training:self.picked_key_total+=1
        if action==5 and old==OBJECT_TO_IDX["door"]:
            before_state=int(before["image"][3,5,2])
            after_state=int(after["image"][3,5,2])
            if not self.has_key and before_state==2 and after_state==2:
                self.probed_without_key=True
                self.episode_failed_probes+=1
                if training:self.failed_without_key+=1
            if self.has_key and before_state in (1,2) and after_state==0:
                self.opened_door=True
                self.episode_successful_unlocks+=1
                if training:self.unlocked_with_key+=1
        super().feedback(before,action,after,reward,training=training)

    def traversable(self,pos):
        from minigrid.core.constants import OBJECT_TO_IDX
        obj=self.tiles.get(pos)
        if obj is None:return False
        if obj==OBJECT_TO_IDX["door"]:
            return self.door_states.get(pos,2)==0
        if obj in (OBJECT_TO_IDX["wall"],OBJECT_TO_IDX["lava"],
                   OBJECT_TO_IDX["ball"],OBJECT_TO_IDX["key"],
                   OBJECT_TO_IDX["box"]):
            return False
        return True

    def oriented_plan(self,desired):
        """BFS in pose+orientation using known free cells; one-step novel frontier."""
        from minigrid.core.constants import OBJECT_TO_IDX
        start=(self.pose[0],self.pose[1],self.current_dir)
        q=[(0,0,start,())]
        seq=0
        cost={start:0}
        targets=[]
        frontiers=[]
        while q:
            steps,_,state,actions=heapq.heappop(q)
            if steps!=cost[state] or steps>55:continue
            x,y,d=state
            fx,fy=self.vectors(d)[0]
            nxt=(x+fx,y+fy)
            obj=self.tiles.get(nxt)
            here=self.tiles.get((x,y))
            if desired=="key" and obj==OBJECT_TO_IDX["key"]:
                targets.append((steps,actions,3))
            elif desired=="door" and obj==OBJECT_TO_IDX["door"]:
                if self.door_states.get(nxt,2)!=0:
                    targets.append((steps,actions,5))
            elif desired=="box" and obj==OBJECT_TO_IDX["box"]:
                targets.append((steps,actions,3))
            elif desired=="goal" and here==OBJECT_TO_IDX["goal"]:
                targets.append((steps,actions,None))
            if obj is None:
                frontiers.append((steps+1+3*self.visits.get(nxt,0),steps,actions,2,nxt))
            # Deterministic tie-break: actions are genuinely paid, left/right/forward.
            for action,follow in ((0,(x,y,(d-1)%4)),
                                  (1,(x,y,(d+1)%4)),
                                  (2,(x+fx,y+fy,d))):
                if action==2 and not self.traversable(nxt):continue
                nd=steps+1
                if nd<cost.get(follow,999):
                    cost[follow]=nd;seq+=1
                    heapq.heappush(q,(nd,seq,follow,actions+(action,)))
        if targets:
            steps,actions,final=min(targets,key=lambda x:(x[0],x[1],x[2]))
            return actions[0] if actions else final
        if desired in ("key","door","goal","box") and frontiers:
            _,_,actions,final,_=min(frontiers,key=lambda x:(x[0],x[1],x[2],x[4]))
            return actions[0] if actions else final
        return None

    def preferred_subgoal(self):
        if self.opened_door:
            return "box" if self.task_family_box else "goal"
        if self.has_key:return "door"
        if self.used_affordance_at_start:
            self.guided_decisions+=1
            return "key"
        return "key" if self.probed_without_key else "door"

    def act(self,obs,t):
        from minigrid.core.constants import OBJECT_TO_IDX
        self.current_dir=int(obs["direction"])
        self.ingest(obs)
        front=m.front_type(obs)
        state=int(obs["image"][3,5,2])
        self.task_family_box=getattr(self,"task_family_box",False) or any(
            tile==OBJECT_TO_IDX["box"] for tile in self.tiles.values())
        mode=self.preferred_subgoal()
        if front==OBJECT_TO_IDX["door"] and state==0:return 2
        if mode=="key" and front==OBJECT_TO_IDX["key"]:return 3
        if mode=="door" and front==OBJECT_TO_IDX["door"] and state!=0:return 5
        if mode=="box" and front==OBJECT_TO_IDX["box"]:return 3
        action=self.oriented_plan(mode)
        if action is None:
            return m.reactive_action(obs,t,self.rng)
        return action

    def dump(self):
        return {"kind":self.kind,"passability":self.passability,
                "train_calls":self.train_calls,
                "failed_without_key":self.failed_without_key,
                "unlocked_with_key":self.unlocked_with_key,
                "picked_key_total":self.picked_key_total,
                "training_episodes":self.training_episodes}

    def load(self,data):
        for k in ("passability","train_calls","failed_without_key",
                  "unlocked_with_key","picked_key_total","training_episodes"):
            setattr(self,k,data[k])


def make_agent(name):
    if name=="causal_affordance":return AffordancePlanner(name)
    if name=="sham_affordance":return AffordancePlanner(name)
    if name in ("reactive","tabular_q","recurrent_imitation"):
        return m.make_agent(name)
    raise ValueError("MD22_UNKNOWN_ARM")


def save(obj):
    data=zlib.compress(m.canon(obj.dump()).encode(),9)
    if len(data)>65536:raise AssertionError("MD22_CHECKPOINT_TOO_LARGE")
    return data


def restore(data):
    state=json.loads(zlib.decompress(data))
    model=make_agent(state["kind"])
    model.load(state)
    if save(model)!=data:
        raise AssertionError("MD22_CHECKPOINT_NONCANONICAL")
    return model


def train_on_shared(agents,episode):
    """One recorded genuine physical teacher trajectory trains ALL arms."""
    seed=episode["seed"]
    for name in ("causal_affordance","sham_affordance"):
        agents[name].start(seed)
        agents[name].training_episodes+=1
    seq=[]
    last=6
    for i,(before,action,reward,after,terminated) in enumerate(episode["transitions"]):
        for name in ("causal_affordance","sham_affordance"):
            agents[name].feedback(before,action,after,reward,training=True)
        agents["tabular_q"].feedback(
            before,action,after,reward,training=True,terminal=terminated)
        seq.append(m.public_features(before,last,i))
        seq=seq[-m.HISTORY:]
        agents["recurrent_imitation"].learn(seq,action,
            2. if episode["success"] else 1.)
        last=action


def teacher_episode(env,seed):
    """No hidden or privileged world view: only public partial sensor + physical action."""
    model=AffordancePlanner("causal_affordance",teacher=True)
    ep=m.make_trace(env,seed,model)
    ep["failed_without_key_probe_count"]=model.episode_failed_probes
    ep["unlocked_with_key_probe_count"]=model.episode_successful_unlocks
    return ep


def stripped_episode(ep):
    return {k:v for k,v in ep.items() if k not in ("transitions","cpu_ns")}


def collect_training(agents,environments,seeds):
    episodes=[];goals=0;failed=0;success=0;steps=0
    for env in environments:
        for seed in seeds:
            ep=teacher_episode(env,seed)
            episodes.append(stripped_episode(ep))
            goals+=ep["success"];steps+=ep["steps"]
            failed+=ep["failed_without_key_probe_count"]
            success+=ep["unlocked_with_key_probe_count"]
            train_on_shared(agents,ep)
    return {"episodes":episodes,"goal_successes":goals,
            "no_key_failed_toggles":failed,
            "with_key_successful_toggles":success,"steps":steps}


def score(agents,environment,seeds):
    """Each agent independently pays for its own chosen physical sequence."""
    snapshots={name:save(model) for name,model in agents.items()}
    episodes={}
    metrics={}
    for name,model in agents.items():
        rec=[]
        for seed in seeds:
            ep=m.make_trace(environment,seed,model)
            receipt=stripped_episode(ep)
            receipt["direct_no_key_probe"]=getattr(model,"episode_failed_probes",0)
            receipt["direct_with_key_unlock"]=getattr(model,"episode_successful_unlocks",0)
            receipt["learned_edge_used"]=int(getattr(model,"used_affordance_at_start",False))
            receipt["guided_decisions"]=getattr(model,"guided_decisions",0)
            receipt["decision_cpu_ns"]=ep["cpu_ns"]
            rec.append(receipt)
        episodes[name]=[{k:v for k,v in x.items() if k!="decision_cpu_ns"} for x in rec]
        metrics[name]={
            "success_count":sum(x["success"] for x in rec),
            "mean_discounted_official_reward":round(statistics.mean(
                x["discounted_reward"] for x in rec),8),
            "mean_paid_steps":round(statistics.mean(x["steps"] for x in rec),8),
            "charged_env_steps":sum(x["steps"] for x in rec),
            "cpu_ns":sum(x["decision_cpu_ns"] for x in rec),
            "action_trace_sha256":{str(x["seed"]):x["sha256"] for x in rec},
            "learned_edge_episode_count":sum(x["learned_edge_used"] for x in rec)}
    for name,model in agents.items():
        if save(model)!=snapshots[name]:
            raise AssertionError("MD22_EVAL_LEARNED_FROM_HELDOUT")
    return {"environment":environment,"episode_count":len(seeds)*len(ARMS),
            "charged_env_steps":sum(v["charged_env_steps"] for v in metrics.values()),
            "metrics":metrics,"episodes":episodes}


def run():
    verify_manifest()
    import minigrid,gymnasium,numpy
    if (minigrid.__version__!="3.2.0" or gymnasium.__version__!="1.4.0"
            or numpy.__version__!="2.3.4"):
        raise AssertionError("MD22_DEPENDENCY_DRIFT")
    agents={name:make_agent(name) for name in ARMS}
    train=collect_training(agents,TRAIN_ENVS,TRAIN_SEEDS)
    trained_raw={k:save(v) for k,v in agents.items()}
    for k,blob in trained_raw.items():
        if restore(blob).dump()!=agents[k].dump():
            raise AssertionError("MD22_TRAINED_COLD_RESTORE_DRIFT")
    cold_before=score(agents,COLD_ENV,COLD_SEEDS)
    interference=collect_training(agents,(INTERFERENCE_ENV,),INTERFERENCE_SEEDS)
    cold_after=score(agents,COLD_ENV,COLD_SEEDS)
    unseen_size=score(agents,SIZE_ENV,SIZE_SEEDS)
    unseen_family=score(agents,FAMILY_ENV,FAMILY_SEEDS)
    charged=train["steps"]+interference["steps"]+sum(
        part["charged_env_steps"] for part in
        (cold_before,cold_after,unseen_size,unseen_family))
    if charged>76800 or len(train["episodes"])!=48 or len(interference["episodes"])!=12:
        raise AssertionError("MD22_PAID_ACTION_BUDGET_DRIFT")
    if any(part["episode_count"]!=60 for part in
           (cold_before,cold_after,unseen_size,unseen_family)):
        raise AssertionError("MD22_EVAL_EPISODE_BUDGET_DRIFT")
    heldout_coverage={n:sum(p["metrics"][a]["success_count"]for a in ARMS)
                      for n,p in (("unseen_size",unseen_size),
                                  ("unseen_family",unseen_family))}
    coverage=train["goal_successes"]>=24 and (
        train["no_key_failed_toggles"]>=8 and train["with_key_successful_toggles"]>=8
        and all(v>=3 for v in heldout_coverage.values()))
    gates={}
    per_seed_wins={}
    for name,part in (("unseen_size",unseen_size),
                      ("unseen_family",unseen_family)):
        c=part["metrics"]["causal_affordance"]
        control=max((a for a in ARMS if a!="causal_affordance"),
                    key=lambda a:(part["metrics"][a]["mean_discounted_official_reward"],a))
        best=part["metrics"][control]
        gates[name+"_strong_reward_margin"]=(
            c["mean_discounted_official_reward"]>=
            best["mean_discounted_official_reward"]+.08)
        gates[name+"_sham_reward_margin"]=(
            c["mean_discounted_official_reward"]>=
            part["metrics"]["sham_affordance"]["mean_discounted_official_reward"]+.08)
        gates[name+"_minimum_goal_success"]=c["success_count"]>=8
        gates[name+"_vs_best_control_success"]=(
            c["success_count"]>=best["success_count"]-1)
        c_by={int(ep["seed"]):ep["discounted_reward"]
              for ep in part["episodes"]["causal_affordance"]}
        b_by={int(ep["seed"]):ep["discounted_reward"]
              for ep in part["episodes"][control]}
        win=sum(c_by[s]>b_by[s]+1e-8 for s in c_by)
        per_seed_wins[name]=win
        gates[name+"_per_seed_reward_wins"]=win>=7
        gates[name+"_learnt_edge_used"]=c["learned_edge_episode_count"]>=8
    gates["physical_contrasts_learned"]=(
        agents["causal_affordance"].failed_without_key>=8 and
        agents["causal_affordance"].unlocked_with_key>=8)
    c_before=cold_before["metrics"]["causal_affordance"]["success_count"]
    c_after=cold_after["metrics"]["causal_affordance"]["success_count"]
    gates["cold_success_retained"]=c_after>=c_before-1
    gates["cold_competitive_vs_reactive"]=(
        c_after>=cold_after["metrics"]["reactive"]["success_count"])
    gates["bounded_checkpoint"]=all(len(save(x))<=65536 for x in agents.values())
    gates["fully_trained_reward_controls"]=(
        agents["tabular_q"].count>0 and agents["recurrent_imitation"].count>0)
    cpu_ratio=round(
        (unseen_size["metrics"]["causal_affordance"]["cpu_ns"]+
         unseen_family["metrics"]["causal_affordance"]["cpu_ns"])/
        max(1,unseen_size["metrics"]["recurrent_imitation"]["cpu_ns"]+
              unseen_family["metrics"]["recurrent_imitation"]["cpu_ns"]),6)
    gates["cpu_vs_trained_recurrent"]=cpu_ratio<=5.
    primary=coverage and all(gates.values())
    mixed=any(
        part["metrics"]["causal_affordance"]["success_count"]>=
        part["metrics"][other]["success_count"]+2
        for part in (unseen_size,unseen_family)
        for other in ARMS if other!="causal_affordance") or (
        any(part["metrics"]["causal_affordance"]["success_count"]>=8 and
            part["metrics"]["causal_affordance"]["learned_edge_episode_count"]>=3
            for part in (unseen_size,unseen_family)))
    classification=("INVALID_TASK_COVERAGE" if not coverage else
                    "DEVELOPMENT_SIGNAL_ONLY" if primary else
                    "MIXED_DEV" if mixed else "NEGATIVE_DEV")
    return {
        "schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
        "manifest_sha256":MANIFEST_HASH,
        "classification":classification,"primary_pass":primary,
        "scientific_acceptance":"UNVERIFIED",
        "packages":{"minigrid":minigrid.__version__,"gymnasium":gymnasium.__version__,
                    "numpy":numpy.__version__},
        "train":train,"interference":interference,
        "heldout_goal_coverage":heldout_coverage,
        "cold_before":cold_before,"cold_after":cold_after,
        "unseen_size":unseen_size,"unseen_family":unseen_family,
        "gates":gates,"per_seed_wins":per_seed_wins,
        "training_contrast_learned":{"failed_without_key":agents["causal_affordance"].failed_without_key,
                                      "unlocked_with_key":agents["causal_affordance"].unlocked_with_key},
        "original_action_cost":charged,"total_episodes":300,"max_paid_actions":76800,
        "cpu_ratio":cpu_ratio,
        "checkpoint_sha256":{k:hashlib.sha256(save(v)).hexdigest() for k,v in agents.items()},
        "checkpoint_bytes":{k:len(save(v)) for k,v in agents.items()},
        "trained_control_updates":{"tabular_q":agents["tabular_q"].count,
                                  "recurrent_imitation":agents["recurrent_imitation"].count},
        "native_model_changed":False}


if __name__=="__main__":
    print(m.canon(run()))
