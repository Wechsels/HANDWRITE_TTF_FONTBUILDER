import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'fs'
import { CONFIG_PATH, DATA_DIR } from './paths'

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

export const THEMES = ['白色', '黑色', '护眼黄'] as const
export const THEME_LIGHT = '白色' as const

const DEFAULT_CONFIG: AppConfig = {
  font_name: '我的手写体',
  ffpython_path: '',
  cols: 8,
  rows: 2,
  theme: THEME_LIGHT,
  guide_font: 'SimHei',
  active_charset: '默认字库',
  category: '全部',
  acknowledged_no_tablet: false,
  acknowledged_no_fontforge: false
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, Math.floor(v)))
}

export function normalizeConfig(cfg: AppConfig): AppConfig {
  cfg.cols = clamp(cfg.cols, 1, 20)
  cfg.rows = clamp(cfg.rows, 1, 8)
  if (!THEMES.includes(cfg.theme as typeof THEMES[number])) {
    cfg.theme = THEME_LIGHT
  }
  return cfg
}

export function loadConfig(): AppConfig {
  if (existsSync(CONFIG_PATH)) {
    try {
      const data = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'))
      return normalizeConfig({ ...DEFAULT_CONFIG, ...data })
    } catch {
      // corrupt config, use default
    }
  }
  return { ...DEFAULT_CONFIG }
}

export function saveConfig(cfg: AppConfig): void {
  mkdirSync(DATA_DIR, { recursive: true })
  writeFileSync(CONFIG_PATH, JSON.stringify(normalizeConfig(cfg), null, 2), 'utf-8')
}
