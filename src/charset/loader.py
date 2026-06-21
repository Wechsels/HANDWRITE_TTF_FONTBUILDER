# -*- coding: utf-8 -*-
"""charset/loader.py — 字表解析与字符集分类。"""
from __future__ import annotations
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from charset import metrics  # noqa: E402

ALL = "全部"
DIGIT = metrics.DIGIT
UPPER = metrics.UPPER
LOWER = metrics.LOWER
CN_PUNCT = metrics.CN_PUNCT
EN_PUNCT = metrics.EN_PUNCT
HANZI = metrics.HANZI

CHARSET_CATEGORIES = [ALL, DIGIT, UPPER, LOWER, CN_PUNCT, EN_PUNCT, HANZI]

_CN_PUNCT_SET = set("，。、；：？！“”‘’（）【】《》「」『』—…・～")
_EN_PUNCT_SET = set(",.!?;:'\"()[]{}-_/\\@#&*")


def load_charset_file(path: Path) -> list[tuple[str, str]]:
    """解析字表文件，返回 (stem 'UXXXX', 字) 有序列表。跳过注释/空行。"""
    if not path.exists():
        return []
    items: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        ch = s[0]
        if "#" in s:
            tag = s.split("#", 1)[1].strip()
            if tag.startswith("U") and len(tag) == 5:
                items.append((tag, ch))
                continue
        items.append((f"U{ord(ch):04X}", ch))
    return items


def classify(ch: str) -> str:
    """单字符所属字符集类别。"""
    cp = ord(ch)
    if 0x30 <= cp <= 0x39:
        return DIGIT
    if 0x41 <= cp <= 0x5A:
        return UPPER
    if 0x61 <= cp <= 0x7A:
        return LOWER
    if ch in _CN_PUNCT_SET:
        return CN_PUNCT
    if ch in _EN_PUNCT_SET:
        return EN_PUNCT
    if 0x4E00 <= cp <= 0x9FFF:
        return HANZI
    return ALL


def filter_by_category(charset, category: str):
    if category == ALL:
        return charset
    return [(s, ch) for s, ch in charset if classify(ch) == category]


def scan_done(svg_dir: Path) -> set[str]:
    if not svg_dir.exists():
        return set()
    return {p.stem for p in svg_dir.glob("*.svg")}
