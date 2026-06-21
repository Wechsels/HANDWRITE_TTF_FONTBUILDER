# -*- coding: utf-8 -*-
"""gui/cell.py — 字帖格子 CopybookCell。

三层叠加：底色 → 浅色范字 + 红色米字格 + 目标区高亮 → 透明笔画层。
压感(QTabletEvent)→笔宽，鼠标回退可画。单击选中、双击重写。
save_png 只存白底+笔画，矢量化干净。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from charset import metrics, loader as charset_loader  # noqa: E402

from PySide6.QtCore import Qt, QEvent, QPoint
from PySide6.QtGui import QPainter, QPen, QPixmap, QFont, QColor
from PySide6.QtWidgets import QWidget

CELL_SIZE = 220


class CopybookCell(QWidget):
    def __init__(self, cell_size: int, pen_max: float, theme,
                 guide_font: str, on_select, on_rewrite):
        super().__init__()
        self.cell_size = cell_size
        self.pen_max = pen_max
        self.theme = theme
        self.guide_font = guide_font
        self.on_select = on_select
        self.on_rewrite = on_rewrite
        self.setFixedSize(cell_size, cell_size)

        self.guide = QPixmap(cell_size, cell_size)
        self.buffer = QPixmap(cell_size, cell_size)
        self.buffer.fill(Qt.transparent)

        self.target_stem: str | None = None
        self.target_char: str = ""
        self.spec: "metrics.GlyphSpec | None" = None
        self.submitted = False
        self.selected = False

        self._last_pos: QPoint | None = None
        self._moved = False
        self._mouse_drawing = False

    def set_theme(self, theme) -> None:
        self.theme = theme
        self._render_guide()
        self.update()

    def set_guide_font(self, family: str) -> None:
        self.guide_font = family
        self._render_guide()
        self.update()

    def set_target(self, stem: str, char: str, done: set[str]) -> None:
        self.target_stem = stem
        self.target_char = char
        self.submitted = stem in done
        self.spec = metrics.spec_for(char, charset_loader.classify(char)) if char else None
        self._render_guide()
        self.clear_strokes()
        self.selected = False

    def _render_guide(self) -> None:
        self.guide.fill(QColor(self.theme.bg))
        p = QPainter(self.guide)
        p.setRenderHint(QPainter.Antialiasing)

        # 范字（浅色底字）
        font = QFont(self.guide_font or "SimHei")
        font.setPointSizeF(self.cell_size * 0.55)
        p.setFont(font)
        p.setPen(self.theme.guide_char)
        p.drawText(self.rect(), Qt.AlignCenter, self.target_char)

        # 目标区高亮（功能10/11：标点/小写字母指示落笔区）
        if self.spec is not None:
            rx0 = self.spec.region[0] * self.cell_size
            ry0 = self.spec.region[1] * self.cell_size
            rx1 = self.spec.region[2] * self.cell_size
            ry1 = self.spec.region[3] * self.cell_size
            box = QPen(QColor(self.theme.accent))
            box.setStyle(Qt.DotLine)
            box.setWidthF(1.4)
            p.setPen(box)
            p.drawRect(int(rx0), int(ry0), int(rx1 - rx0), int(ry1 - ry0))

        # 红色米字格虚线
        pen = QPen(self.theme.guide_line)
        pen.setStyle(Qt.DashLine)
        pen.setWidthF(1.0)
        p.setPen(pen)
        w = h = self.cell_size
        p.drawLine(QPoint(w // 2, 0), QPoint(w // 2, h))
        p.drawLine(QPoint(0, h // 2), QPoint(w, h // 2))
        p.drawLine(QPoint(0, 0), QPoint(w, h))
        p.drawLine(QPoint(w, 0), QPoint(0, h))
        p.end()

    def clear_strokes(self) -> None:
        self.buffer.fill(Qt.transparent)
        self._last_pos = None
        self.update()

    def is_blank(self) -> bool:
        img = self.buffer.toImage()
        for y in range(0, img.height(), 4):
            for x in range(0, img.width(), 4):
                if img.pixelColor(x, y).alpha() > 20:
                    return False
        return True

    def _stroke_to(self, pos: QPoint, width: float) -> None:
        if self._last_pos is None:
            self._last_pos = pos
        p = QPainter(self.buffer)
        pen = QPen(QColor("#101010"))
        pen.setWidthF(width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        p.drawLine(self._last_pos, pos)
        p.end()
        self._last_pos = pos
        self.update()

    def tabletEvent(self, event):
        pos = event.position().toPoint()
        pressure = event.pressure()
        width = (1.0 + pressure * (self.pen_max - 1.0)
                 if pressure > 0 else max(2.0, self.pen_max * 0.5))
        if event.type() == QEvent.Type.TabletPress:
            self._moved = False
            self._last_pos = pos
            self._stroke_to(pos, width)
            event.accept()
        elif event.type() == QEvent.Type.TabletMove:
            self._moved = True
            self._stroke_to(pos, width)
            event.accept()
        elif event.type() == QEvent.Type.TabletRelease:
            if not self._moved:
                self.on_select(self)
            self._last_pos = None
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._moved = False
            self._mouse_drawing = True
            self._last_pos = e.position().toPoint()
            self._stroke_to(self._last_pos, max(2.0, self.pen_max * 0.5))

    def mouseMoveEvent(self, e):
        if self._mouse_drawing:
            self._moved = True
            self._stroke_to(e.position().toPoint(), max(2.0, self.pen_max * 0.5))

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._mouse_drawing = False
            self._last_pos = None
            if not self._moved:
                self.on_select(self)

    def mouseDoubleClickEvent(self, e):
        self.on_rewrite(self)

    def paintEvent(self, e):
        p = QPainter(self)
        p.drawPixmap(0, 0, self.guide)
        p.drawPixmap(0, 0, self.buffer)
        accent = QColor(self.theme.accent)
        if self.selected:
            p.setPen(QPen(accent, 3))
        elif self.submitted:
            p.setPen(QPen(QColor("#2E8B2E"), 2))
        else:
            p.setPen(QPen(QColor(160, 160, 160), 1))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.setPen(QColor(self.theme.fg))
        p.setFont(QFont("Consolas", 8))
        p.drawText(4, 14, self.target_stem or "")
        if self.submitted:
            p.setPen(QColor("#2E8B2E"))
            p.setFont(QFont("", 11, QFont.Bold))
            p.drawText(self.rect(), Qt.AlignBottom | Qt.AlignRight, "✓")

    def save_png(self, path: Path) -> None:
        out = QPixmap(self.cell_size, self.cell_size)
        out.fill(Qt.white)
        p = QPainter(out)
        p.drawPixmap(0, 0, self.buffer)
        p.end()
        out.save(str(path), "PNG")
