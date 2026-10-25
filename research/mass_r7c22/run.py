"""R7-C22: original external dynamic-obstacle episode learning, FIT fixed from C21."""
import argparse, collections, hashlib, json, os, resource, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from research.mass_r7c21 import run as c21
from research.native.itd02.r1.native_policy import PublicGrid, canonical
from research.mass_r7c20 import run as c20
P=json.loads((HERE/"PREREG.json").read_text())

def public_dynamic(o, goal):
    """Only user-available FullyObsWrapper: front tile map checked, then dropped."""
    import numpy as np
    from minigrid.core.constants import OBJECT_TO_IDX as T
    img=o["image"]
    assert img.ndim==3 and img.shape[-1]==3
    poss=np.argwhere(img[:,:,0]==T["agent"])
    assert len(poss)==1, ("PUBLIC_AGENT_COUNT",len(poss))
    x,y=(int(v) for v in poss[0])
    d=int(o["direction"])
    assert d in range(4)
    dx,dy=c20.DIR[d]
    xx,yy=x+dx,y+dy
    if not(0<=xx<img.shape[0] and 0<=yy<img.shape[1]):
        blocked=True
    else:
        token=int(img[xx,yy,0])
        # No hidden map, no privileged obstacle coordinates and NO wall-vs-ball
        # discriminator passed to ANY policy. Unknown cells fail closed.
        assert token in (T["wall"],T["empty"],T["goal"],T["agent"],T["ball"]),("UNEXPECTED_PUBLIC_TILE",token)
        blocked=token in (T["wall"],T["ball"])
    return PublicGrid(x,y,goal[0],goal[1],d,bool(blocked))

class ConventionalRecent(c20.Conventional):
    """Ablate stale edge-memory: retain public visit counts and fitted motor."""
    def choose(self,state):
        self.blocked.clear()
        self.open.clear()
        return super().choose(state)

def model_make(arm, fit):
    if arm=="conventional_recent":
        return ConventionalRecent(fit)
    return c21.choose_model(arm,fit)

def cold(arm,snapshot,dimensions):
    c21.cold_restore("conventional" if arm=="conventional_recent" else arm,snapshot,dimensions)

def dynamic_experiment(arm,model):
    family=P["environment"]
    env=c20.env_make(family)
    totals={"episodes":0,"wins":0,"collision_terminated":0,"reached_source_horizon":0,
            "actions":0,"blocked_forward":0,"blocked_forward_no_motion":0,
            "blocked_forward_with_motion":0,"first_blocked_forward":0,
            "repeat_blocked_forward":0,"reward_sum":0.0,"observed_front_cell_reversals":0}
    episodes=[]
    try:
        for seed in P["fresh_public_dynamic_dev_seeds"]:
            o,_=env.reset(seed=seed)
            goal=c20.goal_from(o)
            dims=tuple(int(v) for v in o["image"].shape[:2])
            model.reset_episode(*dims)
            poses=set()
            cells={}
            trace=[]
            win=False
            term_neg=False
            term_trunc=False
            last_reward=0.0
            for step in range(P["dev_max_actions"]):
                before=public_dynamic(o,goal)
                dx,dy=c20.DIR[before.direction]
                key=(before.x+dx,before.y+dy)
                sensed=int(before.front_blocked)
                if key in cells and cells[key]!=sensed:
                    totals["observed_front_cell_reversals"]+=1
                cells[key]=sensed
                pose=(before.x,before.y,before.direction)
                was_seen=pose in poses
                poses.add(pose)
                action=model.choose(before)
                assert type(action) is int and action in (0,1,2), ("ILLEGAL_PUBLIC_ACTION",action)
                after_obs,reward,done,trunc,_=env.step(action)
                after=public_dynamic(after_obs,goal)
                reward=float(reward)
                if arm in ("conventional","conventional_recent"):
                    model.observe(before,action,after,reward,bool(done))
                else:
                    model.observe(before,action,after,reward,bool(done),False)
                blocked_action=action==2 and before.front_blocked
                moved=(after.x,after.y)!=(before.x,before.y)
                totals["actions"]+=1; totals["reward_sum"]+=reward
                if blocked_action:
                    totals["blocked_forward"]+=1
                    totals["blocked_forward_with_motion" if moved else "blocked_forward_no_motion"]+=1
                    totals["repeat_blocked_forward" if was_seen else "first_blocked_forward"]+=1
                trace.append([before.x,before.y,before.direction,before.goal_x,before.goal_y,
                    sensed,action,after.x,after.y,after.direction,
                    int(after.front_blocked),reward,int(bool(done)),int(bool(trunc))])
                o=after_obs;last_reward=reward
                if done or trunc:
                    win=bool(reward>0)
                    term_neg=bool(done and reward<0)
                    term_trunc=bool(trunc)
                    break
            totals["episodes"]+=1
            totals["wins"]+=int(win)
            totals["collision_terminated"]+=int(term_neg)
            totals["reached_source_horizon"]+=int(term_trunc)
            blob=model.checkpoint() if arm in ("conventional","conventional_recent") else model.snapshot()
            cold(arm,blob,dims)
            episodes.append({"seed":seed,"success":win,"collision_terminated":term_neg,
                "source_horizon":term_trunc,"actions":len(trace),"last_reward":last_reward,
                "trace":trace,"trace_sha256":hashlib.sha256(canonical(trace)).hexdigest(),
                "checkpoint_sha256":hashlib.sha256(blob).hexdigest(),
                "checkpoint_bytes":len(blob)})
    finally:env.close()
    assert totals["episodes"]==len(P["fresh_public_dynamic_dev_seeds"])
    return totals,episodes

def main():
    import gymnasium,minigrid
    ap=argparse.ArgumentParser()
    ap.add_argument("--arm",choices=P["arms"],required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    c20.check_source()
    assert P["original_source"] if "original_source" in P else P["source"].split("@")[-1]=="7f5853792ea7f04f75614661006d87fcf949f26d"
    t0=time.process_time()
    fit,fit_sha,fit_counts=c20.fit_data()
    learner=model_make(args.arm,fit)
    t1=time.process_time()
    totals,episodes=dynamic_experiment(args.arm,learner)
    t2=time.process_time()
    result={"schema":P["schema"],"arm":args.arm,"upstream":P["source"].split("@")[-1],
        "native_head":P["original_native"].split()[-1],
        "protocol_sha256":hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest(),
        "fit_sha256":fit_sha,"fit_rows":len(fit),"fit_counts":fit_counts,
        "totals":totals,"episodes":episodes,
        "max_checkpoint_bytes":max(x["checkpoint_bytes"] for x in episodes),
        "fit_cpu_seconds":round(t1-t0,6),"dev_cpu_seconds":round(t2-t1,6),
        "max_process_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python":sys.version.split()[0],"gymnasium":gymnasium.__version__}
    Path(args.out).write_bytes(canonical(result)+b"\n")
    print("R7C22_SOURCE_ORIGINAL_DYNAMIC",args.arm,json.dumps(totals,sort_keys=True))
if __name__=="__main__":main()
