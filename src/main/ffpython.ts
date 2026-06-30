import { spawnSync } from 'child_process'
import { existsSync } from 'fs'
import { join } from 'path'

export function findFfpython(): string | null {
  const candidates = [
    join('C:', 'Program Files', 'FontForgeBuilds', 'bin', 'ffpython.exe'),
    join('C:', 'Program Files (x86)', 'FontForgeBuilds', 'bin', 'ffpython.exe')
  ]
  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate
  }
  const result = spawnSync('where', ['ffpython'], { encoding: 'utf-8', timeout: 5000 })
  if (result.status === 0 && result.stdout.trim()) {
    return result.stdout.trim().split('\n')[0].trim()
  }
  return null
}
