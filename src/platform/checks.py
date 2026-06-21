# -*- coding: utf-8 -*-
"""platform/checks.py — 启动环境检测（功能6/7，仅提醒不影响功能）。

- detect_tablet：检测数位板/手写笔输入设备。
- detect_fontforge：检测 FontForge(ffpython) 是否可用。
"""
from __future__ import annotations
from platform import ffpython as _ff


def detect_tablet() -> bool:
    """是否检测到数位板/手写笔设备。"""
    try:
        from PySide6.QtGui import QInputDevice
    except Exception:
        return False
    try:
        for dev in QInputDevice.devices():
            t = dev.type()
            # Stylus / Tablet 即数位板笔输入
            if t in (QInputDevice.DeviceType.Stylus,
                     QInputDevice.DeviceType.Tablet):
                return True
    except Exception:
        return False
    return False


def detect_fontforge() -> bool:
    """FontForge(ffpython) 是否已安装。"""
    return _ff.find_ffpython() is not None
