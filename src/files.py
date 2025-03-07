from __future__ import annotations

import datetime
import os
from pathlib import Path
import json


def load_config(json_file: str) -> dict[str, str]:
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def create_snapshot_dir(snapshots_base_dir: Path) -> tuple[Path, int]:
    snapshots = sorted(
        [
            int(d.split("-")[1])
            for d in os.listdir(snapshots_base_dir)
            if d.startswith("snapshot-") and d.split("-")[1].isdigit()
        ]
    )
    snapshot_id = snapshots[-1] + 1 if snapshots else 1  # Ensure correct ID increment
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    snapshot_dir = snapshots_base_dir / f"snapshot-{snapshot_id}-{timestamp}"
    snapshot_dir.mkdir(exist_ok=True)
    return snapshot_dir, snapshot_id


def get_snapshots(snapshots_base_dir: Path) -> list[str]:
    return sorted(
        [d for d in os.listdir(snapshots_base_dir) if d.startswith("snapshot-")]
    )
