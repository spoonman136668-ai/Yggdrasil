"""Genuine conventional fits with conservative exact-semantic-input caching."""
import hashlib
import json
from pathlib import Path
from controls import trained,predict,feature_table,RAW
OPT='adam|0.1|0.9|0.999|1e-8|BCE<=0.01|4096|round12readout'
OPT_SOURCE=hashlib.sha256((Path(__file__).resolve().parent.parent/'WSP-29/controls.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest()
class FitCache:
    def __init__(self):self.cache={};self.logical_fits=0;self.fresh_fits=0;self.hits=0;self.updates=0;self.max_BCE=0.;self.dot_multiplications=0;self.gradient_multiplications=0
    def fit(self,examples,width,context):
        # context includes upstream hashes,actual source/target fact state and representation.
        key=hashlib.sha256(json.dumps({'Xy':examples,'width':width,'context':context,'optimizer':OPT,'optimizer_source':OPT_SOURCE},sort_keys=True,separators=(',',':')).encode()).hexdigest();self.logical_fits+=1
        if key in self.cache:self.hits+=1;w,n,loss=self.cache[key]
        else:
            w,n,loss=trained(examples,width);self.cache[key]=(w,n,loss);self.fresh_fits+=1;self.updates+=n
            self.dot_multiplications+=len(examples)*width*(n+1);self.gradient_multiplications+=len(examples)*width*n
        if not loss<=.01:raise AssertionError('WSP31_NONCONVERGED_CACHED_FIT')
        self.max_BCE=max(self.max_BCE,loss);return w
