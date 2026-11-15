"""FKP15 direct numerical 16-step return memory and genuinely fully fitted controls."""
from __future__ import annotations
import hashlib
import struct
import numpy as np

DIM=393
BINS=4096
ACTIONS=9
LEARN_SEEDS=(1212,3434)
EPOCHS=24
ALPHAS=(0.1,1.0,10.0)


def _features(rows):
    x=np.stack([r["x"] for r in rows]).astype(np.float32)
    y=np.asarray([r["real_return"] for r in rows],dtype=np.float32)
    if x.ndim!=2 or x.shape[1]!=DIM or len(y)!=len(x) or not np.isfinite(y).all():
        raise ValueError("FKP15_INVALID_PUBLIC_FITTING_DATA")
    return x,y


def _action(x):
    if x.shape!=(DIM,) or not np.isfinite(x).all():
        raise ValueError("FKP15_INVALID_PUBLIC_FEATURE")
    a=int(np.argmax(x[384:]))
    if x[384+a]!=1 or int(np.count_nonzero(x[384:]))!=1:
        raise ValueError("FKP15_ACTION_ONEHOT")
    return a


def _coarse(frame):
    return frame.reshape(8,8,3).reshape(2,4,2,4,3).mean(axis=(1,3))


class DirectReturnMemory:
    """Fixed-capacity, associative direct numerical writes, no gradients."""
    MAGIC=b"F15D"
    def __init__(self,streams=2):
        if streams not in (1,2):raise ValueError("FKP15_BAD_STREAM_COUNT")
        self.streams=streams
        self.sums=np.zeros((streams,BINS),dtype="<f8")
        self.counts=np.zeros((streams,BINS),dtype="<f8")
        self.events=0

    def indices(self,row):
        a=_action(row)
        former=_coarse(row[:192])
        current=_coarse(row[192:384])
        q0=np.clip(np.rint(current*7),0,7).astype(np.uint8)
        q1=np.clip(np.rint((current-former+1)*4),0,8).astype(np.uint8)
        keys=[]
        for k,grid in enumerate((q0,q1)[:self.streams]):
            digest=hashlib.blake2b(grid.tobytes()+bytes((a,k)),digest_size=8).digest()
            keys.append(9+int.from_bytes(digest,"little")%(BINS-9))
        return a,tuple(keys)

    def update(self,row,actual_return):
        if not np.isfinite(actual_return) or abs(float(actual_return))>100:
            raise ValueError("FKP15_UNSAFE_PUBLIC_RETURN")
        a,keys=self.indices(row)
        if any(self.counts[k,key]>=2**32-2 or self.counts[k,a]>=2**32-2
               for k,key in enumerate(keys)):
            raise ValueError("FKP15_CAPACITY_EXHAUSTED")
        for stream,key in enumerate(keys):
            self.sums[stream,a]+=float(actual_return)
            self.counts[stream,a]+=1
            self.sums[stream,key]+=float(actual_return)
            self.counts[stream,key]+=1
        self.events+=1

    def fit(self,rows):
        for r in rows:self.update(r["x"],r["real_return"])
        return self

    def predict(self,rows):
        x=np.asarray(rows,dtype=np.float32)
        if x.ndim!=2 or x.shape[1]!=DIM:raise ValueError("FKP15_PREDICTION_SHAPE")
        out=[]
        for row in x:
            a,keys=self.indices(row)
            values=[]
            for stream,key in enumerate(keys):
                count=self.counts[stream,key]
                prior=(self.sums[stream,a]/self.counts[stream,a]
                       if self.counts[stream,a] else 0.)
                values.append((self.sums[stream,key]+5*prior)/(count+5))
            out.append(sum(values)/len(values))
        return np.asarray(out,dtype=np.float64)

    @property
    def raw_weights_bytes(self):
        return self.sums.nbytes+self.counts.nbytes

    def snapshot(self):
        payload=(self.MAGIC+struct.pack("<II",self.streams,self.events)
                 +self.sums.tobytes(order="C")+self.counts.tobytes(order="C"))
        return payload+hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or len(blob)<44 or blob[:4]!=cls.MAGIC:
            raise ValueError("FKP15_COLD_INVALID")
        if hashlib.sha256(blob[:-32]).digest()!=blob[-32:]:
            raise ValueError("FKP15_COLD_TAMPERED")
        streams,events=struct.unpack("<II",blob[4:12])
        obj=cls(streams)
        needed=12+obj.raw_weights_bytes+32
        if len(blob)!=needed:raise ValueError("FKP15_COLD_SIZE")
        one=streams*BINS*8
        obj.sums[:]=np.frombuffer(blob,dtype="<f8",count=streams*BINS,offset=12).reshape(streams,BINS)
        obj.counts[:]=np.frombuffer(blob,dtype="<f8",count=streams*BINS,offset=12+one).reshape(streams,BINS)
        if not np.isfinite(obj.sums).all() or not np.isfinite(obj.counts).all() or np.any(obj.counts<0):
            raise ValueError("FKP15_COLD_DATA_BAD")
        obj.events=events
        if obj.snapshot()!=blob:raise ValueError("FKP15_COLD_BYTE_PARITY")
        return obj


class MLPModel:
    def __init__(self,torch):
        self.torch=torch
        nn=torch.nn
        self.net=nn.Sequential(nn.Linear(DIM,64),nn.ReLU(),
            nn.Linear(64,64),nn.ReLU(),nn.Linear(64,1))
    def __call__(self,x):
        return self.net(x).reshape(-1)


class GRUModel:
    def __init__(self,torch):
        self.torch=torch
        nn=torch.nn
        class Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.gru=nn.GRU(192,64,batch_first=True)
                self.head=nn.Linear(73,1)
            def forward(self,x):
                seq=x[:,:384].reshape(-1,2,192)
                _,h=self.gru(seq)
                return self.head(torch.cat((h[-1],x[:,384:]),dim=1)).reshape(-1)
        self.net=Net()
    def __call__(self,x):
        return self.net(x).reshape(-1)


def _mse(pred,true):
    return float(np.square(np.asarray(pred,dtype=np.float64)-true).mean())


def fit_controls(train,validation):
    """Full, non-skipped strong conventional training on identical real data."""
    import torch
    torch.set_num_threads(2)
    x,y=_features(train)
    vx,vy=_features(validation)
    trained={}
    receipts={}
    xt=torch.tensor(x,dtype=torch.float32)
    yt=torch.tensor(y,dtype=torch.float32)
    vxt=torch.tensor(vx,dtype=torch.float32)
    for name,maker in (("MLP_FROZEN",MLPModel),("GRU_FROZEN",GRUModel)):
        models=[]
        for seed in LEARN_SEEDS:
            torch.manual_seed(seed)
            model=maker(torch).net
            opt=torch.optim.Adam(model.parameters(),lr=0.001,weight_decay=0.0001)
            for epoch in range(EPOCHS):
                rng=torch.Generator().manual_seed(seed+epoch*997)
                order=torch.randperm(len(xt),generator=rng)
                model.train()
                for ids in order.split(128):
                    opt.zero_grad(set_to_none=True)
                    pred=model(xt[ids])
                    loss=torch.mean((pred-yt[ids])**2)
                    loss.backward()
                    opt.step()
            model.eval()
            with torch.no_grad():
                score=_mse(model(vxt).cpu().numpy(),vy)
            models.append((score,seed,model))
        score,seed,model=min(models,key=lambda item:(item[0],item[1]))
        trained[name]=model
        receipts[name]={"trained_epochs_each":EPOCHS,"trained_seeds":list(LEARN_SEEDS),
                        "all_validation_mse":[float(x[0]) for x in models],
                        "selected_seed":seed,"selected_val_mse":score,
                        "parameters":sum(p.numel() for p in model.parameters())}
    # Regression baseline: each candidate fully solves the same data,
    # regularization choice selected only by independent source VAL.
    aug=np.concatenate((x.astype(np.float64),np.ones((len(x),1))),axis=1)
    vaug=np.concatenate((vx.astype(np.float64),np.ones((len(vx),1))),axis=1)
    xtx=aug.T@aug
    xty=aug.T@y.astype(np.float64)
    fitted=[]
    for alpha in ALPHAS:
        penalty=np.eye(394)*alpha
        penalty[-1,-1]=0.
        beta=np.linalg.solve(xtx+penalty,xty)
        fitted.append((_mse(vaug@beta,vy),alpha,beta))
    mse,alpha,beta=min(fitted,key=lambda item:(item[0],item[1]))
    trained["RIDGE_FROZEN"]=beta
    receipts["RIDGE_FROZEN"]={"alphas":list(ALPHAS),"validation_mse":[float(v[0]) for v in fitted],
                              "selected_alpha":alpha,"selected_val_mse":mse,
                              "parameters":len(beta)}
    return torch,trained,receipts


def predict_control(torch,model,x):
    x=np.asarray(x,dtype=np.float32)
    if isinstance(model,np.ndarray):
        return np.concatenate((x.astype(np.float64),np.ones((len(x),1))),axis=1)@model
    model.eval()
    with torch.no_grad():
        return model(torch.from_numpy(x)).cpu().numpy().astype(np.float64).reshape(-1)
