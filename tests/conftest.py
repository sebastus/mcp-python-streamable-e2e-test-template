import logging
import os
import socket
import subprocess
import time
from contextlib import closing
from typing import Dict, Generator, List, Optional

import pytest

# Configure logging for conftest.
# This setup allows log level configuration via the LOG_LEVEL environment variable.
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_socket(host: str, port: int) -> bool:
    """
    Check if a socket is open and listening on the given host and port.

    Args:
        host: The hostname or IP address to check.
        port: The port number to check.

    Returns:
        True if the socket is open, False otherwise.
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(1)  # 1-second timeout for the connection attempt
        if sock.connect_ex((host, port)) == 0:
            return True
    return False


@pytest.fixture(scope="session")
def mcp_server_url() -> Generator[str, None, None]:
    """
    Pytest fixture to start and stop the MCP server for the test session.
    It manages the server lifecycle, ensuring it's running before tests
    and stopped afterwards.

    Yields:
        The URL of the running MCP server (e.g., "http://localhost:8001/mcp").
    """
    server_process: Optional[subprocess.Popen] = None
    host: str = "localhost"
    port: int = 8001  # Dedicated port for testing to avoid conflicts
    server_url: str = f"http://{host}:{port}/mcp"

    try:
        # Command to start the MCP server using the 'mcp-server-demo' entry point.
        server_command: List[str] = [
            "python",
            "-m",
            "uv",
            "run",
            "mcp-server-demo",
        ]
        # Copy current environment variables and set specific ones for the server.
        server_env: Dict[str, str] = os.environ.copy()
        server_env["MCP_SERVER_PORT"] = str(port)  # Pass the test port to the server
        if "LOG_LEVEL" in os.environ:  # Propagate LOG_LEVEL if set for tests
            server_env["LOG_LEVEL"] = os.environ["LOG_LEVEL"]

        logger.info(
            f'Starting MCP server for testing with command: "{" ".join(server_command)}" on port {port}'
        )

        # Start the server as a subprocess.
        server_process = subprocess.Popen(
            server_command,
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE,  # Capture standard error
            env=server_env,
            text=True,  # Decode stdout/stderr as text
            bufsize=1,  # Line-buffered output
        )

        # Wait for the server to become ready.
        max_wait_time_seconds: int = 60
        poll_interval_seconds: float = 0.5
        start_time: float = time.time()
        server_ready: bool = False

        logger.info(
            f"Waiting for MCP server to start at {server_url} (max {max_wait_time_seconds}s)..."
        )

        # Loop until the server is ready or timeout is reached.
        while time.time() - start_time < max_wait_time_seconds:
            if server_process.poll() is not None:  # Check if process has terminated
                logger.error(
                    f"MCP server process terminated prematurely. Exit code: {server_process.returncode}"
                )
                # Output will be logged in the final exception block if termination was unexpected.
                raise RuntimeError(
                    f"MCP server process terminated prematurely with code {server_process.returncode}. Check logs."
                )

            if check_socket(host, port):  # Check if the server socket is listening
                logger.info(
                    f"MCP server started successfully and listening at {server_url}"
                )
                server_ready = True
                break

            logger.debug(f"Still waiting for MCP server at {host}:{port}...")
            time.sleep(poll_interval_seconds)

        if not server_ready:
            logger.error(
                f"MCP server did not start at {host}:{port} within {max_wait_time_seconds} seconds."
            )
            raise RuntimeError(
                f"MCP server failed to start at {server_url} within timeout. Check server logs and test setup."
            )

        yield server_url  # Provide the server URL to the tests

    except Exception as e:
        logger.error(f"Error during MCP server fixture setup: {e}", exc_info=True)
        # Attempt to terminate the server process if it's still running.
        if server_process and server_process.poll() is None:
            server_process.terminate()
        # Log any output from the server process on failure.
        if server_process:
            try:
                stdout, stderr = server_process.communicate(timeout=5)
                if stdout:
                    logger.error(f"Server stdout on failure:\n{stdout.strip()}")
                if stderr:
                    logger.error(f"Server stderr on failure:\n{stderr.strip()}")
            except subprocess.TimeoutExpired:
                logger.warning(
                    "Timeout waiting for server output after failure, killing."
                )
                if server_process.poll() is None:
                    server_process.kill()
        raise  # Re-raise the caught exception to fail the test setup

    finally:
        # Ensure the server process is stopped after tests are done.
        if (
            server_process and server_process.poll() is None
        ):  # Check if process is still running
            logger.info(f"Stopping MCP server (PID: {server_process.pid})...")
            server_process.terminate()  # Send SIGTERM for graceful shutdown
            try:
                # Wait for graceful termination and capture any final output.
                stdout, stderr = server_process.communicate(timeout=10)
                logger.info("MCP server terminated gracefully.")
                if stdout and stdout.strip():
                    logger.debug(f"Final server stdout on shutdown:\n{stdout.strip()}")
                if stderr and stderr.strip():
                    logger.debug(f"Final server stderr on shutdown:\n{stderr.strip()}")
            except subprocess.TimeoutExpired:
                # If graceful shutdown fails, force kill the process.
                logger.warning(
                    "MCP server did not terminate gracefully after 10s, sending SIGKILL..."
                )
                server_process.kill()  # Send SIGKILL
                try:
                    # Capture output after SIGKILL.
                    stdout, stderr = server_process.communicate(timeout=5)
                    logger.info("MCP server killed.")
                    if stdout and stdout.strip():
                        logger.debug(
                            f"Final server stdout after SIGKILL:\n{stdout.strip()}"
                        )
                    if stderr and stderr.strip():
                        logger.debug(
                            f"Final server stderr after SIGKILL:\n{stderr.strip()}"
                        )
                except subprocess.TimeoutExpired:
                    logger.error(
                        "MCP server did not stop even after SIGKILL. Manual intervention may be needed."
                    )
        elif server_process:  # Process existed but had already terminated
            logger.info(
                f"MCP server (PID: {server_process.pid}) already terminated with code {server_process.returncode}."
            )
            # If it terminated before being ready, try to capture any output not already logged.
            if not server_ready:
                try:
                    stdout, stderr = server_process.communicate(
                        timeout=1
                    )  # Short timeout
                    if stdout and stdout.strip():
                        logger.error(
                            f"Server stdout (terminated early):\n{stdout.strip()}"
                        )
                    if stderr and stderr.strip():
                        logger.error(
                            f"Server stderr (terminated early):\n{stderr.strip()}"
                        )
                except subprocess.TimeoutExpired:
                    logger.debug("No further output from early-terminated server.")
        else:  # server_process was None (never started or already cleaned up)
            logger.info("MCP server process was not started or already cleaned up.")
