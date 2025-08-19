"""
Gradio Chat Interface for SSP MCP Tools
Interactive chat interface for database operations via SSP portals
"""

import asyncio
import gradio as gr
import sys
import os
from typing import List, Tuple, Dict, Any
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp.enhanced_tools import EnhancedMCPTools
from src.config.config_manager import ConfigManager
from src.portals.portal_manager import PortalManager
from src.llm.gemini_client import EnhancedGeminiClient
from src.nlp.intent_classifier import DatabaseIntentClassifier, ConversationFlow
from src.workflows.database_workflow import DatabaseWorkflowEngine

class SSPChatInterface:
    def __init__(self):
        """Initialize the SSP Chat Interface"""
        self.config_manager = ConfigManager()
        self.mcp_tools = EnhancedMCPTools(self.config_manager)
        
        # Command mapping for natural language input
        self.command_mapping = {
            "show db": self._handle_show_db,
            "show databases": self._handle_show_db,
            "list databases": self._handle_show_db,
            "show patch status": self._handle_patch_status,
            "patch status": self._handle_patch_status,
            "show status": self._handle_patch_status,
            "system status": self._handle_patch_status,
            "show workflows": self._handle_show_workflows,
            "list workflows": self._handle_show_workflows,
            "workflow status": self._handle_workflow_status,
            "run workflow": self._handle_run_workflow,
            "create workflow": self._handle_create_workflow,
            "help": self._handle_help,
            "commands": self._handle_help
        }

    async def _handle_show_db(self) -> str:
        """Handle show database command"""
        try:
            # Use inventory metadata interaction tool
            result = await self.mcp_tools.inventory_metadata_interaction({
                "action": "list",
                "resource_types": ["databases"],
                "filters": {},
                "portal": "all"
            })
            
            # Extract text content
            if result and len(result) > 0:
                response = result[0].text
                return f"🗄️ **Database Inventory:**\n\n{response}"
            else:
                return "❌ No database information available"
                
        except Exception as e:
            return f"❌ Error retrieving database information: {str(e)}"

    async def _handle_patch_status(self) -> str:
        """Handle patch status command"""
        try:
            # Use SSP portal interaction for system status
            result = await self.mcp_tools.ssp_portal_interaction({
                "operation": "api_call",
                "endpoint": "/api/v1/system/patch-status",
                "method": "GET",
                "parameters": {"include_details": True},
                "portal": "security"
            })
            
            # Extract text content
            if result and len(result) > 0:
                response = result[0].text
                return f"🔧 **System Patch Status:**\n\n{response}"
            else:
                return "❌ No patch status information available"
                
        except Exception as e:
            return f"❌ Error retrieving patch status: {str(e)}"

    async def _handle_show_workflows(self) -> str:
        """Handle show workflows command"""
        try:
            # Get workflow engine instance and show available workflows
            workflows = self.mcp_tools.workflow_engine.get_available_workflows()
            
            response = "🔄 **Available LangGraph Workflows:**\n\n"
            
            if workflows:
                for workflow in workflows:
                    response += f"• **{workflow.get('name', 'Unnamed')}**\n"
                    response += f"  - ID: {workflow.get('id', 'N/A')}\n"
                    response += f"  - Type: {workflow.get('type', 'Database Operation')}\n"
                    response += f"  - Steps: {len(workflow.get('steps', []))}\n"
                    response += f"  - Status: {workflow.get('status', 'Ready')}\n\n"
            else:
                response += "No workflows currently defined.\n\n"
                
            response += "**Default Workflow Templates:**\n"
            response += "• Database Backup & Validation\n"
            response += "• Performance Analysis & Optimization\n" 
            response += "• Security Scan & Patch Management\n"
            response += "• Multi-Portal Data Sync\n\n"
            response += "Type `run workflow <name>` to execute a workflow."
            
            return response
            
        except Exception as e:
            return f"❌ Error retrieving workflows: {str(e)}"

    async def _handle_workflow_status(self) -> str:
        """Handle workflow status command"""
        try:
            # Get running workflow status
            status = self.mcp_tools.workflow_engine.get_workflow_status()
            
            response = "📊 **LangGraph Workflow Status:**\n\n"
            
            if status.get('active_workflows'):
                for workflow_id, workflow_status in status['active_workflows'].items():
                    response += f"🔄 **{workflow_id}**\n"
                    response += f"  - Status: {workflow_status.get('status', 'Unknown')}\n"
                    response += f"  - Progress: {workflow_status.get('progress', 0)}%\n"
                    response += f"  - Current Step: {workflow_status.get('current_step', 'N/A')}\n"
                    response += f"  - Started: {workflow_status.get('start_time', 'N/A')}\n\n"
            else:
                response += "No workflows currently running.\n\n"
                
            response += f"**Statistics:**\n"
            response += f"• Total Workflows Run: {status.get('total_runs', 0)}\n"
            response += f"• Success Rate: {status.get('success_rate', 100)}%\n"
            response += f"• Average Runtime: {status.get('avg_runtime', 'N/A')}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error retrieving workflow status: {str(e)}"

    async def _handle_run_workflow(self) -> str:
        """Handle run workflow command"""
        try:
            # Start a demo workflow
            workflow_result = await self.mcp_tools.workflow_engine.execute_workflow(
                workflow_type="database_analysis",
                parameters={
                    "target_databases": ["all"],
                    "analysis_type": "performance",
                    "include_recommendations": True
                }
            )
            
            response = "🚀 **Workflow Execution Started:**\n\n"
            response += f"• Workflow ID: {workflow_result.get('workflow_id', 'N/A')}\n"
            response += f"• Type: Database Analysis\n"
            response += f"• Status: {workflow_result.get('status', 'Started')}\n"
            response += f"• Estimated Duration: {workflow_result.get('estimated_duration', '5-10 minutes')}\n\n"
            
            if workflow_result.get('steps'):
                response += "**Workflow Steps:**\n"
                for i, step in enumerate(workflow_result['steps'], 1):
                    status_icon = "✅" if step.get('status') == 'completed' else "⏳" if step.get('status') == 'running' else "⏸️"
                    response += f"{status_icon} {i}. {step.get('name', 'Step')}\n"
                    
            response += "\nUse `workflow status` to monitor progress."
            
            return response
            
        except Exception as e:
            return f"❌ Error running workflow: {str(e)}"

    async def _handle_create_workflow(self) -> str:
        """Handle create workflow command"""
        response = "🛠️ **Create Custom LangGraph Workflow:**\n\n"
        response += "**Available Workflow Templates:**\n\n"
        
        templates = [
            {
                "name": "Database Health Check",
                "steps": ["Connect to DBs", "Check Status", "Validate Backups", "Generate Report"],
                "duration": "3-5 minutes"
            },
            {
                "name": "Security Audit",
                "steps": ["Scan Vulnerabilities", "Check Patch Status", "Validate Access Controls", "Create Action Plan"],
                "duration": "10-15 minutes"
            },
            {
                "name": "Performance Optimization", 
                "steps": ["Analyze Metrics", "Identify Bottlenecks", "Generate Recommendations", "Apply Optimizations"],
                "duration": "15-20 minutes"
            }
        ]
        
        for i, template in enumerate(templates, 1):
            response += f"**{i}. {template['name']}**\n"
            response += f"   Steps: {' → '.join(template['steps'])}\n"
            response += f"   Duration: {template['duration']}\n\n"
            
        response += "**Custom Workflow Builder:**\n"
        response += "• Use the workflow designer in the web interface\n"
        response += "• Drag & drop workflow steps\n"
        response += "• Configure SSP portal connections\n"
        response += "• Set up conditional logic and error handling\n\n"
        response += "Type `run workflow <template_name>` to execute a template."
        
        return response

    async def _handle_help(self) -> str:
        """Handle help command"""
        help_text = """
🤖 **SSP Chat Interface Help**

**Database Commands:**
- `show db` / `show databases` / `list databases` - Display database inventory
- `show patch status` / `patch status` - Show system patch status  
- `system status` - Show overall system status

**LangGraph Workflow Commands:**
- `show workflows` / `list workflows` - Display available workflows
- `workflow status` - Show running workflow status
- `run workflow` - Execute a workflow template
- `create workflow` - Show workflow builder options

**General Commands:**
- `help` / `commands` - Show this help message

**Natural Language:**
You can also ask questions in natural language, such as:
- "What databases are available?"
- "Check the security patch status"
- "Show me the system health"
- "Run a database analysis workflow"
- "What workflows are currently running?"

**LangGraph Features:**
- Visual workflow designer with drag & drop
- Real-time workflow execution monitoring
- Multi-step database operations with state management
- Conditional logic and error handling
- Integration with multiple SSP portals

**SSP Integration:**
- All operations use SSP API endpoints
- Multi-portal support (Security, DevOps, Infrastructure)
- Real-time status monitoring
- AI-powered response generation

Type any command or question to get started!
        """
        return help_text.strip()

    async def process_message(self, message: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], str]:
        """Process user message and return updated history"""
        if not message.strip():
            return history, ""
            
        # Add user message to history
        history.append({"role": "user", "content": message})
        
        # Normalize message for command matching
        normalized_message = message.lower().strip()
        
        # Check for direct command matches
        response = None
        for command, handler in self.command_mapping.items():
            if command in normalized_message:
                response = await handler()
                break
        
        # If no direct command match, use natural language processing
        if response is None:
            try:
                # Use the unified response tool for natural language queries
                result = await self.mcp_tools.unified_response({
                    "response_type": "analysis",
                    "session_id": "chat_session",
                    "context_operations": [message],
                    "additional_context": {
                        "user_query": message,
                        "chat_history": [h["content"] for h in history[-5:] if h["role"] == "user"]  # Last 5 user messages
                    }
                })
                
                if result and len(result) > 0:
                    response = result[0].text
                else:
                    response = "🤔 I didn't understand that. Try 'help' for available commands."
                    
            except Exception as e:
                response = f"❌ Error processing request: {str(e)}\n\nTry 'help' for available commands."
        
        # Add assistant response to history
        history.append({"role": "assistant", "content": response})
        
        return history, ""

    def create_workflow_diagram(self) -> go.Figure:
        """Create an interactive workflow diagram using Plotly"""
        
        # Sample workflow data
        workflow_nodes = [
            {"id": "start", "name": "Start", "x": 1, "y": 3, "status": "completed"},
            {"id": "connect", "name": "Connect to SSP", "x": 2, "y": 3, "status": "completed"},
            {"id": "validate", "name": "Validate Access", "x": 3, "y": 3, "status": "completed"},
            {"id": "scan_db", "name": "Scan Databases", "x": 4, "y": 4, "status": "running"},
            {"id": "scan_security", "name": "Security Check", "x": 4, "y": 2, "status": "pending"},
            {"id": "analyze", "name": "Analyze Results", "x": 5, "y": 3, "status": "pending"},
            {"id": "report", "name": "Generate Report", "x": 6, "y": 3, "status": "pending"},
            {"id": "end", "name": "Complete", "x": 7, "y": 3, "status": "pending"}
        ]
        
        workflow_edges = [
            ("start", "connect"),
            ("connect", "validate"),
            ("validate", "scan_db"),
            ("validate", "scan_security"),
            ("scan_db", "analyze"),
            ("scan_security", "analyze"),
            ("analyze", "report"),
            ("report", "end")
        ]
        
        # Create the plot
        fig = go.Figure()
        
        # Add edges (connections between nodes)
        for edge in workflow_edges:
            start_node = next(n for n in workflow_nodes if n["id"] == edge[0])
            end_node = next(n for n in workflow_nodes if n["id"] == edge[1])
            
            fig.add_trace(go.Scatter(
                x=[start_node["x"], end_node["x"]],
                y=[start_node["y"], end_node["y"]],
                mode='lines',
                line=dict(color='lightgray', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Color mapping for status
        status_colors = {
            "completed": "green",
            "running": "orange", 
            "pending": "lightblue",
            "failed": "red"
        }
        
        # Add nodes
        for status in status_colors:
            nodes_with_status = [n for n in workflow_nodes if n["status"] == status]
            if nodes_with_status:
                fig.add_trace(go.Scatter(
                    x=[n["x"] for n in nodes_with_status],
                    y=[n["y"] for n in nodes_with_status],
                    mode='markers+text',
                    marker=dict(
                        size=40,
                        color=status_colors[status],
                        line=dict(width=2, color='white')
                    ),
                    text=[n["name"] for n in nodes_with_status],
                    textposition='middle center',
                    textfont=dict(size=10, color='white'),
                    name=status.title(),
                    hovertemplate='<b>%{text}</b><br>Status: ' + status + '<extra></extra>'
                ))
        
        # Update layout
        fig.update_layout(
            title="LangGraph Workflow Execution",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            showlegend=True,
            height=400,
            margin=dict(l=20, r=20, t=50, b=20),
            plot_bgcolor='white'
        )
        
        return fig

    def create_workflow_stats(self) -> go.Figure:
        """Create workflow execution statistics chart"""
        
        # Sample statistics data
        dates = ['2025-08-15', '2025-08-16', '2025-08-17', '2025-08-18', '2025-08-19', '2025-08-20']
        successful_workflows = [12, 15, 18, 14, 20, 16]
        failed_workflows = [2, 1, 3, 2, 1, 2]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates,
            y=successful_workflows,
            name='Successful',
            marker_color='green'
        ))
        
        fig.add_trace(go.Bar(
            x=dates,
            y=failed_workflows,
            name='Failed',
            marker_color='red'
        ))
        
        fig.update_layout(
            title='Workflow Execution Statistics',
            xaxis_title='Date',
            yaxis_title='Number of Workflows',
            barmode='stack',
            height=300
        )
        
        return fig

def create_chat_interface():
    """Create and configure the Gradio chat interface"""
    
    # Initialize the SSP chat interface
    chat_interface = SSPChatInterface()
    
    # Define the async wrapper for Gradio
    def process_message_sync(message: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], str]:
        """Synchronous wrapper for async message processing"""
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(chat_interface.process_message(message, history))
    
    # Create the Gradio interface
    with gr.Blocks(
        title="SSP Database Chat Interface with LangGraph Workflows",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        .chat-message {
            padding: 10px;
            margin: 5px;
            border-radius: 10px;
        }
        """
    ) as interface:
        
        gr.Markdown("""
        # 🤖 SSP Database Chat Interface with LangGraph Workflows
        
        Interactive chat interface for SSP (Self-Service Portal) database operations with real-time workflow visualization.
        
        **Quick Start:** Try typing `show db`, `show workflows`, or `help`
        """)
        
        # Create tabs for different features
        with gr.Tabs():
            # Chat Tab
            with gr.TabItem("💬 Chat Interface"):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="SSP Assistant",
                    height=500,
                    show_label=True,
                    avatar_images=("👤", "🤖"),
                    type="messages"  # Use new messages format
                )
                
                msg = gr.Textbox(
                    label="Your message",
                    placeholder="Type 'show db', 'show workflows', 'patch status', or ask any question...",
                    lines=1,
                    max_lines=3
                )
                
                clear = gr.Button("Clear Chat")
                
                # Examples
                gr.Examples(
                    examples=[
                        "show db",
                        "show patch status", 
                        "show workflows",
                        "workflow status",
                        "run workflow",
                        "help",
                        "What databases are available?",
                        "Check system health",
                        "Run a database analysis workflow"
                    ],
                    inputs=msg,
                    label="Example Commands"
                )
            
            # Workflow Visualization Tab
            with gr.TabItem("🔄 Workflow Visualization"):
                gr.Markdown("## Real-time LangGraph Workflow Monitoring")
                
                # Workflow diagram
                workflow_plot = gr.Plot(
                    label="Current Workflow Execution",
                    value=chat_interface.create_workflow_diagram()
                )
                
                # Workflow controls
                with gr.Row():
                    workflow_select = gr.Dropdown(
                        choices=["Database Analysis", "Security Audit", "Performance Check", "Backup Validation"],
                        label="Select Workflow Template",
                        value="Database Analysis"
                    )
                    start_workflow_btn = gr.Button("▶️ Start Workflow", variant="primary")
                    stop_workflow_btn = gr.Button("⏹️ Stop Workflow", variant="secondary")
                
                # Workflow status
                workflow_status = gr.Textbox(
                    label="Workflow Status",
                    value="Ready to execute workflows",
                    interactive=False,
                    lines=3
                )
                
            # Analytics Tab  
            with gr.TabItem("📊 Analytics"):
                gr.Markdown("## Workflow Execution Analytics")
                
                # Statistics chart
                stats_plot = gr.Plot(
                    label="Workflow Statistics",
                    value=chat_interface.create_workflow_stats()
                )
                
                # Analytics metrics
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Performance Metrics")
                        total_workflows = gr.Number(label="Total Workflows", value=98, interactive=False)
                        success_rate = gr.Number(label="Success Rate (%)", value=94.2, interactive=False)
                        avg_duration = gr.Textbox(label="Avg Duration", value="4.5 minutes", interactive=False)
                    
                    with gr.Column():
                        gr.Markdown("### Resource Usage")
                        active_connections = gr.Number(label="Active SSP Connections", value=3, interactive=False)
                        memory_usage = gr.Number(label="Memory Usage (MB)", value=245, interactive=False)
                        cpu_usage = gr.Number(label="CPU Usage (%)", value=15.8, interactive=False)
            
            # Workflow Builder Tab
            with gr.TabItem("🛠️ Workflow Builder"):
                gr.Markdown("## Visual LangGraph Workflow Designer")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Available Steps")
                        step_types = gr.CheckboxGroup(
                            choices=[
                                "Connect to SSP Portal",
                                "Database Query",
                                "Security Scan", 
                                "Performance Analysis",
                                "Data Validation",
                                "Generate Report",
                                "Send Notification",
                                "Error Handling"
                            ],
                            label="Workflow Steps",
                            value=["Connect to SSP Portal", "Database Query"]
                        )
                        
                        workflow_name = gr.Textbox(label="Workflow Name", placeholder="My Custom Workflow")
                        save_workflow_btn = gr.Button("💾 Save Workflow", variant="primary")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### Workflow Preview")
                        workflow_preview = gr.Code(
                            label="Generated Workflow Code",
                            language="python",
                            value="""
# Generated LangGraph Workflow
from langgraph.graph import StateGraph

def create_workflow():
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("connect_ssp", connect_to_ssp)
    workflow.add_node("database_query", execute_database_query)
    
    # Add edges
    workflow.add_edge("connect_ssp", "database_query")
    
    return workflow.compile()
                            """.strip()
                        )
        
        # Process message and update chat (Chat tab)
        msg.submit(
            process_message_sync,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        # Clear chat history (Chat tab)
        clear.click(lambda: ([], ""), outputs=[chatbot, msg])
        
        # Workflow control functions
        def start_workflow(workflow_name):
            return f"🚀 Starting {workflow_name} workflow...\nStatus: Initializing\nEstimated time: 5-10 minutes"
        
        def stop_workflow():
            return "⏹️ Workflow stopped.\nStatus: Cancelled by user"
        
        def update_workflow_preview(selected_steps):
            if not selected_steps:
                return "# No steps selected"
                
            code = "# Generated LangGraph Workflow\nfrom langgraph.graph import StateGraph\n\n"
            code += "def create_workflow():\n    workflow = StateGraph(WorkflowState)\n\n"
            code += "    # Add nodes\n"
            
            for step in selected_steps:
                node_name = step.lower().replace(" ", "_")
                code += f'    workflow.add_node("{node_name}", {node_name}_function)\n'
            
            code += "\n    # Add edges\n"
            for i in range(len(selected_steps) - 1):
                current = selected_steps[i].lower().replace(" ", "_")
                next_step = selected_steps[i + 1].lower().replace(" ", "_")
                code += f'    workflow.add_edge("{current}", "{next_step}")\n'
            
            code += "\n    return workflow.compile()"
            return code
        
        # Workflow event handlers
        start_workflow_btn.click(
            start_workflow,
            inputs=[workflow_select],
            outputs=[workflow_status]
        )
        
        stop_workflow_btn.click(
            stop_workflow,
            outputs=[workflow_status]
        )
        
        step_types.change(
            update_workflow_preview,
            inputs=[step_types],
            outputs=[workflow_preview]
        )
        
        # Add footer
        gr.Markdown("""
        ---
        **SSP + LangGraph Integration Features:**
        - 🔌 Multi-portal SSP API integration with visual workflow orchestration
        - 🤖 AI-powered natural language processing with LangGraph state management
        - 📊 Real-time database and system monitoring with workflow analytics
        - 🔧 Unified response aggregation with interactive workflow visualization
        - 🛠️ Visual workflow builder with drag-and-drop interface
        """)
    
    return interface

def refresh_workflow_plot():
    """Function to periodically refresh workflow visualization"""
    # This would be called periodically to update the workflow diagram
    # with real-time status from the workflow engine
    pass

if __name__ == "__main__":
    print("🚀 Starting SSP Database Chat Interface with LangGraph Workflows...")
    
    # Create and launch the interface
    interface = create_chat_interface()
    
    # Launch with automatic browser opening
    interface.launch(
        server_name="localhost",  # Use localhost instead of 0.0.0.0 for local access
        server_port=7860,
        inbrowser=True,  # Automatically open in browser
        share=False,  # Set to True if you want a public link
        show_error=True,
        quiet=False
    )
