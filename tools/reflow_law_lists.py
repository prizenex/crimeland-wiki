#!/usr/bin/env python3
"""Break inline legal subpoints (a), 1), 2.1.) onto separate list lines."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = list((ROOT / "laws").glob("*.md")) + [ROOT / "police" / "officer-guide.md"]


def split_frontmatter(text: str) -> tuple[str, str]:
    m = re.match(r"^(---\r?\n.*?\r?\n---\r?\n)", text, re.DOTALL)
    if not m:
        return "", text
    return m.group(1), text[m.end() :]


def should_skip_line(line: str) -> bool:
    s = line.lstrip()
    if not s:
        return True
    if s.startswith(("#", "|", "!", "{%", "*", "- ", "<")):
        return True
    if s == "-":
        return True
    return False


def repair_corruption(text: str) -> str:
    for c in "abcdefghijklmnopqrstuvwxyz":
        text = text.replace(f"- {c}{c})", f"- {c})")
    text = re.sub(r"- (\d+)\\\)\1\\\)", r"- \1\\)", text)
    text = re.sub(r":\n\n-\n\n- ", ":\n\n- ", text)
    text = re.sub(r"^\-\s*$\n", "", text, flags=re.MULTILINE)
    return text


def reflow_paragraph(line: str) -> str:
    s = line.strip()
    if should_skip_line(line):
        return line.rstrip()

    s = re.sub(r":\s*([a-z]\))", r":\n\n- \1", s)
    s = re.sub(r" ([a-z]\))", r"\n\n- \1", s)
    s = re.sub(r" (\d+\\\))", r"\n\n- \1", s)
    s = re.sub(r"(?<=\S)\s+(?=(\d+\.\d+\.\s))", r"\n\n", s)

    # Same line: "…речення. 2. Наступний" (judicial escaped)
    s = re.sub(r"(?<=\.)\s+(?=(\d+)\\\.\s)", r"\n\n", s)

    out: list[str] = []
    for part in s.split("\n"):
        p = part.strip()
        if not p:
            out.append("")
            continue
        if re.match(r"^[a-z]\)\s", p) and not p.startswith("- "):
            p = "- " + p
        out.append(p)

    return "\n".join(out)


def collapse_extra_blanks(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def strip_escaped_main_clause_lists(text: str) -> str:
    r"""Judicial: "- 1\." -> "1\." for main clause lines."""
    return re.sub(r"^- (\d+\\\.\s)", r"\1", text, flags=re.MULTILINE)


def main() -> None:
    for path in FILES:
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8-sig")
        front, body = split_frontmatter(raw)
        body = repair_corruption(body)
        lines_out: list[str] = []
        for line in body.split("\n"):
            reflowed = reflow_paragraph(line)
            lines_out.extend(reflowed.split("\n"))
        body = collapse_extra_blanks("\n".join(lines_out))
        body = repair_corruption(body)
        body = strip_escaped_main_clause_lists(body)
        if not body.endswith("\n"):
            body += "\n"
        path.write_text(front + body, encoding="utf-8", newline="\n")
        print(f"OK  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
