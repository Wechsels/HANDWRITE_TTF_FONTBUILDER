<template>
  <div class="dialog-overlay" @click.self="$emit('close')">
    <div class="dialog">
      <h3><i class="fas fa-folder-open"></i> 管理自定义字库</h3>
      <div style="margin-bottom:8px">
        <label>当前字库：</label>
        <select v-model="selectedName" @change="onSelect">
          <option v-for="n in names" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>
      <div style="margin-bottom:8px">
        <label>新建/重命名：</label>
        <input v-model="editName" style="width:160px" placeholder="输入新字库名称" />
        <button @click="onRename" :disabled="!editName.trim() || editName === '默认字库'">保存</button>
        <button class="btn-danger" @click="onDelete" :disabled="selectedName === '默认字库'">删除</button>
      </div>
      <div>
        <label>字符内容（每字一行或直接粘贴）：</label>
        <textarea
          v-model="editContent"
          rows="10"
          style="width:100%;font-family:monospace;margin-top:4px"
          placeholder="输入或粘贴要包含的字符..."
        ></textarea>
      </div>
      <div class="dialog-actions">
        <button @click="onSaveContent"><i class="fas fa-save"></i> 保存内容</button>
        <button @click="$emit('close')"><i class="fas fa-times"></i> 关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const hasApi = typeof window !== 'undefined' && 'api' in window

const emit = defineEmits<{ close: [] }>()

const names = ref<string[]>(['默认字库'])
const selectedName = ref('默认字库')
const editName = ref('')
const editContent = ref('')

onMounted(async () => {
  if (!hasApi) return
  try {
    names.value = await window.api.listCharsets()
  } catch (e) {
    console.warn('加载字库列表失败:', e)
  }
})

async function onSelect() {
  if (!hasApi) return
  editName.value = ''
  if (selectedName.value === '默认字库') {
    editContent.value = ''
    return
  }
  try {
    editContent.value = await window.api.loadChars(selectedName.value)
  } catch (e) {
    console.warn('加载字库内容失败:', e)
  }
}

async function onRename() {
  if (!hasApi) return
  const name = editName.value.trim()
  if (!name || name === '默认字库') return
  try {
    await window.api.saveCharset(name, editContent.value)
    editName.value = ''
    selectedName.value = name
    names.value = await window.api.listCharsets()
  } catch (e) {
    console.warn('保存字库失败:', e)
  }
}

async function onDelete() {
  if (!hasApi) return
  if (selectedName.value === '默认字库') return
  if (!confirm(`确定删除字库"${selectedName.value}"？`)) return
  try {
    await window.api.deleteCharset(selectedName.value)
    selectedName.value = '默认字库'
    editContent.value = ''
    names.value = await window.api.listCharsets()
  } catch (e) {
    console.warn('删除字库失败:', e)
  }
}

async function onSaveContent() {
  if (!hasApi) return
  if (selectedName.value === '默认字库') return
  try {
    const newName = await window.api.saveCharset(selectedName.value, editContent.value)
    selectedName.value = newName
    names.value = await window.api.listCharsets()
  } catch (e) {
    console.warn('保存内容失败:', e)
  }
}
</script>