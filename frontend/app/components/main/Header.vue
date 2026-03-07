<template>
  <div class="page-header">
    <h1 class="page-title">Projects</h1>

    <n-button type="primary" class="create-btn" ghost @click="setShow = true">
      <template #icon>
        <Icon name="ph:plus-bold" />
      </template>
      Create Project
    </n-button>
  </div>
</template>

<script setup lang="ts">
  const setShow = defineModel<boolean>('setShow', { default: false });
</script>

<style lang="scss" scoped>
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;

    .page-title {
      font-size: $font-xxl;
      color: $white;
      margin: 0;
      margin-left: 10px;
    }
  }
</style>
