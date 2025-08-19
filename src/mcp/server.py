"""
Enhanced MCP Server with AI-Powered Database Operations
Integrates LangGraph workflows, intent classification, and Gemini LLM
"""

import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, ImageContent, EmbeddedResource

from .enhanced_tools import EnhancedMCPTools
from ..config.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMCPServer:
    """Enhanced MCP Server for database operations with AI capabilities"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.enhanced_tools = EnhancedMCPTools(self.config_manager)
        
        # Initialize FastMCP server
        self.mcp = FastMCP("Database Operations MCP Server")
        
        # Register enhanced tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all enhanced tools with the MCP server"""
        
        # Get tools from enhanced tools manager
        tools = self.enhanced_tools.get_tools()
        
        # Register each tool
        for tool in tools:
            if tool.name == "process_database_request":
                self.mcp.add_tool(tool)(self.enhanced_tools.process_database_request)
            elif tool.name == "confirm_operation":
                self.mcp.add_tool(tool)(self.enhanced_tools.confirm_operation)
            elif tool.name == "get_available_databases":
                self.mcp.add_tool(tool)(self.enhanced_tools.get_available_databases)
            elif tool.name == "analyze_database_performance":
                self.mcp.add_tool(tool)(self.enhanced_tools.analyze_database_performance)
            elif tool.name == "get_compliance_report":
                self.mcp.add_tool(tool)(self.enhanced_tools.get_compliance_report)
            elif tool.name == "execute_multi_step_workflow":
                self.mcp.add_tool(tool)(self.enhanced_tools.execute_multi_step_workflow)
            elif tool.name == "get_conversation_history":
                self.mcp.add_tool(tool)(self.enhanced_tools.get_conversation_history)
            elif tool.name == "explain_database_concept":
                self.mcp.add_tool(tool)(self.enhanced_tools.explain_database_concept)
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Enhanced Database MCP Server...")
        
        # Initialize components
        await self.enhanced_tools.portal_manager.initialize()
        
        logger.info("Enhanced Database MCP Server started successfully")
        logger.info("Available AI-powered capabilities:")
        logger.info("  - Natural language database operation requests")
        logger.info("  - Intelligent intent classification")
        logger.info("  - Multi-step workflow orchestration")
        logger.info("  - AI-powered compliance analysis")
        logger.info("  - Performance analysis with insights")
        logger.info("  - Conversational database management")
        
        # Run the MCP server
        await self.mcp.run()

def main():
    """Main entry point"""
    try:
        server = DatabaseMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()
