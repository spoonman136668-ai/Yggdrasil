"""V32B source-only real public visual feature relevance probe."""
import hashlib,json,platform
import gymnasium as gym
import minigrid

SCRIPTS={"forward":(2,2,2,2,2,2),"turn_forward":(1,2,1,2,1,2)}
def run(seed,script):
    env=gym.make("MiniGrid-Empty-5x5-v0")
    try:
        o,_=env.reset(seed=seed)
        rows=[]
        for step,act in enumerate((None,)+SCRIPTS[script]):
            if act is not None:o,r,term,trunc,_=env.step(act)
            else:r=0.;term=trunc=False
            image=o["image"]
            assert image.shape==(7,7,3)
            digest=hashlib.sha256(image.tobytes()).hexdigest()
            # Raw public center/forward tile encodings, never named object or hidden map.
            tiles=tuple(tuple(int(x) for x in image[k,3,:]) for k in (2,3,4))
            rows.append({"step":step,"image_sha":digest,"hash_code":int(digest[:2],16)%5,
                         "direction":int(o["direction"]),"front_tile":tiles,
                         "reward":float(r)})
            if term or trunc:break
        return {"seed":seed,"script":script,"steps":len(rows)-1,
                "distinct_images":len(set(x["image_sha"] for x in rows)),
                "distinct_hash_codes":len(set(x["hash_code"] for x in rows)),
                "distinct_public_geometry":len(set((x["direction"],x["front_tile"]) for x in rows)),
                "trace_sha":hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
                "rows":rows}
    finally:env.close()
def main():
    assert gym.__version__=="1.2.1" and minigrid.__version__=="3.0.0"
    runs=[run(seed,script) for seed in (31,32) for script in SCRIPTS]
    differences=all(next(x for x in runs if x["seed"]==seed and x["script"]=="forward")["trace_sha"] != next(x for x in runs if x["seed"]==seed and x["script"]=="turn_forward")["trace_sha"] for seed in (31,32))
    feature=all(x["distinct_public_geometry"]>=2 for x in runs)
    passed=differences and feature
    out={"schema":"itd02.v32b.src.public_semantic_feature.v1","classification":"V32B_PUBLIC_FEATURES_DIVERSE__NO_SCIENCE" if passed else "V32B_PUBLIC_FEATURES_NO_GO__NO_SCIENCE","host":platform.system(),"independent_action_scripts":differences,"geometry_feature_diversity":feature,"model_training":False,"heldout_evaluated":False,"scientific_first_use":False,"runs":[{k:v for k,v in x.items() if k!="rows"} for x in runs]}
    print(json.dumps(out,sort_keys=True))
    assert passed,"PRESPECIFIED_PUBLIC_GEOMETRY_DIVERSITY_NOT_MET"
if __name__=="__main__":main()
