# -*- coding: utf-8 -*-
"""services/base.py — 付费功能服务基类。所有付费能力继承此类，预留接口不实装。"""
from __future__ import annotations
from abc import ABC, abstractmethod


class ServiceBase(ABC):
    """付费服务统一基类。enabled=False 表示未开通，调用即抛 NotImplementedError。"""

    name: str = "ServiceBase"
    enabled: bool = False

    def _guard(self) -> None:
        if not self.enabled:
            raise NotImplementedError(
                f"{self.name} 为付费预留功能，尚未实装。")
