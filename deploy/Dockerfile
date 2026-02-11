# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Production stage
FROM python:3.12-slim AS production

WORKDIR /app

# Install make and curl for migrations
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download golang-migrate
RUN curl -L https://github.com/golang-migrate/migrate/releases/download/v4.16.2/migrate.linux-amd64.tar.gz | tar xvz && \
    mv migrate /usr/local/bin/migrate

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src ./src

# Copy Makefile and migrations
COPY Makefile ./
COPY src/db/migrations ./src/db/migrations

# Copy entrypoint script
COPY entrypoint.sh ./entrypoint.sh

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Change ownership to non-root user
RUN chmod +x ./entrypoint.sh && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Run the application
ENTRYPOINT ["./entrypoint.sh"]
