"""Strong same-information symbolic WSP137 comparator.

Independent candidate enumeration and inference via the separately implemented
WSP135 symbolic control. Do not import WSP137 numerical chooser, numeric fit,
source/evaluator, true hidden law, or privileged full-grammar oracle.
"""
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import sys

P=Path(__file__).resolve().parents[1]/'WSP-135'/'controls.py'
S=spec_from_file_location('_wsp137_independent_wsp135_symbolic_bank',P)
BASE=module_from_spec(S);sys.modules[S.name]=BASE;S.loader.exec_module(BASE)
def fit_symbolic(rows):
    if len(rows)!=32 or len(set(x for x,y in rows))!=32:
        raise ValueError('SYMBOLIC_UNDERSAMPLED')
    best=17; selected=[]
    for i,cb in enumerate(BASE.codebooks()):
        out={}
        for x,y in rows:
            label=cb[x]
            old=out.get(label)
            if old is not None and old!=y:break
            out[label]=y
        else:
            n=len(out)
            if n<best:best=n;selected=[]
            if n==best and len(selected)<64:
                selected.append((i,tuple(out.get(j,-1) for j in range(16))))
    return selected

def infer_symbolic(selected,x):
    if not selected:return None
    zero=one=0
    codes=BASE.codebooks()
    for i,lut in selected:
        y=lut[codes[i][x]]
        if y==0:zero+=1
        if y==1:one+=1
    votes=zero+one
    if 5*votes<4*len(selected) or 10*max(zero,one)<9*votes:return None
    return int(one>=zero)
