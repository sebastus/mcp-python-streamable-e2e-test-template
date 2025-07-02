from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .config import Config
from .resources.greeting import get_greeting
from .server_instance import server, logger, cfg
from .tools.calc import calc_add

# Create an MCP server instance.
# The server name "Demo" will be used in logging.
server: FastMCP = FastMCP("Demo", host="127.0.0.1")


# Register tools and resources with the server
@server.tool()
def add(a: int, b: int): 
    return calc_add(a, b)

@server.resource("greeting://{name}")
def greeting(name: str) -> str:
    return get_greeting(name)


def main() -> None:
    """Console script entry point for running the MCP server."""

    logger.info(
        f"Starting server '{server.name}' with transport '{cfg.mcp_transport}' using FastMCP.run()"
    )
    # The port is determined by the FASTMCP_PORT environment variable (defaulting to 8000 by FastMCP)
    # or MCP_SERVER_PORT if FASTMCP_PORT is not set (handled at the beginning of the script).
    server.run(transport=cfg.mcp_transport)


if __name__ == "__main__":
    main()
