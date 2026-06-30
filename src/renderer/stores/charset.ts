import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { filterByCategory } from '../lib/classify'

const hasApi = typeof window !== 'undefined' && 'api' in window

export const useCharsetStore = defineStore('charset', () => {
  const charset = ref<[string, string][]>([])
  const charsetName = ref('默认字库')
  const doneList = ref<string[]>([])
  const category = ref('全部')
  const filtered = ref<[string, string][]>([])
  const charsets = ref<string[]>(['默认字库'])

  const done = computed(() => new Set(doneList.value))

  async function loadDefault() {
    if (!hasApi) return
    try {
      charset.value = await window.api.loadDefaultCharset()
      doneList.value = await window.api.scanDone()
    } catch {
      // load already warns
    }
    applyFilter()
  }

  async function loadCharset(name: string) {
    if (!hasApi) return
    try {
      charsetName.value = name
      charset.value = await window.api.loadCharset(name)
      doneList.value = await window.api.scanDone()
    } catch {
      // load already warns
    }
    applyFilter()
  }

  function setCategory(cat: string) {
    category.value = cat
    if (charset.value.length > 0) {
      applyFilter()
    }
  }

  function applyFilter() {
    filtered.value = filterByCategory(charset.value, category.value)
  }

  async function refreshCharsetList() {
    if (!hasApi) return
    try {
      charsets.value = await window.api.listCharsets()
    } catch {
      // list already warns
    }
  }

  function markDone(stem: string) {
    if (!doneList.value.includes(stem)) {
      doneList.value.push(stem)
    }
  }

  function unmarkDone(stem: string) {
    doneList.value = doneList.value.filter(s => s !== stem)
  }

  function clearDone() {
    doneList.value = []
  }

  async function reloadDone() {
    if (!hasApi) return
    try {
      doneList.value = await window.api.scanDone()
    } catch {
      // reload already warns
    }
  }

  const progressText = computed(() =>
    `进度: ${doneList.value.length} / ${charset.value.length}`
  )

  return {
    charset, charsetName, done, category, filtered, charsets, doneList, progressText,
    loadDefault, loadCharset, setCategory, applyFilter,
    refreshCharsetList, markDone, unmarkDone, clearDone, reloadDone
  }
})