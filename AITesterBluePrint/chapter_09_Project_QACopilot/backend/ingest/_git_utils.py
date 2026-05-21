"""Git utilities for auto-cloning and refreshing source repos."""

import subprocess
from pathlib import Path
from typing import Callable


def ensure_repo(local_dir: Path, url: str, log: Callable[[str], None] = print) -> None:
    """Clone the repo if absent, or pull latest if already cloned.

    Args:
        local_dir: Local directory for the repo.
        url: Git remote URL.
        log: Logging function (defaults to print).
    """
    local_dir = Path(local_dir)

    if not local_dir.exists() or not (local_dir / ".git").exists():
        log(f"Cloning {url} -> {local_dir}")
        local_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(
            ["git", "clone", "--depth", "1", url, str(local_dir)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        log(f"Clone complete: {local_dir}")
    else:
        log(f"Pulling latest in {local_dir}")
        try:
            subprocess.check_call(
                ["git", "-C", str(local_dir), "pull", "--ff-only"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            log("Pull complete.")
        except subprocess.CalledProcessError as e:
            log(f"Warning: git pull failed ({e}). Using existing checkout.")
