<template>
  <n-modal v-model:show="show">
    <n-card
      style="width: 400px"
      title="Create New Project"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
      class="custom-modal"
    >
      <n-form ref="formRef" :model="formData" :rules="rules" @submit="handleCreate">
        <n-form-item path="name" label="Project Name">
          <n-input
            v-model:value="formData.name"
            placeholder="e.g. Production DB"
            @keydown.enter.prevent="handleCreate"
          />
        </n-form-item>

        <n-form-item path="icon" label="Icon (Optional)">
          <n-popover
            v-model:show="showIconPicker"
            trigger="click"
            placement="bottom"
            :show-arrow="false"
          >
            <template #trigger>
              <n-input
                v-model:value="formData.icon"
                placeholder="e.g. ph:database"
                @keydown.enter.prevent="handleCreate"
              >
                <template #suffix>
                  <Icon :name="formData.icon || 'ph:database'" size="18" style="color: #727379" />
                </template>
              </n-input>
            </template>

            <div class="icon-grid">
              <n-button
                v-for="icon in suggestedIcons"
                :key="icon"
                circle
                quaternary
                @click="selectIcon(icon)"
              >
                <template #icon>
                  <Icon :name="icon" size="20" />
                </template>
              </n-button>
            </div>
          </n-popover>
        </n-form-item>

        <div style="display: flex; justify-content: flex-end; margin-top: 12px">
          <n-button
            type="primary"
            attr-type="submit"
            :loading="isCreating"
            :disabled="!formData.name"
          >
            Create
          </n-button>
        </div>
      </n-form>
    </n-card>
  </n-modal>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import { useProjectMutation } from '~/composables/useProjects';

  const show = defineModel<boolean>('show', { default: false });
  const showIconPicker = ref(false);

  const suggestedIcons = [
    'ph:database',
    'ph:folder-simple',
    'ph:cloud',
    'ph:code',
    'ph:chart-bar',
    'ph:lock-key',
    'ph:globe',
    'ph:app-window',
    'ph:cube',
    'ph:rocket-launch',
    'ph:shield-check',
  ];

  const selectIcon = (iconName: string) => {
    formData.value.icon = iconName;
    showIconPicker.value = false;
  };

  const formRef = ref(null);
  const formData = ref({
    name: '',
    icon: '',
  });

  const rules = {
    name: {
      required: true,
      message: 'Please input project name',
      trigger: 'blur',
    },
  };

  const { mutate: createProject, isPending: isCreating } = useProjectMutation();

  const handleCreate = (e: Event) => {
    e.preventDefault();
    formRef.value?.validate((errors: any) => {
      if (!errors) {
        createProject(formData.value, {
          onSuccess: () => {
            show.value = false;
            formData.value = { name: '', icon: '' };
          },
        });
      }
    });
  };
</script>

<style scoped lang="scss">
  .icon-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    padding: 4px;

    :deep(.n-button) {
      color: #eaebeb;

      &:hover {
        color: #11af74;
        background-color: rgba(17, 175, 116, 0.1);
      }
    }
  }
</style>
