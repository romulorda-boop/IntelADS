FROM node:22.13.0-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=3000 \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ffmpeg python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv \
    && corepack enable \
    && corepack prepare pnpm@11.25.0 --activate

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY backend/requirements.txt ./backend/requirements.txt

RUN pnpm install --frozen-lockfile \
    && pip install --no-cache-dir -r backend/requirements.txt

COPY . .

RUN pnpm --filter @adintel/web build \
    && chown -R node:node /app/apps/web/.next \
    && chmod 0755 /app/docker-entrypoint.sh

ENV NODE_ENV=production

EXPOSE 3000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
