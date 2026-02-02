# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package files first
COPY package.json package-lock.json* ./

# Install all dependencies (including new ones like tsconfig-paths-webpack-plugin)
RUN npm ci

# Copy configuration files
COPY tsconfig.json ./
COPY next.config.mjs ./
COPY postcss.config.mjs ./
COPY tailwind.config.ts ./
COPY .eslintrc* ./
COPY eslint.config.mjs ./
COPY next-env.d.ts ./

# Copy source directory
COPY src ./src
COPY public ./public

# Build environment variables (passed at build time)
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Verify tsconfig.json is present and paths are correct
RUN cat tsconfig.json | grep -A 2 '"paths"' || echo "WARNING: paths not found in tsconfig.json"

# Verify next.config.mjs is present
RUN test -f next.config.mjs && echo "✓ next.config.mjs found" || echo "ERROR: next.config.mjs not found"
RUN cat next.config.mjs | grep -A 2 "webpack" || echo "WARNING: webpack config not found"

# Verify source files are present
RUN ls -la src/lib/ || echo "ERROR: src/lib directory not found"
RUN test -f src/lib/auth.ts && echo "✓ auth.ts found" || echo "ERROR: auth.ts not found"
RUN test -f src/lib/api.ts && echo "✓ api.ts found" || echo "ERROR: api.ts not found"

# Build the application
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built files
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set permissions
USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]

