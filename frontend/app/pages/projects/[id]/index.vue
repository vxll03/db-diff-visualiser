<script setup lang="ts">
  const route = useRoute();
  const projectId = Number(route.params.id);

  const { data: snapshots, isSuccess } = useSnapshotTimelineQuery(projectId);

  watchEffect(() => {
    if (isSuccess.value && snapshots.value && snapshots.value.length > 0) {
      const latestSnapId = snapshots.value[snapshots.value.length - 1]?.id;
      navigateTo(`/projects/${projectId}/${latestSnapId}`, { replace: true });
    }
  });
</script>

<template>
  <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
    <n-spin size="large" />
  </div>
</template>