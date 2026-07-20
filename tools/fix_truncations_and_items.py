"""Audit bad truncations; extract credits + item strings with slot sizes."""
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
CHUNKS = pathlib.Path(r"C:\Mods\FunnelRunners_RU\chunks_ui")
TRANS = pathlib.Path(r"C:\Mods\FunnelRunners_RU\translations")
MAP = TRANS / "ui_ru_map.json"

AUDIT_CHUNKS = {
    "SettingsData": "d7521c6950c4694300000001",
    "W_CreateRoomPopup": "ad945e8bdf103e9400000001",
    "W_SearchLobbies_New": "eb4fe21d56945ec600000001",
    "W_CrewLobbyInfo": "38ad8f9c44d2301b00000001",
    "DT_Credits": "0d8d29ca121f9b8800000001",
    "W_Credits": "dd048a4b22f7d73b00000001",
    "W_VendingMachine": "0e0bcc8baf35d42300000001",
    "W_VendingItemInfo": "2616228f199c981f00000001",
    "W_Storage": "d8f774b4ddd4963700000001",
    "DA_Bandage": "dc9af4de452c845300000001",
    "DA_Crowbar": "d76090d556fb66a200000001",
    "DA_Defibrillator": "ecedfe76551c85eb00000001",
    "DA_EnergyDrink": "7f99fb7f2f090b8800000001",
    "DA_EnergyPills": "8ad0dbf26ae3cb5900000001",
    "DA_FlashlightLG": "579ad8caa8d8b56000000001",
    "DA_FlashlightSM": "e608301adfa0c03d00000001",
    "DA_GranolaBar": "7201fa886559f4bf00000001",
    "DA_HealthPills": "4770c4eac3f139cf00000001",
    "DA_Medkit": "7d967971b95f06f600000001",
    "DA_PortableConductor": "1f610c9ecee3a5ee00000001",
    "DA_PortableDoppler": "f222dca0e6b09e7f00000001",
    "DA_Umbrella": "51733974fd664b4300000001",
    "DA_Drenched": "b94f8396ba4249d800000001",
    "DA_Electrified": "9237db203f5bed2800000001",
    "DA_Injuried": "c04c6bddb7975a3c00000001",
    "DA_VeryInjuried": "86e63f3d39b0e9f600000001",
    "DA_Acid": "c907e19ed899ae7e00000001",
    "DA_Hail": "568edd91377a697b00000001",
    "DA_Overemcumbered": "24085bf35be9e51d00000001",
}


def extract_fstrings(data: bytes):
    i = 0
    n = len(data)
    out = []
    while i + 4 <= n:
        ln = struct.unpack_from("<i", data, i)[0]
        if 2 <= ln <= 800 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii")
                if any(c.isalpha() for c in s) and "Property" not in s and not re.fullmatch(r"[0-9A-F]{32}", s):
                    payload = ln
                    even = payload % 2 == 0
                    maxc = (payload // 2) - 1 if even else None
                    out.append((s, payload, even, maxc))
                i += 4 + ln
                continue
        i += 1
    seen = set()
    res = []
    for t in out:
        if t[0] not in seen:
            seen.add(t[0])
            res.append(t)
    return res


def main():
    CHUNKS.mkdir(exist_ok=True)
    mapping = json.loads(MAP.read_text(encoding="utf-8"))
    catalog = {}

    for name, cid in AUDIT_CHUNKS.items():
        dest = CHUNKS / f"{name}.bin"
        if not dest.exists() or dest.stat().st_size < 32:
            subprocess.check_call([RETOC, "get", UTOC, cid, str(dest)])
        rows = extract_fstrings(dest.read_bytes())
        catalog[name] = [
            {"en": s, "payload": p, "even": e, "max_utf16": m}
            for s, p, e, m in rows
            if (" " in s or s.endswith((".", "!", "?", ":")) or s.isupper() or len(s) >= 6)
            and not s.startswith("/")
        ]

    # Audit truncations for mapped strings
    print("=== TRUNCATION AUDIT ===")
    en_index = {}
    for name, rows in catalog.items():
        for r in rows:
            en_index.setdefault(r["en"], []).append((name, r))

    bad = []
    for en, ru in mapping.items():
        if en not in en_index:
            continue
        if not any(ord(c) > 127 for c in ru):
            continue
        for name, r in en_index[en]:
            if not r["even"]:
                bad.append((en, ru, name, "ODD_SLOT", None))
            elif len(ru) > r["max_utf16"]:
                shown = ru[: r["max_utf16"]]
                bad.append((en, ru, name, f"TRUNC->{shown!r}", r["max_utf16"]))

    for en, ru, name, why, maxc in bad:
        print(f"[{name}] max={maxc} {why}")
        print(f"  EN: {en}")
        print(f"  RU: {ru}")

    # Credits dump
    print("\n=== CREDITS STRINGS ===")
    for r in catalog.get("DT_Credits", []):
        print(f"  even={r['even']} max={r['max_utf16']} | {r['en'][:120]!r}")

    # Items sample
    print("\n=== ITEM / VENDING SAMPLES ===")
    for name in sorted(catalog):
        if name.startswith("DA_") or name.startswith("W_Vending") or name == "W_Storage":
            useful = [r for r in catalog[name] if " " in r["en"] or len(r["en"]) >= 4]
            if not useful:
                continue
            print(f"-- {name} ({len(useful)})")
            for r in useful[:12]:
                print(f"  even={r['even']} max={r['max_utf16']} | {r['en'][:100]!r}")

    (TRANS / "items_credits_catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (TRANS / "truncation_audit.json").write_text(
        json.dumps(
            [
                {"en": a, "ru": b, "asset": c, "why": d, "max": e}
                for a, b, c, d, e in bad
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nbad truncations: {len(bad)}")


if __name__ == "__main__":
    main()
