"""Stage 6b repair controls, not primary learning evidence."""
import math
import torch
from torch import nn
from experiments.procedural_event_stage4_monarch import ProceduralMonarchLinear
from experiments.procedural_event_stage6b_qualification import (
    build_model, complete_batches, evaluate, matched_bigram, prerequisite_check,
    rank_audit, rank_safe_blocks,
)


def test_rank_and_memory():
    assert rank_safe_blocks(128, 512) == 16
    for seed in (42, 43):
        for g, expected in ((8, 64), (16, 128)):
            for a,b in ((128, 512), (512, 128)):
                torch.manual_seed(seed)
                m = ProceduralMonarchLinear(a,b,n_blocks=g,seed_dim=32,
                                             block_emb_dim=8,hyper_hidden=16,bias=False)
                with torch.no_grad():
                    assert int(torch.linalg.matrix_rank(m(torch.eye(a)))) == expected
    dense = build_model("dense")
    corrected = build_model("causal")
    assert dense.total_ffn_footprint()[1]/corrected.total_ffn_footprint()[1] >= 4
    for seed in (42,43):
        ranks = rank_audit(build_model("causal", seed=seed))
        assert len(ranks)==8 and all(r==n==128 for _,_,r,n in ranks)


def test_causal_and_random_prefix_in_train_and_eval():
    for arm in ("causal", "random"):
        m = build_model(arm, n_layers=2, dropout=0)
        x = torch.randint(0,256,(2,8))
        y = x.clone(); y[:,3:] = (x[:,3:]+1)%256
        # Freeze from training-only data, not either test sequence.
        train = torch.randint(0,256,(2,8))
        m.calibrate_all_layers_on_train([(train,train)])
        for training in (True, False):
            m.train(training)
            with torch.no_grad():
                a,_,_ = m(x); b,_,_ = m(y); c,_,_ = m(x[:,:3])
                torch.testing.assert_close(a[:,:3],b[:,:3],rtol=1e-5,atol=1e-5)
                torch.testing.assert_close(a[:,:3],c,rtol=1e-5,atol=1e-5)
                for layer in m.layers:
                    h = torch.randn(2,8,128); h2=h.clone(); h2[:,3:]+=10
                    assert torch.equal(layer.ffn(h)[2][:,:3],layer.ffn(h2)[2][:,:3])
                    assert torch.equal(layer.ffn(h)[2][:,:3],layer.ffn(h[:,:3])[2])


def test_controls_and_byte_weighting():
    d = build_model("dense", n_layers=1)
    for arm in ("none", "always", "causal", "random"):
        m = build_model(arm,n_layers=1)
        assert torch.equal(d.emb.weight,m.emb.weight)
        assert torch.equal(d.layers[0].attn.in_proj_weight,m.layers[0].attn.in_proj_weight)
    assert build_model("none",n_layers=1).total_ffn_footprint() == (0,0)
    batches = complete_batches(torch.arange(71),16,2)
    assert [y.numel() for _,y in batches] == [32,32,6]
    assert torch.equal(torch.cat([y.flatten() for _,y in batches]),torch.arange(1,71))
    class Uniform(nn.Module):
        def forward(self,x):
            return torch.zeros(*x.shape,256),0.,[float(x.shape[1]==6)]
    r=evaluate(Uniform(),batches)
    assert r["bytes"]==70 and abs(r["bpb"]-8)<1e-6
    assert math.isclose(r["per_layer_skip"][0],6/70)
    bigram=matched_bigram(torch.arange(128),batches)
    assert bigram["bytes"]==70 and bigram["score_sha256"]==r["score_sha256"]
    bigram["bpb"]=3.8  # deterministic test of the verdict guard, not a science result
    metrics={a:dict(bytes=70,bpb=3.,score_sha256=r["score_sha256"])
             for a in ("dense","none","always","causal","random")}
    assert prerequisite_check(metrics,bigram,70,True)
    assert not prerequisite_check(metrics,dict(bigram,bpb=2.9),70,True)
    assert not prerequisite_check(metrics,bigram,70,False)
    assert not prerequisite_check(metrics,bigram,69,True)
    assert not prerequisite_check(metrics,dict(bigram,score_sha256="different"),70,True)
    del metrics["none"]
    assert not prerequisite_check(metrics,bigram,70,True)
