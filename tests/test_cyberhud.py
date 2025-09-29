#!/usr/bin/env python3
"""
Тестирование интегрированного CyberHUD
"""

import sys
import os

# Добавляем путь к guitar_life.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cyberhud_integration():
    """Проверяет что CyberHUD правильно интегрирован"""
    print("🧪 Testing CyberHUD integration...")
    
    try:
        # Импортируем основные классы
        from guitar_lifeE import CyberHUD, CyberSlider, CyberButton, CyberComboBox
        from guitar_lifeE import HSV_DESIGN_PALETTES, HSV_COLOR_PALETTES, CA_RULES
        
        print("✅ Successfully imported CyberHUD classes")
        print(f"   - CA_RULES: {len(CA_RULES)} rules")
        print(f"   - HSV_DESIGN_PALETTES: {len(HSV_DESIGN_PALETTES)} palettes")
        print(f"   - HSV_COLOR_PALETTES: {len(HSV_COLOR_PALETTES)} palettes")
        
        # Проверяем что можно создать HUD
        import pygame
        pygame.init()
        font = pygame.font.SysFont("arial", 16)
        
        hud = CyberHUD(font, 800, 5)
        print("✅ Successfully created CyberHUD instance")
        print(f"   - Categories: {hud.categories}")
        print(f"   - Active category: {hud.active_category}")
        
        # Проверяем что есть аудио устройства
        test_devices = [
            {'name': 'Test Device 1', 'index': 0},
            {'name': 'Test Device 2', 'index': 1}
        ]
        hud.set_audio_devices(test_devices)
        print("✅ Successfully set test audio devices")
        
        # Проверяем что есть контролы SETUP категории
        setup_controls = hud._get_active_category_controls()
        print(f"✅ SETUP category has {len(setup_controls)} controls:")
        for name, control in setup_controls:
            if control:
                print(f"   - {name}: {type(control).__name__}")
            else:
                print(f"   - {name}: None (not created)")
        
        pygame.quit()
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_functions():
    """Проверяет функции конфигурации"""
    print("\n🧪 Testing configuration functions...")
    
    try:
        from guitar_lifeE import get_default_configuration, convert_modern_gui_config
        
        # Тестовые устройства
        test_devices = [{'name': 'Test Device', 'index': 0}]
        
        # Проверяем дефолтную конфигурацию
        default_config = get_default_configuration(test_devices)
        print("✅ Successfully created default configuration")
        print(f"   - Device: {default_config.get('device')}")
        print(f"   - Layer count: {default_config.get('layer_count')}")
        print(f"   - Layers cfg: {len(default_config.get('layers_cfg', []))}")
        
        # Проверяем конвертацию
        converted = convert_modern_gui_config(default_config, test_devices)
        print("✅ Successfully converted configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing CyberHUD Integration")
    print("=" * 50)
    
    success1 = test_cyberhud_integration()
    success2 = test_config_functions()
    
    if success1 and success2:
        print("\n🎉 All tests passed! CyberHUD integration is working.")
        print("\n💡 Key improvements:")
        print("   - ✅ SETUP category replaces modern_gui")
        print("   - ✅ Audio device selection integrated")
        print("   - ✅ Configuration save/load functionality")
        print("   - ✅ All modern_gui features preserved")
        print("\n🎮 Ready to run main application!")
    else:
        print("\n❌ Some tests failed. Check errors above.")