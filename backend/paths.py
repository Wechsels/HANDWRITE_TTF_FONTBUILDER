# -*- coding: utf-8 -*-
"""paths.py — 全局路径常量。支持 HF_PROJECT_ROOT 环境变量覆盖项目根。"""
from __future__ import annotations
import os
import sys
from pathlib import Path


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


# 项目根：优先环境变量（Electron 主进程注入），回退 __file__ 相对路径
_env_root = os.environ.get("HF_PROJECT_ROOT", "")
if _env_root:
    PROJECT_ROOT = Path(_env_root)
elif _is_frozen():
    RESOURCE_ROOT = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    _user_root = Path.home() / "AppData" / "Roaming" / "HandwriteFontBuilder"
    _user_root.mkdir(parents=True, exist_ok=True)
    PROJECT_ROOT = _user_root
else:
    RESOURCE_ROOT = Path(__file__).resolve().parents[1]
    PROJECT_ROOT = RESOURCE_ROOT

DATA_DIR = PROJECT_ROOT / "data"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"

RAW_DIR = WORKSPACE_DIR / "01_raw"
CLEAN_DIR = WORKSPACE_DIR / "02_clean"
SVG_DIR = WORKSPACE_DIR / "03_svg"
FONT_DIR = WORKSPACE_DIR / "04_font"

CONFIG_PATH = DATA_DIR / "config.json"
CHARSETS_DIR = DATA_DIR / "charsets"
DEFAULT_CHARSET_PATH = PROJECT_ROOT / "data" / "default_charset.txt"

CANVAS_SIZE = 1000
DEFAULT_MARGIN = 30
