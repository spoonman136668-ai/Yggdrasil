"""DG1-MD26, paid-action causal drop site test (toy only; no first use).

This external research module tests a narrow action-effect learning hypothesis.
Both candidate and blind control inherit identical public-view navigation and
identical route repair. A causal occupancy prediction can only affect which
real physical side-drop action is selected when BOTH sides are publicly free.
"""
import hashlib
import heapq
import importlib.util
import json
import statistics
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"dg1-md25-20261114"/"md25.py"
spec=importlib.util.spec_from_file_location("md26_pinned_md25",str(SOURCE))
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
m=p.m
graph=p.graph
FREEZE_SHA="4c4d34f305278fde8132a7be35ecba1ba9baee0d"
PARENT_SHA="563c805f8841e39a8363d76019e86996b611ae14"
ARMS=("learned_effect_bfs","blind_site_bfs","permuted_effect_bfs",
      "md25_causal_site","tabular_q","recurrent_imitation")
TEACHER=(41,43,47,53,59,61)
TOY=(67,71,73,79,83,89)
ENV="MiniGrid-BlockedUnlockPickup-v0"
MAX_STEPS=256
REGISTERED=((1014001,1014024),(1015001,1015024),(1016001,1016012),
            (1017001,1017012),(1018001,1018012),(1019001,1019012))


def prereg():
    x=json.loads(Path(__file__).with_name("prereg.json").read_text())
    if (x["experiment_id"]!="DG1-MD26-20261114" or
        x["parent_SHA"]!=PARENT_SHA or
        x["status"]!="PREREGISTRATION_ONLY_NO_PRIMARY_SEEDS_CONSUMED" or
        x["design"]["toy_evaluation_seeds"]!=list(TOY) or
        x["design"]["arms"]!=list(ARMS) or
        x["design"]["max_step_per_episode"]!=MAX_STEPS):
        raise AssertionError("MD26_FROZEN_PREREG_MISMATCH")
    all_seeds=[s for lo,hi in REGISTERED for s in range(lo,hi+1)]
    if len(all_seeds)!=96 or len(set(all_seeds))!=96:
        raise AssertionError("MD26_REGISTERED_SEED_INTERSECTION")
    if set(all_seeds)&(set(TEACHER)|set(TOY)) or set(TEACHER)&set(TOY):
        raise AssertionError("MD26_TOY_REGISTERED_SEED_LEAKAGE")
    return x


def seed_fence(seed,training=False):
    if type(seed) is not int or seed not in (TEACHER if training else TOY):
        raise AssertionError("MD26_NO_REGISTERED_FIRST_USE_FROM_TOY")


class EffectBfsPolicy(p.SiteChoice):
    """Learned counterfactual occupancy, with equal routed nonlearning controls."""

    BASE={"learned_effect_bfs":"causal_site",
          "blind_site_bfs":"blind_site",
          "permuted_effect_bfs":"permuted_site"}

    def __init__(self,kind):
        if kind not in self.BASE:raise ValueError("MD26_UNKNOWN_EFFECT_BFS_ARM")
        self.source_kind=self.BASE[kind]
        super().__init__(self.source_kind)
        self.kind=kind
        self.start(67)

    def start(self,seed):
        super().start(seed)
        self.both_free_decisions=0
        self.both_free_decisions_learned=0
        self.bfs_choice_left=0
        self.drop_events=[]
        self.action_events=[]
        self.effect_selected_at_paid_action=0

    def gate(self):
        if self.kind=="blind_site_bfs":return True
        if self.kind=="permuted_effect_bfs":
            return self.effects["toggle_shift"]>=6
        return (self.effects["pickup_clear"]>=6 and
                self.effects["drop_place"]>=6)

    def _route_cost(self,blocked):
        """Shortest weighted public-view route to a reachable door-adjacent tile.

        A drop occupies the counterfactual blocked cell; unknown map tiles cost
        four to reflect risk but never reveal hidden world. This is NOT a
        simulator env.step. No privileged target, agent pos, or grid is read.
        """
        from minigrid.core.constants import OBJECT_TO_IDX
        doors={pos for pos,obj in self.tiles.items()
               if obj==OBJECT_TO_IDX["door"]}
        if not doors:return 9999
        start=self.pose
        positions=list(self.tiles)
        xlo=min([start[0]]+[x for x,y in positions])-2
        xhi=max([start[0]]+[x for x,y in positions])+2
        ylo=min([start[1]]+[y for x,y in positions])-2
        yhi=max([start[1]]+[y for x,y in positions])+2
        neighbors=((1,0),(0,1),(-1,0),(0,-1))
        goals={ (x+dx,y+dy) for x,y in doors for dx,dy in neighbors
                if (x+dx,y+dy)!=blocked }
        if not goals:return 9999
        frontier=[(0,0,start)]
        cost={start:0}
        count=0
        while frontier:
            c,_,pos=heapq.heappop(frontier)
            if c!=cost[pos]:continue
            if pos in goals:return c
            x,y=pos
            for dx,dy in neighbors:
                dst=(x+dx,y+dy)
                if (dst==blocked or not xlo<=dst[0]<=xhi or
                    not ylo<=dst[1]<=yhi):
                    continue
                if dst in doors:continue
                tile=self.tiles.get(dst)
                if tile is not None and not self.traversable(dst):continue
                weight=4 if tile is None else 1
                alt=c+weight
                if alt<cost.get(dst,9999):
                    cost[dst]=alt
                    count+=1
                    heapq.heappush(frontier,(alt,count,dst))
        return 9999

    def predicted_drop_side(self,obs):
        from minigrid.core.constants import OBJECT_TO_IDX
        # Every arm sees the same paid physical frame and receives the same
        # map update at this step; learning changes only this site's choice.
        self.ingest(obs)
        empty=OBJECT_TO_IDX["empty"]
        left=int(obs["image"][2,6,0])==empty
        right=int(obs["image"][4,6,0])==empty
        if not left and not right:return None
        if not left:return "right"
        if not right:return "left"
        self.both_free_decisions+=1
        fallback="right"
        if self.kind!="learned_effect_bfs" or not self.gate():
            return fallback
        _,(rx,ry)=self.vectors(int(obs["direction"]))
        x,y=self.pose
        lpt=(x-rx,y-ry)
        rpt=(x+rx,y+ry)
        left_cost=self._route_cost(lpt)
        right_cost=self._route_cost(rpt)
        choice=("left" if left_cost<right_cost else "right")
        self.both_free_decisions_learned+=1
        self.drop_events.append({"left_cost":left_cost,"right_cost":right_cost,
                                 "selected":choice})
        if choice=="left":
            self.bfs_choice_left+=1
        return choice

    def act(self,obs,t):
        before_counter=self.bfs_choice_left
        action=super().act(obs,t)
        # Only credit a learn-specific intervention if its ACTUAL next charged
        # action is 0 (turn left), not based on a hypothetical internal choice.
        if (self.bfs_choice_left>before_counter and action==0):
            self.effect_selected_at_paid_action+=1
        self.action_events.append({"t":t,"action":action,
                                   "causal_actual":int(
                                       self.bfs_choice_left>before_counter and
                                       action==0)})
        return action

    def dump(self):
        x=super().dump()
        x["kind"]=self.kind
        return x

    def load(self,x):
        if x["kind"]!=self.kind:
            raise AssertionError("MD26_ARM_CHECKPOINT_KIND")
        super().load(x)


def make_agent(name):
    if name in EffectBfsPolicy.BASE:return EffectBfsPolicy(name)
    if name=="md25_causal_site":return p.SiteChoice("causal_site")
    if name in ("tabular_q","recurrent_imitation"):return m.make_agent(name)
    raise ValueError("MD26_UNKNOWN_ARM")


def save(agent):
    x=agent.dump()
    if isinstance(agent,p.SiteChoice) and not isinstance(agent,EffectBfsPolicy):
        x=dict(x,kind="md25_causal_site")
    raw=zlib.compress(m.canon(x).encode(),9)
    if len(raw)>65536:raise AssertionError("MD26_CHECKPOINT_CAP")
    return raw


def restore(raw):
    data=json.loads(zlib.decompress(raw))
    obj=make_agent(data["kind"])
    if data["kind"]=="md25_causal_site":
        obj.load(dict(data,kind="causal_site"))
    else:obj.load(data)
    if save(obj)!=raw:raise AssertionError("MD26_COLD_MODEL_NONCANONICAL")
    return obj


def train_common(agents,ep):
    for name in ARMS[:4]:
        agents[name].start(ep["seed"])
        agents[name].training_episodes+=1
    seq=[]
    previous=6
    for t,(before,action,reward,after,terminal) in enumerate(ep["transitions"]):
        for name in ARMS[:4]:
            agents[name].feedback(before,action,after,reward,training=True)
        agents["tabular_q"].feedback(before,action,after,reward,
                                    training=True,terminal=terminal)
        seq.append(m.public_features(before,previous,t))
        seq=seq[-m.HISTORY:]
        agents["recurrent_imitation"].learn(
            seq,action,2. if ep["success"] else 1.)
        previous=action


def train_toy():
    prereg()
    p.versions()
    agents={name:make_agent(name) for name in ARMS}
    counts={"door_goals":0,"box_goals":0,"paid_train_steps":0}
    for env,label in ((p.DOOR,"door"),(p.BOX,"box")):
        for seed in TEACHER:
            seed_fence(seed,training=True)
            teacher=graph.GraphPolicy("fixed_scripted",probe_first=True)
            ep=m.make_trace(env,seed,teacher)
            if ep["steps"]!=len(ep["transitions"]) or ep["steps"]>256:
                raise AssertionError("MD26_TRAIN_PHYSICAL_ACCOUNTING")
            train_common(agents,ep)
            counts[label+"_goals"]+=ep["success"]
            counts["paid_train_steps"]+=ep["steps"]
    a,b,c=[agents[x] for x in ARMS[:3]]
    if a.effects!=b.effects or b.effects!=c.effects:
        raise AssertionError("MD26_UNMATCHED_LEARNED_EFFECT_DATA")
    return agents,counts


def eval_toy(agents):
    original={name:save(model) for name,model in agents.items()}
    results={}
    for name,model in agents.items():
        result=[]
        for seed in TOY:
            seed_fence(seed)
            ep=m.make_trace(ENV,seed,model)
            act=[action for before,action,reward,after,end in ep["transitions"]]
            if (len(act)!=ep["steps"] or
                len(act)>256 or any(a not in m.ACTIONS for a in act)):
                raise AssertionError("MD26_CHARGED_EVAL_ACTION_IDENTITY")
            if isinstance(model,EffectBfsPolicy):
                executed=model.action_events
                if len(executed)!=len(act):
                    raise AssertionError("MD26_DECISION_AUDIT_STEP_COUNT")
                if any(x["action"]!=action for x,action in zip(executed,act)):
                    raise AssertionError("MD26_UNPAID_CAUSAL_SITE_DECISION")
            result.append({
                "seed":seed,"steps":ep["steps"],"official_goals":ep["success"],
                "discounted_reward":ep["discounted_reward"],
                "physical_sha256":ep["sha256"],
                "physical_action_digest":hashlib.sha256(bytes(act)).hexdigest(),
                "real_causal_turn_events":getattr(model,"effect_selected_at_paid_action",0),
                "counterfactual_site_left":getattr(model,"bfs_choice_left",0),
                "both_free":getattr(model,"both_free_decisions",0),
                "public_prediction_events":getattr(model,"drop_events",[]),
                "actual_actions":act})
        if save(model)!=original[name]:
            raise AssertionError("MD26_HELDOUT_MODEL_MUTATION")
        results[name]=result
    return results


def toy_study():
    spec=prereg()
    agents,teacher=train_toy()
    checkpoints={name:save(model) for name,model in agents.items()}
    for name,raw in checkpoints.items():
        if save(restore(raw))!=raw:
            raise AssertionError("MD26_CHECKPOINT_COLD_RESTORE_"+name)
    r=eval_toy(agents)
    learn=r["learned_effect_bfs"]
    blind=r["blind_site_bfs"]
    paired_distinct=sum(x["physical_sha256"]!=y["physical_sha256"]
                        for x,y in zip(learn,blind))
    strict_steps=sum(x["steps"]<y["steps"] and
                     x["official_goals"]>=y["official_goals"]
                     for x,y in zip(learn,blind))
    all_means={name:{"goals":sum(x["official_goals"] for x in rows),
                     "paid_steps":sum(x["steps"] for x in rows),
                     "learned_paid_site_actions":sum(x["real_causal_turn_events"]
                                                     for x in rows)}
               for name,rows in r.items()}
    saving=(all_means["blind_site_bfs"]["paid_steps"]-
            all_means["learned_effect_bfs"]["paid_steps"])/len(TOY)
    goals=all_means["learned_effect_bfs"]["goals"]
    blindgoals=all_means["blind_site_bfs"]["goals"]
    t=spec["toy_gates"]
    conditions={
        "training_door":teacher["door_goals"]>=t["teacher_door_goals_min"],
        "training_box":teacher["box_goals"]>=t["teacher_box_goals_min"],
        "actual_pickup":agents["learned_effect_bfs"].effects["pickup_clear"]>=t["known_pickup_effects_min"],
        "actual_drop":agents["learned_effect_bfs"].effects["drop_place"]>=t["known_drop_effects_min"],
        "candidate_goals":goals>=t["candidate_heldout_goals_min"],
        "paid_action_divergence":paired_distinct>=t["paired_action_trace_differences_min"],
        "decisive_learned_action":all_means["learned_effect_bfs"]["learned_paid_site_actions"]>=t["true_both_free_causal_site_decisions_min"],
        "strict_step_wins":strict_steps>=t["strict_fewer_paid_actions_vs_blind_seed_wins_min"],
        "goal_nonregression":blindgoals-goals<=t["candidate_goal_regression_vs_blind_max"],
        "paid_mean_step_gain":saving>=t["mean_paid_step_saving_vs_blind_min"]
    }
    return {
       "schema":"yggdrasil.dg1-md26-toy.v1",
       "prereg_commit":FREEZE_SHA,
       "registered_first_use":False,
       "classification":("TOY_READY_PENDING_DUAL_PLATFORM_QUALIFICATION"
                         if all(conditions.values())
                         else "TOY_NO_GO_NO_REGISTERED_FIRST_USE"),
       "toy_gates":conditions,
       "shared_training":teacher,
       "learned_effects":agents["learned_effect_bfs"].effects,
       "by_arm":all_means,
       "paired_physical_trace_differences":paired_distinct,
       "strict_paired_step_wins":strict_steps,
       "mean_paid_steps_saved":round(saving,6),
       "checkpoint_sha256":{name:hashlib.sha256(raw).hexdigest()
                            for name,raw in checkpoints.items()},
       "charged_evaluation_traces":r
    }


if __name__=="__main__":
    print(m.canon(toy_study()))
