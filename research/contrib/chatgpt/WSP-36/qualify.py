"""WSP-36 full candidate qualification. Never substitute focused DEV for final regression."""
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

def main():
    receipt = {
        "schema":"wsp36.full-regression.v1",
        "sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "tree":subprocess.check_output(["git","rev-parse","HEAD^{tree}"],text=True).strip(),
        "python":sys.version, "platform":platform.platform(), "steps":[], "unique_tests":0
    }
    steps = [
        ("WSP36-focused",[sys.executable,"-m","unittest","discover",
                          "-s","research/contrib/chatgpt/WSP-36","-p","test_*.py","-v"]),
        ("WSP36-DEV",[sys.executable,"research/contrib/chatgpt/WSP-36/run_dev.py",
                      "--cohort","DEV"]),
        ("full-WSP01-35",[sys.executable,"research/contrib/chatgpt/WSP-35/qualify.py"]),
        ("frozen-WSP35-PRIMARY",[sys.executable,"research/contrib/chatgpt/WSP-35/run_dev.py",
                                  "--cohort","PRIMARY"]),
        ("permanent-atlas",[sys.executable,"scripts/build_code_atlas.py",
                             "--check-if-present"]),
        ("clean-source",["git","diff","--exit-code"])
    ]
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE":"1"}
    for name, command in steps:
        started = time.perf_counter()
        p = subprocess.run(command,text=True,capture_output=True,encoding="utf-8",
                           errors="replace",env=env)
        output = p.stdout + p.stderr
        ntests = sum(int(n) for n in re.findall(r"Ran (\d+) tests? in",output))
        receipt["unique_tests"] += ntests
        receipt["steps"].append({"name":name,"seconds":round(time.perf_counter()-started,6),
                                 "exit_code":p.returncode,"tests":ntests,
                                 "sha256":hashlib.sha256(output.encode()).hexdigest()})
        print("WSP36_STEP "+name+"\n"+output,flush=True)
        if p.returncode:
            receipt["status"]="FAIL"
            print("WSP36_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)
            raise SystemExit(p.returncode)
    receipt["status"]="PASS"
    print("WSP36_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)

if __name__=="__main__":main()
