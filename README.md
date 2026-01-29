# superquick

[![uv](https://img.shields.io/badge/uv-supported-blue)](https://github.com/astral-sh/uv)
[![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

Fast, opinionated file search for interactive exploration and data triage.

<a href="https://github.com/nelsonroque/superquick">
  <img src="logo.png" alt="Superquick python package Logo" width="200">
</a>


---

## Why this exists

Modern machines are full of files you *know* exist but can’t quite remember where they live.
`superquick` (`sq`) is a fast, opinionated alternative to `find` that’s designed for **interactive exploration**, **data triage**, and **developer workflows**.

It favors:
- sensible defaults
- human-readable filters
- output that’s easy to inspect *or* pipe into pandas, R, or other tools

Think of it as `find` + `du` + a little ergonomics.

---

## Installation

```bash
uv pip install git+https://github.com/nelsonroque/superquick.git
```

---

## Features

### Core search
- Recursive search from any directory (defaults to current working directory)
- Positional path argument with `~` expansion and spaces supported
- Case-insensitive filename substring matching (`--substring`, `-s`)
- File extension filtering (`--ext`, `-e`)

### Size filtering
- Human-readable size filters:
  - `--min-size 500MB`, `--min-size 5g`
  - `--max-size 2GB`
- Binary units (1GB = 1024³ bytes)

### Filesystem controls
- Skip common heavy directories by default (`.git`, `node_modules`, `.venv`, etc.)
- `--no-skip` to disable directory skipping
- `--include-hidden` to include dotfiles and hidden directories
- Optional symlink following (`--follow-symlinks`)

### Output modes
- Default: one path per line (pipe-friendly)
- Rich table output with metadata (`--table`)
  - Path
  - File size (human-readable)
  - Last modified time
- CSV export to stdout (`--csv`)
- JSON export to stdout (`--json`)

### Sorting & limits
- Sort results by:
  - path (default)
  - size (largest first)
  - modification time
- Limit output with `--limit / -n`

### Convenience
- Works with or without subcommands:
  ```bash
  sq --ext xlsx ~/Documents/Github
  sq search --ext xlsx ~/Documents/Github
  ```
- Count-only mode for fast scans (`--count-only`, `-c`)

---

## Examples

```bash
# Find all Excel files
sq --ext xlsx ~/Documents/Github

# Find large files (>1GB)
sq --min-size 1GB ~

# Show largest files in a table
sq --sort size --table ~/Documents/Github

# Export results to CSV
sq --ext xlsx --csv ~/Documents/Github > results.csv

# Export results to JSON
sq --min-size 5g --json ~/Desktop > bigfiles.json
```

---

## Roadmap

### Planned

- Ensure CSV/JSON outputs are strictly machine-pure (no footers)
- Custom directory ignore flags (`--ignore-dir build,tmp`)

### Under consideration:
- Slack / Teams “phone home” summary via webhooks
- Optional parallel directory traversal for very large filesystems

---

## Notes

- CSV and JSON output are designed to be pandas-friendly
- Permission errors are skipped gracefully during traversal
- Defaults are optimized for interactive use and shell pipelines
