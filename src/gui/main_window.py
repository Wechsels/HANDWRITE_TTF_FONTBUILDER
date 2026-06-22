# -*- coding: utf-8 -*-
"""gui/main_window.py — 主窗口编排（瘦）。

顶栏：进度 | 字库/字符集 | 视图(行列/主题/范字字体/字体名) | 操作
中部：GridPage 网格分页 | 右侧字库预览 Dock
底部：批量提交/重写/提交选中/翻页 + 状态栏
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import (RAW_DIR, SVG_DIR, FONT_DIR, OUTPUT_DIR,  # noqa: E402
                   DEFAULT_CHARSET_PATH)
from config import AppConfig, load_config, save_config, THEMES  # noqa: E402
from charset import loader as charset_loader, manager  # noqa: E402
from pipeline import pipeline, cleanup  # noqa: E402
from gui import theme as theme_mod  # noqa: E402
from gui.grid_page import GridPage  # noqa: E402
from gui.preview import LibraryPreview  # noqa: E402
from gui.charset_dialog import CharsetDialog  # noqa: E402
from platform import checks, ffpython  # noqa: E402
from utils.logger import get_logger  # noqa: E402

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                                QVBoxLayout, QHBoxLayout, QWidget, QSpinBox,
                                QComboBox, QScrollArea, QMessageBox,
                                QFileDialog, QDockWidget, QLineEdit)

log = get_logger("main")
PEN_MAX = max(4.0, 220 / 30.0)


def _build_font_path() -> Path:
    """build_font.py 的运行期路径。

    开发态：源码位置（__file__ 真实路径）。
    onefile 冻结态：build_font.py 通过 --add-data 放进 _MEIPASS/src/pipeline/，
    ffpython 需要真实 .py 文件（不接受 .pyc），故必须从这里取。
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "src" / "pipeline" / "build_font.py"
    return Path(__file__).resolve().parents[1] / "pipeline" / "build_font.py"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("手写字库构建工具 — HANDWRITE TTF FONTBUILDER")
        self.cfg: AppConfig = load_config()
        self.theme = theme_mod.apply_theme(self.cfg.theme)

        self.charset_name = manager.DEFAULT_NAME
        self.charset: list[tuple[str, str]] = charset_loader.load_charset_file(
            DEFAULT_CHARSET_PATH)
        self.done: set[str] = charset_loader.scan_done(SVG_DIR)
        self.selected_index: int | None = None

        self._build_ui()
        name = self.cfg.active_charset
        valid = [manager.DEFAULT_NAME] + manager.list_custom()
        if name not in valid:
            name = manager.DEFAULT_NAME
        self._reload_charset(name)
        self.resize(1320, 760)

    # ── UI ──
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setSpacing(8)

        outer.addLayout(self._top_bar())
        self.grid_page = GridPage(self._on_cell_select, self._on_cell_rewrite)
        self.grid_page.apply_theme(self.theme)          # 先设主题，再建格子
        self.grid_page.set_guide_font(self.cfg.guide_font)
        self.grid_page.set_layout(self.cfg.cols, self.cfg.rows)
        outer.addWidget(self.grid_page, stretch=1)
        outer.addLayout(self._ops_bar())

        self.lbl_status = QLabel("就绪。在格内书写后点“批量提交本页”。双击格子可重写。")
        self.lbl_status.setStyleSheet("padding:4px;")
        outer.addWidget(self.lbl_status)

        self.preview = LibraryPreview()
        dock = QDockWidget("字库预览", self)
        dock.setWidget(self.preview)
        dock.setFeatures(QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _top_bar(self) -> QHBoxLayout:
        top = QHBoxLayout()

        self.lbl_progress = QLabel()
        top.addWidget(self.lbl_progress)
        top.addSpacing(12)

        top.addWidget(QLabel("字库:"))
        self.combo_charset = QComboBox()
        self.combo_charset.currentTextChanged.connect(self._on_charset_changed)
        top.addWidget(self.combo_charset)
        btn_charset = QPushButton("管理字库…")
        btn_charset.clicked.connect(self._open_charset_dialog)
        top.addWidget(btn_charset)
        top.addSpacing(8)

        top.addWidget(QLabel("分类:"))
        self.combo_category = QComboBox()
        self.combo_category.addItems(charset_loader.CHARSET_CATEGORIES)
        self.combo_category.setCurrentText(self.cfg.category)
        self.combo_category.currentTextChanged.connect(self._on_category_changed)
        top.addWidget(self.combo_category)
        top.addSpacing(8)

        top.addWidget(QLabel("字体名:"))
        self.edit_font_name = QLineEdit(self.cfg.font_name)
        self.edit_font_name.setFixedWidth(120)
        self.edit_font_name.editingFinished.connect(self._on_font_name_changed)
        top.addWidget(self.edit_font_name)

        top.addStretch()
        return top

    def _ops_bar(self) -> QHBoxLayout:
        ops = QHBoxLayout()

        # 视图组
        ops.addWidget(QLabel("列:"))
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 20)
        self.spin_cols.setValue(self.cfg.cols)
        self.spin_cols.valueChanged.connect(self._on_layout_changed)
        ops.addWidget(self.spin_cols)
        ops.addWidget(QLabel("行:"))
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 8)
        self.spin_rows.setValue(self.cfg.rows)
        self.spin_rows.valueChanged.connect(self._on_layout_changed)
        ops.addSpacing(12)

        ops.addWidget(QLabel("范字字体:"))
        self.combo_font = QComboBox()
        self.combo_font.setEditable(True)
        self.combo_font.addItems(["SimHei", "Microsoft YaHei", "SimSun",
                                  "KaiTi", "FangSong"])
        self.combo_font.setCurrentText(self.cfg.guide_font)
        self.combo_font.currentTextChanged.connect(self._on_guide_font_changed)
        ops.addWidget(self.combo_font)
        ops.addSpacing(12)

        ops.addWidget(QLabel("主题:"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(THEMES)
        self.combo_theme.setCurrentText(self.cfg.theme)
        self.combo_theme.currentTextChanged.connect(self._on_theme_changed)
        ops.addWidget(self.combo_theme)

        ops.addStretch()

        btn_submit = QPushButton("✓ 批量提交本页")
        btn_submit.setStyleSheet("font-weight:bold; padding:8px 16px;")
        btn_submit.clicked.connect(self.submit_page)
        btn_rewrite = QPushButton("重写选中格")
        btn_rewrite.clicked.connect(self.rewrite_selected)
        btn_sel = QPushButton("提交选中格")
        btn_sel.clicked.connect(self.submit_selected)
        btn_prev = QPushButton("◀ 上一页")
        btn_prev.clicked.connect(self.grid_page.goto_prev)
        btn_next = QPushButton("下一页 ▶")
        btn_next.clicked.connect(self.grid_page.goto_next)
        btn_jump = QPushButton("跳到未完成")
        btn_jump.clicked.connect(self.grid_page.goto_first_undone)
        btn_reset = QPushButton("重置字库")
        btn_reset.setStyleSheet("color:#b00;")
        btn_reset.clicked.connect(self._on_reset)
        btn_rebuild = QPushButton("重建字库")
        btn_rebuild.clicked.connect(self.rebuild_library)
        for b in (btn_submit, btn_rewrite, btn_sel, btn_prev, btn_next,
                  btn_jump, btn_reset, btn_rebuild):
            ops.addWidget(b)
        return ops

    # ── 字库与字符集 ──
    def _refresh_charset_combo(self) -> None:
        self.combo_charset.blockSignals(True)
        self.combo_charset.clear()
        self.combo_charset.addItems([manager.DEFAULT_NAME] + manager.list_custom())
        if self.charset_name in [self.combo_charset.itemText(i)
                                 for i in range(self.combo_charset.count())]:
            self.combo_charset.setCurrentText(self.charset_name)
        self.combo_charset.blockSignals(False)

    def _reload_charset(self, name: str) -> None:
        self.charset_name = name
        p = manager.path_for(name) if name != manager.DEFAULT_NAME else DEFAULT_CHARSET_PATH
        self.charset = charset_loader.load_charset_file(p)
        self._refresh_charset_combo()
        self._apply_filter()

    def _apply_filter(self) -> None:
        filtered = charset_loader.filter_by_category(self.charset, self.cfg.category)
        self.grid_page.set_charset(filtered, self.done)
        self._update_progress()

    def _on_charset_changed(self, name: str) -> None:
        if not name:
            return
        self.charset_name = name
        self.cfg.active_charset = name
        save_config(self.cfg)
        p = manager.path_for(name) if name != manager.DEFAULT_NAME else DEFAULT_CHARSET_PATH
        self.charset = charset_loader.load_charset_file(p)
        self._apply_filter()

    def _on_category_changed(self, text: str) -> None:
        self.cfg.category = text
        save_config(self.cfg)
        self._apply_filter()

    def _open_charset_dialog(self) -> None:
        dlg = CharsetDialog(self)
        dlg.exec()
        # 返回后刷新字库下拉与当前字库内容
        cur = self.charset_name
        self._reload_charset(cur)

    def _on_font_name_changed(self) -> None:
        self.cfg.font_name = self.edit_font_name.text().strip() or "我的手写体"
        save_config(self.cfg)

    # ── 视图：布局/字体/主题 ──
    def _on_layout_changed(self) -> None:
        self.cfg.cols = self.spin_cols.value()
        self.cfg.rows = self.spin_rows.value()
        save_config(self.cfg)
        self.grid_page.set_layout(self.cfg.cols, self.cfg.rows)
        self._apply_filter()

    def _on_guide_font_changed(self, family: str) -> None:
        self.cfg.guide_font = family
        save_config(self.cfg)
        self.grid_page.set_guide_font(family)

    def _on_theme_changed(self, name: str) -> None:
        self.cfg.theme = name
        save_config(self.cfg)
        self.theme = theme_mod.apply_theme(name)
        self.grid_page.apply_theme(self.theme)

    # ── 交互回调 ──
    def _on_cell_select(self, cell):
        self.selected_index = None
        for i, c in enumerate(self.grid_page.cells):
            c.selected = (c is cell)
            if c is cell:
                self.selected_index = i
            c.update()
        if self.selected_index is not None:
            c = self.grid_page.cells[self.selected_index]
            self._set_status(f"已选中 第{self.selected_index+1}格 {c.target_char} ({c.target_stem})")

    def _on_cell_rewrite(self, cell):
        for i, c in enumerate(self.grid_page.cells):
            if c is cell:
                self.selected_index = i
                break
        cell.clear_strokes()
        cell.submitted = False
        cell.selected = True
        for c in self.grid_page.cells:
            c.selected = (c is cell)
            c.update()
        self._set_status(f"已清空 第{self.selected_index+1}格 {cell.target_char}，请重写后点“提交选中格”。")

    # ── 提交 ──
    def _process_cell(self, cell) -> tuple[bool, str]:
        if cell.target_stem in ("----", None):
            return False, "空格"
        if cell.is_blank():
            return False, "空白"
        stem, ch = cell.target_stem, cell.target_char
        raw_path = RAW_DIR / f"{stem}.png"
        cell.save_png(raw_path)
        ok, info = pipeline.process_glyph(stem, ch, raw_path)
        if ok:
            self.done.add(stem)
            cell.submitted = True
            cell.update()
            return True, ch
        return False, info

    def submit_page(self) -> None:
        ok, fail, skipped = [], [], 0
        for cell in self.grid_page.cells:
            if cell.is_blank():
                skipped += 1
                continue
            success, info = self._process_cell(cell)
            (ok if success else fail).append(info)
            QApplication.processEvents()
        msg = f"本页已提交：成功 {len(ok)} 字"
        if fail:
            msg += f"，失败 {len(fail)} ({','.join(fail[:5])})"
        if skipped:
            msg += f"，跳过空白 {skipped}"
        self._set_status(msg)
        self._update_progress()
        self.preview.refresh()

    def rewrite_selected(self) -> None:
        if self.selected_index is None:
            self._set_status("⚠ 请先点选/双击一个格子再重写。")
            return
        self._on_cell_rewrite(self.grid_page.cells[self.selected_index])

    def submit_selected(self) -> None:
        if self.selected_index is None:
            self._set_status("⚠ 请先点选一个格子再提交。")
            return
        cell = self.grid_page.cells[self.selected_index]
        success, info = self._process_cell(cell)
        self._set_status(f"{'✓' if success else '✗'} 第{self.selected_index+1}格 {info}")
        self._update_progress()
        self.preview.refresh()

    # ── 重置（功能9：二次确认）──
    def _on_reset(self) -> None:
        ans = QMessageBox.question(
            self, "重置字库 — 第 1/2 次确认",
            "将清除所有已采集手写记录与缓存\n(01_raw~04_font)。\n"
            "不会删除 output/ 已生成的 ttf。\n\n确定继续？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans != QMessageBox.Yes:
            return
        ans2 = QMessageBox.warning(
            self, "重置字库 — 第 2/2 次确认",
            "再次确认：此操作不可撤销，所有采集进度将丢失！\n是否执行？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans2 != QMessageBox.Yes:
            return
        removed = cleanup.clear_artifacts()
        self.done = charset_loader.scan_done(SVG_DIR)
        self._update_progress()
        self._apply_filter()
        self.preview.refresh()
        self._set_status(f"已清空 {removed} 个中间产物文件。")
        log.info("字库已重置，删除 %d 个文件", removed)

    # ── 重建字库 ──
    def _ensure_ffpython(self) -> str | None:
        p = self.cfg.ffpython_path
        if p and Path(p).exists():
            return p
        found = ffpython.find_ffpython()
        if found:
            self.cfg.ffpython_path = found
            save_config(self.cfg)
            return found
        chosen, _ = QFileDialog.getOpenFileName(
            self, "选择 FontForge 的 ffpython.exe",
            "C:\\Program Files\\FontForgeBuilds\\bin",
            "Executable (ffpython.exe);;All Files (*)")
        if chosen:
            self.cfg.ffpython_path = chosen
            save_config(self.cfg)
            return chosen
        return None

    def rebuild_library(self) -> None:
        if not SVG_DIR.exists() or not any(SVG_DIR.glob("*.svg")):
            self._set_status("⚠ 暂无已采集的字（03_svg/ 为空），先提交几个字。")
            return
        name = self.cfg.font_name
        ffpython = self._ensure_ffpython()
        if not ffpython:
            self._set_status("✗ 未指定 ffpython，无法重建。请先安装 FontForge。")
            return
        self._set_status(f"正在用 FontForge 重建 ttf（{name}）…")
        QApplication.processEvents()
        try:
            proc = subprocess.run(
                [ffpython, str(_build_font_path()), "--name", name,
                 "--out-dir", str(FONT_DIR)],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace")
        except Exception as e:
            self._set_status(f"✗ 调用 ffpython 失败: {e}")
            log.exception("ffpython 调用失败")
            return
        if proc.returncode != 0:
            self._set_status(f"✗ 重建失败: {proc.stderr.strip()[:200]}")
            return
        ttf = FONT_DIR / f"{name}.ttf"
        if not ttf.exists():
            self._set_status(f"✗ 未找到生成的 {ttf.name}")
            return
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(ttf, OUTPUT_DIR / ttf.name)
        self._set_status(f"✓ 字库已重建并输出到 output/{ttf.name}")
        log.info("字库重建完成: %s", ttf.name)
        self.preview.refresh()

    # ── 杂项 ──
    def _update_progress(self) -> None:
        self.lbl_progress.setText(
            f"进度: {len(self.done)} / {len(self.charset)}")

    def _set_status(self, text: str) -> None:
        self.lbl_status.setText(text)

    def run_startup_checks(self) -> None:
        """功能6/7：数位板与 FontForge 检测，缺失弹一次性 Info。"""
        if not self.cfg.acknowledged_no_tablet and not checks.detect_tablet():
            QMessageBox.information(
                self, "数位板检测",
                "未检测到数位板。\n建议使用数位板获得更好体验（鼠标也可书写）。")
            self.cfg.acknowledged_no_tablet = True
            save_config(self.cfg)
        if not self.cfg.acknowledged_no_fontforge and not checks.detect_fontforge():
            QMessageBox.information(
                self, "FontForge 检测",
                "未检测到 FontForge。\n请安装 FontForge 以重建字库，否则重建会报错。\n"
                "下载: https://fontforge.org")
            self.cfg.acknowledged_no_fontforge = True
            save_config(self.cfg)


def run() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.run_startup_checks()
    sys.exit(app.exec())
