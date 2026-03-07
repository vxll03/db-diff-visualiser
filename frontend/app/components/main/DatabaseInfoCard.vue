<template>
  <n-card :segmented="{ content: true }" class="data-card main-table-card" :bordered="false">
    <template #header>
      <div class="main-header">
        <Icon name="ph:database" size="20" />
        <span>Your Active Projects</span>
      </div>
    </template>
    <template #header-extra>
      <span class="active-count">
        <b>{{ projects?.filter((p: any) => !p._isDeleting).length || 0 }}</b> Active Projects
      </span>
    </template>

    <div v-if="isLoading" style="display: flex; justify-content: center; padding: 20px">
      <n-spin size="small" />
    </div>

    <div v-else class="flat-projects-list">
      <template v-for="project in projects" :key="project.id">
        <div v-show="!(project as any)._isDeleting" class="flat-card">
          <div class="card-header">
            <div class="title-group">
              <Icon :name="project.icon || 'ph:database'" size="22" class="project-icon" />

              <n-input
                v-if="editingId === project.id"
                v-model:value="editNameValue"
                :maxlength="30"
                size="small"
                class="edit-project-input"
                autofocus
                @keyup.enter="saveEdit(project)"
                @blur="saveEdit(project)"
              />
              <NuxtLink v-else :to="`/projects/${project.id}`" class="project-name-link">
                {{ project.name }}
              </NuxtLink>
            </div>

            <n-dropdown
              :options="getDropdownOptions(project)"
              placement="bottom-end"
              @select="(key) => handleProjectAction(key, project)"
              @clickoutside="pendingDeleteId = null"
            >
              <n-button quaternary circle size="small" class="action-btn">
                <template #icon>
                  <Icon name="ph:dots-three-bold" size="20" />
                </template>
              </n-button>
            </n-dropdown>
          </div>

          <div class="card-body">
            <span class="info-tag">{{ project.snapshots_count }} snaps</span>
            <span class="info-text">{{ project.tables_count }} tables</span>
            <span class="info-text">{{ project.views_count }} views</span>
            <span class="info-text">{{ project.mat_views_count }} mat views</span>
            <span class="info-text">{{ project.triggers_count }} triggers</span>
            <span class="info-text">{{ project.functions_count }} functions</span>
            <span class="info-date">Created {{ formatDate(project.created_at) }}</span>
          </div>
        </div>
      </template>
    </div>
  </n-card>
</template>

<script setup lang="ts">
  const { mutate: editProjectMutate } = useUpdateProject();
  const { mutate: deleteProjectMutate } = useDeleteProject();
  const { data: projects, isLoading } = useProjectsQuery();
  const message = useMessage();

  const editingId = ref<number | null>(null);
  const editNameValue = ref<string>('');
  const pendingDeleteId = ref<number | null>(null);

  const startEdit = (project: any) => {
    editingId.value = project.id;
    editNameValue.value = project.name;
    pendingDeleteId.value = null;
  };

  const saveEdit = (project: any) => {
    if (!editingId.value) return;

    const newName = editNameValue.value.trim();
    if (!newName || newName === project.name) {
      editingId.value = null;
      return;
    }

    const oldName = project.name;
    project.name = newName;
    editingId.value = null;

    editProjectMutate(
      { id: project.id, name: newName },
      {
        onError: () => {
          project.name = oldName;
          message.error('Failed to update project');
        },
      },
    );
  };

  const executeDelete = (project: any) => {
    (project as any)._isDeleting = true;
    pendingDeleteId.value = null;

    deleteProjectMutate(project.id, {
      onError: () => {
        (project as any)._isDeleting = false;
        message.error('Failed to delete project');
      },
    });
  };

  const getDropdownOptions = (project: any) => {
    const isPendingDelete = pendingDeleteId.value === project.id;

    return [
      {
        label: 'Edit Name',
        key: 'edit',
        icon: renderIcon('ph:pencil-simple'),
      },
      { type: 'divider', key: 'd1' },
      {
        key: 'custom-delete',
        type: 'render',
        render: () =>
          h(
            'div',
            {
              style: {
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 12px',
                cursor: 'pointer',
                color: isPendingDelete ? RED : 'white',
                transition: 'color 0.2s',
                minWidth: '120px',
              },
              onClick: (e: MouseEvent) => {
                e.stopPropagation();

                if (isPendingDelete) {
                  executeDelete(project);
                } else {
                  pendingDeleteId.value = project.id;
                }
              },
            },
            [
              renderIcon('ph:trash', isPendingDelete ? RED : RED_SOFT)(),
              h('span', isPendingDelete ? 'Confirm?' : 'Delete'),
            ],
          ),
      },
    ];
  };

  const handleProjectAction = (key: string, project: any) => {
    if (key === 'edit') {
      startEdit(project);
    }
  };
</script>

<style lang="scss" scoped>
  :deep(.n-card-header) {
    border-bottom: 2px solid $light;
  }

  .data-card {
    background-color: $medium;
    border-radius: 12px;
  }

  .main-table-card {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;

    :deep(.n-card__content) {
      flex: 1;
      min-height: 0;
      overflow-y: auto;

      &::-webkit-scrollbar {
        width: 6px;
      }
      &::-webkit-scrollbar-thumb {
        background-color: $light;
        border-radius: 4px;
      }
    }

    .main-header {
      display: flex;
      align-items: center;
      gap: 8px;
      color: $white;
      font-size: $font-xl;
      font-weight: 600;
    }

    .active-count {
      color: $gray;
      font-size: $font-m;
      b {
        color: $white;
      }
    }
  }

  :deep(.main-table-card) {
    .n-card-header {
      border-bottom: 2px solid $light;
    }
  }

  .flat-projects-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .flat-card {
    background-color: $medium;
    border-radius: 8px;
    padding: 16px 20px;
    transition: background-color 0.2s ease;

    &:hover {
      background-color: rgba(30, 35, 32, 0.8);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .title-group {
        display: flex;
        align-items: center;
        gap: 12px;

        .project-icon {
          color: $gray;
        }

        .project-name-link {
          color: $white-secondary;
          font-size: $font-xl;
          font-weight: 600;
          text-decoration: none;
          transition: color 0.2s;

          &:hover {
            color: $accent;
          }
        }
      }

      .action-btn {
        color: $gray;
        &:hover {
          color: $white-secondary;
        }
      }
    }

    .card-body {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 16px;
      padding-left: 34px;

      .info-tag {
        background-color: rgba(24, 104, 75, 0.1);
        color: $accent;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
      }

      .info-text {
        position: relative;
        color: $gray;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        margin-left: 0.5rem;
      }

      .info-date {
        color: $gray;
        font-size: 0.8rem;
        margin-left: auto;
      }
    }
  }

  .check-item {
    .db-name.link {
      color: $white-secondary;
      text-decoration: none;
      transition: color 0.2s ease;
      font-weight: 500;

      &:hover {
        color: $accent;
      }
    }
  }
</style>
