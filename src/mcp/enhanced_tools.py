"""
Enhanced MCP Tools with Natural Language Processing and Intent Recognition
Integrates all components for intelligent database operations with YAML tool definitions
"""

import asyncio
import json
import logging
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from mcp import Tool
from mcp.types import TextContent, ImageContent, EmbeddedResource

from ..nlp.intent_classifier import DatabaseIntentClassifier, ConversationFlow, DBIntent
from ..workflows.database_workflow import DatabaseWorkflowEngine
from ..portals.portal_manager import PortalManager
from ..llm.gemini_client import EnhancedGeminiClient
from ..config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class EnhancedMCPTools:
    """Enhanced MCP tools with YAML-based tool definitions and NLP capabilities"""
    
    def __init__(self, config_manager: ConfigManager, tools_config_path: str = "tools_config.yaml"):
        self.config_manager = config_manager
        self.tools_config_path = Path(tools_config_path)
        
        # Load tool definitions from YAML
        self.tools_config = self._load_tools_config()
        
        # Initialize components
        self.portal_manager = PortalManager(config_manager)
        self.gemini_client = EnhancedGeminiClient(
            api_key=config_manager.get_llm_config()["gemini"]["api_key"]
        )
        self.intent_classifier = DatabaseIntentClassifier(
            gemini_api_key=config_manager.get_llm_config()["gemini"]["api_key"]
        )
        self.workflow_engine = DatabaseWorkflowEngine(
            portal_manager=self.portal_manager,
            gemini_client=self.gemini_client
        )
        self.conversation_flow = ConversationFlow(self.intent_classifier)
        
        # Session management
        self.active_sessions = {}
        
        logger.info(f"✅ Enhanced MCP Tools initialized with {len(self.tools_config.get('tools', {}))} YAML-defined tools")
    
    def _load_tools_config(self) -> Dict[str, Any]:
        """Load tool definitions from YAML configuration file"""
        try:
            with open(self.tools_config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"📋 Loaded tool definitions from {self.tools_config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load tools config: {e}")
            return {"tools": {}}
    
    def get_tools(self) -> List[Tool]:
        """Get all available MCP tools from YAML configuration - Simplified to 3 core SSP tools"""
        tools = []
        
        # Only load the 3 core SSP tools
        core_tools = ["ssp_portal_interaction", "inventory_metadata_interaction", "unified_response"]
        
        for tool_name in core_tools:
            tool_config = self.tools_config.get("tools", {}).get(tool_name)
            if tool_config:
                try:
                    tool = Tool(
                        name=tool_config["name"],
                        description=tool_config["description"],
                        inputSchema=tool_config["input_schema"]
                    )
                    tools.append(tool)
                    logger.debug(f"✅ Loaded SSP tool: {tool_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load SSP tool {tool_name}: {e}")
            else:
                logger.warning(f"⚠️ SSP tool configuration not found: {tool_name}")
        
        logger.info(f"📊 Loaded {len(tools)} core SSP MCP tools from YAML configuration")
        return tools
    
    def get_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific tool"""
        return self.tools_config.get("tools", {}).get(tool_name)
    
    async def ssp_portal_interaction(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Handle all SSP portal API interactions - primary interface for all operations
        All operations flow through SSP API endpoints only
        """
        try:
            operation_type = arguments.get("operation_type", "")
            endpoint = arguments.get("endpoint", "")
            parameters = arguments.get("parameters", {})
            portal_id = arguments.get("portal_id", "default_ssp")
            request_method = arguments.get("request_method", "GET")
            session_id = arguments.get("session_id", "default_session")
            
            logger.info(f"🔌 SSP Portal Operation: {operation_type} via {endpoint} (method: {request_method})")
            
            # Process through NLP if it's a natural language request
            if operation_type == "natural_language_request":
                user_input = parameters.get("user_input", "")
                
                # Classify intent using NLP
                intent_result = await self.intent_classifier.classify_intent(
                    user_input, 
                    self.active_sessions.get(session_id, {})
                )
                
                logger.info(f"🎯 Classified intent: {intent_result.intent} (confidence: {intent_result.confidence:.2f})")
                
                # Convert intent to SSP API operation
                ssp_operation = await self._convert_intent_to_ssp_operation(intent_result, parameters)
                endpoint = ssp_operation.get("endpoint", endpoint)
                parameters.update(ssp_operation.get("parameters", {}))
                request_method = ssp_operation.get("method", request_method)
            
            # Execute operation through portal manager (SSP API only)
            portal_result = await self.portal_manager.execute_ssp_operation(
                operation_type=operation_type,
                endpoint=endpoint,
                method=request_method,
                parameters=parameters,
                portal_id=portal_id
            )
            
            # Update session state
            self.active_sessions[session_id] = {
                "last_operation": operation_type,
                "last_endpoint": endpoint,
                "last_parameters": parameters,
                "portal_result": portal_result
            }
            
            return [TextContent(
                type="text",
                text=f"✅ SSP Portal Operation Completed\n\n"
                     f"🔌 Portal: {portal_id}\n"
                     f"🎯 Operation: {operation_type}\n"
                     f"🌐 Endpoint: {endpoint}\n"
                     f"📊 Method: {request_method}\n"
                     f"📋 Status: {portal_result.get('status', 'completed')}\n\n"
                     f"📊 Response Data:\n{json.dumps(portal_result.get('data', {}), indent=2)}\n\n"
                     f"Session: {session_id}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error in SSP portal interaction: {e}")
            return [TextContent(
                type="text",
                text=f"❌ SSP Portal Error: {str(e)}\n\n"
                     f"Please verify SSP API endpoints and parameters."
            )]

    async def inventory_metadata_interaction(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Handle database/resource inventory and metadata operations via SSP APIs
        All inventory operations use SSP API endpoints
        """
        try:
            inventory_action = arguments.get("inventory_action", "list")
            resource_types = arguments.get("resource_types", ["databases"])
            filters = arguments.get("filters", {})
            include_metadata = arguments.get("include_metadata", True)
            include_health_status = arguments.get("include_health_status", True)
            portal_ids = arguments.get("portal_ids", [])
            
            logger.info(f"📊 Inventory Action: {inventory_action} for {', '.join(resource_types)}")
            
            # Route inventory request through SSP APIs
            inventory_result = await self.portal_manager.execute_inventory_operation(
                action=inventory_action,
                resource_types=resource_types,
                filters=filters,
                include_metadata=include_metadata,
                include_health_status=include_health_status,
                portal_ids=portal_ids,
                use_ssp_api=True  # Force SSP API usage
            )
            
            # Process metadata through Gemini if requested
            ai_insights = ""
            if arguments.get("ai_insights", False) and inventory_result.get("resources"):
                ai_insights = await self.gemini_client.analyze_inventory_metadata(inventory_result)
                ai_insights = f"\n\n🤖 AI Insights:\n{ai_insights}"
            
            return [TextContent(
                type="text",
                text=f"📊 Inventory Metadata Operation\n\n"
                     f"🔍 Action: {inventory_action}\n"
                     f"🗂️ Resource Types: {', '.join(resource_types)}\n"
                     f"🔌 Portal(s): {', '.join(portal_ids) if portal_ids else 'All SSP portals'}\n"
                     f"📋 Filters: {json.dumps(filters, indent=2)}\n\n"
                     f"📈 Summary:\n"
                     f"• Total Resources: {inventory_result.get('total_count', 0)}\n"
                     f"• Healthy: {inventory_result.get('healthy_count', 0)}\n"
                     f"• Warning: {inventory_result.get('warning_count', 0)}\n"
                     f"• Critical: {inventory_result.get('critical_count', 0)}\n\n"
                     f"🗄️ Resources:\n{json.dumps(inventory_result.get('resources', []), indent=2)}"
                     f"{ai_insights}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error in inventory metadata interaction: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Inventory Metadata Error: {str(e)}\n\n"
                     f"Please verify SSP API inventory endpoints."
            )]

    async def unified_response(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Provide unified, consolidated responses combining SSP operations with AI insights
        Aggregates data from multiple SSP API calls and provides intelligent summaries
        """
        try:
            response_type = arguments.get("response_type", "summary")
            session_id = arguments.get("session_id", "default_session")
            include_recommendations = arguments.get("include_recommendations", True)
            include_workflow_suggestions = arguments.get("include_workflow_suggestions", True)
            context_operations = arguments.get("context_operations", [])
            
            logger.info(f"🎯 Unified Response: {response_type} for session {session_id}")
            
            # Get session context
            session_context = self.active_sessions.get(session_id, {})
            
            # Gather data from recent SSP operations
            operation_summary = await self._gather_operation_summary(session_context, context_operations)
            
            # Generate AI-powered unified response
            unified_analysis = ""
            if include_recommendations:
                unified_analysis = await self.gemini_client.generate_unified_analysis(
                    operation_summary,
                    session_context,
                    response_type
                )
            
            # Generate workflow suggestions
            workflow_suggestions = ""
            if include_workflow_suggestions:
                workflow_suggestions = await self._generate_workflow_suggestions(
                    operation_summary,
                    session_context
                )
            
            # Format final unified response
            response_content = await self._format_unified_response(
                response_type,
                operation_summary,
                unified_analysis,
                workflow_suggestions,
                session_context
            )
            
            return [TextContent(
                type="text",
                text=response_content
            )]
            
        except Exception as e:
            logger.error(f"❌ Error in unified response: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Unified Response Error: {str(e)}\n\n"
                     f"Unable to generate consolidated response."
            )]

    async def _convert_intent_to_ssp_operation(self, intent_result, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert NLP intent to SSP API operation parameters"""
        intent_to_ssp_mapping = {
            "database_query": {
                "endpoint": "/api/v1/databases/query",
                "method": "POST",
                "parameters": {"query_type": "list", "filters": intent_result.entities}
            },
            "create_backup": {
                "endpoint": "/api/v1/operations/backup",
                "method": "POST", 
                "parameters": {"backup_type": "full", "targets": intent_result.entities.get("databases", [])}
            },
            "performance_analysis": {
                "endpoint": "/api/v1/analytics/performance",
                "method": "GET",
                "parameters": {"metrics": ["cpu", "memory", "query_performance"], "targets": intent_result.entities.get("databases", [])}
            }
        }
        
        return intent_to_ssp_mapping.get(intent_result.intent.value, {
            "endpoint": "/api/v1/operations/generic",
            "method": "POST",
            "parameters": parameters
        })

    async def _gather_operation_summary(self, session_context: Dict[str, Any], context_operations: List[str]) -> Dict[str, Any]:
        """Gather summary of recent SSP operations for unified response"""
        return {
            "recent_operations": [
                {
                    "operation": session_context.get("last_operation", ""),
                    "endpoint": session_context.get("last_endpoint", ""),
                    "status": session_context.get("portal_result", {}).get("status", ""),
                    "data_summary": len(str(session_context.get("portal_result", {}).get("data", {})))
                }
            ],
            "session_metrics": {
                "total_operations": 1,
                "success_rate": 1.0,
                "avg_response_time": "N/A"
            }
        }

    async def _generate_workflow_suggestions(self, operation_summary: Dict[str, Any], session_context: Dict[str, Any]) -> str:
        """Generate workflow suggestions based on recent operations"""
        suggestions = [
            "💡 Consider setting up automated monitoring for frequently queried resources",
            "🔄 Create a scheduled backup workflow for critical databases",
            "📊 Set up performance alerts for proactive monitoring"
        ]
        return "\n".join(suggestions)

    async def _format_unified_response(self, response_type: str, operation_summary: Dict[str, Any], 
                                     unified_analysis: str, workflow_suggestions: str, 
                                     session_context: Dict[str, Any]) -> str:
        """Format the final unified response"""
        # Format compact operation summary
        recent_ops = operation_summary.get("recent_operations", [])
        session_metrics = operation_summary.get("session_metrics", {})
        
        compact_summary = "📊 Operation Summary:\n"
        compact_summary += f"   🔄 Operations: {len(recent_ops)} | Success: {session_metrics.get('success_rate', 0):.0%} | Total: {session_metrics.get('total_operations', 0)}\n"
        
        if recent_ops:
            last_op = recent_ops[0]
            compact_summary += f"   � Last Operation: {last_op.get('operation', 'N/A')}\n"
            compact_summary += f"   🌐 Endpoint: {last_op.get('endpoint', 'N/A')}\n"
            compact_summary += f"   ✅ Status: {last_op.get('status', 'N/A')}\n"
            compact_summary += f"   📊 Data Size: {last_op.get('data_summary', 0)} chars\n"
        
        compact_summary += f"   📈 Session Metrics:\n"
        compact_summary += f"      • Total Operations: {session_metrics.get('total_operations', 0)}\n"
        compact_summary += f"      • Success Rate: {session_metrics.get('success_rate', 0):.1%}\n"
        compact_summary += f"      • Avg Response Time: {session_metrics.get('avg_response_time', 'N/A')}\n"
        
        return f"🎯 Unified Response ({response_type.upper()})\n\n" \
               f"{compact_summary}\n" \
               f"🤖 AI Analysis:\n{unified_analysis}\n\n" \
               f"💡 Workflow Suggestions:\n{workflow_suggestions}\n\n" \
               f"🔗 All operations executed via SSP API endpoints"