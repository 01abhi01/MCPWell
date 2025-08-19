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
        """Get all available MCP tools from YAML configuration"""
        tools = []
        
        for tool_name, tool_config in self.tools_config.get("tools", {}).items():
            try:
                tool = Tool(
                    name=tool_config["name"],
                    description=tool_config["description"],
                    inputSchema=tool_config["input_schema"]
                )
                tools.append(tool)
                logger.debug(f"✅ Loaded tool: {tool_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load tool {tool_name}: {e}")
        
        logger.info(f"📊 Loaded {len(tools)} MCP tools from YAML configuration")
        return tools
    
    def get_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific tool"""
        return self.tools_config.get("tools", {}).get(tool_name)
    
    async def process_database_request(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Process natural language requests for database operations using AI-powered intent recognition
        Tool definition loaded from YAML configuration
        """
        try:
            user_input = arguments.get("user_input", "")
            session_id = arguments.get("session_id", "default_session")
            context = arguments.get("context", {})
            
            logger.info(f"🧠 Processing database request: '{user_input[:50]}...' for session {session_id}")
            
            # Get conversation context
            conversation_context = self.active_sessions.get(session_id, {})
            
            # Classify intent using NLP
            intent_result = await self.intent_classifier.classify_intent(
                user_input, 
                conversation_context
            )
            
            logger.info(f"🎯 Classified intent: {intent_result.intent} (confidence: {intent_result.confidence:.2f})")
            
            # Update conversation flow
            flow_response = await self.conversation_flow.process_turn(
                session_id, 
                user_input, 
                intent_result
            )
            
            # Check if clarification is needed
            if intent_result.confidence < 0.7 and intent_result.intent != DBIntent.UNKNOWN:
                clarification_response = await self.gemini_client.generate_clarification(
                    user_input, 
                    intent_result.intent.value,
                    intent_result.confidence
                )
                
                return [TextContent(
                    type="text",
                    text=f"🤔 I need clarification for your request: '{user_input}'\n\n"
                         f"Intent detected: {intent_result.intent.value} (confidence: {intent_result.confidence:.1%})\n\n"
                         f"💡 {clarification_response}\n\n"
                         f"Please provide more details or confirm if this is what you meant."
                )]
            
            # Process the request based on intent
            if intent_result.requires_confirmation:
                confirmation_data = {
                    "operation_type": intent_result.intent.value,
                    "target_resources": intent_result.entities.get("databases", []),
                    "impact_assessment": {
                        "risk_level": "medium",
                        "affected_records": 0,
                        "rollback_available": True
                    },
                    "user_confirmation": False
                }
                
                confirmation_result = await self.confirm_operation(confirmation_data)
                
                if not confirmation_result[0].text.startswith("✅"):
                    return confirmation_result
            
            # Execute the operation through portal manager
            portal_result = await self.portal_manager.execute_operation(
                intent_result.intent.value,
                intent_result.entities,
                context
            )
            
            # Update session state
            self.active_sessions[session_id] = {
                "last_intent": intent_result.intent.value,
                "last_entities": intent_result.entities,
                "conversation_history": flow_response.get("context", {}).get("history", [])
            }
            
            return [TextContent(
                type="text",
                text=f"✅ Database Request Processed Successfully\n\n"
                     f"🎯 Intent: {intent_result.intent.value}\n"
                     f"🔍 Entities: {json.dumps(intent_result.entities, indent=2)}\n"
                     f"📊 Portal Result: {portal_result.get('status', 'completed')}\n\n"
                     f"💡 AI Analysis: {intent_result.explanation}\n\n"
                     f"Session: {session_id}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error processing database request: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error processing request: {str(e)}\n\n"
                     f"Please try rephrasing your request or contact support if the issue persists."
            )]
    
    async def execute_multi_step_workflow(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Execute complex multi-step database workflows with LangGraph orchestration
        Tool definition loaded from YAML configuration
        """
        try:
            workflow_description = arguments.get("workflow_description", "")
            databases = arguments.get("databases", [])
            dry_run = arguments.get("dry_run", True)
            workflow_options = arguments.get("workflow_options", {})
            
            logger.info(f"🔄 Executing workflow: '{workflow_description}' (dry_run: {dry_run})")
            
            # Initialize workflow engine
            workflow_result = await self.workflow_engine.execute_workflow(
                description=workflow_description,
                target_databases=databases,
                dry_run=dry_run,
                options=workflow_options
            )
            
            return [TextContent(
                type="text",
                text=f"🔄 Multi-Step Workflow {'(Dry Run)' if dry_run else ''}\n\n"
                     f"📝 Description: {workflow_description}\n"
                     f"🗄️ Databases: {', '.join(databases) if databases else 'Auto-detected'}\n"
                     f"📊 Execution Status: {workflow_result.get('status', 'completed')}\n"
                     f"⏱️ Duration: {workflow_result.get('duration', 'N/A')}\n\n"
                     f"🔍 Steps Executed:\n{workflow_result.get('steps_summary', 'No steps available')}\n\n"
                     f"💡 AI Recommendations:\n{workflow_result.get('recommendations', 'None')}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error executing workflow: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Workflow execution failed: {str(e)}"
            )]
    
    async def get_database_inventory(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Retrieve comprehensive database inventory with metadata and AI insights
        Tool definition loaded from YAML configuration
        """
        try:
            portal_filter = arguments.get("portal_filter", [])
            environment_filter = arguments.get("environment_filter", "all")
            health_status_filter = arguments.get("health_status_filter", "all")
            include_metadata = arguments.get("include_metadata", True)
            ai_insights = arguments.get("ai_insights", False)
            
            logger.info(f"📊 Retrieving database inventory (env: {environment_filter}, health: {health_status_filter})")
            
            # Get inventory from portal manager
            inventory = await self.portal_manager.get_database_inventory(
                portal_filter=portal_filter,
                environment_filter=environment_filter,
                health_status_filter=health_status_filter,
                include_metadata=include_metadata
            )
            
            # Generate AI insights if requested
            insights_text = ""
            if ai_insights and inventory.get("databases"):
                insights = await self.gemini_client.analyze_database_inventory(inventory)
                insights_text = f"\n\n🤖 AI Insights:\n{insights}"
            
            return [TextContent(
                type="text",
                text=f"📊 Database Inventory Report\n\n"
                     f"🔍 Environment Filter: {environment_filter}\n"
                     f"💚 Health Filter: {health_status_filter}\n"
                     f"🔌 Portal Filter: {', '.join(portal_filter) if portal_filter else 'All portals'}\n\n"
                     f"📈 Summary:\n"
                     f"• Total Databases: {inventory.get('total_count', 0)}\n"
                     f"• Healthy: {inventory.get('healthy_count', 0)}\n"
                     f"• Warning: {inventory.get('warning_count', 0)}\n"
                     f"• Critical: {inventory.get('critical_count', 0)}\n\n"
                     f"🗄️ Databases:\n{json.dumps(inventory.get('databases', []), indent=2)}"
                     f"{insights_text}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error retrieving inventory: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Failed to retrieve database inventory: {str(e)}"
            )]
    
    async def confirm_operation(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Interactive confirmation system for destructive operations with AI safety validation
        Tool definition loaded from YAML configuration
        """
        try:
            operation_type = arguments.get("operation_type", "")
            target_resources = arguments.get("target_resources", [])
            impact_assessment = arguments.get("impact_assessment", {})
            user_confirmation = arguments.get("user_confirmation", False)
            
            logger.info(f"🛡️ Safety confirmation for {operation_type} on {len(target_resources)} resources")
            
            # AI-powered safety assessment
            safety_analysis = await self.gemini_client.assess_operation_safety(
                operation_type, 
                target_resources, 
                impact_assessment
            )
            
            risk_level = impact_assessment.get("risk_level", "medium")
            risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(risk_level, "⚪")
            
            if user_confirmation:
                return [TextContent(
                    type="text",
                    text=f"✅ Operation Confirmed and Approved\n\n"
                         f"🔧 Operation: {operation_type}\n"
                         f"🎯 Targets: {', '.join(target_resources)}\n"
                         f"{risk_emoji} Risk Level: {risk_level}\n\n"
                         f"🤖 AI Safety Analysis: {safety_analysis}\n\n"
                         f"✅ User confirmation received. Proceeding with operation..."
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"⚠️ Confirmation Required for {operation_type.upper()}\n\n"
                         f"🎯 Target Resources:\n"
                         f"{chr(10).join([f'  • {resource}' for resource in target_resources])}\n\n"
                         f"{risk_emoji} Risk Assessment: {risk_level.upper()}\n"
                         f"📊 Affected Records: {impact_assessment.get('affected_records', 'Unknown')}\n"
                         f"♻️ Rollback Available: {'Yes' if impact_assessment.get('rollback_available') else 'No'}\n\n"
                         f"🤖 AI Safety Analysis:\n{safety_analysis}\n\n"
                         f"❓ Do you want to proceed with this operation? (Reply 'yes' to confirm)"
                )]
            
        except Exception as e:
            logger.error(f"❌ Error in confirmation process: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Error in safety confirmation: {str(e)}"
            )]
    
    async def analyze_database_performance(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        AI-powered database performance analysis with predictive insights
        Tool definition loaded from YAML configuration
        """
        try:
            database_names = arguments.get("database_names", [])
            analysis_type = arguments.get("analysis_type", "comprehensive")
            time_range = arguments.get("time_range", {"period": "24h"})
            metrics = arguments.get("metrics", ["cpu", "memory", "query_performance"])
            ai_recommendations = arguments.get("ai_recommendations", True)
            include_portal_data = arguments.get("include_portal_data", True)
            
            logger.info(f"⚡ Analyzing performance for {len(database_names)} databases ({analysis_type})")
            
            # Collect performance data from portals
            performance_data = await self.portal_manager.collect_performance_metrics(
                database_names=database_names,
                time_range=time_range,
                metrics=metrics,
                include_portal_data=include_portal_data
            )
            
            # AI-powered analysis
            ai_analysis = ""
            if ai_recommendations:
                ai_analysis = await self.gemini_client.analyze_performance_data(
                    performance_data, 
                    analysis_type
                )
            
            return [TextContent(
                type="text",
                text=f"⚡ Database Performance Analysis ({analysis_type})\n\n"
                     f"🗄️ Databases Analyzed: {', '.join(database_names)}\n"
                     f"📊 Metrics: {', '.join(metrics)}\n"
                     f"⏰ Time Range: {time_range.get('period', 'Custom range')}\n\n"
                     f"📈 Performance Data:\n{json.dumps(performance_data, indent=2)}\n\n"
                     f"🤖 AI Performance Analysis:\n{ai_analysis if ai_recommendations else 'AI analysis disabled'}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error analyzing performance: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Performance analysis failed: {str(e)}"
            )]
    
    async def manage_portal_integration(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Manage integration with external self-service portals
        Tool definition loaded from YAML configuration
        """
        try:
            action = arguments.get("action", "list")
            portal_id = arguments.get("portal_id")
            portal_config = arguments.get("portal_config", {})
            discovery_options = arguments.get("discovery_options", {})
            
            logger.info(f"🔌 Portal management action: {action} for {portal_id or 'all portals'}")
            
            result = await self.portal_manager.manage_portal(
                action=action,
                portal_id=portal_id,
                config=portal_config,
                discovery_options=discovery_options
            )
            
            return [TextContent(
                type="text",
                text=f"🔌 Portal Management: {action.upper()}\n\n"
                     f"🎯 Portal: {portal_id or 'All portals'}\n"
                     f"📊 Result: {result.get('status', 'completed')}\n\n"
                     f"📋 Details:\n{json.dumps(result.get('data', {}), indent=2)}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error managing portal: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Portal management failed: {str(e)}"
            )]
    
    async def get_compliance_report(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Generate comprehensive compliance reports with AI analysis
        Tool definition loaded from YAML configuration
        """
        try:
            compliance_frameworks = arguments.get("compliance_frameworks", [])
            scope = arguments.get("scope", {})
            report_format = arguments.get("report_format", "json")
            include_remediation = arguments.get("include_remediation", True)
            ai_risk_assessment = arguments.get("ai_risk_assessment", True)
            
            logger.info(f"📋 Generating compliance report for {', '.join(compliance_frameworks)}")
            
            # Generate compliance report through portal manager
            compliance_data = await self.portal_manager.generate_compliance_report(
                frameworks=compliance_frameworks,
                scope=scope,
                include_remediation=include_remediation
            )
            
            # AI risk assessment
            risk_assessment = ""
            if ai_risk_assessment:
                risk_assessment = await self.gemini_client.assess_compliance_risks(
                    compliance_data,
                    compliance_frameworks
                )
            
            return [TextContent(
                type="text",
                text=f"📋 Compliance Report\n\n"
                     f"🏛️ Frameworks: {', '.join(compliance_frameworks)}\n"
                     f"🎯 Scope: {json.dumps(scope, indent=2)}\n"
                     f"📄 Format: {report_format}\n\n"
                     f"📊 Compliance Status:\n{json.dumps(compliance_data, indent=2)}\n\n"
                     f"🤖 AI Risk Assessment:\n{risk_assessment if ai_risk_assessment else 'Risk assessment disabled'}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error generating compliance report: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Compliance report generation failed: {str(e)}"
            )]
    
    async def orchestrate_conversation_flow(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Manage conversational context and multi-turn interactions
        Tool definition loaded from YAML configuration
        """
        try:
            session_id = arguments.get("session_id", "")
            conversation_action = arguments.get("conversation_action", "start")
            user_message = arguments.get("user_message", "")
            context_data = arguments.get("context_data", {})
            response_options = arguments.get("response_options", {})
            
            logger.info(f"💬 Conversation action: {conversation_action} for session {session_id}")
            
            # Process conversation flow
            flow_result = await self.conversation_flow.handle_conversation_action(
                session_id=session_id,
                action=conversation_action,
                message=user_message,
                context=context_data,
                options=response_options
            )
            
            return [TextContent(
                type="text",
                text=f"💬 Conversation Flow: {conversation_action.upper()}\n\n"
                     f"🔑 Session: {session_id}\n"
                     f"💭 Message: {user_message}\n"
                     f"📊 Flow State: {flow_result.get('state', 'active')}\n\n"
                     f"🤖 Response:\n{flow_result.get('response', 'No response generated')}\n\n"
                     f"💡 Suggestions: {', '.join(flow_result.get('suggestions', []))}"
            )]
            
        except Exception as e:
            logger.error(f"❌ Error in conversation flow: {e}")
            return [TextContent(
                type="text",
                text=f"❌ Conversation flow error: {str(e)}"
            )]