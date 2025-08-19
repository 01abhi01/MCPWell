# Enhanced Database MCP Server - SSP-First Architecture

A sophisticated MCP (Model Context Protocol) server with a **simplified 3-tool SSP-first architecture**. All operations flow through **SSP API endpoints only**, providing unified database operations with advanced AI capabilities and streamlined tool management.

## 🚀 Key Features

### 🎯 **3-Tool SSP Architecture**
- **SSP Portal Interaction**: Primary tool for all SSP API operations including natural language processing
- **Inventory Metadata Interaction**: Database and resource inventory management via SSP APIs
- **Unified Response**: Consolidated response aggregation with AI-powered insights
- **All operations via SSP APIs**: Every operation flows through SSP endpoints exclusively

### 🤖 **Advanced AI Components**
- **Intent Classification**: AI-powered intent recognition with SSP endpoint mapping
- **Conversation Flow Management**: Multi-turn interactions with session tracking
- **Workflow Orchestration**: LangGraph state machines for complex SSP operations
- **Safety Validation**: AI-powered confirmation for destructive operations
- **Unified Analysis**: Cross-operation insights and performance optimization

### 🔌 **SSP-First Integration**
- **Pure SSP API Operations**: All database operations through SSP endpoints
- **Dynamic Endpoint Discovery**: Automatic SSP API capability detection
- **Health Monitoring**: SSP portal availability and performance monitoring
- **Authentication Support**: Bearer token, API key, OAuth2 for SSP portals

## 📁 Project Structure

```
MCP_Well/
├── tools_config.yaml           # 📋 3 SSP tools configuration
├── mcp_server.py              # 🔧 Main server with SSP-first architecture
├── src/                       # 🧠 SSP-focused implementation
│   ├── mcp/
│   │   └── enhanced_tools.py   # 3 core SSP tools only
│   ├── nlp/
│   │   └── intent_classifier.py # Intent→SSP endpoint mapping
│   ├── workflows/
│   │   └── database_workflow.py # SSP workflow orchestration
│   ├── llm/
│   │   └── gemini_client.py    # Enhanced Gemini with SSP analysis
│   ├── portals/
│   │   └── portal_manager.py   # SSP portal management
│   └── config/
│       └── config_manager.py   # SSP configuration management
├── requirements.txt           # Dependencies optimized for SSP operations
├── README.md                 # This documentation
├── .env.example              # SSP environment variables
└── .gitignore               # Git ignore rules
```

## 🛠️ **3 Core SSP Tools**

All tools are focused on SSP API operations with advanced AI capabilities:

### 1. 🔌 **ssp_portal_interaction**
- **Primary SSP Interface**: All database operations through SSP API endpoints
- **Natural Language Processing**: Convert user requests to SSP API calls
- **Intent→Endpoint Mapping**: Automatic mapping of user intents to SSP endpoints
- **Session Management**: Track SSP operations across conversation sessions
- **Operation Types**: `natural_language_request`, `api_call`, `workflow_execution`, `performance_analysis`, `backup_operation`, `query_execution`

### 2. 📊 **inventory_metadata_interaction**  
- **SSP Inventory Management**: Database and resource inventory via SSP APIs only
- **Metadata Operations**: `list`, `detail`, `search`, `health_check`, `metadata_fetch`, `schema_analyze`
- **Multi-Resource Support**: Databases, tables, schemas, indexes, views, procedures
- **AI Insights**: Optional Gemini-powered analysis of inventory data
- **Health Status Monitoring**: Real-time status via SSP health endpoints

### 3. 🎯 **unified_response**
- **Response Aggregation**: Consolidate multiple SSP operations into unified insights
- **AI-Powered Analysis**: Cross-operation patterns and optimization suggestions
- **Workflow Recommendations**: Suggest SSP workflow improvements based on usage patterns
- **Session Analytics**: Track and analyze SSP operation efficiency
- **Response Types**: `summary`, `detailed`, `analysis`, `recommendations`, `workflow_plan`

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure SSP Environment
```bash
cp .env.example .env
# Edit .env with your SSP portal URLs, API tokens, and Gemini API key
```

### 3. Configure SSP Endpoints
```bash
# Edit tools_config.yaml to match your SSP portal configuration
# Update base_url, authentication, and endpoint mappings
```

### 4. Run the SSP MCP Server
```bash
python mcp_server.py
```

### 5. See SSP Tools in Action
The server provides 3 tools that handle all operations through SSP API endpoints.

## 🔧 SSP Tool Configuration

### SSP Portal Integration
```yaml
integration:
  ssp_primary_mode: true
  ssp_endpoints:
    base_url: "${SSP_BASE_URL}"
    api_version: "v1"
    authentication:
      type: "bearer_token"
      token: "${SSP_API_TOKEN}"
    core_endpoints:
      databases: "/api/v1/databases"
      operations: "/api/v1/operations"
      analytics: "/api/v1/analytics"
      metadata: "/api/v1/metadata"
      health: "/api/v1/health"
```

### Tool Categories
- **ssp_operations**: Primary SSP portal operations and natural language processing
- **ssp_inventory**: Inventory and metadata operations via SSP APIs  
- **ssp_aggregation**: Unified response aggregation and AI insights

## 🧪 Example SSP Usage

### Natural Language to SSP API
````
```python
await server.execute_tool("process_database_request", {
    "user_input": "Show me all production databases with performance issues",
    "session_id": "user_session_123"
})
```

### Workflow Orchestration
```python
await server.execute_tool("execute_multi_step_workflow", {
    "workflow_description": "backup all critical databases and run performance analysis", 
    "databases": ["users", "orders", "products"],
    "dry_run": False
})
```

### AI-Powered Performance Analysis
```python
await server.execute_tool("analyze_database_performance", {
    "database_names": ["production_users", "production_orders"],
    "analysis_type": "predictive",
    "ai_recommendations": True
})
```

## 🤖 AI Capabilities

### Intent Classification
- **Hybrid Approach**: Rule-based patterns + LLM classification
- **Confidence Scoring**: Automatic confidence assessment
- **Context Awareness**: Previous conversation context considered
- **Clarification Handling**: Automatic clarification for low confidence

### Conversation Management
- **LangChain Memory**: ConversationBufferWindowMemory for context
- **Session Management**: Multi-user session isolation
- **Flow Control**: State-based conversation management
- **Confirmation Workflows**: Interactive confirmation for destructive operations

### Workflow Orchestration
- **LangGraph Integration**: State machine-based execution
- **Dependency Resolution**: Automatic step ordering
- **Error Recovery**: Rollback and retry capabilities
- **Parallel Execution**: Concurrent operation support

## 🔒 Security & Safety

### AI-Powered Safety
- **Risk Assessment**: Automatic operation risk evaluation
- **Confirmation Requirements**: Required for destructive operations
- **Impact Analysis**: Affected resources and rollback availability
- **Safety Validation**: Gemini-powered safety assessment

### Security Features
- **Authentication**: Multiple methods supported
- **Audit Logging**: Comprehensive operation tracking
- **Rate Limiting**: Protection against excessive requests
- **Session Management**: Secure session isolation

## 📊 Monitoring

- **Tool Usage Analytics**: Track tool execution patterns
- **Performance Metrics**: Response times and success rates
- **Portal Health**: Continuous portal availability monitoring
- **Error Tracking**: Comprehensive error logging and alerting

## 🚀 Benefits of YAML Tool Definitions

### ✅ **Advantages**
1. **Easy Tool Management**: Add/modify tools without touching Python code
2. **Configuration Validation**: YAML schema validation for tool definitions
3. **Documentation**: Self-documenting tool configurations with examples
4. **Version Control**: Easy to track tool changes in git
5. **Environment-Specific**: Different tool configs for different environments

### 🔧 **Full AI Framework Preserved**
- Complete LangChain/LangGraph implementation
- Advanced Gemini LLM integration
- Sophisticated intent classification
- Multi-turn conversation management
- Workflow orchestration capabilities
- Portal integration framework

## 🤝 Contributing

1. **Add New Tools**: Edit `tools_config.yaml` and implement methods
2. **Enhance AI Features**: Modify LangChain/LangGraph components
3. **Portal Integration**: Add new portal types and capabilities
4. **Documentation**: Update YAML examples and usage guides

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **YAML Configuration**: Check `tools_config.yaml` for examples
- **AI Components**: Review LangChain/LangGraph implementations in `src/`
- **Tool Development**: See `EnhancedMCPTools` class for implementation patterns
- **Testing**: Run demo mode with `python mcp_server.py`

---

**Enhanced Database MCP Server** - Combining AI-powered intelligence with YAML-driven simplicity for database operations and multi-portal integration.
