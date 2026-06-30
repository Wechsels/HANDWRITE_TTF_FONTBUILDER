# -*- coding: utf-8 -*-
"""pipeline/gen_charset.py — 生成默认字表。

顺序：数字 → 大写 → 小写 → 中文标点 → 英文标点 → GB2312 一级汉字。
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from paths import DEFAULT_CHARSET_PATH  # noqa: E402

GB2312_LEVEL1_FIRST_BYTE = range(0xB0, 0xD8)

PUNCTUATION = [
    "，", "。", "、", "；", "：", "？", "！",
    "“", "”", "‘", "’",
    "（", "）", "《", "》", "【", "】",
    "「", "」", "『", "』",
    "—", "…", "・", "～",
]

EN_PUNCTUATION = [
    ",", ".", "!", "?", ";", ":", "'", "\"",
    "(", ")", "[", "]", "{", "}",
    "-", "_", "/", "\\", "@", "#", "&", "*",
]


def is_gb2312_level1(ch: str) -> bool:
    if len(ch) != 1:
        return False
    try:
        b = ch.encode("gb2312")
    except UnicodeEncodeError:
        return False
    return len(b) == 2 and b[0] in GB2312_LEVEL1_FIRST_BYTE


def build_charset() -> list[str]:
    chars: list[str] = []
    chars += [chr(cp) for cp in range(0x30, 0x3A)]
    chars += [chr(cp) for cp in range(0x41, 0x5B)]
    chars += [chr(cp) for cp in range(0x61, 0x7B)]
    chars += PUNCTUATION
    chars += EN_PUNCTUATION
    for cp in range(0x4E00, 0xA000):
        ch = chr(cp)
        if is_gb2312_level1(ch):
            chars.append(ch)
    return chars


def main() -> None:
    DEFAULT_CHARSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    chars = build_charset()
    lines = [f"{ch}  # U{ord(ch):04X}" for ch in chars]
    DEFAULT_CHARSET_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已生成字表: {DEFAULT_CHARSET_PATH}（共 {len(chars)} 字）")


if __name__ == "__main__":
    main()
