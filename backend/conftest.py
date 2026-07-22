import asyncio
import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Share a single event loop across all tests for Motor client compatibility."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
