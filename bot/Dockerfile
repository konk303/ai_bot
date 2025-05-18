FROM python:3.13-slim
# Allow statements and log messages to immediately appear
ENV PYTHONUNBUFFERED=True

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["uv", "run", "uvicorn", "main:api", "--port", "8080", "--host", "0.0.0.0"]
