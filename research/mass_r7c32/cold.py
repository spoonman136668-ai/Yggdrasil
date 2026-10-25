"""Cold OS policy action parity after ACTUAL step-three original-world returns."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from research.mass_r7c29.effects import sealed
from research.mass_r7c31.action_bridge import decision, source_sensor_update

ROOT=Path(__file__).resolve().parents[2]
COLD_CODE = """
import json, sys
from research.native.itd02.r1.native_policy import PublicGrid
from research.native.itd02.r3.navigator import Navigator
from research.mass_r7c29.effects import unseal
from research.mass_r7c30.independent_logistic import IndependentPublicLogistic
from research.mass_r7c31.action_bridge import decision,source_sensor_update
d=json.loads(sys.stdin.read())
nav=Navigator.restore(d['r3'].encode('utf-8'))
pub=PublicGrid(**d['public'])
source_sensor_update(nav,pub)
if d['arm']=='r3_original':
    action=nav.choose(pub)
else:
    model=(IndependentPublicLogistic.restore(d['predictor'].encode('utf-8'))
           if d['arm'].startswith('full9_')
           else unseal(d['predictor'].encode('utf-8')))
    action=decision(nav,pub,model)[1]
assert action==d['expected'],'C32_COLD_SELECTED_ACTION_DRIFT'
print('C32_COLD_SOURCE_POLICY_PARITY_PASS')
"""

def cold_policy(nav,model,arm,pub):
    snapshot=nav.snapshot()
    if arm=="r3_original":
        model_bytes=b""
    elif arm.startswith("full9_"):
        model_bytes=model.checkpoint()
    else:
        model_bytes=sealed(model)
    # The policy decision is made on a COPY with the same public-front update
    # that will occur at the beginning of the next physical source step.
    import copy
    navcopy=copy.deepcopy(nav)
    source_sensor_update(navcopy,pub)
    expected=(navcopy.choose(pub) if arm=="r3_original"
              else decision(navcopy,pub,model)[1])
    payload=json.dumps({"r3":snapshot.decode(),"predictor":model_bytes.decode(),
      "arm":arm,"public":pub.__dict__,"expected":expected})
    run=subprocess.run([sys.executable,"-B","-c",COLD_CODE],
      input=payload,text=True,capture_output=True,timeout=35,cwd=ROOT,
      env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
    if run.returncode or "C32_COLD_SOURCE_POLICY_PARITY_PASS" not in run.stdout:
        raise ValueError("C32_ORIGINAL_R3_AND_PREDICTOR_COLD_PARITY_FAILURE")
    return {"restored_in_fresh_process":True,
      "r3_checkpoint_bytes":len(snapshot),
      "model_checkpoint_bytes":len(model_bytes),
      "r3_checkpoint_sha256":hashlib.sha256(snapshot).hexdigest(),
      "model_checkpoint_sha256":hashlib.sha256(model_bytes).hexdigest()}
