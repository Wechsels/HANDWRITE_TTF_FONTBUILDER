import { contextBridge, ipcRenderer } from 'electron'

export interface AppConfig {
  font_name: string
  ffpython_path: string
  cols: number
  rows: number
  theme: string
  guide_font: string
  active_charset: string
  category: string
  acknowledged_no_tablet: boolean
  acknowledged_no_fontforge: boolean
}

export interface GlyphResult {
  ok: boolean
  info: string
}

export interface PreviewItem {
  stem: string
  dataUrl: string
}

export interface ElectronAPI {
  getConfig: () => Promise<AppConfig>
  saveConfig: (cfg: AppConfig) => Promise<void>
  listCharsets: () => Promise<string[]>
  loadDefaultCharset: () => Promise<[string, string][]>
  loadCharset: (name: string) => Promise<[string, string][]>
  loadChars: (name: string) => Promise<string>
  saveCharset: (name: string, chars: string) => Promise<string>
  deleteCharset: (name: string) => Promise<boolean>
  scanDone: () => Promise<string[]>
  processGlyph: (payload: { stem: string; char: string; dataUrl: string }) => Promise<GlyphResult>
  rebuildFont: (name: string) => Promise<GlyphResult>
  pickFfpython: () => Promise<string | null>
  detectTablet: () => Promise<boolean>
  detectFontforge: () => Promise<boolean>
  clearArtifacts: () => Promise<number>
  previewThumbnails: (category: string) => Promise<PreviewItem[]>
  listGuideFonts: () => Promise<string[]>
  onProgress: (cb: (msg: string) => void) => () => void
}

const api: ElectronAPI = {
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (cfg) => ipcRenderer.invoke('save-config', cfg),
  listCharsets: () => ipcRenderer.invoke('list-charsets'),
  loadDefaultCharset: () => ipcRenderer.invoke('load-default-charset'),
  loadCharset: (name) => ipcRenderer.invoke('load-charset', name),
  loadChars: (name) => ipcRenderer.invoke('load-chars', name),
  saveCharset: (name, chars) => ipcRenderer.invoke('save-charset', name, chars),
  deleteCharset: (name) => ipcRenderer.invoke('delete-charset', name),
  scanDone: () => ipcRenderer.invoke('scan-done'),
  processGlyph: (payload) => ipcRenderer.invoke('process-glyph', payload),
  rebuildFont: (name) => ipcRenderer.invoke('rebuild-font', name),
  pickFfpython: () => ipcRenderer.invoke('pick-ffpython'),
  detectTablet: () => ipcRenderer.invoke('detect-tablet'),
  detectFontforge: () => ipcRenderer.invoke('detect-fontforge'),
  clearArtifacts: () => ipcRenderer.invoke('clear-artifacts'),
  previewThumbnails: (category) => ipcRenderer.invoke('preview-thumbnails', category),
  listGuideFonts: () => ipcRenderer.invoke('list-guide-fonts'),
  onProgress: (cb) => {
    const handler = (_e: Electron.IpcRendererEvent, msg: string) => cb(msg)
    ipcRenderer.on('progress', handler)
    return () => ipcRenderer.removeListener('progress', handler)
  }
}

contextBridge.exposeInMainWorld('api', api)
