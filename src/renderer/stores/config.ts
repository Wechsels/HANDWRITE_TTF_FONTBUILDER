import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { applyTheme } from '../lib/themes'
import type { AppConfig } from '../../preload'

export type { AppConfig }

const hasApi = typeof window !== 'undefined' && 'api' in window

export const useConfigStore = defineStore('config', () => {
  const cfg = reactive<AppConfig>({
    font_name: '我的手写体',
    ffpython_path: '',
    cols: 8,
    rows: 2,
    theme: '白色',
    guide_font: 'SimHei',
    active_charset: '默认字库',
    category: '全部',
    acknowledged_no_tablet: false,
    acknowledged_no_fontforge: false
  })

  const theme = ref(applyTheme(cfg.theme))

  async function load() {
    if (!hasApi) {
      console.warn('window.api 不可用，使用默认配置')
      return
    }
    try {
      const saved = await window.api.getConfig()
      Object.assign(cfg, saved)
      theme.value = applyTheme(cfg.theme)
    } catch {
      // load already warns
    }
  }

  async function save() {
    if (!hasApi) return
    try {
      await window.api.saveConfig({ ...cfg })
    } catch {
      // save already warns
    }
  }

  function setTheme(name: string) {
    cfg.theme = name
    theme.value = applyTheme(name)
    save()
  }

  function setLayout(cols: number, rows: number) {
    cfg.cols = Math.max(1, Math.min(20, cols))
    cfg.rows = Math.max(1, Math.min(8, rows))
    save()
  }

  function setGuideFont(family: string) {
    cfg.guide_font = family
    save()
  }

  function setFontName(name: string) {
    cfg.font_name = name.trim() || '我的手写体'
    save()
  }

  function setCategory(cat: string) {
    cfg.category = cat
    save()
  }

  function setActiveCharset(name: string) {
    cfg.active_charset = name
    save()
  }

  return { cfg, theme, load, save, setTheme, setLayout, setGuideFont, setFontName, setCategory, setActiveCharset }
})