import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
FIXTURE = ROOT / "tests" / "fixtures" / "synthetic_npx.csv"


def synthetic_subjects():
    """{subject: (age, [(marker, value, unit), ...])} from the frozen synthetic fixture."""
    out = {}
    with FIXTURE.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            age, rows = out.setdefault(row["subject"], (float(row["age"]), []))
            rows.append((row["marker"], row["value"], row["unit"]))
    return out


def write_rows(path: Path, rows) -> Path:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["marker", "value", "unit"])
        writer.writerows(rows)
    return path
