from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(r"C:\Mods\FunnelRunners_RU")
MAP = ROOT / "translations" / "ui_ru_map.json"
CHUNKS = ROOT / "chunks_ui"
CATALOG = ROOT / "translations" / "items_credits_catalog.json"

# Restored tips/tutorial/settings that previously fit (from earlier successful builds)
CANDIDATES = {
    # tips
    "Changing tires, please stand by": "Меняем колёса, подождите",
    "Cleaning the van, please stand by": "Моем фургон, подождите",
    "Calibrating monitors, please stand by": "Калибруем мониторы, ждите",
    "Watch your step! Open manholes are a hazard": "Осторожно: открытые люки опасны",
    "Avoid abandoned vehicles during thunderstorms": "В грозу избегайте брошенных машин",
    "Carrying heavy items reduces movement speed": "Тяжёлые вещи замедляют движение",
    "Avoid live wires, it is a shocking experience": "Не трогайте провода под напряжением",
    "Remember: APEX is always watching": "Помните: APEX всё видит",
    "Use portable conductors to protect crew": "Портативные проводники защищают",
    "Keep your distance from burning crewmates": "Держитесь дальше от горящих",
    "Do not touch electrocuted crewmates": "Не трогайте ударенных током",
    "Recover APEX property to maximize your rating": "Собирайте имущество APEX для рейтинга",
    "Complete extra tasks to boost your rating": "Доп. задания повышают рейтинг",
    "Wait your turn on the Walkie-Talkie": "Ждите очереди на рацию",
    # content warning / long desc that fit
    "This game contains flashing lights that may trigger photosensitive epilepsy.\r\n\r\nThis game depicts natural disasters and their aftermath, which some players may find distressing.": (
        "В игре есть мигающие эффекты — это может спровоцировать приступ у людей с фотосенситивной эпилепсией.\r\n\r\n"
        "Показаны стихийные бедствия и их последствия — некоторым игрокам это может быть неприятно."
    ),
    # credits
    "Rashaun James Torralba": "Mark Derick - RUS Loc.",
    # items — short complete words only where slot allows
    "Bandage": "Бинт",  # max 3? Bandage payload 8 even max 3 -> "Бинт" = 4 NO. use "Бин"
    "Crowbar": "Лом",  # max 3
    "Medkit": "Аптечк",  # Medkit odd? 
    "Umbrella": "Зонт",
    "Acid Rain": "Кислот",  # max 4 -> "Кислота"=7 no; max 4 "Кисл"
    "Granola Bar": "Снек",  # max 5
    "Energy Drink": None,  # odd often
    "Hail Storm": "Град",
    "Might not be a medkit but it will do.": "Не аптечка, но сойдёт.",  # max 18
    "Needing that extra boost?": "Нужен доп. заряд?",  # max 12 - 17 chars no
    "A hail storm is damaging you.": "Град наносит вам урон.",  # max 14 - 22 no -> shorter
    "Acid rain is damaging you.": "Кислота ранит вас.",
    "Ideal for the darkest environments, so nobody misses any details.": (
        "Для самой тёмной местности — детали не пропустите."
    ),
    "Clear! Just make sure they are actually dead before you apply the pads.": (
        "Заряд! Проверьте, что напарник реально в отключке."
    ),
    "Estimated battery charge: <General>10 min</>.": "Заряд батареи: <General>10 мин</>.",
    "Estimated battery charge: <General>5 min</>.": "Заряд: <General>5 мин</>.",
    "Restores <Positive>30 HP</> instantly.": "Сразу <Positive>+30 HP</>.",
    "Restores <Positive>60 HP</> instantly.": "Сразу <Positive>+60 HP</>.",
    "Restores <Positive>20 HP</> over <General>10s</>.": "<Positive>+20 HP</> / <General>10с</>.",
    "Increases <Bold>movement speed</> by <Positive>36%</> for <General>2 min</>.": (
        "<Bold>Скорость</> <Positive>+36%</> / <General>2м</>."
    ),
    "Increases <Bold>stamina</> by <Positive>30%</> for <General>2 min</>.": (
        "<Bold>Выносливость</> <Positive>+30%</> / <General>2м</>."
    ),
    "Increases <Bold>stamina recovery</> by <Positive>150%</> for <General>2 min</>.": (
        "<Bold>Восст. стамины</> <Positive>+150%</> / <General>2м</>."
    ),
    "<General>Opens locked doors and deals melee damage to players</>.": (
        "<General>Ломает двери и бьёт игроков вблизи</>."
    ),
    "<General>Revives downed teammates or knocks out conscious players</>.": (
        "<General>Поднимает упавших / нокаутит живых</>."
    ),
    "A quick snack since every second counts.": "Быстрый перекус — время дорого.",
    "A premium medkit, to save you from any situation on the field.": (
        "Аптечка для тяжёлых ситуаций в поле."
    ),
    "Better performance, worse taste.": "Сильнее эффект, хуже вкус.",
    # tutorials that fit even slots
    (
        "Can we fix it? Probably, you better hope so. Toolboxes can be used to remove "
        "both broken tires and batteries on the van. To use it, press [{Key0}] while highlighting them."
    ): "Ящик инструментов снимает спущенные колёса и аккумуляторы. Наведите и нажмите [{Key0}].",
    (
        "Scissor Jacks can be used to lift up the van and change broken tires. "
        "To use it, press [{Key0}] while highlighting a flat tire."
    ): "Домкрат поднимает фургон для смены колеса. Наведите на спущенное и [{Key0}].",
    (
        "Umbrellas protect you and other nearby employees from getting wet by rain, "
        "and damaged by hail or acid rain when held. Just make sure to put it away if there is a lightning storm."
    ): "Зонт защищает вас и рядом стоящих от дождя, града и кислоты. Уберите при грозе с молниями.",
    (
        "This is the coolant reservoir. Press and hold [{Key0}] to open and close it, "
        "and [{Key1}] to fill it up when you have a coolant bottle."
    ): "Бачок ОЖ. Удерживайте [{Key0}] чтобы открыть/закрыть, [{Key1}] — залить из бутылки.",
    (
        "This is the fuel tank. Press and hold [{Key0}] to open and close it, "
        "and [{Key1}] to fill it up when you have a fuel can."
    ): "Топливный бак. [{Key0}] — открыть/закрыть, [{Key1}] — залить из канистры.",
    (
        "This is an oil bottle, you should bring it to the oil reservoir on the front "
        "of the van and press [{Key0}] to fill it up."
    ): "Бутылка масла. Отнесите к бачку спереди фургона и нажмите [{Key0}].",
    (
        "These are new fuses, you can replace any blown out fuses that where removed by pressing [{Key0}]."
    ): "Новые предохранители. Установите вместо снятых: [{Key0}].",
    (
        "This is a new battery, you can replace a broken battery that was removed with a toolbox by pressing [{Key0}]."
    ): "Новый аккумулятор. После снятия старого инструментом нажмите [{Key0}].",
    (
        "A collectable! Take it back to the collectables box on the van and you will get a bonus "
        "for your trouble (only if you survive, otherwise it will NOT go to your next of kin)."
    ): "Находка! Отнесите в ящик на фургоне — будет бонус (только если выживете).",
    (
        "Acid rain will damage you constantly while you are not under a roof. "
        "Should you get an umbrella, please be a team player and share it with other employees."
    ): "Кислотный дождь ранит без крыши. Зонт лучше делить с командой.",
    (
        "Communication is key to teamwork! This whiteboard is great tool for that, write on it "
        "and coordinate survival plans. Keep all drawings and messages strictly professional and work-related."
    ): "Доска для координации. Пишите планы выживания — только по делу.",
    (
        "Welcome to the APEX internal broadcast system! Grab the radio microphone and press [{Key0}] "
        "to transmit your voice to your teammates."
    ): "Внутренняя связь APEX. Возьмите микрофон и жмите [{Key0}], чтобы говорить команде.",
}


def build_index():
    idx = {}
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    for asset, rows in cat.items():
        for r in rows:
            idx.setdefault(r["en"], []).append(r)
    for p in CHUNKS.glob("*.bin"):
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
                        {"en": s, "payload": payload, "even": even, "max_utf16": maxc}
                    )
                    i += 4 + ln
                    continue
            i += 1
    return idx


def fits(en: str, ru: str, idx) -> bool:
    if en not in idx or ru is None:
        return False
    for r in idx[en]:
        if any(ord(c) > 127 for c in ru):
            if not r.get("even"):
                return False
            if r.get("max_utf16") is None or len(ru) > r["max_utf16"]:
                return False
        else:
            if len(ru) > r["payload"] - 1:
                return False
    return True


def main():
    idx = build_index()
    cur = json.loads(MAP.read_text(encoding="utf-8"))

    # Keep existing good entries
    out = dict(cur)

    # Add candidates that fit
    added = 0
    for en, ru in CANDIDATES.items():
        if ru is None:
            continue
        if fits(en, ru, idx):
            if out.get(en) != ru:
                out[en] = ru
                added += 1
                print("ADD", en[:50], "=>", ru[:50])
        else:
            # try to show why
            if en in idx:
                r = idx[en][0]
                print(
                    f"SKIP {en[:40]!r} ru_len={len(ru) if ru else None} "
                    f"even={r.get('even')} max={r.get('max_utf16')}"
                )

    # Tuned shorts for names
    tuned = {
        "Bandage": "Бин",  # max 3
        "Crowbar": "Лом",
        "Acid Rain": "Кисл",  # max 4
        "Granola Bar": "Снек",
        "Hail Storm": "Град",
        "Umbrella": "Зонт",
        "Needing that extra boost?": "Нужен заряд?",  # 12 max
        "A hail storm is damaging you.": "Вас бьёт град.",  # 14
        "Lunaria 2D Flashlight": "Фонарь 2D",  # max 10
        "Lunaria 5109LS Flashlight": "Фонарь 5109LS",  # max 12
        "Health Pills": "Хил",  # if odd skip
        "Portable Conductor": "Громоотвод",  # check
        "Portable Doppler": "Доплер",
        "LIFESAVE Defibrillator": "Дефибриллятор",
        "Energy Drink": "Энергетик",
        "Energy Pills": "Пилюли",
        "Medkit": "Аптечк",
    }
    for en, ru in tuned.items():
        if fits(en, ru, idx):
            out[en] = ru
            print("TUNED", en, "=>", ru)
        else:
            if en in idx:
                r = idx[en][0]
                print(f"NO {en!r} need<={r.get('max_utf16')} odd={not r.get('even')} got={len(ru)}")

    MAP.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("TOTAL", len(out), "added_this_pass", added)


if __name__ == "__main__":
    main()
