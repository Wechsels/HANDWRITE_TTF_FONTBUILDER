# -*- coding: utf-8 -*-
"""pipeline/trace.py — 矢量化（02_clean → 03_svg），调 potrace。"""
from __future__ import annotations
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image


def find_potrace() -> str:
    """定位 potrace，找不到报错退出。"""
    exe = shutil.which("potrace")
    if not exe:
        raise FileNotFoundError(
            "未找到 potrace。Windows: scoop install potrace；"
            "macOS: brew install potrace；Linux: apt install potrace")
    return exe


def trace_one(src: Path, dst: Path, potrace: str, force: bool) -> str:
    if dst.exists() and not force:
        return "skip"
    img = Image.open(src).convert("L")
    with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as tmp:
        tmp_bmp = Path(tmp.name)
    try:
        img.save(tmp_bmp, "BMP")
        proc = subprocess.run(
            [potrace, str(tmp_bmp), "-s", "-o", str(dst)],
            capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"potrace 失败: {proc.stderr.strip()}")
        return "ok"
    finally:
        tmp_bmp.unlink(missing_ok=True)
