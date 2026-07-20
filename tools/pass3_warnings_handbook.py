# -*- coding: utf-8 -*-
"""Content warnings + handbook/merits + APEX certified banner; rebuild UI pack."""
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

NEW_ASSETS = {
    "b59f6ff6f0eaa61a00000001": (
        "W_VanSchematic",
        "StormEscape/UI/Widgets/VanSchematic/W_VanSchematic",
    ),
    "3bcc87409dfe7bcb00000001": (
        "DT_SchematicInfo",
        "StormEscape/UI/Widgets/VanSchematic/Data/DT_SchematicInfo",
    ),
}

# All even-slot candidates (will be fit-checked)
WARN_EN = (
    "This game contains flashing lights that may trigger photosensitive epilepsy.\r\n\r\n"
    "This game depicts natural disasters and their aftermath, which some players may find distressing."
)
CERT_EN = (
    "ONLY APEX CERTIFIED PARTS CAN BE USED FOR MAINTENANCE. "
    "CONTACT AN AUTHORIZED MECHANIC FOR FIELD REPAIRS."
)

CANDIDATES: dict[str, str] = {
    # Content warning + credit (first screenshot)
    WARN_EN: (
        "В игре есть мигающие эффекты — риск для людей с фотосенситивной эпилепсией.\r\n\r\n"
        "Показаны стихийные бедствия и их последствия — это может быть тяжело.\r\n\r\n"
        "Localization: mderick.dev"
    ),
    # Handbook banner
    CERT_EN: (
        "ТОЛЬКО СЕРТИФИЦИРОВАННЫЕ ЗАПЧАСТИ APEX. "
        "ДЛЯ РЕМОНТА В ПОЛЕ — К АВТОРИЗОВАННОМУ МЕХАНИКУ. | mderick.dev"
    ),
    "// HANDBOOK": "// СПРАВОЧНИК",
    "HANDBOOK": "СПРАВОЧНИК",
    # Merits remaining (titles + descs)
    "Shock your friends with the defibrillator.": "Шокируй друзей дефибриллятором.",
    "Avoid lightning damage by holding the portable conductor when hit.": (
        "Держи громоотвод при ударе молнии."
    ),
    "Change 4 flat tires in the van.": "Сменить 4 колеса",
    "Be revived after passing out in game.": "Ожить после отключки",
    "Benjamin, Who?": "Бенджамин?",
    "Tire-d": "Шины",
    "Dead? Me?": "Умер?",
    "First Day Fail": "Провал дня",
    "Worst Mechanic": "Худший мех.",
    "Fail at a repair minigame 15 times.": "Провал ремонта x15",
    "First Day Star": "Звезда дня",
    "Succeed at a repair minigame for the first time.": "Успех ремонта впервые.",
    "Energy Drunk": "Энергошок",
    "Drink 5 energy drinks in a minute.": "5 энергетиков за минуту.",
    "Win without ever leaving the van.": "Победа из фургона",
    "High Up": "Высоко",
    "Get caught up by a tornado for the first time.": "Впервые попасть в торнадо.",
    "On Fire": "В огне",
    "Electrified": "Под током",
    "Get hit by lightning for the first time.": "Впервые удар молнии.",
    "Porcupine": "Дикобраз",
    "Have 10 darts on you at the same time.": "10 дротиков на себе сразу.",
    "Up Here!": "Наверх!",
    "Escape the end tornado for the first time.": "Впервые уйти от торнадо.",
    "Lone Wolf": "Одиночка",
    "Escape the end tornado alone.": "Один от торнадо",
    "Walker I": "Ходок I",
    "Walk 10km.": "Пройти 10км.",
    "UNIFORMS": "ФОРМА",
    "MERITS": "ЗАСЛУГИ",
    "SELECT UNIFORM": "ВЫБОР ФОРМЫ",
    # Handbook / tutorial bodies (EVEN slots only will apply)
    "Welcome {Employee}! Use WASD or <Key id=\"Gamepad_Left2D\"/>  to move around, move the mouse cursor to look around and press [{Key0}] to interact. We will explain things as we go.": (
        "Привет, {Employee}! WASD/<Key id=\"Gamepad_Left2D\"/> — ход, мышь — взгляд, [{Key0}] — действие. Дальше объясним по ходу."
    ),
    "Up to for doing some extra hours? No? Too bad, they are mandatory. The mission board lists secondary objectives other than escaping. Completing them will grant extra rewards (and help you keep your job).": (
        "Сверхурочные обязательны. На доске заданий — побочные цели и награды (и шанс сохранить работу)."
    ),
    "Can we fix it? Probably, you better hope so. Toolboxes can be used to remove both broken tires and batteries on the van. To use it, press [{Key0}] while highlighting them.": (
        "Инструменты снимают колёса и АКБ. Наведите и жмите [{Key0}]."
    ),
    "Scissor Jacks can be used to lift up the van and change broken tires. To use it, press [{Key0}] while highlighting a flat tire.": (
        "Домкрат поднимает фургон. На спущенное колесо — [{Key0}]."
    ),
    "Umbrellas protect you and other nearby employees from getting wet by rain, and damaged by hail or acid rain when held. Just make sure to put it away if there is a lightning storm.": (
        "Зонт от дождя, града и кислоты. Уберите при грозе с молниями."
    ),
    "This is the coolant reservoir. Press and hold [{Key0}] to open and close it, and [{Key1}] to fill it up when you have a coolant bottle.": (
        "Бачок ОЖ: [{Key0}] открыть/закрыть, [{Key1}] залить из канистры."
    ),
    "This is the fuel tank. Press and hold [{Key0}] to open and close it, and [{Key1}] to fill it up when you have a fuel can.": (
        "Бак: [{Key0}] открыть/закрыть, [{Key1}] залить из канистры."
    ),
    "This is an oil bottle, you should bring it to the oil reservoir on the front of the van and press [{Key0}] to fill it up.": (
        "Масло — к бачку спереди фургона, затем [{Key0}]."
    ),
    "This is a new tire, you can replace any broken tire on the van with this one. First you need a scissors jack to lift up the van and a toolbox to remove the old tire. Once you do that, just press [{Key0}] to install the new one.": (
        "Новое колесо: домкрат + инструмент снять старое, затем [{Key0}] поставить."
    ),
    "These are new fuses, you can replace any blown out fuses that where removed by pressing [{Key0}].": (
        "Новые предохранители: ставьте на место через [{Key0}]."
    ),
    "This is a new battery, you can replace a broken battery that was removed with a toolbox by pressing [{Key0}].": (
        "Новый АКБ: после снятия старого инструментом жмите [{Key0}]."
    ),
    "A collectable! Take it back to the collectables box on the van and you will get a bonus for your trouble (only if you survive, otherwise it will NOT go to your next of kin).": (
        "Находка! Несите в ящик фургона — бонус, если выживете."
    ),
    "Acid rain will damage you constantly while you are not under a roof. Should you get an umbrella, please be a team player and share it with other employees.": (
        "Кислота ранит без крыши. Зонт лучше делить с командой."
    ),
    "Pay attention employee, certain dangerous actions will require you to be very precise. You must press [{Key0}] when the indicator is on the green area to successfully perform the action. If you fail, you might take damage. Some interactions will require multiple presses to be completed.": (
        "Опасно: жмите [{Key0}] в зелёной зоне. Промах — урон. Иногда нужно несколько нажатий."
    ),
    "Communication is key to teamwork! This whiteboard is great tool for that, write on it and coordinate survival plans. Keep all drawings and messages strictly professional and work-related.": (
        "Доска для планов команды. Пишите по делу — только работа."
    ),
    "Welcome to the APEX internal broadcast system! Grab the radio microphone and press [{Key0}] to transmit your voice to your teammates.": (
        "Рация APEX: микрофон + [{Key0}] — говорить команде."
    ),
    # Odd-payload handbook: ASCII-only short EN replacements are useless;
    # try Latin translit? Skip — keep EN. Exception: if we find even copy elsewhere.
}


def ensure_assets() -> None:
    path = ROOT / "tools" / "build_ui_loc_safe.py"
    text = path.read_text(encoding="utf-8")
    if "W_VanSchematic" in text:
        return
    marker = '    "2819d6c35480ec5500000001": (\n        "W_Locker",\n        "StormEscape/UI/Widgets/Locker/W_Locker",\n    ),\n}'
    extra = []
    for cid, (name, rel) in NEW_ASSETS.items():
        extra.append(f'    "{cid}": (\n        "{name}",\n        "{rel}",\n    ),')
    if marker not in text:
        # try append before last ASSETS closing
        idx = text.find("}\n\n\ndef fit_utf16")
        if idx < 0:
            raise SystemExit("cannot patch ASSETS")
        insert = ",\n" + "\n".join(extra) + "\n"
        # find last ), before }
        j = text.rfind("),", 0, idx)
        text = text[: j + 2] + "\n" + "\n".join(extra) + text[j + 2 :]
        path.write_text(text, encoding="utf-8")
    else:
        path.write_text(text.replace(marker, marker[:-2] + "\n" + "\n".join(extra) + "\n}"), encoding="utf-8")
    print("ASSETS updated")


def legacy_extract(names: list[str]) -> None:
    for name in names:
        base_rel = None
        for _cid, (n, rel) in {**NEW_ASSETS}.items():
            if n == name:
                base_rel = rel
        # also known
        known = {
            "W_ContentWarnings": "StormEscape/UI/Widgets/ContentWarning/W_ContentWarnings",
            "DT_TutorialMessages": "StormEscape/Data/Tutorial/DT_TutorialMessages",
            "DT_Achievements": "StormEscape/Data/Achievements/DT_Achievements",
            "W_Locker": "StormEscape/UI/Widgets/Locker/W_Locker",
        }
        rel = base_rel or known.get(name)
        if not rel:
            continue
        uasset = EXTRACT / "StormEscape" / "Content" / Path(rel + ".uasset")
        if uasset.exists():
            continue
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
                        "file": p.name,
                        "enc": "ansi",
                        "payload": ln,
                        "even": even,
                        "max_utf16": (ln // 2) - 1 if even else None,
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
                    "payload": len(u16),
                    "even": True,
                    "max_utf16": units - 1,
                }
            start = pos + 1
    return best


def fits(slot: dict, ru: str) -> bool:
    if any(ord(c) > 127 for c in ru):
        return slot.get("max_utf16") is not None and len(ru) <= slot["max_utf16"]
    if slot["enc"] == "ansi":
        return len(ru) <= slot["payload"] - 1
    return len(ru) <= slot["max_utf16"]


def main() -> None:
    ensure_assets()
    # refresh chunks
    ids = {
        "f8406abace5b783400000001": "W_ContentWarnings",
        "ef3ae707dd08c5be00000001": "DT_TutorialMessages",
        "544e5eb776e67f3c00000001": "DT_Achievements",
        "2819d6c35480ec5500000001": "W_Locker",
        **{cid: name for cid, (name, _) in NEW_ASSETS.items()},
    }
    for cid, name in ids.items():
        subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(CHUNKS / f"{name}.bin")])
    legacy_extract(list(ids.values()))

    files = [CHUNKS / f"{n}.bin" for n in ids.values()]
    m = json.loads(MAP.read_text(encoding="utf-8"))

    # shorten WARN/CERT to fit if needed
    variants = {
        WARN_EN: [
            CANDIDATES[WARN_EN],
            (
                "Мигающие эффекты — риск фотосенситивной эпилепсии.\r\n\r\n"
                "Стихийные бедствия и последствия — может быть тяжело.\r\n\r\n"
                "mderick.dev"
            ),
            (
                "Мигающий свет: риск эпилепсии.\r\n\r\n"
                "Стихийные бедствия — может быть тяжело.\r\n\r\n"
                "Localization: mderick.dev"
            ),
        ],
        CERT_EN: [
            CANDIDATES[CERT_EN],
            "ТОЛЬКО ЗАПЧАСТИ APEX. РЕМОНТ В ПОЛЕ — К МЕХАНИКУ. mderick.dev",
            "ТОЛЬКО ЗАПЧАСТИ APEX. К АВТОРИЗ. МЕХАНИКУ. mderick.dev",
        ],
    }

    n_ok = 0
    for en, ru in CANDIDATES.items():
        slot = find_slot(en, files)
        if not slot:
            print("NOIDX", en[:70])
            continue
        cands = variants.get(en, [ru])
        chosen = None
        for c in cands:
            if fits(slot, c):
                chosen = c
                break
        if chosen is None:
            print("SKIP", len(ru), "max", slot["max_utf16"], "even", slot.get("even"), en[:50])
            continue
        m[en] = chosen
        n_ok += 1
        print("OK", slot["file"], len(chosen), "<=", slot["max_utf16"], en[:48])

    MAP.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("map", len(m), "pass_ok", n_ok)
    # flush prints then rebuild
    sys.stdout.flush()
    raise SystemExit(subprocess.call([sys.executable, "-u", str(ROOT / "tools" / "build_ui_loc_safe.py")]))


if __name__ == "__main__":
    main()
