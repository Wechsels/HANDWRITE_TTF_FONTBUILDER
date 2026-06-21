# -*- coding: utf-8 -*-
"""paths.py — 全局路径常量。

parents 层级（重要，勿改）：
  Path(__file__) = Code-04/.../src/paths.py
  parents[0] = src/   parents[1] = 项目根 Code-04-HANDWRITE_TTF_FONTBUILDER
  parents[2] = CodeAgent（工作空间根，禁止向其写任何文件）

打包后（PyInstaller onefile）：只读资源在 _MEIPASS，可写目录改到
%APPDATA%/HandwriteFontBuilder 下，避免向只读临时目录写文件。
"""
from __future__ import annotations
import sys
from pathlib import Path


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


# 只读资源根：开发=项目根；打包=_MEIPASS
if _is_frozen():
    RESOURCE_ROOT = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    _user_root = Path.home() / "AppData" / "Roaming" / "HandwriteFontBuilder"
    _user_root.mkdir(parents=True, exist_ok=True)
    PROJECT_ROOT = _user_root  # 可写根
else:
    RESOURCE_ROOT = Path(__file__).resolve().parents[1]
    PROJECT_ROOT = RESOURCE_ROOT

SRC_DIR = PROJECT_ROOT / "src"

# 可写目录（开发在项目内，打包在 %APPDATA% 内）
DATA_DIR = PROJECT_ROOT / "data"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"
ICON_DIR = PROJECT_ROOT / "icon"

# 流水线各阶段
RAW_DIR = WORKSPACE_DIR / "01_raw"
CLEAN_DIR = WORKSPACE_DIR / "02_clean"
SVG_DIR = WORKSPACE_DIR / "03_svg"
FONT_DIR = WORKSPACE_DIR / "04_font"

# 数据文件：默认字表来自只读资源根；配置与自定义字库在可写 DATA_DIR
CONFIG_PATH = DATA_DIR / "config.json"
CHARSETS_DIR = DATA_DIR / "charsets"
DEFAULT_CHARSET_PATH = RESOURCE_ROOT / "data" / "default_charset.txt"

# 画布/EM 尺寸：clean 画布 = EM，使 potrace 输出坐标 1:1 映射字体 EM 空间
CANVAS_SIZE = 1000
DEFAULT_MARGIN = 30
