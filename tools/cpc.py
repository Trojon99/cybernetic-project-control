#!/usr/bin/env python3
"""Convenience entry point; implementation lives in the portable Skill."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] /
        "skills/cybernetic-project-control/scripts/cpc.py"), run_name="__main__")
