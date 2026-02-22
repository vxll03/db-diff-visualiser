<template>
  <div class="dashboard-page">
    <Header v-model:set-show="isModalVisible" />
    <CreateProjectModal v-model:show="isModalVisible" />

    <div class="top-grid">
      <RecentCheckCard />
      <CheckDiagramCard />
    </div>

    <MainTableCard />
  </div>
</template>

<script setup lang="ts">
  import CreateProjectModal from '~/components/main/CreateProjectModal.vue';
  import Header from '~/components/main/Header.vue';
  import RecentCheckCard from '~/components/main/RecentCheckCard.vue';
  import CheckDiagramCard from '~/components/main/CheckDiagramCard.vue';
  import MainTableCard from '~/components/main/MainTableCard.vue';

  const isModalVisible = ref(false);
</script>

<style scoped lang="scss">
  .dashboard-page {
    height: calc(100vh - 64px);
    display: flex;
    flex-direction: column;
    gap: 24px;
    overflow: hidden;
  }

  .top-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    flex-shrink: 0;
  }

  .data-card {
    background-color: $medium;
    border-radius: 12px;
  }
</style>
