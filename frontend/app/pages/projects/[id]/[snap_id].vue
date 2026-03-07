<template>
  <div class="schema-page">
    <projects-schema-canvas
      v-model:revision-id="revisionId"
      v-model:nodes="nodes"
      v-model:edges="edges"
    />
    <projects-time-line
      v-model:set-show="isModalVisible"
      v-model:revision-id="revisionId"
      @select-revision="selectRevision"
    />
    <projects-create-snapshot-modal v-model:show="isModalVisible" />
  </div>
</template>

<script setup lang="ts">
  import type { Node, Edge } from '@vue-flow/core';
  import type { TableNodeData, ViewNodeData } from '@/schemas/parser.schema';

  const route = useRoute();
  
  const nodes = ref<Node<TableNodeData | ViewNodeData>[]>([]);
  const edges = ref<Edge[]>([]);
  
  const revisionId = ref<number | null>(Number(route.params.snap_id) || null);
  const isModalVisible = ref<boolean>(false);

  const selectRevision = (newSnapId: number) => {
    nodes.value = [];
    edges.value = [];
    navigateTo(`/projects/${route.params.id}/${newSnapId}`);
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