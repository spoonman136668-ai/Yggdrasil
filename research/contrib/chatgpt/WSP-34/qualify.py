"""WSP-34 complete final regression; all prior tests and original frozen WSP33 DEV."""
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

def run():
    receipt = {"schema":"wsp34.full-regression.v1",
               "sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
               "tree":subprocess.check_output(["git","rev-parse","HEAD^{tree}"],text=True).strip(),
               "python":sys.version,"platform":platform.platform(),
               "steps":[],"unique_tests":0}
    steps=[("original",[sys.executable,"-m","unittest","discover","-s","tests","-p","test_*.py","-v"])]
    for n in list(range(1,18))+list(range(19,35)):
        folder="research/contrib/chatgpt/WSP-%02d"%n
        steps.append(("WSP%02d-tests"%n,
                     [sys.executable,"-m","unittest","discover","-s",folder,"-p","test_*.py","-v"]))
    for n in (33,34):
        steps.append(("WSP%02d-DEV"%n,[sys.executable,"research/contrib/chatgpt/WSP-%02d/run_dev.py"%n]))
    steps.extend([
        ("permanent-atlas",[sys.executable,"scripts/build_code_atlas.py","--check-if-present"]),
        ("clean-source",["git","diff","--exit-code"])])
    start=time.perf_counter()
    for label,command in steps:
        tick=time.perf_counter()
        proc=subprocess.run(command,capture_output=True,text=True,
                            encoding="utf-8",errors="replace",
                            env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        combined=proc.stdout+proc.stderr
        if label.endswith("-DEV") and proc.returncode == 0:
            report=json.loads(proc.stdout)
            receipt[label.lower().replace("-","_")]=report
            combined=json.dumps(report,sort_keys=True,indent=2)+proc.stderr
        print("\nWSP34_STEP "+label+"\n"+combined,flush=True)
        found=re.search(r"Ran (\d+) tests? in",combined)
        count=int(found.group(1)) if found else 0
        receipt["unique_tests"]+=count
        receipt["steps"].append({"name":label,"seconds":round(time.perf_counter()-tick,6),
                                 "exit_code":proc.returncode,"tests":count,
                                 "output_sha256":hashlib.sha256(combined.encode()).hexdigest()})
        if proc.returncode:
            receipt["status"]="FAIL"
            print("WSP34_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)
            raise SystemExit(proc.returncode)
    receipt["status"]="PASS"
    receipt["total_seconds"]=round(time.perf_counter()-start,6)
    print("WSP34_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)

if __name__=="__main__":
    run()
