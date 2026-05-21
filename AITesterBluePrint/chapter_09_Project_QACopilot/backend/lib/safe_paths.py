"""Path safety utilities — prevents writes outside allowed directories."""

from __future__ import annotations

from pathlib import Path


def safe_resolve(target: str | Path, allowed_dirs: list[Path] | None = None) -> Path:
    """Resolve a target path and verify it's within allowed directories.

    Raises PermissionError if the path is outside allowed dirs or contains traversal.
    """
    if allowed_dirs is None:
        from backend.lib.settings import settings
        allowed_dirs = [
            settings.GENERATED_DIR.resolve(),
            settings.TESTCASES_CSV.parent.resolve(),
        ]

    target_str = str(target)

    # Reject obvious traversal
    if ".." in target_str:
        raise PermissionError(f"Path traversal detected: {target_str}")

    # Resolve to absolute
    p = Path(target_str)
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    else:
        p = p.resolve()

    # Check against allowed dirs
    for allowed in allowed_dirs:
        try:
            p.relative_to(allowed)
            return p
        except ValueError:
            continue

    raise PermissionError(
        f"Refusing to write outside allowed directories: {p}\n"
        f"Allowed: {[str(d) for d in allowed_dirs]}"
    )
