@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Funnel Runners - RU Localization Installer

echo.
echo  ============================================
echo   Funnel Runners - Russian localization
echo   Localization: mderick.dev
echo   Tested on game patch 0.34.28
echo   UNSUPPORTED - use at your own risk
echo  ============================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PAKS_SRC=%SCRIPT_DIR%Paks"
if not exist "%PAKS_SRC%\FunnelRunners_RU_P.utoc" (
  echo [ERROR] Paks folder not found. Extract the RELEASE zip fully.
  echo https://github.com/Freddereck/FunnelRunners/releases/latest
  pause
  exit /b 1
)
if not exist "%PAKS_SRC%\FunnelRunners_RU_UI_P.utoc" (
  echo [ERROR] Missing Paks\FunnelRunners_RU_UI_P.utoc
  pause
  exit /b 1
)
if not exist "%PAKS_SRC%\StormEscape-Windows.pak" (
  echo [ERROR] Missing Paks\StormEscape-Windows.pak ^(fonts^)
  pause
  exit /b 1
)

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
echo Installing to:
echo   !DEST!
echo.

REM Remove leftover font overlay experiments
del /Q "!DEST!\FunnelRunners_RU_Fonts_P.*" 2>nul
del /Q "!DEST!\zz_FunnelRunners_RU_Fonts_P.*" 2>nul
del /Q "!DEST!\StormEscape-Windows_P.*" 2>nul

REM Backup original base pak once, then install font-patched pak
if not exist "!DEST!\StormEscape-Windows.pak.bak_ru" (
  if exist "!DEST!\StormEscape-Windows.pak" (
    echo Backing up StormEscape-Windows.pak -^> .bak_ru ...
    copy /Y "!DEST!\StormEscape-Windows.pak" "!DEST!\StormEscape-Windows.pak.bak_ru" >nul
  )
)
echo Installing font-patched StormEscape-Windows.pak ...
copy /Y "%PAKS_SRC%\StormEscape-Windows.pak" "!DEST!\StormEscape-Windows.pak" >nul

copy /Y "%PAKS_SRC%\FunnelRunners_RU_P.pak" "!DEST!\" >nul
copy /Y "%PAKS_SRC%\FunnelRunners_RU_P.utoc" "!DEST!\" >nul
copy /Y "%PAKS_SRC%\FunnelRunners_RU_P.ucas" "!DEST!\" >nul
copy /Y "%PAKS_SRC%\FunnelRunners_RU_UI_P.pak" "!DEST!\" >nul
copy /Y "%PAKS_SRC%\FunnelRunners_RU_UI_P.utoc" "!DEST!\" >nul
copy /Y "%PAKS_SRC%\FunnelRunners_RU_UI_P.ucas" "!DEST!\" >nul

echo Checking...
set "MISSING=0"
for %%F in (
  FunnelRunners_RU_P.pak FunnelRunners_RU_P.utoc FunnelRunners_RU_P.ucas
  FunnelRunners_RU_UI_P.pak FunnelRunners_RU_UI_P.utoc FunnelRunners_RU_UI_P.ucas
  StormEscape-Windows.pak
) do (
  if not exist "!DEST!\%%F" (echo   [MISSING] %%F & set "MISSING=1") else (echo   [OK] %%F)
)
echo.
if "!MISSING!"=="1" (echo Install failed. & pause & exit /b 1)
echo Done. Launch via Steam.
echo Tested on game patch 0.34.28 - newer game builds may break.
echo After Steam "Verify game files" run Install.bat again.
echo This mod is UNSUPPORTED.
pause
exit /b 0
