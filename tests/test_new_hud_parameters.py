#!/usr/bin/env python3
"""
Тест новых параметров в HUD: fade_sat_drop, fade_val_drop, global_v_mul
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_new_hud_parameters():
    """Тест новых параметров в HUD"""
    try:
        from guitar_li4fe import get_default_settings
        
        # Проверяем настройки по умолчанию
        settings = get_default_settings([])
        
        print("=== Тест новых параметров в HUD ===")
        print()
        
        # Проверяем наличие новых параметров
        required_params = ['fade_sat_drop', 'fade_val_drop', 'global_v_mul']
        
        for param in required_params:
            if param in settings:
                print(f"✅ {param}: {settings[param]}")
            else:
                print(f"❌ {param}: ОТСУТСТВУЕТ")
        
        print()
        print("Описание параметров:")
        print("• fade_sat_drop: Уменьшение насыщенности при старении клеток (%)")
        print("• fade_val_drop: Уменьшение яркости при старении клеток (%)")  
        print("• global_v_mul: Глобальный множитель яркости (0.1-3.0)")
        print()
        print("Расположение в GUI: Вкладка 'Layers' -> внизу")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_new_hud_parameters()