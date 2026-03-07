import { ofetch } from 'ofetch';


export const apiClient = ofetch.create({  
  async onRequest({ request, options }) {
    const config = useRuntimeConfig();
    options.baseURL = config.public.apiBaseUrl as string;
  },

  async onResponseError({ request, response, options }) {
    console.error('[API Error]', response.status, response._data);
  },
});
