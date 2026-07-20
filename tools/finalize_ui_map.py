"""Clean truncations, add fitting RU, rebuild safe UI pack."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Mods\FunnelRunners_RU")
MAP = ROOT / "translations" / "ui_ru_map.json"

# Drop these (truncated / confusing) — keep English in-game
DROP = {
    "Bandage",  # max3: "Бин" bad
    "Acid Rain",  # max4: "Кисл" bad
}

# Extra complete fits (verified against slot sizes)
EXTRA = {
    # settings / lobby (complete words only)
    "Output Device": "Девайс",  # max6
    "Maximum Players": "Игроков",  # max7 — "Макс. игроков" doesn't fit
    "ANYONE CAN JOIN": "Открыто",  # max7
    "Join Permission": "Доступ",  # max7
    "Who can join your session": "Кто входит",  # max12
    "Bloom Quality": "Bloom",
    "CRT Effect Strength": "Сила CRT",
    "FIND SESSIONS": "НАЙТИ",
    "CREATE SESSION": "СОЗДАТЬ",
    # keep invite as EN (no good 5-char RU)
    # tips (tight)
    "Calibrating monitors, please stand by": "Калибруем монитор",  # 18
    "Watch your step! Open manholes are a hazard": "Осторожно: люки!",  # 16<=21
    "Avoid abandoned vehicles during thunderstorms": "В грозу — от машин",  # 17<=22
    "Avoid live wires, it is a shocking experience": "Не трогай провода!",  # 18<=22
    "Keep your distance from burning crewmates": "Дальше от огня",  # 14<=20
    "Do not touch electrocuted crewmates": "Не трогай под током",  # 19>17 — skip via fit check
    "Recover APEX property to maximize your rating": "Носи находки в фургон",  # 20<=22
    "Complete extra tasks to boost your rating": "Доп. задания = рейтинг",  # 22>20
    "Wait your turn on the Walkie-Talkie": "Жди очереди на рацию",  # 20>17
    # items — short complete
    "Crowbar": "Лом",  # 3
    "Granola Bar": "Снек",  # 4<=5
    "Lunaria 2D Flashlight": "Фонарь 2D",
    "Lunaria 5109LS Flashlight": "Фонарь 5109",
    "Needing that extra boost?": "Нужен заряд?",
    "A hail storm is damaging you.": "Вас бьёт град.",
    "Might not be a medkit but it will do.": "Не аптечка, но ок.",
    "Clear! Just make sure they are actually dead before you apply the pads.": (
        "Заряд! Сначала: он без сознания."
    ),  # 32<=35
    "Ideal for the darkest environments, so nobody misses any details.": (
        "Для тьмы — ничего не упустите."
    ),  # 29<=32
    "Estimated battery charge: <General>10 min</>.": "<General>Заряд 10 мин</>.",
    "Restores <Positive>20 HP</> over <General>10s</>.": "<Positive>+20 HP</>/<General>10с</>.",
    "<General>Opens locked doors and deals melee damage to players</>.": (
        "<General>Ломает двери и бьёт игроков</>."
    ),
    "<General>Revives downed teammates or knocks out conscious players</>.": (
        "<General>Режит упавших / нокаутит</>."
    ),
    "<General>Protects nearby players from rain, hail, and acid storms</>.": (
        "<General>Защита от дождя, града и кислоты</>."
    ),
    "<General>Scans the local area for weather anomalies and items</>.": (
        "<General>Скан погоды и предметов рядом</>."
    ),
    "Pocket Radar": "Радар",  # max? pay 13 odd - skip via fit
    "Better performance, worse taste.": "Сильнее, но вкус хуже.",  # odd pay 33 - skip
    "A quick snack since every second counts.": "Быстрый перекус — секунды важны.",  # odd
    "Acid rain is damaging you.": "Кислота ранит вас.",  # odd pay 27
    "A premium medkit, to save you from any situation on the field.": (
        "Аптечка для любых ситуаций на поле."
    ),
    "Welcome {Employee}! Use WASD or <Key id=\"Gamepad_Left2D\"/>  to move around, move the mouse cursor to look around and press [{Key0}] to interact. We will explain things as we go.": (
        "Привет, {Employee}! WASD/<Key id=\"Gamepad_Left2D\"/> ход, мышь взгляд, [{Key0}] действие."
    ),
    # credits (ANSI same length)
    "Rashaun James Torralba": "Mark Derick - RUS Loc.",
}


def main() -> None:
    # reuse fit filter from fix_map_and_rebuild
    sys.path.insert(0, str(ROOT / "tools"))
    import fix_map_and_rebuild as f  # type: ignore

    catalog = json.loads(f.CATALOG.read_text(encoding="utf-8"))
    idx = f.extract_index(catalog)
    # scan all chunks for index
    for p in f.CHUNKS.glob("*.bin"):
        data = p.read_bytes()
        i = 0
        n = len(data)
        while i + 4 <= n:
            import struct

            ln = struct.unpack_from("<i", data, i)[0]
            if 2 <= ln <= 800 and i + 4 + ln <= n:
                raw = data[i + 4 : i + 4 + ln]
                if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                    s = raw[:-1].decode("ascii")
                    payload = ln
                    even = payload % 2 == 0
                    maxc = (payload // 2) - 1 if even else None
                    idx.setdefault(s, []).append(
                        {"asset": p.stem, "en": s, "payload": payload, "even": even, "max_utf16": maxc}
                    )
                    i += 4 + ln
                    continue
            i += 1

    old = json.loads(MAP.read_text(encoding="utf-8"))
    new: dict[str, str] = {}

    # FORCE_EN from fix script
    force = set(f.FORCE_EN)
    # Output Device / Maximum Players we WANT to translate with good shorts — remove from force
    force.discard("Output Device")
    force.discard("Maximum Players")
    force.discard("ANYONE CAN JOIN")
    force.discard("Join Permission")
    force.discard("Who can join your session")

    for en, ru in {**old, **EXTRA}.items():
        if en in DROP or en in force:
            continue
        if ru == en:
            continue
        if en == "Rashaun James Torralba" and len(ru) == len(en):
            new[en] = ru
            continue
        if f.fits(en, ru, idx):
            new[en] = ru
        else:
            print("SKIP", len(ru), "max", (idx.get(en) or [{}])[0].get("max_utf16"), en[:50])

    # second pass tighter variants for skipped
    RETRY = {
        "Do not touch electrocuted crewmates": "Не трогай под током!",  # 19>17
        "Complete extra tasks to boost your rating": "Доп.задания=рейтинг",  # 19
        "Wait your turn on the Walkie-Talkie": "Жди очередь на рацию",  # 19>17 -> "Жди рацию" = 9
        "Estimated battery charge: <General>10 min</>.": "Заряд <General>10 мин</>.",
        "Clear! Just make sure they are actually dead before you apply the pads.": (
            "Заряд! Сначала: он без сознания."
        ),
        "Do not touch electrocuted crewmates": "Не лезь под ток",  # 15
        "Wait your turn on the Walkie-Talkie": "Жди очередь рации",  # 17
    }
    for en, ru in RETRY.items():
        if en not in new and f.fits(en, ru, idx):
            new[en] = ru
            print("RETRY OK", en[:40], "->", ru)

    MAP.write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"total map entries: {len(new)}")
    for k in (
        "Output Device",
        "Input Device",
        "INVITE ONLY",
        "ANYONE CAN JOIN",
        "Maximum Players",
        "Max. Players",
        "Bandage",
        "Crowbar",
        "Rashaun James Torralba",
    ):
        print(f"  {k}: {new.get(k, 'EN')}")

    print("\n=== rebuild safe UI pack ===")
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build_ui_loc_safe.py")],
        cwd=str(ROOT),
    )
    raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
