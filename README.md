# Enhanced Database MCP Server - YAML Tool Definitions

A sophisticated MCP (Model Context Protocol) server that combines the power of **LangChain/LangGraph AI frameworks** with **YAML-based tool definitions**. This approach provides the best of both worlds: advanced AI capabilities with simplified configuration management.

## 🚀 Key Features

### 🎯 **YAML Tool Definitions + LangChain Framework**
- **Tool definitions in YAML**: All 8 MCP tools defined in `tools_config.yaml` for easy management
- **LangChain/LangGraph implementation**: Full AI-powered workflow orchestration and intent classification
- **Sophisticated AI capabilities**: Gemini LLM integration, conversation management, safety validation
- **No code changes for new tools**: Add tools by editing YAML configuration only

### 🤖 **Advanced AI Components**
- **Intent Classification**: Hybrid rule-based + LLM-powered intent recognition (13 intent types)
- **Conversation Flow Management**: Multi-turn interactions with LangChain memory
- **Workflow Orchestration**: LangGraph state machines for complex operations
- **Safety Validation**: AI-powered confirmation for destructive operations
- **Performance Analysis**: Predictive insights and optimization recommendations

### 🔌 **Multi-Portal Integration**
- **Dynamic Portal Registration**: Add new portals without code changes
- **Health Monitoring**: Automatic portal availability monitoring
- **Capability Discovery**: AI-driven portal integration with automatic intent generation
- **Authentication Support**: Multiple auth methods (API key, OAuth2, Bearer token, mTLS)

## 📁 Project Structure

```
MCP_Well/
├── tools_config.yaml           # 📋 YAML tool definitions (NEW!)
├── mcp_server.py              # 🔧 Main server with YAML tool loading
├── src/                       # 🧠 Full LangChain/LangGraph implementation
│   ├── mcp/
│   │   └── enhanced_tools.py   # MCP tools with YAML configuration support
│   ├── nlp/
│   │   └── intent_classifier.py # AI-powered intent classification
│   ├── workflows/
│   │   └── database_workflow.py # LangGraph workflow orchestration
│   ├── llm/
│   │   └── gemini_client.py    # Enhanced Gemini LLM integration
│   ├── portals/
│   │   └── portal_manager.py   # Multi-portal management
│   └── config/
│       └── config_manager.py   # Configuration with YAML support
├── requirements.txt           # Full dependencies (LangChain, LangGraph, etc.)
├── README.md                 # This documentation
├── .env.example              # Environment variables
└── .gitignore               # Git ignore rules
```

## 🛠️ **8 MCP Tools Defined in YAML**

All tools are defined in `tools_config.yaml` but implemented with full LangChain/LangGraph capabilities:

### 1. 🧠 **process_database_request**
- **Natural Language Processing**: AI-powered intent classification
- **Conversation Management**: Multi-turn interactions with context
- **13 Intent Types**: CREATE, READ, UPDATE, DELETE, BACKUP, RESTORE, ANALYZE, OPTIMIZE, MONITOR, TROUBLESHOOT, COMPLIANCE, MIGRATION, ADMINISTRATION

### 2. 🔄 **execute_multi_step_workflow**  
- **LangGraph Orchestration**: State machine-based workflow execution
- **Dependency Management**: Automatic step dependency resolution
- **Error Recovery**: Intelligent rollback and error handling

### 3. 📊 **get_database_inventory**
- **Multi-Portal Data**: Aggregated inventory from all portals
- **AI Insights**: Gemini-powered analysis and recommendations
- **Health Monitoring**: Real-time status and alerts

### 4. 🛡️ **confirm_operation**
- **AI Safety Validation**: Risk assessment for destructive operations
- **Interactive Confirmation**: Context-aware confirmation workflows
- **Impact Assessment**: Automatic risk level calculation

### 5. ⚡ **analyze_database_performance**
- **Predictive Analysis**: AI-powered performance insights
- **Multi-Metric Collection**: CPU, memory, query performance, connections
- **Optimization Recommendations**: Gemini-generated suggestions

### 6. 🔌 **manage_portal_integration**
- **Dynamic Registration**: Add portals without code changes
- **Capability Discovery**: Automatic portal integration
- **Health Monitoring**: Continuous availability checks

### 7. 📋 **get_compliance_report**
- **Multi-Framework Support**: SOX, GDPR, HIPAA, PCI DSS, SOC2, ISO27001
- **Cross-Portal Auditing**: Compliance across all integrated portals
- **AI Risk Assessment**: Automated compliance risk analysis

### 8. 💬 **orchestrate_conversation_flow**
- **LangChain Memory**: Conversation buffer with context management
- **State Management**: Track pending operations and user intent
- **Clarification Handling**: Automatic clarification for ambiguous requests

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Gemini API key and portal credentials
```

### 3. Run the MCP Server
```bash
python mcp_server.py
```

### 4. See YAML Tools in Action
The server demonstrates all 8 tools loaded from YAML configuration with full AI capabilities.

## 🔧 YAML Tool Configuration

### Tool Definition Structure
```yaml
tools:
  your_tool_name:
    name: "your_tool_name"
    description: "Tool description"
    category: "tool_category" 
    requires_confirmation: false
    implementation_class: "EnhancedMCPTools"
    implementation_method: "your_method_name"
    input_schema:
      type: "object"
      properties:
        parameter_name:
          type: "string"
          description: "Parameter description"
      required: ["parameter_name"]
    examples:
      - input: "example input"
        description: "What this example demonstrates"
```

### Adding a New Tool

1. **Edit `tools_config.yaml`** - Add your tool definition
2. **Implement Method** - Add method to `EnhancedMCPTools` class
3. **Test** - Run `python mcp_server.py` to see your tool in action

No other code changes required!

## 🧪 Example Usage

### Natural Language Processing
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
