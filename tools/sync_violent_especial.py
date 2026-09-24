#!/usr/bin/env python3
"""Sync Особливо тяжкий злочин (wiki + ps-mdt)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KK = ROOT / "laws/criminal-code.md"
MDT = Path(__file__).resolve().parents[2] / "chinazes/resources/[unit]/ps-mdt/shared/config.lua"

ESPECIAL = {
    "1.7", "1.8", "1.9", "1.10", "1.11", "1.12", "1.13", "1.14",
    "1.23", "1.24",
    "5.15",
}

def patch_wiki(text: str) -> str:
    def repl_block(m: re.Match) -> str:
        num = m.group(1)
        body = m.group(2)
        if num in ESPECIAL:
            body = re.sub(
                r"\* Класифікація: (?:Тяжкий злочин|Особливо тяжкий злочин)",
                "* Класифікація: Особливо тяжкий злочин",
                body,
                count=1,
            )
        elif re.search(r"\* Класифікація: Особливо тяжкий злочин", body):
            body = re.sub(
                r"\* Класифікація: Особливо тяжкий злочин",
                "* Класифікація: Тяжкий злочин",
                body,
                count=1,
            )
        return f"### Стаття {num}.{body}"

    text = re.sub(
        r"### Стаття ([\d.]+)\.([^\n]*\n(?:.*?\n)*?)(?=### Стаття |\Z)",
        repl_block,
        text,
        flags=re.DOTALL,
    )
    return text


def patch_mdt(text: str) -> str:
    for num in ESPECIAL:
        sid = f"К.К. ст {num}"
        text = re.sub(
            rf"(class = ')(?:Тяжкий злочин|Особливо тяжкий злочин)(', id = '{re.escape(sid)}')",
            r"\1Особливо тяжкий злочин\2",
            text,
        )

    def demote(m: re.Match) -> str:
        num = m.group(1)
        if num in ESPECIAL:
            return m.group(0)
        return f"class = 'Тяжкий злочин', id = 'К.К. ст {num}'"

    text = re.sub(
        r"class = 'Особливо тяжкий злочин', id = 'К\.К\. ст ([\d.]+)'",
        demote,
        text,
    )
    return text


def main() -> None:
    kk = KK.read_text(encoding="utf-8")
    KK.write_text(patch_wiki(kk), encoding="utf-8")
    mdt = MDT.read_text(encoding="utf-8")
    MDT.write_text(patch_mdt(mdt), encoding="utf-8")
    print(f"Особливо тяжкий: {len(ESPECIAL)} статей.")


if __name__ == "__main__":
    main()
