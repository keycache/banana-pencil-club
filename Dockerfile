# syntax=docker/dockerfile:1
############################################################
# Multi-stage build for a uv-managed Streamlit app
#
# Cloud Run currently schedules x86_64 (amd64) by default.
# If you build on Apple Silicon without specifying platform
# you'll get an arm64 image and hit: exec format error.
#
# Build for Cloud Run:
#   docker buildx build --platform=linux/amd64 -t gcr.io/PROJECT_ID/banana-pencil-club:latest .
#   docker push gcr.io/PROJECT_ID/banana-pencil-club:latest
#   gcloud run deploy banana-pencil-club \
#       --image gcr.io/PROJECT_ID/banana-pencil-club:latest \
#       --region=REGION --platform=managed --allow-unauthenticated
#
# For multi-arch (push both):
#   docker buildx build --platform=linux/amd64,linux/arm64 -t gcr.io/PROJECT_ID/banana-pencil-club:latest --push .
############################################################

## Architecture is fixed to linux/amd64 to avoid exec format errors on Cloud Run
## (Built on Apple Silicon hosts this will use qemu for build but produce the correct image.)

############################
# Stage 1: dependency layer #
############################
FROM --platform=linux/amd64 python:3.13-slim AS deps

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1 \
    PATH="/root/.local/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system deps (add more if your libs need them)
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends curl build-essential libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (https://github.com/astral-sh/uv)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy only project metadata first for better layer caching
COPY pyproject.toml uv.lock ./

# Sync dependencies into a local .venv (no dev deps by default)
RUN uv sync --frozen --no-dev

###########################
# Stage 2: runtime image  #
###########################
FROM --platform=linux/amd64 python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}" \
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# Copy virtual environment from deps stage (already built for target platform)
COPY --from=deps /app/.venv ./.venv

# Quick diagnostic (left in final image, cheap): log forced architecture & python version
RUN echo "[build] forced platform: linux/amd64" && python -V


# Copy application source (all python modules, pages, static assets)
COPY ./*.py ./
COPY pages ./pages
COPY static ./static
COPY README.md ./

# Create writable data directory for generated stories & images
RUN mkdir -p .data/stories .data/images && chmod -R 775 .data

# Optional: make it a volume so data persists (user can override)
VOLUME ["/app/.data"]

EXPOSE 8080

# Default command runs the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]
