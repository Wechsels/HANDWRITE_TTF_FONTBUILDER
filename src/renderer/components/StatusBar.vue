<template>
  <div class="status-bar">
    <i class="fas fa-info-circle"></i> {{ status }}
  </div>
</template>

<script setup lang="ts">
defineProps<{ status: string }>()
</script>