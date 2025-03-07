from __future__ import annotations

import hashlib
import os
from pathlib import Path

from rich.console import Console


def compare_snapshots(
    snapshot1: str,
    snapshot2: str,
    snapshots_base_dir: Path,
    verbose: bool,
    repo_name: str = None,
) -> dict[str, str]:
    console = Console()
    snapshot1_path = snapshots_base_dir / snapshot1
    snapshot2_path = snapshots_base_dir / snapshot2
    changes = {}

    repos_to_compare = [repo_name] if repo_name else os.listdir(snapshot1_path)

    for name in repos_to_compare:
        repo1 = snapshot1_path / name
        repo2 = snapshot2_path / name
        if not repo2.exists():
            changes[name] = "Repo deleted"
            continue

        file_changes = []

        # Loop through the files in the first repository
        for file1_path in repo1.rglob("*"):
            # Skip .git directories and files
            if ".git" in file1_path.parts:
                continue

            # Check if the file exists in the second repository
            file2_path = repo2 / file1_path.relative_to(repo1)
            if not file2_path.exists():
                file_changes.append(f"{file1_path} - File deleted in {repo2}")
                continue

            # Skip .git directories and files in repo2
            if ".git" in file2_path.parts:
                continue

            # Compare the hash of both files, ignoring permission errors
            hash1 = hash_file(file1_path)
            hash2 = hash_file(file2_path)
            if hash1 is None or hash2 is None:
                continue  # Skip files that can't be read due to permission errors

            if hash1 != hash2:
                file_changes.append(f"{file1_path} - File content changed")

                # If verbose, show detailed line-by-line diff
                if verbose:
                    diff_output = get_file_diff(file1_path, file2_path)
                    if diff_output:
                        console.print(
                            f"[bold yellow]Detailed diff for {file1_path}:[/]"
                        )
                        console.print(diff_output)

        # Loop through files in the second repository to catch new files
        for file2_path in repo2.rglob("*"):
            # Skip .git directories and files in repo2
            if ".git" in file2_path.parts:
                continue

            file1_path = repo1 / file2_path.relative_to(repo2)
            if not file1_path.exists():
                file_changes.append(f"{file2_path} - New file in {repo2}")

        if file_changes:
            changes[name] = file_changes
            console.print(f"[bold cyan]Changes in {name}:[/]")
            for change in file_changes:
                console.print(f"  [yellow]{change}[/]")
        else:
            console.print(f"[bold green]{name} has no changes.[/]")

    return changes


def hash_file(file_path: Path) -> str:
    """Returns the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
    except PermissionError:
        return None  # Return None if permission is denied
    return sha256.hexdigest()


def get_file_diff(file1_path: Path, file2_path: Path) -> str:
    """Generates a line-by-line diff between two files."""
    diff_lines = []

    try:
        with open(file1_path, "r", encoding="utf-8") as f1, open(
            file2_path, "r", encoding="utf-8"
        ) as f2:
            file1_lines = f1.readlines()
            file2_lines = f2.readlines()

            # Compare each line
            max_len = max(len(file1_lines), len(file2_lines))
            for i in range(max_len):
                line1 = file1_lines[i] if i < len(file1_lines) else ""
                line2 = file2_lines[i] if i < len(file2_lines) else ""

                if line1 != line2:
                    diff_lines.append(
                        f"Line {i + 1}:\n- {line1.strip() if line1 else '[deleted]'}"
                        f"\n+ {line2.strip() if line2 else '[added]'}"
                    )
    except PermissionError:
        return "Permission denied while accessing the file."
    except Exception as e:
        return f"Error: {e}"

    return "\n".join(diff_lines)
