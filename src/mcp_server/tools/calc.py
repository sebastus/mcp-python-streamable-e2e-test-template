from ..server_instance import server, logger

# Define an 'add' tool.
# This tool takes two integers 'a' and 'b' and returns their sum.
def calc_add(a: int, b: int) -> int:
    """Add two numbers."""
    logger.debug(f"Tool 'add' called with a={a}, b={b}")
    result = a + b
    logger.debug(f"Tool 'add' result: {result}")
    return result

