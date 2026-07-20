"""Merge shorter RU + tips/tutorial into ui_ru_map.json."""
from __future__ import annotations

import json
from pathlib import Path

MAP = Path(r"C:\Mods\FunnelRunners_RU\translations\ui_ru_map.json")

UPDATES = {
    "Master Volume": "Громк.",
    "User Interface Volume": "Громк. UI",
    "Voice Chat Volume": "Голос чат",
    "Very High": "Макс",
    "Version 1": "Вер.1",
    "Version 2": "Вер.2",
    "Play": "Играть",
    "settings": "настр.",
    "credits": "титры",
    "Watch Tutorial": "Обучение",
    "Resume": "Играть",
    "Settings": "Опции",
    "Credits": "Титры",
    "Exit": "Уйти",
    "Report Issue": "Репорт",
    "Session Info": "Сессия",
    # loading tips
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
    # tutorials (even slots)
    (
        'Welcome {Employee}! Use WASD or <Key id="Gamepad_Left2D"/>  to move around, '
        "move the mouse cursor to look around and press [{Key0}] to interact. "
        "We will explain things as we go."
    ): (
        "Добро пожаловать, {Employee}! WASD или <Key id=\"Gamepad_Left2D\"/> — ходьба, "
        "мышь — обзор, [{Key0}] — взаимодействие. Дальше объясним по ходу."
    ),
    (
        "Up to for doing some extra hours? No? Too bad, they are mandatory. "
        "The mission board lists secondary objectives other than escaping. "
        "Completing them will grant extra rewards (and help you keep your job)."
    ): (
        "Сверхурочные обязательны. На доске — побочные цели кроме побега. "
        "За них дают награды (и шанс сохранить работу)."
    ),
    (
        "Can we fix it? Probably, you better hope so. Toolboxes can be used to remove "
        "both broken tires and batteries on the van. To use it, press [{Key0}] while highlighting them."
    ): (
        "Ящик инструментов снимает спущенные колёса и аккумуляторы. Наведите и нажмите [{Key0}]."
    ),
    (
        "Scissor Jacks can be used to lift up the van and change broken tires. "
        "To use it, press [{Key0}] while highlighting a flat tire."
    ): (
        "Домкрат поднимает фургон для смены колеса. Наведите на спущенное и [{Key0}]."
    ),
    (
        "Umbrellas protect you and other nearby employees from getting wet by rain, "
        "and damaged by hail or acid rain when held. Just make sure to put it away if there is a lightning storm."
    ): (
        "Зонт защищает вас и рядом стоящих от дождя, града и кислоты. Уберите при грозе с молниями."
    ),
    (
        "This is the coolant reservoir. Press and hold [{Key0}] to open and close it, "
        "and [{Key1}] to fill it up when you have a coolant bottle."
    ): (
        "Бачок ОЖ. Удерживайте [{Key0}] чтобы открыть/закрыть, [{Key1}] — залить из бутылки."
    ),
    (
        "This is the fuel tank. Press and hold [{Key0}] to open and close it, "
        "and [{Key1}] to fill it up when you have a fuel can."
    ): (
        "Топливный бак. [{Key0}] — открыть/закрыть, [{Key1}] — залить из канистры."
    ),
    (
        "This is an oil bottle, you should bring it to the oil reservoir on the front "
        "of the van and press [{Key0}] to fill it up."
    ): (
        "Бутылка масла. Отнесите к бачку спереди фургона и нажмите [{Key0}]."
    ),
    (
        "This is a new tire, you can replace any broken tire on the van with this one. "
        "First you need a scissors jack to lift up the van and a toolbox to remove the old tire. "
        "Once you do that, just press [{Key0}] to install the new one."
    ): (
        "Новое колесо. Сначала домкрат и инструмент, чтобы снять старое. Затем [{Key0}] — поставить новое."
    ),
    (
        "These are new fuses, you can replace any blown out fuses that where removed by pressing [{Key0}]."
    ): ("Новые предохранители. Установите вместо снятых: [{Key0}]."),
    (
        "This is a new battery, you can replace a broken battery that was removed with a toolbox by pressing [{Key0}]."
    ): ("Новый аккумулятор. После снятия старого инструментом нажмите [{Key0}]."),
    (
        "A collectable! Take it back to the collectables box on the van and you will get a bonus "
        "for your trouble (only if you survive, otherwise it will NOT go to your next of kin)."
    ): ("Находка! Отнесите в ящик на фургоне — будет бонус (только если выживете)."),
    (
        "Acid rain will damage you constantly while you are not under a roof. "
        "Should you get an umbrella, please be a team player and share it with other employees."
    ): ("Кислотный дождь ранит без крыши. Зонт лучше делить с командой."),
    (
        "Pay attention employee, certain dangerous actions will require you to be very precise. "
        "You must press [{Key0}] when the indicator is on the green area to successfully perform the action. "
        "If you fail, you might take damage. Some interactions will require multiple presses to be completed."
    ): (
        "Осторожно: для опасных действий жмите [{Key0}] в зелёной зоне. Промах — урон. "
        "Иногда нужно несколько нажатий."
    ),
    (
        "Communication is key to teamwork! This whiteboard is great tool for that, write on it "
        "and coordinate survival plans. Keep all drawings and messages strictly professional and work-related."
    ): ("Доска для координации. Пишите планы выживания — только по делу."),
    (
        "Welcome to the APEX internal broadcast system! Grab the radio microphone and press [{Key0}] "
        "to transmit your voice to your teammates."
    ): ("Внутренняя связь APEX. Возьмите микрофон и жмите [{Key0}], чтобы говорить команде."),
}


def main() -> None:
    m = json.loads(MAP.read_text(encoding="utf-8"))
    m.update(UPDATES)
    MAP.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("map entries", len(m))


if __name__ == "__main__":
    main()
