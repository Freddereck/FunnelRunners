# -*- coding: utf-8 -*-
import json
from pathlib import Path

d = json.loads(Path(r"C:\Mods\FunnelRunners_RU\translations\lore_extract.json").read_text(encoding="utf-8"))
out_dir = Path(r"C:\Mods\FunnelRunners_RU\translations")

SKIP_SUB = ("Anim", "Overlay", "Border", "Noise", "Fade", "Widget", "BPTYPE", "BP_")
SKIP_EXACT = {"DT_LoreArchives", "Achievements", "W_Header", "BackAction"}

for name in [
    "W_LoadingScreen",
    "W_LoreUI",
    "DA_GameplayMaps",
    "W_CrewLobbyInfo",
    "W_ArchiveDocDisplay",
    "DT_LoreArchives",
    "DT_Achievements",
]:
    parts = []
    for r in d[name]:
        s = r["en"]
        if r["enc"] == "ansi":
            if len(s) < 5:
                continue
            if any(x in s for x in SKIP_SUB) or s in SKIP_EXACT:
                continue
            if s.startswith("ACH_") or s.startswith("stat_") or s.endswith("_Name") or s.endswith("_Desc"):
                continue
            if s.endswith("_Title") or s.endswith("_Content") or s.endswith("_DocumentDate"):
                continue
        parts.append(
            f"enc={r['enc']} max={r.get('max_utf16')} even={r.get('even')} pay={r.get('payload')} len={len(s)}\n{s}"
        )
    (out_dir / f"_dump_{name}.txt").write_text("\n---\n".join(parts), encoding="utf-8")
    print("wrote", name, len(parts))

for name, rows in d.items():
    for r in rows:
        if "Interview" in r["en"] or r["en"].startswith("Nathan Pearson"):
            print(name, r["enc"], "max", r.get("max_utf16"), "even", r.get("even"), "len", len(r["en"]))
            print(" ", r["en"][:100])
