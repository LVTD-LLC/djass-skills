#!/usr/bin/env python3
"""Copy the canonical skill into the OpenClaw portable bundle. Run after editing plugins/djass/skills/."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "plugins/djass/skills"
TARGETS = [ROOT / "integrations/openclaw/djass/skills"]


def main() -> None:
    for target in TARGETS:
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SOURCE, target)
        print(f"synced {SOURCE.relative_to(ROOT)} -> {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
