# --- Frontend Base ---
FROM docker.io/library/node:22-alpine AS frontend-base
WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci

# --- Frontend Development ---
FROM frontend-base AS frontend-dev
COPY web/ .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# --- Frontend Builder ---
FROM frontend-base AS frontend-builder
COPY web/ .
RUN npm run build

# --- Backend Base ---
FROM docker.io/library/python:3.12-slim AS backend-base

RUN apt-get update && apt-get install -y --no-install-recommends locales && \
    localedef --no-archive -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG=fr_FR.UTF-8 \
    LANGUAGE=fr_FR:fr \
    LC_ALL=fr_FR.UTF-8

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# uv is a Rust binary; under QEMU cross-arch emulation its multithreaded
# downloader/installer intermittently segfaults (known upstream QEMU/Rust
# bug, unresolved as of uv 0.12). Serializing these operations avoids it.
ENV UV_CONCURRENT_DOWNLOADS=1 \
    UV_CONCURRENT_BUILDS=1 \
    UV_CONCURRENT_INSTALLS=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# --- Backend Development ---
FROM backend-base AS backend-dev
COPY shared_planner/ ./shared_planner/
COPY templates/ ./templates/
RUN uv sync --frozen --no-dev
CMD ["sh", "-c", "uv run init_settings && uv run uvicorn shared_planner.api:app --host 0.0.0.0 --port 8000 --reload --reload-dir shared_planner --reload-dir templates --reload-exclude 'database.db'"]

# --- Frontend Production (nginx) ---
FROM docker.io/library/nginx:alpine AS frontend-prod
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-builder /app/web/dist /usr/share/nginx/html
EXPOSE 80

# --- Production ---
FROM backend-base AS production
COPY shared_planner/ ./shared_planner/
COPY templates/ ./templates/
COPY entrypoint.sh ./

RUN uv sync --frozen --no-dev && chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
