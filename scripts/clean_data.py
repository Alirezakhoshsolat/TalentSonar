import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'talentsonar' / 'output'

FILES_TO_REMOVE = [
    DATA_DIR / 'candidates_data.json',
    DATA_DIR / 'candidates.csv',
    DATA_DIR / 'discovered_candidates.json',
    DATA_DIR / 'job_postings.json',
    DATA_DIR / 'test_results.json',
    DATA_DIR / 'invitations.json',
]


def remove_file(p: Path):
    try:
        if p.exists():
            p.unlink()
            print(f"Removed: {p}")
    except Exception as e:
        print(f"Could not remove {p}: {e}")


def clean_data():
    print(f"Cleaning data directory: {DATA_DIR}")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for f in FILES_TO_REMOVE:
        remove_file(f)

    # Optionally clean output artifacts
    if OUTPUT_DIR.exists():
        try:
            shutil.rmtree(OUTPUT_DIR)
            print(f"Removed directory: {OUTPUT_DIR}")
        except Exception as e:
            print(f"Could not remove {OUTPUT_DIR}: {e}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nCleanup complete. Fresh start ready.")


if __name__ == '__main__':
    clean_data()
