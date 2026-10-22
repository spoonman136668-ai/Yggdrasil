"""MR34I5: training-free NumPy CPU dispatch investigation on frozen source-public logits.
No original model/trainer/actor or protected first-use source is modified.
"""
import hashlib,json,os,platform,struct,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
PARENT="43e1fd51fc5cd7193978b527daa67d3f02314db8"
S4C1="8e1561eb1a542e21307bac669c42435cf48e59bd"
SOURCES={"FaramaMiniGridDoorKey8":"7f5853792ea7f04f75614661006d87fcf949f26d",
         "DeepMindPycolabApprehend":"6504c8065dd5322438f23a2a9026649904f3322a"}
COHORTS=(("canonical_frozen_boundaries",42),("canonical_seeded_binary64_inputs",128),
         ("FaramaMiniGridDoorKey8",160),("DeepMindPycolabApprehend",160))
ARMS=(("original_default",""),("disable_FMA3","FMA3"),
      ("disable_AVX2_FMA3","AVX2,FMA3"))
def sha(data):return hashlib.sha256(data).hexdigest()
def canon(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)
def pack(xs):return b"".join(struct.pack("<d",float(x)) for x in xs)
def cmd(*argv):return subprocess.check_output(argv,text=True).strip()
def clean(root,expected):
    root=Path(root).resolve()
    if cmd("git","-C",str(root),"rev-parse","HEAD")!=expected or cmd("git","-C",str(root),"status","--porcelain"):
        raise ValueError("MR34I5_SOURCE_IDENTITY_OR_WORKTREE_DRIFT")
    return root
def freeze():
    p=json.loads((HERE/"frozen_protocol.json").read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr34i5.source-nonlearning-numpy-dispatch.v1"
        or p["exact_MR34I4_parent_commit"]!=PARENT
        or p["exact_original_S4C1_commit"]!=S4C1
        or p["original_third_party_git_commits"]!=SOURCES
        or tuple(tuple(x) for x in p["cohort_order_and_lengths"])!=COHORTS
        or tuple((x["name"],x["disable"]) for x in p["single_variable_arms_in_order"])!=ARMS
        or p["numpy_runtime_version"]!="1.26.4" or p["python_runtime_version"]!="3.11"
        or any(p[k] is not True for k in ("no_original_model_source_change",
           "no_learner_training_or_optimizer","no_new_development_or_held_source_use",
           "no_qualified_scientific_first_use","no_original_MR34I4_protocol_revision",
           "source_and_agent_authenticity_required",
           "require_independent_windows_and_linux_replicates_each_two"))):
        raise ValueError("MR34I5_FROZEN_PROTOCOL_DRIFT")
    return p
def worker(json_path,mode):
    # NumPy import happens ONLY after a fresh subprocess sets CPU dispatch flags.
    import numpy as np
    import psutil
    from decimal import Decimal,Context,ROUND_HALF_EVEN,localcontext
    if sys.version_info[:2]!=(3,11) or np.__version__!="1.26.4":
        raise ValueError("MR34I5_RUNTIME_VERSION_DRIFT")
    arms=dict(ARMS)
    if mode not in arms or os.environ.get("NPY_DISABLE_CPU_FEATURES","")!=arms[mode]:
        raise ValueError("MR34I5_DISPATCH_MODE_DRIFT")
    features=dict(np.core._multiarray_umath.__cpu_features__)
    for flag in arms[mode].split(",") if arms[mode] else ():
        if features.get(flag) is True:
            raise ValueError("MR34I5_CPU_FEATURE_NOT_DISABLED_"+flag)
    rows=json.loads(Path(json_path).read_text(encoding="utf-8"))
    if tuple((z["cohort"],len(z["hex_values"])) for z in rows)!=COHORTS:
        raise ValueError("MR34I5_PUBLIC_CORPUS_SHAPE_DRIFT")
    start=time.process_time_ns()
    out=[]
    for row in rows:
        xs=np.asarray([float.fromhex(s) for s in row["hex_values"]],dtype=np.float64)
        if not np.isfinite(xs).all() or sha(pack(xs))!=row["source_sha"]:
            raise ValueError("MR34I5_PUBLIC_INPUT_BYTE_DRIFT")
        pad=(-len(xs))%8
        if pad:xs=np.concatenate((xs,np.zeros(pad,dtype=np.float64)))
        ex=np.empty_like(xs);prob=np.empty_like(xs)
        for i in range(0,len(xs),8):
            v=xs[i:i+8];e=np.exp(-np.clip(v,-35.,35.));ex[i:i+8]=e
            prob[i:i+8]=1./(1.+e)
        ref=[]
        for v in xs:
            x=min(35.,max(-35.,float(v)))
            with localcontext(Context(prec=80,rounding=ROUND_HALF_EVEN)):
                d=Decimal.from_float(x)
                ref.append(float(Decimal(1)/(Decimal(1)+(-d).exp())))
        out.append({"cohort":row["cohort"],"n":len(row["hex_values"]),"pad":pad,
                    "input_hex":pack(xs).hex(),"exp_hex":pack(ex).hex(),
                    "p_hex":pack(prob).hex(),"ref_hex":pack(ref).hex(),
                    "input_sha":sha(pack(xs[:len(row["hex_values"])])),"exp_sha":sha(pack(ex)),
                    "p_sha":sha(pack(prob)),"ref_sha":sha(pack(ref))})
    if sys.platform=="win32":
        peak=getattr(psutil.Process().memory_info(),"peak_wset",None)
        if not peak:raise ValueError("MR34I5_WINDOWS_PEAK_RSS_MISSING")
    elif sys.platform.startswith("linux"):
        import resource
        peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    else:raise ValueError("MR34I5_UNSUPPORTED_OS")
    return {"mode":mode,"disabled":arms[mode],"features":{k:features.get(k) for k in
                    ("AVX512F","AVX2","FMA3")},"numpy_version":np.__version__,
            "python_version":platform.python_version(),"cpu_ns":time.process_time_ns()-start,
            "peak_rss_bytes":int(peak),"rows":out,"scientific_first_use":False}
def main(audit,s4c1,farama,pycolab):
    p=freeze();audit=Path(audit).resolve()
    if cmd("git","-C",str(audit),"merge-base","HEAD",PARENT)!=PARENT:
        raise ValueError("MR34I5_PREDECESSOR_ANCESTRY_DRIFT")
    original=subprocess.check_output(["git","-C",str(audit),"show",
        PARENT+":research/mr34i4/kernel_probe.py"])
    if original!=(audit/"research/mr34i4/kernel_probe.py").read_bytes():
        raise ValueError("MR34I5_PRIOR_ORIGINAL_PROBE_DRIFT")
    s4c1=clean(s4c1,S4C1)
    roots={"FaramaMiniGridDoorKey8":clean(farama,SOURCES["FaramaMiniGridDoorKey8"]),
           "DeepMindPycolabApprehend":clean(pycolab,SOURCES["DeepMindPycolabApprehend"])}
    # Exact original MR34I4 input producer, no replacement simulation.
    for path in (audit,s4c1,*roots.values()):sys.path.insert(0,str(path))
    from research.mr34i4.kernel_probe import frozen,static_cases,original_source_u
    if sha((audit/"research/mr34i4/frozen_protocol.json").read_bytes())!= \
            "4254db799efa9d83a7dc6666d9501d64c0490355f9e02e94ed38c10dcbea214d":
        raise ValueError("MR34I5_PREVIOUS_FROZEN_MR34I4_DRIFT")
    edge,random_inputs=static_cases(frozen())
    cohorts=[("canonical_frozen_boundaries",edge),
             ("canonical_seeded_binary64_inputs",random_inputs)]
    custody={}
    for family,root in roots.items():
        xs,proof=original_source_u(root,family)
        if proof["source_original_first_preaction_logit_binary64_sha256"]!= \
           p["original_MR34I4_source_u_sha256"][family]:
            raise ValueError("MR34I5_AUTHENTIC_ORIGINAL_SOURCE_LOGIT_DRIFT")
        cohorts.append((family,xs));custody[family]=proof
    if tuple((k,len(xs)) for k,xs in cohorts)!=COHORTS:
        raise ValueError("MR34I5_FROZEN_490_INPUT_COUNT_DRIFT")
    corpus=[{"cohort":k,"hex_values":[float(x).hex() for x in xs],
             "source_sha":sha(pack(xs))} for k,xs in cohorts]
    results=[]
    with tempfile.TemporaryDirectory(prefix="mr34i5-",dir=os.getenv("RUNNER_TEMP") or None) as tmp:
        path=Path(tmp)/"public-previously-consumed.json"
        path.write_text(canon(corpus),encoding="utf-8")
        for mode,disabled in ARMS:
            env=dict(os.environ);env["NPY_DISABLE_CPU_FEATURES"]=disabled
            env["PYTHONDONTWRITEBYTECODE"]="1"
            cp=subprocess.run([sys.executable,"-B",str(HERE/"dispatch_probe.py"),
                "--worker",str(path),mode],env=env,text=True,capture_output=True,timeout=120)
            if cp.returncode:
                raise ValueError("MR34I5_CPU_CHILD_FAILED "+mode+" "+cp.stderr[-1600:])
            result=json.loads(cp.stdout)
            if len(result["rows"])!=4:raise ValueError("MR34I5_CHILD_REPORT_DRIFT")
            for stage,expected in zip(result["rows"],corpus):
                if stage["input_sha"]!=expected["source_sha"]:
                    raise ValueError("MR34I5_CHILD_INPUT_CHANGED")
                print("MR34I5_DISPATCH_RAW="+canon({
                    "mode":mode,"cohort":stage["cohort"],"source_binary64":stage["input_hex"],
                    "exp_binary64":stage["exp_hex"],"sigmoid_binary64":stage["p_hex"],
                    "decimal_binary64":stage["ref_hex"]}),flush=True)
            results.append({k:v for k,v in result.items() if k!="rows"}|
                {"cohort_shas":[{k:v for k,v in z.items() if k in
                 ("cohort","n","input_sha","exp_sha","p_sha","ref_sha")}
                 for z in result["rows"]]})
    for name,root in roots.items():clean(root,SOURCES[name])
    clean(s4c1,S4C1)
    if cmd("git","-C",str(audit),"status","--porcelain"):
        raise ValueError("MR34I5_AUDIT_REPO_DIRTY")
    print("MR34I5_DISPATCH_SUMMARY="+canon({
        "protocol_sha256":sha((HERE/"frozen_protocol.json").read_bytes()),
        "parent_commit":PARENT,"original_model_commit":S4C1,"source_custody":custody,
        "original_public_input_count":490,"cohort_source_sha":{
            z["cohort"]:z["source_sha"] for z in corpus},
        "per_child_CPU_dispatch":results,
        "cross_OS_numerical_admission":"PENDING_INDEPENDENT_COMPARISON",
        "original_train_checkpoint":"NO_GO","scientific_first_use":False,
        "G29_and_full_regression":"SEPARATE_FAIL_CLOSED"}),flush=True)
def local_smoke():
    import numpy as np
    v=np.array([-35.,-8.,-1.,0.,1.,8.,32.,35.],dtype=np.float64)
    assert np.all(np.diff(1./(1.+np.exp(-np.clip(v,-35.,35.))))>0)
    assert pack(v)==bytes.fromhex(pack(v).hex())
    print("MR34I5_STATIC_SMOKE=PASS_NOT_NATIVE")
if __name__=="__main__":
    if len(sys.argv)==2 and sys.argv[1]=="--selftest":local_smoke()
    elif len(sys.argv)==4 and sys.argv[1]=="--worker":
        print(canon(worker(sys.argv[2],sys.argv[3])))
    elif len(sys.argv)==5:main(*sys.argv[1:])
    else:raise SystemExit("MR34I5: AUDIT ORIGINAL_S4C1 FARAMA PYCOLAB")
