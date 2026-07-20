"""Extract Settings + Main Menu zen chunks and dump user-facing EN strings."""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

RETOC = r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe"
UTOC = (
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)
OUT = pathlib.Path(r"C:\Mods\FunnelRunners_RU\chunks_ui")
TRANS = pathlib.Path(r"C:\Mods\FunnelRunners_RU\translations")

IDS = {
    "SettingsData": "d7521c6950c4694300000001",
    "W_MainMenu": "ee97fce02a60f58900000001",
    "W_StormSettings": "0ad2fc9ead3a07c900000001",
    "W_PauseMenu": "369eaf72f4466c2300000001",
    "W_CreateRoomPopup": "ad945e8bdf103e9400000001",
    "W_SearchLobbies_New": "eb4fe21d56945ec600000001",
    "W_ContentWarnings": "f8406abace5b783400000001",
    "W_CrewAssembly_New": "260ec32e1fdf26d900000001",
    "W_TermsAndConditions": "86067bedad38fbe700000001",
    "W_ErrorPopup": "422e5cf40df4847400000001",
    "W_CrewLobbyInfo": "38ad8f9c44d2301b00000001",
    "W_SessionNameField": "83fb7474c0b3c79000000001",
}

NOISE_RE = re.compile(
    r" ALL\(|Border_|Widget|Canvas|Image_|Button_|TextBlock|SizeBox|Overlay|"
    r"Horizontal|Vertical|Scroll|Spacer|ProgressBar|CheckBox|Slider|ComboBox|"
    r"EditableText|RichText|WrapBox|GridPanel|UniformGrid|NamedSlot|ScaleBox|"
    r"SafeZone|Invalidation|Retainer|Throbber|ListView|TreeView|MenuAnchor|"
    r"WidgetSwitcher|BackgroundBlur|InputKeySelector"
)


def extract_fstrings(data: bytes) -> list[tuple[int, str, str]]:
    strings: list[tuple[int, str, str]] = []
    i = 0
    n = len(data)
    while i + 4 <= n:
        ln = int.from_bytes(data[i : i + 4], "little", signed=True)
        if 2 <= ln <= 600 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii")
                if (
                    any(c.isalpha() for c in s)
                    and not s.startswith("/Game/")
                    and "Property" not in s
                    and not re.fullmatch(r"[0-9A-F]{32}", s)
                ):
                    strings.append((i, s, "ansi"))
                i += 4 + ln
                continue
        if -600 <= ln <= -2:
            nbytes = (-ln) * 2
            if i + 4 + nbytes <= n:
                raw = data[i + 4 : i + 4 + nbytes]
                try:
                    s = raw.decode("utf-16-le")
                    if s.endswith("\x00"):
                        s = s[:-1]
                    if any(c.isalpha() for c in s) and "/Game/" not in s:
                        strings.append((i, s, "utf16"))
                        i += 4 + nbytes
                        continue
                except Exception:
                    pass
        i += 1
    return strings


def keep(s: str) -> bool:
    if NOISE_RE.search(s):
        return False
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s):
        if s.isupper() and 3 <= len(s) <= 28:
            return True
        if len(s) >= 6 and re.search(r"[a-z]", s) and any(c.isupper() for c in s):
            # CamelCase identifiers — only keep if looks like UI label words
            return False
        return False
    return (" " in s) or s.endswith((".", "!", "?", ":")) or len(s) >= 8


def main() -> None:
    OUT.mkdir(exist_ok=True)
    TRANS.mkdir(exist_ok=True)
    for name, cid in IDS.items():
        dest = OUT / f"{name}.bin"
        subprocess.check_call([RETOC, "get", UTOC, cid, str(dest)])
        print(f"{name}: {dest.stat().st_size}")

    catalog: dict[str, list[dict]] = {}
    for name in IDS:
        data = (OUT / f"{name}.bin").read_bytes()
        clean: list[dict] = []
        seen: set[str] = set()
        for off, s, enc in extract_fstrings(data):
            if s in seen or not keep(s):
                continue
            seen.add(s)
            clean.append({"offset": off, "en": s, "enc": enc})
        catalog[name] = clean
        print(f"--- {name} ({len(clean)}) ---")
        for e in clean[:40]:
            print(f"  {e['en'][:140]}")

    path = TRANS / "ui_menu_settings_en.json"
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {path} total={sum(len(v) for v in catalog.values())}")


if __name__ == "__main__":
    main()
