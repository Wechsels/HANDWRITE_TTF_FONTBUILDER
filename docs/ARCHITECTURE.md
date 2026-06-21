# 架构说明

## 数据流

```
数位板书写 → workspace/01_raw/UXXXX.png
clean.py   → workspace/02_clean/UXXXX.png  (二值化/裁边/按规格放置)
trace.py   → workspace/03_svg/UXXXX.svg    (potrace 矢量化)
build_font → workspace/04_font/xxx.ttf     (FontForge 组装)
copy       → output/xxx.ttf
```

## 模块职责

- `src/paths.py` — 全局路径常量，PROJECT_ROOT = parents[1]。
- `src/config.py` — AppConfig 数据类 + JSON 持久化。
- `src/charset/loader.py` — 字表解析 + classify 分类。
- `src/charset/metrics.py` — 字形规格表（功能 10/11 单一真相源）：placement region + advance。
- `src/charset/manager.py` — 自定义字库 CRUD + 命名（功能 2/4）。
- `src/pipeline/clean.py` — clean_one 按 GlyphSpec 放置前景（非总居中）。
- `src/pipeline/trace.py` — potrace 矢量化。
- `src/pipeline/build_font.py` — FontForge 组装，advance 读 metrics。
- `src/pipeline/pipeline.py` — 单字 clean+trace 编排。
- `src/pipeline/cleanup.py` — 清空中间产物（保留 .gitkeep）。
- `src/gui/theme.py` — 主题（白/黑/护眼黄）+ qss。
- `src/gui/cell.py` — 字帖格：米字格 + 目标区高亮 + 压感 + 范字字体。
- `src/gui/grid_page.py` — 行列网格分页（功能 1）。
- `src/gui/preview.py` — 字库即时预览。
- `src/gui/charset_dialog.py` — 自定义字库编辑（功能 2/4）。
- `src/gui/main_window.py` — 主窗口编排（瘦）。
- `src/platform/checks.py` — 数位板 / FontForge 检测（功能 6/7）。
- `src/platform/ffpython.py` — 定位 ffpython。
- `src/services/` — 付费预留接口（OCR / AI 学习，未实装）。

## 关键设计

- **字形规格**：clean 按 `metrics.spec_for(ch)` 的 region 放置前景；build_font 按 advance 设字宽。画布尺寸 = EM(1000)，SVG 坐标 1:1 映射字体空间。
- **主题**：调色板 + qss 统一注入，对比色保证可读。
- **重置**：二次确认，删中间产物不动 output/。
- **导入约定**：扁平绝对导入 + main.py 注入 src/ 到 sys.path，PyInstaller 与直跑通用。
