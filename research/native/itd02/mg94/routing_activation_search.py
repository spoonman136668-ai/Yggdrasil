"""MG94-W: bounded public-sequence search for routing activation; development only."""
from surprise_routing_ablation import RoutedCells
from itertools import product

def inspect(bits):
    routed, disabled = RoutedCells(True), RoutedCells(False)
    routed_predictions = [routed.step(x) for x in bits]
    disabled_predictions = [disabled.step(x) for x in bits]
    return routed.messages, routed_predictions == disabled_predictions

def run():
    found = None
    for size in range(1, 17):
        for candidate in product((0, 1), repeat=size):
            messages, equal = inspect(candidate)
            assert equal, "Communication changed predictions unexpectedly"
            if messages:
                found = candidate
                break
        if found is not None:
            break
    # Routing alerts cannot influence local prediction counters by construction.
    assert all(inspect(seq)[1] for seq in ((0,)*24,(0,1)*12,(1,)*24))
    if found is None:
        print("NO_ACTIVATION_THROUGH_LENGTH_16")
    else:
        print("FIRST_ACTIVATING_SEQUENCE", "".join(map(str,found)))
        print("MESSAGES", inspect(found)[0])
        print("PREDICTIONS_EQUAL", inspect(found)[1])
    print("CONSEQUENTIAL_ROUTING_NOT_IMPLEMENTED")
if __name__ == "__main__":
    run()
