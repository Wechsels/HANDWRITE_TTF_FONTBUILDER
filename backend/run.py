# -*- coding: utf-8 -*-
"""backend/run.py — 薄 CLI 入口：接收 --stem --char --raw，跑 clean+trace，打印 JSON 结果。
Electron 主进程通过 child_process.spawn('python', ['backend/run.py', ...]) 调用。
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from paths import CANVAS_SIZE, DEFAULT_MARGIN  # noqa: E402
from pipeline import pipeline  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="单字清洗+矢量化")
    ap.add_argument("--stem", required=True, help="字形 stem，如 U4E2D")
    ap.add_argument("--char", required=True, help="原字符")
    ap.add_argument("--raw", required=True, help="01_raw PNG 路径")
    ap.add_argument("--size", type=int, default=CANVAS_SIZE)
    ap.add_argument("--margin", type=int, default=DEFAULT_MARGIN)
    args = ap.parse_args()

    src = Path(args.raw)
    if not src.exists():
        result = {"ok": False, "info": f"{args.stem}:raw 文件不存在"}
        print(json.dumps(result, ensure_ascii=False))
        return 1

    ok, info = pipeline.process_glyph(args.stem, args.char, src, args.size, args.margin)
    result = {"ok": ok, "info": info}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
