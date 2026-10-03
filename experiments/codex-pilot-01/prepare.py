#!/usr/bin/env python3
"""Coordinator-only CLI; never copy into evaluated workspaces."""
import argparse
import json
from pathlib import Path
import pilot
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=pilot.HERE, help='Coordinator experiment storage')
parser.add_argument('--environment',type=Path,help='Actual coordinator host observations, never inferred subject metadata')
args=parser.parse_args()
print(json.dumps({'prepared':pilot.prepare(args.root,pilot.read(args.environment) if args.environment else None),'model_runs':0}))
