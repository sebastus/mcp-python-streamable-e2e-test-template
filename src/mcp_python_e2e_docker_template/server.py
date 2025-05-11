import logging
import os

from mcp.server.fastmcp import FastMCP

from .config import Config

# Load configuration
cfg = Config()

# If MCP_SERVER_PORT is set (e.g., in test environments) and FASTMCP_PORT is not,
# ensure FASTMCP_PORT (used by FastMCP) defaults to MCP_SERVER_PORT.
# This allows overriding the port for testing purposes.
if cfg.mcp_server_port and not cfg.fastmcp_port:
    os.environ.setdefault("FASTMCP_PORT", cfg.mcp_server_port)
elif cfg.fastmcp_port:  # If FASTMCP_PORT is explicitly set, ensure it's used.
    os.environ["FASTMCP_PORT"] = cfg.fastmcp_port


# Create an MCP server instance.
# The server name "Demo" will be used in logging.
server: FastMCP = FastMCP("Demo")

# Configure logging.
# The log level is sourced from the Config object.
# Logging is configured after server instance creation to use the server's name.
logging.basicConfig(
    level=cfg.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(server.name)


# Define an 'add' tool.
# This tool takes two integers 'a' and 'b' and returns their sum.
@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    logger.debug(f"Tool 'add' called with a={a}, b={b}")
    result = a + b
    logger.debug(f"Tool 'add' result: {result}")
    return result


# Define a 'greeting' resource.
# This resource takes a 'name' from the URI (e.g., greeting://World)
# and returns a personalized greeting string.
@server.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    logger.debug(f"Resource 'greeting://{name}' accessed")
    greeting = f"Hello, {name}!"
    logger.debug(f"Resource 'greeting://{name}' result: {greeting}")
    return greeting


def main() -> None:
    """Console script entry point for running the MCP server."""
    # Determine the transport mechanism from the MCP_TRANSPORT environment variable,
    # defaulting to "streamable-http".
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    logger.info(
        f"Starting server '{server.name}' with transport '{transport}' using FastMCP.run()"
    )
    # The port is determined by the FASTMCP_PORT environment variable (defaulting to 8000 by FastMCP)
    # or MCP_SERVER_PORT if FASTMCP_PORT is not set (handled at the beginning of the script).
    server.run(transport=transport)


if __name__ == "__main__":
    main()
