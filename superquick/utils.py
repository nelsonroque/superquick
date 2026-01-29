# utils.py
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, Optional

DEFAULT_SKIP_DIRS: set[str] = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".tox",
}


def _normalize_ext(ext: Optional[str]) -> Optional[str]:
    return ext.lower().lstrip(".") if ext else None


def _as_path(p: Optional[Path]) -> Path:
    """
    Expand ~ and return a normalized Path. (Does not force resolve().)
    """
    if p is None:
        return Path.cwd()
    return Path(str(p)).expanduser()


def _walk_files(
    root: Path,
    *,
    follow_symlinks: bool,
    ignore_hidden: bool,
    skip_dirs: set[str],
) -> Iterable[Path]:
    """
    Faster recursive walk using os.scandir(). Yields file Paths.
    """
    stack = [root]

    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    name = entry.name

                    if ignore_hidden and name.startswith("."):
                        continue

                    try:
                        if entry.is_dir(follow_symlinks=follow_symlinks):
                            if name in skip_dirs:
                                continue
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=follow_symlinks):
                            yield Path(entry.path)
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
        except (PermissionError, FileNotFoundError, OSError):
            continue


# -----------------------
# Size parsing + formatting
# -----------------------

_SIZE_MULTIPLIERS = {
    "b": 1,
    "k": 1024,
    "kb": 1024,
    "kib": 1024,
    "m": 1024**2,
    "mb": 1024**2,
    "mib": 1024**2,
    "g": 1024**3,
    "gb": 1024**3,
    "gib": 1024**3,
    "t": 1024**4,
    "tb": 1024**4,
    "tib": 1024**4,
    "p": 1024**5,
    "pb": 1024**5,
    "pib": 1024**5,
}

_SIZE_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]*)\s*$")


def parse_size(size: Optional[str]) -> Optional[int]:
    """
    Parse human sizes like: 5g, 5GB, 5GiB, 500m, 100kb, 123 (bytes)
    Uses binary multiples (1KB = 1024 bytes).
    """
    if size is None:
        return None

    s = str(size).strip()
    if not s:
        return None

    m = _SIZE_RE.match(s)
    if not m:
        raise ValueError(f"Invalid size: {size!r}. Examples: 5GB, 500MB, 120k, 123")

    number_str, unit_str = m.groups()
    unit = unit_str.lower()

    if unit == "":
        return int(float(number_str))

    if unit in _SIZE_MULTIPLIERS:
        return int(float(number_str) * _SIZE_MULTIPLIERS[unit])

    raise ValueError(
        f"Unknown size unit: {unit_str!r}. Use: B, K/KB/KiB, M/MB/MiB, G/GB/GiB, T/TB/TiB"
    )


def human_size(num_bytes: int) -> str:
    n = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if n < 1024.0 or unit == "PB":
            if unit == "B":
                return f"{int(n)}{unit}"
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"
