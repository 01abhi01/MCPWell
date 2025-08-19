"""Test configuration and fixtures."""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock

from mcp_well_server.config import Settings
from mcp_well_server.portals.base_portal import BasePortalClient, portal_registry


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        gemini={"api_key": "test_key", "model": "gemini-pro"},
        apigee={"base_url": "https://test.apigee.com", "api_key": "test_key"},
        database_portal={"base_url": "https://test.db.com", "api_key": "test_key"},
        metadata_portal={"base_url": "https://test.meta.com", "api_key": "test_key"}
    )


@pytest.fixture
def mock_portal_client():
    """Create a mock portal client."""
    client = AsyncMock(spec=BasePortalClient)
    client.portal_name = "test_portal"
    client.base_url = "https://test.portal.com"
    client.health_check.return_value = {"status": "healthy"}
    client.get_capabilities.return_value = ["test_operation"]
    client.execute_operation.return_value = {"result": "success"}
    return client


@pytest.fixture
def clean_portal_registry():
    """Clean the portal registry before and after tests."""
    # Store original state
    original_portals = portal_registry._portals.copy()
    original_configs = portal_registry._portal_configs.copy()
    
    # Clear registry
    portal_registry._portals.clear()
    portal_registry._portal_configs.clear()
    
    yield portal_registry
    
    # Restore original state
    portal_registry._portals = original_portals
    portal_registry._portal_configs = original_configs


@pytest.fixture
def sample_workflow_state():
    """Create a sample workflow state."""
    return {
        "request_id": "test-123",
        "user_id": "user-456",
        "portal_name": "test_portal",
        "operation_type": "test_operation",
        "parameters": {"param1": "value1"},
        "context": {},
        "status": "pending",
        "current_step": "",
        "steps_completed": [],
        "results": {},
        "errors": [],
        "metadata": {}
    }


@pytest.fixture
def sample_database_metadata():
    """Create sample database metadata."""
    return {
        "database_name": "test_db",
        "version": "1.0",
        "schema": {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "int", "primary_key": True},
                        {"name": "name", "type": "varchar(100)"},
                        {"name": "email", "type": "varchar(255)"}
                    ]
                }
            ]
        },
        "configuration": {
            "max_connections": 100,
            "timeout": 30
        }
    }
