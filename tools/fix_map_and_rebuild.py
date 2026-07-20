"""Keep only non-truncated RU; fix lobby/settings; credits; items; rebuild safe pack."""
from __future__ import annotations

import json
import pathlib
import re
import struct
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"C:\Mods\FunnelRunners_RU")
TRANS = ROOT / "translations"
MAP = TRANS / "ui_ru_map.json"
CATALOG = TRANS / "items_credits_catalog.json"
CHUNKS = ROOT / "chunks_ui"
RETOC = r"C:\Users\Derick\Downloads\retoc_cli-x86_64-pc-windows-msvc\retoc.exe"
UTOC = (
    r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)

# Explicit keep-English (user feedback / bad truncations)
FORCE_EN = {
    "Input Device",
    "Output Device",
    "INVITE ONLY",
    "ANYONE CAN JOIN",
    "Who can join your session",
    "Maximum Players",
    "Maximum Players:",
    "Max. Players",
    "Join Permission",
    "Version 1",
    "Version 2",
    "Very High",
    "Voice Chat Volume",
    "Master Volume",
    "User Interface Volume",
    "Borderless Windowed",
    "Resolution (Fullscreen)",
    "Resolution (Borderless)",
    "Resolution (Windowed)",
    "Toggle Sprint",
    "Toggle Crouch",
    "Unit System",
    "m, km",
    "ft, mi",
}

# Only apply if FULL string fits (no truncation). Short, complete words.
SHORT_OK = {
    # settings labels that fit their even slots completely
    "Output Device": None,  # force en via FORCE_EN
    "Bloom Quality": "Bloom",
    "Texture Quality": "Текстуры",  # 8 > max 7? check - max 7 for Texture Quality -> "Текстур" bad. skip
    "Show Moodlets": "Эффекты",  # max 6
    "Show Health Bar": "Здоровье",  # 8 > 7 skip
    "CRT Effect Strength": "Сила CRT",  # 8 <= 9 ok
    "Quality Preset": "Пресет",
    # lobby - Max. Players is ODD so cannot Cyrillic; keep EN
    "SESSION SETUP": "НАСТРОЙКА",  # check fit
    "CREATE SESSION": "СОЗДАТЬ",
    "FIND SESSIONS": "НАЙТИ",
    "Apply Filters": "Применить",
    "Clear Filters": "Сбросить",
    # credits: Special Thanks slot exact ANSI length 22
    "Rashaun James Torralba": "Mark Derick - RUS Loc.",
}

# Item / moodlet RU (will be filtered by fit)
ITEMS_RU = {
    "Bandage": "Бинт",
    "Might not be a medkit but it will do.": "Не аптечка, но сойдёт.",
    "Crowbar": "Лом",
    "Clear! Just make sure they are actually dead before you apply the pads.": (
        "Заряд! Убедитесь, что напарник реально в отключке."
    ),
    "<General>Revives downed teammates or knocks out conscious players</>.": (
        "<General>Поднимает упавших или нокаутит живых</>."
    ),
    "Needing that extra boost?": "Нужен доп. заряд?",
    "Better performance, worse taste.": "Сильнее эффект, хуже вкус.",
    "Lunaria 5109LS Flashlight": "Фонарь Lunaria 5109LS",
    "Ideal for the darkest environments, so nobody misses any details.": (
        "Для самой тёмной местности — детали не пропустите."
    ),
    "Estimated battery charge: <General>10 min</>.": "Заряд батареи: <General>10 мин</>.",
    "Lunaria 2D Flashlight": "Фонарь Lunaria 2D",
    "Estimated battery charge: <General>5 min</>.": "Заряд батареи: <General>5 мин</>.",
    "Granola Bar": "Батончик",
    "A quick snack since every second counts.": "Быстрый перекус — секунды на счету.",
    "A hail storm is damaging you.": "Град наносит вам урон.",
    "Acid Rain": "Кислота",
    "Acid rain is damaging you.": "Кислотный дождь ранит вас.",
    "Health Pills": "Таблетки",
    "Medkit": "Аптечка",
    "A premium medkit, to save you from any situation on the field.": (
        "Аптечка на поле — спасёт в тяжёлой ситуации."
    ),
    "Portable Conductor": "Проводник",
    "Portable Doppler": "Доплер",
    "Umbrella": "Зонт",
    "Energy Drink": "Энергетик",
    "Energy Pills": "Таблетки+",
    "Hail Storm": "Град",
    "LIFESAVE Defibrillator": "Дефибриллятор",
    "<General>Opens locked doors and deals melee damage to players</>.": (
        "<General>Открывает двери и бьёт игроков в ближнем бою</>."
    ),
    "Restores <Positive>30 HP</> instantly.": "Мгновенно <Positive>+30 HP</>.",
    "Restores <Positive>60 HP</> instantly.": "Мгновенно <Positive>+60 HP</>.",
    "Restores <Positive>20 HP</> over <General>10s</>.": (
        "<Positive>+20 HP</> за <General>10с</>."
    ),
    "Increases <Bold>movement speed</> by <Positive>36%</> for <General>2 min</>.": (
        "<Bold>Скорость</> <Positive>+36%</> на <General>2 мин</>."
    ),
    "Increases <Bold>stamina</> by <Positive>30%</> for <General>2 min</>.": (
        "<Bold>Выносливость</> <Positive>+30%</> на <General>2 мин</>."
    ),
    "Increases <Bold>stamina recovery</> by <Positive>150%</> for <General>2 min</>.": (
        "<Bold>Восст. выносливости</> <Positive>+150%</> / <General>2 мин</>."
    ),
}


def extract_index(catalog: dict) -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = {}
    for asset, rows in catalog.items():
        for r in rows:
            idx.setdefault(r["en"], []).append({"asset": asset, **r})
    return idx


def fits(en: str, ru: str, idx: dict) -> bool:
    if en not in idx:
        return False
    for r in idx[en]:
        if any(ord(c) > 127 for c in ru):
            if not r["even"]:
                return False
            if len(ru) > r["max_utf16"]:
                return False
        else:
            # ascii must fit ansi payload
            if len(ru) > r["payload"] - 1:
                return False
    return True


def main() -> None:
    old = json.loads(MAP.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    idx = extract_index(catalog)

    # also need Settings/menu slots from existing chunks for filter
    for name in (
        "SettingsData",
        "W_MainMenu",
        "W_PauseMenu",
        "W_CreateRoomPopup",
        "W_SearchLobbies_New",
        "W_CrewLobbyInfo",
        "DT_LoadingScreenTips",
        "DT_TutorialMessages",
        "W_ContentWarnings",
        "W_TermsAndConditions",
        "W_SessionNameField",
        "W_CrewAssembly_New",
    ):
        p = CHUNKS / f"{name}.bin"
        if not p.exists():
            continue
        # merge into idx from raw extract
        data = p.read_bytes()
        i = 0
        n = len(data)
        while i + 4 <= n:
            ln = struct.unpack_from("<i", data, i)[0]
            if 2 <= ln <= 800 and i + 4 + ln <= n:
                raw = data[i + 4 : i + 4 + ln]
                if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                    s = raw[:-1].decode("ascii")
                    payload = ln
                    even = payload % 2 == 0
                    maxc = (payload // 2) - 1 if even else None
                    idx.setdefault(s, []).append(
                        {"asset": name, "en": s, "payload": payload, "even": even, "max_utf16": maxc}
                    )
                    i += 4 + ln
                    continue
            i += 1

    new_map: dict[str, str] = {}
    kept = dropped = 0
    for en, ru in old.items():
        if en in FORCE_EN:
            dropped += 1
            continue
        if ru == en:
            continue
        if fits(en, ru, idx):
            new_map[en] = ru
            kept += 1
        else:
            dropped += 1

    # apply short_ok / items
    for en, ru in {**SHORT_OK, **ITEMS_RU}.items():
        if ru is None or en in FORCE_EN:
            continue
        if fits(en, ru, idx):
            new_map[en] = ru
        elif en == "Rashaun James Torralba" and ru == "Mark Derick - RUS Loc.":
            # force credits via exact ansi length match
            if en in idx and len(ru) == len(en):
                new_map[en] = ru
                print("CREDITS OK:", ru)

    MAP.write_text(json.dumps(new_map, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"map kept={kept} dropped_trunc_or_forced={dropped} total={len(new_map)}")
    print("credits entry:", new_map.get("Rashaun James Torralba"))
    print("Max. Players:", new_map.get("Max. Players", "EN"))
    print("Output Device:", new_map.get("Output Device", "EN"))
    print("INVITE ONLY:", new_map.get("INVITE ONLY", "EN"))


if __name__ == "__main__":
    main()
