export interface GlyphSpec {
  region: [number, number, number, number]
  advance: number
}

export const SPECS: Record<string, GlyphSpec> = {
  '中标点-句读': { region: [0.00, 0.50, 0.50, 1.00], advance: 0.5 },
  '中标点-竖向': { region: [0.00, 0.00, 0.50, 1.00], advance: 0.5 },
  '中标点-满格': { region: [0.04, 0.04, 0.96, 0.96], advance: 1.0 },
  '小写字母': { region: [0.00, 0.50, 1.00, 1.00], advance: 0.6 },
  '数字': { region: [0.06, 0.06, 0.94, 0.94], advance: 0.6 },
  '大写字母': { region: [0.06, 0.06, 0.94, 0.94], advance: 0.6 },
  '汉字': { region: [0.02, 0.02, 0.98, 0.98], advance: 1.0 },
  '英文标点': { region: [0.25, 0.25, 0.75, 0.75], advance: 0.4 },
}

export const DEFAULT_SPEC: GlyphSpec = { region: [0.04, 0.04, 0.96, 0.96], advance: 1.0 }

// Legacy aliases for backward compatibility
export const _SPECS = SPECS
export const _DEFAULT = DEFAULT_SPEC
