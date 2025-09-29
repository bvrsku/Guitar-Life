# This file has been deleted.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Упрощенный тест запуска без GUI
"""

# Suppress pygame's pkg_resources deprecation warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

import sys
import os
import numpy as np

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import pygame and other dependencies
import pygame

# Import from guitar_life
from guitar_life import apply_scanlines, apply_trails, Layer, HUD
from guitar_life import apply_scale_blur, apply_bloom, apply_posterize, apply_dither, apply_pixelate, apply_outline

# Modern resource utilities
try:
    from resource_utils import resource_manager, load_app_config, save_app_config, load_guitar_config, save_guitar_config
except ImportError:
    resource_manager = None
    def load_app_config(): return {}
    def save_app_config(config): return False
    def load_guitar_config(): return {}
    def save_guitar_config(config): return False

# Import constants and classes from guitar_life_patched
try:
    # Copy minimal required constants
    GRID_W = 240
    GRID_H = 135
    CELL_SIZE = 4
    HUD_WIDTH = 350
    FIELD_OFFSET_X = 20
    BG_COLOR = (0, 0, 0)
    FPS = 60
except Exception as e:
    print(f"Error importing constants: {e}")

def create_test_settings():
    """Create simple test settings without GUI"""
    print("🔧 Creating test settings...")
    
    return {
        'device': None,  # Use default audio device
        'gain': 2.5,
        'layer_count': 2,  # Start with just 2 layers
        'rms_strength': 100,
        'color_rms_min': 0.004,
        'color_rms_max': 0.3,
        'layers_different': False,  # Use same settings for all layers
        'layers_cfg': [],
        'rule': 'Conway',
        'age_palette': 'Blue->Green->Yellow->Red',
        'rms_palette': 'Black->White',
        'color_mode': 'HSV',
        'rms_mode': 'multiply',
        'alpha_live': 255,
        'alpha_old': 180,
        'clear_rms': 0.003
    }

def create_minimal_app(settings):
    """Create a minimal App instance for testing"""
    print("🚀 Creating minimal app...")
    
    # Initialize pygame
    pygame.init()
    
    # Create window
    W = GRID_W * CELL_SIZE + FIELD_OFFSET_X
    H = GRID_H * CELL_SIZE
    
    screen = pygame.display.set_mode((W + HUD_WIDTH, H))
    pygame.display.set_caption("Guitar Life - Test")
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 16)
    
    print(f"✅ Window created: {W + HUD_WIDTH}x{H}")
    
    # Create basic layers
    layers = []
    for i in range(settings['layer_count']):
        # Create a simple layer simulation
        grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        age = np.zeros((GRID_H, GRID_W), dtype=np.int32)
        
        # Add some test patterns
        if i == 0:
            # First layer: some blocks
            grid[50:55, 50:55] = True
            age[50:55, 50:55] = 1
        elif i == 1:
            # Second layer: diagonal line
            for j in range(min(GRID_H, GRID_W) // 2):
                if 60 + j < GRID_H and 60 + j < GRID_W:
                    grid[60 + j, 60 + j] = True
                    age[60 + j, 60 + j] = 1
        
        # Create a minimal layer object
        layer = type('Layer', (), {
            'grid': grid,
            'age': age,
            'rule': settings['rule'],
            'age_palette': settings['age_palette'],
            'rms_palette': settings['rms_palette'],
            'color_mode': settings['color_mode'],
            'rms_mode': settings['rms_mode'],
            'alpha_live': settings['alpha_live'],
            'alpha_old': settings['alpha_old'],
            'mix': 1.0,
            'solo': False,
            'mute': False,
            'blend_mode': 'normal',
            'rms_enabled': True
        })()
        
        layers.append(layer)
    
    print(f"✅ Created {len(layers)} test layers")
    
    return screen, clock, font, layers

def test_render_loop():
    """Test basic render loop"""
    print("🎨 Testing render loop...")
    
    settings = create_test_settings()
    screen, clock, font, layers = create_minimal_app(settings)
    
    print("🎮 Starting test render loop...")
    print("   Press ESC or close window to exit")
    
    running = True
    frame_count = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Simple rendering
        screen.fill(BG_COLOR)
        
        # Draw layers as simple colored rectangles
        for i, layer in enumerate(layers):
            color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)][i % 3]
            
            # Draw alive cells
            alive_positions = np.where(layer.grid)
            for y, x in zip(alive_positions[0], alive_positions[1]):
                rect = pygame.Rect(
                    FIELD_OFFSET_X + x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(screen, color, rect)
        
        # Draw simple info
        info_text = f"Frame: {frame_count} | Layers: {len(layers)} | ESC to exit"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # Draw layer info
        for i, layer in enumerate(layers):
            alive_count = np.sum(layer.grid)
            layer_text = f"Layer {i}: {alive_count} cells"
            layer_surface = font.render(layer_text, True, (200, 200, 200))
            screen.blit(layer_surface, (10, 40 + i * 20))
        
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1
        
        # Auto-exit after showing it works
        if frame_count > 300:  # ~5 seconds at 60 FPS
            print("✅ Render test completed successfully!")
            break
    
    pygame.quit()
    print("🎯 Test completed")

def main():
    """Main test function"""
    print("🎸 Guitar Life - Simple Display Test")
    print("=" * 40)
    
    try:
        test_render_loop()
        print("\n✅ SUCCESS: Display system is working!")
        print("   Your Guitar Life should be able to display properly.")
        print("   If the main app still doesn't work, the issue might be in:")
        print("   - Audio initialization")
        print("   - GUI components")
        print("   - Complex layer management")
        
    except Exception as e:
        print(f"\n❌ ERROR: Display test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()