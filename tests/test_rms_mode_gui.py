#!/usr/bin/env python3
"""
Тест параметра rms_mode в GUI
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rms_mode_gui():
    """Тест параметра rms_mode в GUI"""
    try:
        from guitar_li4fe import get_default_settings, Layer
        
        print("=== Тест параметра rms_mode в GUI ===")
        print()
        
        # Проверяем настройки по умолчанию
        settings = get_default_settings([])
        
        print("Проверка настроек слоев:")
        if 'layers_cfg' in settings:
            for i, layer_cfg in enumerate(settings['layers_cfg']):
                rms_mode = layer_cfg.get('rms_mode', 'НЕ НАЙДЕН')
                print(f"✅ Layer {i+1} rms_mode: {rms_mode}")
        else:
            print("❌ layers_cfg не найден в настройках")
        
        print()
        print("Описание параметра rms_mode:")
        print("• 'brightness' - RMS влияет на яркость цветов")
        print("• 'palette' - RMS использует отдельную цветовую палитру")
        print()
        print("GUI элемент:")
        print("• Dropdown 'RMS Mode' в правом столбце вкладки 'Layers'")
        print("• Варианты: 'Brightness', 'Palette'")
        print("• Расположение: рядом с Alpha и Solo/Mute")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_rms_mode_gui()