@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Funnel Runners - RU Localization Uninstaller

echo.
echo  Removing Funnel Runners RU packs...
echo.

set "GAME="
if exist "%ProgramFiles(x86)%\Steam\steamapps\common\Funnel Runners\StormEscape\Content\Paks\" set "GAME=%ProgramFiles(x86)%\Steam\steamapps\common\Funnel Runners"
if not defined GAME if exist "%ProgramFiles%\Steam\steamapps\common\Funnel Runners\StormEscape\Content\Paks\" set "GAME=%ProgramFiles%\Steam\steamapps\common\Funnel Runners"
if not defined GAME (
  set "STEAM="
  for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Valve\Steam" /v SteamPath 2^>nul') do set "STEAM=%%B"
  if defined STEAM (
    set "STEAM=!STEAM:/=\!"
    if exist "!STEAM!\steamapps\common\Funnel Runners\StormEscape\Content\Paks\" set "GAME=!STEAM!\steamapps\common\Funnel Runners"
  )
)
if not defined GAME (
  for %%D in (C D E F G H I J) do (
    if not defined GAME if exist "%%D:\SteamLibrary\steamapps\common\Funnel Runners\StormEscape\Content\Paks\" set "GAME=%%D:\SteamLibrary\steamapps\common\Funnel Runners"
  )
)
if not defined GAME (
  echo Enter path to Funnel Runners folder:
  set /p "GAME=Path: "
)
if not exist "!GAME!\StormEscape\Content\Paks\" (
  echo [ERROR] Invalid path
  pause
  exit /b 1
)

set "DEST=!GAME!\StormEscape\Content\Paks"
del /Q "!DEST!\FunnelRunners_RU_P.*" 2>nul
del /Q "!DEST!\FunnelRunners_RU_UI_P.*" 2>nul
del /Q "!DEST!\FunnelRunners_RU_Fonts_P.*" 2>nul
del /Q "!DEST!\zz_FunnelRunners_RU_Fonts_P.*" 2>nul
del /Q "!DEST!\StormEscape-Windows_P.*" 2>nul

if exist "!DEST!\StormEscape-Windows.pak.bak_ru" (
  echo Restoring original StormEscape-Windows.pak ...
  copy /Y "!DEST!\StormEscape-Windows.pak.bak_ru" "!DEST!\StormEscape-Windows.pak" >nul
  del /Q "!DEST!\StormEscape-Windows.pak.bak_ru" 2>nul
)

echo Done.
pause
exit /b 0
