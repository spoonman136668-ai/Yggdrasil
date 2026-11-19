"""Run evidence-only YGG-CAP01 sealing from the ORIGINAL scored artifacts.

The original seal.py remains source-pinned; the only corrected comparison
is the explicitly evidenced, bounded cross-OS checkpoint byte-count receipt.
This cannot re-execute native intervention training.
"""
import seal
from parity_recovery import seal_comparison

if __name__=="__main__":
    seal.seal_comparison=seal_comparison
    seal.main()
