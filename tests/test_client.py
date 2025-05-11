import logging
import os
from typing import Any, Callable, Dict, List, Optional

import pytest
from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client

# Configure logging for test execution.
# The log level can be set via the LOG_LEVEL environment variable (e.g., DEBUG, INFO).
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_add_tool_success(mcp_server_url: str) -> None:
    """
    Tests the successful invocation of the 'add' tool on the MCP server.

    Args:
        mcp_server_url: The URL of the MCP server, provided by a pytest fixture.
    """
    server_url: str = mcp_server_url  # Get server URL from the fixture
    tool_name: str = "add"
    arguments: Dict[str, Any] = {"a": 10, "b": 5}
    expected_result: int = 15

    logger.info(
        f"Attempting to connect to MCP server at {server_url} for testing '{tool_name}' tool..."
    )

    try:
        # Connect to the server using the streamable HTTP client.
        async with streamablehttp_client(server_url) as (
            test_read_stream,
            test_write_stream,
            test_get_session_id_callback,
        ):
            read_stream: Any = test_read_stream  # Type hint for the readable stream
            write_stream: Any = test_write_stream  # Type hint for the writable stream
            get_session_id_callback: Callable[[], Optional[str]] = (
                test_get_session_id_callback  # Callback for session ID
            )

            # Create a ClientSession.
            async with ClientSession(read_stream, write_stream) as client_session:
                session: ClientSession = client_session
                # Initialize the session.
                await session.initialize()
                session_id: Optional[str] = get_session_id_callback()
                logger.info(f"Test client connected. Session ID: {session_id}")

                logger.info(f"Calling tool '{tool_name}' with arguments: {arguments}")
                # Call the 'add' tool.
                response_object: types.CallToolResult = await session.call_tool(
                    tool_name, arguments
                )
                logger.info(
                    f"Raw response object from tool '{tool_name}': {response_object}"
                )

                # Assert that the tool call was not an error.
                assert (
                    not response_object.isError
                ), f"Tool call resulted in an error: {response_object.content}"
                # Assert that the response has a 'content' attribute.
                assert hasattr(
                    response_object, "content"
                ), "Response object should have a 'content' attribute"

                actual_content_list: List[types.Content] = response_object.content

                # Assert that the content is a list.
                assert isinstance(
                    actual_content_list, list
                ), f"Response content from tool '{tool_name}' should be a list, got {type(actual_content_list)}"
                # Assert that the content list is not empty.
                assert (
                    len(actual_content_list) > 0
                ), f"Response content list from tool '{tool_name}' should not be empty"

                first_content: types.Content = actual_content_list[0]
                # Assert that the first content item is TextContent.
                assert isinstance(
                    first_content, types.TextContent
                ), f"First content item should be TextContent, got {type(first_content)}"
                # Assert that the content type is 'text'.
                assert (
                    first_content.type == "text"
                ), f"Content type should be 'text', got '{first_content.type}'"

                try:
                    # Attempt to convert the result text to an integer.
                    result_value: int = int(first_content.text)
                    # Assert that the result matches the expected value.
                    assert (
                        result_value == expected_result
                    ), f"Result of {tool_name}({arguments['a']}, {arguments['b']}) was {result_value}, expected {expected_result}"
                    logger.info(
                        f"Tool '{tool_name}' returned expected result: {result_value}"
                    )
                except ValueError:
                    pytest.fail(
                        f"Could not convert result text '{first_content.text}' from tool '{tool_name}' to integer."
                    )

    except ConnectionRefusedError:
        logger.error(
            f"Connection to MCP server at {server_url} refused. Ensure the server is running for tests."
        )
        pytest.fail(
            f"Connection refused to MCP server at {server_url}. Is the server running for tests?"
        )
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during test execution for tool '{tool_name}': {e}",
            exc_info=True,
        )
        pytest.fail(
            f"Test for tool '{tool_name}' failed due to an unexpected error: {e}"
        )
