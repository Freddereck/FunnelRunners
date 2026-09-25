# -*- coding: utf-8 -*-
"""Build full RU IoStore patch for all StormEscape StringTables."""
from __future__ import annotations

import json
import shutil
import struct
import subprocess
from pathlib import Path

RETOC = Path(r"C:\Mods\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
GAME_UTOC = Path(
    r"F:\SteamLibrary\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks\StormEscape-Windows.utoc"
)
PAKS = Path(
    r"F:\SteamLibrary\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks"
)
CHUNKS = Path(r"C:\Mods\FunnelRunners_RU\chunks\st_all")
RAW = Path(r"C:\Mods\FunnelRunners_RU\raw_all_loc")
OUT = Path(r"C:\Mods\FunnelRunners_RU\out_all_loc")

# chunk_id -> package leaf name (for namespace marker)
TABLES = {
    "0374f3e8fd7640b000000001": "ST_GeneralUserInterface",
    "05e04299a5ee231300000001": "ST_Popups",
    "3bb135da1dfd052500000001": "ST_Quests",
    "899e1ebb8134028800000001": "ST_Settings",
    "2ce2dcfd6f4c016d00000001": "ST_Skins",
    "a57bec729ed03cf200000001": "ST_Toasts",
    "97595efc6ec067c500000001": "ST_VanSchematic",
    # New in buildid 24975058+
    "5f7c2858d6e08a4800000001": "ST_Items",
    "c5f0c4fd3a5472fd00000001": "ST_Van",
    "9886aec7f24428b900000001": "ST_HUD",
    "7b1eaa20fd22ec9400000001": "ST_Moodlets",
    "21af07c31f29ce5300000001": "ST_Maps",
    "056ef998f588e1cf00000001": "ST_Minigames",
    "58d74f2fc7cadb4100000001": "ST_Stats",
    # New in buildid 25239041+
    "f41e68ee6cfef8f700000001": "ST_PostGameData",
    "7e8038c56267aae500000001": "ST_TermsAndConditions",
    "16ea38839c248e0200000001": "ST_DopplerRadar",
    "3a6e06760e8cc91900000001": "ST_CrewAssembly",
    "83681719e63c437e00000001": "ST_Emotes",
    "f440072263dc848200000001": "ST_VirtualKeyboard",
    "8685180574f26f9e00000001": "ST_CompanyVault",
    "1c9a92728e27f23f00000001": "ST_VendingMachine",
    # New in buildid 25496102+ (Session Codes / doors / keybinds)
    "9d3477bfef75ded700000001": "ST_Input",
    "8fdeaff1c1e3339500000001": "ST_SessionLobby",
    "f24aa85e4bd3be7300000001": "ST_Interactables",
}

# key -> Russian (preserve {Placeholders} and <Positive>...</> tags)
RU: dict[str, str] = {
    # Popups
    "LeaveSessionHeader": "ВЫХОДИ!?",
    "LeaveSessionBody": "Точно выйти из этой сессии?",
    "LeaveSessionToMenu": "В гл. меню",
    "LeaveSessionToDesktop": "На рабочий стол",
    "GenericOK": "ОК",
    "GenericYes": "Да",
    "GenericNo": "Нет",
    "GenericCancel": "Отмена",
    # Unstuck / keybind conflict (new patch)
    "UnstuckPlayerHeader": "ЗАСТРЯЛ?",
    "UnstuckPlayerConfirm": "Телепорт",
    "UnstuckPlayerCancel": "Отмена",
    "UnstuckPlayerDescription": "Телепортироваться в безопасное место? Это займёт несколько секунд.",
    "KeyBindingHeader": "КОНФЛИКТ КЛАВИШ",
    "KeyBindingMenuConflict": "Клавиша <General>{Key}</> уже занята навигацией интерфейса. Назначение на это действие может вызвать конфликты при открытом меню.",
    "KeyBindingConflict": "Клавиша <General>{Key}</> уже назначена на <Negative>{Action}</>.",
    "KeyBindingConflictBind": "Всё равно",
    "KeyBindingConflictRemove": "Убрать",
    "KeyBindingConflictSwap": "Сменить",
    "KeyBindingMenuHeader": "КОНФЛИКТ UI",
    "KeyBindingMouseErrorTitle": "НЕВЕРНАЯ ПРИВЯЗКА",
    "KeyBindingMouseErrorMessage": "К мыши можно привязать только:\n\nМини-игры — Взаимодействие",
    # General UI
    "CrewAssemblyVoiceConnecting": "Подключение к голосовому чату",
    "CrewAssemblyVoiceConnected": "Голосовой чат подключён",
    "CrewAssemblyVoiceConnect": "Подключиться к голосовому чату",
    "MicIndicatorVoicePending": "Подключение",
    "MidIndicatorVoiceDisconnected": "См. инфо сессии",
    "GameDifficultyEasy": "Тренировка",
    "GameDifficultyNormal": "Обычная",
    "GameDifficultyHard": "Сложная",
    "GameDifficultyNightmare": "Кошмар",
    "GameDifficultyAny": "Любая",
    # Settings
    "SettingsHigh": "В пользу картинки",
    "SettingsUltra": "Кинематограф*",
    "SettingsLow": "В пользу FPS",
    "SettingsMedium": "Баланс",
    "SettingsCustom": "Свои",
    # Voice chat regions (new patch)
    "VoiceChatRegion_Unknown": "---",
    "VoiceChatRegion_Automatic": "Авто",
    "VoiceChatRegion_AsiaNortheast": "Азия СВ (AS-NE)",
    "VoiceChatRegion_AsiaNortheastCode": "AS-NE",
    "VoiceChatRegion_Europe": "Европа (EU)",
    "VoiceChatRegion_EuropeCode": "EU",
    "VoiceChatRegion_Oceania": "Океания (OC)",
    "VoiceChatRegion_OceaniaCode": "OC",
    "VoiceChatRegion_SouthAmerica": "Юж. Америка (SA)",
    "VoiceChatRegion_SouthAmericaCode": "SA",
    "VoiceChatRegion_USCentral": "США Центр (US-C)",
    "VoiceChatRegion_USCentralCode": "US-C",
    "VoiceChatRegion_USEast": "США Восток (US-E)",
    "VoiceChatRegion_USEastCode": "US-E",
    "VoiceChatRegion_USWest": "США Запад (US-W)",
    "VoiceChatRegion_USWestCode": "US-W",
    "VoiceChatRegion_Any": "Любой",
    "Selector_VoiceChatRegion": "Регион голоса",
    # Toasts
    "DifficultyChangedTitle": "Сложность изменена",
    "DifficultyChangedMessage": "Сложность снижена до {Difficulty}, чтобы соответствовать уровню команды.",
    # Quests
    "QuestNoLimitsTitle": "Доступ открыт",
    "QuestInformationLeakObjectiveDoc": "Собрать документ APEX",
    "QuestTitleString": "{Title} {DifficultyLevel}",
    "QuestNoLimitsDescription": "До нас дошли сведения, что бывшие жильцы заколачивают дома перед отъездом. Для нашей компании не должно быть закрытых дверей. Разберитесь.",
    "QuestInformationLeakDescription": "В мелочной попытке запятнать репутацию компании бывший сотрудник слил информацию о внутренней работе APEX. Ваша задача — вернуть эти материалы в штаб.",
    "QuestScanningTheAreaTitle": "Полевой осмотр",
    "QuestInformationLeakObjectiveTape": "Собрать кассету APEX",
    "QuestNoLimitsObjective": "Вскрыть двери ломом",
    "QuestInformationLeakObjectiveNews": "Собрать газету",
    "QuestCollectingBackObjective": "Вернуть жетоны",
    "QuestCollectingBackDescription": "Жетоны APEX обнаружены на частной территории. Это недопустимо: жетоны компании должны оставаться под контролем. Верните их.",
    "QuestCollectingBackTitle": "Изъятие имущества",
    "QuestInformationLeakTitle": "Утечка информации",
    "QuestDifficultyEasy": "I",
    "QuestDifficultyMedium": "II",
    "QuestDifficultyHard": "III",
    "QuestScanningTheAreaDescription": "APEX требует полного обследования зоны вашего назначения. Исследуйте местность и отметьте всё важное.",
    "QuestScanningTheAreaObjective": "Собрать данные у",
    "QuestBrakeFluidRefillTitle": "Долив торм. жидкости",
    "QuestBrakeFluidRefillDescription": "В двигателе мало тормозной жидкости. Залейте резервуар до красной черты.",
    "QuestBrakeFluidRefillObjective": "Залить тормозную жидкость",
    "QuestSparkPlugsTitle": "Ремонт свечей",
    "QuestSparkPlugsDecription": "Свечи зажигания изношены. Срочно найдите замену.",
    "QuestSparkPlugsObjective": "Заменить свечи",
    "DoorButtonRepairTitle": "Ремонт кнопки двери",
    "DoorButtonRepairDescription": "Почините кнопку двери, чтобы закрыть её и сбежать.",
    "DoorButtonRepairObjective": "Починить кнопку двери",
    "HydraulicHoseRepairTitle": "Ремонт шланга",
    "HydraulicHoseRepairObjective": "Заменить повреждённый шланг",
    "HydraulicHoseRepairDescription": "Замените повреждённый шланг риггера.",
    "SatelliteRepairTitle": "Спутник",
    "SatelliteRepairDecription": "Починить сломанный спутник",
    "SatelliteRepairObjective": "Починить спутник",
    # Items
    "ItemGenericUse": "[{Key}]\u202fИсп.",
    "ItemNewspaperUse": "[{Key}] Удар",
    "ItemNewspaperName": "Газета",
    "ItemCrowbarName": "Лом",
    "ItemSparkPlugsName": "Свечи",
    "ItemBatteryName": "Аккумулятор",
    "ItemCoolantName": "Охлаждающая",
    "ItemOilName": "Масло",
    "ItemFusesName": "Предохранители",
    "ItemFuelName": "Топливо",
    "ItemTiresName": "Шины",
    "ItemBrakeFluidName": "Торм. жидкость",
    # Van
    "SparkPlugsInstall": "Установить свечи",
    "SparkPlugsRemove": "Снять неисправные свечи",
    # HUD
    "EmployeeNumber": "Сотрудник #{Number}",
    "SpectatingTitle": "Наблюдение: #{Number}",
    "SpectatingTitleNoNumber": "Наблюдение",
    "CompassNorth": "С",
    "CompassSouth": "Ю",
    "CompassEast": "В",
    "CompassWest": "З",
    "ThreatLevelMiles": "миль",
    "ThreatLevelKilometers": "км",
    "TornadoCategoryF5": "F5",
    "ThreatLevelTitle": "Угроза:",
    "ThreatLevelDistanceApproximation": "~",
    "RecordingMessage": "REC",
    "MovementRestrictionMessage": "ОБНАРУЖЕНО ОГРАНИЧЕНИЕ ДВИЖЕНИЯ",
    "MovementRestrictionCountdown": "ОСВОБОЖДЕНИЕ ЧЕРЕЗ",
    "MovementRestrictionCountdownFormat": "{CountdownMessage} {Time}...",
    "MonitoringTitle": "Мониторинг: #{Number}",
    "MonitoringTitleNoNumber": "Мониторинг",
    # Moodlets
    "ConsumablesBandagedName": "Перевязан",
    "ConsumablesBandagedDescription": "Мгновенно восстанавливает 30 здоровья.",
    "ConsumablesEnergyDrinkName": "Быстрый",
    "ConsumablesEnergyDrinkDescription": "Скорость передвижения +30%.",
    "ConsumablesEnergyPillsName": "Энергичный",
    "ConsumablesEnergyPillsDescription": "Макс. выносливость +30%.",
    "ConsumablesGranolaBarName": "Сыт",
    "ConsumablesGranolaBarDescription": "Регенерация выносливости +150%.",
    "ConsumablesHealthPillsName": "Под лекарством",
    "ConsumablesHealthPillsDescription": "Восстанавливает 20 здоровья за 10 сек.",
    "ConsumablesMedkitName": "Полевая помощь",
    "ConsumablesMedkitDescription": "Мгновенно восстанавливает 60 здоровья.",
    "TrapDefibShockName": "Шок",
    "TrapDefibShockDescription": "Удар дефибриллятором! Остаётся лёгкое покалывание.",
    "TrapFireDamageName": "В огне!",
    "TrapFireDamageDescription": "5 урона огнём/сек 5 сек. Может перекинуться на команду.",
    "TrapFireDamageNightmareName": "В огне!",
    "TrapFireDamageNightmareDescription": "7.5 урона огнём/сек 5 сек. Может перекинуться на команду.",
    "TrapPowerCableShockName": "Под током",
    "TrapPowerCableShockDescription": "1 эл. урон/сек 5 сек. Может перекинуться на команду.",
    "MoodletAcidName": "В кислоте!",
    "MoodletAcidDescription": "Кислотный дождь.",
    "MoodletAnchoredName": "На якоре",
    "MoodletAnchoredDescription": "Выше сопротивление затягиванию торнадо.",
    "MoodletDrenchedName": "Промок",
    "MoodletDrenchedDescription": "Дождь: −5% скорости и +20% уязвимости к электричеству.",
    "MoodletElectrifiedName": "Под током",
    "MoodletElectrifiedDescription": "1 эл. урон/сек 5 сек. Может перекинуться на команду.",
    "MoodletFireProofName": "Огнестойкость",
    "MoodletFireProofDescription": "Урон огнём −50%.",
    "MoodletHailName": "В граде!",
    "MoodletHailDescription": "Град.",
    "MoodletHeavyItemImmunityName": "Сила",
    "MoodletHeavyItemImmunityDescription": "Можно носить тяжёлое без штрафа к скорости.",
    "MoodletInjuredName": "Ранен",
    "MoodletInjuredDescription": "Штраф к скорости −10%.",
    "MoodletLightningProtectionName": "Иммунитет к молнии",
    "MoodletLightningProtectionDescription": "Иммунитет к ударам молнии.",
    "MoodletOverencumberedName": "Перегруз",
    "MoodletOverencumberedDescription": "Тяжёлый груз: −25% к скорости.",
    "MoodletPaperCutName": "Порез",
    "MoodletPaperCutDescription": "1 урон/сек 3 сек.",
    "MoodletRainProtectionName": "Защита от дождя",
    "MoodletRainProtectionDescription": "Защита от кислоты, града и дождя. Выше шанс попадания молнии.",
    "MoodletVeryInjuredName": "Тяжело ранен",
    "MoodletVeryInjuredDescription": "Штраф к скорости −25%.",
    # Maps
    "MapGreatPlainsName": "Великие равнины",
    "MapInaccessibleName": "Недоступно",
    "MapInaccessibleDescription": "Скоро",
    "MapGreatPlainsDescriptoin": "Скоро",
    "MapMockupName": "Американский пригород",
    "MapMockupDescription": "Этот американский пригород когда-то жил спокойной рутиной. Со временем странные события изменили быт: жестокие бури, торнадо и загрязнение воды вынудили жителей уехать. Когда район опустел, APEX выкупила его для исследований нестабильности среды.",
    # Minigames
    "MatchColorTitleYellow": "Ж",
    "MatchColorTitleGreen": "З",
    "MatchColorTitleBlue": "С",
    "MatchColorTitleRed": "К",
    "NavigableMinigameActionDescription": "Навигация: {Key0}, {Key1}, {Key2}, {Key3}\n\nВзаимодействие: {Key4}",
    "TimingWheelAction": "Взаимод.",
    "TimingLineAction": "Лить",
    "EffortAction": "Усилие",
    "MultiWheelAction": "Крутить",
    "MatchAction": "Смена",
    "LogicAction": "Поворот",
    "GenericActionDescription": "Нажмите {Key0} для взаимодействия",
    # Stats
    "StatGameTime": "Время в игре",
    "StatGamesPlayed": "Пережитые бури",
    "StatVictories": "Сбежал от бури",
    "StatLosses": "Погиб в буре",
    "StatFastestWin": "Быстрейший побег",
    "StatDeaths": "Инциденты в поле",
    "StatRevives": "Полевые спасения",
    "StatUnitDartThrows": "попаданий",
    "StatTimeBurned": "Время в огне",
    "StatTimeInAcid": "Время в кислоте",
    "StatTimeInHail": "Время в граде",
    "StatTokensCollected": "Жетоны собраны",
    "StatTokensSpent": "Жетоны потрачены",
    "StatDistanceWalked": "Пройдено",
    "StatHitByLightning": "Удары молнии",
    "StatDoorsOpened": "Двери вскрыты",
    "StatHitByWire": "Удары током",
    "StatFellIntoSewerPit": "Падения в люки",
    "StatCollectablesRecovered": "Коллекционные",
    "StatBullsEyes": "В яблочко",
    "StatUnitTimes": "раз",
    "StatTornadoesEncountered": "Встречи с торнадо",
    "StatTiresChanged": "Шины заменены",
    "StatMinigamesFailed": "Провалы мини-игр",
    "StatMinigamesSucceeded": "Успехи мини-игр",
    "StatDartsHit": "Попадания дротиками",
    "StatItemsCollected": "Предметы собраны",
    "StatCategoryGeneral": "Общее",
    "StatCategorySurvival": "Выживание",
    "StatCategoryRepairs": "Ремонт",
    "StatCategoryScavenging": "Сбор",
    "StatCategoryExploration": "Исследование",
    "StatCategoryAfterHours": "После смены",
    # VanSchematic new repairs
    "SchematicRepairTitleBrakeFluid": "Долив торм. жидкости",
    "SchematicRepairTitleSparkPlugs": "Замена свечей",
    "SchematicRepairMessageSparkPlugs": "1. Снимите изношенные свечи инструментом;\r\n2. Найдите новый комплект свечей;\r\n3. Установите новые свечи.",
    "SchematicRepairMessageBrakeFluid": "1. Откройте бачок торм. жидкости;\r\n2. Найдите новую бутылку;\r\n3. Залейте в бачок;\r\n4. Закройте бачок.",
    "QuestStatusIncomplete": "НЕВЫПОЛНЕНИЕ МИССИИ ПОВЛЕЧЁТ ДИСЦИПЛИНАРНЫЕ МЕРЫ",
    "QuestStatusCompleted": "МИССИЯ ВЫПОЛНЕНА. РЕЗУЛЬТАТ ЗАФИКСИРОВАН.",
    "QuestObjectivesTitle": "ЦЕЛИ МИССИИ",
    "QuestObjectivesTitleShort": "ЦЕЛИ",
    "QuestCheckDashboardTitle": "Проверить приборную панель",
    "QuestCheckDashboardDescription": "С фургоном что-то не так. Проверьте приборную панель и оцените состояние.",
    "QuestCheckDashboardObjective": "Повернуть ключ",
    "QuestBatteryRepairTitle": "Ремонт аккумулятора",
    "QuestBatteryRepairDescription": "Аккумулятор фургона сел. Немедленно найдите подходящую замену.",
    "QuestBatteryRepairObjective": "Заменить аккумулятор",
    "QuestFusesRepairTitle": "Ремонт предохранителей",
    "QuestFusesRepairDescription": "Предохранители фургона перегорели. Немедленно найдите подходящую замену.",
    "QuestFusesRepairObjective": "Заменить предохранители",
    "QuestTireRepairTitle": "Ремонт шин",
    "QuestTireRepairDescription": "Шины пробиты. Замените их немедленно.",
    "QuestTireRepairObjective": "Заменить шины",
    "QuestCoolantRefillTitle": "Долив охлаждающей жидкости",
    "QuestCoolantRefillDescription": "В двигателе недостаточно охлаждающей жидкости для безопасной работы. Заполните бачок.",
    "QuestCoolantRefillObjective": "Заполнить бачок ОЖ",
    "QuestFuelRefillTitle": "Заправка топлива",
    "QuestFuelRefillDescription": "В двигателе недостаточно топлива. Заполните бак.",
    "QuestFuelRefillObjective": "Заправить бак",
    "QuestOilRefillTitle": "Долив масла",
    "QuestOilRefillDescription": "В двигателе недостаточно масла для безопасной работы. Заполните бачок.",
    "QuestOilRefillObjective": "Заполнить бачок масла",
    "QuestCheckQuestsTitle": "Проверить доску миссий",
    "QuestCheckQuestsDescription": "APEX выдал дополнительные задачи на текущую миссию. Проверьте доску миссий.",
    "QuestCheckQuestsObjective": "Проверить доску миссий",
    # Skins
    "SkinFirefighterName": "Первый уголёк",
    "SkinFirefighterDescription": "Форма «Первый уголёк» сочетает традицию и практичность. Жаростойкий верх в духе классических пожарных костюмов: светоотражающие полосы, огнеупорные панели и усиленная защита локтей и коленей. Создана после ряда «инцидентов» с огнём из‑за погодных явлений.\n\nИдеальна для зон после шторма, завалов и высокотемпературных аномалий. В комплекте — модуль усов для морального духа и традиций.",
    "SkinFirefighterEffect": "Огнестойкий костюм даёт <Positive>на 50% меньше урона от огня</> и <Positive>защищает ближайших союзников от возгорания</>.",
    "SkinDefaultName": "Полевой оперативник",
    "SkinDefaultDescription": "Стандартный штормовой разведкостюм Aerodyne. Рассчитан на мобильность и базовую защиту в сильный ветер.\n\nГерметичный шлем с короткой связью, тонированным визором и съёмной антенной. Стандарт для новичков в опасных секторах.",
    "SkinDefaultEffect": "Лёгкая экипировка <Positive>увеличивает скорость передвижения на 10%</>",
    "SkinSheriffName": "Хранитель порядка",
    "SkinSheriffDescription": "Форма «Хранитель порядка» подчёркивает авторитет и готовность к работе: куртка в стиле рейнджера, удобные брюки и нагрудный значок. Особенно полезна в сельской местности, где закон немного «устарел».\n\nОптика на шляпе поддерживает тепловизор и отслеживание движения. Подходит для поддержания порядка и эвакуации.",
    "SkinSheriffEffect": "Компактная развесовка: <Positive>лом занимает меньше места в инвентаре</> и <Positive>двери открываются быстрее</>.",
    "SkinFirstResponderName": "Линия жизни",
    "SkinFirstResponderDescription": "«Линия жизни» — яркий спасательный костюм Crimson Rescue по образцу элитных бригад. Красный термостойкий корпус заметен в дыму и завалах, усиленные суставы сохраняют подвижность.\n\nШлем с визором, связью и маяком для быстрого поиска пострадавших. Для операций, где важна каждая секунда.",
    "SkinFirstResponderEffect": "Снаряжение экстренной помощи: <Positive>дефибриллятор занимает меньше места</> и <Positive>подсвечивает упавших союзников</>.",
    "SkinUnlockTitle": "КАК ОТКРЫТЬ: ",
    "SkinUnlockRevivePlayers": "Оживить {Number} сотрудников дефибриллятором",
    "SkinUnlockBurnTime": "Гореть в сумме {Number} минут",
    "SkinUnlockUnbarDoors": "Вскрыть ломом {Number} дверей",
    "SkinUnlockConditionFormat": "{Condition} {Progress}",
    # Van schematic
    "SchematicRepairMessageBattery": "1. Отсоедините силовые кабели;\r\n2. Снимите аккумулятор инструментом;\r\n3. Найдите заряженный аккумулятор;\r\n4. Установите заряженный аккумулятор.",
    "SchematicRepairTitleCoolant": "Долив охлаждающей жидкости",
    "SchematicRepairTitleBattery": "Замена аккумулятора",
    "SchematicRepairTitleOil": "Долив масла",
    "SchematicRepairTitleFuses": "Ремонт предохранителей",
    "SchematicRepairTitleTires": "Ремонт шин",
    "SchematicRepairTitleFuel": "Заправка топлива",
    "SchematicGadgetTitleDoors": "Двери",
    "SchematicGadgetTitleVendingMachine": "Vitastation",
    "SchematicGadgetTitleRadar": "Радар",
    "SchematicGadgetTitleRadio": "Рация",
    "SchematicGadgetTitleStorage": "Склад",
    "SchematicGadgetTitleQuestBoard": "Доска миссий",
    "SchematicGadgetTitleTutorialList": "Справочник",
    "SchematicRepairMessageCoolant": "1. Откройте бачок ОЖ;\r\n2. Найдите новую бутылку охлаждающей жидкости;\r\n3. Залейте её в бачок;\r\n4. Закройте бачок.",
    "SchematicRepairMessageOil": "1. Откройте бачок масла;\r\n2. Найдите новую бутылку масла;\r\n3. Залейте её в бачок;\r\n4. Закройте бачок.",
    "SchematicRepairMessageFuses": "1. Извлеките сгоревшие предохранители;\r\n2. Найдите новый комплект;\r\n3. Установите новые предохранители.",
    "SchematicRepairMessageTires": "1. Найдите домкрат;\r\n2. Установите домкрат у колеса;\r\n3. Снимите спущенное колесо инструментом;\r\n4. Найдите новое колесо;\r\n5. Установите новое колесо.",
    "SchematicRepairMessageFuel": "1. Откройте топливный бак;\r\n2. Найдите канистру топлива;\r\n3. Залейте топливо в бак;\r\n4. Закройте бак.",
    "SchematicGadgetMessageDoors": "Вы открыли дверь фургона — отлично! Теперь можно работать. Доберитесь до передней части, чтобы осмотреть двигатель. Нажмите {Key0}, чтобы бежать: время — деньги!",
    "SchematicGadgetMessageVendingMachine": "Перед вами Vitastation — торговый автомат, где можно тратить честно заработанные Apex Tokens на официальную продукцию Apex.",
    "SchematicGadgetMessageRadar": "Следите за доплеровским радаром! Он предупреждает о торнадо и (надеемся) поможет их избежать. Также показывает, где другие сотрудники — живые или нет.",
    "SchematicGadgetMessageRadio": "Связь важна. Чтобы пользоваться рациями, жмите ПКМ для включения/выключения и разговора с командой. Ограничьтесь рабочими темами — например, выживанием.",
    "SchematicGadgetMessageStorage": "Это ящик склада. Сюда нужно приносить все находки: газеты, VHS, документы и прочее, иначе наград не будет — политика компании.",
    "SchematicGadgetMessageQuestBoard": "Готовы к сверхурочным? Нет? Жаль, они обязательны. На доске — побочные цели помимо побега; за них дают доп. награды (и шанс сохранить работу).",
    # Patch 2026-09-11 (buildid 25239041)
    "PlayertLevelShort": "УР.",
    "PlayerListTitle": "// ШТОРМОВАЯ КОМАНДА",
    "GameTimeRandom": "Случайно",
    "GameTimeDay": "День",
    "GameTimeDusk": "Сумерки",
    "GameTimeNight": "Ночь",
    "GameDifficultyEasyDescription": "Дольше раунд, слабее бури и меньше торнадо.",
    "GameDifficultyNormalDescription": "Короче раунд, опаснее бури и крупнее торнадо.",
    "GameDifficultyHardDescription": "Ещё опаснее бури и чаще торнадо.",
    "GameDifficultyNightmareDescription": "Ещё короче раунд, меньше предметов, только опасные бури.",
    "GenericConfirm": "Подтвердить",
    "QuestCompletedToastMessage": "{QuestTitle} {QuestDifficulty}",
    "QuestCompletedToastTitle": "Цель миссии выполнена",
    "SettingOptionValueFormat": "{Prefix}{Num}{Suffix}",
    "ToastTitleFormat": "// {Title}",
    "ItemDefibrillatorName": "Дефибриллятор",
    "ItemDefibrillatorUse": "[{Key}]\u202f(удерж.) Шок",
    "ItemConsumableUse": "[{Key}]\u202fИсп.",
    "ItemBandageName": "Бинт",
    "ItemEnergyDrinkName": "Энергетик",
    "ItemEnergyPillsName": "Энерготаблетки",
    "ItemGranolaBarName": "Батончик",
    "ItemMedkitName": "Аптечка",
    "ItemHealthPillsName": "Таблетки",
    "ItemsDropAction": "[{Key}]\u202fБросить",
    "ItemRadioNameOn": "Вкл. рацию",
    "ItemWalkieTalkieName": "Рация",
    "ItemRadioSpeakAction": "[{Key}]\u202fГоворить",
    "ItemRadioMicrophoneName": "Микрофон рации",
    "ItemDartName": "Дротик",
    "ItemDartUse": "[{Key}]\u202fБросок",
    "ItemGenericToggle": "[{Key}]\u202fВкл/Выкл",
    "ItemRadioNameOff": "Выкл. рацию",
    "ItemFlashlightName": "Фонарик",
    "ItemFlashlightBigName": "Большой фонарь",
    "ItemPocketRadarName": "Карманный радар",
    "ItemPocketRadarUse": "[{Key}]\u202fЗум",
    "ItemUmbrellaName": "Зонт",
    "ItemPortableConductorName": "Громоотвод",
    "ItemDartContainerName": "Дротики",
    "ItemTokenBundleName": "Жетоны APEX",
    "ItemCassetteName": "Кассета APEX",
    "ItemTapeName": "Плёнка APEX",
    "ItemDocumentName": "Документ APEX",
    "HoldToSkip": "УДЕРЖИТЕ, ЧТОБЫ ПРОПУСТИТЬ",
    "Skipped": "ПРОПУЩЕНО",
    "VanStatusDamaged": "Повреждён",
    "VanStatusReady": "Готов",
    "VanStatusOnline": "Онлайн",
    "VanStatusTitle": "Состояние фургона",
    "VanStatusEngine": "Двигатель",
    "VanStatusExterior": "Кузов",
    "VanStatusCommunication": "Связь",
    "VanStatusCheck": "Проверка",
    "MuddyName": "В грязи",
    "MuddyMoodletDescription": "Скорость −10%",
    "PostGameDataReport": "Отчёт",
    "PostGameDataSummary": "Итог",
    "PostGameDataContinue": "Далее",
    "PostGameDataLeaveSession": "Выйти из сессии",
    "PostGameDataAutoContinue": "Авто-далее",
    "PostGameDataReportStatusAlive": "Жив",
    "PostGameDataReportCrew": "Штормовая команда",
    "PostGameDataReportStatusDead": "Погиб",
    "PostGameDataReportStatusNone": "Пропал",
    "PostGameDataMatchDataTitle": "// КРАТКИЙ ОТЧЁТ",
    "PostGameDataMatchDataTornadoesObserved": "Замечено торнадо",
    "PostGameDataMatchDataStormsExperienced": "Пережитые бури",
    "PostGameDataMatchDataFieldIncidents": "Инциденты в поле",
    "PostGameDataRewardLevelTitle": "// УРОВЕНЬ",
    "PostGameDataRewardLevelExperience": "[{Current}/{Required}]",
    "RewardListBaseConstantText": "Контракт выполнен",
    "RewardListTimeBonusText": "Оценка по времени",
    "RewardListTeamSizeScalerText": "Доля команды",
    "RewardListVictoryMultiplierText": "Бонус за сохранность фургона",
    "RewardListTeamSurvivalMultiplierText": "Бонус за полный состав",
    "RewardListCompletedQuestShareText": "Бонус за цели миссии",
    "RewardListFailedQuestPenaltyText": "Штраф за незакрытые цели",
    "RewardListReviveBonusText": "Бонус за полевые спасения",
    "RewardListDeathPenaltyText": "Штраф за пропавших",
    "RewardListCollectableBonusText": "Бонус за секретные материалы",
    "RewardListVanRepairRewardBatteryRepair": "Бонус: аккумулятор",
    "RewardListVanRepairRewardFusesRepair": "Бонус: предохранители",
    "RewardListVanRepairRewardSparkPlugsRepair": "Бонус: свечи",
    "RewardListVanRepairRewardTireRepair": "Бонус: шины",
    "RewardListVanRepairRewardCoolantRefill": "Бонус: охлаждение",
    "RewardListVanRepairRewardFuelRefill": "Бонус: топливо",
    "RewardListVanRepairRewardOilRefill": "Бонус: масло",
    "RewardListVanRepairRewardBrakeFluidRefill": "Бонус: торм. жидкость",
    "RewardListVanRepairPenaltyBatteryRepair": "Штраф: севший аккумулятор",
    "RewardListVanRepairPenaltyFusesRepair": "Штраф: предохранители",
    "RewardListVanRepairPenaltySparkPlugsRepair": "Штраф: износ свечей",
    "RewardListVanRepairPenaltyTireRepair": "Штраф: пробитые шины",
    "RewardListVanRepairPenaltyCoolantRefill": "Штраф: мало ОЖ",
    "RewardListVanRepairPenaltyFuelRefill": "Штраф: мало топлива",
    "RewardListVanRepairPenaltyOilRefill": "Штраф: мало масла",
    "RewardListVanRepairPenaltyBrakeFluidRefill": "Штраф: мало торм. жидкости",
    "PostGameDataRewardListTitle": "// ОТЧЁТ О РЕЗУЛЬТАТАХ",
    "PostGameDataRewardListFinalRating": "Итоговая оценка",
    "PostGameDataRewardListYourBalance": "Ваш баланс",
    "PostGameDataRewardListRequiredExperience": "/{RequiredXP}",
    "PostGameDataRewardListNumberPositive": "+{Number}",
    "PostGameDataRewardListNumberNegative": "-{Number}",
    "PostGameDataRewardListNumber": "{Number}",
    "TermsLine3.1": "\nПрочтите наши ",
    "TermsLine3.3": "\nперед игрой в FUNNEL RUNNERS.",
    "TermsLine2.1": "Вы можете прочитать нашу ",
    "TermsLine2.2": "ПОЛИТИКУ КОНФИДЕНЦИАЛЬНОСТИ",
    "TermsTitle": "Конфиденциальность и условия",
    "TermsLine2.3": " чтобы узнать о наших правилах конфиденциальности.",
    "TermsLine3.2": "\nУСЛОВИЯ ИСПОЛЬЗОВАНИЯ",
    "TermsLine1": "SUPERNOVA studios обрабатывает голосовой чат через сторонний сервис для FUNNEL RUNNERS.",
    "TermsConfirm": "Понятно",
    "WeatherDisplayIntensityMedium": "Умерен. ",
    "WeatherDisplayIntensityHeavy": "Сильн. ",
    "WeatherDisplayStormNameFormat": "{Intensity}{StormName}",
    "DopplerRadarUpdateData": "Обновить данные",
    "DopplerRadarTitle": "Доплер-радар",
    "DopplerRadarMachineStarted": "Машина запущена",
    "DopplerRadarStatusReport": "// ОТЧЁТ О СОСТОЯНИИ...",
    "WeatherDisplayIntensityLight": "Слаб. ",
    "WeatherDisplayStormNameRain": "буря",
    "WeatherDisplayStormNameAcid": "кислотная буря",
    "WeatherDisplayStormNameElectric": "электрическая буря",
    "WeatherDisplayStormNameHail": "град",
    "WeatherDisplayPlayerDeathFormat": "Сотрудник у {0} потерял сознание.",
    "WeatherDisplayStormForecastMessageFormat": "Формируется {0}.",
    "WeatherDisplayStormStartMessageFormat": "Началась {0}.",
    "WeatherDisplayStormIntensifyMessageFormat": "{0} усиливается.",
    "WeatherDisplayStormWeakenMessageFormat": "{0} слабеет.",
    "WeatherDisplayStormEndMessageFormat": "{0} стихла.",
    "WeatherDisplaySmallTornadoName": "торнадо F-2",
    "WeatherDisplayMediumTornadoName": "торнадо F-3",
    "WeatherDisplayBigTornadoName": "торнадо F-4",
    "WeatherDisplayFinalTornadoName": "торнадо F-5",
    "WeatherDisplayTornadoForecastMessageFormat": "{0} формируется у {1}.",
    "WeatherDisplayTornadoSpawnMessageFormat": "{0} появился у {1} и движется {2}.",
    "WeatherDisplayTornadoDeviationMessageFormat": "{0} у {1} поворачивает {2}.",
    "WeatherDisplayTornadoDecayMessageFormat": "{0} у {1} рассеивается.",
    "CrewAssemblyTitle": "Инфо сессии",
    "CrewAssemblyStartGame": "Старт",
    "CrewAssemblyInvite": "Пригласить напарника",
    "CrewAssemblyOptionsApply": "Применить",
    "CrewAssemblyOptionsNone": "Без изменений",
    "LobbyInfoSessionName": "Имя сессии:",
    "LobbyInfoJoinPermission": "Доступ:",
    "LobbyInfoMaximumPlayers": "Макс. игроков:",
    "LobbyInfoTimeOfDay": "Время суток:",
    "LobbyInfoDifficulty": "Сложность:",
    "LobbyInfoDifficultyUnlocksAt": "С уровня {N}",
    "LobbyInfoMaxPlayersValue": "{N} ИГРОКОВ",
    "LobbyInfoJoinPermissionPublic": "МОЖЕТ ЗАЙТИ ЛЮБОЙ",
    "LobbyInfoJoinPermissionFriendsOnly": "ТОЛЬКО ДРУЗЬЯ",
    "LobbyInfoJoinPermissionInviteOnly": "ТОЛЬКО ПО ПРИГЛАШЕНИЮ",
    "EmotePoint": "Указать",
    "EmoteItalianFYou": "Пошёл ты",
    "EmoteHandWave": "Махнуть",
    "EmoteNo": "Нет",
    "EmoteRPS": "Камень-ножницы-бумага",
    "EmoteSalute": "Салют",
    "EmoteRagdoll": "Рагдолл",
    "EmoteYes": "Да",
    "EmoteTornadoDance": "Танец торнадо",
    "VirtualKeyboardSpace": "Пробел",
    "VirtualKeyboardBackspace": "Стереть",
    "VirtualKeyboardDone": "Готово",
    "VirtualKeyboardCancel": "Отмена",
    "VirtualKeyboardShift": "Shift",
    "CompanyVaultTitle": "ХРАНИЛИЩЕ КОМПАНИИ",
    "CompanyVaultFilesTitle": "// ФАЙЛЫ",
    "CompanyVaultArchiveDisplayMissingImage": "[ ИЗОБРАЖЕНИЕ НЕ НАЙДЕНО ]",
    "CompanyVaultArchiveDisplayDate": "<Bold>Дата: {Date}</>",
    "CompanyVaultArchiveButtonTitle": "Архив_{N}",
    "CompanyVaultArchiveButtonTitleNew": "НОВОЕ!",
    "CompanyVaultArchivesUnlocked": "{Current}/{Total}",
    "VendingMachineCheckoutTotal": "Сумма",
    "VendingMachineInfoDetails": "Подробнее",
    "VendingMachineItemUnlocksAt": "С УРОВНЯ {N}",
    "VendingMachineTitle": "Витастанция",
    "VendingMachineCheckout": "Оформить заказ",
    "VendingMachineProcessing": "Обработка платежа",
    "VendingMachineAddToCart": "В корзину",
    "VendingMachineUpdateCart": "Обновить корзину",
}

_extra = Path(r"C:\Mods\FunnelRunners_RU\translations\st_extra_ru.json")
if _extra.exists():
    RU.update(json.loads(_extra.read_text(encoding="utf-8")))


def read_fstring(data: bytes, pos: int):
    ln = struct.unpack_from("<i", data, pos)[0]
    pos += 4
    if ln == 0:
        return "", pos, False
    if ln < 0:
        n = -ln
        raw = data[pos : pos + n * 2]
        pos += n * 2
        return raw.decode("utf-16-le").rstrip("\x00"), pos, True
    raw = data[pos : pos + ln]
    pos += ln
    return raw.decode("utf-8", errors="replace").rstrip("\x00"), pos, False


def write_fstring_ansi(s: str) -> bytes:
    b = s.encode("utf-8") + b"\x00"
    return struct.pack("<i", len(b)) + b


def write_fstring_utf16(s: str) -> bytes:
    # Normalize newlines to match game (\r\n often used in schematic messages)
    b = s.encode("utf-16-le") + b"\x00\x00"
    n = len(b) // 2
    return struct.pack("<i", -n) + b


def find_namespace_start(data: bytes, name: str) -> int:
    marker = name.encode("ascii")
    for i in range(len(data) - len(marker)):
        if (
            data[i : i + len(marker)] == marker
            and i >= 4
            and struct.unpack_from("<i", data, i - 4)[0] == len(marker) + 1
        ):
            return i - 4
    raise RuntimeError(f"namespace not found: {name}")


def find_serial_field(data: bytes, str_start: int) -> tuple[int, int]:
    """Return (offset, old_serial_size) for export serial size uint64 lo/hi=0."""
    best = None
    for i in range(0, str_start - 8, 4):
        lo = struct.unpack_from("<I", data, i)[0]
        hi = struct.unpack_from("<I", data, i + 4)[0]
        if hi == 0 and 50 < lo < len(data):
            best = (i, lo)
    if best is None:
        raise RuntimeError("serial size field not found")
    return best


def rebuild_table(name: str, data: bytes) -> bytes:
    start = find_namespace_start(data, name)
    serial_off, old_serial = find_serial_field(data, start)

    pos = start
    ns, pos, _ = read_fstring(data, pos)
    count = struct.unpack_from("<i", data, pos)[0]
    pos += 4
    entries = []
    for _ in range(count):
        key, pos, _ = read_fstring(data, pos)
        val, pos, _ = read_fstring(data, pos)
        entries.append((key, val))
    tail = data[pos:]
    prefix = data[:start]

    out = bytearray(prefix)
    out += write_fstring_ansi(ns)
    out += struct.pack("<i", count)
    missing = []
    for key, old in entries:
        new = RU.get(key, old)
        if key not in RU:
            missing.append(key)
        out += write_fstring_ansi(key)
        if any(ord(ch) > 127 for ch in new):
            out += write_fstring_utf16(new)
        else:
            out += write_fstring_ansi(new)
    out += tail

    delta = len(out) - len(data)
    new_serial = old_serial + delta
    struct.pack_into("<I", out, serial_off, new_serial)

    # Optional cooked-size field seen on some packages (len + 56)
    v14 = struct.unpack_from("<I", out, 0x14)[0]
    if v14 == len(data) + 56:
        struct.pack_into("<I", out, 0x14, len(out) + 56)

    print(
        f"{name}: {len(data)} -> {len(out)} (delta {delta}), "
        f"serial @{serial_off:#x} {old_serial}->{new_serial}, "
        f"entries {count}, missing_tr {len(missing)}"
    )
    if missing:
        print("  missing keys:", ", ".join(missing))
    return bytes(out)


def ensure_chunks() -> None:
    CHUNKS.mkdir(parents=True, exist_ok=True)
    for cid, name in TABLES.items():
        dest = CHUNKS / f"{name}.bin"
        if not dest.exists() or dest.stat().st_size == 0:
            subprocess.check_call([str(RETOC), "get", str(GAME_UTOC), cid, str(dest)])


def main() -> None:
    ensure_chunks()

    # Seed raw layout from existing working popups raw_mod (has ContainerHeader template),
    # then replace with multi-package container via retoc to-zen of a temp legacy pak? 
    # Simpler: pack each chunk into one pack-raw by regenerating container via retoc.
    #
    # Approach: build legacy pak with all rebuilt assets... can't easily.
    # Use pack-raw with multiple ExportBundleData chunks + one ContainerHeader.
    #
    # Generate ContainerHeader by running to-zen on a multi-file legacy pak of
    # ORIGINAL assets first, then replace chunk bytes with rebuilt ones.

    # 1) Rebuild all binaries
    rebuilt: dict[str, bytes] = {}
    for cid, name in TABLES.items():
        src = (CHUNKS / f"{name}.bin").read_bytes()
        rebuilt[cid] = rebuild_table(name, src)

    # 2) Create temporary legacy pak from ORIGINAL extracted legacy assets (for header),
    #    convert to zen to get a valid multi-package ContainerHeader, then swap chunk payloads.
    extract_loc = Path(
        r"C:\Mods\FunnelRunners_RU\extract\StormEscape\Content\StormEscape\Data\Localization"
    )
    pack_root = Path(r"C:\Mods\FunnelRunners_RU\pack_all_st\FunnelRunners_RU_P")
    if pack_root.exists():
        shutil.rmtree(pack_root)
    loc_dst = pack_root / "StormEscape" / "Content" / "StormEscape" / "Data" / "Localization"
    loc_dst.mkdir(parents=True)
    for name in TABLES.values():
        for ext in (".uasset", ".uexp"):
            src = extract_loc / f"{name}{ext}"
            if not src.exists():
                raise SystemExit(f"missing extracted {src}")
            shutil.copy2(src, loc_dst / f"{name}{ext}")

    repak = Path(r"C:\Mods\FunnelRunners_RU\tools\repak\repak.exe")
    tmp_pak = Path(r"C:\Mods\FunnelRunners_RU\out_all_loc_tmp.pak")
    subprocess.check_call(
        [
            str(repak),
            "pack",
            str(pack_root),
            str(tmp_pak),
            "--version",
            "V11",
            "--path-hash-seed",
            str(0x2B03AD40),
            "-q",
        ]
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    tmp_utoc = OUT / "_tmp.utoc"
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "to-zen",
            "--version",
            "UE5_5",
            str(tmp_pak),
            str(tmp_utoc),
        ]
    )

    # unpack-raw tmp, replace chunk payloads with rebuilt game-format chunks
    if RAW.exists():
        shutil.rmtree(RAW)
    subprocess.check_call([str(RETOC), "unpack-raw", str(tmp_utoc), str(RAW)])

    # Map chunk files: names are chunk ids
    chunk_dir = RAW / "chunks"
    replaced = 0
    for cid, blob in rebuilt.items():
        # find file that starts with cid prefix (retoc may use full id)
        matches = list(chunk_dir.glob(f"{cid}*")) + list(chunk_dir.glob(cid))
        # also exact
        target = chunk_dir / cid
        if target.exists():
            target.write_bytes(blob)
            replaced += 1
            continue
        # try without type suffix variations
        found = False
        for p in chunk_dir.iterdir():
            if p.name.startswith(cid[:16]) or cid.startswith(p.name[:16]):
                # Prefer exact ExportBundleData ids from TABLES
                if p.name == cid or p.name.startswith(cid):
                    p.write_bytes(blob)
                    replaced += 1
                    found = True
                    break
        if not found:
            # list and match by known ids
            for p in chunk_dir.iterdir():
                if p.name == cid:
                    p.write_bytes(blob)
                    replaced += 1
                    found = True
                    break
        if not found:
            print("WARN: chunk not in raw:", cid, "files:", [p.name for p in chunk_dir.iterdir()])

    print("replaced chunks:", replaced, "/", len(rebuilt))
    print("raw chunks:", sorted(p.name for p in chunk_dir.iterdir()))

    # For each table cid, force-write if present
    for cid, blob in rebuilt.items():
        p = chunk_dir / cid
        if p.exists():
            p.write_bytes(blob)

    final_utoc = OUT / "FunnelRunners_RU_P.utoc"
    # remove tmp zen outputs first
    for p in OUT.glob("_tmp*"):
        p.unlink()
    subprocess.check_call(
        [
            str(RETOC),
            "--override-container-header-version",
            "SoftPackageReferencesOffset",
            "pack-raw",
            str(RAW),
            str(final_utoc),
        ]
    )

    # pack-raw may omit .pak; UE still needs a same-named stub to mount the IoStore pair
    stub_pak = OUT / "FunnelRunners_RU_P.pak"
    if not stub_pak.exists():
        for candidate in (
            Path(r"C:\Mods\FunnelRunners_RU\out_raw\FunnelRunners_RU_P.pak"),
            Path(r"C:\Mods\FunnelRunners_RU\out_orig\FunnelRunners_RU_P.pak"),
        ):
            if candidate.exists():
                shutil.copy2(candidate, stub_pak)
                break

    # Install
    for ext in (".pak", ".utoc", ".ucas"):
        old = PAKS / f"FunnelRunners_RU_P{ext}"
        if old.exists():
            old.unlink()
    for p in OUT.iterdir():
        if p.name.startswith("FunnelRunners_RU_P") and p.suffix in {".pak", ".utoc", ".ucas"}:
            shutil.copy2(p, PAKS / p.name)
            print("installed", p.name, p.stat().st_size)

    subprocess.check_call([str(RETOC), "info", str(PAKS / "FunnelRunners_RU_P.utoc")])
    subprocess.check_call([str(RETOC), "verify", str(PAKS / "FunnelRunners_RU_P.utoc")])
    print("DONE")


if __name__ == "__main__":
    main()
