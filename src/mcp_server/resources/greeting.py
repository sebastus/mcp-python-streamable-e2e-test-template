from ..server_instance import server, logger

# Define a 'greeting' resource.
# This resource takes a 'name' from the URI (e.g., greeting://World)
# and returns a personalized greeting string.

# Retained as a sample

def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    logger.debug(f"Resource 'greeting://{name}' accessed")
    greeting = f"Hello, {name}!"
    logger.debug(f"Resource 'greeting://{name}' result: {greeting}")
    return greeting

