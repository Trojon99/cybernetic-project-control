#!/usr/bin/env python3
"""Build and re-extract every single-run export; no model/task calls."""
import argparse
import json
from pathlib import Path
import pilot
import exports
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=pilot.HERE)
args=parser.parse_args()
print(json.dumps(exports.export(args.root),indent=2))
