"""MG43: source-context-local selected reward guard over frozen MG28."""
from research.native.itd02.mg28.selected_change_cells import SelectedChangeCells
from research.native.itd02.mg23.selected_target_cells import observed_key
from research.native.itd02.mg37.progress_cells import LocalProgressCells

MAX_REWARD_CONTEXTS=4096

class SelectedProgressCells:
    def __init__(self, parent=None, progress=None):
        self.parent=SelectedChangeCells() if parent is None else parent
        if type(self.parent) is not SelectedChangeCells:
            raise ValueError("MG43_WRONG_NATIVE_PARENT")
        if progress is not None and type(progress) is not LocalProgressCells:
            raise ValueError("MG43_WRONG_PROGRESS")
        self.cells={}
        # An optional prior learner is not inherited across unknown contexts.
        if progress is not None and any(progress.count):
            raise ValueError("MG43_UNSCOPED_LEGACY_REWARD")
    @property
    def progress(self):
        # Compatibility alias for source-only callers before any context is learned.
        if len(self.cells)==1:
            return next(iter(self.cells.values()))
        return LocalProgressCells()

    def start_session(self, adapter, name, live=False):
        self.parent.start_session(adapter,name,live=live)

    def choose(self, before):
        key=observed_key(before)
        base=self.parent.choose(before)
        cell=self.cells.get(key)
        if cell is None:
            return base
        selected,override=cell.choose(base["action"])
        if not override:
            return base
        return {"schema":"yggdrasil.itd02.mg43.context-reward-progress.v1",
                "action":selected,"status":"MG43_CONTEXT_REWARD_PROGRESS_OVERRIDE",
                "external_fallback":False}

    def learn_selected(self, adapter, before, after):
        key=observed_key(before)
        if key not in self.cells and len(self.cells)>=MAX_REWARD_CONTEXTS:
            raise ValueError("MG43_REWARD_CONTEXT_CAP")
        # No reward admitted before the original selected ledger validates.
        receipt=self.parent.learn_selected(adapter,before,after)
        latest=adapter.ledger[-1]
        cell=self.cells.setdefault(key,LocalProgressCells())
        cell.observe_selected(latest["action"],latest["reward"])
        return receipt
