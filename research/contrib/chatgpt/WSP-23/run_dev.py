import argparse
from pathlib import Path
from capacity_proof import run
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write-evidence',type=Path);args=p.parse_args();run(args.write_evidence)
