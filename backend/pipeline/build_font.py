# -*- coding: utf-8 -*-
"""pipeline/build_font.py — FontForge 组装 ttf（03_svg → 04_font）。

必须用 FontForge 自带 Python（ffpython）运行，系统 Python 无 fontforge 模块。
advance 宽度读自 charset.metrics.spec_for，与 clean 放置区一致。
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from charset import metrics  # noqa: E402
from charset import loader as charset_loader  # noqa: E402
from paths import SVG_DIR, FONT_DIR  # noqa: E402

WHITESPACE = {0x0020: 0.5, 0x0009: 0.5, 0x00A0: 0.5, 0x3000: 1.0}


def parse_codepoint(stem: str) -> int:
    if not (stem.startswith("U") and len(stem) == 5):
        raise ValueError(f"非规范命名: {stem}")
    return int(stem[1:], 16)


def width_for(ch: str, em: int) -> int:
    spec = metrics.spec_for(ch, charset_loader.classify(ch))
    return int(round(em * spec.advance))


def main() -> int:
    ap = argparse.ArgumentParser(description="FontForge 组装手写体 ttf")
    ap.add_argument("--name", default="我的手写体")
    ap.add_argument("--em", type=int, default=1000)
    ap.add_argument("--svg-dir", default=str(SVG_DIR))
    ap.add_argument("--out-dir", default=str(FONT_DIR))
    args = ap.parse_args()

    try:
        import fontforge  # type: ignore
    except ImportError:
        print("错误：未找到 fontforge 模块。须用 ffpython 运行本脚本：\n"
              f'  ffpython "{Path(__file__).as_posix()}" --name "{args.name}"',
              file=sys.stderr)
        return 2

    svg_dir = Path(args.svg_dir)
    out_dir = Path(args.out_dir)
    if not svg_dir.exists() or not any(svg_dir.glob("*.svg")):
        print(f"错误：{svg_dir} 内暂无 SVG。", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    font = fontforge.font()
    font.encoding = "UnicodeFull"
    font.em = args.em
    font.fontname = args.name
    font.familyname = args.name
    font.fullname = args.name

    ok = fail = 0
    created: set[int] = set()
    for svg in sorted(svg_dir.glob("*.svg")):
        try:
            cp = parse_codepoint(svg.stem)
            glyph = font.createMappedChar(cp)
            glyph.importOutlines(str(svg))
            glyph.width = width_for(chr(cp), args.em)
            created.add(cp)
            ok += 1
        except Exception as e:
            fail += 1
            print(f"  [失败] {svg.name}: {e}", file=sys.stderr)

    for cp, ratio in WHITESPACE.items():
        if cp in created:
            continue
        glyph = font.createMappedChar(cp)
        glyph.width = int(round(args.em * ratio))

    out_path = out_dir / f"{args.name}.ttf"
    font.generate(str(out_path))
    print(f"字体生成完成：{out_path}\n成功 {ok} 字，失败 {fail} 字")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
