# -*- coding: utf-8 -*-
"""pipeline/clean.py — 位图清洗（01_raw → 02_clean）。

与原版差异：clean_one 接受 GlyphSpec，前景按 region 缩放放置进画布
（而非总居中），使标点/小写字母落在正确子区。画布尺寸 = EM，坐标 1:1 映射字体空间。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from charset import metrics  # noqa: E402
from charset import loader as charset_loader  # noqa: E402

from PIL import Image

FG_BLACK = 0
BG_WHITE = 255


def otsu_threshold(gray: Image.Image) -> int:
    """Otsu 求二值化阈值。前景极稀疏时退化兜底为 128。"""
    hist = gray.histogram()
    total = gray.width * gray.height
    if total == 0:
        return 128
    sum_total = sum(i * hist[i] for i in range(256))
    sum_b = 0.0
    w_b = 0
    max_var = 0.0
    threshold = 128
    for i in range(256):
        w_b += hist[i]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += i * hist[i]
        mean_b = sum_b / w_b
        mean_f = (sum_total - sum_b) / w_f
        var = w_b * w_f * (mean_b - mean_f) ** 2
        if var > max_var:
            max_var = var
            threshold = i
    # 兜底 128：避免稀疏黑字在 Otsu 阈值过低（如只画到 #10/16）时被全部判为背景。
    return max(threshold, 128)


def clean_one(src: Path, dst: Path, size: int, margin: int, force: bool,
              spec: "metrics.GlyphSpec | None" = None) -> str:
    """清洗单张图。spec 给定则按其 region 放置前景，否则居中满放。返回状态。"""
    if dst.exists() and not force:
        return "skip"

    img = Image.open(src).convert("L")
    threshold = otsu_threshold(img)
    table = [BG_WHITE] * 256
    for i in range(threshold):
        table[i] = FG_BLACK
    bw = img.point(table, "1")

    inverted = Image.eval(bw, lambda x: 255 - x)
    bbox = inverted.getbbox()
    if bbox is None:
        return "empty"

    cropped = bw.crop(bbox)
    w, h = cropped.size

    # 计算 target region（像素），默认满放（留 margin）
    if spec is not None:
        rx0 = spec.region[0] * size
        ry0 = spec.region[1] * size
        rx1 = spec.region[2] * size
        ry1 = spec.region[3] * size
    else:
        rx0 = ry0 = margin
        rx1 = ry1 = size - margin
    box_w = max(1, int(rx1 - rx0))
    box_h = max(1, int(ry1 - ry0))

    # 等比缩放进 region 内
    scale = min(box_w / w, box_h / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)
    resized = resized.convert("L").point(lambda x: 0 if x < 128 else 255, "1")

    canvas = Image.new("1", (size, size), 1)  # 白底
    ox = int(rx0 + (box_w - new_w) / 2)
    oy = int(ry0 + (box_h - new_h) / 2)
    canvas.paste(resized, (ox, oy))
    canvas.save(dst, "PNG")
    return "ok"


def clean_for_char(src: Path, dst: Path, ch: str, size: int, margin: int,
                   force: bool) -> str:
    """按字符类别选 spec 清洗。"""
    spec = metrics.spec_for(ch, charset_loader.classify(ch))
    return clean_one(src, dst, size, margin, force, spec)
