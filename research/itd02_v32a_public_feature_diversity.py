"""Bounded public-observation diversity check, no learning or environment internals."""
import hashlib,json,time,platform
import gymnasium as gym
import minigrid
SEEDS=(21,22,23)
ACTIONS=(0,1,2,1,2,0,2,0,2,1,2)
VOCAB=("LRV","MRV","docked_MRV","Nothing","docked_LRV")
def probe(seed):
    env=gym.make("MiniGrid-Empty-5x5-v0")
    try:
        obs,_=env.reset(seed=seed)
        rows=[]
        started=time.process_time_ns()
        for step,act in enumerate((None,)+ACTIONS):
            if act is not None:
                obs,r,term,trunc,_=env.step(act)
            else:
                r=0;term=False;trunc=False
            image=obs["image"]
            assert image.shape==(7,7,3)
            raw=image.tobytes()
            digest=hashlib.sha256(raw).digest()
            old=sum(int(image[row,3,0]!=0) for row in (0,1,2))%5
            projected=digest[0]%5
            direction=int(obs["direction"])
            assert 0<=direction<4
            rows.append({"step":step,"image_sha256":digest.hex(),
                         "old_code":old,"new_code":projected,"direction_code":direction,
                         "public_reward":float(r),"terminated":bool(term),"truncated":bool(trunc)})
            if term or trunc: break
        result={"seed":seed,"steps":len(rows)-1,
                "old_diversity":len(set(x["old_code"] for x in rows)),
                "new_diversity":len(set(x["new_code"] for x in rows)),
                "direction_diversity":len(set(x["direction_code"] for x in rows)),
                "process_cpu_ns":time.process_time_ns()-started,
                "public_trace_sha256":hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
        return result
    finally:env.close()
def main():
    assert gym.__version__=="1.2.1" and minigrid.__version__=="3.0.0"
    rows=[probe(s) for s in SEEDS]
    qualified=all(x["new_diversity"]>=2 and x["new_diversity"]>=x["old_diversity"] for x in rows)
    result={"schema":"itd02.v32a.public_diversity.v1","host":platform.system(),
            "classification":"V32A_PUBLIC_DIVERSITY_PASS__NO_SCIENCE" if qualified else "V32A_PUBLIC_DIVERSITY_NO_GO__NO_SCIENCE",
            "model_training":False,"heldout_evaluated":False,"scientific_first_use":False,"rows":rows}
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
