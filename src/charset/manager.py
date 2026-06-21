# -*- coding: utf-8 -*-
"""charset/manager.py — 自定义字库 CRUD + 命名（功能2/4）。

字库存于 data/charsets/<name>.txt，每行一个字（# 注释行忽略）。
默认字库（data/default_charset.txt）只读，不在管理列表里改名/删除。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from paths import CHARSETS_DIR, DEFAULT_CHARSET_PATH  # noqa: E402

DEFAULT_NAME = "默认字库"
_SAFE = re.compile(r'[\\/:*?"<>|]')


def _safe_name(name: str) -> str:
    name = _SAFE.sub("_", name.strip())
    return name or "未命名"


def list_custom() -> list[str]:
    """返回用户自定义字库名列表。"""
    if not CHARSETS_DIR.exists():
        return []
    return sorted(p.stem for p in CHARSETS_DIR.glob("*.txt"))


def path_for(name: str) -> Path:
    if name == DEFAULT_NAME:
        return DEFAULT_CHARSET_PATH
    return CHARSETS_DIR / f"{_safe_name(name)}.txt"


def load_chars(name: str) -> str:
    p = path_for(name)
    if not p.exists():
        return ""
    # 去重保序地取每行首字符
    seen: set[str] = set()
    out: list[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        ch = s[0]
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    return "".join(out)


def save_chars(name: str, chars: str) -> str:
    """保存字库（去重保序）。返回规范化后的名字。"""
    name = _safe_name(name)
    p = path_for(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    lines: list[str] = []
    for ch in chars:
        if ch in ("\n", "\r", " ", "\t"):
            continue
        if ch not in seen:
            seen.add(ch)
            lines.append(f"{ch}  # U{ord(ch):04X}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return name


def delete(name: str) -> bool:
    if name == DEFAULT_NAME:
        return False
    p = path_for(name)
    if p.exists():
        p.unlink()
        return True
    return False
