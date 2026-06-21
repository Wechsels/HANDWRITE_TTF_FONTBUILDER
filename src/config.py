# -*- coding: utf-8 -*-
"""config.py — 应用配置数据类与持久化。优先级 CLI > config.json > 默认。"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import CONFIG_PATH  # noqa: E402

THEME_LIGHT = "白色"
THEME_DARK = "黑色"
THEME_SEPIA = "护眼黄"
THEMES = [THEME_LIGHT, THEME_DARK, THEME_SEPIA]

ALL = "全部"


@dataclass
class AppConfig:
    font_name: str = "我的手写体"
    ffpython_path: str = ""
    cols: int = 8
    rows: int = 2
    theme: str = THEME_LIGHT
    guide_font: str = "SimHei"
    active_charset: str = "默认字库"
    category: str = ALL
    # 已确认过的启动检测，避免每次弹框
    acknowledged_no_tablet: bool = False
    acknowledged_no_fontforge: bool = False

    def __post_init__(self) -> None:
        self.cols = max(1, min(20, int(self.cols)))
        self.rows = max(1, min(8, int(self.rows)))
        if self.theme not in THEMES:
            self.theme = THEME_LIGHT


def load_config() -> AppConfig:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            known = {f for f in data if f in AppConfig.__dataclass_fields__}
            return AppConfig(**{k: data[k] for k in known})
        except Exception:
            pass
    return AppConfig()


def save_config(cfg: AppConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(cfg), ensure_ascii=False, indent=2),
                           encoding="utf-8")
