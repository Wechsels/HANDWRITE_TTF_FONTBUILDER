import { findFfpython } from './ffpython'

export function detectTablet(): boolean {
  // Electron doesn't expose tablet detection directly
  return false
}

export function detectFontforge(): boolean {
  return findFfpython() !== null
}
