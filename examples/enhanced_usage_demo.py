"""
Example Usage of Enhanced Database MCP Server
Demonstrates natural language processing and AI-powered database operations
"""

import asyncio
import json
from src.mcp.enhanced_tools import EnhancedMCPTools
from src.config.config_manager import ConfigManager

async def main():
    """Demonstrate enhanced MCP capabilities"""
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize enhanced tools
    enhanced_tools = EnhancedMCPTools(config_manager)
    
    print("🤖 Enhanced Database MCP Server Demo")
    print("=" * 50)
    
    # Example 1: Natural language database request
    print("\n1. Natural Language Request Processing")
    print("-" * 40)
    
    user_requests = [
        "Show me compliance status for all production databases",
        "Create a backup for database prod_users and prod_orders",
        "What's the patch version for dev_analytics? If it's outdated, apply the latest patch",
        "Kill all idle sessions in staging_reports database",
        "Show performance statistics for prod_main for the last 24 hours"
    ]
    
    for i, request in enumerate(user_requests, 1):
        print(f"\n📝 Request {i}: '{request}'")
        
        try:
            result = await enhanced_tools.process_database_request({
                "user_input": request,
                "session_id": f"demo_session_{i}"
            })
            
            if result:
                print(f"✅ Response: {result[0].text[:200]}...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Example 2: Multi-step workflow
    print("\n\n2. Multi-Step Workflow Execution")
    print("-" * 40)
    
    workflow_description = """
    I need to prepare for a maintenance window:
    1. First show me all production databases
    2. Check their current patch levels
    3. Create restore points for all of them
    4. Apply the latest security patches
    5. Verify compliance after patching
    """
    
    print(f"📋 Workflow: {workflow_description}")
    
    try:
        result = await enhanced_tools.execute_multi_step_workflow({
            "workflow_description": workflow_description,
            "databases": ["prod_users", "prod_orders", "prod_analytics"],
            "dry_run": True,
            "session_id": "maintenance_workflow"
        })
        
        if result:
            print(f"✅ Workflow Plan: {result[0].text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Example 3: AI-powered compliance analysis
    print("\n\n3. AI-Powered Compliance Analysis")
    print("-" * 40)
    
    try:
        result = await enhanced_tools.get_compliance_report({
            "database_name": "prod_users",
            "compliance_standards": ["SOX", "PCI-DSS", "GDPR"],
            "include_remediation": True
        })
        
        if result:
            print(f"✅ Compliance Analysis: {result[0].text[:300]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Example 4: Performance analysis with AI insights
    print("\n\n4. Performance Analysis with AI Insights")
    print("-" * 40)
    
    try:
        result = await enhanced_tools.analyze_database_performance({
            "database_name": "prod_main",
            "time_range": "24h",
            "metrics": ["cpu", "memory", "disk_io", "connections", "query_performance"]
        })
        
        if result:
            print(f"✅ Performance Analysis: {result[0].text[:300]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Example 5: Conversational context
    print("\n\n5. Conversational Database Management")
    print("-" * 40)
    
    conversation_examples = [
        "Show me all databases in production",
        "Which ones need patching?",
        "What about compliance issues?",
        "Create backups for the non-compliant ones",
        "Now show me what we accomplished"
    ]
    
    session_id = "conversation_demo"
    
    for i, message in enumerate(conversation_examples, 1):
        print(f"\n💬 User: {message}")
        
        try:
            result = await enhanced_tools.process_database_request({
                "user_input": message,
                "session_id": session_id
            })
            
            if result:
                print(f"🤖 Assistant: {result[0].text[:150]}...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Example 6: Get conversation history
    print("\n\n6. Conversation History")
    print("-" * 40)
    
    try:
        result = await enhanced_tools.get_conversation_history({
            "session_id": session_id,
            "limit": 5
        })
        
        if result:
            print(f"📚 History: {result[0].text[:300]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Example 7: Database concept explanation
    print("\n\n7. AI-Powered Database Concept Explanation")
    print("-" * 40)
    
    concepts_to_explain = [
        "database deadlock",
        "ACID properties",
        "database partitioning strategies",
        "backup recovery point objective (RPO)",
        "database compliance requirements for GDPR"
    ]
    
    for concept in concepts_to_explain[:2]:  # Show first 2 for demo
        print(f"\n🎓 Explaining: {concept}")
        
        try:
            result = await enhanced_tools.explain_database_concept({
                "concept": concept,
                "detail_level": "intermediate",
                "context": {"role": "database_administrator"}
            })
            
            if result:
                print(f"📖 Explanation: {result[0].text[:200]}...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n\n🎉 Demo completed! The enhanced MCP server provides:")
    print("   • Natural language understanding for database operations")
    print("   • AI-powered intent classification and workflow orchestration")
    print("   • Conversational context maintenance")
    print("   • Intelligent compliance and performance analysis")
    print("   • Multi-step workflow execution with safety checks")
    print("   • Educational database concept explanations")

if __name__ == "__main__":
    # Note: This demo requires proper configuration in config/
    # Make sure to set up your Gemini API key and portal configurations
    
    print("⚠️  Demo requires:")
    print("   1. Gemini API key in config/llm_config.yaml")
    print("   2. Portal configurations in config/portals/")
    print("   3. Environment variables in .env file")
    print("\nStarting demo...\n")
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Demo failed: {e}")
        print("Please check your configuration and dependencies.")
