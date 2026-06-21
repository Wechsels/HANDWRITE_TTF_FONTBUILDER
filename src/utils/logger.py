# -*- coding: utf-8 -*-
"""utils.logger — 模块级日志单例，写 logs/ + 控制台，按日轮转。"""
from __future__ import annotations
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # src/
from paths import LOG_DIR  # noqa: E402

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_handlers: list[logging.Handler] = []


def _ensure_handlers() -> None:
    if _handlers:
        return
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fh = TimedRotatingFileHandler(LOG_DIR / "fontbuilder.log",
                                  when="midnight", backupCount=7,
                                  encoding="utf-8")
    fh.setFormatter(logging.Formatter(_FORMAT))
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(_FORMAT))
    _handlers.extend([fh, sh])


def get_logger(name: str) -> logging.Logger:
    _ensure_handlers()
    log = logging.getLogger(name)
    if not log.handlers:
        for h in _handlers:
            log.addHandler(h)
    log.setLevel(logging.INFO)
    log.propagate = False
    return log
