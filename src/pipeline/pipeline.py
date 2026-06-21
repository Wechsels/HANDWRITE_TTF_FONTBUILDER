# -*- coding: utf-8 -*-
"""pipeline/pipeline.py — 单字处理编排：clean + trace。"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from paths import RAW_DIR, CLEAN_DIR, SVG_DIR, CANVAS_SIZE, DEFAULT_MARGIN  # noqa: E402
from pipeline import clean, trace  # noqa: E402
from charset import loader as charset_loader  # noqa: E402


def ensure_dirs() -> None:
    for d in (RAW_DIR, CLEAN_DIR, SVG_DIR):
        d.mkdir(parents=True, exist_ok=True)


def process_glyph(stem: str, ch: str, src_png: Path,
                  size: int = CANVAS_SIZE, margin: int = DEFAULT_MARGIN
                  ) -> tuple[bool, str]:
    """对原始 PNG 跑 clean+trace。返回 (成功?, 信息)。"""
    ensure_dirs()
    clean_path = CLEAN_DIR / f"{stem}.png"
    svg_path = SVG_DIR / f"{stem}.svg"
    try:
        st = clean.clean_for_char(src_png, clean_path, ch, size, margin,
                                  force=True)
        if st == "empty":
            return False, f"{stem}:未检测到笔画"
        if st == "fail":
            return False, f"{stem}:清洗失败"
        potrace = trace.find_potrace()
        tst = trace.trace_one(clean_path, svg_path, potrace, force=True)
        if tst != "ok":
            return False, f"{stem}:矢量化失败({tst})"
    except Exception as e:
        return False, f"{stem}:{e}"
    return True, stem
