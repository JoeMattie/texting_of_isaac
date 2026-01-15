"""Pytest configuration and fixtures."""
import pytest
import esper


@pytest.fixture(autouse=True)
def cleanup_esper_worlds():
    """Clean up esper worlds between tests to prevent state leakage.

    This fixture runs automatically before each test to ensure
    esper's global state is cleaned up properly.
    """
    # Clean up before test
    esper._processors.clear()
    esper._components.clear()
    esper._entities.clear()
    esper._dead_entities.clear()

    yield

    # Clean up after test
    esper._processors.clear()
    esper._components.clear()
    esper._entities.clear()
    esper._dead_entities.clear()
