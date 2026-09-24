#!/usr/env python3
"""Compare law wiki Класифікація vs ps-mdt PenalCode class by statute id."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHINAZES = Path(__file__).resolve().parents[2] / "chinazes"
if not CHINAZES.exists():
    CHINAZES = Path(r"F:\git\chinazes")

wiki_kk = (ROOT / "laws/criminal-code.md").read_text(encoding="utf-8")
wiki_ak = (ROOT / "laws/administrative-code.md").read_text(encoding="utf-8")
mdt = (CHINAZES / "resources/[unit]/ps-mdt/shared/config.lua").read_text(encoding="utf-8")

VALID = frozenset(
    {"Правопорушення", "Проступок", "Тяжкий злочин", "Особливо тяжкий злочин"}
)
ESPECIALLY = frozenset(
    {
        f"К.К. ст {x}"
        for x in (
            "1.7", "1.8", "1.9", "1.10", "1.11", "1.12", "1.13", "1.14",
            "1.23", "1.24",
            "5.15",
        )
    }
)
KIDNAP_HEAVY_ONLY = frozenset(
    {f"К.К. ст 1.{n}" for n in range(15, 22)}
)
ARMED_PROPERTY_HEAVY_ONLY = frozenset(
    {f"К.К. ст {x}" for x in ("2.2", "2.8", "2.9", "2.10", "8.8")}
)


def parse_wiki(text: str, prefix: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in re.finditer(
        r"### Стаття ([\d.]+)\.[^\n]*\n(?:.*?\n)*?[●*] Класифікація:\s*([^\n]+)",
        text,
        re.DOTALL,
    ):
        out[f"{prefix} ст {m.group(1)}"] = m.group(2).strip()
    return out


wiki = {**parse_wiki(wiki_kk, "К.К."), **parse_wiki(wiki_ak, "А.К.")}

mdt_d: dict[str, str] = {}
for m in re.finditer(r"class = '([^']+)', id = '([^']+)'", mdt):
    mdt_d[m.group(2)] = m.group(1)

mismatch = [
    (i, wiki[i], mdt_d[i])
    for i in sorted(set(wiki) & set(mdt_d))
    if wiki[i] != mdt_d[i]
]
miss_wiki = sorted(set(mdt_d) - set(wiki))
miss_mdt = sorted(set(wiki) - set(mdt_d))
ak_bad = [(i, c) for i, c in wiki.items() if i.startswith("А.К.") and c != "Правопорушення"]
invalid = [(i, c) for i, c in mdt_d.items() if c not in VALID]
policy = []
for i in sorted(set(wiki) & set(mdt_d)):
    if i in ESPECIALLY and wiki[i] != "Особливо тяжкий злочин":
        policy.append((i, "expected Особливо тяжкий", wiki[i], mdt_d[i]))
    if i.startswith("К.К. ст 1.5") or i == "К.К. ст 1.6":
        if wiki[i] == "Особливо тяжкий злочин":
            policy.append((i, "must not be Особливо тяжкий (необережність)", wiki[i], mdt_d[i]))
    if i in KIDNAP_HEAVY_ONLY:
        if wiki[i] != "Тяжкий злочин" or mdt_d[i] != "Тяжкий злочин":
            policy.append((i, "викрадення — лише Тяжкий злочин", wiki[i], mdt_d[i]))
    if i in ARMED_PROPERTY_HEAVY_ONLY:
        if wiki[i] != "Тяжкий злочин" or mdt_d[i] != "Тяжкий злочин":
            policy.append((i, "зброя щодо майна — лише Тяжкий злочин", wiki[i], mdt_d[i]))

print("MDT vs Wiki mismatch:", len(mismatch))
for row in mismatch:
    print(f"  {row[0]}: wiki={row[1]!r} mdt={row[2]!r}")
print("In MDT, not parsed from wiki:", len(miss_wiki))
for i in miss_wiki:
    print(f"  {i} ({mdt_d[i]})")
print("In wiki, not in MDT:", len(miss_mdt))
for i in miss_mdt:
    print(f"  {i} ({wiki[i]})")
print("AK wiki not Правопорушення:", len(ak_bad))
for i, c in ak_bad:
    print(f"  {i}: {c}")
print("Invalid MDT class:", len(invalid))
for i, c in invalid:
    print(f"  {i}: {c}")
print("Policy (ст.1 особливо тяжкий):", len(policy))
for row in policy:
    print(f"  {row[0]}: {row[1]} wiki={row[2]!r} mdt={row[3]!r}")
