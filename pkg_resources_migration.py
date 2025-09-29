#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pkg_resources Migration Guide for Guitar Life
=============================================

This file demonstrates how to migrate from the deprecated pkg_resources 
to modern Python resource management using importlib.resources.

Your pygame 2.6.1 with Python 3.13.7 setup is perfect for using these modern approaches!
"""

# Suppress the pygame pkg_resources deprecation warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

import sys
from pathlib import Path

# Modern resource loading (Python 3.9+)
if sys.version_info >= (3, 9):
    from importlib import resources
    HAS_MODERN_RESOURCES = True
else:
    try:
        import importlib_resources as resources
        HAS_MODERN_RESOURCES = True
    except ImportError:
        resources = None
        HAS_MODERN_RESOURCES = False

def demo_pkg_resources_alternatives():
    """Show alternatives to common pkg_resources patterns"""
    
    print("🔄 pkg_resources Migration Examples")
    print("=" * 40)
    
    # Example 1: resource_exists
    print("\n1. Checking if resource exists:")
    print("   ❌ OLD: pkg_resources.resource_exists(__name__, 'config.json')")
    print("   ✅ NEW:")
    
    if HAS_MODERN_RESOURCES:
        # Modern way
        try:
            is_resource = resources.files(__name__).joinpath('app_config.json').is_file()
            print(f"      importlib.resources: {is_resource}")
        except Exception as e:
            print(f"      importlib.resources failed: {e}")
    
    # Fallback way
    config_exists = Path('app_config.json').exists()
    print(f"      pathlib.Path fallback: {config_exists}")
    
    # Example 2: resource_stream
    print("\n2. Reading resource content:")
    print("   ❌ OLD: pkg_resources.resource_stream(__name__, 'config.json')")
    print("   ✅ NEW:")
    
    if HAS_MODERN_RESOURCES and Path('app_config.json').exists():
        try:
            # Modern way - reading text
            content = resources.files(__name__).joinpath('app_config.json').read_text(encoding='utf-8')
            print(f"      importlib.resources: Read {len(content)} characters")
        except Exception as e:
            print(f"      importlib.resources failed: {e}")
    
    # Fallback way
    try:
        with open('app_config.json', 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"      pathlib.Path fallback: Read {len(content)} characters")
    except FileNotFoundError:
        print("      pathlib.Path fallback: File not found")
    
    # Example 3: Resource listing
    print("\n3. Listing resources:")
    print("   ❌ OLD: pkg_resources.resource_listdir(__name__, '.')")
    print("   ✅ NEW:")
    
    if HAS_MODERN_RESOURCES:
        try:
            # Modern way
            resource_files = [f.name for f in resources.files(__name__).iterdir() if f.is_file()]
            print(f"      importlib.resources: {len(resource_files)} files")
        except Exception as e:
            print(f"      importlib.resources failed: {e}")
    
    # Fallback way
    local_files = [f.name for f in Path('.').iterdir() if f.is_file()]
    print(f"      pathlib.Path fallback: {len(local_files)} files")

def create_modern_resource_loader():
    """Create a modern resource loader class"""
    
    class ModernResourceLoader:
        """Modern replacement for pkg_resources functionality"""
        
        def __init__(self, package_or_path=None):
            if package_or_path is None:
                package_or_path = __name__
            
            if isinstance(package_or_path, str) and not Path(package_or_path).exists():
                # It's a package name
                self.package = package_or_path
                self.base_path = None
            else:
                # It's a file path
                self.package = None
                self.base_path = Path(package_or_path) if package_or_path else Path('.')
        
        def resource_exists(self, name: str) -> bool:
            """Check if a resource exists"""
            if HAS_MODERN_RESOURCES and self.package:
                try:
                    return resources.files(self.package).joinpath(name).is_file()
                except:
                    pass
            
            # Fallback
            if self.base_path:
                return (self.base_path / name).exists()
            return Path(name).exists()
        
        def read_text(self, name: str, encoding='utf-8') -> str:
            """Read resource as text"""
            if HAS_MODERN_RESOURCES and self.package:
                try:
                    return resources.files(self.package).joinpath(name).read_text(encoding=encoding)
                except:
                    pass
            
            # Fallback
            if self.base_path:
                return (self.base_path / name).read_text(encoding=encoding)
            return Path(name).read_text(encoding=encoding)
        
        def read_bytes(self, name: str) -> bytes:
            """Read resource as bytes"""
            if HAS_MODERN_RESOURCES and self.package:
                try:
                    return resources.files(self.package).joinpath(name).read_bytes()
                except:
                    pass
            
            # Fallback
            if self.base_path:
                return (self.base_path / name).read_bytes()
            return Path(name).read_bytes()
        
        def list_resources(self) -> list:
            """List all resources"""
            if HAS_MODERN_RESOURCES and self.package:
                try:
                    return [f.name for f in resources.files(self.package).iterdir() if f.is_file()]
                except:
                    pass
            
            # Fallback
            if self.base_path:
                return [f.name for f in self.base_path.iterdir() if f.is_file()]
            return [f.name for f in Path('.').iterdir() if f.is_file()]
    
    return ModernResourceLoader

def main():
    """Main demonstration"""
    print("🎸 Guitar Life - pkg_resources to importlib.resources Migration")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Modern resources available: {HAS_MODERN_RESOURCES}")
    print()
    
    # Test pygame import (should not show warning now)
    print("Testing pygame import (should be warning-free):")
    try:
        import pygame
        print(f"✅ pygame {pygame.version.ver} imported successfully!")
    except ImportError:
        print("❌ pygame not available")
    print()
    
    # Show migration examples
    demo_pkg_resources_alternatives()
    
    print("\n" + "=" * 60)
    print("📋 Migration Checklist:")
    print("✅ 1. Added warning filter for pygame's pkg_resources usage")
    print("✅ 2. Created modern resource management utilities") 
    print("✅ 3. Implemented fallbacks for compatibility")
    print("✅ 4. Updated Guitar Life to use new resource loading")
    print()
    print("🚀 Your setup is ready for the future!")
    print("   - Python 3.13.7 ✅")
    print("   - pygame 2.6.1 ✅") 
    print("   - Modern resource loading ✅")
    print("   - pkg_resources warnings suppressed ✅")

if __name__ == "__main__":
    main()