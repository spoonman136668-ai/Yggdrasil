"""Read-only public MiniGrid online native feasibility against two controls."""
import hashlib,json,time,platform
import gymnasium as gym
import minigrid
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS

ENV="MiniGrid-Empty-5x5-v0"
SEEDS=(11,12,13)
STEPS=24
ACTION_IDS={"TurnAround":0,"GoForward":2,"Backup":1}
OBS=("LRV","MRV","docked_MRV","docked_LRV")

def encode(obs,visual=False):
    assert type(obs) is dict and "direction" in obs and "image" in obs
    d=int(obs["direction"])
    assert 0<=d<4
    if visual:
        image=obs["image"]
        assert image.shape==(7,7,3)
        count=sum(int(image[row,3,0]!=0) for row in (0,1,2))
        return ("LRV","MRV","docked_MRV","Nothing","docked_LRV")[count%5]
    return OBS[d]

def run(arm,seed):
    env=gym.make(ENV)
    model=NativeTaskRingBridgeDev()
    try:
        obs,_=env.reset(seed=seed)
        if arm=="visual_frozen":
            ids=model.model_identities()
            model.start_frozen_evaluation(ids["native"],ids["memory"])
        else:
            ids=None
        history=[];codes=[];total=0.;start=time.process_time_ns()
        for step in range(STEPS):
            current=encode(obs,arm!="direction_fit")
            codes.append(current)
            model.start_observation(current)
            action=model.choose()
            obs,r,term,trunc,_=env.step(ACTION_IDS[action])
            assert isinstance(r,(float,int))
            total+=float(r)
            category=10 if r>0 else -3 if r<0 else 0
            model.accept_public_transition(action,encode(obs,arm!="direction_fit"),category,
                learning=(arm!="visual_frozen"),terminal=bool(term or trunc))
            history.append((step,action,float(r),bool(term),bool(trunc)))
            if term or trunc:
                break
        if arm=="visual_frozen":
            assert model.model_identities()==ids
        return {"arm":arm,"seed":seed,"steps":len(history),
                "total_real_reward":round(total,8),
                "completed":bool(history[-1][3] or history[-1][4]),
                "process_cpu_ns":time.process_time_ns()-start,
                "checkpoint_bytes":len(model.checkpoint()),
                "public_code_count":len(set(codes)),
                "model_identity":model.model_identities(),
                "trace_sha256":hashlib.sha256(json.dumps(history).encode()).hexdigest(),
                "actions":[x[1] for x in history]}
    finally:
        env.close()

def main():
    assert minigrid.__version__=="3.0.0"
    assert gym.__version__=="1.2.1"
    rows=[run(arm,seed) for seed in SEEDS for arm in ("direction_fit","visual_fit","visual_frozen")]
    assert len(rows)==9
    print(json.dumps({"schema":"itd02.v31z.public_visual_probe.v1",
       "classification":"V31Z_PUBLIC_VISUAL_PREPROCESSOR_EXPLORATORY_NO_GO__NO_SCIENCE",
       "system":platform.system(),"minigrid_version":minigrid.__version__,
       "gymnasium_version":gym.__version__,"reserved_holdout_evaluated":False,
       "scientific_first_use":False,"image_pixels_used_by_learner":True,
       "native_model_modified":False,"rows":rows},sort_keys=True))
if __name__=="__main__":main()
