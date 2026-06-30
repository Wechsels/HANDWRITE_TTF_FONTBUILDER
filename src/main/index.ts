import { app, BrowserWindow, shell } from 'electron'
import { join } from 'path'
import { existsSync, mkdirSync, copyFileSync } from 'fs'
import { is } from '@electron-toolkit/utils'
import { registerIpcHandlers } from './ipc'
import { DEFAULT_CHARSET_PATH } from './paths'

// Packaged builds ship the default charset under resources/ (via extraResources),
// but the app reads it from userData/. Seed it on first run so it is readable.
function seedDefaultCharset(): void {
  if (is.dev) return
  if (existsSync(DEFAULT_CHARSET_PATH)) return
  const bundled = join(process.resourcesPath!, 'data', 'default_charset.txt')
  if (!existsSync(bundled)) return
  try {
    mkdirSync(join(DEFAULT_CHARSET_PATH, '..'), { recursive: true })
    copyFileSync(bundled, DEFAULT_CHARSET_PATH)
  } catch {
    // best-effort; loadDefault() will just yield an empty charset
  }
}

let mainWindow: BrowserWindow | null = null

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1320,
    height: 760,
    minWidth: 900,
    minHeight: 600,
    show: false,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow!.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

app.whenReady().then(() => {
  seedDefaultCharset()
  registerIpcHandlers()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
