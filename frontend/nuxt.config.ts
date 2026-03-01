import { fileURLToPath } from 'node:url';

export default defineNuxtConfig({
  ssr: false,

  compatibilityDate: '2025-07-15',
  
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL,
    },
  },
  
  modules: [
    '@bg-dev/nuxt-naiveui',
    '@vueuse/nuxt',
    '@pinia/nuxt',
    '@nuxt/eslint',
    '@nuxt/icon',
  ],
  
  eslint: {
    config: {
      stylistic: false, 
    },
  },

  devtools: { enabled: true },
  
   css: ['~/assets/styles/main.scss'],

  alias: {
    '@styles': fileURLToPath(new URL('./assets/styles', import.meta.url)),
    '@components': fileURLToPath(new URL('./components', import.meta.url)),
    '@layouts': fileURLToPath(new URL('./layouts', import.meta.url)),
    '@pages': fileURLToPath(new URL('./pages', import.meta.url)),
    '@composables': fileURLToPath(new URL('./composables', import.meta.url)),
  },

  devServer: {
    host: '0.0.0.0',
    port: 3000,
  },

  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @use "~/assets/styles/_variables.scss" as *;
            @use "~/assets/styles/mixins.scss" as *;
          `,
        },
      },
    },
  },

  typescript: {
    strict: true,
    typeCheck: process.env.NODE_ENV === 'production', 
  },

  naiveui: {
    colorModePreference: 'dark',
    iconSize: 18,
  },
});