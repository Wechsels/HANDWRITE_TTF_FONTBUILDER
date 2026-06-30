export interface Theme {
  name: string
  bg: string
  fg: string
  accent: string
  guideChar: string
  guideLine: string
  baseDir: string
}

export const THEMES: Record<string, Theme> = {
  '白色': {
    name: '白色', bg: '#FFFFFF', fg: '#1A1A1A', accent: '#1F6FB3',
    guideChar: '#DADADA', guideLine: 'rgba(200,40,40,0.6)', baseDir: '#F2F2F2'
  },
  '黑色': {
    name: '黑色', bg: '#1E1E22', fg: '#ECECEC', accent: '#4FA3E0',
    guideChar: '#3A3A40', guideLine: 'rgba(220,80,80,0.63)', baseDir: '#26262C'
  },
  '护眼黄': {
    name: '护眼黄', bg: '#F5E6C8', fg: '#3E2C18', accent: '#9A4A1A',
    guideChar: '#C9B489', guideLine: 'rgba(170,50,40,0.6)', baseDir: '#EEDDB8'
  }
}

export function theme(name: string): Theme {
  return THEMES[name] || THEMES['白色']
}

export function applyTheme(name: string): Theme {
  const t = theme(name)
  const root = document.documentElement
  root.dataset.theme = name
  root.style.setProperty('--bg', t.bg)
  root.style.setProperty('--fg', t.fg)
  root.style.setProperty('--accent', t.accent)
  root.style.setProperty('--base-dir', t.baseDir)
  root.style.setProperty('--guide-char', t.guideChar)
  root.style.setProperty('--guide-line', t.guideLine)
  return t
}
