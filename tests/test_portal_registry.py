"""Tests for portal registry and base portal functionality."""

import pytest
from unittest.mock import AsyncMock

from mcp_well_server.portals.base_portal import (
    BasePortalClient, PortalRegistry, PortalError,
    PortalAuthenticationError, PortalConnectionError
)


class TestPortalClient(BasePortalClient):
    """Test implementation of BasePortalClient."""
    
    async def health_check(self):
        return {"status": "healthy", "portal": self.portal_name}
    
    async def get_capabilities(self):
        return ["test_operation", "health_check"]
    
    async def validate_operation(self, operation, parameters):
        return {"valid": True}
    
    async def execute_operation(self, operation, parameters):
        return {"result": "success", "operation": operation}
    
    async def get_operation_status(self, operation_id):
        return {"status": "completed", "operation_id": operation_id}


@pytest.mark.asyncio
class TestBasePortalClient:
    """Test BasePortalClient functionality."""
    
    async def test_client_initialization(self):
        """Test portal client initialization."""
        client = TestPortalClient(
            base_url="https://test.com",
            api_key="test_key",
            portal_name="test_portal"
        )
        
        assert client.base_url == "https://test.com"
        assert client.api_key == "test_key"
        assert client.portal_name == "test_portal"
        
        await client.close()
    
    async def test_health_check(self):
        """Test health check implementation."""
        client = TestPortalClient(
            base_url="https://test.com",
            api_key="test_key",
            portal_name="test_portal"
        )
        
        result = await client.health_check()
        assert result["status"] == "healthy"
        assert result["portal"] == "test_portal"
        
        await client.close()
    
    async def test_get_capabilities(self):
        """Test get capabilities implementation."""
        client = TestPortalClient(
            base_url="https://test.com",
            api_key="test_key",
            portal_name="test_portal"
        )
        
        capabilities = await client.get_capabilities()
        assert "test_operation" in capabilities
        assert "health_check" in capabilities
        
        await client.close()
    
    async def test_execute_operation(self):
        """Test operation execution."""
        client = TestPortalClient(
            base_url="https://test.com",
            api_key="test_key",
            portal_name="test_portal"
        )
        
        result = await client.execute_operation("test_operation", {"param": "value"})
        assert result["result"] == "success"
        assert result["operation"] == "test_operation"
        
        await client.close()


class TestPortalRegistry:
    """Test PortalRegistry functionality."""
    
    def test_registry_initialization(self, clean_portal_registry):
        """Test registry initialization."""
        registry = clean_portal_registry
        assert len(registry.list_portals()) == 0
    
    def test_register_portal(self, clean_portal_registry, mock_portal_client):
        """Test portal registration."""
        registry = clean_portal_registry
        
        registry.register_portal("test_portal", mock_portal_client)
        
        assert "test_portal" in registry.list_portals()
        assert registry.get_portal("test_portal") == mock_portal_client
    
    def test_register_portal_with_config(self, clean_portal_registry, mock_portal_client):
        """Test portal registration with configuration."""
        registry = clean_portal_registry
        config = {"key": "value"}
        
        registry.register_portal("test_portal", mock_portal_client, config)
        
        assert registry.get_portal_config("test_portal") == config
    
    def test_unregister_portal(self, clean_portal_registry, mock_portal_client):
        """Test portal unregistration."""
        registry = clean_portal_registry
        
        registry.register_portal("test_portal", mock_portal_client)
        assert "test_portal" in registry.list_portals()
        
        result = registry.unregister_portal("test_portal")
        assert result is True
        assert "test_portal" not in registry.list_portals()
    
    def test_unregister_nonexistent_portal(self, clean_portal_registry):
        """Test unregistering a non-existent portal."""
        registry = clean_portal_registry
        
        result = registry.unregister_portal("nonexistent")
        assert result is False
    
    def test_get_nonexistent_portal(self, clean_portal_registry):
        """Test getting a non-existent portal."""
        registry = clean_portal_registry
        
        portal = registry.get_portal("nonexistent")
        assert portal is None
    
    @pytest.mark.asyncio
    async def test_health_check_all(self, clean_portal_registry, mock_portal_client):
        """Test health check for all portals."""
        registry = clean_portal_registry
        
        # Register multiple portals
        registry.register_portal("portal1", mock_portal_client)
        
        portal2 = AsyncMock()
        portal2.health_check.return_value = {"status": "healthy"}
        registry.register_portal("portal2", portal2)
        
        # Test health check
        results = await registry.health_check_all()
        
        assert "portal1" in results
        assert "portal2" in results
        assert results["portal1"]["status"] == "healthy"
        assert results["portal2"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_with_error(self, clean_portal_registry):
        """Test health check with portal error."""
        registry = clean_portal_registry
        
        # Create a portal that raises an exception
        failing_portal = AsyncMock()
        failing_portal.health_check.side_effect = Exception("Connection failed")
        registry.register_portal("failing_portal", failing_portal)
        
        results = await registry.health_check_all()
        
        assert "failing_portal" in results
        assert results["failing_portal"]["status"] == "error"
        assert "Connection failed" in results["failing_portal"]["error"]
