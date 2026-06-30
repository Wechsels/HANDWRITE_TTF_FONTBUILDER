import { existsSync, mkdirSync, readFileSync, readdirSync, unlinkSync, writeFileSync } from 'fs'
import { join, basename, extname } from 'path'
import { CHARSETS_DIR, DEFAULT_CHARSET_PATH, SVG_DIR } from './paths'

const DEFAULT_NAME = '默认字库'
const SAFE_RE = /[\\/:*?"<>|]/g

function safeName(name: string): string {
  return name.replace(SAFE_RE, '_').trim() || '未命名'
}

export { DEFAULT_NAME }

export function listCustom(): string[] {
  if (!existsSync(CHARSETS_DIR)) return []
  return readdirSync(CHARSETS_DIR)
    .filter(f => extname(f) === '.txt')
    .map(f => basename(f, '.txt'))
    .sort()
}

export function pathFor(name: string): string {
  if (name === DEFAULT_NAME) return DEFAULT_CHARSET_PATH
  return join(CHARSETS_DIR, `${safeName(name)}.txt`)
}

export function loadCharsetFile(p: string): [string, string][] {
  if (!existsSync(p)) return []
  const items: [string, string][] = []
  const content = readFileSync(p, 'utf-8')
  for (const line of content.split('\n')) {
    const s = line.trim()
    if (!s || s.startsWith('#')) continue
    const ch = s[0]
    const hashIdx = s.indexOf('#')
    if (hashIdx > 0) {
      const tag = s.substring(hashIdx + 1).trim()
      if (tag.startsWith('U') && tag.length === 5) {
        items.push([tag, ch])
        continue
      }
    }
    items.push([`U${ch.codePointAt(0)!.toString(16).toUpperCase().padStart(4, '0')}`, ch])
  }
  return items
}

export function loadChars(name: string): string {
  const p = pathFor(name)
  if (!existsSync(p)) return ''
  const content = readFileSync(p, 'utf-8')
  const seen = new Set<string>()
  const out: string[] = []
  for (const line of content.split('\n')) {
    const s = line.trim()
    if (!s || s.startsWith('#')) continue
    const ch = s[0]
    if (!seen.has(ch)) {
      seen.add(ch)
      out.push(ch)
    }
  }
  return out.join('')
}

export function saveChars(name: string, chars: string): string {
  name = safeName(name)
  const p = pathFor(name)
  mkdirSync(CHARSETS_DIR, { recursive: true })
  const seen = new Set<string>()
  const lines: string[] = []
  for (const ch of chars) {
    if (ch === '\n' || ch === '\r' || ch === ' ' || ch === '\t') continue
    if (!seen.has(ch)) {
      seen.add(ch)
      const cp = ch.codePointAt(0)!.toString(16).toUpperCase().padStart(4, '0')
      lines.push(`${ch}  # U${cp}`)
    }
  }
  writeFileSync(p, lines.join('\n') + '\n', 'utf-8')
  return name
}

export function deleteCharset(name: string): boolean {
  if (name === DEFAULT_NAME) return false
  const p = pathFor(name)
  if (existsSync(p)) {
    unlinkSync(p)
    return true
  }
  return false
}

export function scanDone(): string[] {
  if (!existsSync(SVG_DIR)) return []
  return readdirSync(SVG_DIR)
    .filter(f => extname(f) === '.svg')
    .map(f => basename(f, '.svg'))
}

const _CN_PUNCT_CODES: number[] = [
  0xFF0C, 0x3002, 0x3001, 0xFF1B, 0xFF01, 0xFF1F, 0xFF1A,
  0x201C, 0x201D, 0x2018, 0x2019, 0xFF08, 0xFF09,
  0x3010, 0x3011, 0x300A, 0x300B, 0x300C, 0x300D,
  0x300E, 0x300F, 0x2014, 0x2026, 0x30FB, 0xFF5E
]

const _EN_PUNCT_CODES: number[] = [
  0x002C, 0x002E, 0x0021, 0x003F, 0x003B, 0x003A,
  0x0027, 0x0022, 0x0028, 0x0029, 0x005B, 0x005D,
  0x007B, 0x007D, 0x002D, 0x005F, 0x002F, 0x005C,
  0x0040, 0x0023, 0x0026, 0x002A
]

const _CN_PUNCT_SET = new Set(_CN_PUNCT_CODES.map(c => String.fromCodePoint(c)))
const _EN_PUNCT_SET = new Set(_EN_PUNCT_CODES.map(c => String.fromCodePoint(c)))

export function classify(ch: string): string {
  const cp = ch.codePointAt(0)!
  if (cp >= 0x30 && cp <= 0x39) return '数字'
  if (cp >= 0x41 && cp <= 0x5A) return '大写字母'
  if (cp >= 0x61 && cp <= 0x7A) return '小写字母'
  if (_CN_PUNCT_SET.has(ch)) return '中文标点'
  if (_EN_PUNCT_SET.has(ch)) return '英文标点'
  if (cp >= 0x4E00 && cp <= 0x9FFF) return '汉字'
  return '全部'
}

export function filterByCategory(charset: [string, string][], category: string): [string, string][] {
  if (category === '全部') return charset
  return charset.filter(([, ch]) => classify(ch) === category)
}

export const CHARSET_CATEGORIES = [
  '全部',
  '数字',
  '大写字母',
  '小写字母',
  '中文标点',
  '英文标点',
  '汉字'
]