#!/usr/bin/env python3
"""Coordinator-only CLI; never copy into evaluated workspaces."""
import argparse
import json
from pathlib import Path
import pilot
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=pilot.HERE, help='Coordinator experiment storage')
parser.add_argument('operation',choices=['begin','finish'])
parser.add_argument('--run',required=True)
parser.add_argument('--metadata',type=Path)
parser.add_argument('--response',type=Path)
parser.add_argument('--status',choices=sorted(pilot.TERMINAL))
parser.add_argument('--subject-stopped',action='store_true')
args=parser.parse_args()
metadata=pilot.read(args.metadata) if args.metadata else {}
if args.operation=='begin':
    pilot.begin(args.root,args.run,metadata)
else:
    if not args.subject_stopped or not args.status:parser.error('Finish requires --subject-stopped and --status')
    pilot.collect(args.root,args.run,args.response,args.status,metadata)
print(json.dumps({'recorded':args.operation,'run_id':args.run}))
