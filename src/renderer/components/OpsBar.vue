<template>
  <div class="bar ops-bar">
    <label><i class="fas fa-columns"></i> 列:</label>
    <div class="spin-group">
      <input type="number" :value="configStore.cfg.cols" min="1" max="20" @change="onColsChange" />
    </div>
    <label><i class="fas fa-bars"></i> 行:</label>
    <div class="spin-group">
      <input type="number" :value="configStore.cfg.rows" min="1" max="8" @change="onRowsChange" />
    </div>

    <label><i class="fas fa-pen-nib"></i> 范字字体:</label>
    <select :value="configStore.cfg.guide_font" @change="onGuideFontChange">
      <option v-for="f in guideFonts" :key="f" :value="f">{{ f }}</option>
    </select>

    <label><i class="fas fa-palette"></i> 主题:</label>
    <select :value="configStore.cfg.theme" @change="onThemeChange">
      <option v-for="t in themeNames" :key="t" :value="t">{{ t }}</option>
    </select>

    <span class="spacer" />

    <button class="btn-primary" @click="$emit('submitPage')"><i class="fas fa-check-double"></i> 批量提交本页</button>
    <button @click="$emit('rewriteSelected')"><i class="fas fa-undo"></i> 重写选中</button>
    <button @click="$emit('submitSelected')"><i class="fas fa-check"></i> 提交选中</button>
    <button @click="$emit('prevPage')"><i class="fas fa-chevron-left"></i> 上一页</button>
    <button @click="$emit('nextPage')"><i class="fas fa-chevron-right"></i> 下一页</button>
    <button @click="$emit('jumpUndone')"><i class="fas fa-forward"></i> 跳到未完成</button>
    <button class="btn-danger" @click="$emit('reset')"><i class="fas fa-trash-alt"></i> 重置</button>
    <button @click="$emit('rebuild')"><i class="fas fa-sync"></i> 重建字库</button>
  </div>
</template>

<script setup lang="ts">
import { useConfigStore } from '../stores/config'
import { THEMES } from '../lib/themes'

const configStore = useConfigStore()
const guideFonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong']
const themeNames = Object.keys(THEMES)

defineEmits<{
  submitPage: []
  rewriteSelected: []
  submitSelected: []
  prevPage: []
  nextPage: []
  jumpUndone: []
  reset: []
  rebuild: []
}>()

function onColsChange(e: Event) {
  const v = parseInt((e.target as HTMLInputElement).value) || 8
  configStore.setLayout(v, configStore.cfg.rows)
}

function onRowsChange(e: Event) {
  const v = parseInt((e.target as HTMLInputElement).value) || 2
  configStore.setLayout(configStore.cfg.cols, v)
}

function onGuideFontChange(e: Event) {
  configStore.setGuideFont((e.target as HTMLSelectElement).value)
}

function onThemeChange(e: Event) {
  configStore.setTheme((e.target as HTMLSelectElement).value)
}
</script>