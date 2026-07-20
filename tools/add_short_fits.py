from __future__ import annotations

import json
import struct
from pathlib import Path

MAP = Path(r"C:\Mods\FunnelRunners_RU\translations\ui_ru_map.json")
CHUNKS = Path(r"C:\Mods\FunnelRunners_RU\chunks_ui")
CATALOG = Path(r"C:\Mods\FunnelRunners_RU\translations\items_credits_catalog.json")

# Pre-sized to fit max_utf16 from audit
FITS = {
    # tips (max in comment)
    "Changing tires, please stand by": "Меняем колёса…",  # 15
    "Cleaning the van, please stand by": "Моем фургон…",  # 16
    "Calibrating monitors, please stand by": "Калибруем мониторы…",  # 18
    "Watch your step! Open manholes are a hazard": "Осторожно: открытые люки!",  # 21
    "Avoid abandoned vehicles during thunderstorms": "В грозу — прочь от машин",  # 22
    "Carrying heavy items reduces movement speed": "Тяжёлое замедляет бег",  # 21
    "Avoid live wires, it is a shocking experience": "Не трогай провода — ток!",  # 22
    "Remember: APEX is always watching": "APEX всё видит",  # 16
    "Use portable conductors to protect crew": "Берите громоотводы",  # 19
    "Keep your distance from burning crewmates": "Держись дальше от огня",  # 20
    "Do not touch electrocuted crewmates": "Не трогай под током",  # 17
    "Recover APEX property to maximize your rating": "Носи находки APEX в фургон",  # 22
    "Complete extra tasks to boost your rating": "Доп. задания = рейтинг",  # 20
    "Wait your turn on the Walkie-Talkie": "Жди очереди на рацию",  # 17
    # items
    "Lunaria 5109LS Flashlight": "Фонарь 5109",  # 12
    "Might not be a medkit but it will do.": "Не аптечка, но ок.",  # 18
    "Clear! Just make sure they are actually dead before you apply the pads.": (
        "Заряд! Сначала убедись, что он без сознания."
    ),  # 35
    "Ideal for the darkest environments, so nobody misses any details.": (
        "Для самой тьмы — ничего не упустите."
    ),  # 32
    "Estimated battery charge: <General>10 min</>.": "Заряд: <General>10 мин</>.",  # 22
    "Restores <Positive>20 HP</> over <General>10s</>.": "<Positive>+20 HP</> / <General>10с</>.",  # 24
    "Increases <Bold>stamina</> by <Positive>30%</> for <General>2 min</>.": (
        "<Bold>Стамина</> <Positive>+30%</> / <General>2м</>."
    ),  # 34
    "Increases <Bold>stamina recovery</> by <Positive>150%</> for <General>2 min</>.": (
        "<Bold>Восст.стамины</> <Positive>+150%</>/<General>2м</>."
    ),  # 39
    "<General>Opens locked doors and deals melee damage to players</>.": (
        "<General>Ломает двери и бьёт игроков</>."
    ),  # 32
    "<General>Revives downed teammates or knocks out conscious players</>.": (
        "<General>Режит упавших / нокаутит живых</>."
    ),  # 34
    # tutorials shortened
    "Can we fix it? Probably, you better hope so. Toolboxes can be used to remove both broken tires and batteries on the van. To use it, press [{Key0}] while highlighting them.": (
        "Инструменты снимают колёса и АКБ. Наведите и жмите [{Key0}]."
    ),
    "Scissor Jacks can be used to lift up the van and change broken tires. To use it, press [{Key0}] while highlighting a flat tire.": (
        "Домкрат поднимает фургон. На спущенное колесо — [{Key0}]."
    ),
    "Umbrellas protect you and other nearby employees from getting wet by rain, and damaged by hail or acid rain when held. Just make sure to put it away if there is a lightning storm.": (
        "Зонт от дождя/града/кислоты. Уберите при молниях."
    ),
    "This is the coolant reservoir. Press and hold [{Key0}] to open and close it, and [{Key1}] to fill it up when you have a coolant bottle.": (
        "Бачок ОЖ: [{Key0}] открыть, [{Key1}] залить."
    ),
    "This is the fuel tank. Press and hold [{Key0}] to open and close it, and [{Key1}] to fill it up when you have a fuel can.": (
        "Бак: [{Key0}] открыть/закрыть, [{Key1}] залить."
    ),
    "This is an oil bottle, you should bring it to the oil reservoir on the front of the van and press [{Key0}] to fill it up.": (
        "Масло — к бачку спереди, затем [{Key0}]."
    ),
    "These are new fuses, you can replace any blown out fuses that where removed by pressing [{Key0}].": (
        "Новые предохранители: ставьте через [{Key0}]."
    ),
    "This is a new battery, you can replace a broken battery that was removed with a toolbox by pressing [{Key0}].": (
        "Новый АКБ: после снятия старого жмите [{Key0}]."
    ),
    "A collectable! Take it back to the collectables box on the van and you will get a bonus for your trouble (only if you survive, otherwise it will NOT go to your next of kin).": (
        "Находка! Несите в ящик фургона — бонус, если выживете."
    ),
    "Acid rain will damage you constantly while you are not under a roof. Should you get an umbrella, please be a team player and share it with other employees.": (
        "Кислота ранит без крыши. Зонт лучше делить с командой."
    ),
    "Communication is key to teamwork! This whiteboard is great tool for that, write on it and coordinate survival plans. Keep all drawings and messages strictly professional and work-related.": (
        "Доска для планов. Пишите по делу — только работа."
    ),
    "Welcome to the APEX internal broadcast system! Grab the radio microphone and press [{Key0}] to transmit your voice to your teammates.": (
        "Рация APEX: микрофон + [{Key0}] — говорить команде."
    ),
    "Up to for doing some extra hours? No? Too bad, they are mandatory. The mission board lists secondary objectives other than escaping. Completing them will grant extra rewards (and help you keep your job).": (
        "Сверхурочные обязательны. На доске — побочные цели и награды."
    ),
    'Welcome {Employee}! Use WASD or <Key id="Gamepad_Left2D"/>  to move around, move the mouse cursor to look around and press [{Key0}] to interact. We will explain things as we go.': (
        "Привет, {Employee}! WASD/<Key id=\"Gamepad_Left2D\"/> — ход, мышь — взгляд, [{Key0}] — действие."
    ),
}


def index():
    idx = {}
    if CATALOG.exists():
        for rows in json.loads(CATALOG.read_text(encoding="utf-8")).values():
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
                    idx.setdefault(s, []).append(
                        {
                            "payload": payload,
                            "even": even,
                            "max_utf16": (payload // 2) - 1 if even else None,
                        }
                    )
                    i += 4 + ln
                    continue
            i += 1
    return idx


def ok(en, ru, idx):
    if en not in idx:
        return False
    for r in idx[en]:
        if any(ord(c) > 127 for c in ru):
            if not r["even"] or len(ru) > r["max_utf16"]:
                return False
        elif len(ru) > r["payload"] - 1:
            return False
    return True


def main():
    idx = index()
    m = json.loads(MAP.read_text(encoding="utf-8"))
    n = 0
    for en, ru in FITS.items():
        if ok(en, ru, idx):
            m[en] = ru
            n += 1
            print("OK", len(ru), en[:40])
        else:
            r = idx.get(en, [{}])[0]
            print("NO", len(ru), "max", r.get("max_utf16"), en[:40])
    MAP.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("added", n, "total", len(m))


if __name__ == "__main__":
    main()
