# -*- coding: utf-8 -*-
"""gui/grid_page.py — 行列网格分页（功能1）。

cols × rows 个 CopybookCell，分页浏览当前字符集。取代原单行横滚。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gui.cell import CopybookCell, CELL_SIZE  # noqa: E402
from gui import theme as theme_mod  # noqa: E402
from config import THEME_LIGHT  # noqa: E402

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QGridLayout, QScrollArea)


class GridPage(QWidget):
    def __init__(self, on_select, on_rewrite):
        super().__init__()
        self.on_select = on_select
        self.on_rewrite = on_rewrite
        self.theme = theme_mod.theme(THEME_LIGHT)  # 默认浅色，apply_theme 会覆盖
        self.guide_font = "SimHei"
        self.cols = 8
        self.rows = 2
        self.cells: list[CopybookCell] = []
        self.page_start = 0
        self.filtered: list[tuple[str, str]] = []
        self.done: set[str] = set()

        self._container = QWidget()
        self.grid = QGridLayout(self._container)
        self.grid.setSpacing(8)
        self.grid.setContentsMargins(8, 8, 8, 8)
        scroll = QScrollArea()
        scroll.setWidget(self._container)
        scroll.setWidgetResizable(True)
        outer = __import__("PySide6.QtWidgets", fromlist=["QVBoxLayout"]).QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def set_charset(self, filtered, done: set[str]) -> None:
        self.filtered = filtered
        self.done = done
        self.page_start = 0
        self._rebuild_cells()
        self._load_page()

    def set_layout(self, cols: int, rows: int) -> None:
        self.cols = max(1, cols)
        self.rows = max(1, rows)
        self.page_start = 0
        self._rebuild_cells()
        self._load_page()

    def apply_theme(self, theme) -> None:
        self.theme = theme
        for c in self.cells:
            c.set_theme(theme)

    def set_guide_font(self, family: str) -> None:
        self.guide_font = family
        for c in self.cells:
            c.set_guide_font(family)

    def _rebuild_cells(self) -> None:
        # 清空旧
        while self.grid.count():
            it = self.grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        self.cells = []
        pen_max = max(4.0, CELL_SIZE / 30.0)
        page = self.cols * self.rows
        for i in range(page):
            cell = CopybookCell(CELL_SIZE, pen_max, self.theme,
                                self.guide_font, self.on_select, self.on_rewrite)
            r, c = divmod(i, self.cols)
            self.grid.addWidget(cell, r, c)
            self.cells.append(cell)

    def page_size(self) -> int:
        return self.cols * self.rows

    def _load_page(self) -> None:
        n = len(self.filtered)
        for i, cell in enumerate(self.cells):
            idx = self.page_start + i
            if idx < n:
                stem, ch = self.filtered[idx]
                cell.set_target(stem, ch, self.done)
                cell.setEnabled(True)
            else:
                cell.set_target("----", "", set())
                cell.setEnabled(False)
            cell.update()

    def goto_first_undone(self) -> None:
        for i, (stem, _) in enumerate(self.filtered):
            if stem not in self.done:
                self.page_start = (i // self.page_size()) * self.page_size()
                self._load_page()
                return
        self.page_start = 0
        self._load_page()

    def goto_prev(self) -> None:
        self.page_start = max(0, self.page_start - self.page_size())
        self._load_page()

    def goto_next(self) -> None:
        n = len(self.filtered)
        ps = self.page_size()
        self.page_start = min(max(0, n - 1), self.page_start + ps)
        # 对齐到页首
        self.page_start = (self.page_start // ps) * ps
        self._load_page()

    def clear_all_strokes(self) -> None:
        for c in self.cells:
            c.clear_strokes()

    def cell_at(self, idx: int) -> CopybookCell | None:
        if 0 <= idx < len(self.cells):
            return self.cells[idx]
        return None

    def page_info(self) -> tuple[int, int]:
        n = len(self.filtered)
        a = self.page_start
        b = min(n, self.page_start + self.page_size()) - 1
        return a, max(a, b)
