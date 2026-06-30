<template>
  <div
    class="cell"
    :class="{ selected: modelValue, submitted: isSubmitted }"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointerleave="onPointerUp"
    @dblclick="$emit('rewrite')"
  >
    <canvas ref="guideCanvas" class="guide-layer" />
    <canvas ref="strokeCanvas" class="stroke-layer" />
    <span class="cell-stem">{{ stem }}</span>
    <span v-if="isSubmitted" class="cell-check">✓</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import type { Theme } from '../lib/themes'
import { classifyChar, classify as baseClassify } from '../lib/classify'
import { SPECS, DEFAULT_SPEC } from '../lib/metrics'

const props = defineProps<{
  stem: string
  char: string
  cellSize: number
  penMax: number
  theme: Theme
  guideFont: string
  isSubmitted: boolean
  modelValue: boolean
  savedStrokes: ImageData | null
}>()

const emit = defineEmits<{
  select: []
  rewrite: []
  'update:modelValue': [v: boolean]
  'saveStroke': [stem: string, data: ImageData | null]
}>()

const guideCanvas = ref<HTMLCanvasElement | null>(null)
const strokeCanvas = ref<HTMLCanvasElement | null>(null)

let guideCtx: CanvasRenderingContext2D | null = null
let strokeCtx: CanvasRenderingContext2D | null = null
let lastPos: { x: number; y: number } | null = null
let moved = false
let drawing = false

const dpr = window.devicePixelRatio || 1

function initCanvases() {
  const size = props.cellSize
  for (const refEl of [guideCanvas.value, strokeCanvas.value]) {
    if (!refEl) continue
    refEl.width = size * dpr
    refEl.height = size * dpr
    refEl.style.width = size + 'px'
    refEl.style.height = size + 'px'
  }
  guideCtx = guideCanvas.value!.getContext('2d')!
  strokeCtx = strokeCanvas.value!.getContext('2d')!
  strokeCtx.setTransform(dpr, 0, 0, dpr, 0, 0)
  guideCtx.setTransform(dpr, 0, 0, dpr, 0, 0)
  renderGuide()
  if (props.savedStrokes) {
    strokeCtx.setTransform(1, 0, 0, 1, 0, 0)
    strokeCtx.putImageData(props.savedStrokes, 0, 0)
    strokeCtx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }
}

function renderGuide() {
  if (!guideCtx) return
  const size = props.cellSize
  const ctx = guideCtx
  ctx.clearRect(0, 0, size, size)

  ctx.fillStyle = props.theme.bg
  ctx.fillRect(0, 0, size, size)

  ctx.fillStyle = props.theme.guideChar
  ctx.font = `${size * 0.55}px ${props.guideFont || 'SimHei'}`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(props.char, size / 2, size / 2)

  if (props.char) {
    const baseCat = baseClassify(props.char)
    const cat = classifyChar(props.char, baseCat)
    const spec = SPECS[cat] || DEFAULT_SPEC
    if (spec) {
      const [rx0, ry0, rx1, ry1] = spec.region
      ctx.strokeStyle = props.theme.accent
      ctx.lineWidth = 1.4
      ctx.setLineDash([4, 4])
      ctx.strokeRect(rx0 * size, ry0 * size, (rx1 - rx0) * size, (ry1 - ry0) * size)
      ctx.setLineDash([])
    }
  }

  ctx.strokeStyle = props.theme.guideLine
  ctx.lineWidth = 1
  ctx.setLineDash([3, 3])
  ctx.beginPath()
  ctx.moveTo(size / 2, 0); ctx.lineTo(size / 2, size)
  ctx.moveTo(0, size / 2); ctx.lineTo(size, size / 2)
  ctx.moveTo(0, 0); ctx.lineTo(size, size)
  ctx.moveTo(size, 0); ctx.lineTo(0, size)
  ctx.stroke()
  ctx.setLineDash([])
}

function getPressure(e: PointerEvent): number {
  return e.pressure > 0 ? e.pressure : 0.5
}

function getWidth(pressure: number): number {
  if (pressure > 0.01) return 1 + pressure * (props.penMax - 1)
  return Math.max(2, props.penMax * 0.5)
}

function strokeTo(x: number, y: number, width: number) {
  if (!strokeCtx) return
  if (!lastPos) { lastPos = { x, y }; return }
  const ctx = strokeCtx
  ctx.strokeStyle = '#101010'
  ctx.lineWidth = width
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.beginPath()
  ctx.moveTo(lastPos.x, lastPos.y)
  ctx.lineTo(x, y)
  ctx.stroke()
  lastPos = { x, y }
}

function onPointerDown(e: PointerEvent) {
  if (e.button !== 0) return
  drawing = true
  moved = false
  const rect = strokeCanvas.value!.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  lastPos = { x, y }
  const w = getWidth(getPressure(e))
  strokeTo(x, y, w)
  strokeCanvas.value!.setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!drawing) return
  moved = true
  const rect = strokeCanvas.value!.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const w = getWidth(getPressure(e))
  strokeTo(x, y, w)
}

function onPointerUp(e: PointerEvent) {
  if (!drawing) return
  drawing = false
  lastPos = null
  if (!moved) {
    emit('select')
  } else {
    saveCurrentStrokes()
  }
}

function isBlank(): boolean {
  if (!strokeCtx) return true
  const size = props.cellSize
  const physW = Math.round(size * dpr)
  const physH = Math.round(size * dpr)
  const imgData = strokeCtx.getImageData(0, 0, physW, physH)
  for (let y = 0; y < physH; y += Math.max(1, Math.round(4 * dpr))) {
    for (let x = 0; x < physW; x += Math.max(1, Math.round(4 * dpr))) {
      if (imgData.data[(y * physW + x) * 4 + 3] > 20) return false
    }
  }
  return true
}

function getStrokeData(): ImageData | null {
  if (!strokeCtx) return null
  const size = props.cellSize
  const physW = Math.round(size * dpr)
  const physH = Math.round(size * dpr)
  return strokeCtx.getImageData(0, 0, physW, physH)
}

function savePng(): string {
  const size = props.cellSize
  const canvas = document.createElement('canvas')
  canvas.width = size * dpr
  canvas.height = size * dpr
  const ctx = canvas.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.fillStyle = '#FFFFFF'
  ctx.fillRect(0, 0, size, size)
  if (strokeCanvas.value) {
    ctx.drawImage(strokeCanvas.value, 0, 0, size, size)
  }
  return canvas.toDataURL('image/png')
}

function clearStrokes() {
  if (!strokeCtx) return
  const size = props.cellSize
  strokeCtx.clearRect(0, 0, size, size)
  lastPos = null
}

function saveCurrentStrokes() {
  emit('saveStroke', props.stem, getStrokeData())
}

defineExpose({ isBlank, savePng, clearStrokes, saveCurrentStrokes })

onMounted(() => {
  nextTick(() => initCanvases())
})

watch(() => props.savedStrokes, (data) => {
  if (!strokeCtx) return
  const size = props.cellSize
  if (data) {
    strokeCtx.setTransform(1, 0, 0, 1, 0, 0)
    strokeCtx.putImageData(data, 0, 0)
    strokeCtx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }
})

watch([() => props.theme, () => props.guideFont, () => props.char], () => {
  if (guideCtx) renderGuide()
})
</script>