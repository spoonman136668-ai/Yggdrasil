"""WSP-39 broad state/action capability qualification on exact source."""
import hashlib,json,os,platform,re,subprocess,sys,time

def main():
    receipt={"schema":"wsp39.full-regression.v1",
             "sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
             "tree":subprocess.check_output(["git","rev-parse","HEAD^{tree}"],text=True).strip(),
             "python":sys.version,"platform":platform.platform(),"steps":[],"unique_tests":0}
    steps=[
      ("WSP39-focused-and-DEV",[sys.executable,"-m","unittest","discover","-s","research/contrib/chatgpt/WSP-39","-p","test_*.py","-v"]),
      ("WSP38-focused-and-DEV",[sys.executable,"-m","unittest","discover","-s","research/contrib/chatgpt/WSP-38","-p","test_*.py","-v"]),
      ("full-WSP01-37",[sys.executable,"research/contrib/chatgpt/WSP-37/qualify.py"]),
      ("frozen-WSP37-PRIMARY",[sys.executable,"research/contrib/chatgpt/WSP-37/battery.py","--cohort","PRIMARY"]),
      ("frozen-WSP38-PRIMARY",[sys.executable,"research/contrib/chatgpt/WSP-38/battery.py","--cohort","PRIMARY"]),
      ("permanent-atlas",[sys.executable,"scripts/build_code_atlas.py","--check-if-present"]),
      ("clean-source",["git","diff","--exit-code"])
    ]
    env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"}
    for name,cmd in steps:
        started=time.perf_counter()
        p=subprocess.run(cmd,text=True,capture_output=True,encoding="utf-8",errors="replace",env=env)
        output=p.stdout+p.stderr
        tests=sum(int(n) for n in re.findall(r"Ran (\d+) tests? in",output))
        receipt["unique_tests"]+=tests
        receipt["steps"].append({"name":name,"seconds":round(time.perf_counter()-started,6),
                                 "exit_code":p.returncode,"tests":tests,
                                 "sha256":hashlib.sha256(output.encode()).hexdigest()})
        print("WSP39_STEP "+name+"\n"+output,flush=True)
        if p.returncode:
            receipt["status"]="FAIL"
            print("WSP39_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)
            raise SystemExit(p.returncode)
    receipt["status"]="PASS"
    print("WSP39_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)
if __name__=="__main__": main()
