# -*- coding: utf-8 -*-
"""Batch UI loc improvements for menus, schematic labels, handbook, ranks."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Mods\FunnelRunners_RU")
MAP_PATH = ROOT / "translations" / "ui_ru_map.json"
GH_MAP = ROOT / "dist" / "github" / "translations" / "ui_ru_map.json"

# EN -> RU. build_ui_loc_safe fits UTF-16 or ASCII translit automatically.
UPDATES: dict[str, str] = {
    # --- menus / session ---
    "SESSION SETUP": "НАСТР.",
    "CREATE SESSION": "Sozdat sessiy.",
    "SESSION INFO": "Sess. info",
    "Session Info": "Sess. info",
    "FIND SESSIONS": "NAYTI",
    "SELECT UNIFORM": "FORMA",
    "MERITS": "DOSTIZ",
    "Uniforms": "Forma",
    "Merits": "Dostiz",
    "SERVICE SCHEMATIC": "СХЕМА",
    "Service Schematic": "Схема",
    "// HANDBOOK": "//СПР",
    "APEX is always watching": "APEX vsegda smotrit",
    "Remember: APEX is always watching": "APEX vsegda smotrit",
    "Session Name:": "Имя сес.",
    "Session Name": "Imya sessii",
    "NEW SESSION NAME": "NOVOE IMYA",
    "Enter a name between 3-36 characters": "Imya: 3-36 simvolov",
    "Must be 3-36 characters and can only include A-Z, _ - .": "Tolko A-Z, _ - . (3-36)",
    "Inaccessible": "Nedostupno",
    "Join Permission": "Dostup",
    "Join Permission:": "Dostup:",
    "Who can join your session": "Kto mozhet voyti",
    "Leave Session": "Vyyti",
    # --- schematic node labels ---
    "Battery": "АКБ",
    "Coolant": "ОЖ",
    "Oil": "Mas",
    "Fuses": "ПР",
    "Fuel": "Top.",
    "Tires": "Кол",
    "Handbook": "Spravka",
    "Locker": "Shkaf",
    "Vitastation": "Авто.",
    "Workbench": "Стол",
    "Storage": "СКЛ",
    "Monitors": "Ekrany",
    "Computer": "ArhivPC",
    "Mission Board": "Доска",
    # --- maintenance banner ---
    "ONLY APEX CERTIFIED PARTS CAN BE USED FOR MAINTENANCE. CONTACT AN AUTHORIZED MECHANIC FOR FIELD REPAIRS.": (
        "ТОЛЬКО ЗАПЧАСТИ APEX. РЕМОНТ В ПОЛЕ — К АВТОРИЗ. МЕХАНИКУ."
    ),
    # --- odd training titles (ASCII; odd slots cannot hold Cyrillic) ---
    "Training #00STRT": "Start",
    "Training #05CHTCHT": "Walkie",
    "Training #12PHNX": "Defib",
    "Training #13KLLY": "Zont+",
    "Training #15SNCK": "Snack",
    "Training #16BTTN": "Beg",
    "Training #19NRGY": "Energy",
    "Training #20SHRT": "Korotk",
    "Training #21STCK": "Maslo",
    "Training #23GSGSGS": "Toplivo",
    "Training #24GSRN": "Kanistra",
    "Training #25BTTL": "Butyl",
    "Training #27RBBR": "Shina",
    "Training #31CSHGRB": "Zhetony",
    "Training #32FNNL": "Voronka",
    "Training #35NCLR": "Kislota",
    "Training #36ICED": "Grad",
    "Training #37SHCK": "Tok",
    # even titles (Cyrillic ok when slot allows)
    "Training #01ESC": "Побег",
    "Training #02RDR": "Радар",
    "Training #03RAT": "Экраны",
    "Training #04BRN": "Задачи",
    "Training #06SDQ": "Склад",
    "Training #07SHP": "Магаз.",
    "Training #08BOB": "Ящик",
    "Training #09CAT": "Домкрат",
    "Training #10HLFLF": "Фонари",
    "Training #11DRK": "Темнота",
    "Training #14SCF": "Зонт",
    "Training #17SNC": "Еда",
    "Training #18MNQ": "Таблет.",
    "Training #22CLD": "ОЖ",
    "Training #26FRZ": "Холод",
    "Training #28FSS": "Предохр",
    "Training #29BTTRY": "АКБ",
    "Training #30XTR": "Лут",
    "Training #33DMG": "Урон",
    "Training #34SNG": "Дождь",
    "Training #38QTE": "QTE",
    "Training #39WBC": "Верстак",
    "Training #40WBD": "Доска",
    "Training #41LPC": "Архив",
    "Training #42LCK": "Шкаф",
    "Training #43BRD": "Рация",
    # --- handbook bodies ---
    "Pay attention to the doppler radar! It warns you about imminent tornados and storms. It can (hopefully) help you avoid them. It also tells you where other employees are and whether they are alive, or not...": (
        "Следите за доплер-радаром! Он предупреждает о торнадо и бурях и (надеемся) поможет их избежать. "
        "Также показывает, где сотрудники и живы ли они."
    ),
    "This is a consumable. Like the name suggests, it will get consumed after use. Hold [{Key0}] to use it, each one either heals you or gives different temporary benefits. ": (
        "Расходник: после использования пропадает. Удерживайте [{Key0}] — лечение или временный бафф."
    ),
    "Where your survival begins! The workbench will spawn useful tools for the match. Some are essential to fix the van, others help you navigate the map safely! Use them wisely, time is money!": (
        "Верстак выдаёт инструменты: одни чинят фургон, другие помогают на карте. Время — деньги!"
    ),
    "Information is authorized on a need-to-know basis. This company computer houses the official archives, as you evolve as an employee and complete missions, you will unlock more restricted archives.": (
        "ПК компании: официальные архивы. Чем больше миссий — тем больше секретных документов."
    ),
    "Dressing appropriately is company policy! Use the locker to change your uniform, which will alter certain aspects of your gameplay. You can also review your hard-earned official merits here. Look sharp, employee!": (
        "Шкафчик: смените форму (влияет на геймплей) и смотрите заслуги. Выглядите опрятно!"
    ),
    "We present to you the Vitastation™! A vending machine where you can spend your hard-earned (often risking your life) APEX Tokens™ to buy official APEX Products™.": (
        "Vitastation™ — автомат: тратьте APEX Tokens™ на официальные товары APEX™ (часто рискуя жизнью)."
    ),
    # --- ranks / achievements ---
    "Spend 100 tokens in the vending machine.": "Потрать 100 жетонов в автомате.",
    "Spend 500 tokens in the vending machine.": "Потрать 500 жетонов в автомате.",
    "Spend 1000 tokens in the vending machine.": "Потрать 1000 жетонов в автомате.",
    "Trigger all protocol information.": "Открой все протоколы.",
    "Collect 10 information related collectables.": "Собери 10 информационных находок.",
    "Collect 50 information related collectables.": "Собери 50 информационных находок.",
    "Collect 100 information related collectables.": "Собери 100 информационных находок.",
    "Collect 50 items found in the city.": "Собери 50 находок в городе.",
    "Collect 100 items found in the city.": "Собери 100 находок в городе.",
    "Collect 500 items found in the city.": "Собери 500 находок в городе.",
    "Big Spender I": "Траты I",
    "Big Spender II": "Траты II",
    "Big Spender III": "Траты III",
    "Protocol Nerd": "Проток",
    "The Suck Zone": "Втяжка",
    "Throw a dart into a big tornado, close enough so it doesn’t fall to the ground. “It’s the suck zone”": (
        "Брось дротик в большой торнадо так, чтобы он не упал. «Это зона всасывания»"
    ),
    # battery repair steps on schematic (long ANSI)
    "1. Disconnect the battery cables;\r\n2. Disconnect the battery using the toolbox;\r\n3. Find a new, working battery;\r\n4. Install the new battery;\r\n5. Connect the cables again using the toolbox.": (
        "1. Отсоедините кабели;\r\n2. Снимите АКБ инструментом;\r\n3. Найдите рабочий АКБ;\r\n"
        "4. Установите новый;\r\n5. Подключите кабели инструментом."
    ),
}


def main() -> int:
    m: dict[str, str] = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    changed = 0
    for k, v in UPDATES.items():
        if m.get(k) != v:
            m[k] = v
            changed += 1
    MAP_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if GH_MAP.parent.exists():
        GH_MAP.write_text(MAP_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"updated keys: {changed}, map size: {len(m)}")

    # wipe cached chunks so rebuild pulls fresh base from 0.34.28
    chunks = ROOT / "chunks_ui"
    for p in chunks.glob("*.bin"):
        if p.name.startswith("_"):
            continue
        p.unlink()

    r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_ui_loc_safe.py")])
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
