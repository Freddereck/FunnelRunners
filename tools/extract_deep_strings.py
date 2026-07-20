"""Extract user-facing English strings from DataTables / DataAssets / Widgets."""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"C:\Mods\FunnelRunners_RU\extract\StormEscape\Content\StormEscape")
OUT = pathlib.Path(r"C:\Mods\FunnelRunners_RU\translations")

DATA_FILES = [
    "Data/Tutorial/DT_TutorialMessages.uexp",
    "Data/Loading/DT_LoadingScreenTips.uexp",
    "Data/Achievements/DT_Achievements.uexp",
    "Data/Progression/DT_ProgressionTitles.uexp",
    "Data/Tasks/DT_Tasks.uexp",
    "Data/Lore/DT_LoreArchives.uexp",
    "Data/Settings/SettingsData.uexp",
]

WIDGET_GLOBS = [
    "UI/Widgets/**/W_*.uexp",
    "UI/Widgets/**/WBP_*.uexp",
]

JUNK = {
    "True",
    "False",
    "None",
    "Default",
    "NewEnumerator",
    "ByteProperty",
    "StrProperty",
    "NameProperty",
    "TextProperty",
    "ArrayProperty",
    "StructProperty",
    "ObjectProperty",
    "SoftObjectProperty",
    "FloatProperty",
    "IntProperty",
    "BoolProperty",
    "MapProperty",
    "Class",
    "Package",
    "CoreUObject",
    "Engine",
    "StormEscape",
}


def extract_fstrings(data: bytes) -> list[str]:
    strings: list[str] = []
    i = 0
    n = len(data)
    while i + 4 <= n:
        ln = int.from_bytes(data[i : i + 4], "little", signed=True)
        if 2 <= ln <= 800 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii", errors="ignore")
                if any(c.isalpha() for c in s) and not s.startswith("/Game/") and s != "None":
                    strings.append(s)
                    i += 4 + ln
                    continue
        if -800 <= ln <= -2:
            nbytes = (-ln) * 2
            if i + 4 + nbytes <= n:
                raw = data[i + 4 : i + 4 + nbytes]
                try:
                    s = raw.decode("utf-16-le")
                    if s.endswith("\x00"):
                        s = s[:-1]
                    if any(c.isalpha() for c in s) and "/Game/" not in s:
                        if all((ord(c) < 0x300 or 0x400 <= ord(c) < 0x530) for c in s if not c.isspace()):
                            strings.append(s)
                            i += 4 + nbytes
                            continue
                except Exception:
                    pass
        i += 1
    return strings


def clean_strings(strs: list[str]) -> list[str]:
    clean: list[str] = []
    seen: set[str] = set()
    for s in strs:
        if s in JUNK or s in seen:
            continue
        if s.startswith("b'") or s.startswith("/Script/"):
            continue
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s):
            # keep readable CamelCase / TitleCase only if long enough
            if not (re.search(r"[a-z]", s) and re.search(r"[A-Z]", s) and len(s) >= 8):
                continue
        if " " in s or s.endswith((".", "!", "?")) or len(s) >= 8:
            seen.add(s)
            clean.append(s)
    return clean


def main() -> None:
    files: list[pathlib.Path] = []
    for rel in DATA_FILES:
        p = ROOT / rel
        if p.exists():
            files.append(p)
    for pattern in (
        "Data/Entitlements/VendingItems/DA_*.uexp",
        "Data/Moodlets/DA_*.uexp",
        "Data/Lore/Archives_*.uexp",
        "Data/Lore/archives_*.uexp",
    ):
        files.extend(sorted(ROOT.glob(pattern)))
    for pattern in WIDGET_GLOBS:
        files.extend(sorted(ROOT.glob(pattern)))

    catalog: dict[str, list[str]] = {}
    for p in files:
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        catalog[rel] = clean_strings(extract_fstrings(p.read_bytes()))

    # keep only files that actually have candidate UI strings
    catalog = {k: v for k, v in catalog.items() if v}

    summary = {
        k: {"count": len(v), "samples": v[:12]}
        for k, v in sorted(catalog.items(), key=lambda kv: -len(kv[1]))
    }

    OUT.mkdir(exist_ok=True)
    (OUT / "deep_en_catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "deep_en_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"TOTAL_FILES {len(catalog)}")
    print(f"TOTAL_STRINGS {sum(len(v) for v in catalog.values())}")
    print("--- top sources ---")
    for k, meta in list(summary.items())[:25]:
        print(f"{meta['count']:4d}  {k}")
        for s in meta["samples"][:3]:
            print(f"      - {s[:140]}")


if __name__ == "__main__":
    main()
