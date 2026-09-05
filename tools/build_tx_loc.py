# -*- coding: utf-8 -*-
"""Build FunnelRunners_RU_TX_P — same-size texture ubulk overlay.

Takes bulk chunks from the Codex fan pack raw extract. Skips their
ST_Items / IA_RotateLeft / locres / fonts.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

RETOC = Path(r"C:\Mods\retoc_cli-x86_64-pc-windows-msvc\retoc.exe")
PAKS = Path(
    r"F:\SteamLibrary\steamapps\common\Funnel Runners"
    r"\StormEscape\Content\Paks"
)
ROOT = Path(r"C:\Mods\FunnelRunners_RU")
THEIR_RAW = ROOT / "tmp_probe" / "their" / "raw"
RAW = ROOT / "raw_tx_loc"
OUT = ROOT / "out_tx_loc"

SKIP = {
    "5f7c2858d6e08a4800000001",  # ST_Items
    "7a0cf0e4f753824b00000001",  # IA_RotateLeft
}


def main() -> None:
    man_path = THEIR_RAW / "manifest.json"
    if not man_path.exists():
        raise SystemExit(f"missing {man_path} — unpack their StormEscape_P first")

    man = json.loads(man_path.read_text(encoding="utf-8"))
    if RAW.exists():
        shutil.rmtree(RAW)
    (RAW / "chunks").mkdir(parents=True)

    new_paths: dict[str, str] = {}
    for cid, path in man["chunk_paths"].items():
        if cid in SKIP:
            print("skip", Path(path).name)
            continue
        src = THEIR_RAW / "chunks" / cid
        blob = src.read_bytes()
        (RAW / "chunks" / cid).write_bytes(blob)
        new_paths[cid] = path
        print(f"keep {Path(path).name} {len(blob)}")
    man["chunk_paths"] = new_paths
    (RAW / "manifest.json").write_text(json.dumps(man, indent=2), encoding="utf-8")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    final_utoc = OUT / "FunnelRunners_RU_TX_P.utoc"
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

    stub = OUT / "FunnelRunners_RU_TX_P.pak"
    for cand in (
        ROOT / "out_raw" / "FunnelRunners_RU_P.pak",
        ROOT / "out_all_loc" / "FunnelRunners_RU_P.pak",
        ROOT / "dist" / "FunnelRunners_RU" / "Paks" / "FunnelRunners_RU_P.pak",
    ):
        if cand.exists():
            shutil.copy2(cand, stub)
            break
    if not stub.exists():
        raise SystemExit("missing stub .pak")

    for p in PAKS.glob("FunnelRunners_RU_TX_P*"):
        p.unlink()
    for p in OUT.iterdir():
        if p.name.startswith("FunnelRunners_RU_TX_P") and p.suffix in {".pak", ".utoc", ".ucas"}:
            shutil.copy2(p, PAKS / p.name)
            print("installed", p.name, p.stat().st_size)

    subprocess.check_call([str(RETOC), "verify", str(PAKS / "FunnelRunners_RU_TX_P.utoc")])
    print("DONE — texture overlay installed (local only)")


if __name__ == "__main__":
    main()
