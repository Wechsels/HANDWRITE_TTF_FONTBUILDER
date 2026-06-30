# -*- coding: utf-8 -*-
"""charset/metrics.py — 字形规格表（功能 10/11 核心，单一真相源）。

每个字符 → GlyphSpec(placement region 分数, advance EM 比例)。
clean 按 region 把前景缩放放置进画布；build_font 按 advance 设字宽。
advance 取 region 水平宽度，避免与下一字重叠。改这里即可全局调整。
"""
from __future__ import annotations
from dataclasses import dataclass

# 字符集类别（与 loader.classify 一致）
HANZI = "汉字"
DIGIT = "数字"
UPPER = "大写字母"
LOWER = "小写字母"
CN_PUNCT = "中文标点"
EN_PUNCT = "英文标点"

# 中文标点细分：句读(1/4) / 竖向(1/2) / 满格
PUNCT_QUARTER = "中标点-句读"   # ，。、  → 左下 1/4
PUNCT_HALF = "中标点-竖向"      # ；！？： → 左半
PUNCT_FULL = "中标点-满格"      # …— 及括号引号 → 满格


@dataclass(frozen=True)
class GlyphSpec:
    region: tuple[float, float, float, float]   # (x0,y0,x1,y1) 分数
    advance: float                              # EM 比例


_SPECS: dict[str, GlyphSpec] = {
    PUNCT_QUARTER: GlyphSpec((0.00, 0.50, 0.50, 1.00), 0.5),
    PUNCT_HALF:    GlyphSpec((0.00, 0.00, 0.50, 1.00), 0.5),
    PUNCT_FULL:    GlyphSpec((0.04, 0.04, 0.96, 0.96), 1.0),
    LOWER:         GlyphSpec((0.00, 0.50, 1.00, 1.00), 0.6),   # 功能11：下半
    DIGIT:         GlyphSpec((0.06, 0.06, 0.94, 0.94), 0.6),
    UPPER:         GlyphSpec((0.06, 0.06, 0.94, 0.94), 0.6),
    HANZI:         GlyphSpec((0.02, 0.02, 0.98, 0.98), 1.0),
    EN_PUNCT:      GlyphSpec((0.25, 0.25, 0.75, 0.75), 0.4),
}

# 细分字符集合（公开供 loader 引用）
_CN_PUNCT_SET = set("，。、；：？！""''（）【】《》「」『』—…・～")
_EN_PUNCT_SET = set(",.!?;:'\"()[]{}-_/\\@#&*")
_QUARTER_SET = set("，。、")
_HALF_SET = set("；！？：")
# 中文标点里非句读/非竖向的归满格（括号/引号/省略号/破折号/波浪/间隔号等）

_DEFAULT = GlyphSpec((0.04, 0.04, 0.96, 0.96), 1.0)


def classify_char(ch: str, base_cat: str) -> str:
    """在基础分类上细分中文标点为 QUARTER/HALF/FULL。"""
    if base_cat == CN_PUNCT:
        if ch in _QUARTER_SET:
            return PUNCT_QUARTER
        if ch in _HALF_SET:
            return PUNCT_HALF
        return PUNCT_FULL
    return base_cat


def spec_for(ch: str, base_cat: str) -> GlyphSpec:
    """返回字符的放置规格。base_cat 来自 loader.classify。"""
    return _SPECS.get(classify_char(ch, base_cat), _DEFAULT)
