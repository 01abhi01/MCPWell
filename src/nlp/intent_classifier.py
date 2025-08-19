"""
Enhanced Intent Classifier with LangChain Integration
AI-powered database intent classification and conversation management
"""

import asyncio
import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
import google.generativeai as genai

logger = logging.getLogger(__name__)

class DBIntent(Enum):
    """Database operation intent types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    BACKUP = "backup"
    RESTORE = "restore"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    MONITOR = "monitor"
    TROUBLESHOOT = "troubleshoot"
    COMPLIANCE = "compliance"
    MIGRATION = "migration"
    ADMINISTRATION = "administration"
    UNKNOWN = "unknown"

@dataclass
class IntentResult:
    """Result of intent classification"""
    intent: DBIntent
    confidence: float
    entities: Dict[str, Any]
    explanation: str
    requires_confirmation: bool = False
    suggested_actions: List[str] = None

class DatabaseIntentClassifier:
    """AI-powered intent classifier for database operations"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Intent patterns for hybrid classification
        self.intent_patterns = {
            DBIntent.CREATE: [
                "create", "make", "build", "establish", "set up", "initialize", "generate",
                "add", "insert", "new", "fresh", "start"
            ],
            DBIntent.READ: [
                "show", "list", "display", "get", "fetch", "retrieve", "view", "see",
                "find", "search", "query", "select", "check", "look"
            ],
            DBIntent.UPDATE: [
                "update", "modify", "change", "edit", "alter", "revise", "adjust",
                "fix", "correct", "improve", "enhance"
            ],
            DBIntent.DELETE: [
                "delete", "remove", "drop", "clear", "erase", "purge", "clean",
                "eliminate", "destroy", "wipe"
            ],
            DBIntent.BACKUP: [
                "backup", "copy", "save", "archive", "preserve", "snapshot",
                "dump", "export", "replicate"
            ],
            DBIntent.RESTORE: [
                "restore", "recover", "import", "load", "reinstate", "rollback",
                "revert", "undo", "bring back"
            ],
            DBIntent.ANALYZE: [
                "analyze", "examine", "study", "investigate", "review", "assess",
                "evaluate", "inspect", "performance", "statistics", "stats"
            ],
            DBIntent.OPTIMIZE: [
                "optimize", "improve", "enhance", "tune", "speed up", "accelerate",
                "efficiency", "performance", "faster", "better"
            ],
            DBIntent.MONITOR: [
                "monitor", "watch", "track", "observe", "supervise", "check",
                "status", "health", "alerts", "notifications"
            ],
            DBIntent.TROUBLESHOOT: [
                "troubleshoot", "debug", "diagnose", "fix", "solve", "resolve",
                "issue", "problem", "error", "bug"
            ],
            DBIntent.COMPLIANCE: [
                "compliance", "audit", "regulation", "policy", "security",
                "gdpr", "sox", "hipaa", "pci", "standards"
            ],
            DBIntent.MIGRATION: [
                "migrate", "move", "transfer", "relocate", "upgrade", "convert",
                "switch", "transition", "port"
            ],
            DBIntent.ADMINISTRATION: [
                "admin", "manage", "configure", "setup", "permissions", "users",
                "roles", "access", "security", "settings"
            ]
        }
        
        # High-risk operations requiring confirmation
        self.confirmation_required = {
            DBIntent.DELETE, DBIntent.UPDATE, DBIntent.RESTORE, 
            DBIntent.MIGRATION, DBIntent.ADMINISTRATION
        }
        
        logger.info("🧠 Database Intent Classifier initialized with Gemini LLM")
    
    async def classify_intent(self, user_input: str, context: Dict[str, Any] = None) -> IntentResult:
        """Classify user intent using hybrid approach (patterns + LLM)"""
        try:
            # First pass: Rule-based pattern matching
            pattern_result = self._classify_with_patterns(user_input)
            
            # Second pass: LLM-powered classification for ambiguous cases
            if pattern_result.confidence < 0.8:
                llm_result = await self._classify_with_llm(user_input, context)
                # Combine results, preferring LLM for low-confidence pattern matches
                if llm_result.confidence > pattern_result.confidence:
                    final_result = llm_result
                else:
                    final_result = pattern_result
            else:
                final_result = pattern_result
            
            # Add confirmation requirement
            final_result.requires_confirmation = (
                final_result.intent in self.confirmation_required and 
                final_result.confidence > 0.6
            )
            
            logger.info(f"🎯 Intent classified: {final_result.intent.value} (confidence: {final_result.confidence:.2f})")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Intent classification error: {e}")
            return IntentResult(
                intent=DBIntent.UNKNOWN,
                confidence=0.0,
                entities={},
                explanation=f"Error classifying intent: {str(e)}"
            )
    
    def _classify_with_patterns(self, user_input: str) -> IntentResult:
        """Rule-based intent classification using keyword patterns"""
        user_input_lower = user_input.lower()
        intent_scores = {}
        
        # Calculate pattern match scores
        for intent, patterns in self.intent_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                if pattern in user_input_lower:
                    score += 1
                    matched_patterns.append(pattern)
            
            if score > 0:
                intent_scores[intent] = {
                    'score': score / len(patterns),  # Normalize by pattern count
                    'matches': matched_patterns
                }
        
        # Find best match
        if not intent_scores:
            return IntentResult(
                intent=DBIntent.UNKNOWN,
                confidence=0.0,
                entities={},
                explanation="No pattern matches found"
            )
        
        best_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x]['score'])
        best_score = intent_scores[best_intent]['score']
        matched_patterns = intent_scores[best_intent]['matches']
        
        # Extract basic entities
        entities = self._extract_entities(user_input)
        
        return IntentResult(
            intent=best_intent,
            confidence=min(best_score * 2, 1.0),  # Scale to 0-1 range
            entities=entities,
            explanation=f"Pattern-based classification. Matched keywords: {', '.join(matched_patterns)}"
        )
    
    async def _classify_with_llm(self, user_input: str, context: Dict[str, Any] = None) -> IntentResult:
        """LLM-powered intent classification for complex cases"""
        try:
            # Prepare context information
            context_info = ""
            if context:
                context_info = f"Context: {context.get('previous_operations', 'None')}\n"
            
            # Create comprehensive prompt
            prompt = f"""
You are an expert database administrator and intent classifier. 
Analyze the following user request and classify it into one of these database operation intents:

INTENTS:
- CREATE: Creating new databases, tables, indexes, or data
- READ: Querying, viewing, or retrieving data/information  
- UPDATE: Modifying existing data or structure
- DELETE: Removing data, tables, or databases
- BACKUP: Creating backups, snapshots, or copies
- RESTORE: Restoring from backups or recovering data
- ANALYZE: Performance analysis, statistics, or data examination
- OPTIMIZE: Performance tuning, optimization, or improvements
- MONITOR: Monitoring health, status, or setting up alerts
- TROUBLESHOOT: Debugging, fixing issues, or problem-solving
- COMPLIANCE: Audit, security, or regulatory compliance
- MIGRATION: Moving, upgrading, or transferring databases
- ADMINISTRATION: User management, permissions, or configuration
- UNKNOWN: Cannot determine intent

{context_info}
USER REQUEST: "{user_input}"

Provide your analysis in this exact format:
INTENT: [intent_name]
CONFIDENCE: [0.0-1.0]
ENTITIES: {{
  "databases": ["db1", "db2"],
  "tables": ["table1"], 
  "operations": ["specific_ops"],
  "time_period": "timeframe",
  "environment": "env_type"
}}
EXPLANATION: [brief explanation of your reasoning]
SUGGESTED_ACTIONS: ["action1", "action2"]
"""
            
            response = await self.model.generate_content_async(prompt)
            return self._parse_llm_response(response.text)
            
        except Exception as e:
            logger.error(f"❌ LLM classification error: {e}")
            return IntentResult(
                intent=DBIntent.UNKNOWN,
                confidence=0.0,
                entities={},
                explanation=f"LLM classification failed: {str(e)}"
            )
    
    def _parse_llm_response(self, response_text: str) -> IntentResult:
        """Parse LLM response into IntentResult"""
        try:
            lines = response_text.strip().split('\n')
            intent_str = ""
            confidence = 0.0
            entities = {}
            explanation = ""
            suggested_actions = []
            
            for line in lines:
                line = line.strip()
                if line.startswith("INTENT:"):
                    intent_str = line.replace("INTENT:", "").strip()
                elif line.startswith("CONFIDENCE:"):
                    confidence = float(line.replace("CONFIDENCE:", "").strip())
                elif line.startswith("ENTITIES:"):
                    # Simple entity parsing (could be enhanced)
                    entities_str = line.replace("ENTITIES:", "").strip()
                    try:
                        entities = eval(entities_str)  # Note: Use json.loads in production
                    except:
                        entities = {}
                elif line.startswith("EXPLANATION:"):
                    explanation = line.replace("EXPLANATION:", "").strip()
                elif line.startswith("SUGGESTED_ACTIONS:"):
                    actions_str = line.replace("SUGGESTED_ACTIONS:", "").strip()
                    try:
                        suggested_actions = eval(actions_str)
                    except:
                        suggested_actions = []
            
            # Convert intent string to enum
            try:
                intent = DBIntent(intent_str.lower())
            except ValueError:
                intent = DBIntent.UNKNOWN
                confidence = 0.0
            
            return IntentResult(
                intent=intent,
                confidence=confidence,
                entities=entities,
                explanation=explanation,
                suggested_actions=suggested_actions
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing LLM response: {e}")
            return IntentResult(
                intent=DBIntent.UNKNOWN,
                confidence=0.0,
                entities={},
                explanation=f"Failed to parse LLM response: {str(e)}"
            )
    
    def _extract_entities(self, user_input: str) -> Dict[str, Any]:
        """Extract basic entities from user input using simple patterns"""
        entities = {
            "databases": [],
            "tables": [],
            "operations": [],
            "time_period": None,
            "environment": None
        }
        
        user_input_lower = user_input.lower()
        
        # Environment detection
        if any(env in user_input_lower for env in ["prod", "production"]):
            entities["environment"] = "production"
        elif any(env in user_input_lower for env in ["dev", "development"]):
            entities["environment"] = "development"
        elif any(env in user_input_lower for env in ["test", "testing", "stage", "staging"]):
            entities["environment"] = "staging"
        
        # Time period detection
        time_patterns = {
            "today": "1d",
            "yesterday": "1d",
            "week": "7d",
            "month": "30d",
            "year": "365d",
            "hour": "1h"
        }
        
        for pattern, period in time_patterns.items():
            if pattern in user_input_lower:
                entities["time_period"] = period
                break
        
        # Simple database/table name extraction (could be enhanced with NER)
        words = user_input.split()
        for i, word in enumerate(words):
            # Look for database-like names (simple heuristic)
            if (word.endswith("_db") or word.endswith("_database") or 
                (i > 0 and words[i-1].lower() in ["database", "db", "table"])):
                if word.endswith("_db") or word.endswith("_database"):
                    entities["databases"].append(word)
                else:
                    entities["tables"].append(word)
        
        return entities

class ConversationFlow:
    """Manages conversation context and multi-turn interactions"""
    
    def __init__(self, intent_classifier: DatabaseIntentClassifier):
        self.intent_classifier = intent_classifier
        self.sessions = {}
        self.memory_window = 10
        
        logger.info("💬 Conversation Flow Manager initialized")
    
    async def process_turn(self, session_id: str, user_input: str, intent_result: IntentResult) -> Dict[str, Any]:
        """Process a conversation turn and update session state"""
        try:
            # Initialize session if new
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "memory": ConversationBufferWindowMemory(k=self.memory_window),
                    "context": {},
                    "pending_operations": [],
                    "last_intent": None
                }
            
            session = self.sessions[session_id]
            
            # Add to conversation memory
            session["memory"].chat_memory.add_user_message(user_input)
            
            # Update context
            session["context"].update({
                "last_user_input": user_input,
                "last_intent": intent_result.intent.value,
                "last_entities": intent_result.entities,
                "confidence": intent_result.confidence
            })
            
            # Handle conversation flow based on intent
            flow_response = await self._handle_conversation_flow(session, intent_result)
            
            # Add AI response to memory
            session["memory"].chat_memory.add_ai_message(flow_response["response"])
            
            return flow_response
            
        except Exception as e:
            logger.error(f"❌ Error processing conversation turn: {e}")
            return {
                "response": f"Error processing conversation: {str(e)}",
                "context": {},
                "next_actions": []
            }
    
    async def _handle_conversation_flow(self, session: Dict[str, Any], intent_result: IntentResult) -> Dict[str, Any]:
        """Handle conversation flow logic based on intent and context"""
        
        context = session["context"]
        pending_ops = session["pending_operations"]
        
        # Check for confirmation responses
        if (context.get("waiting_for_confirmation") and 
            intent_result.intent in [DBIntent.CREATE, DBIntent.READ] and
            any(word in intent_result.explanation.lower() for word in ["yes", "confirm", "proceed"])):
            
            # User confirmed operation
            pending_op = pending_ops[-1] if pending_ops else {}
            response = f"✅ Confirmed! Proceeding with {pending_op.get('operation', 'operation')}..."
            context["waiting_for_confirmation"] = False
            
            return {
                "response": response,
                "context": context,
                "next_actions": ["execute_operation"],
                "confirmed_operation": pending_op
            }
        
        # Check for clarification needs
        if intent_result.confidence < 0.7:
            clarification_questions = self._generate_clarification_questions(intent_result)
            context["waiting_for_clarification"] = True
            
            return {
                "response": f"🤔 I need clarification: {clarification_questions}",
                "context": context,
                "next_actions": ["await_clarification"]
            }
        
        # Add to pending operations if confirmation required
        if intent_result.requires_confirmation:
            operation = {
                "intent": intent_result.intent.value,
                "entities": intent_result.entities,
                "timestamp": "now",
                "risk_level": self._assess_risk_level(intent_result)
            }
            pending_ops.append(operation)
            context["waiting_for_confirmation"] = True
            
            return {
                "response": f"⚠️ This operation requires confirmation. {intent_result.explanation}",
                "context": context,
                "next_actions": ["await_confirmation"],
                "pending_operation": operation
            }
        
        # Normal flow - operation can proceed
        return {
            "response": f"✅ Processing {intent_result.intent.value} operation: {intent_result.explanation}",
            "context": context,
            "next_actions": ["execute_operation"],
            "ready_to_execute": True
        }
    
    def _generate_clarification_questions(self, intent_result: IntentResult) -> str:
        """Generate clarification questions based on ambiguous intent"""
        
        questions = []
        
        if not intent_result.entities.get("databases"):
            questions.append("Which database(s) are you referring to?")
        
        if not intent_result.entities.get("environment"):
            questions.append("Which environment (development/staging/production)?")
        
        if intent_result.intent == DBIntent.UNKNOWN:
            questions.append("What specific operation do you want to perform?")
        
        return " ".join(questions) if questions else "Could you please provide more details?"
    
    def _assess_risk_level(self, intent_result: IntentResult) -> str:
        """Assess risk level of operation"""
        
        high_risk_intents = {DBIntent.DELETE, DBIntent.MIGRATION, DBIntent.ADMINISTRATION}
        medium_risk_intents = {DBIntent.UPDATE, DBIntent.RESTORE}
        
        if intent_result.intent in high_risk_intents:
            return "high"
        elif intent_result.intent in medium_risk_intents:
            return "medium"
        else:
            return "low"
    
    async def handle_conversation_action(self, session_id: str, action: str, message: str, 
                                       context: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Handle specific conversation actions"""
        try:
            if action == "start":
                return {"response": "👋 Hello! I'm ready to help with database operations.", "state": "active"}
            elif action == "continue":
                intent_result = await self.intent_classifier.classify_intent(message, context)
                return await self.process_turn(session_id, message, intent_result)
            elif action == "clarify":
                return {"response": "🤔 Please provide more specific details about your request.", "state": "awaiting_clarification"}
            elif action == "confirm":
                return {"response": "✅ Operation confirmed and will proceed.", "state": "confirmed"}
            elif action == "cancel":
                if session_id in self.sessions:
                    self.sessions[session_id]["pending_operations"] = []
                return {"response": "❌ Operation cancelled.", "state": "cancelled"}
            elif action == "summarize":
                summary = self._generate_session_summary(session_id)
                return {"response": f"📋 Session Summary:\n{summary}", "state": "summarized"}
            else:
                return {"response": f"❓ Unknown conversation action: {action}", "state": "error"}
                
        except Exception as e:
            logger.error(f"❌ Error handling conversation action: {e}")
            return {"response": f"Error: {str(e)}", "state": "error"}
    
    def _generate_session_summary(self, session_id: str) -> str:
        """Generate summary of conversation session"""
        if session_id not in self.sessions:
            return "No session found."
        
        session = self.sessions[session_id]
        context = session["context"]
        pending_ops = session["pending_operations"]
        
        summary_parts = []
        
        if context.get("last_intent"):
            summary_parts.append(f"Last intent: {context['last_intent']}")
        
        if pending_ops:
            summary_parts.append(f"Pending operations: {len(pending_ops)}")
        
        if context.get("last_entities"):
            entities = context["last_entities"]
            if entities.get("databases"):
                summary_parts.append(f"Databases involved: {', '.join(entities['databases'])}")
        
        return "; ".join(summary_parts) if summary_parts else "No significant activity."
