"""
Enhanced Database MCP Server with YAML Tool Definitions
Demonstrates LangChain/LangGraph framework with YAML-based tool configuration
"""

import asyncio
import json
import logging
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import the original sophisticated components
from src.config.config_manager import ConfigManager
from src.mcp.enhanced_tools import EnhancedMCPTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPServerWithYAMLTools:
    """MCP Server with LangChain/LangGraph framework and YAML tool definitions"""
    
    def __init__(self, tools_config_file: str = "tools_config.yaml"):
        self.tools_config_file = tools_config_file
        self.config_manager = None
        self.enhanced_tools = None
        
    async def initialize(self):
        """Initialize the MCP server with YAML tool definitions"""
        try:
            # Initialize configuration manager
            self.config_manager = ConfigManager(self.tools_config_file)
            
            # Initialize enhanced tools with YAML configuration
            self.enhanced_tools = EnhancedMCPTools(
                config_manager=self.config_manager,
                tools_config_path=self.tools_config_file
            )
            
            # Initialize portal manager
            await self.enhanced_tools.portal_manager.initialize()
            
            logger.info("✅ MCP Server initialized with YAML tool definitions")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP server: {e}")
            return False
    
    def get_yaml_tools(self) -> List[Dict[str, Any]]:
        """Get tool definitions from YAML configuration"""
        tools_config = self.config_manager.get_tools_config()
        return list(tools_config.get("tools", {}).values())
    
    def get_mcp_tools(self):
        """Get MCP tools from enhanced tools"""
        return self.enhanced_tools.get_tools()
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Execute a tool by name with arguments"""
        try:
            # Get tool configuration
            tool_config = self.enhanced_tools.get_tool_config(tool_name)
            if not tool_config:
                return f"❌ Tool '{tool_name}' not found in YAML configuration"
            
            # Get implementation method
            implementation_method = tool_config.get("implementation_method", tool_name)
            
            # Execute the tool
            if hasattr(self.enhanced_tools, implementation_method):
                method = getattr(self.enhanced_tools, implementation_method)
                result = await method(arguments)
                return result
            else:
                return f"❌ Implementation method '{implementation_method}' not found"
                
        except Exception as e:
            logger.error(f"❌ Error executing tool {tool_name}: {e}")
            return f"❌ Tool execution failed: {str(e)}"
    
    async def demonstrate_yaml_tools(self):
        """Demonstrate all YAML-defined tools"""
        print("\n🚀 Enhanced Database MCP Server - YAML Tool Definitions Demo")
        print("=" * 70)
        
        # Show YAML tool definitions
        yaml_tools = self.get_yaml_tools()
        print(f"\n📋 YAML Tool Definitions Loaded: {len(yaml_tools)}")
        print("-" * 50)
        
        for tool in yaml_tools:
            print(f"• {tool['name']}: {tool['description'][:60]}...")
            print(f"  Category: {tool.get('category', 'N/A')}")
            print(f"  Requires Confirmation: {tool.get('requires_confirmation', False)}")
            print()
        
        # Show MCP tools converted from YAML
        mcp_tools = self.get_mcp_tools()
        print(f"📊 MCP Tools Generated from YAML: {len(mcp_tools)}")
        print("-" * 50)
        
        for tool in mcp_tools:
            print(f"• {tool.name}")
        
        # Demonstrate tool execution
        print(f"\n🧪 SSP Tool Execution Demonstrations:")
        print("-" * 50)
        
        # Test 1: SSP Portal Interaction - Natural Language
        print("\n1. 🔌 SSP Portal Interaction (Natural Language):")
        ssp_result = await self.execute_tool("ssp_portal_interaction", {
            "operation_type": "natural_language_request",
            "parameters": {
                "user_input": "Show me all production databases with performance issues"
            },
            "session_id": "demo_session_1"
        })
        print(f"   Result: {ssp_result[0].text[:100]}..." if ssp_result and hasattr(ssp_result[0], 'text') else ssp_result)
        
        # Test 2: SSP Portal Interaction - API Call
        print("\n2. � SSP Portal Interaction (API Call):")
        api_result = await self.execute_tool("ssp_portal_interaction", {
            "operation_type": "api_call",
            "endpoint": "/api/v1/databases/list",
            "request_method": "GET",
            "parameters": {
                "filters": {
                    "environment": "production"
                }
            }
        })
        print(f"   Result: {api_result[0].text[:100]}..." if api_result and hasattr(api_result[0], 'text') else api_result)
        
        # Test 3: Inventory Metadata Interaction
        print("\n3. 📊 Inventory Metadata Interaction:")
        inventory_result = await self.execute_tool("inventory_metadata_interaction", {
            "inventory_action": "list",
            "resource_types": ["databases"],
            "filters": {
                "environment": "production",
                "health_status": "critical"
            },
            "ai_insights": True
        })
        print(f"   Result: {inventory_result[0].text[:100]}..." if inventory_result and hasattr(inventory_result[0], 'text') else inventory_result)
        
        # Test 4: Unified Response - Analysis
        print("\n4. 🎯 Unified Response (Analysis):")
        unified_result = await self.execute_tool("unified_response", {
            "response_type": "analysis",
            "session_id": "demo_session_1",
            "include_recommendations": True,
            "aggregation_options": {
                "time_window": "session_only",
                "include_metrics": True
            }
        })
        print(f"   Result: {unified_result[0].text[:100]}..." if unified_result and hasattr(unified_result[0], 'text') else unified_result)
        
        # Test 5: Unified Response - Workflow Plan
        print("\n5. 🎯 Unified Response (Workflow Plan):")
        workflow_result = await self.execute_tool("unified_response", {
            "response_type": "workflow_plan",
            "context_operations": ["database_query", "performance_analysis"],
            "include_workflow_suggestions": True
        })
        print(f"   Result: {workflow_result[0].text[:100]}..." if workflow_result and hasattr(workflow_result[0], 'text') else workflow_result)
        
        print(f"\n✅ SSP Tool Definitions Demo Completed Successfully!")
        print("=" * 70)
        
        # Show SSP YAML configuration summary
        print(f"\n📋 SSP YAML Configuration Summary:")
        tools_config = self.config_manager.get_tools_config()
        metadata = tools_config.get("metadata", {})
        print(f"   Name: {metadata.get('name', 'N/A')}")
        print(f"   Version: {metadata.get('version', 'N/A')}")
        print(f"   Description: {metadata.get('description', 'N/A')}")
        print(f"   Architecture: {metadata.get('architecture', 'N/A')}")
        print(f"   SSP Tools Defined: {len(tools_config.get('tools', {}))}")
        print(f"   Tool Categories: {len(tools_config.get('tool_settings', {}).get('categories', {}))}")
        
        # SSP Architecture highlights
        integration = tools_config.get("integration", {})
        if integration.get("ssp_primary_mode"):
            print(f"\n🔌 SSP-First Architecture:")
            print(f"   - All operations via SSP API endpoints")
            print(f"   - LangChain/LangGraph integration: {integration.get('langgraph_workflows', False)}")
            print(f"   - Gemini LLM enhanced: {integration.get('gemini_llm', False)}")
            print(f"   - Portal manager active: {integration.get('portal_manager', False)}")

    async def cleanup(self):
        """Cleanup server resources"""
        try:
            if self.enhanced_tools and self.enhanced_tools.portal_manager:
                await self.enhanced_tools.portal_manager.cleanup()
            logger.info("✅ MCP Server cleanup completed")
        except Exception as e:
            logger.error(f"❌ MCP Server cleanup failed: {e}")

async def main():
    """Main function to demonstrate SSP YAML tool definitions"""
    
    print("🔧 Enhanced Database MCP Server - SSP YAML Tool Definitions")
    print("Demonstrates LangChain/LangGraph framework with SSP-first YAML-based tool configuration")
    print()
    
    # Initialize server
    server = MCPServerWithYAMLTools()
    
    try:
        if await server.initialize():
            # Run demonstration
            await server.demonstrate_yaml_tools()
        else:
            print("❌ Failed to initialize MCP server")
    finally:
        # Cleanup resources
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
