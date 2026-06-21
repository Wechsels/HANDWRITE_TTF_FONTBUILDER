# -*- coding: utf-8 -*-
"""pipeline/cleanup.py — 清空流水线各阶段产物，保留 .gitkeep 与目录结构。

不触碰 output/ 已生成的 ttf（成果非中间产物）。删除需调用方二次确认。
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from paths import RAW_DIR, CLEAN_DIR, SVG_DIR, FONT_DIR  # noqa: E402

STAGE_DIRS = [RAW_DIR, CLEAN_DIR, SVG_DIR, FONT_DIR]
KEEP_FILES = {".gitkeep"}


def has_artifacts() -> bool:
    for d in STAGE_DIRS:
        if d.exists():
            for p in d.iterdir():
                if p.name not in KEEP_FILES:
                    return True
    return False


def clear_artifacts() -> int:
    removed = 0
    for d in STAGE_DIRS:
        if not d.exists():
            continue
        for p in d.iterdir():
            if p.name in KEEP_FILES:
                continue
            try:
                if p.is_file():
                    p.unlink()
                    removed += 1
                elif p.is_dir():
                    import shutil
                    shutil.rmtree(p)
                    removed += 1
            except Exception:
                pass
    return removed
