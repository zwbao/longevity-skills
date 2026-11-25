#!/usr/bin/env python3
"""Maintainer-only extraction of corrected Appendix 2 Table S1; needs pdftotext.

Usage: python extract_table.py /tmp/mmc2.pdf /tmp/table_s1.csv
No download and no original PDF is distributed with this skill.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

FIELDS = ["region", "age_group", "year", "sex", "tmrel_standard_drinks_day",
          "tmrel_ui_low", "tmrel_ui_high", "nde_standard_drinks_day",
          "nde_ui_low", "nde_ui_high", "appendix_page", "pdf_page"]


def extract(pdf, output):
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    row_re = re.compile(r"^\s*(.*?)\s+(\d+ to \d+|80 plus)\s+(1990|2000|2010|2020)\s+(.*)$")
    rows = []
    for pdf_page, page in enumerate(text.split("\f"), 1):
        # Corrected source Table S1: PDF pp 4–32 / appendix pp 3–31.
        if not 4 <= pdf_page <= 32:
            continue
        lines = page.splitlines()
        for i, line in enumerate(lines):
            match = row_re.match(line)
            if not match:
                continue
            means = lines[i - 1].split()
            intervals = re.findall(r"\(([^()]+)\)", match[4])
            if len(means) != 4 or len(intervals) != 4:
                raise ValueError(f"Cannot parse PDF page {pdf_page}: {line}")
            cells = []
            for mean, interval in zip(means, intervals):
                values = [mean, *interval.split("–")]
                if len(values) != 3:
                    raise ValueError(interval)
                cells.append([v.replace("·", ".") for v in values])
            for offset, sex in [(0, "female"), (2, "male")]:
                rows.append([match[1], match[2], match[3], sex,
                             *cells[offset], *cells[offset + 1], pdf_page - 1, pdf_page])
    # Structural completeness: 21 printed regions × 14 printed age groups × 4 years × 2 sexes.
    if len(rows) != 21 * 14 * 4 * 2 or len({tuple(r[:4]) for r in rows}) != len(rows):
        raise ValueError("Incomplete or duplicate Table S1")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(FIELDS)
        writer.writerows(rows)


if __name__ == "__main__":
    extract(*sys.argv[1:])
