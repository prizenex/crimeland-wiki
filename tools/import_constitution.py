#!/usr/bin/env python3
"""Import laws/КОНСТИТУЦІЯ ШТАТУ САН-АНДРЕАС.md → laws/constitution.md"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "laws" / "КОНСТИТУЦІЯ ШТАТУ САН-АНДРЕАС.md"
DEST = ROOT / "laws" / "constitution.md"

FRONT = """---
description: "Конституція штату Сан-Андреас — основний закон штату."
icon: scale-balanced
layout:
  width: wide
  tableOfContents:
    visible: true
---

# Конституція штату Сан-Андреас

"""


def normalize_line(line: str) -> str | None:
    s = line.rstrip()
    if not s.strip():
        return ""
    stripped = s.strip()
    if stripped == "---":
        return "---"
    m = re.match(r"^(#{1,6})\s+\*\*(.+?)\*\*\s*$", stripped)
    if m:
        level = len(m.group(1))
        content = m.group(2).strip()
        if re.match(r"^КОНСТИТУЦІЯ", content, re.I):
            return None
        if re.match(r"^(РОЗДІЛ|ПРЕАМБУЛА)\b", content, re.I):
            level = max(2, level) if level == 1 else level
        if re.match(r"^Стаття\s", content, re.I):
            level = 3
        return "#" * level + " " + content
    if stripped.startswith("# **"):
        inner = re.sub(r"^\#+\s*\*\*|\*\*$", "", stripped).strip()
        return normalize_line("# " + inner) if inner else None
    return s.rstrip()


def clean_body(raw: str) -> str:
    lines = raw.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    for line in lines:
        norm = normalize_line(line)
        if norm is None:
            continue
        out.append(norm)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing {SRC}")
    body = clean_body(SRC.read_text(encoding="utf-8-sig"))
    DEST.write_text(FRONT + body, encoding="utf-8", newline="\n")
    SRC.unlink()
    print(f"Wrote {DEST.relative_to(ROOT)}")
    reflow = ROOT / "tools" / "reflow_law_lists.py"
    subprocess.run([sys.executable, str(reflow)], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
