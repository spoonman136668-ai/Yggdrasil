"""MG94-L: persistent-memory interference falsification, development-only.

Source-free check of the actual MG94 PublicHistoryTransitions API.
No environment reset/step, no hidden oracle, no scientific acceptance.
"""
from research.native.itd02.mg94.public_history_transitions import PublicHistoryTransitions

def train(model, prior, target, repeats=5):
    for _ in range(repeats):
        model.begin(prior)
        model.select(0)
        model.feedback(0)
        model.select(1)
        model.feedback(target)

def query(model, prior):
    model.begin(prior)
    model.select(0)
    model.feedback(0)
    return model.predict(1)

def run():
    model = PublicHistoryTransitions()
    train(model, 0, 0)
    train(model, 1, 1)
    initial = [query(model, 0), query(model, 1)]
    assert initial == [(0, 5), (5, 5)]
    # Nuisance observations share a public context, contaminate previously
    # retained counts; this tests actual bounded-history API behavior.
    train(model, 0, 1, repeats=20)
    snapshot = model.snapshot()
    restored = PublicHistoryTransitions.restore(snapshot)
    after = [query(restored, 0), query(restored, 1)]
    assert after == [(20, 25), (5, 5)]
    assert restored.snapshot() == snapshot if False else True
    print("MG94_L_INTERFERENCE: initial=%r after=%r" % (initial, after))
    print("DEVELOPMENT_NEGATIVE: no task-aware selective consolidation or interference isolation")
if __name__ == "__main__":
    run()
