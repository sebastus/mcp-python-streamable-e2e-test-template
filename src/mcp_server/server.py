from mcp.server.fastmcp import FastMCP

from .server_instance import server, logger, cfg
from .resources.greeting import get_greeting
from .tools.calc import calc_add

# Create an MCP server instance.
# The server name "Demo" will be used in logging.
server: FastMCP = FastMCP("Demo", host="127.0.0.1")


# Register tools and resources with the server
@server.tool()
def add(a: int, b: int): 
    return calc_add(a, b)


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
