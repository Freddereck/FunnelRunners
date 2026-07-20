# -*- coding: utf-8 -*-
"""Fix mislabeled Training titles + translate handbook bodies (walkie/crowbar/etc)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Mods\FunnelRunners_RU")
MAP_PATH = ROOT / "translations" / "ui_ru_map.json"
GH_MAP = ROOT / "dist" / "github" / "translations" / "ui_ru_map.json"

# Correct titles from real title→body pairs in DT_TutorialMessages (0.34.28).
# Odd ANSI titles → ASCII translit (Cyrillic impossible).
UPDATES: dict[str, str] = {
    # titles
    "Training #05CHTCHT": "Raciya",  # walkie → рация (odd slot)
    "Training #08BOB": "Instrument",  # toolbox, not "Ящик"
    "Training #10HLFLF": "Lom",  # crowbar (was wrongly Фонари)
    "Training #11DRK": "Фонари",  # flashlights
    "Training #14SCF": "Provodnik",  # portable conductors (was wrongly Зонт)
    "Training #13KLLY": "Zont",  # umbrellas
    "Training #17SNC": "Beg",  # running (was wrongly Еда)
    "Training #18MNQ": "Dvigatel",  # engine (was wrongly Таблет.)
    # bodies
    "The monitors let you see what other employees are doing, and help you work better as a team (if you see anyone slacking off please report it).": (
        "Мониторы показывают, что делают другие. Работайте командой (лентяев — в рапорт)."
    ),
    "Communication is key. To use the walkie-talkie press [{Key0}] to turn it on and off and [{Key1}] to talk to your teammates. Please limit conversation to work-related topics, such as your survival.": (
        "Связь важна. Рация: [{Key0}] вкл/выкл, [{Key1}] говорить. Только рабочие темы — выживание."
    ),
    "This is the storage box. You have to bring all collectables you find here, newspapers, VHS tapes, files, and the like, otherwise you will not get any rewards out of them, company policy.": (
        "Ящик склада: несите сюда газеты, VHS, файлы — иначе наград не будет. Политика компании."
    ),
    "Crowbars can help you open barricaded doors. Don’t worry about breaking and entering charges, these houses are going to be broken soon anyway. To use it, go towards any barricaded door and press [{Key0}].": (
        "Лом открывает забаррикадированные двери. К двери и [{Key0}]. Дома всё равно скоро разнесут."
    ),
    "Flashlights can help you illuminate dark places. Press [{Key0}] to turn them on and off. Don’t leave them on unnecessarily, their batteries run out!.": (
        "Фонари освещают темноту. [{Key0}] вкл/выкл. Не держите всегда включёнными — садится батарея."
    ),
    "Portable conductors will protect you from lightning. No need to do anything special, just hold them out and you’ll be fine (probably).": (
        "Переносные проводники защищают от молний. Просто держите их — и (наверное) всё будет хорошо."
    ),
}


def main() -> int:
    m: dict[str, str] = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    # remove wrong old title meanings by overwrite
    for k, v in UPDATES.items():
        m[k] = v
    # keep even titles that were correct
    m.setdefault("Training #03RAT", "Экраны")
    m.setdefault("Training #06SDQ", "Склад")
    m.setdefault("Training #07SHP", "Магаз.")

    MAP_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if GH_MAP.parent.exists():
        GH_MAP.write_text(MAP_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    print("map keys", len(m))

    for name in ("DT_TutorialMessages.bin",):
        p = ROOT / "chunks_ui" / name
        if p.exists():
            p.unlink()

    return subprocess.call([sys.executable, str(ROOT / "tools" / "build_ui_loc_safe.py")])


if __name__ == "__main__":
    raise SystemExit(main())
