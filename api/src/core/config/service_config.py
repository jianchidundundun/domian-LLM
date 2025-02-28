import yaml
from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ServiceConfig:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent.parent.parent / "config" / "services.yaml")
        self.config_path = config_path
        self.services = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load service configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('services', {})
        except Exception as e:
            logger.error(f"Failed to load service configuration: {str(e)}")
            return {}
            
    def get_service_config(self, service_type: str, domain: str) -> Dict[str, Any]:
        """Get configuration for specific service and domain"""
        try:
            return self.services.get(service_type, {}).get(domain, {})
        except Exception as e:
            logger.error(f"Failed to get service configuration: {str(e)}")
            return {}
            
    def get_all_services(self) -> Dict[str, Any]:
        """Get all service configurations"""
        return self.services 