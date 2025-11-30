"""Pytest configuration and shared fixtures."""
from asyncio import get_event_loop_policy
from pytest import fixture


@fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
