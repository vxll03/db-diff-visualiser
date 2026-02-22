<template>
  <n-card :segmented="{ content: true }" class="data-card main-table-card" :bordered="false">
    <template #header>
      <div class="main-header">
        <Icon name="ph:database" size="20" />
        <span>Your Active Projects</span>
      </div>
    </template>
    <template #header-extra>
      <span class="active-count"
        ><b>{{ projects?.length || 0 }}</b> Active Projects</span
      >
    </template>

    <div v-if="isLoading" style="display: flex; justify-content: center; padding: 20px">
      <n-spin size="small" />
    </div>

    <div v-else class="flat-projects-list">
      <div v-for="project in projects" :key="project.id" class="flat-card">
        <div class="card-header">
          <div class="title-group">
            <Icon :name="project.icon || 'ph:database'" size="22" class="project-icon" />
            <NuxtLink :to="`/projects/${project.id}`" class="project-name-link">
              {{ project.name }}
            </NuxtLink>
          </div>

          <n-dropdown
            :options="actionOptions"
            placement="bottom-end"
            @select="(key) => handleProjectAction(key, project.id)"
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
          <span class="info-date">Created {{ formatDate(project.created_at) }}</span>
        </div>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
  const { data: projects, isLoading } = useProjectsQuery();

  const actionOptions = [
    {
      label: 'Edit Project',
      key: 'edit',
      icon: renderIcon('ph:pencil-simple'),
    },
    {
      label: 'Settings',
      key: 'settings',
      icon: renderIcon('ph:gear'),
    },
    {
      type: 'divider',
      key: 'd1',
    },
    {
      label: 'Delete',
      key: 'delete',
      icon: renderIcon('ph:trash', '#e88080'),
    },
  ];

  const handleProjectAction = (key: string, projectId: number) => {
    if (key === 'delete') {
      console.log(`Deleting project ${projectId}`);
    } else if (key === 'edit') {
      console.log(`Editing project ${projectId}`);
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
