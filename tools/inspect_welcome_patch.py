from __future__ import annotations

import json
import struct
from pathlib import Path

base = Path(r"C:\Mods\FunnelRunners_RU\chunks_ui\W_Welcome_base.bin").read_bytes()
ui = Path(r"C:\Mods\FunnelRunners_RU\chunks_ui\W_Welcome_ui.bin").read_bytes()
mapping = json.loads(
    Path(r"C:\Mods\FunnelRunners_RU\translations\ui_ru_map.json").read_text(encoding="utf-8")
)
report: list[str] = []
report.append(f"sizes {len(base)} {len(ui)} same={len(base)==len(ui)}")

keys = [
    k
    for k in mapping
    if any(
        x in k
        for x in (
            "vehicle is broken",
            "Welcome {Employee}",
            "Hide Tutorial",
            "APEX internal broadcast",
            "Service Schematic poster",
        )
    )
]


def find_fstring(data: bytes, text: str):
    raw = text.encode("ascii") + b"\x00"
    blob = struct.pack("<i", len(raw)) + raw
    i = data.find(blob)
    if i >= 0:
        return "ansi", i, len(blob)
    raw = text.encode("utf-16-le") + b"\x00\x00"
    units = len(raw) // 2
    blob = struct.pack("<i", -units) + raw
    i = data.find(blob)
    if i >= 0:
        return "u16", i, len(blob)
    i = data.find(text.encode("ascii"))
    return "loose", i, None


for k in keys:
    report.append("")
    report.append("KEY " + k[:70])
    report.append("  map-> " + mapping[k][:100])
    report.append(f"  base {find_fstring(base, k)}")
    report.append(f"  ui   {find_fstring(ui, k)}")
    kind, off, ln = find_fstring(base, k)
    if off >= 0 and ln:
        chunk = ui[off : off + ln]
        ln_field = struct.unpack_from("<i", chunk, 0)[0]
        report.append(f"  ui@same ln_field={ln_field}")
        if ln_field > 0:
            body = chunk[4 : 4 + ln_field]
            report.append("  ui body cp1251=" + body[:-1].decode("cp1251", "replace")[:140])
            report.append("  hex " + body[:64].hex())
        else:
            body = chunk[4 : 4 + (-ln_field) * 2]
            report.append("  ui utf16=" + body.decode("utf-16-le", "replace")[:140])

out = Path(r"C:\Mods\FunnelRunners_RU\chunks_ui\welcome_compare.txt")
out.write_text("\n".join(report), encoding="utf-8")
print(out, "lines", len(report))
