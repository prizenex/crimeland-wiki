#!/usr/bin/env python3
"""Convert label-style markdown tables to lists. Keep price/loot/comparison tables."""
import re
from pathlib import Path

SKIP_FILES = {'WIKI-AUTHORING.md', 'SUMMARY.md', 'структура.md'}
MAX_CONVERT_ROWS = 25

PRICE_HEADERS = {
    'ціна', 'вартість', 'орієнтовна ціна', 'шанс', 'нагорода', 'оплата', 'скільки',
    'джерело', 'деталі в benny', 'ціна деталі',
}
DATA_ROW_HEADERS = {
    'предмет', 'контракт', 'рівень', '№', 'тип', 'категорія', 'зброя', 'послуга',
    'іконка', 'бліп', 'модель',
}
COMPARISON_WORDS = {
    'мала', 'велика', 'fleeca', 'paleto', 'pacific', 'безкоштовна', 'преміум',
    'легальний', 'нелегальний', 'до', 'після',
}


def parse_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith('|'):
        return []
    return [p.strip() for p in line.strip('|').split('|')]


def is_separator(line: str) -> bool:
    return bool(re.match(r'^\|\s*[-:]+\s*\|', line.strip()))


def strip_bold(s: str) -> str:
    return re.sub(r'\*+', '', s).strip()


def has_price(cell: str) -> bool:
    return bool(re.search(r'\$\s*[\d]', cell)) or bool(re.search(r'\d[\d\s]*\$', cell))


def table_rows(lines: list[str], start: int) -> tuple[list[str], list[list[str]], int] | None:
    header = parse_row(lines[start])
    if len(header) < 2:
        return None
    i = start + 1
    if i >= len(lines) or not is_separator(lines[i]):
        return None
    i += 1
    rows = []
    while i < len(lines):
        row_line = lines[i]
        if not row_line.strip().startswith('|'):
            break
        if is_separator(row_line):
            i += 1
            continue
        row = parse_row(row_line)
        if len(row) != len(header):
            break
        rows.append(row)
        i += 1
    if not rows or len(rows) > MAX_CONVERT_ROWS:
        return None
    return header, rows, i


def should_keep_table(header: list[str], rows: list[list[str]]) -> bool:
    hlow = [h.lower() for h in header]
    if len(header) == 3 and any('шанс' in h or '%' in h for h in hlow):
        if any('%' in c for r in rows for c in r):
            return True
    if len(header) == 3 and hlow[0] in ('зібрано', 'сорт', 'категорія'):
        if any('%' in c for r in rows for c in r):
            return True
    cols = len(header)
    joined = '\n'.join('|'.join(r) for r in rows)
    hlow = [h.lower() for h in header]

    if any('%' in c for r in rows for c in r):
        if any('шанс' in h for h in hlow):
            return True

    icon_rows = sum(1 for r in rows for c in r if 'data-size="line"' in c or '<img ' in c.lower())
    if icon_rows >= 2:
        return True

    dollar_rows = sum(1 for r in rows if any(has_price(c) for c in r))
    if dollar_rows >= 2:
        return True

    if cols == 2 and any(h in PRICE_HEADERS or 'ціна' in h for h in hlow):
        if dollar_rows >= 1 or any(h in ('категорія', 'послуга', 'тип') for h in hlow):
            return True

    if cols >= 2 and hlow[0] in DATA_ROW_HEADERS and len(rows) >= 4:
        if dollar_rows >= 1 or icon_rows >= 1 or '%' in joined:
            return True

    if cols >= 3:
        if any(any(w in h for w in COMPARISON_WORDS) for h in hlow[1:]):
            return True
        if dollar_rows >= 2 or '%' in joined:
            return True
        if len(rows) >= 6 and cols >= 3:
            return True
        return False

    if cols == 2:
        return False

    return cols >= 4


def format_row(header: list[str], row: list[str], numbered: bool, n: int) -> str:
    cols = len(header)
    if cols == 2:
        k, v = row[0], row[1]
        key = strip_bold(k)
        if key.lower() in ('крок', 'етап') or re.match(r'^\d+\.?$', key):
            return f'{n}. {v}'
        return f'- **{key}** — {v}'
    if cols == 3 and 'як відновити' in header[2].lower():
        a, b, c = row[0], row[1], row[2]
        return f'- **{strip_bold(a)}** — {b}. Відновити: {c}'
    # fallback: don't emit ugly semicolon lines — keep table
    return None


def use_numbered(header: list[str], rows: list[list[str]]) -> bool:
    h0 = header[0].lower()
    if h0 in ('крок', 'етап', '№'):
        return True
    if rows and re.match(r'^\d+\.?$', strip_bold(rows[0][0])):
        return True
    return False


def convert_table(lines: list[str], start: int) -> tuple[str, int] | None:
    parsed = table_rows(lines, start)
    if not parsed:
        return None
    header, rows, end = parsed
    if should_keep_table(header, rows):
        return None

    numbered = use_numbered(header, rows)
    out = []
    for n, row in enumerate(rows, 1):
        line = format_row(header, row, numbered, n)
        if line is None:
            return None
        out.append(line)
    return '\n'.join(out) + '\n', end


def fix_double_bold(text: str) -> str:
    text = re.sub(r'\*\*\*\*([^*]+)\*\*\*\*', r'**\1**', text)
    text = re.sub(r'\*\*\*\*', r'**', text)
    return text


def process(content: str) -> tuple[str, int]:
    lines = content.splitlines(keepends=True)
    out = []
    i = 0
    changes = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('|') and not is_separator(line):
            result = convert_table([l.rstrip('\n') for l in lines], i)
            if result:
                block, end = result
                out.append(block)
                i = end
                changes += 1
                continue
        out.append(line)
        i += 1
    text = ''.join(out)
    text = fix_double_bold(text)
    return text, changes


def main():
    root = Path(__file__).resolve().parents[1]
    total = 0
    files_changed = []
    for path in sorted(root.rglob('*.md')):
        if path.name in SKIP_FILES or 'tools' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        new_text, n = process(text)
        new_text = fix_double_bold(new_text)
        if n or new_text != text:
            path.write_text(new_text, encoding='utf-8', newline='\n')
            if n:
                files_changed.append((str(path.relative_to(root)), n))
                total += n
    for rel, n in files_changed:
        print(f'{rel}: {n} table(s)')
    print(f'Done: {total} tables in {len(files_changed)} files')


if __name__ == '__main__':
    main()
