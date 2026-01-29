from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .utils import (
    _normalize_ext,
    _as_path,
    _walk_files,
    parse_size,
)

from .constants import DEFAULT_SKIP_DIRS

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    help="Recursively search for files by extension and/or filename substring.",
    rich_markup_mode="rich",
)

# Disable Rich auto-highlighting (prevents weird blue numbers)
console = Console(highlight=False)


@app.command()
def search(
    root: Optional[Path] = typer.Argument(
        None,
        help='Root directory to search (positional). Example: "~/Documents/Github"',
    ),
    substring: Optional[str] = typer.Option(
        None,
        "--substring",
        "-s",
        help="Substring to match in filename (case-insensitive).",
    ),
    min_size: Optional[str] = typer.Option(
        None,
        "--min-size",
        help="Minimum file size (e.g. 10MB, 5GB).",
    ),
    max_size: Optional[str] = typer.Option(
        None,
        "--max-size",
        help="Maximum file size (e.g. 500MB).",
    ),
    ext: Optional[str] = typer.Option(
        None,
        "--ext",
        "-e",
        help="File extension (e.g., xlsx). Case-insensitive.",
    ),
    absolute: bool = typer.Option(
        False,
        "--absolute/--relative",
        help="Print absolute paths (default: relative to root).",
    ),
    count_only: bool = typer.Option(
        False,
        "--count-only",
        "-c",
        help="Only print the number of matches.",
    ),
    follow_symlinks: bool = typer.Option(
        False,
        "--follow-symlinks",
        help="Follow symlinks (can be slow / cause loops).",
    ),
    ignore_hidden: bool = typer.Option(
        True,
        "--ignore-hidden/--include-hidden",
        help="Ignore hidden files/dirs (dotfiles).",
    ),
    no_skip: bool = typer.Option(
        False,
        "--no-skip",
        help="Do not skip common heavy directories like .git/node_modules.",
    ),
):
    root_path = _as_path(root)
    ext_norm = _normalize_ext(ext)
    sub_norm = substring.lower() if substring else None

    min_bytes = parse_size(min_size)
    max_bytes = parse_size(max_size)

    skip_dirs = set() if no_skip else DEFAULT_SKIP_DIRS

    matches = 0
    errors = 0

    for path in _walk_files(
        root_path,
        follow_symlinks=follow_symlinks,
        ignore_hidden=ignore_hidden,
        skip_dirs=skip_dirs,
    ):
        try:
            # size filter (if provided)
            if min_bytes is not None or max_bytes is not None:
                size = path.stat().st_size
                if min_bytes is not None and size < min_bytes:
                    continue
                if max_bytes is not None and size > max_bytes:
                    continue

            name = path.name.lower()

            if sub_norm and sub_norm not in name:
                continue
            if ext_norm and path.suffix.lower().lstrip(".") != ext_norm:
                continue

            matches += 1
            if not count_only:
                if absolute:
                    console.print(str(path.resolve()))
                else:
                    try:
                        console.print(str(path.relative_to(root_path)))
                    except Exception:
                        console.print(str(path))
        except (PermissionError, FileNotFoundError, OSError):
            errors += 1
            continue

    if count_only:
        console.print(matches)
    else:
        console.print(f"\n{matches} file(s) found")
        if errors:
            console.print(f"{errors} path(s) skipped due to permission/filesystem errors")


# Convenience: allow `sq --ext xlsx "~/Documents/Github"` (no subcommand)
@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    root: Optional[Path] = typer.Argument(None),
    substring: Optional[str] = typer.Option(None, "--substring", "-s"),
    min_size: Optional[str] = typer.Option(None, "--min-size"),
    max_size: Optional[str] = typer.Option(None, "--max-size"),
    ext: Optional[str] = typer.Option(None, "--ext", "-e"),
    absolute: bool = typer.Option(False, "--absolute/--relative"),
    count_only: bool = typer.Option(False, "--count-only", "-c"),
    follow_symlinks: bool = typer.Option(False, "--follow-symlinks"),
    ignore_hidden: bool = typer.Option(True, "--ignore-hidden/--include-hidden"),
    no_skip: bool = typer.Option(False, "--no-skip"),
):
    if ctx.invoked_subcommand is None:
        search(
            root=root,
            substring=substring,
            min_size=min_size,
            max_size=max_size,
            ext=ext,
            absolute=absolute,
            count_only=count_only,
            follow_symlinks=follow_symlinks,
            ignore_hidden=ignore_hidden,
            no_skip=no_skip,
        )

if __name__ == "__main__":
    app()
