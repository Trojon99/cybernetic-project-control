#!/usr/bin/env python3
"""Coordinator-only CLI; never copy into evaluated workspaces."""
import argparse
import json
from pathlib import Path
import pilot
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=pilot.HERE, help='Coordinator experiment storage')
args=parser.parse_args()
print(json.dumps(pilot.report(args.root),indent=2))
