"""MD25 prefirstuse: learned action-effect intervention-site choice.

External MiniGrid toy research only. Same base navigation for learned and blind
arms. No privileged grid, mission parsing, unseen task family training, or
registered seed use on this module's default/test path.
"""
import hashlib
import importlib.util
import json
import statistics
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MD24=ROOT/"dg1-md24-20261114"/"md24.py"
spec=importlib.util.spec_from_file_location("md25_frozen_md24",str(MD24))
d=importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m=d.m
graph=d.d
FROZEN_PREREG_SHA="f8b4d11855918a987144885f4885f0598d271136"
EXACT_PARENT_SHA="ea9ceca774a50bb3126bdf066120cb32ea4ddec5"
ARMS=("causal_site","blind_site","permuted_site","md23_causal",
      "tabular_q","recurrent_imitation")
TOY=(41,43,47,53,59,61)
DOOR="MiniGrid-DoorKey-6x6-v0"
BOX="MiniGrid-UnlockPickup-v0"
NOVEL="MiniGrid-BlockedUnlockPickup-v0"
PRIMARY_RANGES=((996001,996024),(997001,997024),(998001,998012),
                (999001,999012),(1000001,1000012),(1001001,1001012))


def guard_seeds(seeds):
    if not seeds or any(type(s) is not int or s not in TOY for s in seeds):
        raise AssertionError("MD25_NO_REGISTERED_SEEDS_IN_TOY")


def verify_protocol():
    x=json.loads(Path(__file__).with_name("prereg.json").read_text())
    if (x["experiment_id"]!="DG1-MD25-20261114" or
        x["exact_parent_sha"]!=EXACT_PARENT_SHA or
        x["status"]!="FROZEN_PREREGISTRATION_ONLY_NO_PRIMARY_EXECUTION" or
        x["toy_development_seeds"]!=list(TOY) or
        x["arms"]!=list(ARMS) or
        x["budget"]["episodes"]!=348 or
        x["budget"]["total_physical_env_steps_max"]!=89088 or
        x["scientific_acceptance"]!="UNVERIFIED_NOT_NATIVE"):
        raise AssertionError("MD25_PREREG_DRIFT")
    all_primary=[i for lo,hi in PRIMARY_RANGES for i in range(lo,hi+1)]
    if len(set(all_primary))!=96 or set(all_primary)&set(TOY):
        raise AssertionError("MD25_COHORT_COLLISION")
    d.verify_manifest()
    return x


def versions():
    d.versions()


class SiteChoice(d.TransferPolicy):
    """Matched action-effect/geometry policies; learning changes predicted site.

    The strong blind control has identical repair of post-obstacle navigation.
    Only the candidate consults previously trained drop-occupancy counts to
    project whether a site will interfere with approach to the nearest door.
    """
    KINDS=d.TransferPolicy.KINDS+("causal_site","blind_site","permuted_site")
    def __init__(self,kind):
        if kind not in self.KINDS:raise ValueError("MD25_UNKNOWN_SITE_ARM")
        base={"causal_site":"learned_transfer",
              "blind_site":"blind_generic",
              "permuted_site":"permuted_effect"}[kind]
        super().__init__(base)
        self.kind=kind
        self.start(41)

    def start(self,seed):
        super().start(seed)
        self.site_predictions=0
        self.site_left_choices=0
        self.nav_resume=0
        self.complete_clearance=False
        self.postclear_attempts=0

    def learned_effect_available(self):
        if self.kind=="blind_site":return True
        if self.kind=="permuted_site":
            return self.effects["toggle_shift"]>=6
        return self.effects["pickup_clear"]>=6 and self.effects["drop_place"]>=6

    def gate(self):
        return self.learned_effect_available()

    def predicted_drop_side(self,obs):
        """Return left/right based on public geometry and training effects.

        The otherwise identical blind arm uses a nearest-free right-first
        tie breaker. Learned edge identity determines whether drop occupancy
        enters the evaluation (permuted arm does not use the correct edge).
        """
        from minigrid.core.constants import OBJECT_TO_IDX
        img=obs["image"]
        empty=OBJECT_TO_IDX["empty"]
        left=int(img[2,6,0])==empty
        right=int(img[4,6,0])==empty
        if not left and not right:return None
        if not left:return "right"
        if not right:return "left"
        if self.kind!="causal_site" or self.effects["drop_place"]<6:
            return "right"
        heading=int(obs["direction"])
        (fx,fy),(rx,ry)=self.vectors(heading)
        x,y=self.pose
        doors=[key for key,value in self.tiles.items()
               if value==OBJECT_TO_IDX["door"]]
        if not doors:
            return "right"
        nearest=min(doors,key=lambda k:(abs(k[0]-x)+abs(k[1]-y),k))
        left_pt=(x-rx,y-ry)
        right_pt=(x+rx,y+ry)
        dl=abs(nearest[0]-left_pt[0])+abs(nearest[1]-left_pt[1])
        dr=abs(nearest[0]-right_pt[0])+abs(nearest[1]-right_pt[1])
        self.site_predictions+=1
        return "left" if dl>dr else "right"

    def feedback(self,before,action,after,reward,training=False):
        from minigrid.core.constants import OBJECT_TO_IDX
        opaque=self.last_opaque
        front=m.front_type(before)
        carry_before=int(m.objects(before)[3,6])
        carry_after=int(m.objects(after)[3,6])
        fwd,_=self.vectors(int(before["direction"]))
        site=(self.pose[0]+fwd[0],self.pose[1]+fwd[1])
        pickup=(action==3 and opaque is not None and front==opaque
                and m.front_type(after)==OBJECT_TO_IDX["empty"]
                and carry_before==OBJECT_TO_IDX["empty"] and carry_after==opaque)
        dropped=(action==4 and carry_before not in
                 (OBJECT_TO_IDX["empty"],OBJECT_TO_IDX["unseen"])
                 and carry_after==OBJECT_TO_IDX["empty"]
                 and m.front_type(after)==carry_before)
        super().feedback(before,action,after,reward,training=training)
        if not training:
            if pickup:
                self.tiles[site]=OBJECT_TO_IDX["empty"]
                self.complete_clearance=True
            if dropped:
                self.tiles[site]=carry_before

    def act(self,obs,t):
        from minigrid.core.constants import OBJECT_TO_IDX
        # All arms receive the same explicit fix to MD24's proven navigation
        # defect: once the single novel obstruction is actually cleared, the
        # agent must complete the key-door-box procedure instead of searching
        # for a second unknown object or re-intercepting key release.
        if self.complete_clearance and self.phase is None:
            self.nav_resume+=1
            return graph.GraphPolicy.act(self,obs,t)
        if self.phase=="turn_right" and self.relobj is not None:
            choice=self.predicted_drop_side(obs)
            if choice=="left":
                self.phase="left_side"
                if self.kind=="causal_site":self.site_left_choices+=1
                return 0
        return super().act(obs,t)

    def dump(self):
        x=super().dump()
        x["kind"]=self.kind
        return x

    def load(self,x):
        if x["kind"]!=self.kind:raise AssertionError("MD25_SITE_LOAD_KIND")
        super().load(x)


def make_agent(name):
    if name in ARMS[:3]:return SiteChoice(name)
    if name=="md23_causal":return graph.GraphPolicy("causal_graph",probe_first=True)
    if name in ("tabular_q","recurrent_imitation"):return m.make_agent(name)
    raise ValueError("MD25_UNKNOWN_ARM")


def save(agent):
    x=agent.dump()
    if not isinstance(agent,SiteChoice) and isinstance(agent,graph.GraphPolicy):
        x=dict(x,kind="md23_causal")
    raw=zlib.compress(m.canon(x).encode(),9)
    if len(raw)>65536:raise AssertionError("MD25_CHECKPOINT_CAP")
    return raw


def restore(raw):
    x=json.loads(zlib.decompress(raw))
    agent=make_agent(x["kind"])
    if x["kind"]=="md23_causal":
        agent.load(dict(x,kind="causal_graph"))
    else:agent.load(x)
    if save(agent)!=raw:raise AssertionError("MD25_BAD_COLD_RESTORE")
    return agent


def physical_teacher(env,seed):
    guard_seeds((seed,))
    policy=graph.GraphPolicy("fixed_scripted",probe_first=True)
    ep=m.make_trace(env,seed,policy)
    if ep["steps"]!=len(ep["transitions"]) or ep["steps"]>256:
        raise AssertionError("MD25_UNCHARGED_ACTION")
    return ep


def train_shared(agents,ep):
    for name in ARMS[:4]:
        agents[name].start(ep["seed"])
        agents[name].training_episodes+=1
    seq=[]
    prior=6
    for i,(before,act,reward,after,terminal) in enumerate(ep["transitions"]):
        for name in ARMS[:4]:
            agents[name].feedback(before,act,after,reward,training=True)
        agents["tabular_q"].feedback(before,act,after,reward,training=True,
                                    terminal=terminal)
        seq.append(m.public_features(before,prior,i))
        seq=seq[-m.HISTORY:]
        agents["recurrent_imitation"].learn(seq,act,2. if ep["success"] else 1.)
        prior=act


def evaluate(agents,env,seeds):
    guard_seeds(seeds)
    frozen={name:save(agent) for name,agent in agents.items()}
    rows={}
    for name,agent in agents.items():
        results=[]
        for seed in seeds:
            ep=m.make_trace(env,seed,agent)
            results.append({
                "seed":seed,"success":ep["success"],
                "discounted_reward":ep["discounted_reward"],
                "sha256":ep["sha256"],"steps":ep["steps"],
                "obstacle_cleared":getattr(agent,"new_obstacle_cleared",0),
                "site_predictions":getattr(agent,"site_predictions",0),
                "site_left_choices":getattr(agent,"site_left_choices",0),
                "nav_resumes":getattr(agent,"nav_resume",0)})
        if save(agent)!=frozen[name]:
            raise AssertionError("MD25_HELDOUT_PERSISTENT_WEIGHT_MUTATION")
        rows[name]=results
    return rows


def toy_study():
    verify_protocol()
    versions()
    agents={name:make_agent(name) for name in ARMS}
    teacher={"door_goals":0,"box_goals":0,"steps":0}
    for env,label in ((DOOR,"door"),(BOX,"box")):
        for seed in TOY:
            ep=physical_teacher(env,seed)
            teacher[label+"_goals"]+=ep["success"]
            teacher["steps"]+=ep["steps"]
            train_shared(agents,ep)
    a,b,c=[agents[k] for k in ARMS[:3]]
    if not(a.effects==b.effects==c.effects and
           a.effect_trials==b.effect_trials==c.effect_trials):
        raise AssertionError("MD25_TRAINED_CONTROL_DATA_OR_CAPACITY_MISMATCH")
    saved={k:save(v) for k,v in agents.items()}
    for k,v in saved.items():
        if save(restore(v))!=v:raise AssertionError("MD25_NO_COLD_RESTORE_"+k)
    traces=evaluate(agents,NOVEL,TOY)
    learned,blind=traces["causal_site"],traces["blind_site"]
    paired_equal=sum(x["sha256"]==y["sha256"] for x,y in zip(learned,blind))
    observed_any=sum(x["success"] for rows in traces.values() for x in rows)
    counts={k:{"goals":sum(v["success"] for v in rows),
               "charged_steps":sum(v["steps"] for v in rows),
               "real_obstacle_clears":sum(v["obstacle_cleared"] for v in rows),
               "site_predictions":sum(v["site_predictions"] for v in rows),
               "site_left_choices":sum(v["site_left_choices"] for v in rows)}
            for k,rows in traces.items()}
    toy_gate=verify_protocol()["toy_coverage_gates"]
    differs=len(TOY)-paired_equal
    coverage=(teacher["door_goals"]>=toy_gate["public_training_door_goals_min"]
              and teacher["box_goals"]>=toy_gate["public_training_box_goals_min"]
              and observed_any>=toy_gate["novel_any_arm_goals_min"]
              and counts["causal_site"]["goals"]>=toy_gate["candidate_novel_goals_min"]
              and differs>=toy_gate["learned_and_blind_trace_differences_min"]
              and a.effects["pickup_clear"]>0 and a.effects["drop_place"]>0)
    classification="TOY_READY_FOR_FURTHER_QUALIFICATION" if coverage else "TOY_COVERAGE_NO_GO"
    return {"schema":"yggdrasil.dg1-md25-toy.v1",
            "classification":classification,"eligible_for_registered_first_use":False,
            "registered_seeds_used":False,"teacher":teacher,
            "learned_counts":a.effects,"paired_identical":paired_equal,
            "paired_different":differs,"novel_goals_all_arms":observed_any,
            "metrics":counts,"toy_traces":traces,
            "checkpoint_sha256":{k:hashlib.sha256(v).hexdigest()
                                 for k,v in saved.items()}}


if __name__=="__main__":
    print(m.canon(toy_study()))
