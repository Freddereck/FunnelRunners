from __future__ import annotations

import json
import pathlib
import re
import struct
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
    "DT_LoadingScreenTips": "63e53e5b4d48dcbd00000001",
    "DT_TutorialMessages": "ef3ae707dd08c5be00000001",
}


def extract(data: bytes):
    i = 0
    n = len(data)
    out = []
    while i + 4 <= n:
        ln = struct.unpack_from("<i", data, i)[0]
        if 2 <= ln <= 800 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii")
                if (
                    any(c.isalpha() for c in s)
                    and "Property" not in s
                    and not re.fullmatch(r"[0-9A-F]{32}", s)
                    and not s.startswith("/")
                    and (
                        " " in s
                        or s.endswith((".", "!", "?"))
                        or (s.isupper() and 3 <= len(s) <= 48)
                        or len(s) >= 8
                    )
                ):
                    payload = ln
                    even = payload % 2 == 0
                    maxc = (payload // 2) - 1 if even else None
                    out.append({"en": s, "payload": payload, "even": even, "max_utf16": maxc})
                i += 4 + ln
                continue
        i += 1
    seen = set()
    res = []
    for e in out:
        if e["en"] not in seen:
            seen.add(e["en"])
            res.append(e)
    return res


def main():
    OUT.mkdir(exist_ok=True)
    catalog = {}
    for name, cid in IDS.items():
        dest = OUT / f"{name}.bin"
        subprocess.check_call([RETOC, "get", UTOC, cid, str(dest)])
        rows = extract(dest.read_bytes())
        catalog[name] = rows
        print(f"=== {name} size={dest.stat().st_size} strings={len(rows)} "
              f"even={sum(1 for r in rows if r['even'])} odd={sum(1 for r in rows if not r['even'])}")
        for r in rows[:40]:
            print(f"  even={r['even']} max={r['max_utf16']} | {r['en'][:120]!r}")
    (TRANS / "tips_tutorial_en.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
