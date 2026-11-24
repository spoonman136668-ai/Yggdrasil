"""Clean-process engineering fixture; no Yggdrasil package or real data."""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


DRIVER = '''import hashlib, pathlib, sys
sys.path.insert(0, str(pathlib.Path.cwd()))
import torch
from session import Session
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)
rows=[(b'a',b'x'),(b'b',b'y'),(b'c',b'z'),(b'd',b'w')]
plan=dict(seed=7,epochs=3,batch_size=2,rate=.001,max_steps=6,max_bytes=24,mode='mixture',width=4,latent=2)
source=hashlib.sha256(b''.join(pathlib.Path(p).read_bytes() for p in ('session.py','learned_jepa.py','checkpoint.py'))).hexdigest()
root=pathlib.Path.cwd(); mode=sys.argv[1]
if mode=='resume':
    raw=(root/'partial.json').read_bytes(); digest=(root/'partial.sha256').read_text()
    s=Session.load(raw,sha256=digest,pairs=rows,source=source,plan=plan)
    s.advance(3)
else:
    s=Session(rows,source=source,**plan)
    s.advance(3 if mode=='partial' else 6)
raw,digest=s.save()
(root/(mode+'.json')).write_bytes(raw)
(root/(mode+'.sha256')).write_text(digest)
assert s.cursor == (3 if mode=='partial' else 6)
assert s.exposure == (12 if mode=='partial' else 24)
'''


class ColdSessionTests(unittest.TestCase):
    def test_fresh_process_continuation(self):
        origin = pathlib.Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as tmp:
            isolated = pathlib.Path(tmp)
            for name in ('session.py','learned_jepa.py','checkpoint.py'):
                shutil.copyfile(origin/name, isolated/name)
            for mode in ('full','partial','resume'):
                subprocess.run([sys.executable,'-I','-B','-c',DRIVER,mode],
                               cwd=isolated, check=True, timeout=120)
            self.assertEqual((isolated/'full.json').read_bytes(),
                             (isolated/'resume.json').read_bytes())
            self.assertEqual((isolated/'full.sha256').read_text(),
                             (isolated/'resume.sha256').read_text())


if __name__ == '__main__':
    unittest.main()
