"""WSP-35 exact-source full regression; includes all prior frozen DEV suites."""
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

def run():
    receipt={"schema":"wsp35.full-regression.v1",
       "sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
       "tree":subprocess.check_output(["git","rev-parse","HEAD^{tree}"],text=True).strip(),
       "python":sys.version,"platform":platform.platform(),"steps":[],"unique_tests":0}
    steps=[("original",[sys.executable,"-m","unittest","discover","-s","tests","-p","test_*.py","-v"])]
    for n in list(range(1,18))+list(range(19,36)):
        folder="research/contrib/chatgpt/WSP-%02d"%n
        steps.append(("WSP%02d-tests"%n,[sys.executable,"-m","unittest","discover","-s",folder,"-p","test_*.py","-v"]))
    for n in (33,34):
        steps.append(("WSP%02d-DEV"%n,[sys.executable,"research/contrib/chatgpt/WSP-%02d/run_dev.py"%n]))
    steps.append(("WSP35-DEV",[sys.executable,"research/contrib/chatgpt/WSP-35/run_dev.py","--cohort","DEV"]))
    steps.extend([("permanent-atlas",[sys.executable,"scripts/build_code_atlas.py","--check-if-present"]),
                  ("clean-source",["git","diff","--exit-code"])])
    for name,cmd in steps:
        start=time.perf_counter()
        proc=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8",errors="replace",env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        combined=proc.stdout+proc.stderr
        match=re.search(r"Ran (\d+) tests? in",combined)
        n=int(match.group(1)) if match else 0
        receipt["unique_tests"]+=n
        receipt["steps"].append({"name":name,"seconds":round(time.perf_counter()-start,6),"exit_code":proc.returncode,"tests":n,"sha256":hashlib.sha256(combined.encode()).hexdigest()})
        print("WSP35_STEP "+name+"\n"+combined,flush=True)
        if proc.returncode:
            receipt["status"]="FAIL"
            print("WSP35_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)
            raise SystemExit(proc.returncode)
    receipt["status"]="PASS"
    print("WSP35_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)

if __name__=="__main__":run()
