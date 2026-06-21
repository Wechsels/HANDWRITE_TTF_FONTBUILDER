# -*- coding: utf-8 -*-
"""gui/preview.py — 字库即时预览面板（02_clean 缩略图，按类型筛选）。"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import CLEAN_DIR  # noqa: E402
from charset import loader as charset_loader  # noqa: E402

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QListWidget, QListWidgetItem, QComboBox)

THUMB = 80


class LibraryPreview(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(6, 6, 6, 6)
        top = QHBoxLayout()
        top.addWidget(QLabel("字库预览"))
        top.addStretch()
        top.addWidget(QLabel("筛选:"))
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(charset_loader.CHARSET_CATEGORIES)
        self.combo_filter.currentTextChanged.connect(self.refresh)
        top.addWidget(self.combo_filter)
        v.addLayout(top)

        self.lbl_count = QLabel("0 字")
        v.addWidget(self.lbl_count)

        self.list = QListWidget()
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setIconSize(QSize(THUMB, THUMB))
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setMovement(QListWidget.Static)
        v.addWidget(self.list, stretch=1)

    def refresh(self, *_):
        category = self.combo_filter.currentText()
        self.list.clear()
        if not CLEAN_DIR.exists():
            self.lbl_count.setText("0 字")
            return
        shown = 0
        for png in sorted(CLEAN_DIR.glob("*.png")):
            char = _char_from_stem(png.stem)
            if char is None:
                continue
            if category != charset_loader.ALL and \
               charset_loader.classify(char) != category:
                continue
            item = QListWidgetItem(QIcon(QPixmap(str(png))),
                                   f"{char}\n{png.stem}")
            item.setSizeHint(QSize(THUMB + 12, THUMB + 28))
            self.list.addItem(item)
            shown += 1
        self.lbl_count.setText(f"{shown} 字")


_stem2char: dict[str, str] | None = None


def _char_from_stem(stem: str) -> str | None:
    global _stem2char
    if _stem2char is None:
        _stem2char = {}
        for s, ch in charset_loader.load_charset_file(
                Path(__file__).resolve().parents[2] / "data" / "default_charset.txt"):
            _stem2char[s] = ch
    if stem in _stem2char:
        return _stem2char[stem]
    if stem.startswith("U") and len(stem) == 5:
        try:
            return chr(int(stem[1:], 16))
        except ValueError:
            return None
    return None
