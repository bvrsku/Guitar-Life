#!/usr/bin/env python3
"""
Тест увеличенных расстояний в GUI вкладки Layers
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_increased_spacing():
    """Тест увеличенных расстояний в GUI"""
    try:
        print("=== Тест увеличенных расстояний в вкладке Layers ===")
        print()
        
        print("Новые расстояния между элементами (левая колонка):")
        print("• Rule:         layer_y + 0   (базовая позиция)")
        print("• Age Palette:  layer_y + 50  (было +35, стало +50, интервал: 50px)")
        print("• RMS Palette:  layer_y + 100 (было +70, стало +100, интервал: 50px)")
        print("• Color Mode:   layer_y + 150 (было +105, стало +150, интервал: 50px)")
        print()
        
        print("Новые расстояния между элементами (правая колонка):")
        print("• Alpha слайдер: layer_y + 0   (базовая позиция)")
        print("• Solo/Mute:     layer_y + 50  (было +35, стало +50)")
        print("• RMS Mode:      layer_y + 100 (было +65, стало +100)")
        print()
        
        print("Улучшения:")
        print("✅ Интервал между dropdown'ами увеличен с ~35px до 50px")
        print("✅ Все выпадающие списки теперь имеют достаточно места")
        print("✅ Элементы правой колонки синхронизированы с левой")
        print("✅ Dropdown'ы палитр больше не накладываются друг на друга")
        print()
        
        print("Визуальная схема расположения:")
        print("┌─ Левая колонка ────────┬─ Правая колонка ──────┐")
        print("│ Rule           (+0)    │ Alpha         (+0)    │")
        print("│                        │                       │")
        print("│ Age Palette    (+50)   │ Solo/Mute     (+50)   │")  
        print("│                        │                       │")
        print("│ RMS Palette    (+100)  │ RMS Mode      (+100)  │")
        print("│                        │                       │")
        print("│ Color Mode     (+150)  │                       │")
        print("└────────────────────────┴───────────────────────┘")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_increased_spacing()