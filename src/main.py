# -*- coding: utf-8 -*-
"""main.py — 应用入口。

运行：python src/main.py
"""
from __future__ import annotations
import sys
from pathlib import Path

# 把 src/ 注入 sys.path，使扁平绝对导入生效（PyInstaller 与直跑通用）
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    # 生成默认字表（首次运行 / 缺失时）
    from pipeline import gen_charset
    from paths import DEFAULT_CHARSET_PATH
    if not DEFAULT_CHARSET_PATH.exists():
        gen_charset.main()

    from gui.main_window import run
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
