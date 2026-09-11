# syntax=docker/dockerfile:1
#
# Production image for the product-crud API.
#
#   docker build -t product-crud-server:local .
#   docker run --rm -p 4000:4000 \
#     -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/products" \
#     product-crud-server:local
#
# Three stages: deps (full install) -> build (tsc) -> runtime (prod deps only).

# ---------- deps ----------
FROM node:22-alpine AS deps
WORKDIR /app

# Prisma's query engine links against OpenSSL; alpine ships without it.
RUN apk add --no-cache openssl

COPY package.json package-lock.json ./
COPY prisma ./prisma

# `npm ci` is used everywhere so the lockfile is authoritative.
RUN npm ci

# ---------- build ----------
FROM deps AS build
WORKDIR /app

COPY tsconfig.json ./
COPY src ./src

RUN npx prisma generate \
 && npm run build

# ---------- runtime ----------
FROM node:22-alpine AS runtime
WORKDIR /app

ENV NODE_ENV=production

# openssl for Prisma, tini so PID 1 forwards signals and reaps zombies
# (the app relies on SIGTERM for its graceful shutdown path).
RUN apk add --no-cache openssl tini \
 && addgroup -S -g 1001 nodejs \
 && adduser -S -u 1001 -G nodejs nodejs

COPY package.json package-lock.json ./
COPY prisma ./prisma

# --omit=dev drops typescript/vitest/supertest. `prisma` is a runtime dependency
# (it ships the CLI the entrypoint uses to apply the schema), so the generate
# step still works here.
RUN npm ci --omit=dev \
 && npx prisma generate \
 && npm cache clean --force

COPY --from=build /app/dist ./dist
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER nodejs
EXPOSE 4000

# Node 22 has a global fetch, so no curl/wget needed in the image.
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.PORT||4000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["node", "dist/index.js"]
