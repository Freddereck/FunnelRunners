# -*- coding: utf-8 -*-
"""Short handbook labels + new menu strings; null-pad short titles to stop UI overflow."""
from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Mods\FunnelRunners_RU")
MAP = ROOT / "translations" / "ui_ru_map.json"
RETOC = Path(r"C:\Mods\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
GAME_UTOC = Path(
    r"F:\SteamLibrary\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)
PAKS = Path(
    r"F:\SteamLibrary\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks"
)
CHUNKS = ROOT / "chunks_ui"
RAW = ROOT / "raw_ui_loc"
OUT = ROOT / "out_ui_loc"

# Short list labels (row-name slots are long; keep visible part tiny).
TITLES: dict[str, str] = {
    "Training #00STRT": "Start",
    "Training #01ESC": "Pobeg",
    "Training #02RDR": "Radar",
    "Training #03RAT": "Ekran",
    "Training #04BRN": "Zadach",
    "Training #05CHTCHT": "Raciya",
    "Training #06SDQ": "Sklad",
    "Training #07SHP": "Magazin",
    "Training #08BOB": "Tools",
    "Training #09CAT": "Domkr",
    "Training #10HLFLF": "Lom",
    "Training #11DRK": "Fonari",
    "Training #12PHNX": "Defib",
    "Training #13KLLY": "Zont",
    "Training #14SCF": "Provod",
    "Training #15SNCK": "Snek",
    "Training #16BTTN": "Knopka",
    "Training #17SNC": "Beg",
    "Training #18MNQ": "Motor",
    "Training #19NRGY": "Energy",
    "Training #20SHRT": "Korot",
    "Training #21STCK": "Maslo",
    "Training #22CLD": "OJ",
    "Training #23GSGSGS": "Fuel",
    "Training #24GSRN": "Kanist",
    "Training #25BTTL": "Butyl",
    "Training #26FRZ": "Holod",
    "Training #27RBBR": "Shina",
    "Training #28FSS": "Predoh",
    "Training #29BTTRY": "AKB",
    "Training #30XTR": "Lut",
    "Training #31CSHGRB": "Token",
    "Training #32FNNL": "Voronk",
    "Training #33DMG": "Uron",
    "Training #34SNG": "Dozhd",
    "Training #35NCLR": "Kislot",
    "Training #36ICED": "Grad",
    "Training #37SHCK": "Tok",
    "Training #38QTE": "QTE",
    "Training #39WBC": "Versta",
    "Training #40WBD": "Doska",
    "Training #41LPC": "Arhiv",
    "Training #42LCK": "Shkaf",
    "Training #43BRD": "Radio",
}

# Bodies: keep well under slot; ASCII translit for odd ANSI bodies.
BODIES: dict[str, str] = {
    "Communication is key. To use the walkie-talkie press [{Key0}] to turn it on and off and [{Key1}] to talk to your teammates. Please limit conversation to work-related topics, such as your survival.": (
        "Raciya: [{Key0}] vkl/vykl, [{Key1}] govorit. Tolko po delu."
    ),
    "This is a consumable. Like the name suggests, it will get consumed after use. Hold [{Key0}] to use it, each one either heals you or gives different temporary benefits. ": (
        "Rashodnik. Derzhite [{Key0}] — lechit ili buff."
    ),
    "Running can help you get to places quickly or escape danger, just be careful to not \u201crun\u201d out of stamina or you\u2019ll have to stop and rest (break time will be automatically deducted from your paycheck).": (
        "Beg uskorayet, no stamina konchayetsya - otdyh spishet s zarplaty."
    ),
    "Running can help you get to places quickly or escape danger, just be careful to not \"run\" out of stamina or you'll have to stop and rest (break time will be automatically deducted from your paycheck).": (
        "Beg uskorayet, no stamina konchayetsya - otdyh spishet s zarplaty."
    ),
    "Defibrillators can bring a fellow employee back from the brink of death!, it can also let them keep working for us. To use it, hold [{Key0}] to charge it up, and aim at a downed employee to revive them.": (
        "Defib: derzhite [{Key0}], tsel'tes' v lezhashchego — ozhivit."
    ),
    "You are looking at the van\u2019s engine, your only hope for escape. It\u2019s also APEX\u2019s property, so treat it with care. Interact with any highlighted element to get more information on how to fix it. Don\u2019t forget to check the fuel tank and the tires later.": (
        "Dvigatel van - shans na pobeg. Tyknite podsvetku: kak chinit. Potom bak i shiny."
    ),
    "You are looking at the van's engine, your only hope for escape. It's also APEX's property, so treat it with care. Interact with any highlighted element to get more information on how to fix it. Don't forget to check the fuel tank and the tires later.": (
        "Dvigatel van - shans na pobeg. Tyknite podsvetku: kak chinit. Potom bak i shiny."
    ),
    "The monitors let you see what other employees are doing, and help you work better as a team (if you see anyone slacking off please report it).": (
        "Monitory: chto delayut drugie. Lentyaev — v raport."
    ),
    "This is the storage box. You have to bring all collectables you find here, newspapers, VHS tapes, files, and the like, otherwise you will not get any rewards out of them, company policy.": (
        "Sklad: nesite gazety/VHS/fayly syuda — inache net nagrad."
    ),
    "Crowbars can help you open barricaded doors. Don’t worry about breaking and entering charges, these houses are going to be broken soon anyway. To use it, go towards any barricaded door and press [{Key0}].": (
        "Lom: k zabitoj dveri i [{Key0}]."
    ),
    "Crowbars can help you open barricaded doors. Don't worry about breaking and entering charges, these houses are going to be broken soon anyway. To use it, go towards any barricaded door and press [{Key0}].": (
        "Lom: k zabitoj dveri i [{Key0}]."
    ),
    "Flashlights can help you illuminate dark places. Press [{Key0}] to turn them on and off. Don’t leave them on unnecessarily, their batteries run out!.": (
        "Fonari: [{Key0}] vkl/vykl. Ne zhgi zrya batareyku."
    ),
    "Flashlights can help you illuminate dark places. Press [{Key0}] to turn them on and off. Don't leave them on unnecessarily, their batteries run out!.": (
        "Fonari: [{Key0}] vkl/vykl. Ne zhgi zrya batareyku."
    ),
    "Portable conductors will protect you from lightning. No need to do anything special, just hold them out and you’ll be fine (probably).": (
        "Provodnik ot molniy — prosto derzhite."
    ),
    "Portable conductors will protect you from lightning. No need to do anything special, just hold them out and you'll be fine (probably).": (
        "Provodnik ot molniy — prosto derzhite."
    ),
    "Dressing appropriately is company policy! Use the locker to change your uniform, which will alter certain aspects of your gameplay. You can also review your hard-earned official merits here. Look sharp, employee!": (
        "Shkaf: forma (vliyet na igru) i zaslugi."
    ),
}

# Menu / tips / schematic (same-size; odd → ASCII)
MENUS: dict[str, str] = {
    "SESSION LOBBY": "LOBBI",
    "QUICK FILTERS": "FILTRY",
    "// STORM CREW": "// SPR",
    "Locker": "Shkaf",
    "Handbook": "Spravka",
    "Computer": "Komp",
    "Storage": "Sklad",
    "Monitors": "Ekrany",
    "Whiteboard": "Doska",
    "Workbench": "Verstak",
    "Vitastation": "Magazin",
    "Mission Board": "Missii",
    "SELECT UNIFORM": "FORMA",
    "MERITS": "ZASLUGI",
    "Carrying heavy items reduces movement speed": "Heavy loot slows you",
    # Employee slot label prefix if present as plain string
    "EMPLOYEE": "SOTR.",
}


def fit_ansi_nullpad(old_blob: bytes, new_text: str) -> bytes | None:
    """Same-size ANSI; pad with NUL so UMG width doesn't explode on spaces."""
    size = len(old_blob)
    payload = size - 4
    if payload < 2:
        return None
    max_chars = payload - 1
    text = new_text[:max_chars]
    if any(ord(c) > 127 for c in text):
        return None
    raw = text.encode("ascii") + (b"\x00" * (max_chars - len(text))) + b"\x00"
    if len(raw) != payload:
        return None
    return struct.pack("<i", payload) + raw


def fit_ansi_space(old_blob: bytes, new_text: str) -> bytes | None:
    size = len(old_blob)
    payload = size - 4
    if payload < 2:
        return None
    max_chars = payload - 1
    text = new_text[:max_chars]
    if any(ord(c) > 127 for c in text):
        return None
    if len(text) < max_chars:
        text = text + (" " * (max_chars - len(text)))
    raw = text.encode("ascii") + b"\x00"
    if len(raw) != payload:
        return None
    return struct.pack("<i", payload) + raw


def fit_utf16(old_blob: bytes, new_text: str) -> bytes | None:
    size = len(old_blob)
    ln = struct.unpack_from("<i", old_blob, 0)[0]
    if ln >= 0:
        # convert even ANSI payload to UTF-16 when possible
        payload = size - 4
        if payload % 2 != 0 or payload < 4:
            return None
        units = payload // 2
        max_chars = units - 1
        if max_chars < 1:
            return None
        text = new_text[:max_chars]
        if len(text) < max_chars:
            text = text + (" " * (max_chars - len(text)))
        raw = text.encode("utf-16-le") + b"\x00\x00"
        if len(raw) != payload:
            return None
        return struct.pack("<i", -units) + raw
    units = -ln
    payload = units * 2
    max_chars = units - 1
    text = new_text[:max_chars]
    if len(text) < max_chars:
        text = text + ("\u0000" * (max_chars - len(text)))  # null-pad utf16 units
    # For UTF-16 titles prefer null-pad for width; bodies use spaces
    if any(c == "\u0000" for c in text[1:]):
        # rebuild: visible + null units
        vis = new_text[:max_chars]
        pad_units = max_chars - len(vis)
        raw = vis.encode("utf-16-le") + (b"\x00\x00" * pad_units) + b"\x00\x00"
    else:
        text = new_text[:max_chars]
        if len(text) < max_chars:
            text = text + (" " * (max_chars - len(text)))
        raw = text.encode("utf-16-le") + b"\x00\x00"
    if len(raw) != payload:
        return None
    return struct.pack("<i", -units) + raw


def patch_map(data: bytes, mapping: dict[str, str], null_pad_keys: set[str]) -> tuple[bytes, int]:
    hits: list[tuple[int, int, str, str]] = []
    i = 0
    n = len(data)
    keyset = set(mapping)
    while i + 4 <= n:
        ln = struct.unpack_from("<i", data, i)[0]
        if 2 <= ln <= 800 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii")
                if s in keyset:
                    hits.append((i, i + 4 + ln, s, mapping[s]))
                i += 4 + ln
                continue
        if -800 <= ln <= -2:
            nbytes = (-ln) * 2
            if i + 4 + nbytes <= n:
                try:
                    s = data[i + 4 : i + 4 + nbytes].decode("utf-16-le")
                    if s.endswith("\x00"):
                        s = s[:-1]
                    # trim embedded nulls for match
                    s_clean = s.split("\x00")[0]
                    if s in keyset:
                        hits.append((i, i + 4 + nbytes, s, mapping[s]))
                        i += 4 + nbytes
                        continue
                    if s_clean in keyset:
                        hits.append((i, i + 4 + nbytes, s_clean, mapping[s_clean]))
                        i += 4 + nbytes
                        continue
                except Exception:
                    pass
        i += 1

    out = bytearray(data)
    ok = 0
    for start, end, old, new in sorted(hits, key=lambda h: h[0], reverse=True):
        old_blob = bytes(out[start:end])
        if old in null_pad_keys or old.startswith("Training #"):
            repl = fit_ansi_nullpad(old_blob, new) or fit_utf16(old_blob, new)
        else:
            repl = fit_utf16(old_blob, new) or fit_ansi_space(old_blob, new) or fit_ansi_nullpad(
                old_blob, new
            )
        if repl is None or len(repl) != len(old_blob):
            continue
        out[start:end] = repl
        ok += 1
    assert len(out) == len(data)
    return bytes(out), ok


def main() -> int:
    m: dict[str, str] = json.loads(MAP.read_text(encoding="utf-8"))
    m.update(TITLES)
    m.update(BODIES)
    m.update(MENUS)
    # Prefer short ASCII titles over old Cyrillic/long ones for list slots
    MAP.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("map", len(m))

    # Rebuild base UI from map first
    rc = subprocess.call([sys.executable, str(ROOT / "tools" / "build_ui_loc_safe.py")])
    if rc != 0:
        return rc

    # Extra null-pad pass on tutorial + menus (re-get patched from installed? use chunks after build)
    # build_ui_loc_safe overwrites chunks from game then patches — read installed UI chunk
    tut_id = "ef3ae707dd08c5be00000001"
    lob_id = "eb4fe21d56945ec600000001"
    crew_id = "260ec32e1fdf26d900000001"
    van_id = "b59f6ff6f0eaa61a00000001"
    tips_id = "63e53e5b4d48dcbd00000001"
    lock_id = None
    for cid, name in [
        (tut_id, "DT_TutorialMessages"),
        (lob_id, "W_SearchLobbies_New"),
        (crew_id, "W_CrewAssembly_New"),
        (van_id, "W_VanSchematic"),
        (tips_id, "DT_LoadingScreenTips"),
    ]:
        dest = CHUNKS / f"{name}.bin"
        subprocess.check_call(
            [str(RETOC), "get", str(PAKS / "FunnelRunners_RU_UI_P.utoc"), cid, str(dest)]
        )

    combined = {**TITLES, **BODIES, **MENUS}
    null_keys = set(TITLES)
    raw_chunks = RAW / "chunks"
    if not raw_chunks.is_dir():
        raw_chunks = RAW

    id_by_name = {
        "DT_TutorialMessages": tut_id,
        "W_SearchLobbies_New": lob_id,
        "W_CrewAssembly_New": crew_id,
        "W_VanSchematic": van_id,
        "DT_LoadingScreenTips": tips_id,
    }
    for name, cid in id_by_name.items():
        src = CHUNKS / f"{name}.bin"
        data = src.read_bytes()
        data2, ok = patch_map(data, combined, null_keys)
        src.write_bytes(data2)
        dst = raw_chunks / cid
        if dst.exists():
            dst.write_bytes(data2)
            print(f"{name}: nullpad/extra ok={ok}")
        else:
            print("missing raw", cid)

    # Also patch Locker widget MERITS / SELECT UNIFORM if present
    for cid, name in [
        ("c0a0c0a0c0a0c0a000000001", "skip"),
    ]:
        pass
    lock_path = CHUNKS / "W_Locker.bin"
    if lock_path.exists():
        # refresh from UI pack
        # find locker chunk id from build_ui ASSETS
        sys.path.insert(0, str(ROOT / "tools"))
        import build_ui_loc_safe as ui  # type: ignore

        for cid, (n, _) in ui.ASSETS.items():
            if n == "W_Locker":
                subprocess.check_call(
                    [
                        str(RETOC),
                        "get",
                        str(PAKS / "FunnelRunners_RU_UI_P.utoc"),
                        cid,
                        str(lock_path),
                    ]
                )
                d2, ok = patch_map(lock_path.read_bytes(), MENUS, set())
                lock_path.write_bytes(d2)
                dst = raw_chunks / cid
                if dst.exists():
                    dst.write_bytes(d2)
                print(f"W_Locker: ok={ok}")
                break

    for p in OUT.glob("FunnelRunners_RU_UI_P*"):
        if p.suffix in {".utoc", ".ucas", ".pak"}:
            p.unlink()
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "pack-raw",
            str(RAW),
            str(OUT / "FunnelRunners_RU_UI_P.utoc"),
        ]
    )
    for ext in (".utoc", ".ucas", ".pak"):
        src = OUT / f"FunnelRunners_RU_UI_P{ext}"
        if src.exists():
            subprocess.check_call(["cmd", "/c", "copy", "/Y", str(src), str(PAKS / src.name)])
            print("installed", src.name, src.stat().st_size)

    # verify title padding
    subprocess.check_call(
        [
            str(RETOC),
            "get",
            str(PAKS / "FunnelRunners_RU_UI_P.utoc"),
            tut_id,
            str(CHUNKS / "DT_Tutorial_check.bin"),
        ]
    )
    b = (CHUNKS / "DT_Tutorial_check.bin").read_bytes()
    i = b.find(b"Raciya")
    print("Raciya bytes", b[i : i + 19] if i >= 0 else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
