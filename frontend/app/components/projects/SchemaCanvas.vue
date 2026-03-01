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
        <Background :pattern-color="LIGHT" :gap="35" :size="3" />
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
            <div v-if="data.triggers?.length" class="triggers-section">
              <div class="triggers-header">
                <Icon name="ph:lightning-duotone" class="header-icon" />
                Triggers
              </div>
              <div class="triggers-list">
                <n-popover
                  v-for="trg in data.triggers"
                  :key="trg.name"
                  trigger="click"
                  placement="right"
                  scrollable
                  style="max-width: 500px; max-height: 400px"
                >
                  <template #trigger>
                    <div :class="['trigger-row', `status-${trg.status}`]">
                      <Icon name="ph:lightning-fill" class="trg-icon" />
                      <span class="trg-name">{{ trg.name }}</span>
                    </div>
                  </template>

                  <div class="diff-container">
                    <div
                      v-for="(line, idx) in generateSqlDiff(trg.oldDefinition, trg.definition)"
                      :key="idx"
                      :class="['diff-line', `line-${line.type}`]"
                    >
                      {{ line.content }}
                    </div>
                    <div v-if="!trg.definition && !trg.oldDefinition" class="diff-empty">
                      No definition available
                    </div>
                  </div>
                </n-popover>
              </div>
            </div>
          </n-card>
        </template>

        <template #node-customView="{ data }">
          <n-card :class="['view-node', `status-${data.status}`]" size="small" :bordered="true">
            <template #header>
              <div class="view-header">
                <Icon
                  :name="
                    data.type === 'materialized_view' ? 'ph:database-duotone' : 'ph:eye-duotone'
                  "
                />
                <span>{{ data.label }}</span>
              </div>
            </template>
            <div v-if="data.status === 'removed'" class="removed-placeholder">View Dropped</div>

            <div v-else class="view-content">
              <n-popover
                trigger="click"
                placement="bottom"
                scrollable
                style="max-width: 500px; max-height: 400px"
              >
                <template #trigger>
                  <span class="sql-badge">View SQL Definition</span>
                </template>

                <div class="diff-container">
                  <div
                    v-for="(line, idx) in generateSqlDiff(data.oldDefinition, data.definition)"
                    :key="idx"
                    :class="['diff-line', `line-${line.type}`]"
                  >
                    {{ line.content }}
                  </div>
                  <div v-if="!data.definition && !data.oldDefinition" class="diff-empty">
                    No definition available
                  </div>
                </div>
              </n-popover>
            </div>
          </n-card>
        </template>

        <Panel v-if="canvasMode === 'views'" position="top-left" class="top-panel">
          <n-button strong secondary type="primary" @click="canvasMode = 'tables'">
            <template #icon><Icon name="ph:arrow-left-bold" /></template>
            Back to Tables
          </n-button>
        </Panel>

        <Panel position="bottom-right" class="controls-panel">
          <div class="panel-layout">
            <n-button-group vertical class="canvas-controls">
                <n-button
                  :type="canvasMode === 'views' ? 'primary' : 'default'"
                  quaternary
                  @click="canvasMode = 'views'"
                >
                  <template #icon><Icon name="ph:eye" /></template>
                  Views
                  </n-button>
            </n-button-group>

            <n-button-group class="canvas-controls">
              <n-button quaternary @click="() => zoomOut()">
                <template #icon><Icon name="ph:magnifying-glass-minus" /></template>
              </n-button>
              <n-button quaternary @click="() => zoomIn()">
                <template #icon><Icon name="ph:magnifying-glass-plus" /></template>
              </n-button>
              <n-button quaternary @click="() => fitView()">
                <template #icon><Icon name="ph:corners-out" /></template>
              </n-button>
            </n-button-group>
          </div>
        </Panel>
      </VueFlow>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
  import { generateSqlDiff, type DiffLine } from '~/utils/diffFormatter';
  import '@vue-flow/core/dist/style.css';
  import '@vue-flow/core/dist/theme-default.css';
  import {
    VueFlow,
    Panel,
    useVueFlow,
    Handle,
    Position,
    type Node,
    type Edge,
  } from '@vue-flow/core';
  import { Background } from '@vue-flow/background';

  const { parseSchemaToFlow, parseViewsToFlow } = useSchemaParser();
  const { zoomIn, zoomOut, fitView, onNodeDrag } = useVueFlow();

  const canvasMode = ref<'tables' | 'views'>('tables');

  const nodes = defineModel<Node<TableNodeData | ViewNodeData>[]>('nodes', { default: () => [] });
  const edges = defineModel<Edge[]>('edges', { default: () => [] });
  const revisionId = defineModel<number | null>('revisionId');

  const route = useRoute();
  const projectId = route.params.id as string;

  const { data: currentSchemaData, isLoading: isLoadingDetails } = useSnapshotDetailsQuery(
    Number.parseInt(projectId),
    revisionId as Ref<number | null>,
  );

  watch([currentSchemaData, canvasMode], ([newData, mode]) => {
    if (newData) {
      try {
        const flowData = mode === 'tables' ? parseSchemaToFlow(newData) : parseViewsToFlow(newData);

        nodes.value = flowData.nodes as any;
        edges.value = flowData.edges as any;

        setTimeout(() => {
          if (mode === 'tables') updateHandles();
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

  .panel-layout {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: flex-end;
  }

  .canvas-controls {
    border: 2px solid $medium !important;
    border-radius: 8px;
  }

  .view-node {
    width: 300px;
    background-color: #1e2320;
    border: 1px solid #3b3c3d;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);

    :deep(.n-card-header) {
      padding: 12px;
      background-color: rgba(255, 255, 255, 0.03);
      border-bottom: 1px solid #3b3c3d;
    }

    .view-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.95rem;
      color: #eaebeb;
      font-weight: 600;
    }

    .view-content {
      padding: 16px;
      display: flex;
      justify-content: center;
      align-items: center;

      .sql-badge {
        font-size: 0.75rem;
        padding: 4px 8px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        color: #a0a0a0;
      }
    }

    &.status-added {
      border-color: rgba(17, 175, 116, 0.5);
      box-shadow: 0 0 15px rgba(17, 175, 116, 0.1);
    }
    &.status-removed {
      border-color: rgba(208, 48, 80, 0.5);
      opacity: 0.7;
      .view-header span {
        text-decoration: line-through;
        color: #d03050;
      }
    }
    &.status-changed {
      border-color: rgba(32, 128, 240, 0.4);
    }
  }

  .top-panel {
    margin: 16px;
  }

  .view-content {
    padding: 16px;
    display: flex;
    justify-content: center;
    align-items: center;

    .sql-badge {
      font-size: 0.75rem;
      padding: 6px 12px;
      background-color: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      color: #eaebeb;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
      }
    }
  }

  .diff-container {
    font-family: var(--n-font-family-mono); // Моноширинный шрифт Naive UI
    font-size: 0.8rem;
    line-height: 1.4;
    white-space: pre-wrap; // Сохраняем пробелы и переносы
    word-break: break-word;
    background-color: #111;
    padding: 8px 0;
    border-radius: 4px;

    .diff-line {
      padding: 0 12px;

      &.line-added {
        background-color: rgba(17, 175, 116, 0.15); // Прозрачный зеленый
        color: #1fd08c;
      }
      &.line-removed {
        background-color: rgba(208, 48, 80, 0.15); // Прозрачный красный
        color: #ea607e;
      }
      &.line-common {
        color: #a0a0a0;
      }
    }

    .diff-empty {
      padding: 0 12px;
      color: #666;
      font-style: italic;
    }
  }

  .triggers-section {
    border-top: 1px solid rgba(255, 255, 255, 0.03);
    background-color: rgba(0, 0, 0, 0.15);
  }

  .triggers-header {
    padding: 6px 12px;
    font-size: 0.7rem;
    color: #a0a0a0;
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;

    .header-icon {
      color: #e2a829;
      font-size: 0.9rem;
    }
  }

  .trigger-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.02);
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background-color: rgba(255, 255, 255, 0.05);
    }
    &:last-child {
      border-bottom: none;
    }

    .trg-icon {
      color: #e2a829;
      font-size: 0.85rem;
    }

    .trg-name {
      color: #eaebeb;
      font-size: 0.75rem;
      font-family: var(--n-font-family-mono);
    }

    &.status-added {
      background-color: rgba(17, 175, 116, 0.15);
    }
    &.status-removed {
      background-color: rgba(208, 48, 80, 0.15);
      opacity: 0.6;
    }
    &.status-changed {
      background-color: rgba(32, 128, 240, 0.15);
    }
  }
</style>
