#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from pathlib import Path
from typing import Optional, Any, Dict

if sys.version_info >= (3, 9):
    from importlib import resources
    
class ResourceManager:
    """resource manager using importlib.resources"""
    
    def __init__(self, package_name: str = __name__):
        self.package_name = package_name
        self.base_path = Path(__file__).parent if "__file__" in globals() else Path(".")
    
    def load_json_config(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load JSON configuration"""
        try:
            # Try modern importlib.resources first
            if resources and sys.version_info >= (3, 9):
                try:
                    from importlib import resources as res
                    with res.open_text(self.package_name, filename, encoding='utf-8') as f:
                        return json.load(f)
                except (FileNotFoundError, AttributeError):
                    pass
            
            #Fallback to file system
            config_paths = [
                self.base_path / filename,
                self.base_path / "config" / filename,
                Path(filename)
            ]
            
            for path in config_paths:
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            print(f"Warning: Config file {filename} not found")
            return None
            
        except Exception as e:
            print(f"Error loading config {filename}: {e}")
            return None
    
    def save_json_config(self, filename: str, data: Dict[str, Any]) -> bool:
        """Save JSON configuration file"""
        try:
            # Ensure config directory exists
            config_dir = self.base_path / "config"
            config_dir.mkdir(exist_ok=True)
            
            # Save to config directory
            config_path = config_dir / filename
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Config saved to {config_path}")
            return True
            
        except Exception as e:
            print(f"Error saving config {filename}: {e}")
            return False
    
    def resource_exists(self, filename: str) -> bool:
        """Check if a resource exists using modern methods"""
        if resources and sys.version_info >= (3, 9):
            try:
                from importlib import resources as res
                return res.is_resource(self.package_name, filename)
            except (FileNotFoundError, AttributeError):
                pass
        
        # Fallback to filesystem check
        return (self.base_path / filename).exists()
    
    def get_resource_path(self, filename: str) -> Optional[Path]:
        """Get the path to a resource file"""
        # Check common locations
        paths_to_check = [
            self.base_path / filename,
            self.base_path / "config" / filename,
            self.base_path / "presets" / filename,
            self.base_path / "palettes" / filename,
            Path(filename)
        ]
        
        for path in paths_to_check:
            if path.exists():
                return path
        
        return None

#Global resource manager instance
resource_manager = ResourceManager()

def load_app_config() -> Dict[str, Any]:
    """Load application configuration"""
    config = resource_manager.load_json_config("app_config.json")
    if config is None:
        # Return default configuration
        return {
            "layers": {
                "layer_settings": [],
                "max_layers": 5
            },
            "audio": {
                "enabled": True,
                "device": None
            },
            "visual": {
                "fullscreen": False,
                "resolution": [1920, 1080]
            }
        }
    return config

def save_app_config(config: Dict[str, Any]) -> bool:
    """Save application configuration"""
    return resource_manager.save_json_config("app_config.json", config)

def load_guitar_config() -> Dict[str, Any]:
    """Load guitar-specific configuration"""
    config = resource_manager.load_json_config("guitar_config.json")
    if config is None:
        # Return default guitar configuration
        return {
            "tuning": ["E", "A", "D", "G", "B", "E"],
            "strings": 6,
            "frets": 24
        }
    return config

def save_guitar_config(config: Dict[str, Any]) -> bool:
    """Save guitar-specific configuration"""
    return resource_manager.save_json_config("guitar_config.json", config)
