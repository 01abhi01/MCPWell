<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created. ✅ Created

- [x] Clarify Project Requirements ✅ Python MCP server with Gemini LLM, LangGraph architecture for multi-portal integration

- [x] Scaffold the Project ✅ Complete project structure created with MCP server, LangGraph workflows, portal integrations, and Gemini LLM

- [x] Customize the Project ✅ Converted entire codebase to YAML-based configuration in single mcp_tools.yaml file
	
- [x] Simplified Architecture ✅ Reduced to 3 core SSP tools - all operations via SSP API endpoints only

- [ ] Install Required Extensions

- [x] Compile the Project ✅ Minimal dependencies installed, simplified Python loader created

- [ ] Create and Run Task

- [ ] Launch the Project

- [x] Ensure Documentation is Complete ✅ Updated README.md for SSP-first 3-tool architecture

## SSP-First Architecture Notes

This project now uses a simplified 3-tool architecture where ALL operations flow through SSP API endpoints:

1. **ssp_portal_interaction** - Primary tool for all SSP API operations including natural language processing
2. **inventory_metadata_interaction** - Database and resource inventory management via SSP APIs only  
3. **unified_response** - Consolidated response aggregation with AI-powered insights

Key principles:
- Every database operation uses SSP API endpoints exclusively
- No direct database connections or alternate portal interfaces
- All tools are defined in tools_config.yaml with SSP-specific configurations
- AI capabilities (Gemini LLM) enhance SSP operations but don't bypass them
- Session management tracks SSP operation history for unified responses
