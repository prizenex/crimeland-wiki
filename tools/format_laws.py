#!/usr/bin/env python3
"""Normalize law markdown for GitBook (UTF-8, no BOM)."""
from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / ".gitbook" / "assets"

FILES = [
    ("laws/constitution.md", None, "law-constitution"),
    ("laws/administrative-code.md", None, "law-administrative"),
    ("laws/criminal-code.md", None, "law-criminal"),
    ("laws/procedural-code.md", "law-procedural-header.png", "law-procedural"),
    ("laws/judicial-code.md", "law-judicial-header.png", "law-judicial"),
    ("laws/law-enforcement-law.md", None, "law-enforcement"),
    ("laws/lspd-statute.md", None, "law-lspd-statute"),
    ("laws/law-enforcement-jurisdiction.md", None, "law-jurisdiction"),
    ("laws/san-andreas-zssh-law.md", None, "law-zssh"),
    ("police/officer-guide.md", "police-officer-handbook-header.png", "police-officer"),
]

ANY_IMAGE_RE = re.compile(
    r"^\[image(?P<num>\d+)\]:\s*<data:image/(?P<fmt>png|jpeg|jpg|webp);base64,(?P<data>[^>]+)>\s*$",
    re.MULTILINE,
)
HINT_END = re.compile(r"(\{% endhint %\}\s*\n)")

LAYOUT_BLOCK = """layout:
  width: wide
  tableOfContents:
    visible: true
"""

H1_TITLES = {
    "constitution.md": "Конституція штату Сан-Андреас",
    "administrative-code.md": "Адміністративний кодекс",
    "criminal-code.md": "Кримінальний кодекс",
    "procedural-code.md": "Процесуальний кодекс штату",
    "judicial-code.md": "Судовий кодекс уряду Лос-Сантос",
    "law-enforcement-law.md": "Закон про правоохоронні органи штату Сан-Андреас",
    "lspd-statute.md": "Статут поліцейського департаменту Los Santos",
    "law-enforcement-jurisdiction.md": "Юрисдикція та взаємодія правоохоронних органів",
    "san-andreas-zssh-law.md": "Закон штату Сан-Андреас про ЗСШ",
    "officer-guide.md": "Посібник офіцера поліції",
}


def split_header(text: str) -> tuple[str, str]:
    m = re.match(r"^(---\r?\n.*?\r?\n---\r?\n)", text, re.DOTALL)
    if not m:
        raise ValueError("Missing YAML frontmatter")
    rest = text[m.end() :]
    hm = HINT_END.search(rest)
    if hm:
        return text[: m.end() + hm.end()], rest[hm.end() :]
    return m.group(1) + "\n", rest


def inject_layout(front: str) -> str:
    if "layout:" in front:
        return front
    return front.replace("\n---\n", f"\n{LAYOUT_BLOCK}---\n", 1)


def extract_all_images(
    body: str, slug: str, primary_asset: str | None
) -> tuple[str, dict[str, str]]:
    images: dict[str, str] = {}

    def save(num: str, fmt: str, data: str) -> str:
        ext = "jpg" if fmt in ("jpeg", "jpg") else fmt
        if num == "1" and primary_asset:
            fname = primary_asset
        else:
            fname = f"{slug}-img-{num}.{ext}"
        ASSETS.mkdir(parents=True, exist_ok=True)
        (ASSETS / fname).write_bytes(base64.b64decode(data))
        images[f"image{num}"] = f"../.gitbook/assets/{fname}"
        return ""

    body = ANY_IMAGE_RE.sub(
        lambda m: save(m.group("num"), m.group("fmt"), m.group("data")), body
    )
    return body, images


def apply_image_markers(body: str, images: dict[str, str]) -> str:
    for key, rel in sorted(images.items(), key=lambda x: int(x[0].replace("image", ""))):
        body = body.replace(f"![][{key}]", f"![Ілюстрація]({rel})")
    body = re.sub(r"^!\[\]\[image\d+\]\s*$", "", body, flags=re.MULTILINE)
    body = re.sub(r"(\!\[[^\n]+\))\s*(\!\[)", r"\1\n\n\2", body)
    return body


def unwrap_list_hashes(line: str) -> str:
    prev = None
    while prev != line:
        prev = line
        line = re.sub(r"^(\s*[-*+]\s+)# (.+)$", r"\1\2", line)
    return line


def strip_bold_wrapper(s: str) -> str:
    s = s.strip()
    m = re.match(r"^\*\*(.+)\*\*$", s)
    return m.group(1).strip() if m else s


def heading_level_for(content: str, current: int) -> int:
    c = strip_bold_wrapper(content)
    if re.match(r"^(Розділ|РОЗДІЛ)\s", c):
        return max(2, current) if current == 1 else max(2, current)
    if re.match(r"^ЗМІСТ\s*$", c, re.I):
        return 2
    if re.match(r"^Стаття\s+[IVXLC]+\.", c):
        return 2
    if re.match(r"^Стаття\s", c, re.I):
        return 3
    if re.match(r"^(Преамбула|Тлумачення)\s*$", c, re.I):
        return 2
    if re.match(r"^[\U0001F300-\U0001FAFF]", c):
        return 2
    if current == 1 and len(c) > 60:
        return 0
    return current


def is_prose_hash(content: str) -> bool:
    c = strip_bold_wrapper(content)
    if not c or c == "---":
        return True
    if c.startswith("![]") or c.startswith("!["):
        return True
    if re.match(r"^[\W\d_]+$", c):
        return True
    if re.match(
        r"^(Розділ|РОЗДІЛ|ЗМІСТ|Стаття|СТАТУТ|КРИМІНАЛЬНИЙ|АДМІНІСТРАТИВНИЙ|СУДОВИЙ|Преамбула|Тлумачення)",
        c,
        re.I,
    ):
        return False
    if re.match(r"^[\U0001F300-\U0001FAFF]", c):
        return False
    if c.isupper() and len(c) < 100:
        return False
    if len(c) > 70 and re.search(r"[а-яіїєґa-z]", c, re.I):
        if "." in c or "," in c:
            return True
    if not c.startswith("**") and len(c) > 55:
        return True
    return False


def normalize_heading_line(line: str) -> str | None:
    m = re.match(r"^(#{1,6})\s+(.+)$", line)
    if not m:
        return line
    level = len(m.group(1))
    raw = m.group(2).strip()
    if not raw or raw in ("---", "#"):
        return None
    if raw.startswith("![][image") or raw.startswith("![]"):
        return None
    if is_prose_hash(raw):
        return strip_bold_wrapper(raw)
    content = strip_bold_wrapper(raw)
    level = heading_level_for(content, level)
    if level == 0:
        return content
    if level == 1 and re.match(r"^(Розділ|РОЗДІЛ|ЗМІСТ)", content, re.I):
        level = 2
    return "#" * level + " " + content


def continuation_mergeable(prev: str, cont: str) -> bool:
    cont = cont.strip()
    if not cont:
        return False
    if cont[0].isdigit() or cont.startswith("("):
        return False
    if re.match(r"^[\d*#>|{%]", cont):
        return False
    return True


def merge_soft_breaks(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        stripped = line.rstrip()
        if (
            out
            and stripped
            and stripped[0] == " "
            and out[-1].strip()
            and continuation_mergeable(out[-1], stripped)
            and not out[-1].lstrip().startswith(("#", "-", "*", "|", ">", "{%"))
        ):
            out[-1] = out[-1].rstrip() + " " + stripped.strip()
            continue
        out.append(stripped)
    return out


def merge_wrapped_paragraphs(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (
            line.strip()
            and i + 2 < len(lines)
            and not lines[i + 1].strip()
            and lines[i + 2].startswith(" ")
            and not line.lstrip().startswith(("#", "-", "*", "|"))
        ):
            para = line.strip()
            i += 2
            while i < len(lines) and lines[i].startswith(" "):
                para += " " + lines[i].strip()
                i += 1
            out.append(para)
            continue
        out.append(line)
        i += 1
    return out


def promote_articles(line: str) -> str:
    m = re.match(r"^\*\*(Стаття\s+.+?)\*\*\s*$", line.strip())
    if m:
        return f"### {m.group(1).strip()}"
    m = re.match(r"^\*\*(Розділ\s+\d+:.+?)\*\*\s*$", line.strip())
    if m:
        return f"## {m.group(1).strip()}"
    return line


def cleanup_stray_markers(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        if re.match(r"^#{1,6}\s*$", line):
            continue
        if line.strip() in ("#", "##", "####"):
            continue
        out.append(line)
    return out


def format_body(body: str) -> str:
    body = body.replace("\r\n", "\n")
    lines = body.split("\n")
    lines = merge_wrapped_paragraphs(lines)
    lines = merge_soft_breaks(lines)

    out: list[str] = []
    h1_set = False
    for line in lines:
        line = unwrap_list_hashes(line)
        line = promote_articles(line)

        if re.match(r"^#{1,6}\s*---\s*$", line):
            out.append("---")
            continue

        if re.match(r"^#{1,6}\s", line):
            norm = normalize_heading_line(line)
            if norm is None:
                continue
            if norm == "---":
                out.append("---")
                continue
            if norm.startswith("#"):
                if re.match(r"^#\s", norm) and not h1_set:
                    h1_set = True
                elif re.match(r"^#\s", norm) and h1_set:
                    norm = "##" + norm[1:]
                out.append(norm)
            else:
                out.append(norm)
            continue

        if not line.strip():
            out.append("")
            continue

        line = line.replace("\t", " ")
        line = re.sub(r"^○\s*", "- ", line)
        line = re.sub(r"^  ○\s*", "  - ", line)
        out.append(line.rstrip())

    out = cleanup_stray_markers(out)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def normalize_h1(body: str, filename: str) -> str:
    title = H1_TITLES[filename]
    body = re.sub(r"^#\s+.+", f"# {title}", body, count=1, flags=re.MULTILINE)
    if filename == "constitution.md":
        body = re.sub(
            rf"^# {title}\n\n{title}\n",
            f"# {title}\n\n",
            body,
            flags=re.MULTILINE,
        )
        body = re.sub(r"^---\n\n## Преамбула", "## Преамбула", body, count=1, flags=re.MULTILINE)
    return body


def merge_comma_paragraphs(body: str) -> str:
    lines = body.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (
            not line.strip()
            and out
            and out[-1].rstrip().endswith((",", ";"))
            and not out[-1].startswith(("#", "-", "*", "{%"))
        ):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and not lines[j].startswith("#"):
                out[-1] = out[-1].rstrip() + " " + lines[j].strip()
                i = j + 1
                continue
        stripped = line.strip()
        if (
            out
            and stripped
            and not stripped.startswith("#")
            and not out[-1].startswith("#")
            and not out[-1].startswith(("-", "*", "{%"))
            and out[-1].rstrip().endswith((",", ";"))
        ):
            out[-1] = out[-1].rstrip() + " " + stripped
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def split_article_paragraphs(body: str) -> str:
    """Break long judicial-style lines before top-level пункти (2., 3., …)."""
    lines = body.split("\n")
    out: list[str] = []
    for line in lines:
        if line.startswith("### Стаття") or re.match(r"^\d+\\\.", line):
            parts = re.split(r"(?<=\.)\s+(?=\d+\\\.)", line)
            if len(parts) > 1:
                out.extend(parts)
                continue
        out.append(line)
    return "\n".join(out)


def main() -> None:
    for rel, primary_asset, slug in FILES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8-sig")
        front, body = split_header(text)
        front = inject_layout(front)
        body, images = extract_all_images(body, slug, primary_asset)
        body = apply_image_markers(body, images)
        body = format_body(body)
        body = split_article_paragraphs(body)
        body = merge_comma_paragraphs(body)
        body = normalize_h1(body, path.name)
        body = re.sub(r"\n{3,}", "\n\n", body)
        path.write_text(front + body, encoding="utf-8", newline="\n")
        print(f"OK  {rel}  ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
