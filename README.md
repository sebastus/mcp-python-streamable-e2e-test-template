# Python MCP Server Template (FastMCP + Docker/Devcontainer)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

This is a template project for efficiently developing Python-based Model Context Protocol (MCP) servers using [FastMCP](https://github.com/modelcontextprotocol/fastmcp) and Docker (Devcontainer).
It provides samples for basic MCP server functionalities (e.g., an `add` tool and a `greeting` resource), utilizes type hints, includes `Ruff` for static analysis and formatting, a test environment, and supports a ready-to-use development environment setup.

This repository is a **Streamable-ready End-to-End (E2E) test template** for MCP written in Python and comes with a **Docker/Devcontainer setup** out of the box.

---

**Detailed explanatory articles have been published!**

*   English (dev.to): [Python MCP Remote Server: The Dawn of the Streamable HTTP Era, with a Minimalist Template](https://dev.to/akitana-airtanker/python-mcp-remote-server-the-dawn-of-the-streamable-http-era-with-a-minimalist-template-1o6j)
*   Japanese (Qiita): [リモートサーバーで動かす Python MCP Server — Streamable HTTP 時代の始まり ~ uv / Docker / pytest を備えたミニマルテンプレート付き ~](https://qiita.com/airtanker/items/d940ef8c346c3644da3b)

---

## Table of Contents

*   [Features](#features)
*   [Prerequisites](#prerequisites)
*   [Setup (Local Environment)](#setup-local-environment)
    *   [Using Ruff (Linter/Formatter) Locally](#using-ruff-linterformatter-locally)
*   [Running the Server (Local Environment)](#running-the-server-local-environment)
*   [Running the Client (Local Environment)](#running-the-client-local-environment)
*   [Development with Devcontainer (Recommended)](#development-with-devcontainer-recommended)
*   [Running with Docker](#running-with-docker)
*   [Running Tests (pytest)](#running-tests-pytest)
    *   [Mechanism](#mechanism)
    *   [Execution](#execution)
*   [Connecting with MCP Inspector](#connecting-with-mcp-inspector)
*   [Current Features](#current-features)
*   [License](#license)

## Features

*   **MCP Python SDK**: Built upon the official [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk).
*   **FastMCP Based**: Uses [FastMCP](https://github.com/modelcontextprotocol/fastmcp) (part of the SDK), a lightweight and fast MCP server library for Python.
*   **Docker & Devcontainer**: Provides containerization with Docker and a consistent development environment with VS Code Dev Containers.
    *   The container runs as a non-root user (`appuser`) for enhanced security.
*   **Package Management with `uv`**: Employs `uv`, a fast Python package installer and resolver.
*   **Static Analysis and Formatting**: Linting and formatting with `Ruff` are pre-configured.
*   **Test Environment**: Sample asynchronous tests using `pytest` and `pytest-asyncio` with an execution environment.
*   **Type Hints**: Actively uses type hints throughout the project to improve code robustness and readability.
*   **Configurable Logging**: Log output can be controlled via the `LOG_LEVEL` environment variable (e.g., `DEBUG`, `INFO`, `WARNING`).

## Prerequisites

*   Python (3.10 or higher, see `pyproject.toml`. Dockerfile uses 3.13-slim)
*   `uv` (Python package management tool)
*   Docker (for container execution)
*   (Optional) VS Code and Dev Containers extension (for Devcontainer usage)

## Setup (Local Environment)

1.  **Create a new repository from this template or clone the repository.**
    Use the "Use this template" button on GitHub or clone as follows:
    ```bash
    git clone https://github.com/akitana-airtanker/mcp-python-streamable-e2e-test-template.git <your-project-name>
    cd <your-project-name>
    ```
    Replace `<your-project-name>` with your project's name.

2.  **Create a virtual environment and install dependencies.**
    Run the following commands in the project's root directory:
    ```bash
    uv venv
    uv pip install -e ".[test,dev]" # Install test and dev dependencies as well
    ```
    This creates a virtual environment in the `.venv` directory and installs the necessary packages (including those for testing and development) based on `pyproject.toml`.

### Using Ruff (Linter/Formatter) Locally
This template uses `Ruff`. To use it locally:
```bash
# Install Ruff (should already be installed with dev dependencies, but can be installed individually)
# uv pip install ruff
# Check code
ruff check .
# Format code
ruff format .
```
It's recommended to set up pre-commit hooks to automate this:
```bash
pre-commit install
```

## Running the Server (Local Environment)

1.  Activate the virtual environment (if not already activated).
    ```bash
    source .venv/bin/activate
    ```

2.  Start the server.
    ```bash
    mcp-server-demo
    ```
    The server will start at `http://0.0.0.0:8000` and listen for MCP requests.
    You can change the log verbosity by setting the `LOG_LEVEL` environment variable (e.g., `LOG_LEVEL=DEBUG mcp-server-demo`).

## Running the Client (Local Environment)

1.  Ensure the server is running.
2.  Open another terminal and activate the virtual environment.
    ```bash
    cd <your-project-name> # Navigate to the project root directory
    source .venv/bin/activate
    ```
3.  Run the client.
    ```bash
    mcp-client-demo
    ```
    The client will connect to the server, call the `add` tool, and print the result (`Result of add(10, 5): 15`) to the console.
    You can control the client's output verbosity using the `--quiet` or `--verbose` flags:
    ```bash
    mcp-client-demo --quiet   # Suppresses print statements, logs WARNING and above
    mcp-client-demo --verbose # Enables DEBUG logging and print statements
    ```
    The `LOG_LEVEL` environment variable can also be used to set the logging level, with CLI flags taking precedence if specified.

## Development with Devcontainer (Recommended)

Using VS Code Dev Containers allows for an easy setup of a consistent development environment with all necessary tools and configurations.

1.  **Prerequisites**:
    *   [Visual Studio Code](https://code.visualstudio.com/)
    *   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
    *   VS Code's [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (recommended, though VS Code may automatically suggest installing it)

2.  **Open the Development Container**:
    *   Open this project folder in VS Code.
    *   VS Code will detect the `.devcontainer/devcontainer.json` file and show a notification "Reopen in Container" in the bottom right. Click this notification.
    *   Alternatively, open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P), type "Dev Containers: Reopen in Container", and execute it.

3.  **Working inside the Container**:
    *   Once the container is built and started, VS Code will automatically connect to the project inside the container.
    *   Opening a terminal will open a terminal inside the container.
    *   `mcp-server-demo` and `mcp-client-demo` can be run directly in this container terminal.
        ```bash
        # Start the server (in the container terminal)
        mcp-server-demo

        # Run the client (in another container terminal)
        mcp-client-demo
        ```
    *   Dependencies (including `test` and `dev` extras) are installed via the Dockerfile and `postCreateCommand` in `devcontainer.json`, so all necessary packages are available when the container starts. Pre-commit hooks are also installed.
    *   Linting and formatting with `Ruff` will be performed automatically due to VS Code settings.
    *   The container runs as a non-root user (`appuser`).
    *   Port 8000 is automatically forwarded, so you can access `http://localhost:8000/mcp` (for MCP Inspector) from your host machine's browser.

## Running with Docker

1.  **Build the Docker image.**
    Run the following command in the project's root directory:
    ```bash
    docker build -t mcp-server .
    ```

2.  **Run the Docker container.**
    ```bash
    docker run -p 8000:8000 -e LOG_LEVEL=DEBUG mcp-server
    ```
    This starts the MCP server inside the container and maps it to port 8000 on the host. You can control the server's log level in the container by passing environment variables like `-e LOG_LEVEL=DEBUG`. The container runs as a non-root user (`appuser`).

## Running Tests (pytest)

This repository includes a minimal test setup located in the `tests/` directory (e.g., `tests/test_client.py`).
The tests start the FastMCP server on a **dedicated port 8001** (configured in `tests/conftest.py`) and verify that tool calls work correctly.

### Mechanism

* The `tests/conftest.py` fixture passes `MCP_SERVER_PORT=8001` as an environment variable to the child process when starting the server process.
* In `src/mcp_python_streamable_e2e_test_template/server.py`, the `Config` class reads `MCP_SERVER_PORT` and `FASTMCP_PORT`. If `MCP_SERVER_PORT` is set and `FASTMCP_PORT` is not, `FASTMCP_PORT` (used by FastMCP) defaults to the value of `MCP_SERVER_PORT`.
  ```python
  # src/mcp_python_streamable_e2e_test_template/server.py
  # ...
  from .config import Config
  cfg = Config()
  if cfg.mcp_server_port and not cfg.fastmcp_port:
      os.environ.setdefault("FASTMCP_PORT", cfg.mcp_server_port)
  # ...
  ```
  This ensures that **normal startup (`mcp-server-demo`) defaults to port 8000** (or the value of `FASTMCP_PORT` / `MCP_SERVER_PORT` if set), while **pytest execution uses port 8001** for the server.

### Execution

```bash
# Assuming the virtual environment is activated
pytest
```

If the tests pass, you will see output similar to this:

```
collected 1 item

test_client.py .                                                       [100%]

============================= 1 passed in X.XXs =============================
```

---

## Connecting with MCP Inspector

With the server running locally or in Docker, you can connect to it using MCP Inspector to verify its behavior.

1.  **Start MCP Inspector.**
    Run the following command in a new terminal:
    ```bash
    npx --yes @modelcontextprotocol/inspector
    ```

2.  **Connect to MCP Inspector.**
    Once MCP Inspector opens in your browser, connect with the following settings:
    *   **Transport Type**: `Streamable HTTP`
    *   **URL**: `http://localhost:8000/mcp`

## Current Features

*   **`add` Tool**: Adds two numbers.
    *   Example Input: `{"a": 10, "b": 5}`
    *   Example Output: `15` (as TextContent)
*   **`greeting` Resource**: Returns a greeting for a specified name.
    *   Example URI: `greeting://World`
    *   Example Output: `"Hello, World!"`

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
