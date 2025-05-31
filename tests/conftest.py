"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import Generator
import os
import sys
from unittest.mock import AsyncMock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables before any imports."""
    # Set testing flag BEFORE any imports happen
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    os.environ["ASYNC_DATABASE_URL"] = "sqlite+aiosqlite:///test.db"
    os.environ["JWT_SECRET_KEY"] = "zJ_R2&;a$fjql@q3H7r!G{FJK&tK0[<y(!9zzFb@se6ADZJzY?Y;<t!py>Lc28=t"
    
    yield
    
    # Cleanup
    for key in ["TESTING", "DATABASE_URL", "ASYNC_DATABASE_URL"]:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_get_async_session():
    """Mock the get_async_session dependency for API tests."""
    with patch('infrastructure.db.database.get_async_session') as mock:
        mock_session = AsyncMock()
        mock.return_value = mock_session
        yield mock_session