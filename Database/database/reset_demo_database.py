"""
reset_demo_database.py
======================
URL-Based Cyber Attack Detection & IP Intelligence System
DEMO PROTOTYPE

Completely resets the SQLite demo database by:
  1. Dropping all tables
  2. Recreating the schema
  3. (Optionally) reseeding with fresh synthetic data

⚠ DISCLAIMER: This script only affects the local SQLite file.
  No real data is ever stored in this database.

Usage:
    cd database/
    python reset_demo_database.py                        # reset only
    python reset_demo_database.py --reseed               # reset + seed
    python reset_demo_database.py --reseed --records 800 # reset + seed 800 rows
    python reset_demo_database.py --db /path/to/demo.db  # custom path
"""

import argparse
import sqlite3
import subprocess
import sys
from pathlib import Path

DEFAULT_DB = "../backend/demo.db"


def reset(db_path: str, verbose: bool = False) -> None:
    """
    Drop all demo tables and recreate the schema from scratch.
    The SQLite file is NOT deleted — only its contents are cleared.
    """
    print(f"[RESET] Connecting to: {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Drop tables in reverse-dependency order (FK safety)
    tables = ["detections", "requests", "ip_analysis", "uploads"]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        if verbose:
            print(f"[RESET] Dropped table: {table}")

    # Drop all associated indexes (cleaned automatically with tables in SQLite,
    # but explicit drop avoids any edge-case orphaned index names)
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
    """)
    indexes = [row[0] for row in cur.fetchall()]
    for idx in indexes:
        cur.execute(f"DROP INDEX IF EXISTS {idx}")
        if verbose:
            print(f"[RESET] Dropped index: {idx}")

    conn.commit()
    conn.close()

    print(f"[RESET] All tables and indexes dropped from: {db_path}")


def _confirm_reset(db_path: str) -> bool:
    """Interactive confirmation prompt."""
    print(f"\nWARNING: This will PERMANENTLY delete all records in: {db_path}")
    print("   (The file itself is kept; only table contents are erased.)")
    answer = input("   Type 'yes' to continue: ").strip().lower()
    return answer == "yes"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reset the demo SQLite database (drops all tables and data)."
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"Path to the SQLite .db file (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--reseed",
        action="store_true",
        help="After reset, automatically run seed_demo_data.py",
    )
    parser.add_argument(
        "--records",
        type=int,
        default=500,
        help="Number of records to seed (only used with --reseed, default: 500)",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Demo Database Reset Utility")
    print("  URL-Based Cyber Attack Detection System - DEMO PROTOTYPE")
    print("=" * 60)
    print()

    if not args.yes:
        if not _confirm_reset(args.db):
            print("[RESET] Cancelled.")
            sys.exit(0)

    print()

    try:
        reset(args.db, verbose=args.verbose)
    except Exception as exc:
        print(f"[RESET] ERROR during reset: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.reseed:
        print()
        print("[RESET] Starting seed_demo_data.py …")
        seed_script = Path(__file__).parent / "seed_demo_data.py"
        result = subprocess.run(
            [sys.executable, str(seed_script),
             "--db", args.db,
             "--records", str(args.records),
             *(["--verbose"] if args.verbose else [])],
            check=False,
        )
        if result.returncode != 0:
            print("[RESET] Seed script returned a non-zero exit code.", file=sys.stderr)
            sys.exit(result.returncode)
    else:
        print()
        print("[RESET] To reseed the database run:")
        print(f"        python seed_demo_data.py --db {args.db}")
        print()
        print("[RESET] Or use the shortcut:")
        print(f"        python reset_demo_database.py --reseed --db {args.db}")
