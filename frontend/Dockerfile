FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

ENV NUXT_PUBLIC_API_BASE_URL="/api"

RUN npx nuxi prepare
RUN npm run generate

FROM nginx:1.27-alpine AS production
COPY --from=build /app/.output/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]