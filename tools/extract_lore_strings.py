# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import struct
from pathlib import Path

CH = Path(r"C:\Mods\FunnelRunners_RU\chunks_ui")
OUT = Path(r"C:\Mods\FunnelRunners_RU\translations\lore_extract.json")

FILES = [
    "DT_Achievements",
    "DT_LoreArchives",
    "W_LoreUI",
    "W_LoadingScreen",
    "DA_GameplayMaps",
    "archives_1",
    "W_ArchiveEntry",
    "W_ArchiveDocDisplay",
    "W_MapOption",
    "W_CrewLobbyInfo",
    "DT_LoadingScreenTips",
    "W_Locker",
]


def extract(data: bytes) -> list[dict]:
    out: list[dict] = []
    i = 0
    n = len(data)
    while i + 4 <= n:
        ln = struct.unpack_from("<i", data, i)[0]
        if 2 <= ln <= 4000 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii")
                if any(c.isalpha() for c in s):
                    if len(s) == 32 and all(c in "0123456789ABCDEFabcdef" for c in s):
                        i += 4 + ln
                        continue
                    even = ln % 2 == 0
                    out.append(
                        {
                            "enc": "ansi",
                            "en": s,
                            "payload": ln,
                            "even": even,
                            "max_utf16": (ln // 2) - 1 if even else None,
                        }
                    )
                i += 4 + ln
                continue
        if -4000 <= ln <= -2:
            nbytes = (-ln) * 2
            if i + 4 + nbytes <= n:
                try:
                    s = data[i + 4 : i + 4 + nbytes].decode("utf-16-le")
                    if s.endswith("\x00"):
                        s = s[:-1]
                    printable = sum(1 for c in s if 32 <= ord(c) < 127 or ord(c) > 160)
                    if len(s) >= 2 and printable / max(len(s), 1) > 0.75:
                        out.append(
                            {
                                "enc": "utf16",
                                "en": s,
                                "payload": nbytes,
                                "max_utf16": len(s),
                            }
                        )
                        i += 4 + nbytes
                        continue
                except Exception:
                    pass
        i += 1
    return out


def main() -> None:
    result: dict[str, list] = {}
    for name in FILES:
        p = CH / f"{name}.bin"
        if not p.exists():
            continue
        keep = []
        for r in extract(p.read_bytes()):
            s = r["en"]
            if r["enc"] == "ansi" and len(s) < 3:
                continue
            if any(ord(c) < 32 and c not in "\t\n\r" for c in s):
                continue
            keep.append(r)
        result[name] = keep
        print(name, len(keep))
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
