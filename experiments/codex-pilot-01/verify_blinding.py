#!/usr/bin/env python3
"""Coordinator-only CLI; never copy into evaluated workspaces."""
import argparse
import json
from pathlib import Path
import pilot
import exports
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=pilot.HERE, help='Coordinator experiment storage')
parser.add_argument('--exports',action='store_true',help='Re-extract and validate all subject-only archives')
args=parser.parse_args()
result=exports.verify_exports(args.root) if args.exports else pilot.verify(args.root)
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['passed'] else 1)
