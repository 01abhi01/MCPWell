"""
Configuration Manager with YAML Tool Definitions Support
Manages all configuration including YAML-based tool definitions
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management with YAML tool definitions support"""
    
    def __init__(self, tools_config_path: str = "tools_config.yaml"):
        self.tools_config_path = Path(tools_config_path)
        self.config = {}
        self.tools_config = {}
        
        # Load environment variables
        self._load_env_config()
        
        # Load tool definitions from YAML
        self._load_tools_config()
        
        logger.info("⚙️ Configuration Manager initialized with YAML tool definitions")
    
    def _load_env_config(self):
        """Load configuration from environment variables"""
        self.config = {
            "llm": {
                "gemini": {
                    "api_key": os.getenv("GEMINI_API_KEY", ""),
                    "model": os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
                    "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.3")),
                    "max_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "4096"))
                }
            },
            "database": {
                "default_timeout": int(os.getenv("DB_TIMEOUT", "30")),
                "max_connections": int(os.getenv("DB_MAX_CONNECTIONS", "10"))
            },
            "portal": {
                "health_check_interval": int(os.getenv("PORTAL_HEALTH_INTERVAL", "60")),
                "request_timeout": int(os.getenv("PORTAL_TIMEOUT", "30"))
            },
            "security": {
                "require_confirmation": os.getenv("REQUIRE_CONFIRMATION", "true").lower() == "true",
                "audit_logging": os.getenv("AUDIT_LOGGING", "true").lower() == "true"
            }
        }
    
    def _load_tools_config(self):
        """Load tool definitions from YAML file"""
        try:
            if self.tools_config_path.exists():
                with open(self.tools_config_path, 'r', encoding='utf-8') as file:
                    self.tools_config = yaml.safe_load(file)
                logger.info(f"📋 Loaded tool definitions from {self.tools_config_path}")
            else:
                logger.warning(f"⚠️ Tools config file not found: {self.tools_config_path}")
                self.tools_config = {"tools": {}}
        except Exception as e:
            logger.error(f"❌ Failed to load tools config: {e}")
            self.tools_config = {"tools": {}}
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.config.get("llm", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.config.get("database", {})
    
    def get_portal_config(self) -> Dict[str, Any]:
        """Get portal configuration"""
        return self.config.get("portal", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.config.get("security", {})
    
    def get_tools_config(self) -> Dict[str, Any]:
        """Get tools configuration from YAML"""
        return self.tools_config
    
    def get_tool_definition(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get specific tool definition from YAML"""
        return self.tools_config.get("tools", {}).get(tool_name)
    
    def get_all_tool_names(self) -> List[str]:
        """Get list of all tool names defined in YAML"""
        return list(self.tools_config.get("tools", {}).keys())
    
    def reload_tools_config(self):
        """Reload tool definitions from YAML file"""
        self._load_tools_config()
        logger.info("🔄 Tools configuration reloaded from YAML")
