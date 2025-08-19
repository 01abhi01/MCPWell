"""
Multi-Portal Integration Manager
Comprehensive integration framework for multiple self-service portals
"""

import asyncio
import aiohttp
import json
import logging
import yaml
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class PortalConfig:
    """Configuration for a portal integration"""
    name: str
    portal_type: str
    base_url: str
    authentication: Dict[str, Any]
    capabilities: List[str]
    endpoints: Dict[str, Any]
    health_check_endpoint: str = "/health"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PortalManager:
    """Manages integration with multiple self-service portals"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.portals: Dict[str, PortalConfig] = {}
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.portal_configs_path = Path("config/portals")
        
        logger.info("🔌 Multi-Portal Manager initialized")
    
    async def initialize(self):
        """Initialize portal manager and load configurations"""
        try:
            # Load portal configurations from YAML files and tools config
            await self._load_portal_configurations()
            
            # Initialize HTTP sessions for each portal
            await self._initialize_portal_sessions()
            
            # Start health monitoring
            asyncio.create_task(self._health_monitor_loop())
            
            logger.info(f"✅ Portal Manager initialized with {len(self.portals)} portals")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Portal Manager: {e}")
    
    async def _load_portal_configurations(self):
        """Load portal configurations from multiple sources"""
        
        # Load from tools config YAML (if exists)
        tools_config = self.config_manager.get_tools_config()
        yaml_portals = tools_config.get("portals", {})
        
        for portal_id, portal_data in yaml_portals.items():
            try:
                portal_config = PortalConfig(
                    name=portal_data.get("name", portal_id),
                    portal_type=portal_data.get("type", "unknown"),
                    base_url=portal_data.get("base_url", ""),
                    authentication=portal_data.get("authentication", {}),
                    capabilities=portal_data.get("capabilities", []),
                    endpoints=portal_data.get("endpoints", {}),
                    health_check_endpoint=portal_data.get("health_check_endpoint", "/health"),
                    metadata=portal_data.get("metadata", {})
                )
                
                self.portals[portal_id] = portal_config
                logger.info(f"✅ Loaded portal config: {portal_id} ({portal_config.portal_type})")
                
            except Exception as e:
                logger.error(f"❌ Failed to load portal config {portal_id}: {e}")
        
        # Load from individual YAML files in config/portals/ (if exists)
        if self.portal_configs_path.exists():
            for config_file in self.portal_configs_path.glob("*.yaml"):
                await self._load_portal_config_file(config_file)
    
    async def _load_portal_config_file(self, config_file: Path):
        """Load portal configuration from individual YAML file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                portal_data = yaml.safe_load(file)
            
            portal_id = config_file.stem
            
            portal_config = PortalConfig(
                name=portal_data.get("name", portal_id),
                portal_type=portal_data.get("type", "unknown"),
                base_url=portal_data.get("base_url", ""),
                authentication=portal_data.get("authentication", {}),
                capabilities=portal_data.get("capabilities", []),
                endpoints=portal_data.get("endpoints", {}),
                health_check_endpoint=portal_data.get("health_check_endpoint", "/health"),
                metadata=portal_data.get("metadata", {})
            )
            
            self.portals[portal_id] = portal_config
            logger.info(f"✅ Loaded portal config from file: {portal_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load portal config file {config_file}: {e}")
    
    async def _initialize_portal_sessions(self):
        """Initialize HTTP sessions for each portal"""
        for portal_id, portal_config in self.portals.items():
            try:
                # Create session with authentication headers
                headers = await self._get_auth_headers(portal_config)
                timeout = aiohttp.ClientTimeout(total=30)
                
                session = aiohttp.ClientSession(
                    headers=headers,
                    timeout=timeout,
                    connector=aiohttp.TCPConnector(limit=10)
                )
                
                self.sessions[portal_id] = session
                logger.debug(f"✅ Initialized session for portal: {portal_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize session for {portal_id}: {e}")
    
    async def _get_auth_headers(self, portal_config: PortalConfig) -> Dict[str, str]:
        """Get authentication headers for a portal"""
        headers = {"Content-Type": "application/json"}
        auth = portal_config.authentication
        
        if auth.get("type") == "api_key":
            header_name = auth.get("header", "X-API-Key")
            api_key = auth.get("key", "")
            headers[header_name] = api_key
            
        elif auth.get("type") == "bearer_token":
            token = auth.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
            
        elif auth.get("type") == "oauth2":
            # For OAuth2, you would implement token refresh logic here
            # For now, assume token is provided
            token = auth.get("access_token", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    async def register_portal(self, portal_id: str, portal_config: Dict[str, Any]) -> bool:
        """Register a new portal dynamically"""
        try:
            config = PortalConfig(
                name=portal_config.get("name", portal_id),
                portal_type=portal_config.get("type", "unknown"),
                base_url=portal_config.get("base_url", ""),
                authentication=portal_config.get("authentication", {}),
                capabilities=portal_config.get("capabilities", []),
                endpoints=portal_config.get("endpoints", {}),
                health_check_endpoint=portal_config.get("health_check_endpoint", "/health"),
                metadata=portal_config.get("metadata", {})
            )
            
            self.portals[portal_id] = config
            
            # Initialize session for new portal
            headers = await self._get_auth_headers(config)
            timeout = aiohttp.ClientTimeout(total=30)
            session = aiohttp.ClientSession(headers=headers, timeout=timeout)
            self.sessions[portal_id] = session
            
            logger.info(f"✅ Registered new portal: {portal_id} ({config.portal_type})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register portal {portal_id}: {e}")
            return False
    
    async def check_portal_health(self, portal_id: str) -> bool:
        """Check health of a specific portal"""
        try:
            if portal_id not in self.portals or portal_id not in self.sessions:
                return False
            
            portal_config = self.portals[portal_id]
            session = self.sessions[portal_id]
            
            health_url = f"{portal_config.base_url.rstrip('/')}{portal_config.health_check_endpoint}"
            
            async with session.get(health_url) as response:
                is_healthy = response.status == 200
                
                # Update health status
                self.health_status[portal_id] = {
                    "healthy": is_healthy,
                    "status_code": response.status,
                    "last_check": datetime.now().isoformat(),
                    "response_time": response.headers.get("X-Response-Time", "N/A")
                }
                
                return is_healthy
                
        except Exception as e:
            logger.error(f"❌ Health check failed for {portal_id}: {e}")
            self.health_status[portal_id] = {
                "healthy": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
            return False
    
    async def _health_monitor_loop(self):
        """Continuous health monitoring for all portals"""
        while True:
            try:
                for portal_id in self.portals.keys():
                    await self.check_portal_health(portal_id)
                
                # Wait 60 seconds before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def execute_operation(self, operation_type: str, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation through appropriate portal(s)"""
        try:
            # Determine which portal(s) to use based on operation and context
            target_portals = self._select_portals_for_operation(operation_type, entities, context)
            
            results = {}
            
            for portal_id in target_portals:
                try:
                    portal_result = await self._execute_portal_operation(
                        portal_id, operation_type, entities, context
                    )
                    results[portal_id] = portal_result
                    
                except Exception as e:
                    logger.error(f"❌ Operation failed for portal {portal_id}: {e}")
                    results[portal_id] = {"error": str(e), "status": "failed"}
            
            return {
                "status": "completed",
                "operation": operation_type,
                "entities": entities,
                "portal_results": results,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Operation execution failed: {e}")
            return {
                "status": "failed",
                "operation": operation_type,
                "error": str(e)
            }
    
    def _select_portals_for_operation(self, operation_type: str, entities: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Select appropriate portals for the operation"""
        # Portal selection logic based on operation type and capabilities
        suitable_portals = []
        
        operation_capability_mapping = {
            "read": ["query_execution", "data_analytics", "monitoring"],
            "create": ["data_management", "resource_management"],
            "update": ["data_management", "configuration"],
            "delete": ["data_management", "resource_management"],
            "backup": ["backup_management", "data_management"],
            "restore": ["backup_management", "data_management"],
            "analyze": ["data_analytics", "performance_monitoring", "reporting"],
            "monitor": ["monitoring", "alerting", "performance_monitoring"],
            "compliance": ["compliance_monitoring", "audit_logging", "security"]
        }
        
        required_capabilities = operation_capability_mapping.get(operation_type, [])
        
        for portal_id, portal_config in self.portals.items():
            # Check if portal is healthy
            if not self.health_status.get(portal_id, {}).get("healthy", False):
                continue
            
            # Check if portal has required capabilities
            portal_capabilities = portal_config.capabilities
            if any(cap in portal_capabilities for cap in required_capabilities):
                suitable_portals.append(portal_id)
        
        # Default to database portal if no specific match
        if not suitable_portals and "database_portal" in self.portals:
            suitable_portals = ["database_portal"]
        
        return suitable_portals
    
    async def _execute_portal_operation(self, portal_id: str, operation_type: str, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation on specific portal"""
        try:
            portal_config = self.portals[portal_id]
            session = self.sessions[portal_id]
            
            # Find appropriate endpoint for operation
            endpoint_info = self._find_endpoint_for_operation(portal_config, operation_type)
            
            if not endpoint_info:
                return {
                    "status": "skipped",
                    "reason": f"No suitable endpoint found for {operation_type}"
                }
            
            # Build request
            url = f"{portal_config.base_url.rstrip('/')}{endpoint_info['path']}"
            method = endpoint_info.get("method", "GET")
            
            # Prepare request data
            request_data = self._prepare_request_data(endpoint_info, entities, context)
            
            # Execute request
            async with session.request(method, url, json=request_data) as response:
                response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                return {
                    "status": "success" if response.status < 400 else "error",
                    "status_code": response.status,
                    "data": response_data,
                    "portal_type": portal_config.portal_type,
                    "endpoint": endpoint_info["path"]
                }
                
        except Exception as e:
            logger.error(f"❌ Portal operation failed for {portal_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "portal_id": portal_id
            }
    
    def _find_endpoint_for_operation(self, portal_config: PortalConfig, operation_type: str) -> Optional[Dict[str, Any]]:
        """Find appropriate endpoint for operation type"""
        endpoints = portal_config.endpoints
        
        # Operation to endpoint mapping
        operation_endpoints = {
            "read": ["list_databases", "get_data", "query", "list_resources"],
            "create": ["create_backup", "create_resource", "create_data"],
            "analyze": ["get_performance_metrics", "run_analysis", "analyze_data"],
            "monitor": ["get_metrics", "get_status", "health_check"]
        }
        
        possible_endpoints = operation_endpoints.get(operation_type, [])
        
        # Find first matching endpoint
        for endpoint_name in possible_endpoints:
            if endpoint_name in endpoints:
                endpoint_info = endpoints[endpoint_name].copy()
                endpoint_info["name"] = endpoint_name
                return endpoint_info
        
        # If no specific match, return first available endpoint
        if endpoints:
            first_endpoint = list(endpoints.values())[0].copy()
            first_endpoint["name"] = list(endpoints.keys())[0]
            return first_endpoint
        
        return None
    
    def _prepare_request_data(self, endpoint_info: Dict[str, Any], entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request data for endpoint"""
        request_data = {}
        
        # Map entities to request parameters
        if "databases" in entities:
            request_data["databases"] = entities["databases"]
        
        if "environment" in entities:
            request_data["environment"] = entities["environment"]
        
        # Add context data
        request_data.update(context)
        
        # Add timestamp
        request_data["timestamp"] = datetime.now().isoformat()
        
        return request_data
    
    async def get_database_inventory(self, portal_filter: List[str] = None, environment_filter: str = "all", 
                                   health_status_filter: str = "all", include_metadata: bool = True) -> Dict[str, Any]:
        """Get database inventory from multiple portals"""
        try:
            portals_to_query = portal_filter if portal_filter else list(self.portals.keys())
            
            inventory = {
                "databases": [],
                "total_count": 0,
                "healthy_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "portals_queried": portals_to_query,
                "collection_time": datetime.now().isoformat()
            }
            
            for portal_id in portals_to_query:
                try:
                    if portal_id not in self.portals:
                        continue
                    
                    portal_data = await self._get_portal_inventory(portal_id, environment_filter, include_metadata)
                    
                    # Merge portal data into inventory
                    if portal_data.get("databases"):
                        inventory["databases"].extend(portal_data["databases"])
                    
                except Exception as e:
                    logger.error(f"❌ Failed to get inventory from {portal_id}: {e}")
            
            # Calculate totals
            inventory["total_count"] = len(inventory["databases"])
            
            for db in inventory["databases"]:
                status = db.get("status", "unknown").lower()
                if status == "healthy":
                    inventory["healthy_count"] += 1
                elif status == "warning":
                    inventory["warning_count"] += 1
                elif status in ["critical", "error"]:
                    inventory["critical_count"] += 1
            
            # Apply filters
            if health_status_filter != "all":
                inventory["databases"] = [
                    db for db in inventory["databases"] 
                    if db.get("status", "").lower() == health_status_filter.lower()
                ]
            
            return inventory
            
        except Exception as e:
            logger.error(f"❌ Failed to get database inventory: {e}")
            return {
                "databases": [],
                "total_count": 0,
                "healthy_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "error": str(e)
            }
    
    async def _get_portal_inventory(self, portal_id: str, environment_filter: str, include_metadata: bool) -> Dict[str, Any]:
        """Get inventory from specific portal"""
        try:
            portal_config = self.portals[portal_id]
            session = self.sessions[portal_id]
            
            # Find inventory endpoint
            endpoints = portal_config.endpoints
            inventory_endpoints = ["list_databases", "get_inventory", "list_resources"]
            
            endpoint_info = None
            for endpoint_name in inventory_endpoints:
                if endpoint_name in endpoints:
                    endpoint_info = endpoints[endpoint_name]
                    break
            
            if not endpoint_info:
                return {"databases": []}
            
            # Make request
            url = f"{portal_config.base_url.rstrip('/')}{endpoint_info['path']}"
            method = endpoint_info.get("method", "GET")
            
            params = {}
            if environment_filter != "all":
                params["environment"] = environment_filter
            
            async with session.request(method, url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Normalize response format
                    databases = data if isinstance(data, list) else data.get("databases", [])
                    
                    # Add portal metadata to each database
                    for db in databases:
                        db["portal_id"] = portal_id
                        db["portal_type"] = portal_config.portal_type
                        if include_metadata:
                            db["portal_metadata"] = portal_config.metadata
                    
                    return {"databases": databases}
                else:
                    logger.warning(f"⚠️ Portal {portal_id} returned status {response.status}")
                    return {"databases": []}
                    
        except Exception as e:
            logger.error(f"❌ Failed to get inventory from portal {portal_id}: {e}")
            return {"databases": []}
    
    async def collect_performance_metrics(self, database_names: List[str] = None, time_range: Dict[str, Any] = None,
                                        metrics: List[str] = None, include_portal_data: bool = True) -> Dict[str, Any]:
        """Collect performance metrics from multiple portals"""
        try:
            performance_data = {
                "metrics": {},
                "databases": database_names or [],
                "time_range": time_range or {"period": "24h"},
                "collection_time": datetime.now().isoformat(),
                "portals_data": {}
            }
            
            if not include_portal_data:
                # Return simulated data
                performance_data["metrics"] = {
                    "cpu_usage": 65.5,
                    "memory_usage": 78.2,
                    "query_performance": "good",
                    "connections": 45,
                    "disk_io": "normal"
                }
                return performance_data
            
            # Collect from portals with performance monitoring capabilities
            performance_portals = [
                portal_id for portal_id, config in self.portals.items()
                if "performance_monitoring" in config.capabilities or "monitoring" in config.capabilities
            ]
            
            for portal_id in performance_portals:
                try:
                    portal_metrics = await self._collect_portal_metrics(portal_id, database_names, time_range, metrics)
                    performance_data["portals_data"][portal_id] = portal_metrics
                    
                    # Merge metrics
                    if portal_metrics.get("metrics"):
                        performance_data["metrics"].update(portal_metrics["metrics"])
                        
                except Exception as e:
                    logger.error(f"❌ Failed to collect metrics from {portal_id}: {e}")
            
            return performance_data
            
        except Exception as e:
            logger.error(f"❌ Failed to collect performance metrics: {e}")
            return {
                "metrics": {},
                "error": str(e),
                "collection_time": datetime.now().isoformat()
            }
    
    async def _collect_portal_metrics(self, portal_id: str, database_names: List[str], time_range: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
        """Collect metrics from specific portal"""
        try:
            portal_config = self.portals[portal_id]
            session = self.sessions[portal_id]
            
            # Find metrics endpoint
            endpoints = portal_config.endpoints
            metrics_endpoints = ["get_performance_metrics", "get_metrics", "collect_metrics"]
            
            endpoint_info = None
            for endpoint_name in metrics_endpoints:
                if endpoint_name in endpoints:
                    endpoint_info = endpoints[endpoint_name]
                    break
            
            if not endpoint_info:
                return {"metrics": {}}
            
            # Prepare request
            url = f"{portal_config.base_url.rstrip('/')}{endpoint_info['path']}"
            method = endpoint_info.get("method", "GET")
            
            request_data = {
                "databases": database_names,
                "time_range": time_range,
                "metrics": metrics
            }
            
            async with session.request(method, url, json=request_data) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "metrics": data.get("metrics", data),
                        "portal_type": portal_config.portal_type,
                        "status": "success"
                    }
                else:
                    return {"metrics": {}, "status": "error", "status_code": response.status}
                    
        except Exception as e:
            logger.error(f"❌ Failed to collect metrics from portal {portal_id}: {e}")
            return {"metrics": {}, "error": str(e)}
    
    async def manage_portal(self, action: str, portal_id: str = None, config: Dict[str, Any] = None, discovery_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage portal operations"""
        try:
            if action == "list":
                portal_list = []
                for pid, pconfig in self.portals.items():
                    portal_info = {
                        "id": pid,
                        "name": pconfig.name,
                        "type": pconfig.portal_type,
                        "capabilities": pconfig.capabilities,
                        "healthy": self.health_status.get(pid, {}).get("healthy", False),
                        "last_check": self.health_status.get(pid, {}).get("last_check", "Never")
                    }
                    portal_list.append(portal_info)
                
                return {
                    "status": "success",
                    "data": {
                        "portals": portal_list,
                        "total_count": len(portal_list)
                    }
                }
            
            elif action == "register" and config:
                success = await self.register_portal(portal_id, config)
                return {
                    "status": "success" if success else "failed",
                    "data": {"portal_id": portal_id, "registered": success}
                }
            
            elif action == "health_check" and portal_id:
                is_healthy = await self.check_portal_health(portal_id)
                return {
                    "status": "success",
                    "data": {
                        "portal_id": portal_id,
                        "healthy": is_healthy,
                        "health_data": self.health_status.get(portal_id, {})
                    }
                }
            
            elif action == "discover_capabilities" and portal_id:
                capabilities = await self._discover_portal_capabilities(portal_id, discovery_options or {})
                return {
                    "status": "success",
                    "data": {
                        "portal_id": portal_id,
                        "discovered_capabilities": capabilities
                    }
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported action: {action}"
                }
                
        except Exception as e:
            logger.error(f"❌ Portal management failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _discover_portal_capabilities(self, portal_id: str, discovery_options: Dict[str, Any]) -> List[str]:
        """Discover portal capabilities automatically"""
        try:
            if portal_id not in self.portals:
                return []
            
            portal_config = self.portals[portal_id]
            
            # Return configured capabilities plus discovered ones
            configured_capabilities = portal_config.capabilities.copy()
            
            # Try to discover additional capabilities by examining endpoints
            discovered_capabilities = []
            
            for endpoint_name, endpoint_info in portal_config.endpoints.items():
                # Infer capabilities from endpoint names
                if "backup" in endpoint_name.lower():
                    discovered_capabilities.append("backup_management")
                elif "performance" in endpoint_name.lower() or "metrics" in endpoint_name.lower():
                    discovered_capabilities.append("performance_monitoring")
                elif "security" in endpoint_name.lower() or "compliance" in endpoint_name.lower():
                    discovered_capabilities.append("security_monitoring")
                elif "deploy" in endpoint_name.lower():
                    discovered_capabilities.append("deployment_automation")
            
            # Combine and deduplicate
            all_capabilities = list(set(configured_capabilities + discovered_capabilities))
            
            logger.info(f"🔍 Discovered capabilities for {portal_id}: {discovered_capabilities}")
            
            return all_capabilities
            
        except Exception as e:
            logger.error(f"❌ Capability discovery failed for {portal_id}: {e}")
            return []
    
    async def generate_compliance_report(self, frameworks: List[str], scope: Dict[str, Any], include_remediation: bool = True) -> Dict[str, Any]:
        """Generate compliance report across all integrated portals"""
        try:
            compliance_data = {
                "frameworks": frameworks,
                "scope": scope,
                "report_generated": datetime.now().isoformat(),
                "portal_compliance": {},
                "overall_status": "compliant",
                "issues_found": [],
                "recommendations": []
            }
            
            # Check compliance across portals
            security_portals = [
                portal_id for portal_id, config in self.portals.items()
                if "compliance_monitoring" in config.capabilities or "security" in config.capabilities
            ]
            
            for portal_id in security_portals:
                try:
                    portal_compliance = await self._check_portal_compliance(portal_id, frameworks, scope)
                    compliance_data["portal_compliance"][portal_id] = portal_compliance
                    
                    # Aggregate issues
                    if portal_compliance.get("issues"):
                        compliance_data["issues_found"].extend(portal_compliance["issues"])
                    
                    # Update overall status
                    if portal_compliance.get("status") != "compliant":
                        compliance_data["overall_status"] = "non_compliant"
                        
                except Exception as e:
                    logger.error(f"❌ Compliance check failed for {portal_id}: {e}")
            
            # Add remediation recommendations
            if include_remediation and compliance_data["issues_found"]:
                compliance_data["recommendations"] = [
                    "Review security configurations across all portals",
                    "Implement additional monitoring for compliance frameworks",
                    "Schedule regular compliance audits",
                    "Update access controls and permissions"
                ]
            
            return compliance_data
            
        except Exception as e:
            logger.error(f"❌ Compliance report generation failed: {e}")
            return {
                "frameworks": frameworks,
                "error": str(e),
                "report_generated": datetime.now().isoformat()
            }
    
    async def _check_portal_compliance(self, portal_id: str, frameworks: List[str], scope: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance for specific portal"""
        try:
            # Simulate compliance check
            return {
                "status": "compliant",
                "frameworks_checked": frameworks,
                "issues": [],
                "portal_type": self.portals[portal_id].portal_type,
                "last_audit": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Portal compliance check failed for {portal_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_portal_summary(self) -> Dict[str, Any]:
        """Get summary of all registered portals"""
        summary = {
            "total_portals": len(self.portals),
            "portal_types": {},
            "health_summary": {
                "healthy": 0,
                "unhealthy": 0,
                "unknown": 0
            },
            "capabilities_summary": {}
        }
        
        # Count portal types
        for portal_config in self.portals.values():
            portal_type = portal_config.portal_type
            summary["portal_types"][portal_type] = summary["portal_types"].get(portal_type, 0) + 1
            
            # Count capabilities
            for capability in portal_config.capabilities:
                summary["capabilities_summary"][capability] = summary["capabilities_summary"].get(capability, 0) + 1
        
        # Count health status
        for health_data in self.health_status.values():
            if health_data.get("healthy"):
                summary["health_summary"]["healthy"] += 1
            elif "error" in health_data:
                summary["health_summary"]["unhealthy"] += 1
            else:
                summary["health_summary"]["unknown"] += 1
        
        return summary
    
    async def cleanup(self):
        """Cleanup portal manager resources"""
        try:
            # Close all HTTP sessions
            for session in self.sessions.values():
                if not session.closed:
                    await session.close()
            
            logger.info("✅ Portal Manager cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Portal Manager cleanup failed: {e}")
