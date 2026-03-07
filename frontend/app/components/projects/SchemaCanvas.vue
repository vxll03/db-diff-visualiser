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
  import { generateSqlDiff } from '~/utils/diffFormatter';
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
    type NodeDragEvent,
  } from '@vue-flow/core';
  import { Background } from '@vue-flow/background';
  import type { TableNodeData, ViewNodeData } from '@/schemas/parser.schema';
  import {
    TABLE_NODE_WIDTH,
    VIEW_NODE_WIDTH,
    TABLE_HEADER_HEIGHT,
    COLUMN_ROW_HEIGHT,
    TRIGGERS_HEADER_HEIGHT,
    TRIGGER_ROW_HEIGHT,
    TABLE_REMOVED_PLACEHOLDER_HEIGHT,
  } from '@/utils/parser/layout';

  const tableWidth = ref(`${TABLE_NODE_WIDTH}px`);
  const viewWidth = ref(`${VIEW_NODE_WIDTH}px`);
  const headerHeight = ref(`${TABLE_HEADER_HEIGHT}px`);
  const colHeight = ref(`${COLUMN_ROW_HEIGHT}px`);
  const trgHeaderHeight = ref(`${TRIGGERS_HEADER_HEIGHT}px`);
  const trgRowHeight = ref(`${TRIGGER_ROW_HEIGHT}px`);
  const removedHeight = ref(`${TABLE_REMOVED_PLACEHOLDER_HEIGHT}px`);

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

        nodes.value = flowData.nodes as Node<TableNodeData | ViewNodeData>[];
        edges.value = flowData.edges as Edge[];

        setTimeout(() => {
          if (mode === 'tables') updateHandles();
          fitView();
        }, 50);
      } catch (e) {
        console.error('Schema parsing error:', e);
      }
    }
  });

  const getNodeWidth = (node: Node<TableNodeData | ViewNodeData>) =>
    node.type === 'customView' ? VIEW_NODE_WIDTH : TABLE_NODE_WIDTH;

  const updateHandles = (draggedEvent?: NodeDragEvent) => {
    const GAP_THRESHOLD = 25;
    const draggedNodeId = draggedEvent?.node?.id;

    const edgesToUpdate = draggedNodeId
      ? edges.value.filter((e) => e.source === draggedNodeId || e.target === draggedNodeId)
      : edges.value;

    edgesToUpdate.forEach((edge) => {
      const sNode = nodes.value.find((n) => n.id === edge.source);
      const tNode = nodes.value.find((n) => n.id === edge.target);

      if (!sNode || !tNode) return;

      if (sNode.id === tNode.id) {
        edge.sourceHandle = `${edge.data.sourceCol}-source-right`;
        edge.targetHandle = `${edge.data.targetCol}-target-right`;
        return;
      }

      const sWidth = getNodeWidth(sNode);
      const tWidth = getNodeWidth(tNode);

      const isSourceLeft = sNode.position.x <= tNode.position.x;

      const lt = isSourceLeft ? sNode : tNode;
      const pt = isSourceLeft ? tNode : sNode;
      const ltWidth = isSourceLeft ? sWidth : tWidth;

      const gap = pt.position.x - (lt.position.x + ltWidth);

      if (gap > GAP_THRESHOLD) {
        if (isSourceLeft) {
          edge.sourceHandle = `${edge.data.sourceCol}-source-right`;
          edge.targetHandle = `${edge.data.targetCol}-target-left`;
        } else {
          edge.sourceHandle = `${edge.data.sourceCol}-source-left`;
          edge.targetHandle = `${edge.data.targetCol}-target-right`;
        }
      } else {
        edge.sourceHandle = `${edge.data.sourceCol}-source-right`;
        edge.targetHandle = `${edge.data.targetCol}-target-right`;
      }
    });
  };

  onNodeDrag(updateHandles);
</script>

<style lang="scss" scoped>
  $status-removed: #d03050;
  $status-changed: #2080f0;

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
    width: v-bind(tableWidth);
    background-color: $medium;
    border: 1px solid $light;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba($black, 0.3);
    user-select: none;
    overflow: hidden;

    :deep(.n-card-header) {
      height: v-bind(headerHeight);
      box-sizing: border-box;
      background-color: rgba($white, 0.03);
      border-bottom: 1px solid $light;
    }

    :deep(.n-card-header__main) {
      font-size: $font-m;
      color: $white-secondary;
      font-weight: 600;
    }

    :deep(.n-card__content) {
      padding: 0;
    }

    // Модификаторы статуса таблицы
    &.status-added {
      border-color: rgba($accent, 0.5);
      box-shadow: 0 0 15px rgba($accent, 0.1);
    }
    &.status-removed {
      border-color: rgba($status-removed, 0.5);
      opacity: 0.7;
      :deep(.n-card-header__main) {
        text-decoration: line-through;
        color: $status-removed;
      }
    }
    &.status-changed {
      border-color: rgba($status-changed, 0.4);
    }
  }

  .columns-list {
    display: flex;
    flex-direction: column;
  }

  .column-row {
    min-height: v-bind(colHeight);
    box-sizing: border-box;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    gap: 12px;
    border-bottom: 1px solid rgba($white, 0.03);
    font-size: $font-s;

    &:last-child {
      border-bottom: none;
    }

    .col-name {
      color: $white-secondary;
      flex: 1 1 auto;
      word-break: break-word;
      line-height: 1.2;
    }

    .col-type {
      color: $gray;
      font-size: $font-xs;
      flex: 0 0 auto;
      max-width: 45%;
      text-align: right;
      word-break: break-word;
      line-height: 1.2;
    }

    // Модификаторы статуса колонки
    &.status-added {
      background-color: rgba($accent, 0.15);
    }
    &.status-removed {
      background-color: rgba($status-removed, 0.15);
      .col-name,
      .col-type {
        text-decoration: line-through;
        opacity: 0.6;
      }
    }
    &.status-changed {
      background-color: rgba($status-changed, 0.15);
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

  .removed-placeholder {
    height: v-bind(removedHeight);
    box-sizing: border-box;
    text-align: center;
    color: $status-removed;
    font-size: $font-xs;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
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
    width: v-bind(viewWidth);
    background-color: $medium;
    border: 1px solid $light;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba($black, 0.3);
    overflow: hidden;

    :deep(.n-card-header) {
      padding: 12px;
      background-color: rgba($white, 0.03);
      border-bottom: 1px solid $light;
    }

    .view-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.95rem;
      color: $white-secondary;
      font-weight: 600;
    }

    // Модификаторы статуса View
    &.status-added {
      border-color: rgba($accent, 0.5);
      box-shadow: 0 0 15px rgba($accent, 0.1);
    }
    &.status-removed {
      border-color: rgba($status-removed, 0.5);
      opacity: 0.7;
      .view-header span {
        text-decoration: line-through;
        color: $status-removed;
      }
    }
    &.status-changed {
      border-color: rgba($status-changed, 0.4);
    }
  }

  .view-content {
    padding: 16px;
    display: flex;
    justify-content: center;
    align-items: center;

    .sql-badge {
      font-size: $font-xs;
      padding: 6px 12px;
      background-color: rgba($white, 0.05);
      border: 1px solid rgba($white, 0.1);
      border-radius: 6px;
      color: $white-secondary;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background-color: rgba($white, 0.1);
        border-color: rgba($white, 0.2);
      }
    }
  }

  .top-panel {
    margin: 16px;
  }

  .diff-container {
    font-family: var(--n-font-family-mono);
    font-size: $font-s;
    line-height: 1.4;
    white-space: pre-wrap;
    word-break: break-word;
    background-color: $dark;
    padding: 8px 0;
    border-radius: 4px;

    .diff-line {
      padding: 0 12px;

      &.line-added {
        background-color: rgba($accent, 0.15);
        color: lighten($accent, 15%);
      }
      &.line-removed {
        background-color: rgba($status-removed, 0.15);
        color: lighten($status-removed, 15%);
      }
      &.line-common {
        color: $gray;
      }
    }

    .diff-empty {
      padding: 0 12px;
      color: $gray;
      font-style: italic;
    }
  }

  .triggers-section {
    border-top: 1px solid rgba($white, 0.03);
    background-color: rgba($black, 0.15);
  }

  .triggers-header {
    height: v-bind(trgHeaderHeight);
    box-sizing: border-box;
    font-size: 0.7rem;
    color: $gray;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 8px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;

    .header-icon {
      color: #e2a829;
      font-size: 0.9rem;
    }
  }

  .trigger-row {
    height: v-bind(trgRowHeight);
    box-sizing: border-box;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 8px;
    border-bottom: 1px solid rgba($white, 0.02);
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background-color: rgba($white, 0.05);
    }
    &:last-child {
      border-bottom: none;
    }

    .trg-icon {
      color: #e2a829;
      font-size: 0.85rem;
    }

    .trg-name {
      color: $white-secondary;
      font-size: $font-xs;
      font-family: var(--n-font-family-mono);
    }

    // Модификаторы статуса триггера
    &.status-added {
      background-color: rgba($accent, 0.15);
    }
    &.status-removed {
      background-color: rgba($status-removed, 0.15);
      opacity: 0.6;
    }
    &.status-changed {
      background-color: rgba($status-changed, 0.15);
    }
  }
</style>
