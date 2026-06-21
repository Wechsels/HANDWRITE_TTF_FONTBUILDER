# -*- coding: utf-8 -*-
"""services/ocr.py — OCR 手写识别（付费预留接口，未实装）。

设计：输入手写位图，返回识别出的字符，用于自动校正采集。
实装时继承并覆盖 recognize，把 enabled 置 True。
"""
from __future__ import annotations
from pathlib import Path
from services.base import ServiceBase


class OCRRecognizer(ServiceBase):
    name = "OCR 手写识别"

    def recognize(self, image: Path) -> str:
        """识别一张手写位图，返回字符。未实装。"""
        self._guard()
        raise NotImplementedError
