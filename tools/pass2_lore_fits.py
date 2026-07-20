# -*- coding: utf-8 -*-
"""Second pass: fit short RU for lore/loading/merits; rebuild UI pack."""
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

ASSETS = {
    "5857cf4ad72ea14c00000001": "W_LoadingScreen",
    "66fa3353083ec59a00000001": "W_LoreUI",
    "87fcfd8159ee9f6f00000001": "DA_GameplayMaps",
    "2bbbbe8a0883bb3200000001": "DT_LoreArchives",
    "3da0a5539c13767800000001": "W_ArchiveDocDisplay",
    "544e5eb776e67f3c00000001": "DT_Achievements",
    "2819d6c35480ec5500000001": "W_Locker",
    "38ad8f9c44d2301b00000001": "W_CrewLobbyInfo",
    "63e53e5b4d48dcbd00000001": "DT_LoadingScreenTips",
}


def refresh() -> None:
    for cid, name in ASSETS.items():
        subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(CHUNKS / f"{name}.bin")])


def find_slot(en: str) -> dict | None:
    """Find FString slot for exact EN text across chunks (ANSI or UTF-16)."""
    try:
        ansi = en.encode("ascii") + b"\x00"
    except UnicodeEncodeError:
        ansi = None
    u16 = en.encode("utf-16-le") + b"\x00\x00"
    best = None
    for name in ASSETS.values():
        data = (CHUNKS / f"{name}.bin").read_bytes()
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
                        "asset": name,
                        "enc": "ansi",
                        "payload": ln,
                        "even": even,
                        "max_utf16": (ln // 2) - 1 if even else None,
                    }
                    best = info if best is None else best
                    if even:
                        return info
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
                    "asset": name,
                    "enc": "utf16",
                    "payload": len(u16),
                    "even": True,
                    "max_utf16": units - 1,
                }
            start = pos + 1
    return best


EXTRA = {
    # loading
    "Keep an eye out for uncovered sewer holes": "Осторожно: люки!",
    "Tornado around? Try crouching": "Торнадо? Пригнись",
    "APEX is always watching": "APEX видит",
    "Please stand by": "Ждите…",
    "Changing tires, please stand by": "Меняем колёса…",
    "Cleaning the van, please stand by": "Моем фургон…",
    "Calibrating monitors, please stand by": "Калибруем монитор",
    "Improve your mission rating by recovering APEX property": "Localization: mderick.dev",
    # vault / maps
    "COMPANY VAULT": "АРХИВЫ",
    "Coming Soon": "Скоро",
    "Session Name:": "Имя:",
    "Testing Game mechanics and gameplay systems": "Тест механик игры",
    "Longer game time, less dangerous storms, and smaller tornadoes.": (
        "Дольше игра, слабее бури/торнадо."
    ),
    "Shorter game time, more dangerous storms, and bigger tornadoes.": (
        "Короче игра, сильнее бури/торнадо."
    ),
    "Even more dangerous storms and more frequent tornadoes.": (
        "Опаснее бури, чаще торнадо."
    ),
    # archives
    "Interview with APEX founder, Nathan Pearson": "Интервью: N. Pearson",
    "APEX's 45th Anniversary": "45 лет APEX",
    "APEX's First Contract": "Контракт 1",
    "Revisions to Municipal Protection Contracts": "Правки контрактов ГО",
    "Red Mesa Guarded From Natural Disasters": "Red Mesa под охраной",
    "Reduction of Security Personnel": "Меньше охраны",
    "Operation #094 Report": "Отчёт №094",
    "Front Line of Civil Defense": "Фронт ГО",
    "Shelter Negotiation Results": "Итоги убежищ",
    "Public Survey Results": "Опрос",
    "Weird Atmospheric Behaviour": "Странная атмосф.",
    "Guided Tour": "Тур",
    "Toxic Rains in Oakhaven": "Яд.дождь",
    "Post-1966 Operatinal Casuality Escalation": "Потери после 1966",
    # merits
    "Get caught up by a tornado while holding an umbrella.": "В торнадо с зонтом.",
    "Hit a bulls eye on the dart board in the van.": "Яблочко на дартсе.",
    "Change 4 flat tires in the van.": "Сменить 4 колеса",
    "Be revived after passing out in game.": "Ожить после отключки",
    "Fail at a repair minigame for the first time.": "Провал ремонта #1.",
    "Fail at a repair minigame 15 times.": "Провал ремонта x15",
    "Win without ever leaving the van.": "Победа из фургона",
    "Get damaged by fire for the first time.": "Первый урон от огня",
    "Get on top of the van for the first time.": "Впервые на фургон.",
    "First Escape!": "Побег!",
    "Escape the end tornado alone.": "Один от торнадо",
    "Fail to escape the city for the first time.": "Впервые не сбежать.",
    "Bulls Eye": "Ябл.",
    "Electric Friendship": "Шок-друг",
    "Designated Driver": "Водитель",
}


def ok(slot: dict, ru: str) -> bool:
    if any(ord(c) > 127 for c in ru):
        return slot.get("max_utf16") is not None and len(ru) <= slot["max_utf16"]
    if slot["enc"] == "ansi":
        return len(ru) <= slot["payload"] - 1
    return len(ru) <= slot["max_utf16"]


def main() -> None:
    refresh()
    m = json.loads(MAP.read_text(encoding="utf-8"))

    # keep suburban if present
    suburban = (
        "This American suburban town was once home to ordinary families and a quiet, "
        "predictable routine. Over time, a series of unusual events began to reshape "
        "daily life, with violent storms, recurring tornado activity, and water "
        "contamination gradually driving residents away. As the neighborhood emptied, "
        "APEX acquired the area for research purposes, citing an interest in the "
        "region’s environmental instability."
    )
    suburban_ru = (
        "Этот американский пригород когда-то был домом обычных семей с тихой, "
        "предсказуемой жизнью. Со временем необычные события изменили быт: "
        "жестокие бури, торнадо и загрязнение воды вынудили жителей уехать. "
        "Когда район опустел, APEX выкупил земли для исследований, ссылаясь на "
        "интерес к нестабильности окружающей среды."
    )
    EXTRA[suburban] = suburban_ru

    # interview body from W_ArchiveDocDisplay / DT
    slot_iv = None
    for name in ("W_ArchiveDocDisplay", "DT_LoreArchives"):
        data = (CHUNKS / f"{name}.bin").read_bytes()
        marker = "As we close in on the 6th anniversary".encode("utf-16-le")
        pos = data.find(marker)
        if pos < 4:
            continue
        ln = struct.unpack_from("<i", data, pos - 4)[0]
        if ln >= -1:
            continue
        units = -ln
        en = data[pos : pos + units * 2].decode("utf-16-le")
        if en.endswith("\x00"):
            en = en[:-1]
        body = (
            "К 6-й годовщине создания APEX мы взяли интервью у основателя — "
            "Натана Пирсона — о росте компании и о том, как ей удаётся оставаться "
            "«на шаг впереди» природы.\n\n"
            "Натан говорит о документации, дисциплине и гордости за сотрудников. "
            "APEX защищает города от аномальной погоды.\n\n"
            "Localization: mderick.dev\n"
        )
        EXTRA[en] = body[: units - 1]
        print("interview from", name, "max", units - 1)
        break

    n_ok = 0
    for en, ru in EXTRA.items():
        slot = find_slot(en)
        if not slot:
            print("NOIDX", en[:60])
            continue
        if ok(slot, ru):
            m[en] = ru
            n_ok += 1
            print("OK", slot["asset"], len(ru), "<=", slot["max_utf16"], en[:48])
        else:
            print("SKIP", len(ru), "max", slot["max_utf16"], en[:48])

    MAP.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("map", len(m), "new_ok", n_ok)
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "tools" / "build_ui_loc_safe.py")]))


if __name__ == "__main__":
    main()
