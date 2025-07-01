import argparse
import asyncio
import logging
import os
import sys  # Added for sys.exit
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)

async def run_client(quiet: bool, verbose: bool) -> None:
    """Runs the MCP client to connect to the server and call a tool.

    Args:
        quiet: If True, suppress print statements.
        verbose: If True, set logging level to DEBUG.
    """
    # URL of the target server.
    # Read from environment variable with fallback to default
    server_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")

    try:
        logger.info(f"Connecting to MCP server at {server_url}...")
        # Connect to the server using the streamable HTTP client.
        # This context manager provides read/write streams and a session ID callback.
        async with streamablehttp_client(server_url) as (
            client_read_stream,
            client_write_stream,
            client_get_session_id_callback,
        ):
            read_stream: Any = client_read_stream  # Type hint for the readable stream
            write_stream: Any = client_write_stream  # Type hint for the writable stream
            get_session_id_callback: Callable[[], Optional[str]] = (
                client_get_session_id_callback  # Callback to get session ID
            )

            # Create a ClientSession using the established streams.
            async with ClientSession(read_stream, write_stream) as current_session:
                session: ClientSession = current_session
                # Initialize the session with the server.
                await session.initialize()
                session_id: Optional[str] = get_session_id_callback()
                logger.info(
                    f"Successfully connected to server. Session ID: {session_id}"
                )

                # Prepare to call the 'add' tool.
                tool_name: str = "add"
                arguments: Dict[str, Any] = {"a": 10, "b": 5}
                logger.info(f"Calling tool '{tool_name}' with arguments: {arguments}")

                # Call the tool and await the response.
                response_object: types.CallToolResult = await session.call_tool(
                    tool_name, arguments
                )

                logger.info(
                    f"Raw response object from tool '{tool_name}': {response_object}"
                )

                # Process the response.
                if response_object.isError:
                    # If isError is True, the content might hold error details.
                    logger.error(
                        f"Tool '{tool_name}' returned an error: {response_object.content}"
                    )
                    if not quiet:
                        print(
                            f"Tool '{tool_name}' returned an error: {response_object.content}"
                        )
                elif response_object.content and isinstance(
                    response_object.content, list
                ):
                    actual_content_list: List[types.Content] = response_object.content
                    if actual_content_list:  # Check if the list is not empty
                        first_content: types.Content = actual_content_list[0]
                        if (
                            isinstance(first_content, types.TextContent)
                            and first_content.type == "text"
                        ):
                            try:
                                # Attempt to parse the result as an integer.
                                result_value: int = int(first_content.text)
                                if not quiet:
                                    print(f"Result of add(10, 5): {result_value}")
                            except ValueError:
                                logger.warning(
                                    f"Could not parse result of add(10, 5) as int: {first_content.text}"
                                )
                                if not quiet:
                                    print(
                                        f"Result of add(10, 5) (text): {first_content.text}"
                                    )
                        else:
                            logger.warning(
                                f"Tool '{tool_name}' returned content of unexpected type or structure. First content item: {first_content}. Full content list: {actual_content_list}"
                            )
                            if not quiet:
                                print(
                                    f"Tool '{tool_name}' returned content of unexpected type or structure. First content item: {first_content}. Full content list: {actual_content_list}"
                                )
                    else:
                        logger.warning(
                            f"Tool '{tool_name}' returned an empty content list. Full response object: {response_object}"
                        )
                        if not quiet:
                            print(
                                f"Tool '{tool_name}' returned an empty content list. Full response object: {response_object}"
                            )
                else:
                    logger.warning(
                        f"Tool '{tool_name}' did not return the expected content list structure. Full response object: {response_object}"
                    )
                    if not quiet:
                        print(
                            f"Tool '{tool_name}' did not return the expected content list structure. Full response object: {response_object}"
                        )

    except ConnectionRefusedError:
        logger.error(
            f"Connection to {server_url} refused. Ensure the server is running."
        )
        if not quiet:
            print(
                f"Error: Connection to {server_url} refused. Ensure the server is running."
            )
        sys.exit(1)  # Exit with error code
    except Exception as e:
        logger.error(f"An error occurred during client execution: {e}", exc_info=True)
        if not quiet:
            print(f"An unexpected error occurred: {e}")
        sys.exit(1)  # Exit with error code


def main() -> None:
    """Console script entry point for the MCP client."""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="MCP client to connect to a server and call a tool."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress print statements (logs WARNING and above).",
    )
    group.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging and print statements.",
    )
    args = parser.parse_args()

    # Configure logging based on CLI arguments.
    log_level = logging.INFO  # Default
    if args.quiet:
        log_level = logging.WARNING
    elif args.verbose:
        log_level = logging.DEBUG

    # Override with LOG_LEVEL env var if it's more specific (e.g. DEBUG when quiet is not set)
    # or if no CLI log level flag is set.
    env_log_level_str = os.getenv("LOG_LEVEL")
    if env_log_level_str:
        env_log_level = logging.getLevelName(env_log_level_str.upper())
        if isinstance(
            env_log_level, int
        ):  # Check if getLevelName returned a valid level
            # Let CLI flags take precedence if they are more restrictive (quiet) or more permissive (verbose)
            # than the environment variable.
            if args.quiet and env_log_level < logging.WARNING:
                pass  # quiet flag overrides env var to WARNING
            elif args.verbose and env_log_level > logging.DEBUG:
                pass  # verbose flag overrides env var to DEBUG
            else:
                log_level = env_log_level

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    asyncio.run(run_client(args.quiet, args.verbose))


if __name__ == "__main__":
    main()
