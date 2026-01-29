# cli.py
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .utils import (
    DEFAULT_SKIP_DIRS,
    _as_path,
    _normalize_ext,
    _walk_files,
    human_size,
    parse_size,
)

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    help="Recursively search for files by extension and/or filename substring.",
    rich_markup_mode="rich",
)

# Disable Rich auto-highlighting (prevents weird blue numbers)
console = Console(highlight=False)


@dataclass
class MatchRow:
    path: str
    size_bytes: int
    size_human: str
    mtime_iso: str


def _output_paths(p: Path, root: Path, absolute: bool) -> str:
    if absolute:
        return str(p.resolve())
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)


def _render_table(rows: list[MatchRow], title: str):
    t = Table(title=title, show_lines=False)
    t.add_column("#", justify="right")
    t.add_column("Path", overflow="fold")
    t.add_column("Size", justify="right")
    t.add_column("Modified", justify="left")

    for i, r in enumerate(rows, start=1):
        t.add_row(str(i), r.path, r.size_human, r.mtime_iso)

    console.print(t)


def _render_csv(rows: list[MatchRow]):
    w = csv.DictWriter(
        typer.get_text_stream("stdout"),
        fieldnames=["path", "size_bytes", "size_human", "mtime_iso"],
    )
    w.writeheader()
    for r in rows:
        w.writerow(asdict(r))


def _render_json(rows: list[MatchRow]):
    payload = [asdict(r) for r in rows]
    typer.echo(json.dumps(payload, indent=2))


@app.command()
def search(
    root: Optional[Path] = typer.Argument(
        None,
        help='Root directory to search (positional). Example: "~/Documents/Github"',
    ),
    substring: Optional[str] = typer.Option(
        None, "--substring", "-s", help="Substring in filename (case-insensitive)."
    ),
    ext: Optional[str] = typer.Option(
        None, "--ext", "-e", help="File extension (e.g., xlsx)."
    ),
    min_size: Optional[str] = typer.Option(
        None, "--min-size", help="Minimum file size (e.g. 10MB, 5g)."
    ),
    max_size: Optional[str] = typer.Option(
        None, "--max-size", help="Maximum file size (e.g. 500MB)."
    ),
    absolute: bool = typer.Option(
        False, "--absolute/--relative", help="Print absolute paths (default: relative)."
    ),
    count_only: bool = typer.Option(
        False, "--count-only", "-c", help="Only print number of matches."
    ),
    follow_symlinks: bool = typer.Option(
        False, "--follow-symlinks", help="Follow symlinks (can be slow / loop)."
    ),
    ignore_hidden: bool = typer.Option(
        True, "--ignore-hidden/--include-hidden", help="Ignore hidden files/dirs."
    ),
    no_skip: bool = typer.Option(
        False, "--no-skip", help="Do not skip heavy dirs like .git/node_modules."
    ),
    # Output modes
    table: bool = typer.Option(False, "--table", help="Render output as a rich table."),
    csv_out: bool = typer.Option(False, "--csv", help="Output CSV to stdout."),
    json_out: bool = typer.Option(False, "--json", help="Output JSON to stdout."),
    # Extras
    sort: str = typer.Option("path", "--sort", help="Sort by: path, size, mtime"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit printed matches."),
):
    # Enforce single output mode (or default)
    modes = sum([1 if table else 0, 1 if csv_out else 0, 1 if json_out else 0])
    if modes > 1:
        raise typer.BadParameter("Use only one of: --table, --csv, --json")

    root_path = _as_path(root)
    ext_norm = _normalize_ext(ext)
    sub_norm = substring.lower() if substring else None

    min_bytes = parse_size(min_size)
    max_bytes = parse_size(max_size)

    skip_dirs = set() if no_skip else DEFAULT_SKIP_DIRS

    rows: list[MatchRow] = []
    errors = 0

    for path in _walk_files(
        root_path,
        follow_symlinks=follow_symlinks,
        ignore_hidden=ignore_hidden,
        skip_dirs=skip_dirs,
    ):
        try:
            name = path.name.lower()

            if sub_norm and sub_norm not in name:
                continue
            if ext_norm and path.suffix.lower().lstrip(".") != ext_norm:
                continue

            st = path.stat()
            size_b = st.st_size

            if min_bytes is not None and size_b < min_bytes:
                continue
            if max_bytes is not None and size_b > max_bytes:
                continue

            mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            out_path = _output_paths(path, root_path, absolute)

            rows.append(
                MatchRow(
                    path=out_path,
                    size_bytes=size_b,
                    size_human=human_size(size_b),
                    mtime_iso=mtime,
                )
            )
        except (PermissionError, FileNotFoundError, OSError):
            errors += 1
            continue

    # Sorting
    sort_key = sort.lower()
    if sort_key == "size":
        rows.sort(key=lambda r: r.size_bytes, reverse=True)
    elif sort_key == "mtime":
        rows.sort(key=lambda r: r.mtime_iso)
    else:
        rows.sort(key=lambda r: r.path.lower())

    # Limit
    if limit is not None:
        rows = rows[: max(0, limit)]

    if count_only:
        console.print(len(rows))
        return

    # Output
    if csv_out:
        _render_csv(rows)
    elif json_out:
        _render_json(rows)
    elif table:
        _render_table(rows, title=f"Matches in {root_path}")
    else:
        # Default: one path per line (pipe-friendly)
        for r in rows:
            console.print(r.path)

    console.print(f"\n{len(rows)} file(s) found")
    if errors:
        console.print(f"{errors} path(s) skipped due to permission/filesystem errors")


# Convenience: allow `sq --ext xlsx "~/Documents/Github"` without `search`
@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    root: Optional[Path] = typer.Argument(None),
    substring: Optional[str] = typer.Option(None, "--substring", "-s"),
    ext: Optional[str] = typer.Option(None, "--ext", "-e"),
    min_size: Optional[str] = typer.Option(None, "--min-size"),
    max_size: Optional[str] = typer.Option(None, "--max-size"),
    absolute: bool = typer.Option(False, "--absolute/--relative"),
    count_only: bool = typer.Option(False, "--count-only", "-c"),
    follow_symlinks: bool = typer.Option(False, "--follow-symlinks"),
    ignore_hidden: bool = typer.Option(True, "--ignore-hidden/--include-hidden"),
    no_skip: bool = typer.Option(False, "--no-skip"),
    table: bool = typer.Option(False, "--table"),
    csv_out: bool = typer.Option(False, "--csv"),
    json_out: bool = typer.Option(False, "--json"),
    sort: str = typer.Option("path", "--sort"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n"),
):
    if ctx.invoked_subcommand is None:
        search(
            root=root,
            substring=substring,
            ext=ext,
            min_size=min_size,
            max_size=max_size,
            absolute=absolute,
            count_only=count_only,
            follow_symlinks=follow_symlinks,
            ignore_hidden=ignore_hidden,
            no_skip=no_skip,
            table=table,
            csv_out=csv_out,
            json_out=json_out,
            sort=sort,
            limit=limit,
        )


if __name__ == "__main__":
    app()
