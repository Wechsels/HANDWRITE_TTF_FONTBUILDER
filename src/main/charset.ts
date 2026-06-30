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