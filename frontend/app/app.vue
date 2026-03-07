<template>
  <n-config-provider :locale="ruRU" :date-locale="dateRuRU" :theme-overrides="naiveThemeOverrides">
    <n-message-provider placement="bottom-right">
      <NuxtLayout>
        <div class="layout">
          <NuxtPage />
        </div>
      </NuxtLayout>
    </n-message-provider>
  </n-config-provider>
</template>
<script setup lang="ts">
  import { ruRU, dateRuRU } from 'naive-ui';
  import { naiveThemeOverrides } from '~/theme/naive-theme-dark';
</script>
