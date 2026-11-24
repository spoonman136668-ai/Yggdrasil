import torch
from experiments.procedural_event_stage7_capacity import model_for, ranks, classify, corpus


def test_factor_identity_and_gradient():
    x = torch.arange(16).reshape(2,8)
    models = [model_for(a,43,dim=32,layers=1).eval() for a in ('generated','direct','residual')]
    out = [m(x)[0] for m in models]
    assert all(torch.equal(out[0], y) for y in out[1:])
    for arm,m in zip(('generated','direct','residual'),models):
        assert ranks(m,arm)==[32,32]
        m(x)[0].square().mean().backward()
        assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.layers[0].ffn.parameters())
    assert classify({}, {}) == 'INVALID'


def test_corpus_fail_closed(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        corpus(tmp_path)
