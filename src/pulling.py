from __future__ import annotations

import subprocess
from pathlib import Path

from rich.console import Console


def clone_repos(repos: dict[str, str], snapshot_dir: Path) -> None:
    console = Console()
    console.print("[bold]Cloning repositories...[/]")

    for name, repo_url in repos.items():
        target_path = snapshot_dir / name

        process = subprocess.run(
            ["git", "clone", "--quiet", repo_url, str(target_path)],
            capture_output=True,
            text=True,
        )

        if process.returncode == 0:
            console.print(f":white_check_mark: [green]Cloned {name} successfully[/]")
        else:
            console.print(f":x: [red]Failed to clone {name}[/]")
            console.print(process.stderr, style="red")
