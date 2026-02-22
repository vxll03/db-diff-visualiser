<template>
  <div class="canvas-wrapper">
    <n-spin :show="isLoadingDetails" class="canvas-spinner">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :default-viewport="{ zoom: 1.2 }"
        :min-zoom="0.2"
        :max-zoom="4"
        fit-view-on-init
        class="db-canvas"
      >
        <template #node-customTable="{ data }">
          <n-card
            :class="['table-node', `status-${data.status}`]"
            :title="data.label"
            size="small"
            :bordered="true"
          >
            <div v-if="data.status === 'removed'" class="removed-placeholder">Table Dropped</div>

            <div class="columns-list">
              <n-tooltip
                v-for="col in data.columns"
                :key="col.name"
                :disabled="col.status !== 'changed' || !col.changeDetails?.length"
                placement="right"
                trigger="hover"
              >
                <template #trigger>
                  <div :class="['column-row', `status-${col.status}`]">
                    <Handle
                      :id="col.name + '-target-left'"
                      type="target"
                      :position="Position.Left"
                      class="custom-handle"
                    />
                    <Handle
                      :id="col.name + '-source-left'"
                      type="source"
                      :position="Position.Left"
                      class="custom-handle"
                    />

                    <span class="col-name">{{ col.name }}</span>
                    <span class="col-type">{{ col.type }}</span>

                    <Handle
                      :id="col.name + '-target-right'"
                      type="target"
                      :position="Position.Right"
                      class="custom-handle"
                    />
                    <Handle
                      :id="col.name + '-source-right'"
                      type="source"
                      :position="Position.Right"
                      class="custom-handle"
                    />
                  </div>
                </template>

                <div class="diff-tooltip">
                  <div v-for="(line, idx) in col.changeDetails" :key="idx" class="diff-line">
                    {{ line }}
                  </div>
                </div>
              </n-tooltip>
            </div>
          </n-card>
        </template>

        <Panel position="bottom-right" class="controls-panel">
          <n-button-group class="canvas-controls">
            <n-button quaternary @click="zoomIn">
              <template #icon><Icon name="ph:magnifying-glass-plus" /></template>
            </n-button>
            <n-button quaternary @click="zoomOut">
              <template #icon><Icon name="ph:magnifying-glass-minus" /></template>
            </n-button>
            <n-button quaternary @click="fitView">
              <template #icon><Icon name="ph:corners-out" /></template>
            </n-button>
          </n-button-group>
        </Panel>
      </VueFlow>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
  import '@vue-flow/core/dist/style.css';
  import '@vue-flow/core/dist/theme-default.css';
  import { VueFlow, Panel, useVueFlow, Handle, Position } from '@vue-flow/core';

  const { parseSchemaToFlow } = useSchemaParser();
  const { zoomIn, zoomOut, fitView, onNodeDrag } = useVueFlow();

  const nodes = defineModel<any[]>('nodes');
  const edges = defineModel<any[]>('edges');
  const revisionId = defineModel<number | null>('revisionId');

  const route = useRoute();
  const projectId = route.params.id as string;
  const { data: currentSchemaData, isLoading: isLoadingDetails } = useSnapshotDetailsQuery(
    Number.parseInt(projectId),
    revisionId,
  );

  watch(currentSchemaData, (newData) => {
    if (newData) {
      const payloadForParser = {
        ...newData.schema_data,
        diff_data: newData.diff_data || {},
      };

      try {
        const flowData = parseSchemaToFlow(payloadForParser);
        nodes.value = flowData.nodes;
        edges.value = flowData.edges;

        setTimeout(() => {
          updateHandles();
          fitView();
        }, 50);
      } catch (e) {
        console.error('Schema parsing error:', e);
      }
    }
  });

  const updateHandles = () => {
    edges.value.forEach((edge) => {
      const sNode = nodes.value.find((n) => n.id === edge.source);
      const tNode = nodes.value.find((n) => n.id === edge.target);

      if (sNode && tNode) {
        if (sNode.position.x > tNode.position.x) {
          edge.sourceHandle = `${edge.data.sourceCol}-source-left`;
          edge.targetHandle = `${edge.data.targetCol}-target-right`;
        } else {
          edge.sourceHandle = `${edge.data.sourceCol}-source-right`;
          edge.targetHandle = `${edge.data.targetCol}-target-left`;
        }
      }
    });
  };

  onNodeDrag(updateHandles);
</script>

<style lang="scss" scoped>
  .canvas-wrapper {
    flex: 1 1 auto;
    position: relative;

    .canvas-spinner {
      height: 100%;
      :deep(.n-spin-content) {
        height: 100%;
      }
    }
  }

  .db-canvas {
    width: 100%;
    height: 100%;
  }

  .table-node {
    width: 250px;
    background-color: #1e2320;
    border: 1px solid #3b3c3d;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    user-select: none;

    :deep(.n-card-header) {
      padding: 8px 12px;
      background-color: rgba(255, 255, 255, 0.03);
      border-bottom: 1px solid #3b3c3d;
    }

    :deep(.n-card-header__main) {
      font-size: 0.9rem;
      color: #eaebeb;
      font-weight: 600;
    }

    :deep(.n-card__content) {
      padding: 0;
    }
  }

  .columns-list {
    display: flex;
    flex-direction: column;
  }
  .column-row {
    position: relative;
    display: flex;
    justify-content: space-between;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    font-size: 0.8rem;
    &:last-child {
      border-bottom: none;
    }
    .col-name {
      color: #eaebeb;
    }
    .col-type {
      color: #727379;
      font-size: 0.75rem;
    }
  }

  .custom-handle {
    opacity: 0 !important;
    width: 1px;
    height: 1px;
    border: none;
    background: transparent;
    &.vue-flow__handle-left {
      left: 0;
    }
    &.vue-flow__handle-right {
      right: 0;
    }
  }

  .table-node {
    &.status-added {
      border-color: rgba(17, 175, 116, 0.5);
      box-shadow: 0 0 15px rgba(17, 175, 116, 0.1);
    }
    &.status-removed {
      border-color: rgba(208, 48, 80, 0.5);
      opacity: 0.7;
      :deep(.n-card-header__main) {
        text-decoration: line-through;
        color: #d03050;
      }
    }
    &.status-changed {
      border-color: rgba(32, 128, 240, 0.4);
    }
  }

  .removed-placeholder {
    padding: 12px;
    text-align: center;
    color: #d03050;
    font-size: 0.75rem;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .column-row {
    &.status-added {
      background-color: rgba(17, 175, 116, 0.15);
    }
    &.status-removed {
      background-color: rgba(208, 48, 80, 0.15);
      .col-name,
      .col-type {
        text-decoration: line-through;
        opacity: 0.6;
      }
    }
    &.status-changed {
      background-color: rgba(32, 128, 240, 0.15);
    }
  }

  .canvas-controls {
    border: 2px solid $medium !important;
    border-radius: 8px;
  }
</style>
