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
        print(f"\n🧪 Tool Execution Demonstrations:")
        print("-" * 50)
        
        # Test 1: Natural Language Processing
        print("\n1. 🧠 Natural Language Processing:")
        nlp_result = await self.execute_tool("process_database_request", {
            "user_input": "Show me all production databases with performance issues",
            "session_id": "demo_session_1"
        })
        print(f"   Result: {nlp_result[0].text[:100]}..." if nlp_result and hasattr(nlp_result[0], 'text') else nlp_result)
        
        # Test 2: Workflow Orchestration
        print("\n2. 🔄 Workflow Orchestration:")
        workflow_result = await self.execute_tool("execute_multi_step_workflow", {
            "workflow_description": "backup production databases and analyze performance",
            "databases": ["users_db", "orders_db"],
            "dry_run": True
        })
        print(f"   Result: {workflow_result[0].text[:100]}..." if workflow_result and hasattr(workflow_result[0], 'text') else workflow_result)
        
        # Test 3: Database Inventory
        print("\n3. 📊 Database Inventory:")
        inventory_result = await self.execute_tool("get_database_inventory", {
            "environment_filter": "production",
            "ai_insights": True
        })
        print(f"   Result: {inventory_result[0].text[:100]}..." if inventory_result and hasattr(inventory_result[0], 'text') else inventory_result)
        
        # Test 4: Safety Confirmation
        print("\n4. 🛡️ Safety Confirmation:")
        safety_result = await self.execute_tool("confirm_operation", {
            "operation_type": "delete",
            "target_resources": ["temp_analytics_table"],
            "impact_assessment": {
                "risk_level": "medium",
                "affected_records": 50000,
                "rollback_available": False
            }
        })
        print(f"   Result: {safety_result[0].text[:100]}..." if safety_result and hasattr(safety_result[0], 'text') else safety_result)
        
        # Test 5: Performance Analysis
        print("\n5. ⚡ Performance Analysis:")
        perf_result = await self.execute_tool("analyze_database_performance", {
            "database_names": ["production_users", "production_orders"],
            "analysis_type": "comprehensive",
            "ai_recommendations": True
        })
        print(f"   Result: {perf_result[0].text[:100]}..." if perf_result and hasattr(perf_result[0], 'text') else perf_result)
        
        print(f"\n✅ YAML Tool Definitions Demo Completed Successfully!")
        print("=" * 70)
        
        # Show YAML configuration summary
        print(f"\n📋 YAML Configuration Summary:")
        tools_config = self.config_manager.get_tools_config()
        metadata = tools_config.get("metadata", {})
        print(f"   Name: {metadata.get('name', 'N/A')}")
        print(f"   Version: {metadata.get('version', 'N/A')}")
        print(f"   Description: {metadata.get('description', 'N/A')}")
        print(f"   Tools Defined: {len(tools_config.get('tools', {}))}")
        print(f"   Tool Categories: {len(tools_config.get('tool_settings', {}).get('categories', {}))}")

async def main():
    """Main function to demonstrate YAML tool definitions"""
    
    print("🔧 Enhanced Database MCP Server - YAML Tool Definitions")
    print("Demonstrates LangChain/LangGraph framework with YAML-based tool configuration")
    print()
    
    # Initialize server
    server = MCPServerWithYAMLTools()
    
    if await server.initialize():
        # Run demonstration
        await server.demonstrate_yaml_tools()
    else:
        print("❌ Failed to initialize MCP server")

if __name__ == "__main__":
    asyncio.run(main())
