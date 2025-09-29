#!/usr/bin/env python3
"""
Simple test for the App class in guitar_life_backup.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import everything from the backup file
from guitar_life_backup import *

def test_app():
    """Test the App class with minimal configuration"""
    print("Testing App class from backup file...")
    
    # Create minimal configuration
    sel = {
        'device': 0,  # Default audio device
        'layer_count': 2,  # Test with 2 layers
        'tick_ms': 150,
        'fx': {
            'trails': True,
            'blur': False,
            'bloom': False,
            'posterize': False,
            'dither': False,
            'scanlines': False,
            'pixelate': False,
            'outline': False
        },
        'layers_different': True,
        'clear_rms': 0.01,
        'aging_speed': 1.0,
        'max_age': 120
    }
    
    try:
        print("Creating App instance...")
        app = App(sel)
        print("✅ App created successfully!")
        
        print(f"Layers: {len(app.layers)}")
        for i, layer in enumerate(app.layers):
            cells = np.sum(layer.grid)
            print(f"  Layer {i}: {cells} cells, rule={layer.rule}, solo={layer.solo}, mute={layer.mute}")
        
        print("✅ App test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating App: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Initialize pygame to avoid issues
    import pygame
    pygame.init()
    
    success = test_app()
    
    pygame.quit()
    
    if success:
        print("\n🎉 Backup file App class is working correctly!")
    else:
        print("\n💥 Backup file has issues that need to be fixed")