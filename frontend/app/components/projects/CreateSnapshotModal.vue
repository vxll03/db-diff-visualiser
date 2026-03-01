<template>
  <n-modal v-model:show="show">
    <n-card
      style="width: 400px"
      title="Create New Snapshot"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
      class="custom-modal"
    >
      <n-form ref="formRef" :model="formData" :rules="rules" @submit="handleCreate">
        <n-form-item path="fileList" label="Migration File">
          <n-upload
            v-model:file-list="formData.fileList"
            multiple
            :max="50"
            :default-upload="false"
            accept=".py"
          >
            <n-upload-dragger>
              <div style="margin-bottom: 12px">
                <Icon name="ph:upload-simple" size="48" class="dragger-img" />
              </div>
              <n-text class="dragger-text"> Click or drag file here </n-text>
              <n-p depth="3" class="dragger-desc"> Strictly .py (alembic files) </n-p>
            </n-upload-dragger>
          </n-upload>
        </n-form-item>

        <div style="display: flex; justify-content: flex-end; margin-top: 12px">
          <n-button
            type="primary"
            attr-type="submit"
            :loading="isCreating"
            :disabled="formData.fileList.length === 0"
          >
            Create
          </n-button>
        </div>
      </n-form>
    </n-card>
  </n-modal>
</template>

<script setup lang="ts">
  import type { UploadFileInfo, FormInst } from 'naive-ui';
  import { useSnapshotMutation } from '~/composables/useMigrationMutation';

  const show = defineModel<boolean>('show', { default: false });

  const route = useRoute();
  const projectId = Number.parseInt(route.params.id as string);

  const formRef = ref<FormInst | null>(null);
  const formData = ref<{ fileList: UploadFileInfo[] }>({
    fileList: [],
  });

  const rules = {
    fileList: {
      type: 'array' as const,
      required: true,
      min: 1,
      message: 'Please upload a migration file',
      trigger: ['change'],
    },
  };

  const { mutate: createSnapshot, isPending: isCreating } = useSnapshotMutation();

  const handleCreate = (e: Event) => {
    e.preventDefault();
    formRef.value?.validate((errors: any) => {
      if (!errors) {
        const submitData = new FormData();

        formData.value.fileList.forEach((item: any) => {
          if (item.file) {
            submitData.append('files', item.file);
          }
        });

        createSnapshot(
          { projectId, formData: submitData },
          {
            onSuccess: () => {
              show.value = false;
              formData.value.fileList = [];
            },
          },
        );
      }
    });
  };
</script>

<style scoped lang="scss">
  .custom-modal {
    background-color: $medium;

    :deep(.n-card-header__main) {
      color: $white-secondary;
    }

    :deep(.n-upload-dragger) {
      background-color: rgba(255, 255, 255, 0.02);
      border: 2px dashed $light;
      transition: all 0.2s ease;

      &:hover {
        border-color: $accent;
        background-color: rgba(17, 175, 116, 0.05);
      }
    }
  }

  .dragger-text {
    font-size: 16px;
    color: $white-secondary;
  }
  .dragger-desc {
    margin-top: 8px;
    font-size: 12px;
    color: $gray;
  }
  .dragger-img {
    color: $accent;
  }
</style>
