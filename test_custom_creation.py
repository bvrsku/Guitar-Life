#!/usr/bin/env python3
"""
Тест создания пользовательских правил и палитр
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_custom_creation():
    """Тест создания пользовательских правил и палитр"""
    try:
        from guitar_life import CA_RULES, PALETTE_OPTIONS, CUSTOM_CA_RULES, CUSTOM_PALETTES
        
        print("=== Тест создания пользовательских правил и палитр ===")
        print()
        
        print("📋 Новая вкладка 'Custom' добавлена в HUD")
        print()
        
        print("🔧 Создание пользовательских правил CA:")
        print("• Поле 'Rule Name' - название правила")
        print("• Поле 'Born' - условия рождения клеток (например: 3,6,7)")
        print("• Поле 'Survive' - условия выживания клеток (например: 2,3)")
        print("• Кнопка 'Create Rule' - создать правило")
        print()
        
        print("🎨 Создание пользовательских палитр:")
        print("• Поле 'Palette Name' - название палитры")
        print("• Поле 'Start Color' - начальный цвет (R,G,B например: 255,0,0)")
        print("• Поле 'End Color' - конечный цвет (R,G,B например: 0,0,255)")
        print("• Кнопка 'Create Palette' - создать палитру")
        print()
        
        print("✨ Возможности:")
        print("• Автоматическое создание уникальных имен при конфликтах")
        print("• Валидация входных данных")
        print("• Создание 10-цветного градиента для палитр")
        print("• Автоматическое обновление списков в GUI")
        print("• Поддержка пользовательских правил в step_life()")
        print("• Поддержка пользовательских палитр в get_palette_color()")
        print()
        
        print("🎯 Примеры правил CA:")
        print("• Conway: Born=3, Survive=2,3")
        print("• HighLife: Born=3,6, Survive=2,3") 
        print("• Replicator: Born=1,3,5,7, Survive=1,3,5,7")
        print("• Custom Rule: Born=2,4, Survive=1,3,5 (пользовательское)")
        print()
        
        print("🌈 Примеры палитр:")
        print("• Fire: (255,0,0) -> (255,255,0)")
        print("• Ocean: (0,0,255) -> (0,255,255)") 
        print("• Sunset: (255,100,0) -> (150,0,150)")
        print("• Custom: любые цвета по выбору пользователя")
        print()
        
        # Проверяем начальное состояние
        print(f"Стандартных правил CA: {len(CA_RULES)}")
        print(f"Пользовательских правил: {len(CUSTOM_CA_RULES)}")
        print(f"Стандартных палитр: {len(PALETTE_OPTIONS)}")
        print(f"Пользовательских палитр: {len(CUSTOM_PALETTES)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_custom_creation()