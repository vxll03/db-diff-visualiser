<template>
  <n-layout has-sider class="app-layout">
    <n-layout-sider :width="260" class="sidebar" content-class="sider-content">
      <div class="logo">
        <img src="/logo.svg" alt="VantageDB Logo" class="logo-img" />
        VantageDB
      </div>

      <div class="top-menu">
        <n-menu :options="topMenuOptions" :value="activeKey" />
      </div>

      <div class="bottom-section">
        <n-menu :options="bottomMenuOptions" :value="activeKey" />

        <div class="user-profile">
          <n-dropdown
            :options="accountOptions"
            placement="right-end"
            trigger="hover"
            @select="handleAccountAction"
          >
            <n-button block class="account-btn" :bordered="false">
              <div class="btn-content">
                <div class="btn-left">
                  <div class="icon-wrapper">
                    <Icon name="ph:user-bold" size="14" :color="DARK" />
                  </div>
                  <span>My Account</span>
                </div>
                <Icon name="ph:caret-right" size="16" :color="GRAY" />
              </div>
            </n-button>
          </n-dropdown>
        </div>
      </div>
    </n-layout-sider>

    <n-layout class="main-content">
      <slot />
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
  import type { MenuOption } from 'naive-ui';
  import { useProjectsQuery } from '@/composables/useProjects';

  const route = useRoute();
  const NuxtLink = resolveComponent('NuxtLink');
  const Icon = resolveComponent('Icon');

  const renderIcon = (iconName: string) => {
    return () => h(Icon, { name: iconName, size: '18' });
  };

  const renderLink = (label: string, to: string) => {
    return () => h(NuxtLink, { to }, { default: () => label });
  };

  const activeKey = computed(() => {
    if (route.path === '/') return 'dashboard';

    if (route.path.startsWith('/projects/')) {
      const projectId = route.path.split('/')[2];
      return `proj-${projectId}`;
    }

    return '';
  });

  const { data: projects, isLoading } = useProjectsQuery();

  const topMenuOptions = computed<MenuOption[]>(() => {
    const projectChildren: MenuOption[] = isLoading.value
      ? [{ label: 'Loading...', key: 'loading', disabled: true }]
      : projects.value?.length
        ? projects.value.map((p) => ({
            label: renderLink(p.name, `/projects/${p.id}`),
            key: `proj-${p.id}`,
            icon: renderIcon(p.icon || 'ph:database'),
          }))
        : [{ label: 'No projects', key: 'empty', disabled: true }];

    return [
      {
        type: 'group',
        label: 'PLATFORM',
        key: 'platform-group',
        children: [
          {
            label: renderLink('Dashboard', '/'),
            key: 'dashboard',
            icon: renderIcon('ph:house-line'),
          },
        ],
      },
      {
        type: 'group',
        label: 'PROJECTS',
        key: 'projects-group',
        children: projectChildren,
      },
    ];
  });

  const bottomMenuOptions: MenuOption[] = [
    {
      type: 'group',
      label: 'ORGANIZATION',
      key: 'org-group',
      children: [
        { label: 'Teams', key: 'teams', icon: renderIcon('ph:users') },
        { label: 'Users', key: 'users', icon: renderIcon('ph:user') },
        { label: 'Security', key: 'security', icon: renderIcon('ph:shield-check') },
      ],
    },
  ];

  const accountOptions = [
    { label: 'Profile Settings', key: 'profile', icon: renderIcon('ph:user-gear') },
    { label: 'Billing', key: 'billing', icon: renderIcon('ph:credit-card') },
    { type: 'divider', key: 'divider' }, // Разделитель
    { label: 'Log out', key: 'logout', icon: renderIcon('ph:sign-out') },
  ];

  const handleAccountAction = (key: string) => {
    console.log('Selected action:', key);
  };
</script>

<style scoped lang="scss">
  .app-layout {
    height: 100vh;
    background-color: $dark;
  }

  .sidebar {
    background-color: $light-dark;
    border-right: 2px solid $medium;
  }

  :deep(.sider-content) {
    display: flex;
    flex-direction: column;
    min-height: 100%;
  }

  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    padding: 0 24px;
    font-size: $font-xl;
    font-weight: bold;
    color: $accent;
    flex-shrink: 0;
    user-select: none;
  }

  .top-menu {
    flex: 1;
    overflow-y: auto;
  }

  .bottom-section {
    flex-shrink: 0;
  }

  .user-profile {
    padding: 16px 16px 24px 16px;

    .account-btn {
      background-color: transparent;
      border: 1px solid $light;
      border-radius: 8px;
      height: 44px;
      padding: 0 12px;

      :deep(.n-button__content) {
        width: 100%;
      }

      &:hover {
        border-color: $accent;
      }
    }
  }

  .btn-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;

    .btn-left {
      display: flex;
      align-items: center;
      gap: 12px;
      color: $white;
      font-weight: 500;
    }
  }

  .main-content {
    background-color: $dark;
    padding: 32px 40px;
  }

  :deep(.n-menu-item-group-title) {
    font-weight: 600;
    letter-spacing: 0.5px;
    color: $gray;
  }

  :deep(.n-menu-item-group) {
    margin-top: 24px;
  }

  :deep(.n-menu-item-group:first-child) {
    margin-top: 0;
  }

  .btn-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;

    .btn-left {
      display: flex;
      align-items: center;
      gap: 12px;
      color: $white;
      font-weight: 500;
    }
  }

  .icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background-color: $accent;
    border-radius: 6px;
  }

  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 24px;
    font-size: $font-xl;
    font-weight: bold;
    color: $accent;
    flex-shrink: 0;
    user-select: none;
  }

  .logo-img {
    height: 32px;
    width: auto;
    display: block;
  }
</style>
