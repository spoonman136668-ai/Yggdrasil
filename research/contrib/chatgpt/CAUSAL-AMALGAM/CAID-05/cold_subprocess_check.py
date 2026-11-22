"""CAID-05 local engineering-only cold subprocess probe using exact native source.

24 public deterministic rows, no original-world actions and no claimed science.
"""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
TEST = Path(__file__).with_name('test_native_history_support.py')
spec = importlib.util.spec_from_file_location('caid05_original_tests', TEST)
original_tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original_tests)

native = original_tests.actual_native(24)
raw = native.checkpoint()
pin = hashlib.sha256(raw).hexdigest()
readout = original_tests.PublicHistorySupport.from_native(native, pin)
with tempfile.TemporaryDirectory() as work:
    p = Path(work) / 'state.json'
    p.write_bytes(raw)
    code = '''import hashlib, json, sys
from pathlib import Path
from yggdrasil.native_episode_experience import NativeEpisodeExperience
specfile=Path(sys.argv[2])
import importlib.util
spec=importlib.util.spec_from_file_location('caid05_support_child', specfile)
support=importlib.util.module_from_spec(spec); spec.loader.exec_module(support)
raw=Path(sys.argv[1]).read_bytes(); pin=hashlib.sha256(raw).hexdigest()
restored=NativeEpisodeExperience.restore(raw,pin)
read=support.PublicHistorySupport.from_native(restored,pin)
assert restored.checkpoint()==raw
print(json.dumps({'pin':pin,'fingerprint':read.fingerprint,'reward':read.reward((0,0),0,0,0),'observed':read.observed}))
'''
    env = dict(os.environ)
    env['PYTHONPATH'] = str(ROOT)
    run = subprocess.run([sys.executable, '-c', code, str(p),
                          str(Path(__file__).with_name('native_history_support.py'))],
                         cwd=ROOT, env=env, text=True, capture_output=True, check=True)
    child = json.loads(run.stdout)
    assert child['pin'] == pin
    assert child['fingerprint'] == readout.fingerprint
    assert child['observed'] == 24
    assert tuple(child['reward']) == readout.reward((0,0),0,0,0)
    damaged=bytearray(raw); damaged[-5]^=1
    try:
        native.restore(bytes(damaged), hashlib.sha256(bytes(damaged)).hexdigest())
    except ValueError: pass
    else: raise AssertionError('MUTATED_CHECKPOINT_WRONGLY_ADMITTED')
    print(json.dumps({'cold_child_pass': True,'parent_immutable':native.checkpoint()==raw,
           'observed':24,'checkpoint_sha256':pin,'cold_fingerprint_equal':True,
           'tampered_valid_pin_denied':True,'original_world_action_count':0},sort_keys=True))
