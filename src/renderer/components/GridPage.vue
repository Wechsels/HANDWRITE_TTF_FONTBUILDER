<template>
  <div class="main-area">
    <div class="grid-container">
      <div class="grid" :style="gridStyle">
        <CopybookCell
          v-for="(item, i) in pageCells"
          :key="item[0]"
          :ref="(el: any) => setCellRef(i, el)"
          :stem="item[0]"
          :char="item[1]"
          :cell-size="CELL_SIZE"
          :pen-max="PEN_MAX"
          :theme="themeObj"
          :guide-font="configStore.cfg.guide_font"
          :is-submitted="charsetStore.done.has(item[0])"
          :model-value="selectedIndex === (pageStart + i)"
          :saved-strokes="strokesCache.get(item[0]) || null"
          @select="onCellSelect(pageStart + i)"
          @rewrite="onCellRewrite(pageStart + i)"
          @save-stroke="onSaveStroke"
        />
        <div v-if="pageCells.length === 0" style="grid-column:1/-1;text-align:center;padding:40px;color:var(--border)">
          <span v-if="charsetStore.charset.length > 0">暂无该分类下的字符</span>
          <span v-if="charsetStore.charset.length === 0">加载中…</span>
        </div>
      </div>
    </div>
    <div class="dock">
      <div class="dock-title"><i class="fas fa-book-open"></i> 字库预览</div>
      <div v-if="libraryStore.loading" style="font-size:12px;color:var(--border)">加载中…</div>
      <div
        v-for="t in libraryStore.thumbs"
        :key="t.stem"
        class="dock-thumb"
      >
        <img :src="t.dataUrl" :alt="t.stem" />
      </div>
      <div v-if="!libraryStore.loading && libraryStore.thumbs.length === 0" style="font-size:11px;color:var(--border)">
        暂无预览，请先提交字
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useConfigStore } from '../stores/config'
import { useCharsetStore } from '../stores/charset'
import { useLibraryStore } from '../stores/library'
import { theme as getTheme } from '../lib/themes'
import CopybookCell from './CopybookCell.vue'

const CELL_SIZE = 220
const PEN_MAX = Math.max(4, CELL_SIZE / 30)

const configStore = useConfigStore()
const charsetStore = useCharsetStore()
const libraryStore = useLibraryStore()

const pageStart = ref(0)
const selectedIndex = ref<number | null>(null)
const strokesCache = new Map<string, ImageData>()
const cellRefs = new Map<number, any>()

const themeObj = computed(() => getTheme(configStore.cfg.theme))
const pageSize = computed(() => configStore.cfg.cols * configStore.cfg.rows)

const pageCells = computed(() => {
  const start = pageStart.value
  const end = start + pageSize.value
  const data = charsetStore.filtered
  if (!data || !Array.isArray(data)) return []
  return data.slice(start, end)
})

const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(${configStore.cfg.cols}, ${CELL_SIZE}px)`
}))

function setCellRef(i: number, el: any) {
  if (el) {
    cellRefs.set(i, el)
  } else {
    cellRefs.delete(i)
  }
}

function onSaveStroke(stem: string, data: ImageData | null) {
  if (data) {
    strokesCache.set(stem, data)
  } else {
    strokesCache.delete(stem)
  }
}

function onCellSelect(idx: number) {
  selectedIndex.value = idx
  const item = charsetStore.filtered[idx]
  if (item) {
    emitStatus(`已选中 ${item[1]} (${item[0]})`)
  }
}

function onCellRewrite(idx: number) {
  selectedIndex.value = idx
  const item = charsetStore.filtered[idx]
  if (!item) return

  // Clear canvas and remove cached strokes
  const localIdx = idx - pageStart.value
  cellRefs.get(localIdx)?.clearStrokes()
  strokesCache.delete(item[0])
  charsetStore.unmarkDone(item[0])
  emitStatus(`已清空 ${item[1]}，请重写后点"提交选中格"。`)
}

const emit = defineEmits<{ status: [msg: string] }>()
const emitStatus = (msg: string) => emit('status', msg)

function gotoPrev() {
  pageStart.value = Math.max(0, pageStart.value - pageSize.value)
}

function gotoNext() {
  const n = charsetStore.filtered.length
  const ps = pageSize.value
  if (ps <= 0 || n === 0) return
  const lastPageStart = Math.floor((n - 1) / ps) * ps
  pageStart.value = Math.min(lastPageStart, pageStart.value + ps)
  pageStart.value = Math.floor(pageStart.value / ps) * ps
}

function gotoFirstUndone() {
  const items = charsetStore.filtered
  const doneSet = charsetStore.done.value
  const ps = pageSize.value
  for (let i = 0; i < items.length; i++) {
    if (!doneSet.has(items[i][0])) {
      pageStart.value = Math.floor(i / ps) * ps
      return
    }
  }
  pageStart.value = 0
}

const hasApi = typeof window !== 'undefined' && 'api' in window

async function submitPage() {
  if (!hasApi) { emitStatus('当前环境不支持提交'); return }
  let ok = 0, fail = 0, skipped = 0
  const failList: string[] = []
  const ps = pageSize.value
  const start = pageStart.value

  for (let i = 0; i < ps; i++) {
    const cellRef = cellRefs.get(i)
    if (!cellRef) continue
    if (cellRef.isBlank()) { skipped++; continue }
    const item = charsetStore.filtered[start + i]
    if (!item) continue
    try {
      const result = await window.api.processGlyph({
        stem: item[0], char: item[1], dataUrl: cellRef.savePng()
      })
      if (result.ok) { ok++; charsetStore.markDone(item[0]) }
      else { fail++; failList.push(result.info) }
    } catch (e: any) {
      fail++; failList.push(`${item[0]}:${e.message}`)
    }
  }

  let msg = `本页已提交：成功 ${ok} 字`
  if (fail) msg += `，失败 ${fail} (${failList.slice(0, 5).join(', ')})`
  if (skipped) msg += `，跳过空白 ${skipped}`
  emitStatus(msg)
  libraryStore.refresh()
}

async function submitSelected() {
  if (!hasApi) { emitStatus('当前环境不支持提交'); return }
  if (selectedIndex.value === null) { emitStatus('⚠ 请先点选一个格子再提交。'); return }
  const idx = selectedIndex.value
  const cellRef = cellRefs.get(idx - pageStart.value)
  if (!cellRef) return
  const item = charsetStore.filtered[idx]
  if (!item) return
  try {
    const result = await window.api.processGlyph({
      stem: item[0], char: item[1], dataUrl: cellRef.savePng()
    })
    if (result.ok) charsetStore.markDone(item[0])
    emitStatus(result.ok ? `✓ 已提交 ${item[1]}` : `✗ 提交失败 ${result.info}`)
  } catch (e: any) {
    emitStatus(`✗ 提交错误: ${e.message}`)
  }
  libraryStore.refresh()
}

function rewriteSelected() {
  if (selectedIndex.value === null) { emitStatus('⚠ 请先点选/双击一个格子再重写。'); return }
  onCellRewrite(selectedIndex.value)
}

async function resetLibrary() {
  if (!hasApi) { emitStatus('当前环境不支持重置'); return }
  if (!confirm('将清除所有已采集手写记录与缓存(01_raw~04_font)。\n不会删除 output/ 已生成的 ttf。\n\n确定继续？')) return
  if (!confirm('再次确认：此操作不可撤销，所有采集进度将丢失！\n是否执行？')) return
  try {
    for (const i of cellRefs.keys()) cellRefs.get(i)?.clearStrokes()
    strokesCache.clear()
    const removed = await window.api.clearArtifacts()
    charsetStore.clearDone()
    await charsetStore.reloadDone()
    charsetStore.applyFilter()
    libraryStore.clearThumbs()
    pageStart.value = 0
    selectedIndex.value = null
    emitStatus(`已清空 ${removed} 个中间产物文件。`)
  } catch (e: any) {
    emitStatus(`重置失败: ${e.message}`)
  }
}

async function rebuildFont() {
  if (!hasApi) { emitStatus('当前环境不支持重建'); return }
  const name = configStore.cfg.font_name
  try {
    const result = await window.api.rebuildFont(name)
    emitStatus(result.ok ? `✓ 字库已重建并输出到 output/${name}.ttf` : `✗ 重建失败: ${result.info}`)
    if (result.ok) libraryStore.refresh()
  } catch (e: any) {
    emitStatus(`重建错误: ${e.message}`)
  }
}

watch([() => configStore.cfg.cols, () => configStore.cfg.rows], () => {
  const ps = pageSize.value
  if (ps > 0) pageStart.value = Math.floor(pageStart.value / ps) * ps
})

defineExpose({
  gotoPrev, gotoNext, gotoFirstUndone,
  submitPage, submitSelected, rewriteSelected,
  resetLibrary, rebuildFont, emitStatus
})
</script>