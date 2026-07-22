ARG NODE_VERSION=22-alpine
ARG API_URL=http://backend:8080

FROM node:${NODE_VERSION} AS base

FROM base AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

FROM base AS builder
ARG API_URL
WORKDIR /app
COPY package.json ./
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN NEXT_PUBLIC_API_URL=${API_URL} npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_PUBLIC_API_URL=${API_URL} \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3000 || exit 1

CMD ["node", "server.js"]
