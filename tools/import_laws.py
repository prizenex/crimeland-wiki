#!/usr/bin/env python3
"""Merge uploaded law markdown into GitBook slug paths (UTF-8, no BOM)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAPPINGS: list[tuple[str, str]] = [
    ("laws/Конституція уряду Лос-Сантос.md", "laws/constitution.md"),
    ("laws/АДМІНІСТРАТИВНИЙ КОДЕКС.md", "laws/administrative-code.md"),
    ("laws/КРИМІНАЛЬНИЙ КОДЕКС.md", "laws/criminal-code.md"),
    ("laws/Процесуальний кодекс штату.md", "laws/procedural-code.md"),
    ("laws/СУДОВИЙ КОДЕКС УРЯДУ Лос-Сантос.md", "laws/judicial-code.md"),
    (
        "laws/Закон про правоохоронні органи штату Сан-Андреас.md",
        "laws/law-enforcement-law.md",
    ),
    (
        "laws/law-enforcement/СТАТУТ ПОЛІЦЕЙСЬКОГО ДЕПАРТАМЕНТУ LOS SANTOS.md",
        "laws/lspd-statute.md",
    ),
    (
        "laws/law-enforcement/_Юрисдикція та взаємодія правоохоронних органів штату Сан-Андреас.md",
        "laws/law-enforcement-jurisdiction.md",
    ),
    (
        "laws/law-enforcement/ЗАКОН ШТАТУ САН-АНДРЕАС про ЗСШ.md",
        "laws/san-andreas-zssh-law.md",
    ),
    ("laws/law-enforcement/Посібник Офіцера поліції.md", "police/officer-guide.md"),
]

HINT = ""


def read_frontmatter(dest: Path) -> str:
    text = dest.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n.*?\r?\n---\r?\n", text, re.DOTALL)
    if not m:
        raise SystemExit(f"No frontmatter in {dest}")
    return m.group(0)


def strip_leading_blank_headers(body: str) -> str:
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s == "" or s == "#" or re.match(r"^#+\s*$", s):
            i += 1
            continue
        break
    return "\n".join(lines[i:]).lstrip("\n") + ("\n" if body.endswith("\n") else "")


def main() -> None:
    for src_rel, dest_rel in MAPPINGS:
        src = ROOT / src_rel
        dest = ROOT / dest_rel
        if not src.is_file():
            raise SystemExit(f"Missing source: {src}")
        if not dest.is_file():
            raise SystemExit(f"Missing destination (need frontmatter): {dest}")

        front = read_frontmatter(dest)
        body = src.read_text(encoding="utf-8-sig").lstrip("\ufeff")
        body = strip_leading_blank_headers(body)

        out = front + HINT + body
        dest.write_text(out, encoding="utf-8", newline="\n")
        print(f"OK  {dest_rel}")
        src.unlink()

    law_enf = ROOT / "laws" / "law-enforcement"
    if law_enf.is_dir() and not any(law_enf.iterdir()):
        law_enf.rmdir()
        print("Removed empty laws/law-enforcement/")


if __name__ == "__main__":
    main()
