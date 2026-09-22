# Funnel Runners — русская локализация (неофициальная)

**Localization:** [mderick.dev](https://mderick.dev/?utm_source=funnelrunners_ru&utm_medium=github_readme&utm_campaign=v0_1_20&utm_content=readme#services)

Для стримеров: [robinsystem.live](https://robinsystem.live/?utm_source=funnelrunners_ru&utm_medium=github_readme&utm_campaign=v0_1_20&utm_content=readme) — сервис, который поддерживает локализацию.

## Совместимость

**Проверено на хотфиксе игры от 22.09.2026** (Steam buildid `25444214`).

На версиях **новее** — может не работать (краш при старте, битый UI, снова `?????`). После обновления игры почти всегда нужен новый релиз мода.

Старые релизы мода (**v0.1.19** и ниже) на этом хотфиксе **не ставить** — только **v0.1.20+**.

## Поддержка не оказывается

Этот русификатор **не поддерживается**.

- Баги, краши, `?????`, белые экраны, поломки после патча игры — разбирайте сами.
- Issues / просьбы «почините» можно не писать: ответа не будет.
- Исходный код в репозитории — **используйте как хотите**: форки, правки, свои сборки, гайды.

Лицензия: см. [LICENSE](LICENSE) (MIT). Контент самой игры Funnel Runners принадлежит правообладателям.

## Ограничения (важно)

- Часть длинных строк в UI — **транслит латиницей** (ANSI-слоты нечётной длины нельзя безопасно заполнить UTF-16).
- Установщик подменяет `StormEscape-Windows.pak` (шрифты → DroidSansFallback) и сохраняет оригинал как `.bak_ru`.
- После **Verify integrity of game files** в Steam мод нужно ставить снова (`Install.bat`).

## Скачивать только из Releases

https://github.com/Freddereck/FunnelRunners/releases/latest

Не используйте **Code → Download ZIP** как установщик — там нет готовых `.pak` / `.utoc` / `.ucas`.

## Установка

1. Скачайте `FunnelRunners_RU_vX.Y.Z.zip` из Releases  
2. Распакуйте  
3. Если стоял старый RU-пак — сначала `Uninstall.bat` (или удалите `StormEscape-Windows.pak.bak_ru`), затем Steam → **Verify integrity of game files**
4. Запустите `Install.bat`  
5. Запустите игру через Steam  

## Удаление

`Uninstall.bat` (восстанавливает оригинальный `StormEscape-Windows.pak` из `.bak_ru`).

## Что в релизе

- `FunnelRunners_RU_P` — String Tables  
- `FunnelRunners_RU_UI_P` — UI / Data (same-size патч)  
- `FunnelRunners_RU_TX_P` — текстуры в мире (доска, постеры, предметы в фургоне)  
- `StormEscape-Windows.pak` — шрифты UI с кириллицей (подмена базового пака)

## Исходники

В репозитории: скрипты сборки (`tools/`), карты перевода (`translations/`), установщики.

Сборка у себя — на ваш страх и риск. Подсказок по окружению и retoc в рамках поддержки не будет.
