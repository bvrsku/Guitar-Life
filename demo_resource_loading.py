#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Modern Resource Management for Guitar Life
Demonstrates replacing pkg_resources with importlib.resources and modern alternatives
"""

import sys
from pathlib import Path

# Suppress pygame's pkg_resources deprecation warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

# Add the current directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from resource_utils import ResourceManager, load_app_config, save_app_config

def demo_resource_loading():
    """Demonstrate modern resource loading techniques"""
    print("🎸 Guitar Life - Modern Resource Management Demo")
    print("=" * 50)
    
    # Initialize resource manager
    rm = ResourceManager()
    
    print(f"📁 Base path: {rm.base_path}")
    print()
    
    # Demo 1: Check if resources exist
    print("1. Checking for configuration files:")
    configs = ["app_config.json", "guitar_config.json", "runtime_state.json"]
    
    for config in configs:
        exists = rm.resource_exists(config)
        path = rm.get_resource_path(config)
        print(f"   {config}: {'✅ Found' if exists else '❌ Missing'}")
        if path:
            print(f"      → {path}")
    print()
    
    # Demo 2: Load configuration with fallbacks
    print("2. Loading application configuration:")
    app_config = load_app_config()
    print(f"   Config loaded: {bool(app_config)}")
    print(f"   Keys: {list(app_config.keys())}")
    print()
    
    # Demo 3: Create and save a sample configuration
    print("3. Creating sample configuration:")
    sample_config = {
        "app": {
            "name": "Guitar Life",
            "version": "1.0.0",
            "pygame_version": "2.6.1",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        },
        "audio": {
            "enabled": True,
            "sample_rate": 44100,
            "buffer_size": 1024
        },
        "visual": {
            "fullscreen": False,
            "width": 1920,
            "height": 1080,
            "fps": 60
        },
        "layers": {
            "max_layers": 5,
            "default_rule": "Conway",
            "layer_settings": []
        }
    }
    
    success = save_app_config(sample_config)
    print(f"   Sample config saved: {'✅ Success' if success else '❌ Failed'}")
    print()
    
    # Demo 4: Alternative to pkg_resources.resource_stream
    print("4. Modern alternatives to pkg_resources:")
    print("   ❌ Old way: pkg_resources.resource_stream(__name__, 'config.json')")
    print("   ✅ New way: importlib.resources (Python 3.9+)")
    print("   ✅ Fallback: Direct file operations with pathlib.Path")
    print()
    
    # Demo 5: Environment info
    print("5. Environment information:")
    print(f"   Python version: {sys.version}")
    print(f"   Working directory: {Path.cwd()}")
    print(f"   Script location: {Path(__file__).parent}")
    
    # Check if importlib.resources is available
    if sys.version_info >= (3, 9):
        print("   ✅ importlib.resources available (Python 3.9+)")
    else:
        print("   ⚠️  Python < 3.9, using fallback methods")
        try:
            import importlib_resources
            print("   ✅ importlib_resources backport available")
        except ImportError:
            print("   ❌ importlib_resources not available")

def demo_pygame_info():
    """Show pygame information"""
    try:
        import pygame
        print(f"\n🎮 Pygame Information:")
        print(f"   Version: {pygame.version.ver}")
        print(f"   SDL Version: {pygame.version.SDL}")
        
        # Initialize pygame to get more info
        pygame.init()
        print(f"   Audio frequency: {pygame.mixer.get_init()[0] if pygame.mixer.get_init() else 'Not initialized'}")
        print(f"   Display driver: {pygame.display.get_driver()}")
        pygame.quit()
        
    except ImportError:
        print("   ❌ Pygame not available")

if __name__ == "__main__":
    demo_resource_loading()
    demo_pygame_info()
    
    print("\n" + "=" * 50)
    print("💡 Tips for migrating from pkg_resources:")
    print("   1. Use importlib.resources for Python 3.9+")
    print("   2. Use pathlib.Path for file operations")
    print("   3. Implement fallbacks for older Python versions")
    print("   4. Consider using importlib_resources for compatibility")
    print("   5. Test resource loading in both development and packaged environments")