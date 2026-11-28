"""Sequential regime-shift benchmark with bounded feedback history.

No original DoorKey access. The correct action depends on the second byte in
phase A, on the first byte in phase B, then on the second byte again in A2.
This measures adaptation and catastrophic forgetting of the learned selector.
"""
import json
from learned_byte_cells import LearnedByteCells

def training_phase(agent, regime):
    for first in (b"x", b"y"):
        for second in (b"A", b"B"):
            correct = (1 if second == b"A" else 0) if regime == "A" else (1 if first == b"x" else 0)
            for action in (0, 1):
                frame = first + second + b"-train"
                agent.observe(frame, [0, 1])
                agent.learn(action, b"terminal", int(action == correct), True)

def evaluate(agent, regime):
    decisions = []
    for first in (b"x", b"y"):
        for second in (b"A", b"B"):
            correct = (1 if second == b"A" else 0) if regime == "A" else (1 if first == b"x" else 0)
            agent.observe(first + second + b"-holdout", [0, 1])
            decisions.append(int(agent.choose() == correct))
    return sum(decisions)

def run():
    agent = LearnedByteCells(feature_positions=2, max_examples=8)
    phases = []
    for regime in ("A", "B", "A"):
        training_phase(agent, regime)
        phases.append({"regime": regime, "selected_position": agent.feature_position,
                       "own_regime_correct": evaluate(agent, regime),
                       "former_A_correct": evaluate(agent, "A"),
                       "former_B_correct": evaluate(agent, "B"),
                       "history_size": len(agent.examples)})
    return {"phases": phases,
            "limitation": "Hard task switches and matched source-free observations; replay memory eight items"}

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
