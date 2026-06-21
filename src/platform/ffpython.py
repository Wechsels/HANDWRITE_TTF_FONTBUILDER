# -*- coding: utf-8 -*-
"""platform/ffpython.py — 定位 FontForge 的 ffpython.exe。"""
from __future__ import annotations
import shutil
from pathlib import Path

CANDIDATES = [
    r"C:\Program Files\FontForgeBuilds\bin\ffpython.exe",
    r"C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe",
]


def find_ffpython() -> str | None:
    """返回可用的 ffpython 路径，找不到返回 None。"""
    for cand in CANDIDATES:
        if Path(cand).exists():
            return cand
    found = shutil.which("ffpython")
    return found
