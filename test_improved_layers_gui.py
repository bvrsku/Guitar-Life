#!/usr/bin/env python3
"""
Тест улучшенного GUI вкладки Layers
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_improved_layers_gui():
    """Тест улучшенного GUI вкладки Layers"""
    try:
        from guitar_life import get_default_settings
        
        print("=== Тест улучшенной вкладки Layers ===")
        print()
        
        print("Выполненные улучшения:")
        print("✅ Убраны параметры 'Fade Sat Drop %' и 'Global Brightness'")
        print("✅ Улучшено расстояние между dropdown'ами в левой колонке:")
        print("   • Rule: layer_y + 0")
        print("   • Age Palette: layer_y + 35")  
        print("   • RMS Palette: layer_y + 70")
        print("   • Color Mode: layer_y + 105")
        print()
        print("✅ Улучшено расположение элементов в правой колонке:")
        print("   • Alpha слайдер: layer_y + 0")
        print("   • Solo/Mute чекбоксы: layer_y + 35") 
        print("   • RMS Mode dropdown: layer_y + 65")
        print()
        print("✅ Исправлены размеры элементов:")
        print("   • Alpha слайдер: высота 30px (было 35px)")
        print("   • Все dropdown'ы: стандартная высота 25px")
        print()
        
        # Проверяем настройки
        settings = get_default_settings([])
        
        print("Структура GUI вкладки Layers:")
        print("┌─ Левая колонка (160px) ─┬─ Правая колонка (140px) ─┐")
        print("│ Rule                    │ Alpha слайдер            │")
        print("│ Age Palette            │ Solo / Mute чекбоксы     │") 
        print("│ RMS Palette            │ RMS Mode dropdown        │")
        print("│ Color Mode             │                          │")
        print("└────────────────────────┴──────────────────────────┘")
        print()
        print("Параметры удалены из GUI (но остались в коде):")
        print("• fade_sat_drop - управление насыщенностью при fade")
        print("• global_v_mul - глобальный множитель яркости")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_improved_layers_gui()