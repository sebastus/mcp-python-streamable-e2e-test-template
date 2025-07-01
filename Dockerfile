# syntax=docker/dockerfile:1
FROM python:3.13-slim

# OCI metadata
LABEL org.opencontainers.image.licenses="MIT"

# Install system utilities and Python package manager 'uv'.
# - curl: For downloading files if needed.
# - git: For version control operations if needed during build.
# - openssh-client: For SSH operations (e.g., git push over SSH).
# --no-install-recommends: Avoids installing optional packages.
# Clean up apt lists to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        git \
        openssh-client \
    && pip install --no-cache-dir uv \
    && rm -rf /var/lib/apt/lists/*

# Ensure Python output is sent straight to terminal without being buffered.
ENV PYTHONUNBUFFERED=1

# Arguments for user and group creation, can be overridden at build time.
ARG APP_USER=appuser
ARG APP_GROUP=appgroup

# Create a non-root user and group for security.
# The user 'appuser' will own and run the application.
RUN groupadd ${APP_GROUP} && useradd -ms /bin/bash -g ${APP_GROUP} ${APP_USER}

# Set the working directory in the container.
WORKDIR /app

# Copy documentation files into the container.
COPY docs ./docs

# Copy project files required for dependency installation.
# This includes pyproject.toml and uv.lock (if it exists).
# Copying these first leverages Docker's layer caching if dependencies don't change.
COPY pyproject.toml uv.lock* ./
# Copy source code and README early so that the editable install can locate
# the package modules and README file during the build step.
COPY src/ ./src
COPY README.md ./README.md

# Create a virtual environment and install dependencies using uv.
# -e ".[test]": Installs the project in editable mode along with 'test' extras.
# --no-cache-dir: Disables pip's cache to reduce image size.
RUN uv venv .venv && \
    . .venv/bin/activate && \
    uv pip install --no-cache-dir -e ".[test,dev]"
    # Note: Added 'dev' dependencies for pre-commit hooks if needed in the image,
    # though typically pre-commit is a local dev tool.
    # If pre-commit is not run inside the final image, 'dev' can be removed here.

# Copy the rest of the application code into the container.
# Assumes .dockerignore is configured to exclude unnecessary files (e.g., .git, .venv).
COPY . .

# Change ownership of the /app directory and its contents to the appuser.
# This ensures the non-root user has permissions to operate in this directory.
RUN chown -R ${APP_USER}:${APP_GROUP} /app

# Switch to the non-root user for subsequent commands.
USER ${APP_USER}

# Add the virtual environment's bin directory to the PATH.
# This allows running executables from the venv directly (e.g., mcp-server-demo).
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="/app/.venv/bin:$PATH"
ENV FASTMCP_PORT=8000
ENV MCP_TRANSPORT="streamable-http"

# Document Exposure of the port the MCP server listens on.
EXPOSE 8000

# Define the default command to run when the container starts.
# This will execute the 'mcp-server-demo' script defined in pyproject.toml.
CMD ["mcp-server-demo"]
