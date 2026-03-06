"""
LaRa Memory Inspector
======================
Prints all rows from every table in the LaRa SQLite session database.

Usage:
    python scripts/inspect_memory.py
    python scripts/inspect_memory.py --db path/to/lara_memory.db
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime

# ── Resolve project root and runtime path ───────────────────────────────────
_SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

try:
    from core.runtime_paths import get_sessions_dir
    _DEFAULT_DB = os.path.join(get_sessions_dir(), "lara_memory.db")
except Exception:
    _DEFAULT_DB = os.path.join(_PROJECT_ROOT, "runtime", "sessions", "lara_memory.db")

# ── ANSI colors ──────────────────────────────────────────────────────────────
_CYAN   = "\033[96m"
_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_BOLD   = "\033[1m"
_RESET  = "\033[0m"
_DIM    = "\033[2m"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fmt_value(col: str, val) -> str:
    """Pretty-format a cell value."""
    if val is None:
        return f"{_DIM}NULL{_RESET}"
    if isinstance(val, float) and "timestamp" in col.lower():
        try:
            return datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(val)
    return str(val)


def print_table(conn: sqlite3.Connection, table: str) -> None:
    """Fetch and pretty-print all rows from a table."""
    print(f"\n{_CYAN}{_BOLD}── {table} {'─' * (50 - len(table))}{_RESET}")

    cursor = conn.execute(f"SELECT * FROM {table}")
    rows   = cursor.fetchall()
    cols   = [desc[0] for desc in cursor.description]

    if not rows:
        print(f"  {_YELLOW}(empty){_RESET}")
        return

    # Column widths
    widths = [max(len(c), max(len(_fmt_value(c, r[i])) for r in rows)) for i, c in enumerate(cols)]

    # Header
    header = "  " + "  ".join(f"{_BOLD}{c:<{widths[i]}}{_RESET}" for i, c in enumerate(cols))
    sep    = "  " + "  ".join("─" * w for w in widths)
    print(header)
    print(sep)

    for row in rows:
        cells = "  ".join(f"{_fmt_value(cols[i], v):<{widths[i]}}" for i, v in enumerate(row))
        print(f"  {cells}")

    print(f"\n  {_DIM}{len(rows)} row(s){_RESET}")


def inspect(db_path: str) -> None:
    if not os.path.isfile(db_path):
        print(f"\n{_YELLOW}No database found at: {db_path}{_RESET}")
        print("  → Start LaRa and complete at least one session to populate the database.\n")
        return

    print(f"\n{_BOLD}{_GREEN}LaRa Memory Inspector{_RESET}")
    print(f"{_DIM}Database: {db_path}{_RESET}")
    print(f"{_DIM}Inspected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{_RESET}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    if not tables:
        print(f"\n{_YELLOW}Database exists but contains no tables yet.{_RESET}\n")
        conn.close()
        return

    for (table,) in tables:
        print_table(conn, table)

    conn.close()
    print()


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Inspect LaRa SQLite memory database.")
    parser.add_argument(
        "--db",
        default=_DEFAULT_DB,
        help=f"Path to the SQLite database (default: {_DEFAULT_DB})"
    )
    args = parser.parse_args()
    inspect(args.db)


if __name__ == "__main__":
    main()
