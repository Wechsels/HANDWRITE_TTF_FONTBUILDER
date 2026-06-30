<template>
  <div class="app-shell">
    <TopBar />
    <GridPage ref="gridPageRef" @status="status = $event" />
    <OpsBar
      @submit-page="gridPageRef?.submitPage()"
      @rewrite-selected="gridPageRef?.rewriteSelected()"
      @submit-selected="gridPageRef?.submitSelected()"
      @prev-page="gridPageRef?.gotoPrev()"
      @next-page="gridPageRef?.gotoNext()"
      @jump-undone="gridPageRef?.gotoFirstUndone()"
      @reset="gridPageRef?.resetLibrary()"
      @rebuild="gridPageRef?.rebuildFont()"
    />
    <StatusBar :status="status" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useConfigStore } from './stores/config'
import { useCharsetStore } from './stores/charset'
import TopBar from './components/TopBar.vue'
import GridPage from './components/GridPage.vue'
import OpsBar from './components/OpsBar.vue'
import StatusBar from './components/StatusBar.vue'

const configStore = useConfigStore()
const charsetStore = useCharsetStore()

const gridPageRef = ref<InstanceType<typeof GridPage> | null>(null)
const status = ref('就绪。在格内书写后点"批量提交本页"。双击格子可重写。')

onMounted(async () => {
  try {
    await configStore.load()
    charsetStore.setCategory(configStore.cfg.category)
    await charsetStore.refreshCharsetList()
    await charsetStore.loadDefault()
    if (configStore.cfg.active_charset !== '默认字库') {
      await charsetStore.loadCharset(configStore.cfg.active_charset)
    }
  } catch (e) {
    console.error('[App] 初始化失败:', e)
    status.value = '初始化失败，请检查配置和字库文件。'
  }
})
</script>

<style>
@import './assets/main.css';
</style>