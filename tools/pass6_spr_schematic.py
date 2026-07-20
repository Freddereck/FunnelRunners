# -*- coding: utf-8 -*-
"""Translate remaining SPR titles (incl. odd via ASCII short), SERVICE SCHEMATIC,
and odd bodies where UTF-16 copies exist. Experiment: CP1251 in odd ANSI slots."""
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

# Odd titles → short labels (ASCII if odd can't hold Cyrillic; Cyrillic if even)
# For ODD we try CP1251 encoding into ANSI payload (same byte size).
ODD_TITLES_RU = {
    "Training #00STRT": "Старт",
    "Training #05CHTCHT": "Рация",
    "Training #12PHNX": "Дефиб",
    "Training #13KLLY": "Зонт+",
    "Training #15SNCK": "Снек",
    "Training #16BTTN": "Кнопки",
    "Training #19NRGY": "АКБ?",  # battery text shown for 19 - wait screenshot says battery for 19NRGY
    "Training #20SHRT": "Коротк",
    "Training #21STCK": "Масло",
    "Training #23GSGSGS": "Топливо",
    "Training #24GSRN": "Канистра",
    "Training #25BTTL": "Бутыль",
    "Training #27RBBR": "Шина",
    "Training #31CSHGRB": "Жетоны",
    "Training #32FNNL": "Воронка",
    "Training #35NCLR": "Кислота",
    "Training #36ICED": "Град",
    "Training #37SHCK": "Ток",
}

# Even titles already mostly done; fill gaps
EVEN_TITLES = {
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
}

# Full RU for odd bodies — will pack as CP1251 into ANSI slot if fits by bytes
ODD_BODIES_RU = {
    "Pay attention to the doppler radar! It warns you about imminent tornados and storms. It can (hopefully) help you avoid them. It also tells you where other employees are and whether they are alive, or not...": (
        "Следите за доплер-радаром! Он предупреждает о торнадо и бурях и (надеемся) поможет их избежать. "
        "Также показывает, где сотрудники и живы ли они."
    ),
    "The monitors let you see what other employees are doing, and help you work better as a team (if you see anyone slacking off please report it).": (
        "Мониторы показывают, что делают другие. Работайте командой (лентяев — в рапорт)."
    ),
    "Communication is key. To use the walkie-talkie press [{Key0}] to turn it on and off and [{Key1}] to talk to your teammates. Please limit conversation to work-related topics, such as your survival.": (
        "Связь важна. Рация: [{Key0}] вкл/выкл, [{Key1}] говорить. Только рабочие темы — выживание."
    ),
    "This is the storage box. You have to bring all collectables you find here, newspapers, VHS tapes, files, and the like, otherwise you will not get any rewards out of them, company policy.": (
        "Ящик склада: несите сюда газеты, VHS, файлы — иначе наград не будет. Политика компании."
    ),
    "Defibrillators can bring a fellow employee back from the brink of death!, it can also let them keep working for us. To use it, hold [{Key0}] to charge it up, and aim at a downed employee to revive them.": (
        "Дефибриллятор поднимает упавших. Удерживайте [{Key0}] для заряда и целитесь в лежащего."
    ),
    "This is a consumable. Like the name suggests, it will get consumed after use. Hold [{Key0}] to use it, each one either heals you or gives different temporary benefits. ": (
        "Расходник: после использования пропадает. Удерживайте [{Key0}] — лечение или временный бафф."
    ),
    "These are the fuses, they protect the entire electricity network of the van. If they break, the lights on the van will flicker. Press and hold [{Key0}] to remove the blown out fuses, then get new fuses to replace them.": (
        "Предохранители защищают сеть фургона. Если мигают огни — удерживайте [{Key0}], снимите сгоревшие и поставьте новые."
    ),
    "This is the oil reservoir. Press and hold the [{Key0}] to open and close it, and [{Key1}] to fill it up when you have an oil bottle.": (
        "Бачок масла: [{Key0}] открыть/закрыть, [{Key1}] залить из бутылки."
    ),
    "This is a fuel can, you should bring it to the fuel tank on the left side of the van and press [{Key0}] to fill it up.": (
        "Канистра: к баку слева, затем [{Key0}] залить."
    ),
    "This is a coolant bottle, you should bring it to the coolant reservoir on the front of the van and press [{Key0}] to fill it up.": (
        "ОЖ: к бачку спереди, затем [{Key0}] залить."
    ),
    "Rain will simply get you wet while you are not under a roof, nothing too serious on its own, but be careful with electricity while wet! You should get an umbrella, please be a team player and share it with other employees.": (
        "Дождь только мочит, но мокрым опасно лезть к электричеству. Возьмите зонт и делитесь с командой."
    ),
    "Hail has a chance of damaging you while you are not under a roof. Should you get an umbrella, please be a team player and share it with other employees.": (
        "Град может ранить без крыши. Зонт лучше делить с командой."
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
}

# Need exact EN for battery / tokens from game — filled at runtime from chunk scan
SCHEMATIC_CANDIDATES = [
    "SERVICE SCHEMATIC",
    "Service Schematic",
    "// SERVICE SCHEMATIC",
    "SERVICE SCHEMATIC ",
]


def refresh() -> None:
    for cid, name in (
        ("ef3ae707dd08c5be00000001", "DT_TutorialMessages"),
        ("b59f6ff6f0eaa61a00000001", "W_VanSchematic"),
        ("cf4f8414fc705fd600000001", "WBP_HandbookButton"),
        ("043a163d52dc095d00000001", "WBP_SchematicButton"),
    ):
        dest = CHUNKS / f"{name}.bin"
        try:
            subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(dest)])
        except subprocess.CalledProcessError:
            print("skip get", name)


def find_ansi_slot(data: bytes, en: str) -> tuple[int, int] | None:
    try:
        ansi = en.encode("ascii") + b"\x00"
    except UnicodeEncodeError:
        return None
    start = 0
    while True:
        pos = data.find(ansi, start)
        if pos < 4:
            return None
        ln = struct.unpack_from("<i", data, pos - 4)[0]
        if ln == len(ansi):
            return pos - 4, ln
        start = pos + 1


def find_u16_slot(data: bytes, en: str) -> tuple[int, int] | None:
    u16 = en.encode("utf-16-le") + b"\x00\x00"
    start = 0
    while True:
        pos = data.find(u16, start)
        if pos < 4:
            return None
        ln = struct.unpack_from("<i", data, pos - 4)[0]
        units = len(u16) // 2
        if ln == -units:
            return pos - 4, units
        start = pos + 1


def pack_cp1251(old_payload: int, text: str) -> bytes | None:
    """Pack Cyrillic as Windows-1251 into positive FString of exact payload size."""
    max_bytes = old_payload - 1
    try:
        raw = text.encode("cp1251")
    except UnicodeEncodeError:
        # drop unsupported chars
        raw = text.encode("cp1251", errors="replace")
    if len(raw) > max_bytes:
        raw = raw[:max_bytes]
        # avoid cutting mid... cp1251 is 1 byte/char so OK
    if len(raw) < max_bytes:
        raw = raw + (b" " * (max_bytes - len(raw)))
    if len(raw) != max_bytes:
        return None
    return struct.pack("<i", old_payload) + raw + b"\x00"


def pack_utf16(units_with_null: int, text: str) -> bytes | None:
    max_chars = units_with_null - 1
    if len(text) > max_chars:
        text = text[:max_chars]
    if len(text) < max_chars:
        text = text + (" " * (max_chars - len(text)))
    raw = text.encode("utf-16-le") + b"\x00\x00"
    if len(raw) != units_with_null * 2:
        return None
    return struct.pack("<i", -units_with_null) + raw


def patch_file(path: Path, mapping: dict[str, str], mode: str) -> int:
    """mode: utf16 | cp1251 | ascii"""
    data = bytearray(path.read_bytes())
    ok = 0
    # apply longer keys first
    for en in sorted(mapping.keys(), key=len, reverse=True):
        ru = mapping[en]
        if mode == "utf16":
            slot = find_u16_slot(data, en)
            if slot:
                off, units = slot
                blob = pack_utf16(units, ru)
                if blob and len(blob) == 4 + units * 2:
                    data[off : off + len(blob)] = blob
                    ok += 1
                    continue
            # also try ansi even → utf16
            slot_a = find_ansi_slot(data, en)
            if slot_a:
                off, pay = slot_a
                if pay % 2 == 0 and any(ord(c) > 127 for c in ru):
                    units = pay // 2
                    blob = pack_utf16(units, ru)
                    if blob and len(blob) == 4 + pay:
                        data[off : off + len(blob)] = blob
                        ok += 1
                elif not any(ord(c) > 127 for c in ru):
                    maxc = pay - 1
                    t = ru[:maxc].ljust(maxc)
                    blob = struct.pack("<i", pay) + t.encode("ascii") + b"\x00"
                    if len(blob) == 4 + pay:
                        data[off : off + len(blob)] = blob
                        ok += 1
        elif mode == "cp1251":
            slot_a = find_ansi_slot(data, en)
            if not slot_a:
                continue
            off, pay = slot_a
            blob = pack_cp1251(pay, ru)
            if blob and len(blob) == 4 + pay:
                data[off : off + len(blob)] = blob
                ok += 1
                print("CP1251", path.name, len(ru.encode("cp1251", errors="replace")), "<=", pay - 1, en[:40])
    path.write_bytes(data)
    return ok


def scan_schematic_labels() -> dict[str, str]:
    found: dict[str, str] = {}
    for name in ("W_VanSchematic", "WBP_SchematicButton", "WBP_HandbookButton", "DT_TutorialMessages"):
        p = CHUNKS / f"{name}.bin"
        if not p.exists():
            continue
        data = p.read_bytes()
        for en in SCHEMATIC_CANDIDATES:
            if find_ansi_slot(data, en) or find_u16_slot(data, en):
                print("found schematic label", name, repr(en))
        # brute search SERVICE
        idx = data.find(b"SERVICE")
        while idx != -1:
            # try read fstring
            if idx >= 4:
                ln = struct.unpack_from("<i", data, idx - 4)[0]
                if 5 <= ln <= 40 and idx + ln <= len(data):
                    raw = data[idx : idx + ln]
                    if raw.endswith(b"\x00"):
                        s = raw[:-1].decode("ascii", errors="replace")
                        if "SCHEMATIC" in s.upper() or "SERVICE" in s.upper():
                            print("ANSI svc", name, repr(s), "pay", ln, "even", ln % 2 == 0)
                            if ln % 2 == 0:
                                # max_utf16 = pay//2 - 1; pay 18 → 8
                                found[s] = "СХ.СЕРВ."
                            else:
                                found[s] = "SCHEMA"
            idx = data.find(b"SERVICE", idx + 1)
        # utf16 SERVICE
        m = "SERVICE".encode("utf-16-le")
        idx = data.find(m)
        while idx != -1:
            if idx >= 4:
                ln = struct.unpack_from("<i", data, idx - 4)[0]
                if ln <= -3:
                    units = -ln
                    s = data[idx : idx + units * 2].decode("utf-16-le")
                    if s.endswith("\x00"):
                        s = s[:-1]
                    if "SCHEMATIC" in s.upper() or s.upper().startswith("SERVICE"):
                        print("U16 svc", name, repr(s), "chars", len(s))
                        # fit short RU
                        found[s] = ("СХ.СЕРВ." + " " * 20)[: len(s)].rstrip()
            idx = data.find(m, idx + 2)
    return found


def pull_missing_bodies(data: bytes) -> dict[str, str]:
    """Find battery / tokens strings from screenshots if present."""
    extra = {}
    needles = [
        b"van",
        b"APEX Tokens",
        b"battery, it powers",
        b"workbench will spawn",
    ]
    # extract all long ansi strings and match keywords
    i = 0
    n = len(data)
    while i + 4 <= n:
        ln = struct.unpack_from("<i", data, i)[0]
        if 40 <= ln <= 400 and i + 4 + ln <= n:
            raw = data[i + 4 : i + 4 + ln]
            if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
                s = raw[:-1].decode("ascii")
                if "battery, it powers" in s or "powers the engine" in s:
                    extra[s] = (
                        "Это АКБ фургона: двигатель, автомат, радар, рация, свет. "
                        "Сломан — всё мёртво. Снимите инструментом [{Key0}], поставьте новый."
                    )
                elif "APEX Tokens" in s:
                    extra[s] = (
                        "Вы нашли APEX Tokens! Тратьте их на продукцию компании в фургоне "
                        "(не обмениваются на реальные деньги)."
                    )
                i += 4 + ln
                continue
        if -400 <= ln <= -40:
            nbytes = (-ln) * 2
            if i + 4 + nbytes <= n:
                try:
                    s = data[i + 4 : i + 4 + nbytes].decode("utf-16-le")
                    if s.endswith("\x00"):
                        s = s[:-1]
                    if "battery, it powers" in s or "powers the engine" in s:
                        extra[s] = (
                            "Это АКБ фургона: двигатель, автомат, радар, рация, свет. "
                            "Сломан — всё мёртво. Снимите инструментом [{Key0}], поставьте новый."
                        )
                    elif "APEX Tokens" in s:
                        extra[s] = (
                            "Вы нашли APEX Tokens! Тратьте их в фургоне "
                            "(не обмениваются на реальные деньги)."
                        )
                    i += 4 + nbytes
                    continue
                except Exception:
                    pass
        i += 1
    return extra


def ensure_asset(cid: str, name: str, rel: str) -> None:
    path = ROOT / "tools" / "build_ui_loc_safe.py"
    text = path.read_text(encoding="utf-8")
    if name in text:
        return
    j = text.rfind("),", 0, text.find("def fit_utf16"))
    insert = f'\n    "{cid}": (\n        "{name}",\n        "{rel}",\n    ),'
    path.write_text(text[: j + 2] + insert + text[j + 2 :], encoding="utf-8")
    print("added asset", name)
    # legacy
    subprocess.check_call(
        [
            str(RETOC),
            "to-legacy",
            "--no-shaders",
            "--version",
            "UE5_5",
            "-f",
            name,
            str(GAME_UTOC.parent),
            str(ROOT / "extract_ui"),
        ]
    )


def main() -> None:
    refresh()
    ensure_asset(
        "cf4f8414fc705fd600000001",
        "WBP_HandbookButton",
        "StormEscape/UI/Widgets/VanSchematic/SubWidgets/WBP_HandbookButton",
    )
    ensure_asset(
        "043a163d52dc095d00000001",
        "WBP_SchematicButton",
        "StormEscape/UI/Widgets/VanSchematic/SubWidgets/WBP_SchematicButton",
    )
    refresh()

    tut = CHUNKS / "DT_TutorialMessages.bin"
    van = CHUNKS / "W_VanSchematic.bin"
    data_tut = tut.read_bytes()

    bodies = dict(ODD_BODIES_RU)
    bodies.update(pull_missing_bodies(data_tut))
    bodies.update(pull_missing_bodies(van.read_bytes()))
    print("body keys", len(bodies))

    schematic = scan_schematic_labels()
    print("schematic labels", schematic)

    # 1) Patch odd titles+bodies with CP1251 directly into DT chunk
    cp_map = {**ODD_TITLES_RU, **bodies}
    n1 = patch_file(tut, cp_map, "cp1251")
    print("tutorial cp1251 patches", n1)

    # 2) Even titles via normal map + utf16
    m = json.loads(MAP.read_text(encoding="utf-8"))
    m.update(EVEN_TITLES)
    for en, ru in schematic.items():
        if any(ord(c) > 127 for c in ru):
            m[en] = ru
        else:
            # ascii schematic label
            m[en] = ru
    # SERVICE SCHEMATIC heuristics
    for en, ru in (
        ("SERVICE SCHEMATIC", "СХЕМА СЕРВИСА"),
        ("Service Schematic", "Схема сервиса"),
    ):
        # prefer fitting
        for p in (van, CHUNKS / "WBP_SchematicButton.bin", CHUNKS / "WBP_HandbookButton.bin"):
            if not p.exists():
                continue
            d = p.read_bytes()
            a = find_ansi_slot(d, en)
            if a:
                pay = a[1]
                if pay % 2 == 0 and len(ru) <= (pay // 2) - 1:
                    m[en] = ru
                    print("map schematic", en, "->", ru, "max", (pay // 2) - 1)
                elif pay % 2 == 1:
                    # cp1251 direct later
                    pass
            u = find_u16_slot(d, en)
            if u and len(ru) <= u[1] - 1:
                m[en] = ru

    MAP.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3) Also CP1251 patch vanschematic for any matching bodies/labels
    n2 = patch_file(van, {**bodies, **schematic, **ODD_TITLES_RU}, "cp1251")
    print("van cp1251", n2)

    # 4) Rebuild pack from map (even utf16), then overwrite tutorial/van chunks with our CP1251-patched bins
    sys.stdout.flush()
    rc = subprocess.call([sys.executable, "-u", str(ROOT / "tools" / "build_ui_loc_safe.py")])
    if rc != 0:
        raise SystemExit(rc)

    # After build, ensure_chunks re-got vanilla — we need to inject CP1251 patches into packed raw
    # Re-apply: get was done inside build from game. So we must patch AFTER build on raw chunks
    # OR skip ensure overwrite: patch installed by writing into raw before pack.

    # Rebuild path: patch chunks_ui again, then manually replace in raw and repack
    # Simpler: patch the installed approach — re-get, cp1251 patch, then call a slim repack

    # Re-do CP1251 on fresh get and inject into raw_ui_loc then pack-raw
    refresh()
    tut.write_bytes((CHUNKS / "DT_TutorialMessages.bin").read_bytes())  # already fresh
    # fresh get already in refresh
    n1 = patch_file(CHUNKS / "DT_TutorialMessages.bin", cp_map, "cp1251")
    n2 = patch_file(CHUNKS / "W_VanSchematic.bin", {**bodies, **schematic}, "cp1251")
    # also apply even titles as utf16 on tutorial
    n3 = patch_file(CHUNKS / "DT_TutorialMessages.bin", EVEN_TITLES, "utf16")
    print("repatch", n1, n2, n3)

    raw_chunks = ROOT / "raw_ui_loc" / "chunks"
    if not raw_chunks.is_dir():
        raw_chunks = ROOT / "raw_ui_loc"
    mapping_ids = {
        "DT_TutorialMessages": "ef3ae707dd08c5be00000001",
        "W_VanSchematic": "b59f6ff6f0eaa61a00000001",
    }
    for name, cid in mapping_ids.items():
        src = CHUNKS / f"{name}.bin"
        dst = raw_chunks / cid
        if dst.exists():
            dst.write_bytes(src.read_bytes())
            print("injected", name, "->", cid)
        else:
            print("MISSING raw", cid)

    out = ROOT / "out_ui_loc" / "FunnelRunners_RU_UI_P.utoc"
    for p in (ROOT / "out_ui_loc").glob("FunnelRunners_RU_UI_P*"):
        if p.suffix in {".utoc", ".ucas"}:
            p.unlink()
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "pack-raw",
            str(ROOT / "raw_ui_loc"),
            str(out),
        ]
    )
    paks = Path(
        r"C:\Program Files (x86)\Steam\steamapps\common\Funnel Runners\StormEscape\Content\Paks"
    )
    for p in (ROOT / "out_ui_loc").iterdir():
        if p.name.startswith("FunnelRunners_RU_UI_P") and p.suffix in {".pak", ".utoc", ".ucas"}:
            dest = paks / p.name
            dest.write_bytes(p.read_bytes())
            print("installed", p.name, p.stat().st_size)
    subprocess.check_call([str(RETOC), "verify", str(paks / "FunnelRunners_RU_UI_P.utoc")])
    print("DONE CP1251 SPR experiment + schematic")


if __name__ == "__main__":
    main()
