import { ipcMain, dialog, BrowserWindow } from 'electron'
import { copyFileSync, existsSync } from 'fs'
import { loadConfig, saveConfig } from './config'
import {
  listCustom, loadCharsetFile, loadChars, saveChars, deleteCharset,
  scanDone, pathFor, DEFAULT_NAME
} from './charset'
import { findFfpython } from './ffpython'
import { detectTablet, detectFontforge } from './checks'
import { processGlyph, rebuildFont, clearArtifacts, previewThumbnails } from './pipeline'
import { DEFAULT_CHARSET_PATH } from './paths'

export function registerIpcHandlers(): void {
  // ── Config ──
  ipcMain.handle('get-config', () => loadConfig())
  ipcMain.handle('save-config', (_e, cfg) => saveConfig(cfg))

  // ── Charset management ──
  ipcMain.handle('list-charsets', () => ['默认字库', ...listCustom()])
  ipcMain.handle('load-default-charset', () => loadCharsetFile(DEFAULT_CHARSET_PATH))
  ipcMain.handle('load-charset', (_e, name: string) => loadCharsetFile(pathFor(name)))
  ipcMain.handle('load-chars', (_e, name: string) => loadChars(name))
  ipcMain.handle('save-charset', (_e, name: string, chars: string) => saveChars(name, chars))
  ipcMain.handle('delete-charset', (_e, name: string) => deleteCharset(name))

  // ── Pipeline ──
  ipcMain.handle('scan-done', () => scanDone())
  ipcMain.handle('process-glyph', async (_e, payload: { stem: string; char: string; dataUrl: string }) =>
    processGlyph(payload.stem, payload.char, payload.dataUrl))
  ipcMain.handle('rebuild-font', async (_e, name: string) => {
    const cfg = loadConfig()
    return rebuildFont(name, cfg.ffpython_path)
  })

  // ── Utilities ──
  ipcMain.handle('pick-ffpython', async () => {
    const win = BrowserWindow.getFocusedWindow()
    if (!win) return null
    const result = await dialog.showOpenDialog(win, {
      title: '选择 FontForge 的 ffpython.exe',
      defaultPath: 'C:\\Program Files\\FontForgeBuilds\\bin',
      filters: [{ name: 'Executable', extensions: ['exe'] }]
    })
    if (result.canceled || result.filePaths.length === 0) return null
    return result.filePaths[0]
  })

  // Let the user choose where to save a generated TTF (save dialog).
  ipcMain.handle('pick-save-ttf', async (_e, defaultName: string) => {
    const win = BrowserWindow.getFocusedWindow()
    if (!win) return null
    const name = (defaultName || '字体').trim()
    const baseName = name.toLowerCase().endsWith('.ttf') ? name : `${name}.ttf`
    const result = await dialog.showSaveDialog(win, {
      title: '保存 TTF 字库文件',
      defaultPath: baseName,
      filters: [{ name: 'TrueType Font', extensions: ['ttf'] }]
    })
    if (result.canceled || !result.filePath) return null
    return result.filePath
  })

  // Copy a generated TTF from its build location to the user-chosen path.
  ipcMain.handle('save-ttf-to', (_e, srcPath: string, destPath: string) => {
    if (!srcPath || !destPath) return false
    if (!existsSync(srcPath)) return false
    try {
      copyFileSync(srcPath, destPath)
      return true
    } catch {
      return false
    }
  })

  ipcMain.handle('detect-tablet', () => detectTablet())
  ipcMain.handle('detect-fontforge', () => detectFontforge())
  ipcMain.handle('clear-artifacts', () => clearArtifacts())
  ipcMain.handle('preview-thumbnails', (_e, category: string) => previewThumbnails(category))
  ipcMain.handle('list-guide-fonts', () => [
    'SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong'
  ])
}