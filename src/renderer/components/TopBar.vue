<template>
  <div class="bar top-bar">
    <span class="progress-label"><i class="fas fa-chart-bar"></i> {{ charsetStore.progressText }}</span>
    <label><i class="fas fa-database"></i> 字库:</label>
    <select :value="charsetStore.charsetName" @change="onCharsetChange">
      <option v-for="n in charsetStore.charsets" :key="n" :value="n">{{ n }}</option>
    </select>
    <button @click="showCharsetDialog = true"><i class="fas fa-cog"></i> 管理字库</button>
    <label><i class="fas fa-filter"></i> 分类:</label>
    <select :value="configStore.cfg.category" @change="onCategoryChange">
      <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
    </select>
    <label><i class="fas fa-font"></i> 字体名:</label>
    <input
      :value="configStore.cfg.font_name"
      @change="onFontNameChange"
      style="width:120px"
    />
    <span class="spacer" />

    <CharsetDialog v-if="showCharsetDialog" @close="showCharsetDialog = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useConfigStore } from '../stores/config'
import { useCharsetStore } from '../stores/charset'
import { CHARSET_CATEGORIES } from '../lib/classify'
import CharsetDialog from './CharsetDialog.vue'

const configStore = useConfigStore()
const charsetStore = useCharsetStore()
const showCharsetDialog = ref(false)

const categories = CHARSET_CATEGORIES

async function onCharsetChange(e: Event) {
  const name = (e.target as HTMLSelectElement).value
  configStore.setActiveCharset(name)
  await charsetStore.loadCharset(name)
}

async function onCategoryChange(e: Event) {
  const cat = (e.target as HTMLSelectElement).value
  configStore.setCategory(cat)
  charsetStore.setCategory(cat)
}

function onFontNameChange(e: Event) {
  configStore.setFontName((e.target as HTMLInputElement).value)
}
</script>