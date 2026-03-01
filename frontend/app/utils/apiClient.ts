import { ofetch } from 'ofetch';

const config = useRuntimeConfig()

export const apiClient = ofetch.create({
  // baseURL: config.public.apiBaseUrl,
  baseURL: '/api',
  
  async onRequest({ request, options }) {
  },
  
  async onResponseError({ request, response, options }) {
    console.error('[API Error]', response.status, response._data);
  }
});