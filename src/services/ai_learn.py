# -*- coding: utf-8 -*-
"""services/ai_learn.py — AI 字库学习（付费预留接口，未实装）。

设计：用已有字形样本训练风格模型，生成/补全缺失字形。
实装时继承并覆盖 learn / generate，把 enabled 置 True。
"""
from __future__ import annotations
from services.base import ServiceBase


class AILearningEngine(ServiceBase):
    name = "AI 字库学习"

    def learn(self, samples: dict[str, "Path"]) -> None:
        """用 {字符: 位图路径} 样本训练风格模型。未实装。"""
        self._guard()
        raise NotImplementedError

    def generate(self, char: str) -> "Path | None":
        """为缺失字符生成字形位图。未实装。"""
        self._guard()
        raise NotImplementedError
