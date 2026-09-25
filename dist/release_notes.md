## Summary
- Tested on the game patch from **2026-09-25** (Steam buildid **25496102**, PATCH NOTES #013 Session Codes).
- Rebuild required: the patch replaced the base pak and moved settings text into String Tables (`SettingsData` 38102→32273). Older RU packs (**v0.1.20** and below) do not match this build.
- New/expanded ST: `ST_Settings`, `ST_Input`, `ST_SessionLobby`, `ST_Interactables` — session codes, door prompts, split mouse/controller look, tutorial subtitle toggle, player name indicators, keybinds.
- Tutorial video subtitles (`LS_TutorialVideoSubtitles`, same-size UI patch).
- World textures overlay kept (bulk sizes still match).
- Unsupported; source is free to use.

## Install
Download the zip → run `Install.bat` → launch via Steam.

If you had **v0.1.20** (or older) installed: run `Uninstall.bat` (or delete `StormEscape-Windows.pak.bak_ru`), then Steam **Verify integrity of game files**, then `Install.bat`. The old `.bak_ru` is from a previous game build.

## Uninstall
`Uninstall.bat`
