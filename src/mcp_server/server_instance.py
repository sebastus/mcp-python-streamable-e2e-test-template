import logging
import os
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from .config import Config

# Load configuration
load_dotenv(".env")
cfg = Config()

# If MCP_SERVER_PORT is set (e.g., in test environments) and FASTMCP_PORT is not,
# ensure FASTMCP_PORT (used by FastMCP) defaults to MCP_SERVER_PORT.
# This allows overriding the port for testing purposes.
if cfg.mcp_server_port and not cfg.fastmcp_port:
    os.environ.setdefault("FASTMCP_PORT", cfg.mcp_server_port)
elif cfg.fastmcp_port:  # If FASTMCP_PORT is explicitly set, ensure it's used.
    os.environ["FASTMCP_PORT"] = cfg.fastmcp_port

# Configure logging.
# The log level is sourced from the Config object.
logging.basicConfig(
    level=cfg.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Configure OpenTelemetry to use Azure Monitor with the
# APPLICATIONINSIGHTS_CONNECTION_STRING environment variable.
configure_azure_monitor(
    logger_name="mcp-server-demo",
)

logger = logging.getLogger("mcp-server-demo")

# Create an MCP server instance.
# The server name "Demo" will be used in logging.
server: FastMCP = FastMCP("Demo", host="127.0.0.1")
