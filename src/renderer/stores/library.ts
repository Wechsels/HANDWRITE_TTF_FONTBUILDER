import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export interface PreviewItem {
  stem: string
  dataUrl: string
}

const hasApi = typeof window !== 'undefined' && 'api' in window

export const useLibraryStore = defineStore('library', () => {
  const thumbs = reactive<PreviewItem[]>([])
  const loading = ref(false)

  async function refresh(category = '全部') {
    if (!hasApi) return
    loading.value = true
    try {
      const newThumbs = await window.api.previewThumbnails(category)
      thumbs.length = 0
      thumbs.push(...newThumbs)
    } catch (e) {
      console.warn('预览刷新失败:', e)
    } finally {
      loading.value = false
    }
  }

  function clearThumbs() {
    thumbs.length = 0
  }

  return { thumbs, loading, refresh, clearThumbs }
})