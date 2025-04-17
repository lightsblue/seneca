import pytest
import logging

def pytest_configure(config):
    """Set up pytest configuration."""
    # Add the integration marker
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )

@pytest.fixture(autouse=True)
def setup_logging(caplog):
    """Set up logging for all tests.
    
    This configuration prioritizes getting logs into the Cursor UI test results tab
    while still allowing viewing logs in terminal with -s flag.
    """
    # Set caplog to capture all logs at DEBUG level for Cursor UI
    caplog.set_level(logging.DEBUG)
    
    # Set the root logger level to DEBUG
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Configure specific loggers
    logging.getLogger("openai").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # Keep httpx quieter
    
    yield 