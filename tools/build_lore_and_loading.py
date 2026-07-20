# -*- coding: utf-8 -*-
"""Patch loading quotes, session info, vault, archives, merits (same-size safe)."""
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

# Extra assets for this pass (merged into build_ui_loc_safe ASSETS)
NEW_ASSETS: dict[str, tuple[str, str]] = {
    "5857cf4ad72ea14c00000001": (
        "W_LoadingScreen",
        "StormEscape/UI/Widgets/LoadingScreen/W_LoadingScreen",
    ),
    "66fa3353083ec59a00000001": (
        "W_LoreUI",
        "StormEscape/UI/Widgets/LoreUI/W_LoreUI",
    ),
    "87fcfd8159ee9f6f00000001": (
        "DA_GameplayMaps",
        "StormEscape/Data/ProjectSettings/DA_GameplayMaps",
    ),
    "2bbbbe8a0883bb3200000001": (
        "DT_LoreArchives",
        "StormEscape/Data/Lore/DT_LoreArchives",
    ),
    "3da0a5539c13767800000001": (
        "W_ArchiveDocDisplay",
        "StormEscape/UI/Widgets/LoreUI/W_ArchiveDocDisplay",
    ),
    "544e5eb776e67f3c00000001": (
        "DT_Achievements",
        "StormEscape/Data/Achievements/DT_Achievements",
    ),
    "2819d6c35480ec5500000001": (
        "W_Locker",
        "StormEscape/UI/Widgets/Locker/W_Locker",
    ),
}

SUBURBAN_EN = (
    "This American suburban town was once home to ordinary families and a quiet, "
    "predictable routine. Over time, a series of unusual events began to reshape "
    "daily life, with violent storms, recurring tornado activity, and water "
    "contamination gradually driving residents away. As the neighborhood emptied, "
    "APEX acquired the area for research purposes, citing an interest in the "
    "region’s environmental instability."
)

# Candidate RU (will be fit-filtered). Prefer complete words.
CANDIDATES: dict[str, str] = {
    # --- Loading screen (actual startup quotes) ---
    "Please stand by": "Ждите…",
    "Changing tires, please stand by": "Меняем колёса…",
    "Cleaning the van, please stand by": "Моем фургон…",
    "Calibrating monitors, please stand by": "Калибруем монитор",
    "Keep an eye out for uncovered sewer holes": "Осторожно: открытые люки",
    "Tornado around? Try crouching": "Торнадо? Пригнись",
    "APEX is always watching": "APEX всё видит",
    # credit on a tip slot (max 27)
    "Improve your mission rating by recovering APEX property": "Localization: mderick.dev",
    # --- Company Vault ---
    "COMPANY VAULT": "АРХИВЫ",
    "Coming Soon": "Скоро",
    "Session Name:": "Сессия:",
    "Difficulty:": "Сложн:",
    # --- Session info ---
    SUBURBAN_EN: (
        "Этот американский пригород когда-то был домом обычных семей с тихой, "
        "предсказуемой жизнью. Со временем необычные события изменили быт: "
        "жестокие бури, торнадо и загрязнение воды вынудили жителей уехать. "
        "Когда район опустел, APEX выкупил земли для исследований, ссылаясь на "
        "интерес к нестабильности окружающей среды."
    ),
    "Testing Game mechanics and gameplay systems": "Тест механик и геймплея",
    # difficulty blurbs in lobby
    "Longer game time, less dangerous storms, and smaller tornadoes.": (
        "Дольше игра, слабее бури и меньше торнадо."
    ),
    "Shorter game time, more dangerous storms, and bigger tornadoes.": (
        "Короче игра, опаснее бури и крупнее торнадо."
    ),
    "Even more dangerous storms and more frequent tornadoes.": (
        "Ещё опаснее бури и чаще торнадо."
    ),
    # --- Archive titles ---
    "Interview with APEX founder, Nathan Pearson": "Интервью: N. Pearson",
    "APEX's 45th Anniversary": "45 лет APEX",
    "APEX's First Contract": "1й контракт",
    "Revisions to Municipal Protection Contracts": "Правки гор. контрактов",
    "Red Mesa Guarded From Natural Disasters": "Red Mesa под охраной",
    "Reduction of Security Personnel": "Сокращение охраны",
    "Operation #094 Report": "Отчёт №094",
    "Front Line of Civil Defense": "Фронт ГО",
    "Shelter Negotiation Results": "Итоги по убежищам",
    "Public Survey Results": "Опрос людей",
    "Weird Atmospheric Behaviour": "Странная атмосфера",
    "Guided Tour": "Тур",
    "Toxic Rains in Oakhaven": "Токсичный дождь",
    "Post-1966 Operatinal Casuality Escalation": "Рост потерь после 1966",
    # --- Merits (descriptions that fit) ---
    "Get caught up by a tornado while holding an umbrella.": "В торнадо с зонтом в руках.",
    "Hit a bulls eye on the dart board in the van.": "Попасть в яблочко на дартсе.",
    "Change 4 flat tires in the van.": "Сменить 4 спущенных колеса.",
    "Be revived after passing out in game.": "Ожить после потери сознания.",
    "Fail at a repair minigame for the first time.": "Провалить ремонт впервые.",
    "Fail at a repair minigame 15 times.": "Провалить ремонт 15 раз.",
    "Win without ever leaving the van.": "Победа, не выходя из фургона.",
    "Get damaged by fire for the first time.": "Впервые получить урон от огня.",
    "Get on top of the van for the first time.": "Впервые залезть на фургон.",
    "First Escape!": "Побег!",
    "Escape the end tornado alone.": "Уйти от торнадо в одиночку.",
    "Fail to escape the city for the first time.": "Впервые не сбежать из города.",
    "Bulls Eye": "В яб.",
    "Electric Friendship": "Шок-друг",
    "Designated Driver": "Водитель",
    "Dead? Me?": "Я? Умер?",
    # names with tiny slots stay EN (Mary Poppins odd, Tire-d odd, etc.)
}


def index_chunks(names: list[str]) -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = {}
    for name in names:
        p = CHUNKS / f"{name}.bin"
        if not p.exists():
            continue
        data = p.read_bytes()
        i = 0
        n = len(data)
        while i + 4 <= n:
            ln = struct.unpack_from("<i", data, i)[0]
            if 2 <= ln <= 5000 and i + 4 + ln <= n:
                raw = data[i + 4 : i + 4 + ln]
                if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                    s = raw[:-1].decode("ascii")
                    even = ln % 2 == 0
                    idx.setdefault(s, []).append(
                        {
                            "asset": name,
                            "enc": "ansi",
                            "payload": ln,
                            "even": even,
                            "max_utf16": (ln // 2) - 1 if even else None,
                        }
                    )
                    i += 4 + ln
                    continue
            if -5000 <= ln <= -2:
                nbytes = (-ln) * 2
                if i + 4 + nbytes <= n:
                    try:
                        s = data[i + 4 : i + 4 + nbytes].decode("utf-16-le")
                        if s.endswith("\x00"):
                            s = s[:-1]
                        if len(s) >= 2:
                            idx.setdefault(s, []).append(
                                {
                                    "asset": name,
                                    "enc": "utf16",
                                    "payload": nbytes,
                                    "even": True,
                                    "max_utf16": len(s),
                                }
                            )
                            i += 4 + nbytes
                            continue
                    except Exception:
                        pass
            i += 1
    return idx


def fits(en: str, ru: str, rows: list[dict]) -> bool:
    for r in rows:
        maxc = r["max_utf16"]
        if any(ord(c) > 127 for c in ru):
            if maxc is None:
                return False
            if len(ru) > maxc:
                return False
        else:
            # ascii into ansi slot
            if r["enc"] == "ansi":
                if len(ru) > r["payload"] - 1:
                    return False
            else:
                if maxc is None or len(ru) > maxc:
                    return False
    return True


def ensure_new_chunks() -> None:
    CHUNKS.mkdir(parents=True, exist_ok=True)
    for cid, (name, _) in NEW_ASSETS.items():
        dest = CHUNKS / f"{name}.bin"
        subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(dest)])


def patch_build_ui_assets() -> None:
    """Inject NEW_ASSETS into build_ui_loc_safe.ASSETS if missing."""
    path = ROOT / "tools" / "build_ui_loc_safe.py"
    text = path.read_text(encoding="utf-8")
    if "W_LoadingScreen" in text and "DT_LoreArchives" in text:
        return
    # rewrite ASSETS block end before closing brace of ASSETS
    marker = "    \"568edd91377a697b00000001\": (\n        \"DA_Hail\",\n        \"StormEscape/Data/Moodlets/DA_Hail\",\n    ),\n}"
    extra_lines = []
    for cid, (name, rel) in NEW_ASSETS.items():
        extra_lines.append(f'    "{cid}": (\n        "{name}",\n        "{rel}",\n    ),')
    extra = "\n".join(extra_lines)
    repl = (
        "    \"568edd91377a697b00000001\": (\n"
        "        \"DA_Hail\",\n"
        "        \"StormEscape/Data/Moodlets/DA_Hail\",\n"
        "    ),\n"
        f"{extra}\n"
        "}"
    )
    if marker not in text:
        raise SystemExit("ASSETS marker not found in build_ui_loc_safe.py")
    path.write_text(text.replace(marker, repl), encoding="utf-8")
    print("updated build_ui_loc_safe ASSETS")


def main() -> None:
    ensure_new_chunks()
    patch_build_ui_assets()

    names = [
        "W_LoadingScreen",
        "W_LoreUI",
        "DA_GameplayMaps",
        "W_CrewLobbyInfo",
        "DT_LoreArchives",
        "W_ArchiveDocDisplay",
        "DT_Achievements",
        "W_Locker",
        "DT_LoadingScreenTips",
        "SettingsData",
        "W_CreateRoomPopup",
        "W_SearchLobbies_New",
    ]
    idx = index_chunks(names)

    # interview body: take EN from index, build padded RU summary
    interview_en = None
    for key in idx:
        if key.startswith("As we close in on the 6th anniversary"):
            interview_en = key
            break
    if interview_en:
        maxc = idx[interview_en][0]["max_utf16"]
        body_ru = (
            "К 6-й годовщине создания APEX мы решили взять интервью у основателя "
            "корпорации — Натана Пирсона — о росте компании и о том, как ей удаётся "
            "оставаться «на шаг впереди» природы.\n\n"
            "Натан говорит о документации, дисциплине и гордости за сотрудников. "
            "Он напоминает: APEX строит защиту городов от аномальной погоды и "
            "ценится за прогнозирование и готовность.\n\n"
            "Полный английский текст сжат здесь из‑за лимита слота локализации. "
            "Localization: mderick.dev\n\n"
        )
        if len(body_ru) > maxc:
            body_ru = body_ru[:maxc]
        CANDIDATES[interview_en] = body_ru
        print(f"interview body max={maxc} ru_len={len(body_ru)}")

    old = json.loads(MAP.read_text(encoding="utf-8"))
    merged = dict(old)
    ok = skip = 0
    for en, ru in CANDIDATES.items():
        rows = idx.get(en)
        if not rows:
            print("NOIDX", en[:70])
            skip += 1
            continue
        if fits(en, ru, rows):
            merged[en] = ru
            ok += 1
            assets = sorted({r["asset"] for r in rows})
            print("OK", assets, len(ru), "<=", rows[0]["max_utf16"], en[:50])
        else:
            print(
                "SKIP",
                len(ru),
                "max",
                rows[0]["max_utf16"],
                "even",
                rows[0].get("even"),
                en[:50],
            )
            skip += 1

    MAP.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"map total={len(merged)} added_ok={ok} skipped={skip}")

    extract_ui = ROOT / "extract_ui"
    missing_legacy = []
    for _cid, (_name, rel) in NEW_ASSETS.items():
        base = extract_ui / "StormEscape" / "Content" / Path(rel)
        if not Path(str(base) + ".uasset").exists():
            missing_legacy.append((_name, rel))
    if missing_legacy:
        paks = GAME_UTOC.parent
        for name, _rel in missing_legacy:
            print("to-legacy", name)
            subprocess.check_call(
                [
                    str(RETOC),
                    "to-legacy",
                    "--no-shaders",
                    "--version",
                    "UE5_5",
                    "-f",
                    name,
                    str(paks),
                    str(extract_ui),
                ]
            )

    r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_ui_loc_safe.py")])
    raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
