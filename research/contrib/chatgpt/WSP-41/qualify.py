"""Full inherited source regression plus WSP41, no selection or skipped tests."""
import json
import os
import platform
import re
import subprocess
import sys
import time


def main():
    steps=[
        ("full-WSP01-40",[sys.executable,"research/contrib/chatgpt/WSP-40/qualify.py"]),
        ("frozen-WSP40-PRIMARY",[sys.executable,"research/contrib/chatgpt/WSP-40/battery.py","--cohort","PRIMARY"]),
        ("WSP41-focused",[sys.executable,"-m","unittest","discover","-s","research/contrib/chatgpt/WSP-41","-p","test_*.py","-v"]),
        ("WSP41-DEV",[sys.executable,"research/contrib/chatgpt/WSP-41/battery.py","--cohort","DEV"]),
        ("clean-source",["git","diff","--exit-code"])]
    receipt={"schema":"wsp41.qualification.v1","sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
             "tree":subprocess.check_output(["git","rev-parse","HEAD^{tree}"],text=True).strip(),"platform":platform.platform(),
             "python":sys.version,"unique_tests":0,"steps":[]}
    for name,cmd in steps:
        t=time.perf_counter()
        p=subprocess.run(cmd,text=True,capture_output=True,encoding="utf-8",errors="replace",env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        out=p.stdout+p.stderr
        tests=sum(map(int,re.findall(r"Ran (\d+) tests? in",out)))
        receipt["unique_tests"]+=tests
        receipt["steps"].append({"name":name,"seconds":time.perf_counter()-t,"exit":p.returncode,"tests":tests})
        print("WSP41_STEP "+name+"\n"+out,flush=True)
        if p.returncode:
            receipt["status"]="FAIL"
            print("WSP41_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)
            raise SystemExit(p.returncode)
    receipt["status"]="PASS"
    print("WSP41_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)


if __name__=="__main__":main()
