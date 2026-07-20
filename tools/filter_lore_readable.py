# -*- coding: utf-8 -*-
import json
from pathlib import Path

d = json.loads(Path(r"C:\Mods\FunnelRunners_RU\translations\lore_extract.json").read_text(encoding="utf-8"))
lines = []
for name, rows in d.items():
    lines.append(f"==== {name}")
    for r in rows:
        s = r["en"]
        if r["enc"] == "ansi" and len(s) >= 4:
            if s.startswith("/") or "Widget" in s or "Blueprint" in s:
                continue
            if "_Name" in s or "_Desc" in s or s.endswith("_Title") or s.endswith("_Content"):
                continue
            if s.endswith("_DocumentDate") or (len(s) == 32 and s.isalnum()):
                continue
            mx = r.get("max_utf16")
            lines.append(f"  [A] max={mx} even={r.get('even')} pay={r.get('payload')} | {s[:220]}")
        elif r["enc"] == "utf16" and len(s) >= 4:
            if sum(1 for c in s if c.isalpha()) < 3:
                continue
            lines.append(f"  [U] len={r['max_utf16']} | {s[:220]}")
out = Path(r"C:\Mods\FunnelRunners_RU\translations\lore_readable.txt")
out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out, "lines", len(lines))
