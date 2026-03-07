<template>
  <n-card class="auth-card" hoverable>
    <n-card-header class="header">
      <!-- Icon -->
    </n-card-header>

    <n-tabs v-model:value="activeTab" size="large" justify-content="space-evenly">
      <n-tab-pane name="login">
        <div class="pane-text">
          <h2>Log in to account</h2>
          <p>to start using tool</p>
        </div>

        <n-form ref="loginFormRef" :model="loginModel" :rules="loginRules">
          <n-form-item path="email" label="Email" label-style="margin-left: .25rem">
            <n-input v-model:value="loginModel.email" placeholder="admin@example.com">
              <template #prefix>
                <Icon name="mdi:email" size="14" />
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password" label="Password" label-style="margin-left: .25rem">
            <n-input
              v-model:value="loginModel.password"
              type="password"
              show-password-on="click"
              placeholder="••••••••"
            >
              <template #prefix>
                <Icon name="solar:password-outline" size="16" />
              </template>
            </n-input>
          </n-form-item>

          <div class="other-auth-options">
            <div class="auth-option-container google">
              <Icon name="mdi:google" size="24" />
            </div>
            <div class="auth-option-container github">
              <Icon name="mdi:github" size="24" />
            </div>
          </div>

          <n-button
            type="primary"
            block
            class="handler-button"
            :loading="isLoginPending"
            @click="handleLogin"
            >Log In</n-button
          >

          <div class="toggle-link">
            Do not have an account?
            <n-button text type="primary" @click="activeTab = 'register'"> Register </n-button>
          </div>
        </n-form>
      </n-tab-pane>

      <n-tab-pane name="register">
        <div class="pane-text">
          <h2>Create an account</h2>
          <p>to start using tool</p>
        </div>

        <n-form ref="registerFormRef" :model="registerModel" :rules="registerRules">
          <n-form-item path="email" label="Email" label-style="margin-left: .25rem">
            <n-input v-model:value="registerModel.email" placeholder="admin@example.com">
              <template #prefix>
                <Icon name="mdi:email" size="14" />
              </template>
            </n-input>
          </n-form-item>
          <n-form-item path="username" label="Username" label-style="margin-left: .25rem">
            <n-input v-model:value="registerModel.username" placeholder="user25">
              <template #prefix>
                <Icon name="solar:user-bold" size="14" />
              </template>
            </n-input>
          </n-form-item>
          <n-form-item path="password" label="Password" label-style="margin-left: .25rem;">
            <n-input
              v-model:value="registerModel.password"
              type="password"
              show-password-on="click"
              placeholder="••••••••"
            >
              <template #prefix>
                <Icon name="solar:password-outline" size="16" />
              </template>
            </n-input>
          </n-form-item>
          <n-button
            type="primary"
            block
            class="handler-button"
            :loading="isRegisterPending"
            @click="handleRegister"
            >Sign Up</n-button
          >

          <div class="toggle-link">
            Already have an account?
            <n-button text type="primary" @click="activeTab = 'login'"> Log in </n-button>
          </div>
        </n-form>
      </n-tab-pane>
    </n-tabs>
  </n-card>
</template>

<script setup lang="ts">
  import type { FormInst, FormRules, FormItemRule } from 'naive-ui';
  import { AuthSchema } from '~/schemas/auth.schema';
  import { useMutation } from '@tanstack/vue-query';
  import { useMessage } from 'naive-ui';
  import { ref } from 'vue';

  definePageMeta({
    layout: 'auth',
  });

  const activeTab = ref('login');

  const createZodRule = (field: keyof typeof AuthSchema.shape): FormItemRule => ({
    trigger: ['input', 'blur'],
    validator: (_, value) => {
      const result = AuthSchema.shape[field].safeParse(value);
      if (!result.success) return new Error(JSON.parse(result.error.message)[0].message);
      return true;
    },
  });

  const loginFormRef = ref<FormInst | null>(null);
  const registerFormRef = ref<FormInst | null>(null);

  const loginModel = ref({ email: '', password: '' });
  const registerModel = ref({ email: '', username: '', password: '' });

  const loginRules: FormRules = {
    email: createZodRule('email'),
    password: createZodRule('password'),
  };

  const registerRules: FormRules = {
    email: createZodRule('email'),
    username: createZodRule('username'),
    password: createZodRule('password'),
  };

  const message = useMessage();

  const { mutate: login, isPending: isLoginPending } = useMutation({
    mutationFn: async (credentials: typeof loginModel.value) => {
      return await $fetch('http://127.0.0.1:8000/api/v1/auth/login', {
        method: 'POST',
        body: credentials,
      });
    },
    onSuccess: (data) => {
      console.log('Токен получен:', data);
      message.success('Успешный вход!');
    },
    onError: (error: any) => {
      message.error(error.data?.detail || 'Authorization error');
    },
  });

  const { mutate: register, isPending: isRegisterPending } = useMutation({
    mutationFn: async (userData: typeof registerModel.value) => {
      return await $fetch('http://127.0.0.1:8000/api/v1/auth/register', {
        method: 'POST',
        body: userData,
      });
    },
    onSuccess: () => {
      message.success('Аккаунт создан! Теперь вы можете войти.');
      activeTab.value = 'login';
    },
    onError: (error: any) => {
      message.error(error.data?.detail || 'Registration error');
    },
  });

  const handleLogin = async () => {
    await loginFormRef.value?.validate((errors) => {
      if (!errors) {
        login(loginModel.value);
      }
    });
  };

  const handleRegister = async () => {
    await registerFormRef.value?.validate((errors) => {
      if (!errors) {
        register(registerModel.value);
      }
    });
  };
</script>

<style scoped lang="scss">
  :deep(.n-tabs-nav) {
    display: none !important;
  }

  .auth-card {
    width: 400px;
    height: 500px;
    border-width: 2px;
  }

  .toggle-link {
    margin-top: 16px;
    text-align: center;
    font-size: 14px;
    color: $gray;
  }

  .pane-text {
    color: $white;
    p {
      margin-left: 0.25rem;
      color: $gray;
    }

    margin-bottom: 2rem;
  }

  .other-auth-options {
    margin-left: 45px;
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 2rem;
    align-items: center;
    border-top: 2px solid $medium;
    width: 250px;
    margin-bottom: 3.15rem;
    margin-top: 1rem;

    .auth-option-container {
      background-color: $dark;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      margin-top: 1rem;
    }
  }

  .handler-button {
    width: 15rem;
    margin-left: 50px;
    margin-top: 2rem;
  }
</style>
