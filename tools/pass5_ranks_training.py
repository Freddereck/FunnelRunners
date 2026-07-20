# -*- coding: utf-8 -*-
"""Ranks + Training titles + #01ESC body + more merits; rebuild UI pack."""
from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Mods\FunnelRunners_RU")
MAP = ROOT / "translations" / "ui_ru_map.json"
CHUNKS = ROOT / "chunks_ui"
EXTRACT = ROOT / "extract_ui"
RETOC = Path(r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
GAME_UTOC = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)
PAKS = GAME_UTOC.parent

NEW = {
    "4c499511be10632100000001": (
        "DT_ProgressionTitles",
        "StormEscape/Data/Progression/DT_ProgressionTitles",
    ),
    "8a7c18cb873e5a7d00000001": (
        "W_PlayerInfo",
        "StormEscape/UI/Widgets/PauseMenu/SubWidgets/W_PlayerInfo",
    ),
}

ESC_EN = Path(r"C:\Mods\FunnelRunners_RU\translations\_esc_body.txt").read_text(encoding="utf-8")

# Training list labels (max 7 for most even titles)
TRAINING_TITLES = {
    "Training #01ESC": "Побег",
    "Training #02RDR": "Радар",
    "Training #03RAT": "Экраны",
    "Training #04BRN": "Задачи",
    "Training #06SDQ": "Склад",
    "Training #07SHP": "Магаз.",
    "Training #08BOB": "Ящик",
    "Training #09CAT": "Домкрат",
    "Training #10HLFLF": "Фонари",  # max 8
    "Training #11DRK": "Темнота",
    "Training #14SCF": "Зонт",
    "Training #17SNC": "Еда",
    "Training #18MNQ": "Таблет.",
    "Training #22CLD": "ОЖ",
    "Training #26FRZ": "Антифриз",  # 8 > 7 skip
    "Training #28FSS": "Предохр",
    "Training #29BTTRY": "АКБ",  # max 8
    "Training #30XTR": "Лут",
    "Training #33DMG": "Урон",
    "Training #34SNG": "Дождь",
    "Training #38QTE": "QTE",
    "Training #39WBC": "Верстак",
    "Training #40WBD": "Доска",
    "Training #41LPC": "Архив",
    "Training #42LCK": "Шкаф",
    "Training #43BRD": "Рация",
}

RANKS = {
    "Field Recruit": "Рекрут",  # max 6
    "Event Marshal": "Маршал",  # max 6
    "Disaster Lead": "Лидер",  # max 6
    # odd ranks — ASCII short labels (no Cyrillic possible)
    "Junior Spotter": "Jr Spotter",
    "Data Scout": "Data Scout",
    "Storm Expert": "Storm Expert",
    "Hazard Analyst": "Hazard Analyst",
    "Senior Operative": "Sr Operative",
    "Funnel CEO": "Funnel CEO",
}

MERITS = {
    "High Up": "Небо",  # max 3
    "On Fire": "Жар",  # max 3
    "Walker II": "ХодII",  # max 4
    "Walk 100km.": "100км",  # max 5
    "Historian I": "Истор",  # max 5
    "Historian III": "Истор3",  # max 6
    "Not This Time": "Не враз",
    "Scavenger I": "СборI",
    "Scavenger III": "Сбор3",
    "Big Spender I": "ТратI",
    "Big Spender III": "Траты3",
    "Protocol Nerd": "Проток",
    "The Suck Zone": "Втяжка",
    "Get caught up by a tornado while holding an umbrella.": "В торнадо с зонтом.",
    "Hit a bulls eye on the dart board in the van.": "Яблочко на дартсе.",
    "Shock your friends with the defibrillator.": None,  # odd
    "Little Treat": "Вкусн.",
    "Buy something from the vending machine for the first time.": "Первая покупка в автомате.",
    "Collect 500 items found in the city.": "Собери 500 находок в городе.",
    "Trigger all protocol information.": "Открой все протоколы.",
    "Spend 100 tokens in the vending machine.": "Потрать 100 жетонов.",
    "Spend 500 tokens in the vending machine.": "Потрать 500 жетонов.",
    "Spend 1000 tokens in the vending machine.": "Потрать 1000 жетонов.",
}

ESC_RU = (
    "Отличная инициатива! Поверните ключ фургона, чтобы завести двигатель. "
    "Если что-то сломано — увидите на панели. Если всё цело — двигатель "
    "заведётся, и можно рулить на выход. Localization: mderick.dev"
)


def ensure_assets() -> None:
    path = ROOT / "tools" / "build_ui_loc_safe.py"
    text = path.read_text(encoding="utf-8")
    if "DT_ProgressionTitles" in text:
        return
    # append before fit_utf16
    marker = "\n\n\ndef fit_utf16"
    if marker not in text:
        marker = "\n\ndef fit_utf16"
    extra = []
    for cid, (name, rel) in NEW.items():
        extra.append(f'    "{cid}": (\n        "{name}",\n        "{rel}",\n    ),')
    # insert before closing of ASSETS
    idx = text.find("}\n\n\ndef fit_utf16")
    if idx < 0:
        idx = text.find("}\n\ndef fit_utf16")
    if idx < 0:
        raise SystemExit("ASSETS end not found")
    # find last ), before }
    j = text.rfind("),", 0, idx)
    text = text[: j + 2] + "\n" + "\n".join(extra) + text[j + 2 :]
    path.write_text(text, encoding="utf-8")
    print("ASSETS+ranks")


def legacy(name: str) -> None:
    uasset_checks = {
        "DT_ProgressionTitles": EXTRACT
        / "StormEscape/Content/StormEscape/Data/Progression/DT_ProgressionTitles.uasset",
        "W_PlayerInfo": EXTRACT
        / "StormEscape/Content/StormEscape/UI/Widgets/PauseMenu/Subwidgets/W_PlayerInfo.uasset",
    }
    p = uasset_checks[name]
    if p.exists():
        return
    subprocess.check_call(
        [
            str(RETOC),
            "to-legacy",
            "--no-shaders",
            "--version",
            "UE5_5",
            "-f",
            name,
            str(PAKS),
            str(EXTRACT),
        ]
    )


def find_slot(en: str, files: list[Path]) -> dict | None:
    try:
        ansi = en.encode("ascii") + b"\x00"
    except UnicodeEncodeError:
        ansi = None
    u16 = en.encode("utf-16-le") + b"\x00\x00"
    best = None
    for p in files:
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
                        "file": p.name,
                        "enc": "ansi",
                        "even": even,
                        "max_utf16": (ln // 2) - 1 if even else None,
                        "max_ansi": ln - 1,
                    }
                    if even:
                        return info
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
                    "file": p.name,
                    "enc": "utf16",
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
    ensure_assets()
    ids = {
        **{cid: name for cid, (name, _) in NEW.items()},
        "ef3ae707dd08c5be00000001": "DT_TutorialMessages",
        "544e5eb776e67f3c00000001": "DT_Achievements",
        "b59f6ff6f0eaa61a00000001": "W_VanSchematic",
        "2819d6c35480ec5500000001": "W_Locker",
    }
    for cid, name in ids.items():
        subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(CHUNKS / f"{name}.bin")])
    for name in NEW.values():
        legacy(name[0])

    files = [CHUNKS / f"{n}.bin" for n in ids.values()]
    m = json.loads(MAP.read_text(encoding="utf-8"))

    # ESC body — trim to fit
    esc_slot = find_slot(ESC_EN, files)
    if esc_slot:
        ru = ESC_RU
        if len(ru) > esc_slot["max_utf16"]:
            ru = ru[: esc_slot["max_utf16"]]
        m[ESC_EN] = ru
        print("ESC body", len(ru), "<=", esc_slot["max_utf16"])
    else:
        print("NO ESC body")

    candidates: dict[str, str] = dict(TRAINING_TITLES)
    candidates["Training #26FRZ"] = "Холод"
    for k, v in RANKS.items():
        if any(ord(c) > 127 for c in v):
            candidates[k] = v
    for k, v in MERITS.items():
        if v:
            candidates[k] = v

    n_ok = 0
    for en, ru in candidates.items():
        slot = find_slot(en, files)
        if not slot:
            print("NOIDX", en[:50])
            continue
        if fits(slot, ru):
            m[en] = ru
            n_ok += 1
            print("OK", slot["file"], len(ru), "<=", slot.get("max_utf16") or slot["max_ansi"], en)
        else:
            print("SKIP", len(ru), "max", slot.get("max_utf16") or slot["max_ansi"], en)

    # handbook header nicer if possible — max 5
    hb = find_slot("// HANDBOOK", files)
    if hb and fits(hb, "//СПР"):
        m["// HANDBOOK"] = "//СПР"

    MAP.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("map", len(m), "ok", n_ok)
    sys.stdout.flush()
    raise SystemExit(subprocess.call([sys.executable, "-u", str(ROOT / "tools" / "build_ui_loc_safe.py")]))


if __name__ == "__main__":
    main()
