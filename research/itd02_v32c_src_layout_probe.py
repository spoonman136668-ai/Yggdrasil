"""Preregistered public-only comparison of two real MiniGrid layouts."""
import hashlib,json,platform
import gymnasium as gym
import minigrid
TASKS=("MiniGrid-Empty-5x5-v0","MiniGrid-Empty-6x6-v0")
ACTIONS=(2,2,1,2,1,2)
def run(task,seed):
    env=gym.make(task)
    try:
        obs,_=env.reset(seed=seed)
        rows=[]
        for i,a in enumerate((None,)+ACTIONS):
            if a is not None: obs,reward,term,trunc,_=env.step(a)
            else: reward=0.;term=trunc=False
            image=obs["image"]
            assert image.shape==(7,7,3)
            local=tuple(tuple(int(k) for k in image[j,3,:]) for j in (2,3,4))
            rows.append({"step":i,"direction":int(obs["direction"]),
                "local":local,"image":hashlib.sha256(image.tobytes()).hexdigest(),
                "reward":float(reward)})
            if term or trunc:break
        geometry=[(x["direction"],x["local"]) for x in rows]
        return {"task":task,"seed":seed,"steps":len(rows)-1,
            "geometry_diversity":len(set(geometry)),
            "image_diversity":len(set(x["image"] for x in rows)),
            "geometry_digest":hashlib.sha256(json.dumps(geometry).encode()).hexdigest(),
            "image_digest":hashlib.sha256(json.dumps([x["image"] for x in rows]).encode()).hexdigest()}
    finally:env.close()
def main():
    assert gym.__version__=="1.2.1" and minigrid.__version__=="3.0.0"
    rows=[run(task,seed) for seed in (41,42) for task in TASKS]
    distinct=all(rows[k]["geometry_digest"]!=rows[k+1]["geometry_digest"] for k in (0,2))
    diverse=all(x["geometry_diversity"]>=2 for x in rows)
    output={"schema":"itd02.v32c.src.layout_public_discrimination.v1","host":platform.system(),
        "classification":"V32C_LAYOUT_PUBLIC_GEOMETRY_PASS__NO_SCIENCE" if distinct and diverse else "V32C_LAYOUT_PUBLIC_GEOMETRY_NO_GO__NO_SCIENCE",
        "layout_distinguished":distinct,"local_diverse":diverse,"model_trained":False,
        "reserved_holdout_evaluated":False,"scientific_first_use":False,"rows":rows}
    print(json.dumps(output,sort_keys=True))
    assert distinct and diverse,"PREREGISTERED_GEOMETRY_INFORMATION_FAILURE"
if __name__=="__main__":main()
