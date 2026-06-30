import type { GlyphSpec } from './metrics'
import { _SPECS, _DEFAULT } from './metrics'

export const ALL = '全部'
export const DIGIT = '数字'
export const UPPER = '大写字母'
export const LOWER = '小写字母'
export const CN_PUNCT = '中文标点'
export const EN_PUNCT = '英文标点'
export const HANZI = '汉字'

export const CHARSET_CATEGORIES = [ALL, DIGIT, UPPER, LOWER, CN_PUNCT, EN_PUNCT, HANZI]

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
  if (cp >= 0x30 && cp <= 0x39) return DIGIT
  if (cp >= 0x41 && cp <= 0x5A) return UPPER
  if (cp >= 0x61 && cp <= 0x7A) return LOWER
  if (_CN_PUNCT_SET.has(ch)) return CN_PUNCT
  if (_EN_PUNCT_SET.has(ch)) return EN_PUNCT
  if (cp >= 0x4E00 && cp <= 0x9FFF) return HANZI
  return ALL
}

export function filterByCategory(charset: [string, string][], category: string): [string, string][] {
  if (category === ALL) return charset
  if (!Array.isArray(charset)) return []
  return charset.filter(([, ch]) => classify(ch) === category)
}

const _QUARTER_CODES = [0xFF0C, 0x3002, 0x3001]
const _HALF_CODES = [0xFF1B, 0xFF01, 0xFF1F, 0xFF1A]

const _QUARTER_SET = new Set(_QUARTER_CODES.map(c => String.fromCodePoint(c)))
const _HALF_SET = new Set(_HALF_CODES.map(c => String.fromCodePoint(c)))

export function classifyChar(ch: string, baseCat: string): string {
  if (baseCat === CN_PUNCT) {
    if (_QUARTER_SET.has(ch)) return '中标点-句读'
    if (_HALF_SET.has(ch)) return '中标点-竖向'
    return '中标点-满格'
  }
  return baseCat
}

export function specFor(ch: string, baseCat: string): GlyphSpec {
  return _SPECS[classifyChar(ch, baseCat)] || _DEFAULT
}