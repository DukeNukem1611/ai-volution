# Use Python 3.12 slim image as base, supporting multithreading
FROM python:3.12-slim

# Set non-interactive mode to avoid timezone prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install curl and build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    python3-dev \
    && curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Poetry files 
COPY pyproject.toml poetry.lock ./

# Install dependencies with Poetry
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Create a script to wait for database and run migrations
RUN echo '#!/bin/bash\n\

    poetry run alembic upgrade head\n\
    poetry run python main.py' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expose the necessary ports
EXPOSE 8000

# Run the application with the entrypoint script
CMD ["/app/entrypoint.sh"]
