# -*- coding: utf-8 -*-
"""Fit content warning, APEX banner, more merits/handbook; rebuild."""
from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Mods\FunnelRunners_RU")
MAP = ROOT / "translations" / "ui_ru_map.json"
CHUNKS = ROOT / "chunks_ui"
RETOC = Path(r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
GAME_UTOC = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)

FILES = [
    "W_ContentWarnings",
    "W_VanSchematic",
    "DT_TutorialMessages",
    "DT_Achievements",
    "W_Locker",
    "DT_SchematicInfo",
]

WARN_EN = (
    "This game contains flashing lights that may trigger photosensitive epilepsy.\r\n\r\n"
    "This game depicts natural disasters and their aftermath, which some players may find distressing."
)
CERT_EN = (
    "ONLY APEX CERTIFIED PARTS CAN BE USED FOR MAINTENANCE. "
    "CONTACT AN AUTHORIZED MECHANIC FOR FIELD REPAIRS."
)

EXTRA = {
    WARN_EN: (
        "Мигающий свет (риск эпилепсии).\r\n\r\n"
        "Стихийные бедствия — может быть тяжело. mderick.dev"
    ),
    # odd ANSI → ASCII only, keep meaning + credit
    CERT_EN: "ONLY APEX PARTS FOR MAINTENANCE. CONTACT AUTHORIZED MECHANIC. mderick.dev",
    "// HANDBOOK": "//СПР",
    # merits short fits
    "Change 4 flat tires in the van.": "Сменить 4 шины",
    "Be revived after passing out in game.": "Вернуться в строй",
    "Fail at a repair minigame 15 times.": "Провал ремонта 15",
    "Win without ever leaving the van.": "Победа в фургоне",
    "Escape the end tornado alone.": "Уйти один",
    "Dead? Me?": "Я?",
    "Bulls Eye": "Ябл.",
    "High Up": "Верх",
    "On Fire": "Огонь",
    "Electrified": "Ток",
    "Porcupine": "Ёжик",
    "Lone Wolf": "Волк",
    "Electric Friendship": "Шок-друг",
    "Designated Driver": "Водитель",
    "First Escape!": "Побег!",
    # handbook even bodies (shorter where needed)
    "These are new fuses, you can replace any blown out fuses that where removed by pressing [{Key0}].": (
        "Новые предохранители: ставьте через [{Key0}]."
    ),
    "This is a new battery, you can replace a broken battery that was removed with a toolbox by pressing [{Key0}].": (
        "Новый АКБ после снятия старого: жмите [{Key0}]."
    ),
    "Welcome {Employee}! Use WASD or <Key id=\"Gamepad_Left2D\"/>  to move around, move the mouse cursor to look around and press [{Key0}] to interact. We will explain things as we go.": (
        "Привет, {Employee}! WASD/<Key id=\"Gamepad_Left2D\"/> ход, мышь взгляд, [{Key0}] действие."
    ),
}


def refresh() -> None:
    ids = {
        "W_ContentWarnings": "f8406abace5b783400000001",
        "W_VanSchematic": "b59f6ff6f0eaa61a00000001",
        "DT_TutorialMessages": "ef3ae707dd08c5be00000001",
        "DT_Achievements": "544e5eb776e67f3c00000001",
        "W_Locker": "2819d6c35480ec5500000001",
        "DT_SchematicInfo": "3bcc87409dfe7bcb00000001",
    }
    for name, cid in ids.items():
        subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(CHUNKS / f"{name}.bin")])


def find_slot(en: str) -> dict | None:
    try:
        ansi = en.encode("ascii") + b"\x00"
    except UnicodeEncodeError:
        ansi = None
    u16 = en.encode("utf-16-le") + b"\x00\x00"
    best = None
    for name in FILES:
        p = CHUNKS / f"{name}.bin"
        if not p.exists():
            continue
        data = p.read_bytes()
        if ansi is not None:
            start = 0
            while True:
                pos = data.find(ansi, start)
                if pos < 4:
                    break
                ln = struct.unpack_from("<i", data, pos - 4)[0]
                if ln == len(ansi):
                    even = ln % 2 == 0
                    info = {
                        "file": name,
                        "enc": "ansi",
                        "payload": ln,
                        "even": even,
                        "max_utf16": (ln // 2) - 1 if even else None,
                        "max_ansi": ln - 1,
                    }
                    if even or any(ord(c) > 127 for c in en):
                        # prefer even for later cyrillic; keep odd for ansi-only
                        if even:
                            return info
                        best = best or info
                    else:
                        best = best or info
                start = pos + 1
        start = 0
        while True:
            pos = data.find(u16, start)
            if pos < 4:
                break
            ln = struct.unpack_from("<i", data, pos - 4)[0]
            units = len(u16) // 2
            if ln == -units:
                return {
                    "file": name,
                    "enc": "utf16",
                    "payload": len(u16),
                    "even": True,
                    "max_utf16": units - 1,
                    "max_ansi": units - 1,
                }
            start = pos + 1
    return best


def fits(slot: dict, ru: str) -> bool:
    if any(ord(c) > 127 for c in ru):
        return slot.get("max_utf16") is not None and len(ru) <= slot["max_utf16"]
    return len(ru) <= slot["max_ansi"]


def main() -> None:
    refresh()
    m = json.loads(MAP.read_text(encoding="utf-8"))
    n_ok = 0
    for en, ru in EXTRA.items():
        slot = find_slot(en)
        if not slot:
            print("NOIDX", en[:60])
            continue
        if fits(slot, ru):
            m[en] = ru
            n_ok += 1
            print("OK", slot["file"], len(ru), "max", slot.get("max_utf16") or slot["max_ansi"], en[:45])
        else:
            print("SKIP", len(ru), "need<=", slot.get("max_utf16") or slot["max_ansi"], en[:45])

    # verify cert length
    print("cert ascii len", len(EXTRA[CERT_EN]), "limit", 104)
    print("warn ru len", len(EXTRA[WARN_EN]), "limit", 88)

    MAP.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("map", len(m), "ok", n_ok)
    sys.stdout.flush()
    raise SystemExit(subprocess.call([sys.executable, "-u", str(ROOT / "tools" / "build_ui_loc_safe.py")]))


if __name__ == "__main__":
    main()
