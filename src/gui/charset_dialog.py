# -*- coding: utf-8 -*-
"""gui/charset_dialog.py — 自定义字库编辑对话框（功能2/4）。

增删改命名字库：选名字 + 字符文本，保存到 data/charsets/<name>.txt。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from charset import manager  # noqa: E402

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QComboBox, QPushButton, QTextEdit, QMessageBox,
                                QLineEdit, QInputDialog)


class CharsetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义字库管理")
        self.resize(420, 460)
        self._build_ui()
        self._reload()

    def _build_ui(self) -> None:
        v = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("字库:"))
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self._on_pick)
        top.addWidget(self.combo, 1)
        btn_new = QPushButton("新建")
        btn_new.clicked.connect(self._new)
        btn_rename = QPushButton("重命名")
        btn_rename.clicked.connect(self._rename)
        btn_del = QPushButton("删除")
        btn_del.clicked.connect(self._delete)
        for b in (btn_new, btn_rename, btn_del):
            top.addWidget(b)
        v.addLayout(top)

        self.edit = QTextEdit()
        self.edit.setPlaceholderText("在此输入字库字符，一行一个或连续输入皆可（自动去重保序）")
        v.addWidget(self.edit, 1)

        bottom = QHBoxLayout()
        bottom.addStretch()
        btn_save = QPushButton("保存")
        btn_save.clicked.connect(self._save)
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        bottom.addWidget(btn_save)
        bottom.addWidget(btn_close)
        v.addLayout(bottom)

    def _all_names(self) -> list[str]:
        return [manager.DEFAULT_NAME] + manager.list_custom()

    def _reload(self, select: str | None = None) -> None:
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItems(self._all_names())
        if select and select in self._all_names():
            self.combo.setCurrentText(select)
        self.combo.blockSignals(False)
        self._on_pick()

    def _on_pick(self) -> None:
        name = self.combo.currentText()
        if name:
            self.edit.setPlainText(manager.load_chars(name))

    def _new(self) -> None:
        name, ok = QInputDialog.getText(self, "新建字库", "字库名称:")
        if not ok or not name.strip():
            return
        name = manager._safe_name(name)
        if name in self._all_names():
            QMessageBox.warning(self, "重复", f"字库“{name}”已存在。")
            return
        manager.save_chars(name, "")
        self._reload(select=name)

    def _rename(self) -> None:
        name = self.combo.currentText()
        if not name or name == manager.DEFAULT_NAME:
            QMessageBox.information(self, "提示", "默认字库不可重命名。")
            return
        new, ok = QInputDialog.getText(self, "重命名", "新名称:", text=name)
        if not ok or not new.strip() or new == name:
            return
        new = manager._safe_name(new)
        chars = manager.load_chars(name)
        manager.delete(name)
        manager.save_chars(new, chars)
        self._reload(select=new)

    def _delete(self) -> None:
        name = self.combo.currentText()
        if not name or name == manager.DEFAULT_NAME:
            QMessageBox.information(self, "提示", "默认字库不可删除。")
            return
        if QMessageBox.question(self, "删除", f"删除字库“{name}”？") \
                != QMessageBox.Yes:
            return
        manager.delete(name)
        self._reload()

    def _save(self) -> None:
        name = self.combo.currentText()
        if not name:
            return
        saved = manager.save_chars(name, self.edit.toPlainText())
        self.combo.blockSignals(True)
        # 名字可能被规范化
        idx = self.combo.findText(saved)
        if idx < 0:
            self._reload(select=saved)
        else:
            self.combo.setCurrentIndex(idx)
        self.combo.blockSignals(False)
        QMessageBox.information(self, "已保存", f"字库“{saved}”已保存。")

    def selected_name(self) -> str:
        return self.combo.currentText()
