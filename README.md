# Handwrite TTF FontBuilder / 手写字体生成器

[English](#english) ｜ 中文（默认）

## 简介

一个桌面应用：用数位板（或鼠标）在字帖格内书写汉字 / 字母 / 标点，自动清洗、矢量化并用 FontForge 组装成可安装的 `.ttf` 手写字体。支持多列网格书写、自定义字库、字帖字体切换、主题切换（白 / 黑 / 护眼黄）、数位板与 FontForge 启动检测。

## 依赖环境

| 类型 | 依赖 | 安装 |
|---|---|---|
| Node.js | 18+ | — |
| Python | 3.10+ | — |
| Python 包 | Pillow 等（后端） | `pip install -r backend/requirements.txt` |
| npm 包 | Vue 3, Electron 等 | `npm install` |
| 系统工具 | potrace（矢量化） | Windows: `scoop install potrace` / `winget install potrace`；macOS: `brew install potrace`；Linux: `apt install potrace` |
| 系统工具 | FontForge（组装 ttf） | https://fontforge.org ，装后 `ffpython` 通常在 `C:\Program Files\FontForgeBuilds\bin\ffpython.exe` |

## 运行

```shell
npm install
pip install -r backend/requirements.txt
npm run dev
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

## 许可证

[![License: WNCPL v1.0](https://img.shields.io/badge/License-WNCPL%20v1.0-orange.svg)](LICENSE)

本项目基于 **Wechsels 非商用许可证 v1.0 (WNCPL v1.0)** 发布。

- 允许:查看、修改、非商业场景下分发
- 禁止:任何形式的商用
- 强制:保留版权声明与许可证副本；衍生作品必须使用本协议

详情请参阅 [LICENSE](LICENSE) 文件。Copyright (c) 2026 Yurui He (GitHub: Wechsels)。

---

# English

A desktop app: write Chinese characters / letters / punctuation in copybook cells with a tablet (or mouse); the app auto-cleans, vectorizes, and assembles an installable `.ttf` handwriting font via FontForge. Supports multi-column grid writing, custom charsets, copybook font switching, themes (light / dark / sepia), and tablet/FontForge startup detection.

## Dependencies

| Type | Dependency | Install |
|---|---|---|
| Node.js | 18+ | — |
| Python | 3.10+ | — |
| Python pkgs | Pillow (backend) | `pip install -r backend/requirements.txt` |
| npm pkgs | Vue 3, Electron etc. | `npm install` |
| System tool | potrace (vectorize) | Windows: `scoop install potrace`; macOS: `brew install potrace`; Linux: `apt install potrace` |
| System tool | FontForge (assemble ttf) | https://fontforge.org |

## Run

```shell
npm install
pip install -r backend/requirements.txt
npm run dev
```

## Usage

1. Select a charset and category in the top bar; adjust columns / rows; write in cells.
2. Click **batch submit** button to clean + vectorize; preview updates on the right.
3. Double-click a cell to redo a character; **reset** clears intermediate files.
4. Click **rebuild font** to generate a `.ttf` via FontForge, output to `output/`.
5. Install the `.ttf` from `output/` to use in any application.

## License

[![License: WNCPL v1.0](https://img.shields.io/badge/License-WNCPL%20v1.0-orange.svg)](LICENSE)

This project is released under the **Wechsels Non-Commercial License v1.0 (WNCPL v1.0)**.

- Allowed: view, modify, redistribute for non-commercial purposes
- Prohibited: any form of commercial use
- Required: retain copyright notice and license copy; derivative works must use this license

See the [LICENSE](LICENSE) file for full terms. Copyright (c) 2026 Yurui He (GitHub: Wechsels).


