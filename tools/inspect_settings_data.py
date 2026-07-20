"""Inspect SettingsData for FText / StringTable references vs hardcoded strings."""
from __future__ import annotations

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = pathlib.Path(
    r"C:\Mods\FunnelRunners_RU\extract\StormEscape\Content\StormEscape\Data\Settings\SettingsData.uexp"
)
data = p.read_bytes()

# Find StringTable / ST_ references
for m in re.finditer(rb"ST_[A-Za-z0-9_]+|/Game/StormEscape/Data/Localization/[A-Za-z0-9_]+", data):
    print("REF", m.group().decode("ascii", errors="ignore"), "@", hex(m.start()))

# Extract readable ASCII sentences
print("\n--- readable strings ---")
i = 0
n = len(data)
seen = set()
while i + 4 <= n:
    ln = int.from_bytes(data[i : i + 4], "little", signed=True)
    if 3 <= ln <= 300 and i + 4 + ln <= n:
        raw = data[i + 4 : i + 4 + ln]
        if raw.endswith(b"\x00") and all(32 <= b < 127 or b in (9, 10, 13) for b in raw[:-1]):
            s = raw[:-1].decode("ascii")
            if s not in seen and (" " in s or s.endswith((".", "!", "?"))) and not s.startswith("/"):
                # skip GUIDs-ish and property noise
                if not re.fullmatch(r"[0-9A-F]{32}", s) and "Property" not in s:
                    seen.add(s)
                    print(s[:160])
            i += 4 + ln
            continue
    i += 1

print(f"\nunique readable: {len(seen)}")
