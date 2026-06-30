import { app } from 'electron'
import { join, resolve } from 'path'
import { is } from '@electron-toolkit/utils'

const RESOURCE_ROOT = is.dev
  ? resolve(__dirname, '..', '..')
  : join(app.getPath('userData'), '..')

export const RESOURCE_ROOT_PATH = RESOURCE_ROOT
export const PROJECT_ROOT = RESOURCE_ROOT

export const DATA_DIR = join(PROJECT_ROOT, 'data')
export const WORKSPACE_DIR = join(PROJECT_ROOT, 'workspace')
export const OUTPUT_DIR = join(PROJECT_ROOT, 'output')
export const LOG_DIR = join(PROJECT_ROOT, 'logs')

export const RAW_DIR = join(WORKSPACE_DIR, '01_raw')
export const CLEAN_DIR = join(WORKSPACE_DIR, '02_clean')
export const SVG_DIR = join(WORKSPACE_DIR, '03_svg')
export const FONT_DIR = join(WORKSPACE_DIR, '04_font')

export const CONFIG_PATH = join(DATA_DIR, 'config.json')
export const CHARSETS_DIR = join(DATA_DIR, 'charsets')
export const DEFAULT_CHARSET_PATH = is.dev
  ? join(RESOURCE_ROOT, 'data', 'default_charset.txt')
  : join(app.getPath('userData'), 'data', 'default_charset.txt')

export const CANVAS_SIZE = 1000
export const DEFAULT_MARGIN = 30

export const BACKEND_DIR = is.dev
  ? join(RESOURCE_ROOT, 'backend')
  : join(process.resourcesPath!, 'backend')