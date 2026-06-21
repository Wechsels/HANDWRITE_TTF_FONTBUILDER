# -*- coding: utf-8 -*-
"""gui/theme.py — 主题管理（功能5/8）：白/黑/护眼黄，对比色保证可读性。"""
from __future__ import annotations
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtWidgets import QApplication

from config import THEME_LIGHT, THEME_DARK, THEME_SEPIA


class Theme:
    def __init__(self, name: str, bg: str, fg: str, accent: str,
                 guide: str, line: str, base_dir: str):
        self.name = name
        self.bg = bg
        self.fg = fg
        self.accent = accent
        self.guide_char = QColor(guide)
        self.guide_line = QColor(line)
        self.base_dir = base_dir  # 目录/面板底色


THEMES: dict[str, Theme] = {
    THEME_LIGHT: Theme(THEME_LIGHT, "#FFFFFF", "#1A1A1A", "#1F6FB3",
                       "#DADADA", "rgba(200,40,40,150)", "#F2F2F2"),
    THEME_DARK: Theme(THEME_DARK, "#1E1E22", "#ECECEC", "#4FA3E0",
                      "#3A3A40", "rgba(220,80,80,160)", "#26262C"),
    THEME_SEPIA: Theme(THEME_SEPIA, "#F5E6C8", "#3E2C18", "#9A4A1A",
                       "#C9B489", "rgba(170,50,40,150)", "#EEDDB8"),
}


def theme(name: str) -> Theme:
    return THEMES.get(name, THEMES[THEME_LIGHT])


def apply_theme(name: str) -> Theme:
    """切换全局调色板与样式表，返回当前 Theme。"""
    t = theme(name)
    app = QApplication.instance()
    if app is None:
        return t
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(t.bg))
    pal.setColor(QPalette.WindowText, QColor(t.fg))
    pal.setColor(QPalette.Base, QColor(t.bg))
    pal.setColor(QPalette.Text, QColor(t.fg))
    pal.setColor(QPalette.Button, QColor(t.base_dir))
    pal.setColor(QPalette.ButtonText, QColor(t.fg))
    pal.setColor(QPalette.Highlight, QColor(t.accent))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(pal)
    app.setStyleSheet(_qss(t))
    app.setFont(QFont("Microsoft YaHei", 9))
    return t


def _qss(t: Theme) -> str:
    return f"""
    QWidget {{ background: {t.bg}; color: {t.fg}; }}
    QPushButton {{
        background: {t.base_dir}; color: {t.fg};
        border: 1px solid {t.accent}; border-radius: 6px;
        padding: 6px 14px;
    }}
    QPushButton:hover {{ background: {t.accent}; color: #FFFFFF; }}
    QPushButton:disabled {{ color: gray; border-color: gray; }}
    QComboBox, QSpinBox, QLineEdit {{
        background: {t.bg}; color: {t.fg};
        border: 1px solid {t.accent}; border-radius: 4px;
        padding: 3px 6px;
    }}
    QDockWidget {{ background: {t.base_dir}; color: {t.fg}; }}
    QListWidget {{ background: {t.bg}; color: {t.fg}; }}
    QScrollArea {{ background: {t.bg}; }}
    QLabel {{ background: transparent; }}
    QStatusBar {{ background: {t.base_dir}; color: {t.fg}; }}
    """
