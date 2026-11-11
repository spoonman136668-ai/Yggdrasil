"""WSP21 constructive EXTERNAL capacity oracle; not a native learner."""
import functools,hashlib,importlib.util,json,platform,sys,time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/"WSP-15"))
from structural import PlasticNand,context,LENGTHS
OBSERVED=(0,1,2,4,7,3)

@functools.lru_cache(maxsize=1)
def reference():
    path=Path(__file__).resolve().parents[1]/"WSP-14"/"nand_program.py"
    spec=importlib.util.spec_from_file_location("wsp21_external_reference",path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def evidence(sig):
    if type(sig) is not int or sig not in range(64):raise ValueError("WSP21_BAD_SIGNATURE")
    return tuple((context(i),(sig>>j)&1) for j,i in enumerate(OBSERVED))

def select(obs):
    if type(obs) is not tuple or len(obs)!=6:raise ValueError("WSP21_BAD_EVIDENCE")
    for pair,i in zip(obs,OBSERVED):
        if type(pair) is not tuple or len(pair)!=2 or type(pair[0]) is not tuple or pair[0]!=context(i) or any(type(v) is not int for v in pair[0]) or type(pair[1]) is not int or pair[1] not in (0,1):raise ValueError("WSP21_BAD_EVIDENCE")
    ref=reference()
    return min(((cost,mask,tree) for mask,(cost,tree) in ref.catalog().items()
                if all(ref.symbolic_eval(tree,x)==y for x,y in obs)),key=lambda t:(t[0],t[1]))

def embed(tree):
    compiled=reference().NumericNand.from_program(tree)
    if compiled.used>6:raise ValueError("WSP21_MORE_THAN_SIX_SITES")
    model=PlasticNand()
    for g in range(compiled.used):
        for side in range(2):
            src=compiled.sources[g][side]
            model.rows[2*g+side]=[int(i==src) for i in range(LENGTHS[2*g+side])]
    model.rows[-1]=[int(i==compiled.output) for i in range(9)]
    if not model.canonical():raise AssertionError("WSP21_BAD_EMBEDDING")
    return model

def run():
    start=time.perf_counter();ref=reference();certificates=[];hist={};cert=public=agreement=cold=lesion=hidden=symbolic_public=0;all_predictions=[]
    for sig in range(64):
        obs=evidence(sig);cost,mask,tree=select(obs)
        hist[str(cost)]=hist.get(str(cost),0)+1
        sym=tuple(ref.symbolic_eval(tree,context(i)) for i in range(8));all_predictions.append(sym)
        symbolic_public+=sum(sym[i]==y for i,(_x,y) in zip(OBSERVED,obs))
        if cost<=6:
            model=embed(tree);raw=model.snapshot();restored=PlasticNand.restore(raw)
            if restored.snapshot()!=raw:raise AssertionError("WSP21_COLD_BYTES")
            cold+=1;cert+=1
            for i in range(8):
                pred=model.predict(context(i));agreement+=pred==sym[i]
                if pred!=restored.predict(context(i)):raise AssertionError("WSP21_COLD_OUTPUT")
            public+=sum(model.predict(x)==y for x,y in obs)
            erased=PlasticNand()
            lesion+=sum(erased.predict(context(i))!=sym[i] for i in range(8))
            certificates.append({"signature":sig,"nand_sites":cost,"hypothesis_mask":mask,"rows":model.rows,"checkpoint_sha256":hashlib.sha256(raw).hexdigest()})
        else:certificates.append({"signature":sig,"selected_expression_sites":cost,"status":"UNRESOLVED_NOT_INFEASIBLE"})
    for mask in range(256):
        sig=sum(((mask>>i)&1)<<j for j,i in enumerate(OBSERVED))
        hidden+=sum(all_predictions[sig][i]==((mask>>i)&1) for i in (5,6))
    required=(symbolic_public==384 and public==cert*6 and agreement==cert*8 and cold==cert and hidden==256 and (cert==0 or lesion>0))
    report={"schema":"wsp21.six-site-capacity.v1","engineering":"PASS" if required else "FAIL",
      "capacity_classification":"CAPACITY_EXCUSE_FALSIFIED" if cert==64 else "UNRESOLVED",
      "scientific_superiority":"NONE; external constructive capacity certificates, not learning",
      "certified_signatures_of64":cert,"maximum_selected_tree_sites":max(map(int,hist)),"size_histogram":hist,
      "public_numeric_correct":public,"public_symbolic_correct":symbolic_public,"numeric_symbolic_agreement":agreement,
      "cold_restores":cold,"lesion_output_changes":lesion,"hidden_correct_of512":hidden,"candidate_mask_scans":16384,
      "resident_binary_synapses_per_certificate":75,"checkpoint_bytes":len(PlasticNand().snapshot()),
      "certificate_digest_sha256":hashlib.sha256(json.dumps(certificates,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
      "certificates":certificates,"seconds":time.perf_counter()-start,
      "environment":{"python":sys.version,"platform":platform.platform()},
      "limit":"Expression cost>6 is unresolved, not an infeasibility proof, because DAG sharing might fit. Oracle supplies programs externally; no native learning, hidden truth recovery, efficiency or unfamiliar transfer claim."}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report
if __name__=="__main__":run()
