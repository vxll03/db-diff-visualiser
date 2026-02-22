<template>
  <div class="timeline-container">
    <n-spin :show="isLoadingSnapshots" size="small">
      <n-scrollbar x-scrollable>
        <div class="timeline-track">
          <div
            v-for="(snap, index) in snapshots"
            :key="snap.id"
            :class="['timeline-item', { active: revisionId === snap.id }]"
            @click="selectRevision(snap.id)"
          >
            <div class="label">{{ snap.revision_id }}</div>
            <div class="dot-wrapper">
              <div class="dot"></div>
              <div v-if="index !== snapshots.length - 1" class="line"></div>
            </div>
            <div class="date">{{ formatDateTime(snap.created_at) }}</div>
          </div>

          <div v-if="!snapshots?.length && !isLoadingSnapshots" class="no-data">
            No snapshots found for this project.
          </div>
        </div>
      </n-scrollbar>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
  import { watch } from 'vue';
  import { useRoute } from 'vue-router';
  import { formatDateTime } from '~/utils/date';

  const emit = defineEmits(['selectRevision']);
  const revisionId = defineModel<number | null>('revisionId');

  const route = useRoute();
  const projectId = route.params.id as string;

  const { data: snapshots, isLoading: isLoadingSnapshots } = useSnapshotTimelineQuery(
    Number.parseInt(projectId),
  );

  const selectRevision = (revId: number) => {
    if (revisionId.value !== revId) {
      revisionId.value = revId;
      emit('selectRevision');
    }
  };

  watch(snapshots, (newSnaps) => {
    if (newSnaps && newSnaps.length > 0 && !revisionId.value) {
      revisionId.value = newSnaps[0].id;
      emit('selectRevision');
    }
  });
</script>

<style scoped lang="scss">
  .timeline-container {
    flex: 0 0 auto;
    padding: 16px 24px;
    background-color: $light-dark;
    border-bottom: 2px solid $medium;
  }

  .timeline-track {
    display: flex;
    align-items: center;
    min-width: min-content;
    padding-bottom: 8px;
  }

  .timeline-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 120px;
    cursor: pointer;
    opacity: 0.6;
    transition: all 0.2s ease;

    &:hover {
      opacity: 0.9;
    }

    &.active {
      opacity: 1;
      .dot {
        background-color: $accent !important;
      }
      .label {
        color: $white-secondary;
        font-weight: bold;
      }
    }

    .dot-wrapper {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      margin: 8px 0;
      position: relative;

      .dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: $light;
        border: 2px solid $dark;
        z-index: 2;
        transition: all 0.2s ease;
      }

      .line {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100%;
        height: 2px;
        background-color: $light;
        transform: translateY(-50%);
        z-index: 1;
      }
    }

    .label {
      color: $gray;
      font-size: 0.85rem;
    }

    .date {
      color: $gray;
      font-size: 0.7rem;
    }
  }

  .no-data {
    color: $gray;
    font-size: 0.9rem;
  }
</style>
