<template>
  <n-card class="data-card" title="Recent checks" :bordered="false">
    <div v-if="isLoadingLatest" style="display: flex; justify-content: center; padding: 20px">
      <n-spin size="small" />
    </div>

    <div v-else-if="latestSnapshots && latestSnapshots.length > 0" class="check-list">
      <div v-for="snap in latestSnapshots" :key="snap.id" class="check-item">
        <NuxtLink :to="`/projects/${snap.project_id}`" class="db-name link">
          {{ snap.project_name }}
        </NuxtLink>

        <span class="divider">|</span>
        <span class="rev-name">Revision: {{ snap.revision_id }}</span>
      </div>
    </div>

    <div v-else :color="GRAY" style="text-align: center; padding: 10px 0">
      No recent checks found
    </div>
  </n-card>
</template>

<script setup lang="ts">
  const { data: latestSnapshots, isLoading: isLoadingLatest } = useLatestSnapshotsQuery();
</script>

<style scoped lang="scss">
  .data-card {
    border-radius: 12px;
  }
  .check-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .check-item {
      font-size: $font-m;
      color: $gray;
      padding-bottom: 8px;
      border-bottom: 1px solid $light;

      &:last-child {
        border-bottom: none;
      }

      .divider {
        margin: 0 8px;
        opacity: 0.5;
      }

      .db-name.link {
        color: $white;
        text-decoration: none;
        transition: color 0.2s ease;
        font-weight: 500;

        &:hover {
          color: $accent;
        }
      }
    }
  }
</style>
