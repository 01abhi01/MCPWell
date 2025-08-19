"""
Enhanced Gemini LLM Client with Advanced AI Capabilities
Provides natural language understanding, analysis, and generation for database operations
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from google.ai.generativelanguage_v1beta.types import content

logger = logging.getLogger(__name__)

class EnhancedGeminiClient:
    """
    Enhanced Gemini client with specialized database operation capabilities
    Provides AI-powered analysis, recommendations, and safety validation
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self.mock_mode = False
        
        # Check if API key is valid (not a placeholder)
        if not api_key or api_key in ["your_gemini_api_key_here", "test_google_api_key_placeholder"]:
            logger.warning("⚠️ Gemini API key not configured, running in mock mode")
            self.mock_mode = True
            self.model = None
        else:
            try:
                # Configure Gemini
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Gemini client: {e}. Running in mock mode")
                self.mock_mode = True
                self.model = None
        
        # Safety settings for database operations
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Generation configuration for database contexts
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        # Specialized prompts for database operations
        self.system_prompts = {
            "database_expert": """You are an expert database administrator and architect with deep knowledge of:
- SQL databases (MySQL, PostgreSQL, SQL Server, Oracle)
- NoSQL databases (MongoDB, Cassandra, DynamoDB)
- Cloud database services (AWS RDS, Azure SQL, GCP Cloud SQL)
- Database performance optimization
- Data security and compliance
- Backup and recovery strategies
- Database monitoring and troubleshooting

Provide accurate, safe, and actionable advice for database operations.""",
            
            "safety_validator": """You are a database safety validator responsible for:
- Identifying potentially destructive operations
- Assessing risk levels of database changes
- Recommending safety measures and rollback strategies
- Ensuring compliance with best practices
- Warning about data loss risks

Always err on the side of caution and provide clear warnings for high-risk operations.""",
            
            "performance_analyst": """You are a database performance analyst specializing in:
- Query optimization and indexing strategies
- Resource utilization analysis
- Bottleneck identification
- Capacity planning
- Performance monitoring and alerting
- Cost optimization

Provide data-driven insights and actionable recommendations."""
        }
        
        logger.info(f"🤖 Enhanced Gemini Client initialized with model: {model_name}")
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None, 
                              expert_mode: str = "database_expert") -> str:
        """
        Generate AI response with specialized database expertise
        """
        try:
            # Return mock response if in mock mode
            if self.mock_mode:
                logger.info("🤖 Mock mode: Generating placeholder response")
                return f"Mock response for: {prompt[:50]}... (Gemini API not configured)"
            
            # Prepare system prompt
            system_prompt = self.system_prompts.get(expert_mode, self.system_prompts["database_expert"])
            
            # Add context if provided
            context_str = ""
            if context:
                context_str = f"\nContext: {context}"
            
            # Construct full prompt
            full_prompt = f"{system_prompt}\n\n{prompt}{context_str}"
            
            # Generate response
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            logger.debug(f"🤖 Generated response for prompt: '{prompt[:50]}...'")
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return f"Error generating AI response: {str(e)}"
    
    async def classify_database_intent(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify user intent for database operations with high accuracy
        """
        try:
            prompt = f"""
            Classify this database request into one of these intent categories:
            
            INTENT CATEGORIES:
            - CREATE: Creating databases, tables, indexes, or data
            - READ: Querying, viewing, or retrieving information
            - UPDATE: Modifying existing data or database structure
            - DELETE: Removing data, tables, or databases (HIGH RISK)
            - BACKUP: Creating backups or exports
            - RESTORE: Restoring from backups (HIGH RISK)
            - ANALYZE: Performance analysis or data examination
            - OPTIMIZE: Performance tuning or improvements
            - MONITOR: Health checks or monitoring setup
            - TROUBLESHOOT: Debugging or issue resolution
            - COMPLIANCE: Security audits or compliance checks
            - MIGRATION: Moving or upgrading databases (HIGH RISK)
            - ADMINISTRATION: User management or configuration
            - UNKNOWN: Cannot determine intent
            
            USER REQUEST: "{user_input}"
            CONTEXT: {context or 'None'}
            
            Respond in JSON format:
            {{
                "intent": "category_name",
                "confidence": 0.95,
                "reasoning": "explanation of classification",
                "risk_level": "low|medium|high",
                "entities": {{
                    "databases": ["db_names"],
                    "tables": ["table_names"],
                    "operations": ["specific_operations"],
                    "environment": "prod|dev|test",
                    "time_scope": "time_range"
                }},
                "requires_confirmation": true|false,
                "safety_concerns": ["concern1", "concern2"]
            }}
            """
            
            response = await self.generate_response(prompt, context, "database_expert")
            
            # Parse JSON response
            try:
                import json
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "intent": "UNKNOWN",
                    "confidence": 0.5,
                    "reasoning": "Failed to parse AI response",
                    "risk_level": "medium",
                    "entities": {},
                    "requires_confirmation": True,
                    "safety_concerns": ["Unable to properly classify request"]
                }
                
        except Exception as e:
            logger.error(f"❌ Error classifying intent: {e}")
            return {
                "intent": "UNKNOWN",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "risk_level": "high",
                "entities": {},
                "requires_confirmation": True,
                "safety_concerns": ["Classification failed"]
            }
    
    async def assess_operation_safety(self, operation_type: str, target_resources: List[str], 
                                    impact_assessment: Dict[str, Any]) -> str:
        """
        AI-powered safety assessment for database operations
        """
        try:
            prompt = f"""
            Assess the safety of this database operation:
            
            OPERATION: {operation_type}
            TARGET RESOURCES: {', '.join(target_resources)}
            IMPACT ASSESSMENT: {impact_assessment}
            
            Provide a comprehensive safety analysis including:
            1. Risk level assessment (low/medium/high/critical)
            2. Potential consequences
            3. Recommended precautions
            4. Rollback strategy
            5. Approval requirements
            
            Be specific about data loss risks, downtime, and compliance implications.
            """
            
            safety_analysis = await self.generate_response(prompt, expert_mode="safety_validator")
            return safety_analysis
            
        except Exception as e:
            logger.error(f"❌ Error assessing operation safety: {e}")
            return f"Safety assessment failed: {str(e)}"
    
    async def analyze_database_inventory(self, inventory_data: Dict[str, Any]) -> str:
        """
        AI-powered analysis of database inventory
        """
        try:
            prompt = f"""
            Analyze this database inventory and provide insights:
            
            INVENTORY DATA: {inventory_data}
            
            Provide analysis on:
            1. Database distribution and patterns
            2. Resource utilization insights
            3. Health and performance observations
            4. Security and compliance status
            5. Cost optimization opportunities
            6. Maintenance recommendations
            
            Focus on actionable insights and potential issues.
            """
            
            analysis = await self.generate_response(prompt, expert_mode="performance_analyst")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing inventory: {e}")
            return f"Inventory analysis failed: {str(e)}"
    
    async def analyze_performance_data(self, performance_data: Dict[str, Any], 
                                     analysis_type: str = "comprehensive") -> str:
        """
        AI-powered performance analysis
        """
        try:
            prompt = f"""
            Analyze this database performance data:
            
            PERFORMANCE DATA: {performance_data}
            ANALYSIS TYPE: {analysis_type}
            
            Provide detailed analysis including:
            1. Performance bottlenecks identification
            2. Resource utilization patterns
            3. Query performance insights
            4. Scalability recommendations
            5. Optimization strategies
            6. Alerting recommendations
            
            Include specific metrics and thresholds where applicable.
            """
            
            analysis = await self.generate_response(prompt, expert_mode="performance_analyst")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing performance data: {e}")
            return f"Performance analysis failed: {str(e)}"
    
    async def assess_compliance_risks(self, compliance_data: Dict[str, Any], 
                                    frameworks: List[str]) -> str:
        """
        AI-powered compliance risk assessment
        """
        try:
            prompt = f"""
            Assess compliance risks based on this data:
            
            COMPLIANCE DATA: {compliance_data}
            FRAMEWORKS: {', '.join(frameworks)}
            
            Provide risk assessment including:
            1. Critical compliance gaps
            2. Risk severity levels
            3. Regulatory implications
            4. Remediation priorities
            5. Timeline recommendations
            6. Resource requirements
            
            Focus on actionable compliance improvements.
            """
            
            assessment = await self.generate_response(prompt, expert_mode="safety_validator")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Error assessing compliance risks: {e}")
            return f"Compliance risk assessment failed: {str(e)}"
    
    async def generate_clarification(self, user_input: str, detected_intent: str, 
                                   confidence: float) -> str:
        """
        Generate clarification questions for ambiguous requests
        """
        try:
            prompt = f"""
            The user made this request: "{user_input}"
            
            I detected the intent as: {detected_intent}
            But my confidence is only: {confidence:.1%}
            
            Generate 2-3 specific clarification questions to help understand:
            1. What exactly they want to do
            2. Which databases/tables are involved
            3. Any specific requirements or constraints
            
            Make the questions natural and helpful, not technical jargon.
            """
            
            clarification = await self.generate_response(prompt, expert_mode="database_expert")
            return clarification
            
        except Exception as e:
            logger.error(f"❌ Error generating clarification: {e}")
            return "Could you please provide more details about what you'd like to do?"
    
    async def generate_sql_query(self, natural_language_request: str, 
                               database_schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate SQL queries from natural language descriptions
        """
        try:
            schema_info = ""
            if database_schema:
                schema_info = f"\nDATABASE SCHEMA: {database_schema}"
            
            prompt = f"""
            Convert this natural language request into a SQL query:
            
            REQUEST: "{natural_language_request}"
            {schema_info}
            
            Provide response in JSON format:
            {{
                "sql_query": "SELECT statement here",
                "explanation": "What this query does",
                "assumptions": ["assumption1", "assumption2"],
                "safety_level": "safe|caution|dangerous",
                "estimated_impact": "description of what this query will do"
            }}
            
            Ensure the query is safe and follows best practices.
            """
            
            response = await self.generate_response(prompt, expert_mode="database_expert")
            
            try:
                import json
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                return {
                    "sql_query": "-- Unable to generate query",
                    "explanation": "Failed to parse AI response",
                    "assumptions": [],
                    "safety_level": "dangerous",
                    "estimated_impact": "Unknown impact"
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating SQL query: {e}")
            return {
                "sql_query": f"-- Error: {str(e)}",
                "explanation": "SQL generation failed",
                "assumptions": [],
                "safety_level": "dangerous",
                "estimated_impact": "Cannot determine impact"
            }
    
    async def generate_database_recommendations(self, context: Dict[str, Any]) -> str:
        """
        Generate database recommendations based on context
        """
        try:
            prompt = f"""
            Based on this database context, provide recommendations:
            
            CONTEXT: {context}
            
            Provide recommendations for:
            1. Performance improvements
            2. Security enhancements
            3. Backup and recovery strategies
            4. Monitoring and alerting
            5. Cost optimization
            6. Maintenance procedures
            
            Prioritize recommendations by impact and effort required.
            """
            
            recommendations = await self.generate_response(prompt, expert_mode="database_expert")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return f"Recommendations generation failed: {str(e)}"
    
    async def validate_database_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate database configuration for best practices
        """
        try:
            prompt = f"""
            Validate this database configuration:
            
            CONFIGURATION: {config}
            
            Check for:
            1. Security best practices
            2. Performance optimization
            3. Backup configuration
            4. Network security
            5. Resource allocation
            6. Compliance requirements
            
            Respond in JSON format:
            {{
                "validation_score": 85,
                "issues_found": [
                    {{"severity": "high", "issue": "description", "recommendation": "fix"}},
                    {{"severity": "medium", "issue": "description", "recommendation": "fix"}}
                ],
                "best_practices": ["practice1", "practice2"],
                "security_concerns": ["concern1", "concern2"],
                "overall_assessment": "description"
            }}
            """
            
            response = await self.generate_response(prompt, expert_mode="safety_validator")
            
            try:
                import json
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                return {
                    "validation_score": 0,
                    "issues_found": [{"severity": "high", "issue": "Validation failed", "recommendation": "Manual review required"}],
                    "best_practices": [],
                    "security_concerns": ["Unable to validate configuration"],
                    "overall_assessment": "Configuration validation failed"
                }
                
        except Exception as e:
            logger.error(f"❌ Error validating configuration: {e}")
            return {
                "validation_score": 0,
                "issues_found": [{"severity": "critical", "issue": f"Validation error: {str(e)}", "recommendation": "Manual review required"}],
                "best_practices": [],
                "security_concerns": ["Validation process failed"],
                "overall_assessment": "Unable to validate configuration due to error"
            }
    
    async def explain_database_concepts(self, concept: str, complexity_level: str = "intermediate") -> str:
        """
        Explain database concepts at different complexity levels
        """
        try:
            prompt = f"""
            Explain this database concept: "{concept}"
            
            Complexity level: {complexity_level} (beginner/intermediate/advanced)
            
            Include:
            1. Clear definition
            2. Why it's important
            3. Common use cases
            4. Best practices
            5. Related concepts
            6. Practical examples
            
            Adjust the explanation depth for the specified complexity level.
            """
            
            explanation = await self.generate_response(prompt, expert_mode="database_expert")
            return explanation
            
        except Exception as e:
            logger.error(f"❌ Error explaining concept: {e}")
            return f"Unable to explain concept '{concept}': {str(e)}"
    
    async def generate_troubleshooting_guide(self, issue_description: str, 
                                           database_type: str = "general") -> Dict[str, Any]:
        """
        Generate troubleshooting guide for database issues
        """
        try:
            prompt = f"""
            Generate a troubleshooting guide for this database issue:
            
            ISSUE: {issue_description}
            DATABASE TYPE: {database_type}
            
            Provide response in JSON format:
            {{
                "issue_category": "performance|connectivity|corruption|security",
                "likely_causes": ["cause1", "cause2"],
                "diagnostic_steps": [
                    {{"step": 1, "action": "description", "expected_result": "what to look for"}},
                    {{"step": 2, "action": "description", "expected_result": "what to look for"}}
                ],
                "resolution_steps": [
                    {{"priority": "high", "action": "what to do", "risk": "low|medium|high"}},
                    {{"priority": "medium", "action": "what to do", "risk": "low|medium|high"}}
                ],
                "prevention_measures": ["measure1", "measure2"],
                "escalation_criteria": "when to escalate"
            }}
            """
            
            response = await self.generate_response(prompt, expert_mode="database_expert")
            
            try:
                import json
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                return {
                    "issue_category": "unknown",
                    "likely_causes": ["Unable to determine"],
                    "diagnostic_steps": [{"step": 1, "action": "Manual investigation required", "expected_result": "Depends on specific issue"}],
                    "resolution_steps": [{"priority": "high", "action": "Contact database administrator", "risk": "low"}],
                    "prevention_measures": ["Regular monitoring and maintenance"],
                    "escalation_criteria": "If issue persists after initial investigation"
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating troubleshooting guide: {e}")
            return {
                "issue_category": "error",
                "likely_causes": [f"Troubleshooting generation failed: {str(e)}"],
                "diagnostic_steps": [{"step": 1, "action": "Manual investigation required", "expected_result": "Contact support"}],
                "resolution_steps": [{"priority": "high", "action": "Manual intervention required", "risk": "unknown"}],
                "prevention_measures": ["Ensure AI system is functioning properly"],
                "escalation_criteria": "Immediately - AI troubleshooting failed"
            }
    
    async def batch_analysis(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple AI requests in batch for efficiency
        """
        try:
            logger.info(f"🔄 Processing batch of {len(requests)} AI requests")
            
            # Process requests concurrently
            tasks = []
            for request in requests:
                if request["type"] == "intent_classification":
                    task = self.classify_database_intent(request["input"], request.get("context"))
                elif request["type"] == "safety_assessment":
                    task = self.assess_operation_safety(
                        request["operation"], 
                        request["resources"], 
                        request["impact"]
                    )
                elif request["type"] == "performance_analysis":
                    task = self.analyze_performance_data(request["data"], request.get("analysis_type"))
                elif request["type"] == "general_response":
                    task = self.generate_response(request["prompt"], request.get("context"))
                else:
                    task = asyncio.create_task(self._handle_unknown_request(request))
                
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    formatted_results.append({
                        "request_id": i,
                        "status": "error",
                        "error": str(result),
                        "result": None
                    })
                else:
                    formatted_results.append({
                        "request_id": i,
                        "status": "success",
                        "error": None,
                        "result": result
                    })
            
            logger.info(f"✅ Batch processing completed: {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error in batch analysis: {e}")
            return [{"status": "error", "error": str(e), "result": None} for _ in requests]
    
    async def _handle_unknown_request(self, request: Dict[str, Any]) -> str:
        """Handle unknown request types"""
        return f"Unknown request type: {request.get('type', 'undefined')}"
    
    # =============================================================================
    # SSP-SPECIFIC METHODS FOR UNIFIED RESPONSE
    # =============================================================================
    
    async def analyze_inventory_metadata(self, inventory_data: Dict[str, Any]) -> str:
        """
        Analyze inventory metadata specifically for SSP operations
        Generate insights from SSP API inventory responses
        """
        try:
            prompt = f"""
            Analyze this database inventory metadata from SSP API responses and provide insights:
            
            Inventory Data:
            {inventory_data}
            
            Please provide:
            1. Resource distribution analysis
            2. Health status trends
            3. Potential optimization opportunities
            4. Risk assessments
            5. Recommendations for SSP portal configurations
            
            Focus on actionable insights for SSP portal management.
            """
            
            result = await self.generate_response(prompt)
            logger.info("🤖 Generated SSP inventory metadata analysis")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing inventory metadata: {e}")
            return f"Error analyzing inventory metadata: {str(e)}"
    
    async def generate_unified_analysis(self, operation_summary: Dict[str, Any], 
                                      session_context: Dict[str, Any], 
                                      response_type: str) -> str:
        """
        Generate unified analysis combining multiple SSP operations
        Provides consolidated insights across SSP API interactions
        """
        try:
            prompt = f"""
            Generate a unified {response_type} analysis based on these SSP portal operations:
            
            Operation Summary:
            {operation_summary}
            
            Session Context:
            {session_context}
            
            Response Type: {response_type}
            
            Please provide:
            1. Overall operation assessment
            2. Cross-operation insights and patterns
            3. Performance and efficiency analysis
            4. Recommendations for future operations
            5. SSP portal optimization suggestions
            
            Format the response for {response_type} presentation with clear sections and actionable insights.
            """
            
            result = await self.generate_response(prompt)
            logger.info(f"🤖 Generated unified {response_type} analysis")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating unified analysis: {e}")
            return f"Error generating unified analysis: {str(e)}"
    
    async def create_ssp_workflow_recommendations(self, operation_history: List[Dict[str, Any]], 
                                                session_context: Dict[str, Any]) -> str:
        """
        Create workflow recommendations based on SSP operation patterns
        Suggest optimized workflows for recurring SSP operations
        """
        try:
            prompt = f"""
            Based on these SSP portal operation patterns, suggest optimized workflows:
            
            Operation History:
            {operation_history}
            
            Session Context:
            {session_context}
            
            Please provide:
            1. Workflow automation opportunities
            2. SSP API call optimization patterns
            3. Recommended operation sequences
            4. Error handling and retry strategies
            5. Performance improvement suggestions
            
            Focus on practical SSP portal workflow improvements.
            """
            
            result = await self.generate_response(prompt)
            logger.info("🤖 Generated SSP workflow recommendations")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error creating workflow recommendations: {e}")
            return f"Error creating workflow recommendations: {str(e)}"
    
    async def assess_ssp_operation_efficiency(self, operation_metrics: Dict[str, Any]) -> str:
        """
        Assess efficiency of SSP operations and suggest improvements
        """
        try:
            prompt = f"""
            Assess the efficiency of these SSP portal operations and suggest improvements:
            
            Operation Metrics:
            {operation_metrics}
            
            Please analyze:
            1. Response time patterns
            2. Error rates and types
            3. Resource utilization
            4. API endpoint performance
            5. Optimization opportunities
            
            Provide specific recommendations for improving SSP portal operations.
            """
            
            result = await self.generate_response(prompt)
            logger.info("🤖 Generated SSP operation efficiency assessment")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error assessing operation efficiency: {e}")
            return f"Error assessing operation efficiency: {str(e)}"
