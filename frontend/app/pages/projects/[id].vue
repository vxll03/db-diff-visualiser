<template>
  <div class="schema-page">
    <projects-time-line v-model:revision-id="revisionId" @select-revision="selectRevision" />
    <projects-schema-canvas 
      v-model:revision-id="revisionId" 
      v-model:nodes="nodes" 
      v-model:edges="edges" 
    />
  </div>
</template>

<script setup lang="ts">
  const nodes = ref<any[]>([]);
  const edges = ref<any[]>([]);
  const revisionId = ref<number | null>(null);

  const selectRevision = () => {
    nodes.value = [];
    edges.value = [];
  };
</script>

<style scoped lang="scss">
  .schema-page {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 68px);
    width: 99.7%;
    background-color: $light-dark;
    border-radius: 12px;
    border: 2px solid $medium;
    overflow: hidden;
  }
</style>
