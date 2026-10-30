"""MG38: opt-in reward guard over unchanged local-cell MG28 original adapter."""
from research.native.itd02.mg28.selected_change_cells import SelectedChangeCells
from research.native.itd02.mg37.progress_cells import LocalProgressCells

class SelectedProgressCells:
    def __init__(self, parent=None, progress=None):
        self.parent=SelectedChangeCells() if parent is None else parent
        self.progress=LocalProgressCells() if progress is None else progress
        if type(self.parent) is not SelectedChangeCells or type(self.progress) is not LocalProgressCells:
            raise ValueError("MG38_WRONG_NATIVE_PARENT")

    def start_session(self, adapter, name, live=False):
        self.parent.start_session(adapter,name,live=live)

    def choose(self, before):
        base=self.parent.choose(before)
        selected,override=self.progress.choose(base["action"])
        if not override:
            return base
        return {"schema":"yggdrasil.itd02.mg38.selected-reward-progress.v1",
                "action":selected,"status":"MG38_SELECTED_REWARD_PROGRESS_OVERRIDE",
                "external_fallback":False}

    def learn_selected(self, adapter, before, after):
        # Only the validated original selected source event can contribute reward.
        receipt=self.parent.learn_selected(adapter,before,after)
        latest=adapter.ledger[-1]
        self.progress.observe_selected(latest["action"],latest["reward"])
        return receipt
