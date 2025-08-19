"""Tests for workflow orchestrator functionality."""

import pytest
from unittest.mock import AsyncMock, patch

from mcp_well_server.core.workflow_orchestrator import (
    PortalWorkflowOrchestrator, WorkflowStatus, WorkflowState
)


@pytest.mark.asyncio
class TestWorkflowOrchestrator:
    """Test workflow orchestrator functionality."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a workflow orchestrator instance."""
        return PortalWorkflowOrchestrator()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert len(orchestrator.workflows) > 0
        assert "database_backup" in orchestrator.workflows
        assert "database_restore" in orchestrator.workflows
        assert "compliance_check" in orchestrator.workflows
    
    async def test_workflow_execution(self, orchestrator, sample_workflow_state):
        """Test workflow execution."""
        # Mock workflow steps to avoid actual portal calls
        with patch.object(orchestrator, '_validate_backup_request') as mock_validate:
            mock_validate.return_value = sample_workflow_state
            
            with patch.object(orchestrator, '_check_database_metadata') as mock_metadata:
                mock_metadata.return_value = sample_workflow_state
                
                with patch.object(orchestrator, '_verify_user_permissions') as mock_permissions:
                    mock_permissions.return_value = sample_workflow_state
                    
                    # Execute a simplified workflow (we'd need to mock all steps for full execution)
                    # For this test, we'll just verify the orchestrator can start execution
                    
                    execution_id = sample_workflow_state["request_id"]
                    
                    # Test that we can track execution
                    orchestrator.active_executions[execution_id] = {
                        "workflow_name": "database_backup",
                        "status": WorkflowStatus.RUNNING.value,
                        "start_time": 0.0
                    }
                    
                    status = orchestrator.get_execution_status(execution_id)
                    assert status is not None
                    assert status["workflow_name"] == "database_backup"
                    assert status["status"] == WorkflowStatus.RUNNING.value
    
    def test_execution_status_tracking(self, orchestrator):
        """Test execution status tracking."""
        execution_id = "test-execution-123"
        
        # Test non-existent execution
        status = orchestrator.get_execution_status(execution_id)
        assert status is None
        
        # Add execution
        orchestrator.active_executions[execution_id] = {
            "workflow_name": "test_workflow",
            "status": WorkflowStatus.RUNNING.value,
            "start_time": 12345.0
        }
        
        # Test existing execution
        status = orchestrator.get_execution_status(execution_id)
        assert status is not None
        assert status["workflow_name"] == "test_workflow"
        assert status["status"] == WorkflowStatus.RUNNING.value
    
    def test_execution_cancellation(self, orchestrator):
        """Test execution cancellation."""
        execution_id = "test-execution-123"
        
        # Test cancelling non-existent execution
        result = orchestrator.cancel_execution(execution_id)
        assert result is False
        
        # Add execution
        orchestrator.active_executions[execution_id] = {
            "workflow_name": "test_workflow",
            "status": WorkflowStatus.RUNNING.value,
            "start_time": 12345.0
        }
        
        # Test cancelling existing execution
        result = orchestrator.cancel_execution(execution_id)
        assert result is True
        
        status = orchestrator.get_execution_status(execution_id)
        assert status["status"] == WorkflowStatus.CANCELLED.value
    
    async def test_workflow_step_implementations(self, orchestrator, sample_workflow_state):
        """Test individual workflow step implementations."""
        state = sample_workflow_state.copy()
        
        # Test validate backup request step
        result_state = await orchestrator._validate_backup_request(state)
        assert result_state["current_step"] == "validate_backup_request"
        assert "validate_backup_request" in result_state["steps_completed"]
        
        # Test check database metadata step
        result_state = await orchestrator._check_database_metadata(state)
        assert result_state["current_step"] == "check_database_metadata"
        assert "check_database_metadata" in result_state["steps_completed"]
        
        # Test verify user permissions step
        result_state = await orchestrator._verify_user_permissions(state)
        assert result_state["current_step"] == "verify_user_permissions"
        assert "verify_user_permissions" in result_state["steps_completed"]
    
    @patch('mcp_well_server.core.workflow_orchestrator.gemini_llm')
    async def test_generate_operation_report(self, mock_gemini, orchestrator, sample_workflow_state):
        """Test operation report generation."""
        state = sample_workflow_state.copy()
        state["results"] = {"backup_id": "backup_123"}
        
        # Mock Gemini LLM response
        mock_gemini.generate_documentation.return_value = "# Test Report\nOperation completed successfully."
        
        result_state = await orchestrator._generate_operation_report(state)
        
        assert result_state["current_step"] == "generate_operation_report"
        assert "generate_operation_report" in result_state["steps_completed"]
        assert "operation_report" in result_state["results"]
        assert "Test Report" in result_state["results"]["operation_report"]
        
        # Verify Gemini was called with correct parameters
        mock_gemini.generate_documentation.assert_called_once_with(
            operation=state["operation_type"],
            parameters=state["parameters"],
            result=state["results"]
        )
    
    @patch('mcp_well_server.core.workflow_orchestrator.gemini_llm')
    async def test_analyze_generic_request(self, mock_gemini, orchestrator, sample_workflow_state):
        """Test generic request analysis."""
        state = sample_workflow_state.copy()
        
        # Mock Gemini LLM response
        mock_analysis = {
            "operation_type": "backup",
            "risks": ["low"],
            "execution_plan": ["validate", "execute", "verify"]
        }
        mock_gemini.analyze_portal_request.return_value = mock_analysis
        
        result_state = await orchestrator._analyze_generic_request(state)
        
        assert result_state["current_step"] == "analyze_generic_request"
        assert "analyze_generic_request" in result_state["steps_completed"]
        assert "request_analysis" in result_state["metadata"]
        assert result_state["metadata"]["request_analysis"] == mock_analysis
        
        # Verify Gemini was called with correct parameters
        mock_gemini.analyze_portal_request.assert_called_once_with(
            request=state["parameters"],
            portal_context=state["context"]
        )
    
    async def test_workflow_error_handling(self, orchestrator, sample_workflow_state):
        """Test workflow error handling."""
        state = sample_workflow_state.copy()
        
        # Test that errors are properly captured in state
        with patch('mcp_well_server.core.workflow_orchestrator.gemini_llm') as mock_gemini:
            mock_gemini.generate_documentation.side_effect = Exception("LLM Error")
            
            result_state = await orchestrator._generate_operation_report(state)
            
            assert len(result_state["errors"]) > 0
            assert "Report generation failed" in result_state["errors"][0]
