import { spawn, execSync } from 'child_process'
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'fs'
import { dirname, join } from 'path'
import { RAW_DIR, CLEAN_DIR, SVG_DIR, FONT_DIR, OUTPUT_DIR, BACKEND_DIR, CANVAS_SIZE, DEFAULT_MARGIN, PROJECT_ROOT } from './paths'
import { findFfpython } from './ffpython'

function ensureDirs(): void {
  for (const d of [RAW_DIR, CLEAN_DIR, SVG_DIR, FONT_DIR, OUTPUT_DIR]) {
    mkdirSync(d, { recursive: true })
  }
}

// Writable project root passed to the Python backend via HF_PROJECT_ROOT.
// Must never resolve into resources/app.asar (an archive) — that breaks mkdir.
function getProjectRoot(): string {
  return PROJECT_ROOT
}

// Parent of the backend dir, so `from backend.pipeline...` is importable as a
// namespace package (dev: project root; packaged: resources/).
function getBackendImportRoot(): string {
  return dirname(BACKEND_DIR)
}

export interface GlyphResult {
  ok: boolean
  info: string
}

export async function processGlyph(stem: string, ch: string, dataUrl: string): Promise<GlyphResult> {
  ensureDirs()
  const rawPath = join(RAW_DIR, `${stem}.png`)
  const base64 = dataUrl.replace(/^data:image\/png;base64,/, '')
  writeFileSync(rawPath, Buffer.from(base64, 'base64'))

  const runPy = join(BACKEND_DIR, 'run.py')
  const projectRoot = getProjectRoot()
  const env = { ...process.env, HF_PROJECT_ROOT: projectRoot }

  return new Promise<GlyphResult>((resolve) => {
    const proc = spawn('python', [
      runPy, '--stem', stem, '--char', ch, '--raw', rawPath,
      '--size', String(CANVAS_SIZE), '--margin', String(DEFAULT_MARGIN)
    ], { env, timeout: 30000 })

    let stdout = ''
    let stderr = ''
    proc.stdout?.on('data', (d: Buffer) => { stdout += d.toString() })
    proc.stderr?.on('data', (d: Buffer) => { stderr += d.toString() })

    proc.on('close', (code: number | null) => {
      if (code !== 0) {
        resolve({ ok: false, info: `${stem}:${stderr.trim() || '流水线失败'}` })
        return
      }
      try {
        const parsed = JSON.parse(stdout.trim())
        resolve(parsed as GlyphResult)
      } catch {
        resolve({ ok: false, info: `${stem}:解析流水线输出失败` })
      }
    })
    proc.on('error', (err: Error) => {
      resolve({ ok: false, info: `${stem}:${err.message}` })
    })
  })
}

export interface RebuildResult {
  ok: boolean
  info: string
  ttfPath?: string
}

export function rebuildFont(name: string, ffpythonPath: string): Promise<RebuildResult> {
  const buildPy = join(BACKEND_DIR, 'pipeline', 'build_font.py')
  const ffpython = ffpythonPath || findFfpython()
  if (!ffpython) {
    return Promise.resolve({ ok: false, info: '未指定 ffpython，无法重建。请先安装 FontForge。' })
  }
  if (!existsSync(SVG_DIR)) {
    return Promise.resolve({ ok: false, info: '暂无已采集的字（03_svg/ 为空），先提交几个字。' })
  }

  return new Promise<RebuildResult>((resolve) => {
    const proc = spawn(ffpython, [
      buildPy, '--name', name, '--svg-dir', SVG_DIR, '--out-dir', FONT_DIR
    ], { timeout: 120000 })

    let stdout = ''
    let stderr = ''
    proc.stdout?.on('data', (d: Buffer) => { stdout += d.toString() })
    proc.stderr?.on('data', (d: Buffer) => { stderr += d.toString() })

    proc.on('close', (code: number | null) => {
      if (code !== 0) {
        resolve({ ok: false, info: stderr.trim().slice(0, 200) || '重建失败' })
        return
      }
      const ttf = join(FONT_DIR, `${name}.ttf`)
      if (!existsSync(ttf)) {
        resolve({ ok: false, info: `未找到生成的 ${name}.ttf` })
        return
      }
      mkdirSync(OUTPUT_DIR, { recursive: true })
      const dest = join(OUTPUT_DIR, `${name}.ttf`)
      writeFileSync(dest, readFileSync(ttf))
      resolve({ ok: true, info: `字库已重建并输出到 output/${name}.ttf`, ttfPath: dest })
    })
    proc.on('error', (err: Error) => {
      resolve({ ok: false, info: `调用 ffpython 失败: ${err.message}` })
    })
  })
}

export async function clearArtifacts(): Promise<number> {
  const cmd = execSync(
    'python -c "from backend.pipeline.cleanup import clear_artifacts; print(clear_artifacts())"',
    { cwd: getBackendImportRoot(), encoding: 'utf-8' }
  )
  return Number(cmd.trim())
}

export function previewThumbnails(_category: string): { stem: string; dataUrl: string }[] {
  if (!existsSync(CLEAN_DIR)) return []
  return readdirSync(CLEAN_DIR)
    .filter((f: string) => f.endsWith('.png'))
    .map((f) => ({
      stem: f.slice(0, -4),
      dataUrl: `data:image/png;base64,${readFileSync(join(CLEAN_DIR, f)).toString('base64')}`
    }))
}
