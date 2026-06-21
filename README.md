# HANDWRITE TTF FONTBUILDER

[English](#english) ｜ 中文（默认）

## 简介

一个桌面应用：用数位板（或鼠标）在字帖格内书写汉字 / 字母 / 标点，自动清洗、矢量化并用 FontForge 组装成可安装的 `.ttf` 手写字体。支持多列网格书写、自定义字库、字帖字体切换、主题切换（白 / 黑 / 护眼黄）、数位板与 FontForge 启动检测。

## 依赖环境

| 类型 | 依赖 | 安装 |
|---|---|---|
| Python | 3.10+ | — |
| Python 包 | PySide6, Pillow | `pip install -r requirements.txt` |
| 系统工具 | potrace（矢量化） | Windows: `scoop install potrace` / `winget install potrace`；macOS: `brew install potrace`；Linux: `apt install potrace` |
| 系统工具 | FontForge（组装 ttf） | https://fontforge.org ，装后 `ffpython` 通常在 `C:\Program Files\FontForgeBuilds\bin\ffpython.exe` |

## 运行

```shell
cd D:\Codex\CodeAgent\Code-04-HANDWRITE_TTF_FONTBUILDER
pip install -r requirements.txt
python src/main.py
```

首次启动会自动生成默认字表（数字 / 字母 / 中英文标点 / GB2312 一级汉字，共约 3863 字）。

## 用法

1. 顶栏选字库与分类，调列数 / 行数；在格内书写。
2. 点 **✓ 批量提交本页** → 自动清洗 + 矢量化入库；右侧预览实时刷新。
3. 双击格子重写单字；**重置字库**（二次确认）清空中间产物。
4. 点 **重建字库** → 调 FontForge 生成 ttf，输出到 `output/`。
5. 把 `output/xxx.ttf` 安装到系统字体即可在任何应用中使用。

## 标点 / 小写字母规格

逗号、句号等占标准字左下 1/4；分号、感叹号等占左半 1/2；省略号、破折号等占满格；小写字母占下半。规格集中在 `src/charset/metrics.py`，可调。

---

# English

A desktop app: write Chinese characters / letters / punctuation in copybook cells with a tablet (or mouse); the app auto-cleans, vectorizes, and assembles an installable `.ttf` handwriting font via FontForge. Supports multi-column grid writing, custom charsets, copybook font switching, themes (light / dark / sepia), and tablet/FontForge startup detection.

## Dependencies

| Type | Dependency | Install |
|---|---|---|
| Python | 3.10+ | — |
| Python pkgs | PySide6, Pillow | `pip install -r requirements.txt` |
| System tool | potrace (vectorize) | Windows: `scoop install potrace`; macOS: `brew install potrace`; Linux: `apt install potrace` |
| System tool | FontForge (assemble ttf) | https://fontforge.org |

## Run

```shell
cd D:\Codex\CodeAgent\Code-04-HANDWRITE_TTF_FONTBUILDER
pip install -r requirements.txt
python src/main.py
```


