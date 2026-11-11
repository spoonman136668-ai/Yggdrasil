"""WSP19 frozen whole-process cost assay. Implementation-dependent CPU timing."""
import hashlib
import importlib.util
import json
import math
import platform
import random
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

SEEDS=(17,29,43)
WORKLOADS=(1,32,1024)
METHODS=('compiled','symbolic','adam8hot','mlp')
PUBLIC=(0,1,2,4,7)
HIDDEN=(3,5,6)
CONTEXTS=tuple(tuple((i>>j)&1 for j in range(3)) for i in range(8))


def observations(signature):
    return tuple((CONTEXTS[i],(signature>>j)&1) for j,i in enumerate(PUBLIC))


def fresh_reference():
    path=Path(__file__).resolve().parents[1]/'WSP-14'/'nand_program.py'
    spec=importlib.util.spec_from_file_location('wsp19_fresh_reference',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


def mlp_forward(w,x):
    h=tuple(math.tanh(sum(w[4*j+i]*x[i] for i in range(3))+w[4*j+3]) for j in range(8))
    z=sum(w[32+j]*h[j] for j in range(8))+w[40]
    return h,z


def train_mlp(obs,seed):
    rng=random.Random(seed)
    w=[rng.uniform(-.5,.5) for _ in range(41)]
    moment=[0.]*41;velocity=[0.]*41
    for step in range(1,4097):
        grad=[0.]*41;loss=0.
        for x,y in obs:
            h,z=mlp_forward(w,x)
            loss+=(max(z,0)+math.log1p(math.exp(-abs(z)))-y*z)/5
            p=1/(1+math.exp(-z))
            dz=(p-y)/5
            grad[40]+=dz
            for j in range(8):
                grad[32+j]+=dz*h[j]
                hidden=dz*w[32+j]*(1-h[j]*h[j])
                grad[4*j+3]+=hidden
                for i in range(3):grad[4*j+i]+=hidden*x[i]
        if loss<=.02:return tuple(w),step-1,loss
        for i in range(41):
            moment[i]=.9*moment[i]+.1*grad[i]
            velocity[i]=.999*velocity[i]+.001*grad[i]*grad[i]
            w[i]-=.05*(moment[i]/(1-.9**step))/(math.sqrt(velocity[i]/(1-.999**step))+1e-8)
    return tuple(w),4096,loss


def predict(method,model,x,ref):
    if method=='compiled':return model.predict(x)
    if method=='symbolic':return ref.symbolic_eval(model,x)
    if method=='adam8hot':return int(model[sum(b<<i for i,b in enumerate(x))]>0)
    return int(mlp_forward(model,x)[1]>0)


def build(method,seed):
    ref=fresh_reference()
    models=[];steps=0
    for sig in range(32):
        obs=observations(sig)
        if method in ('compiled','symbolic'):
            _cost,_mask,tree=ref.synthesize(obs)
            models.append(ref.NumericNand.from_program(tree) if method=='compiled' else tree)
        elif method=='adam8hot':
            weights,n,bce=ref.fully_train_8hot(obs)
            if bce>.02:raise AssertionError('WSP19_8HOT_NOT_CONVERGED')
            models.append(weights);steps+=n
        else:
            weights,n,bce=train_mlp(obs,seed)
            if bce>.02:raise AssertionError('WSP19_MLP_NOT_CONVERGED')
            models.append(weights);steps+=n
    return ref,models,steps


def checkpoint(method,models,ref):
    if method=='compiled':
        raw=[m.snapshot() for m in models]
        restored=[ref.NumericNand.restore(r) for r in raw]
        return restored,sum(map(len,raw))
    raw=json.dumps(models,sort_keys=True,separators=(',',':')).encode('ascii')
    return json.loads(raw),len(raw)


def run():
    start=time.perf_counter();runs=[];digests=[]
    for repeat,seed in enumerate(SEEDS):
        order=METHODS[repeat:]+METHODS[:repeat]
        for method in order:
            tracemalloc.start()
            tick=time.perf_counter()
            ref,models,steps=build(method,seed)
            construction=time.perf_counter()-tick
            tick=time.perf_counter()
            restored,byte_count=checkpoint(method,models,ref)
            custody=time.perf_counter()-tick
            _current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
            predictions=[];public=hidden=0
            for sig,(old,cold) in enumerate(zip(models,restored)):
                a=tuple(predict(method,old,x,ref) for x in CONTEXTS)
                b=tuple(predict(method,cold,x,ref) for x in CONTEXTS)
                if a!=b:raise AssertionError('WSP19_COLD_REPLAY')
                predictions.append(a)
                public+=sum(a[i]==y for i,(_x,y) in zip(PUBLIC,observations(sig)))
            for mask in range(256):
                sig=sum(((mask>>i)&1)<<j for j,i in enumerate(PUBLIC))
                hidden+=sum(predictions[sig][i]==((mask>>i)&1) for i in HIDDEN)
            if public!=160 or hidden!=384:raise AssertionError('WSP19_QUALITY_OR_INFORMATION_BOUND')
            measured={}
            for queries in WORKLOADS:
                tick=time.perf_counter();checksum=0
                for model in restored:
                    for q in range(queries):checksum+=predict(method,model,CONTEXTS[q%8],ref)
                elapsed=time.perf_counter()-tick
                measured[str(queries)]={'inference_seconds':elapsed,'end_to_end_seconds':construction+custody+elapsed,'checksum':checksum,'queries':32*queries}
            digest=hashlib.sha256(json.dumps(predictions,separators=(',',':')).encode()).hexdigest()
            digests.append((method,seed,digest))
            runs.append({'method':method,'repeat':repeat,'seed':seed,'public_correct':public,'hidden_correct':hidden,
                         'construction_seconds':construction,'checkpoint_restore_seconds':custody,
                         'tracemalloc_peak_bytes':peak,'serialized_checkpoint_bytes':byte_count,
                         'optimizer_steps':steps,'workloads':measured,'prediction_digest':digest})
    medians={m:{str(q):statistics.median(r['workloads'][str(q)]['end_to_end_seconds'] for r in runs if r['method']==m) for q in WORKLOADS} for m in METHODS}
    ratios={str(q):{'compiled_over_fastest_trained':medians['compiled'][str(q)]/min(medians[m][str(q)] for m in ('adam8hot','mlp')),
                    'compiled_over_symbolic':medians['compiled'][str(q)]/medians['symbolic'][str(q)]} for q in WORKLOADS}
    supported=all(v['compiled_over_fastest_trained']<=.5 for v in ratios.values())
    report={'schema':'wsp19.whole-process-dev.v1','engineering':'PASS',
            'frozen_efficiency_hypothesis':'DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE',
            'scientific_superiority':'UNVERIFIED; implementation-dependent authored DEV; compare exact symbolic as well',
            'repeats':3,'models_per_method_repeat':32,'cold_restored_models':384,
            'all_public_correct_per_method_repeat':160,'all_hidden_correct_per_method_repeat':384,
            'resident_scalars':{'mlp':41,'adam8hot':8,'compiled':'14sites x2sources+2weights plus metadata; bounded universal NAND/search prior external','symbolic':'variable NAND expression tree; external exact synthesis catalog'},
            'median_end_to_end_seconds':medians,'ratios':ratios,'runs':runs,
            'gradient_steps_compiled':0,'external_search_included':True,
            'total_actual_seconds':time.perf_counter()-start,
            'environment':{'python':sys.version,'platform':platform.platform()},
            'limitations':'Tracemalloc construction overhead included; inference untraced. Representation, inductive prior and capacity differ. Times describe these Python implementations/hardware, not hardware FLOPs/energy or universal architectural speed. One construction measured once then charged to each declared workload projection; actual elapsed reported separately. Program synthesis/compilation remains external. No independent first-use or stronger unfamiliar-world generalization.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    return report


if __name__=='__main__':run()
