# src/utils/config.py
"""
Configuration utilities for the orchestration spine.
"""

import os
from typing import Any, Dict, Optional
from pathlib import Path


class Config:
    """
    Simple configuration manager for the orchestration spine.
    """
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration with defaults and override from config_dict.
        
        Args:
            config_dict: Optional dictionary with configuration overrides
        """
        # Default configuration
        self._config = {
            # Storage paths
            "checkpoint_storage_path": "./checkpoints",
            "handoff_storage_path": "./handoffs",
            "decision_log_storage_path": "./decision_logs",
            
            # Execution settings
            "default_timeout_seconds": 3600,  # 1 hour
            "default_max_attempts": 3,
            "default_backoff_seconds": 5,
            
            # Checkpointing
            "checkpoint_interval_seconds": 300,  # 5 minutes
            "checkpoint_retention_count": 10,
            
            # Feature flags
            "enable_async_checkpointing": True,
            "enable_parameter_substitution": True,
        }
        
        # Override with provided config
        if config_dict:
            self._config.update(config_dict)
        
        # Override from environment variables
        self._load_from_env()
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mapping = {
            "ORCHESTRATION_CHECKPOINT_PATH": "checkpoint_storage_path",
            "ORCHESTRATION_HANDOFF_PATH": "handoff_storage_path",
            "ORCHESTRATION_DECISION_LOG_PATH": "decision_log_storage_path",
            "ORCHESTRATION_DEFAULT_TIMEOUT": "default_timeout_seconds",
            "ORCHESTRATION_MAX_ATTEMPTS": "default_max_attempts",
            "ORCHESTRATION_BACKOFF_SECONDS": "default_backoff_seconds",
            "ORCHESTRATION_CHECKPOINT_INTERVAL": "checkpoint_interval_seconds",
            "ORCHESTRATION_RETENTION_COUNT": "checkpoint_retention_count",
            "ORCHESTRATION_ASYNC_CHECKPOINTING": "enable_async_checkpointing",
            "ORCHESTRATION_PARAM_SUBSTITUTION": "enable_parameter_substitution",
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Try to convert to appropriate type
                if config_key in ["default_timeout_seconds", "default_max_attempts", 
                                "default_backoff_seconds", "checkpoint_interval_seconds",
                                "checkpoint_retention_count"]:
                    try:
                        self._config[config_key] = int(value)
                    except ValueError:
                        pass  # Keep default if conversion fails
                elif config_key in ["enable_async_checkpointing", "enable_parameter_substitution"]:
                    self._config[config_key] = value.lower() in ("true", "1", "yes", "on")
                else:
                    self._config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get a copy of the full configuration.
        
        Returns:
            Dictionary with all configuration values
        """
        return self._config.copy()


# Global configuration instance
config = Config()