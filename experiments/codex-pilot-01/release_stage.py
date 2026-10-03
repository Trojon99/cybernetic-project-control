#!/usr/bin/env python3
"""Coordinator-only CLI; never copy into evaluated workspaces."""
import argparse
import json
from pathlib import Path
import pilot
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=pilot.HERE, help='Coordinator experiment storage')
parser.add_argument('--task',choices=sorted(pilot.STAGES),required=True)
parser.add_argument('--stage',type=int,required=True)
parser.add_argument('--target',type=Path,required=True)
parser.add_argument('--prior',type=Path)
parser.add_argument('--handoff',type=Path)
parser.add_argument('--prior-subject-stopped',action='store_true')
args=parser.parse_args()
if args.stage>1 and not args.prior_subject_stopped:parser.error('Stop prior subject before release')
print(json.dumps(pilot.release(args.root,args.task,args.stage,args.target,args.prior,args.handoff)))
