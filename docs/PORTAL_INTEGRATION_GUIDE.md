# Adding New Self-Service Portals to MCP

This guide explains how to integrate any self-service portal with the Enhanced Database MCP Server. The system is designed to automatically discover capabilities and extend functionality with minimal configuration.

## 🚀 Quick Start: Adding a New Portal

### 1. Create Portal Configuration

Create a YAML configuration file in `config/portals/your_portal.yaml`:

```yaml
# Example: Monitoring Portal Configuration
name: "Application Monitoring Portal"
base_url: "${APIGEE_BASE_URL}/monitoring/v1"
authentication:
  type: "api_key"
  header: "X-Monitor-Key"
  api_key: "${MONITORING_PORTAL_API_KEY}"

capabilities:
  - "performance_monitoring"
  - "alerting"
  - "log_analytics"
  - "cost_optimization"

metadata:
  portal_type: "monitoring"
  supported_metrics: ["cpu", "memory", "disk", "network"]
  alert_channels: ["email", "slack", "webhook"]
  
health_check_endpoint: "/health"

endpoints:
  get_metrics:
    path: "/metrics/{resource_id}"
    method: "GET"
    parameters:
      - name: "resource_id"
        type: "path"
        required: true
      - name: "time_range"
        type: "query"
        required: false

  create_alert:
    path: "/alerts"
    method: "POST"
    requires_confirmation: false
    parameters:
      - name: "metric"
        type: "body"
        required: true
      - name: "threshold"
        type: "body"
        required: true
      - name: "notification_channel"
        type: "body"
        required: true
```

### 2. Set Environment Variables

Add the necessary environment variables to your `.env` file:

```env
# Monitoring Portal
MONITORING_PORTAL_API_KEY=your_monitoring_api_key_here
```

### 3. Restart the MCP Server

The portal will be automatically discovered and integrated when the server starts.

## 🔧 Configuration Reference

### Authentication Types

The system supports multiple authentication methods:

#### API Key Authentication
```yaml
authentication:
  type: "api_key"
  header: "X-API-Key"  # or "Authorization"
  api_key: "${YOUR_API_KEY}"
  prefix: ""  # Optional prefix like "Bearer"
```

#### Bearer Token Authentication
```yaml
authentication:
  type: "bearer_token"
  header: "Authorization"
  token: "${YOUR_BEARER_TOKEN}"
```

#### Basic Authentication
```yaml
authentication:
  type: "basic_auth"
  header: "Authorization"
  username: "${YOUR_USERNAME}"
  password: "${YOUR_PASSWORD}"
```

#### Custom Headers
```yaml
authentication:
  type: "custom"
  custom_headers:
    "X-Custom-Auth": "${CUSTOM_TOKEN}"
    "X-Client-ID": "${CLIENT_ID}"
```

### Endpoint Configuration

Each endpoint supports various configuration options:

```yaml
endpoints:
  endpoint_name:
    path: "/api/resource/{id}"  # Path with parameters
    method: "POST"              # HTTP method
    requires_confirmation: true # User confirmation needed
    safety_check: true         # AI safety validation
    timeout: 30                # Request timeout (seconds)
    retry_count: 3            # Number of retries
    parameters:
      - name: "id"
        type: "path"           # path, query, or body
        required: true
      - name: "filter"
        type: "query"
        required: false
      - name: "data"
        type: "body"
        required: true
```

## 🤖 Automatic Capability Discovery

The system automatically discovers portal capabilities by analyzing:

1. **Explicit Capabilities**: Listed in the `capabilities` field
2. **Endpoint Names**: Inferred from endpoint naming patterns
3. **Endpoint Paths**: Analyzed for common patterns

### Supported Capability Categories

#### Database Operations
- `database_backup` - Database backup operations
- `database_restore` - Database restore operations  
- `database_compliance` - Compliance checking
- `database_patching` - Patch management
- `database_monitoring` - Performance monitoring

#### Infrastructure Operations
- `vm_management` - Virtual machine management
- `container_orchestration` - Container deployment/scaling
- `network_management` - Network configuration
- `storage_management` - Storage provisioning
- `load_balancer_management` - Load balancer management

#### Security Operations
- `vulnerability_scanning` - Security vulnerability scans
- `compliance_auditing` - Security compliance audits
- `access_control_management` - Access control management
- `certificate_management` - SSL/TLS certificate management
- `threat_detection` - Threat detection and analysis

#### DevOps Operations
- `pipeline_management` - CI/CD pipeline management
- `deployment_orchestration` - Application deployment
- `release_management` - Release coordination
- `artifact_management` - Build artifact management

#### Monitoring & Analytics
- `performance_monitoring` - Performance metrics
- `log_analytics` - Log analysis
- `cost_optimization` - Cost analysis and optimization
- `alerting` - Alert management

## 🎯 Natural Language Pattern Generation

For each discovered capability, the system automatically generates natural language patterns:

### Example Generated Patterns

If your portal has a `create_vm` endpoint, the system generates patterns like:
- "create vm in {portal_name}"
- "provision virtual machine"
- "start new instance"

### Custom Pattern Addition

You can add custom patterns by extending the portal integration framework:

```python
# In your custom integration code
integration_framework = PortalIntegrationFramework(portal_manager)

# Add custom patterns for specific domain terminology
custom_patterns = {
    "your_portal_vm_management_create_vm": [
        r"spin up.*server",
        r"provision.*box",
        r"create.*compute.*instance"
    ]
}

integration_framework.dynamic_intents.update(custom_patterns)
```

## 🔄 Workflow Integration

The system automatically creates workflow steps for each portal endpoint and intelligently infers dependencies:

### Automatic Dependency Inference

- **Create operations** depend on list operations (e.g., `create_vm` depends on `list_vms`)
- **Restore operations** depend on backup status (e.g., `restore_database` depends on `get_backup_status`)
- **Update operations** depend on current state queries

### Custom Workflow Steps

For complex workflows, you can define custom steps:

```python
custom_workflow_steps = {
    "complex_deployment": WorkflowStep(
        name="complex_deployment",
        description="Multi-step application deployment",
        portal="devops_portal",
        endpoint="deploy_application",
        requires_confirmation=True,
        dependencies=["validate_environment", "create_backup", "run_tests"]
    )
}
```

## 🔒 Safety and Confirmation

### Automatic Safety Detection

The system automatically identifies potentially destructive operations and applies safety measures:

- **Destructive Keywords**: delete, remove, terminate, destroy
- **State-Changing Keywords**: create, update, modify, deploy
- **Critical Keywords**: production, prod, live

### Manual Safety Configuration

Override automatic detection in your portal configuration:

```yaml
endpoints:
  critical_operation:
    path: "/critical/{resource}"
    method: "DELETE"
    requires_confirmation: true    # Force user confirmation
    safety_check: true           # Enable AI safety validation
    parameters:
      - name: "resource"
        type: "path"
        required: true
```

## 📊 Real-World Examples

### Example 1: Content Management Portal

```yaml
name: "Content Management Portal"
base_url: "${APIGEE_BASE_URL}/cms/v1"
authentication:
  type: "bearer_token"
  token: "${CMS_PORTAL_TOKEN}"

capabilities:
  - "content_management"
  - "publishing_workflow"
  - "media_management"

endpoints:
  publish_content:
    path: "/content/{content_id}/publish"
    method: "POST"
    requires_confirmation: true
    parameters:
      - name: "content_id"
        type: "path"
        required: true
      - name: "environment"
        type: "body"
        required: true

  upload_media:
    path: "/media/upload"
    method: "POST"
    parameters:
      - name: "file_type"
        type: "body"
        required: true
```

**Generated Natural Language Patterns:**
- "publish content to production"
- "upload media file"
- "manage content in CMS portal"

### Example 2: Network Operations Portal

```yaml
name: "Network Operations Portal"
base_url: "${APIGEE_BASE_URL}/network/v1"
authentication:
  type: "api_key"
  header: "X-Network-Key"
  api_key: "${NETWORK_PORTAL_API_KEY}"

capabilities:
  - "network_configuration"
  - "firewall_management"
  - "traffic_analysis"

endpoints:
  create_firewall_rule:
    path: "/firewall/rules"
    method: "POST"
    requires_confirmation: true
    safety_check: true
    parameters:
      - name: "source_ip"
        type: "body"
        required: true
      - name: "destination_port"
        type: "body"
        required: true
      - name: "action"
        type: "body"
        required: true

  analyze_traffic:
    path: "/traffic/analyze"
    method: "GET"
    parameters:
      - name: "time_range"
        type: "query"
        required: false
```

**Generated Natural Language Patterns:**
- "create firewall rule for network portal"
- "analyze network traffic"
- "configure network settings"

## 🧪 Testing New Portal Integration

### 1. Validation Script

Create a test script to validate your portal integration:

```python
import asyncio
from src.portals.portal_manager import PortalManager
from src.integration.portal_integration_framework import PortalIntegrationFramework
from src.config.config_manager import ConfigManager

async def test_portal_integration():
    config_manager = ConfigManager()
    portal_manager = PortalManager(config_manager)
    integration_framework = PortalIntegrationFramework(portal_manager)
    
    # Initialize and test
    await portal_manager.initialize()
    
    # Test portal health
    is_healthy = await portal_manager.check_portal_health("your_portal_name")
    print(f"Portal health: {is_healthy}")
    
    # Register integration
    result = await integration_framework.register_portal_integration("your_portal_name")
    print(f"Integration result: {result}")
    
    # Generate integration guide
    guide = integration_framework.generate_portal_integration_guide("your_portal_name")
    print(guide)

if __name__ == "__main__":
    asyncio.run(test_portal_integration())
```

### 2. Natural Language Testing

Test the generated natural language patterns:

```python
from src.mcp.enhanced_tools import EnhancedMCPTools

async def test_natural_language():
    enhanced_tools = EnhancedMCPTools(config_manager)
    
    test_queries = [
        "create vm in your_portal_name",
        "show metrics from monitoring portal",
        "publish content to production",
        "analyze network traffic for the last hour"
    ]
    
    for query in test_queries:
        result = await enhanced_tools.process_database_request({
            "user_input": query,
            "session_id": "test_session"
        })
        print(f"Query: {query}")
        print(f"Result: {result[0].text if result else 'No result'}")
        print("-" * 50)
```

## 🚨 Troubleshooting

### Common Issues

1. **Portal Not Discovered**
   - Check YAML syntax in configuration file
   - Verify environment variables are set
   - Ensure health check endpoint is accessible

2. **Authentication Failures**
   - Validate API keys/tokens
   - Check authentication header format
   - Verify token permissions

3. **Natural Language Not Working**
   - Check that capabilities are properly detected
   - Add explicit patterns for domain-specific terminology
   - Verify intent classifier is updated

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger("src.portals").setLevel(logging.DEBUG)
logging.getLogger("src.integration").setLevel(logging.DEBUG)
```

## 🔄 Runtime Portal Registration

You can also register portals dynamically at runtime:

```python
# Dynamic portal registration
portal_config = {
    "name": "Runtime Portal",
    "base_url": "https://api.example.com/v1",
    "authentication": {
        "type": "api_key",
        "header": "X-API-Key",
        "api_key": "your-key-here"
    },
    "endpoints": {
        "get_data": {
            "path": "/data",
            "method": "GET"
        }
    }
}

success = await portal_manager.register_portal("runtime_portal", portal_config)
if success:
    await integration_framework.register_portal_integration("runtime_portal")
```

## 📈 Best Practices

1. **Portal Naming**: Use descriptive, consistent naming conventions
2. **Capability Mapping**: Explicitly define capabilities for better pattern generation
3. **Safety Configuration**: Always configure safety checks for destructive operations
4. **Health Checks**: Implement proper health check endpoints
5. **Error Handling**: Provide meaningful error responses from your portal APIs
6. **Documentation**: Include metadata about supported operations and parameters
7. **Testing**: Thoroughly test both API connectivity and natural language patterns

## 🎯 Advanced Customization

For advanced use cases, you can extend the integration framework:

```python
class CustomPortalIntegration(PortalIntegrationFramework):
    def __init__(self, portal_manager):
        super().__init__(portal_manager)
        # Add custom capability patterns
        self.capability_patterns.update({
            CustomCapability.CUSTOM_OPERATION: [
                r"custom.*operation",
                r"special.*task"
            ]
        })
    
    async def custom_capability_discovery(self, portal_config):
        # Custom logic for capability discovery
        pass
```

This extensible architecture ensures that any self-service portal can be integrated with minimal effort while providing powerful AI-driven natural language interfaces and intelligent workflow orchestration.
