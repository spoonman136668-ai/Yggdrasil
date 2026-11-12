"""Full inherited source regression plus WSP45, no selection or skipped tests."""
import json
import os
import platform
import re
import subprocess
import sys
import time


def main():
    steps=[
        ("full-WSP01-44",[sys.executable,"research/contrib/chatgpt/WSP-44/qualify.py"]),
        ("frozen-WSP44-PRIMARY",[sys.executable,"research/contrib/chatgpt/WSP-44/battery.py","--cohort","PRIMARY"]),
        ("WSP45-focused",[sys.executable,"-m","unittest","discover","-s","research/contrib/chatgpt/WSP-45","-p","test_*.py","-v"]),
        ("WSP45-DEV",[sys.executable,"research/contrib/chatgpt/WSP-45/battery.py","--cohort","DEV"]),
        ("clean-source",["git","diff","--exit-code"])]
    receipt={"schema":"wsp45.qualification.v1","sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
             "tree":subprocess.check_output(["git","rev-parse","HEAD^{tree}"],text=True).strip(),"platform":platform.platform(),
             "python":sys.version,"unique_tests":0,"steps":[]}
    for name,cmd in steps:
        t=time.perf_counter()
        p=subprocess.run(cmd,text=True,capture_output=True,encoding="utf-8",errors="replace",env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        out=p.stdout+p.stderr
        tests=sum(map(int,re.findall(r"Ran (\d+) tests? in",out)))
        receipt["unique_tests"]+=tests
        receipt["steps"].append({"name":name,"seconds":time.perf_counter()-t,"exit":p.returncode,"tests":tests})
        print("WSP45_STEP "+name+"\n"+out,flush=True)
        if p.returncode:
            receipt["status"]="FAIL"
            print("WSP45_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)
            raise SystemExit(p.returncode)
    receipt["status"]="PASS"
    print("WSP45_QUALIFICATION_RECEIPT "+json.dumps(receipt,sort_keys=True),flush=True)


if __name__=="__main__":main()
