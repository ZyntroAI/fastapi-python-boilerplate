dockerfile
FROM node:26-alpine AS deps
COPY package*.json ./
RUN npm ci

...

FROM node:26-alpine AS production
...
RUN npm ci --omit=dev && npm cache clean --force

USER node
EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget -qO- http://127.0.0.1:4000/health || exit 1

CMD ["node", "dist/index.js"]
